---
name: zotero-team-fetcher
description: 从团队 Zotero 群组库只读抓取论文条目。用于精读前获取元数据/PDF附件/分类清单，按 Item Key 或 Zotero collection 批量列出条目，或环境自检。脚本对 Zotero 绝对只读；配置读 config/.env。
---

# zotero-team-fetcher

团队 Zotero 群组库的只读数据源。除 `doctor` 输出人读报告外，其余子命令输出 UTF-8 JSON。

## 何时使用

- 用户要求精读某篇论文 / 生成文献笔记 → 先 `item <KEY>` 拿元数据与 PDF 附件信息
- 用户要求处理某个分类（collection）→ 先 `collections` 看清单，再 `collection <KEY或名称>` 拿条目
- 环境报错 / 首次配置 → `doctor` 自检，按提示补配置

## 用法

脚本位于本技能 `scripts/` 目录，Python 3.9+，无第三方依赖：

```bat
python scripts\zotero_team_extract.py doctor
python scripts\zotero_team_extract.py collections
python scripts\zotero_team_extract.py collection <KEY或名称> [--limit N]
python scripts\zotero_team_extract.py item <ITEM_KEY>
python scripts\zotero_team_extract.py top [--limit N]
```

数据源：优先 Zotero Web API（`https://api.zotero.org/groups/<ID>`，需 `ZOTERO_API_KEY`），不可用时兜底本机 Zotero 本地 API（需本机 Zotero 运行且已同步群组库）。

## 配置

读 `<vault>/config/.env`（可被同名环境变量覆盖）：`RESEARCH_VAULT`、`ZOTERO_GROUP_ID`、`ZOTERO_API_KEY`、`ZOTERO_LOCAL_API`。`.env` 由各成员本机维护，不入 Git。

## 输出字段（brief 摘要）

`item_key` / `item_type` / `title` / `authors`（分号分隔姓氏） / `year` / `doi` / `url` / `tags` / `collections`；`item` 子命令另附 Zotero 原始 JSON、`children`（笔记/附件）与 `pdf_attachments`（PDF Key 与文件名，用于拼 `zotero://open-pdf/library/items/<PDF_KEY>` 跳转）。

## 下游衔接（写文献笔记时）

1. 模板：`07_Templates/文献笔记模板.md`，字段含义见模板内注释。
2. 必填映射：`item_key`、`pdf_key`、`zotero`（select 链接）、`pdf`（open-pdf 链接）、`authors`、`year`、`source`。
3. 归档：按论文**主要贡献**选 `02_Literature` 五个主题目录之一；Zotero collection 只写入 frontmatter `collection` 字段，不决定目录。
4. 写入前按 `item_key` 全库查重（幂等），已存在则补全而非新建；`assignee` 填当前认领人。
5. 对 Zotero 严格只读：不写 `zotero.sqlite` / `storage`，新增条目提示用户走 Zotero 客户端。
