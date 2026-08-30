#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TeamVault 知识库质检工具（只读，不修改任何笔记）。

扫描 02_Literature（文献笔记）与 03_Concepts（概念卡片）下全部 .md 笔记。

文献笔记检查：
  1. 文件命名符合 作者_年份_短标题（00_ 开头的索引页自动跳过）
  2. frontmatter 必填字段非空
  3. reading_status / screening_status 取值合法
  4. year 为 4 位数字
  5. source_id 格式合法且全库唯一
  6. source_type / theme 合法，theme 与所在目录一致
  7. source_url / pdf_url 至少有一个可用链接
  8. finished 笔记至少有一条页码证据，且 screening_status 为 included
概念卡片检查：
  9. title / created / assignee 必填；tags、related_sources 缺失给 WARN

frontmatter 解析会剥离行内注释（与 Obsidian/YAML 一致：注释以空白+# 开始）。

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

REQUIRED = [
    "title", "source_id", "source_type", "authors", "year", "theme",
    "reading_status", "screening_status", "created",
]
READING_OK = {"unread", "reading", "finished", "excluded"}
SCREENING_OK = {"included", "candidate", "excluded"}
SOURCE_TYPE_OK = {"article", "conference", "book", "chapter", "report", "dataset", "web", "thesis", "other"}
THEME_OK = {
    "01_综述论文", "02_数据集与基准", "03_检测方法",
    "04_泛化与鲁棒性", "05_评价协议与可复现性",
}
NAME_RE = re.compile(r"^(?P<author>[^_\s][^_]*)_(?P<year>\d{4})_(?P<slug>.+)$")
SOURCE_ID_RE = re.compile(r"^(doi|url|manual):\S+$")
HTTP_RE = re.compile(r"^https?://", re.I)
EVIDENCE_ROW_RE = re.compile(
    r"^\|\s*[^|\s][^|]*\|\s*(?:第\s*)?\d+\s*页?\s*\|\s*[^|\s][^|]*\|",
    re.M,
)
CONCEPT_REQUIRED = ["title", "created", "assignee"]
INLINE_COMMENT_RE = re.compile(r"\s#")


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


def strip_inline_comment(val: str) -> str:
    """剥离 YAML 行内注释：注释以空白+# 开始；值首直接 # 视为空值。

    与 Obsidian/Dataview 的 YAML 解析保持一致，模板中的
    `reading_status: unread   # unread | ...` 应解析为 `unread`。
    """
    m = INLINE_COMMENT_RE.search(val)
    if m:
        val = val[: m.start()].rstrip()
    return "" if val.startswith("#") else val


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
        val = strip_inline_comment(val.strip())
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

    name_match = NAME_RE.match(md.stem)
    if not name_match:
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
    st = fm.get("source_type")
    if st and st not in SOURCE_TYPE_OK:
        issues.append(("ERR", f"source_type 非法：{st}"))
    theme = fm.get("theme")
    if theme and theme not in THEME_OK:
        issues.append(("ERR", f"theme 非法：{theme}"))
    if theme in THEME_OK and md.parent.name != theme:
        issues.append(("ERR", f"theme 与所在目录不一致：{theme} != {md.parent.name}"))
    y = fm.get("year")
    if y and not re.fullmatch(r"\d{4}", str(y)):
        issues.append(("ERR", f"year 应为 4 位数字：{y}"))
    if name_match and y and name_match.group("year") != str(y):
        issues.append(("ERR", f"文件名年份与 frontmatter 不一致：{name_match.group('year')} != {y}"))
    sid = fm.get("source_id")
    if sid and not SOURCE_ID_RE.match(str(sid)):
        issues.append(("ERR", f"source_id 格式应为 doi: / url: / manual: 前缀：{sid}"))
    if sid and str(sid).startswith("doi:") and str(sid)[4:] != str(sid)[4:].lower():
        issues.append(("ERR", f"DOI 型 source_id 应使用小写：{sid}"))
    links = [fm.get("source_url"), fm.get("pdf_url")]
    if not any(isinstance(v, str) and v.strip() for v in links):
        issues.append(("WARN", "source_url / pdf_url 均为空"))
    for field in ("source_url", "pdf_url"):
        value = fm.get(field)
        if isinstance(value, str) and value.strip() and not HTTP_RE.match(value):
            issues.append(("WARN", f"{field} 不是 HTTP(S) 稳定链接：{value}"))
    if not fm.get("assignee"):
        issues.append(("WARN", "未填 assignee（待认领）"))
    if rs == "finished" and not EVIDENCE_ROW_RE.search(text):
        issues.append(("ERR", "finished 笔记缺少带页码的证据表行"))
    if rs == "finished" and ss in SCREENING_OK and ss != "included":
        issues.append(("ERR", f"finished 要求终检通过（screening_status 应为 included，当前 {ss}）"))
    return issues, fm


