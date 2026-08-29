#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zotero 团队群组库只读抓取工具。

数据源优先级：
  1. Zotero Web API   https://api.zotero.org/groups/<ZOTERO_GROUP_ID>（需 ZOTERO_API_KEY）
  2. 本地 Zotero API  <ZOTERO_LOCAL_API>/api/groups/<ZOTERO_GROUP_ID>（本机 Zotero 已同步群组库时的兜底）

只读边界：本脚本绝不写入 zotero.sqlite / storage；新增条目一律走 Zotero 客户端。
配置来源：环境变量优先，其次 <vault>/config/.env。vault 根目录取环境变量
RESEARCH_VAULT，默认 E:\\TeamVault。

用法：
  python zotero_team_extract.py doctor                    # 环境自检
  python zotero_team_extract.py collections               # 列出群组库全部分类
  python zotero_team_extract.py collection <KEY或名称>     # 列出某分类顶层条目（JSON）
  python zotero_team_extract.py item <ITEM_KEY>           # 抓单条（含子项与附件，JSON）
  python zotero_team_extract.py top [--limit N]           # 列出库顶层条目（JSON）
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_VERSION = "3"
DEFAULT_VAULT = r"E:\TeamVault"
TIMEOUT = 20
PAGE = 100


def out_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ------------------------------------------------------------------ 配置

def load_env_file(path: Path) -> dict:
    env = {}
    if not path.is_file():
        return env
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip('"').strip("'")
        if value:
            env[key.strip()] = value
    return env


def load_config() -> dict:
    env = dict(load_env_file(Path(DEFAULT_VAULT) / "config" / ".env"))
    env.update({k: os.environ[k] for k in
                ("RESEARCH_VAULT", "ZOTERO_GROUP_ID", "ZOTERO_API_KEY", "ZOTERO_LOCAL_API")
                if os.environ.get(k)})
    vault = env.get("RESEARCH_VAULT") or DEFAULT_VAULT
    env.update(load_env_file(Path(vault) / "config" / ".env"))
    env["RESEARCH_VAULT"] = vault
    env.setdefault("ZOTERO_LOCAL_API", "http://127.0.0.1:23119")
    return env


# ------------------------------------------------------------------ HTTP

class ApiError(RuntimeError):
    pass


def http_get(url: str, api_key: str = "", timeout: int = TIMEOUT):
    req = urllib.request.Request(url)
    req.add_header("Zotero-API-Version", API_VERSION)
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", "replace")
        total = resp.headers.get("Total-Results")
    return body, (int(total) if total else None)


def get_json(base: str, path: str, api_key: str = ""):
    body, _ = http_get(f"{base}{path}", api_key)
    return json.loads(body)


def fetch_all(base: str, path: str, api_key: str, hard_cap: int = 2000):
    """按 start/limit 翻页抓全（Zotero API 单页上限 100）。"""
    items, start = [], 0
    while True:
        body, total = http_get(f"{base}{path}?format=json&limit={PAGE}&start={start}", api_key)
        batch = json.loads(body)
        if not isinstance(batch, list):
            raise ApiError(f"非列表响应：{str(batch)[:200]}")
        items.extend(batch)
        start += len(batch)
        if not batch or start >= hard_cap:
            break
        if total is not None and start >= total:
            break
        if len(batch) < PAGE:
            break
    return items


def web_base(cfg: dict) -> str:
    gid = cfg.get("ZOTERO_GROUP_ID", "")
    if not gid.isdigit():
        raise ApiError("ZOTERO_GROUP_ID 未配置或不是数字（取 zotero.org 群组页 URL 中的数字）")
    return f"https://api.zotero.org/groups/{gid}"


def local_base(cfg: dict) -> str:
    gid = cfg.get("ZOTERO_GROUP_ID", "")
    if not gid.isdigit():
        raise ApiError("ZOTERO_GROUP_ID 未配置或不是数字")
    return f"{cfg['ZOTERO_LOCAL_API'].rstrip('/')}/api/groups/{gid}"


