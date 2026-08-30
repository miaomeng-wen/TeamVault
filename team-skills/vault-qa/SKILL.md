---
name: vault-qa
description: 对 TeamVault 文献库做只读规范巡检：frontmatter 完整性、文件命名、状态机、source_id 唯一性、主题目录与证据要求。用于写完笔记后的自检、定期全库巡检、周报异常摘要。只输出报告，不修改任何笔记。
---

# vault-qa

文献库规范巡检工具。只读：不修改任何笔记，只输出报告。

## 用法

脚本位于本技能 `scripts/` 目录，Python 3.9+，无第三方依赖：

```bat
python scripts\vault_qa.py                 # 全库扫描，输出报告
python scripts\vault_qa.py --strict        # 有 ERR 时退出码 2（供定时巡检）
python scripts\vault_qa.py --vault <路径>   # 指定 vault（默认自动定位）
```

定位顺序：`--vault` 参数 → 环境变量 `RESEARCH_VAULT` → 脚本所在仓库根。

## 检查项

文献笔记（`02_Literature`）：

- ERR：文件名或年份不一致；必填字段为空；状态、来源类型或主题非法；`source_id` 格式错误或重复；`theme` 与所在目录不一致；`finished` 笔记没有带页码的证据表行，或 `screening_status` 不是 `included`。
- WARN：`source_url` / `pdf_url` 均为空或不是 HTTP(S) 稳定链接；未填 `assignee`（待认领）。
- `00_` 开头的索引页自动豁免。

概念卡片（`03_Concepts`）：

- ERR：`title` / `created` / `assignee` 缺失或为空。
- WARN：`tags` 或 `related_sources` 为空。

frontmatter 解析与 Obsidian/YAML 行为一致：行内 `#` 注释（以空白+# 开始）会被剥离，模板中的行内注释不会误报。

## 何时运行

1. 单篇笔记写完后的自检（跑一遍，确认该笔记无 ERR 再提交）。
2. 每周随 team-digest 跑一次全库巡检（`--strict`）。
3. 团队成员报告"看板数据不对"时先跑一遍定位漏字段。

## 结果处置

- 报告只呈现问题，**不自动修复**。修复原则：属于自己认领的笔记直接修；他人笔记列清单转交认领人；批量修复（如统一改模板缺字段）须团队确认后单独一次 `qa:` 前缀提交。
- 周报（team-digest）引用本工具输出作为"质检异常摘要"小节。