def check_concept(md: Path):
    """概念卡片检查：返回 (issues, fm)。只查基础 frontmatter，不约束命名。"""
    issues = []
    try:
        text = md.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return [("ERR", f"无法读取：{e}")], {}
    fm, _ = parse_frontmatter(text)
    for f in CONCEPT_REQUIRED:
        v = fm.get(f)
        if v is None or v == [] or (isinstance(v, str) and not v.strip()):
            issues.append(("ERR", f"必填字段缺失或为空：{f}"))
    if not fm.get("tags"):
        issues.append(("WARN", "未填 tags（建议 concept 或 method）"))
    if not fm.get("related_sources"):
        issues.append(("WARN", "未关联任何文献（related_sources 为空）"))
    return issues, fm


def main(argv=None) -> int:
    out_utf8()
    p = argparse.ArgumentParser(description="TeamVault 知识库质检（只读）")
    p.add_argument("--vault", help="vault 根目录（默认自动定位）")
    p.add_argument("--strict", action="store_true", help="存在 ERR 时退出码 2")
    a = p.parse_args(argv)

    vault = find_vault(a.vault)
    if not (vault / "02_Literature").is_dir():
        print(f"[ERR] 未找到文献目录：{vault / '02_Literature'}")
        return 2

    areas = (("02_Literature", check_note), ("03_Concepts", check_concept))
    source_id_map = defaultdict(list)
    all_issues = []
    area_counts = {}
    for area, checker in areas:
        area_path = vault / area
        if not area_path.is_dir():
            continue
        n_checked = 0
        for md in sorted(area_path.rglob("*.md")):
            if md.stem.startswith("00_"):
                continue
            issues, fm = checker(md)
            n_checked += 1
            if area == "02_Literature":
                sid = fm.get("source_id")
                if sid:
                    source_id_map[str(sid)].append(md)
            for lv, msg in issues:
                all_issues.append((lv, md.relative_to(vault), msg))
        area_counts[area] = n_checked

    for source_id, paths in sorted(source_id_map.items()):
        if len(paths) > 1:
            for md in paths:
                all_issues.append(("ERR", md.relative_to(vault), f"source_id 重复：{source_id}（{len(paths)} 篇共用）"))

    err = sum(1 for lv, _, _ in all_issues if lv == "ERR")
    warn = sum(1 for lv, _, _ in all_issues if lv == "WARN")
    print("== TeamVault 知识库质检报告 ==")
    print(f"vault：{vault}")
    scan_summary = " · ".join(f"{area} {n} 篇" for area, n in area_counts.items())
    print(f"扫描笔记：{scan_summary or '无'}；问题：{err} ERR / {warn} WARN")
    if not all_issues:
        print("全部通过")
        return 0
    for lv, rel, msg in sorted(all_issues, key=lambda t: (t[0] != "ERR", str(t[1]))):
        print(f"[{lv}] {rel} — {msg}")
    return 2 if (a.strict and err) else 0


if __name__ == "__main__":
    sys.exit(main())