def resolve_base(cfg: dict):
    """返回 (base_url, api_key)。Web API 可用则优先，否则尝试本地兜底。"""
    base = web_base(cfg)
    key = cfg.get("ZOTERO_API_KEY", "")
    if key:
        try:
            http_get(f"{base}/items?limit=1", key, timeout=10)
            return base, key
        except Exception:
            pass
    try:
        http_get(f"{local_base(cfg)}/items?limit=1", "", timeout=6)
        return local_base(cfg), ""
    except Exception:
        raise ApiError("Web API 与本地 API 均不可用：检查 ZOTERO_GROUP_ID / ZOTERO_API_KEY，"
                       "或确认本机 Zotero 正在运行且已同步群组库。可先执行 doctor 自检。")


# ------------------------------------------------------------------ 提炼

def year_of(data: dict) -> str:
    m = re.search(r"\d{4}", data.get("date", "") or "")
    return m.group(0) if m else ""


def creators_of(data: dict) -> str:
    names = []
    for c in data.get("creators") or []:
        if c.get("name"):
            names.append(c["name"])
        elif c.get("familyName"):
            names.append(c["familyName"])
    return "; ".join(names)


def brief(it: dict) -> dict:
    d = it.get("data", {})
    return {
        "item_key": d.get("key", it.get("key", "")),
        "item_type": d.get("itemType", ""),
        "title": d.get("title", d.get("name", "")),
        "authors": creators_of(d),
        "year": year_of(d),
        "doi": d.get("DOI", ""),
        "url": d.get("url", ""),
        "tags": [t.get("tag", "") for t in d.get("tags") or []],
        "collections": d.get("collections", []),
    }


# ------------------------------------------------------------------ 子命令

def cmd_doctor(cfg: dict) -> int:
    print("== TeamVault / Zotero 群组库环境自检 ==")
    problems = 0

    vault = Path(cfg["RESEARCH_VAULT"])
    if (vault / "AGENTS.md").is_file() and (vault / "02_Literature").is_dir():
        print(f"[OK]   vault 就绪：{vault}")
    else:
        print(f"[ERR]  vault 不完整：{vault}（缺 AGENTS.md 或 02_Literature 目录）")
        problems += 1

    env_file = vault / "config" / ".env"
    if env_file.is_file():
        print(f"[OK]   配置文件：{env_file}")
    else:
        print(f"[WARN] 未找到 {env_file}（复制 config/.env.example 生成）")

    gid = cfg.get("ZOTERO_GROUP_ID", "")
    key = cfg.get("ZOTERO_API_KEY", "")
    if gid.isdigit():
        print(f"[OK]   ZOTERO_GROUP_ID = {gid}")
    else:
        print("[ERR]  ZOTERO_GROUP_ID 未配置（zotero.org 群组页 URL 中的数字）")
        problems += 1
    if key:
        print("[OK]   ZOTERO_API_KEY 已配置")
    else:
        print("[WARN] ZOTERO_API_KEY 未配置（Web API 不可用，仅剩本地兜底）")

    try:
        http_get(cfg["ZOTERO_LOCAL_API"].rstrip("/") + "/api/users/0/items?limit=1", timeout=4)
        print(f"[OK]   本机 Zotero 运行中（{cfg['ZOTERO_LOCAL_API']}）")
    except Exception:
        print(f"[WARN] 本机 Zotero 未运行或本地 API 不可用（{cfg['ZOTERO_LOCAL_API']}）")

    reachable = False
    if gid.isdigit() and key:
        try:
            get_json(f"https://api.zotero.org/groups/{gid}", "/items?limit=1", key)
            print("[OK]   Web API 可访问群组库")
            reachable = True
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("[ERR]  Web API 401：API Key 无效或没有该群组的读权限")
            elif e.code == 404:
                print("[ERR]  Web API 404：群组不存在（检查 ZOTERO_GROUP_ID）")
            else:
                print(f"[ERR]  Web API HTTP {e.code}")
            problems += 1
        except Exception as e:
            print(f"[ERR]  Web API 不可达：{e}")
            problems += 1
    if not reachable and gid.isdigit():
        try:
            http_get(f"{local_base(cfg)}/items?limit=1", "", timeout=6)
            print("[OK]   本地 API 可访问群组库（本机已同步）")
            reachable = True
        except Exception:
            print("[WARN] 本地 API 也无法访问群组库")

    if not reachable:
        print()
        print("下一步：1) 在 zotero.org 建群组并记下群组 ID；2) 在 settings/keys/new 生成只读 Key；")
        print("        3) 复制 config/.env.example 为 config/.env 并填入。详见 CONTRIBUTING.md。")
    return 2 if problems else 0


