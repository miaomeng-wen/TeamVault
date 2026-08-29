---
name: team-digest
description: 生成 TeamVault 周报：汇总本周新增文献、状态流转、待认领积压与质检异常，写入 08_Daily。用于每周定时巡检汇报或用户临时要求"看看本周进展"。只写 08_Daily 一个文件，不改文献笔记。
---

# team-digest

团队周报生成流程（无独立脚本，按以下步骤操作 vault 即可）。

## 生成流程

1. **确定时间窗**：默认近 7 天；用户指定日期则以指定为准。
2. **取变更清单**：
   ```bat
   git log --since="YYYY-MM-DD" --name-only --pretty=format:"%h %an %ad %s" --date=short
   ```
   无 Git 可用时退化为扫描 `02_Literature` frontmatter 的 `created` 字段。
3. **取质检异常**：运行 `../vault-qa/scripts/vault_qa.py`，摘要 ERR 项。
4. **汇总指标**（读 `02_Literature` 全部笔记 frontmatter）：
   - 新增文献 N 篇（`created` 在时间窗内），按 `theme` 分布，逐篇列出 `[[笔记链接]]` + 一句话来源
   - 状态流转：本周变为 `finished` 的清单；`reading` 中的进行中清单（按 `assignee` 分组）
   - 待认领积压：`assignee` 为空且 `reading_status=unread` 的笔记，按建档时间最旧前 10 篇
   - 质检异常：ERR 条数 + 最常见的 3 类问题
5. **写周报**：`08_Daily/周报-YYYY-MM-DD.md`（周一生成上周报），结构如下：

   ```markdown
   ---
   date: YYYY-MM-DD
   type: 周报
   tags: [digest]
   ---
   # 周报 YYYY-MM-DD ~ YYYY-MM-DD
   ## 本周新增文献（N 篇）
   ## 状态流转
   ## 待认领积压（前 10）
   ## 质检异常
   ## 建议
   （最多 3 条：积压分配、字段补全、主题空缺等）
   ```

## 边界

- 只新建/覆盖 `08_Daily/周报-*.md`，**不修改** `02_Literature`、`04_Tables` 下任何文件。
- 提交信息前缀用 `digest:`（如 `digest: 2026-W35 周报`）。
- 数据只陈述事实（可核对），"建议"一节不超过 3 条且必须由数据支撑。
