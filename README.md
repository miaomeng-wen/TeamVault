# TeamVault · 团队科研知识库

Obsidian + Zotero 群组库 + 智能体流水线构成的团队知识库。文献管理规范、协作规则与智能体写入边界见 [AGENTS.md](AGENTS.md)；新成员上手步骤见 [CONTRIBUTING.md](CONTRIBUTING.md)；整体设计思路见 `00_Home/建设方案.md`，vault 内入口页为 `00_Home/Home.md`。

## 目录速览

| 目录 | 用途 |
| --- | --- |
| `00_Home` | 入口导航、建设方案 |
| `01_Project` | 研究项目与实验记录 |
| `02_Literature` | 正式文献笔记（五个主题子目录，唯一笔记存放区） |
| `03_Concepts` | 概念词典与方法卡片 |
| `04_Tables` | Dataview 自动派生索引（**禁止手工编辑**） |
| `05_Chapter-Notes` | 章节级阅读笔记 |
| `06_Drafts` | 论文写作与草稿 |
| `07_Templates` | 笔记模板 |
| `08_Daily` | 日报、周报、日常记录 |
| `09_Assets` | 图片等附件 |
| `99_Archive` | 归档 |
| `config` | 环境配置（`.env` 不入库） |
| `team-skills` | 团队版智能体技能（待安装到本机 skills 目录） |

## 三条铁律

1. Zotero 只读：任何脚本、任何人不直接写 Zotero 数据库，新增条目走 Zotero 客户端。
2. 状态即事实：阅读/筛选状态只写在文献笔记的 frontmatter 里，看板自动汇总，没有手工进度表。
3. 认领制写入：文献笔记只由 `assignee` 认领人（或其 agent）写入，写入前按 `item_key` 全库查重。