def cmd_collections(cfg: dict) -> int:
    base, key = resolve_base(cfg)
    cols = fetch_all(base, "/collections", key)
    if not cols:
        print("群组库暂无分类。")
        return 0
    print(f"{'KEY':<10} {'条目数':>6}  名称")
    for c in sorted(cols, key=lambda c: c.get("data", {}).get("name", "")):
        d = c.get("data", {})
        num = c.get("meta", {}).get("numItems", 0)
        print(f"{d.get('key', ''):<10} {num:>6}  {d.get('name', '')}")
    return 0


def cmd_collection(cfg: dict, target: str, limit: int) -> int:
    base, key = resolve_base(cfg)
    cols = fetch_all(base, "/collections", key)
    ckey = target if re.fullmatch(r"[A-Z0-9]{8}", target) else None
    if not ckey:
        for c in cols:
            if c.get("data", {}).get("name", "").strip().lower() == target.strip().lower():
                ckey = c.get("data", {}).get("key")
                break
    if not ckey:
        names = [c.get("data", {}).get("name", "") for c in cols]
        raise ApiError(f"未找到分类“{target}”。现有分类：{'、'.join(names) if names else '（无）'}；也可直接用 8 位 KEY。")
    items = fetch_all(base, f"/collections/{ckey}/items/top", key)
    if limit:
        items = items[:limit]
    print(json.dumps([brief(i) for i in items], ensure_ascii=False, indent=2))
    return 0


def cmd_item(cfg: dict, item_key: str) -> int:
    base, key = resolve_base(cfg)
    item = get_json(base, f"/items/{item_key}", key)
    try:
        children = get_json(base, f"/items/{item_key}/children", key)
        if not isinstance(children, list):
            children = []
    except Exception:
        children = []
    pdfs = [{"key": c.get("data", {}).get("key", ""),
             "filename": c.get("data", {}).get("filename", c.get("data", {}).get("title", "")),
             "content_type": c.get("data", {}).get("contentType", "")}
            for c in children if c.get("data", {}).get("itemType") == "attachment"]
    print(json.dumps({"brief": brief(item), "item": item, "children": children,
                      "pdf_attachments": pdfs}, ensure_ascii=False, indent=2))
    return 0


def cmd_top(cfg: dict, limit: int) -> int:
    base, key = resolve_base(cfg)
    items = fetch_all(base, "/items/top", key)
    if limit:
        items = items[:limit]
    print(json.dumps([brief(i) for i in items], ensure_ascii=False, indent=2))
    return 0


def main(argv=None) -> int:
    out_utf8()
    p = argparse.ArgumentParser(description="Zotero 团队群组库只读抓取工具")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    sub.add_parser("collections")
    pc = sub.add_parser("collection")
    pc.add_argument("target")
    pc.add_argument("--limit", type=int, default=0)
    pi = sub.add_parser("item")
    pi.add_argument("item_key")
    pt = sub.add_parser("top")
    pt.add_argument("--limit", type=int, default=0)
    a = p.parse_args(argv)

    cfg = load_config()
    try:
        if a.cmd == "doctor":
            return cmd_doctor(cfg)
        if a.cmd == "collections":
            return cmd_collections(cfg)
        if a.cmd == "collection":
            return cmd_collection(cfg, a.target, a.limit)
        if a.cmd == "item":
            return cmd_item(cfg, a.item_key)
        if a.cmd == "top":
            return cmd_top(cfg, a.limit)
    except ApiError as e:
        print(f"[ERR] {e}", file=sys.stderr)
        return 1
    except urllib.error.HTTPError as e:
        print(f"[ERR] HTTP {e.code}: {e.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"[ERR] 网络错误：{e.reason}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
