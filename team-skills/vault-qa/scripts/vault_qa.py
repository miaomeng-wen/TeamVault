#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TeamVault 文献库质检工具（只读，不修改任何笔记）。

扫描 02_Literature 下全部 .md 笔记，检查：
  1. 文件命名符合 作者_年份_短标题（00_ 开头的索引页自动跳过）
  2. frontmatter 必填字段非空：title / item_key / authors / year / reading_status
  3. reading_status / screening_status 取值合法
  4. year 为 4 位数字
  5. item_key 格式合法（8 位字母数字）且全库唯一
  6. zotero / pdf 跳转链接存在（缺则 WARN）
  7. assignee 已填（缺则 WARN，提示待认领）

定位 vault：--vault 参数 > 环境变量 RESEARCH_VAULT > 脚本所在仓库根（本脚本位于
<vault>/team-skills/vault-qa/scripts/，自动向上取 parents[3]）。

用法：
  python vault_qa.py                 # 输出报告
  python vault_qa.py --strict        # 有 ERR 时退出码 2（供定时巡检 / CI）
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

REQUIRED = ["title", "item_key", "authors", "year", "reading_status"]
READING_OK = {"unread", "reading", "finished", "excluded"}
SCREENING_OK = {"included", "candidate", "excluded"}
NAME_RE = re.compile(r"^(?P<author>[^_\s][^_]*)_(?P<year>\d{4})_(?P<slug>.+)$")
KEY_RE = re.compile(r"^[A-Z0-9]{8}$")


def out_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def find_vault(explicit) -> Path:
    if explicit:
        return Path(explicit)
    if os.environ.get("RESEARCH_VAULT"):
        return Path(os.environ["RESEARCH_VAULT"])
    return Path(__file__).resolve().parents[3]


def parse_frontmatter(text: str):
    """极简 frontmatter 解析：仅支持 key: value 与 key: [a, b] 两种形态。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, False
    fm = {}
    for line in lines[1:]:
        s = line.strip()
        if s == "---":
            return fm, True
        if not s or s.startswith("#") or ":" not in s:
            continue
        key, _, val = s.partition(":")
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            fm[key.strip()] = [x.strip().strip("'\"") for x in inner.split(",")] if inner else []
        else:
            fm[key.strip()] = val.strip("'\"")
    return fm, True


def check_note(md: Path):
    """返回 (issues, fm)。issue = (level, msg)，level ∈ ERR / WARN。"""
    issues = []
    if md.stem.startswith("00_"):  # 索引页豁免
        return issues, {}
    try:
        text = md.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return [("ERR", f"无法读取：{e}")], {}
    fm, _ = parse_frontmatter(text)

    if not NAME_RE.match(md.stem):
        issues.append(("ERR", "文件名不符合 作者_年份_短标题"))
    for f in REQUIRED:
        v = fm.get(f)
        if v is None or v == [] or (isinstance(v, str) and not v.strip()):
            issues.append(("ERR", f"必填字段缺失或为空：{f}"))
    rs = fm.get("reading_status")
    if rs and rs not in READING_OK:
        issues.append(("ERR", f"reading_status 非法：{rs}（允许 {sorted(READING_OK)}）"))
    ss = fm.get("screening_status")
    if ss and ss not in SCREENING_OK:
        issues.append(("ERR", f"screening_status 非法：{ss}"))
    y = fm.get("year")
    if y and not re.fullmatch(r"\d{4}", str(y)):
        issues.append(("ERR", f"year 应为 4 位数字：{y}"))
    ik = fm.get("item_key")
    if ik and not KEY_RE.match(str(ik)):
        issues.append(("ERR", f"item_key 应为 8 位字母数字：{ik}"))
    for link in ("zotero", "pdf"):
        v = fm.get(link)
        if v is None or (isinstance(v, str) and not v.strip()):
            issues.append(("WARN", f"缺少 {link} 跳转链接"))
    if not fm.get("assignee"):
        issues.append(("WARN", "未填 assignee（待认领）"))
    return issues, fm


def main(argv=None) -> int:
    out_utf8()
    p = argparse.ArgumentParser(description="TeamVault 文献库质检（只读）")
    p.add_argument("--vault", help="vault 根目录（默认自动定位）")
    p.add_argument("--strict", action="store_true", help="存在 ERR 时退出码 2")
    a = p.parse_args(argv)

    vault = find_vault(a.vault)
    lit = vault / "02_Literature"
    if not lit.is_dir():
        print(f"[ERR] 未找到文献目录：{lit}")
        return 2

    key_map = defaultdict(list)
    all_issues = []
    n_checked = 0
    for md in sorted(lit.rglob("*.md")):
        issues, fm = check_note(md)
        if md.stem.startswith("00_"):
            continue
        n_checked += 1
        ik = fm.get("item_key")
        if ik:
            key_map[str(ik)].append(md)
        for lv, msg in issues:
            all_issues.append((lv, md.relative_to(vault), msg))

    for k, paths in sorted(key_map.items()):
        if len(paths) > 1:
            for md in paths:
                all_issues.append(("ERR", md.relative_to(vault), f"item_key 重复：{k}（{len(paths)} 篇共用）"))

    err = sum(1 for lv, _, _ in all_issues if lv == "ERR")
    warn = sum(1 for lv, _, _ in all_issues if lv == "WARN")
    print("== TeamVault 文献库质检报告 ==")
    print(f"vault：{vault}")
    print(f"扫描笔记：{n_checked} 篇；问题：{err} ERR / {warn} WARN")
    if not all_issues:
        print("全部通过")
        return 0
    for lv, rel, msg in sorted(all_issues, key=lambda t: (t[0] != "ERR", str(t[1]))):
        print(f"[{lv}] {rel} — {msg}")
    return 2 if (a.strict and err) else 0


if __name__ == "__main__":
    sys.exit(main())
