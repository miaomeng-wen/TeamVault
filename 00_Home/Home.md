---
tags: [home]
---

# TeamVault · 首页

> [!tip] 新成员
> 先读 [[../CONTRIBUTING|上手指南]] 装好环境，再浏览 [[建设方案]] 了解整体设计。日常规则见 [[../AGENTS|AGENTS.md]]。

## 看板（自动派生，勿手改）

- [[../04_Tables/团队任务看板|团队任务看板]] — 按人汇总认领与进度、待认领清单
- [[../04_Tables/待读清单|待读清单]] — 未读与在读中的全部文献
- [[../04_Tables/文献索引|文献索引]] — 全库文献总索引

## 文献库

- [[../02_Literature/01_综述论文|01_综述论文]] · [[../02_Literature/02_数据集与基准|02_数据集与基准]] · [[../02_Literature/03_检测方法|03_检测方法]] · [[../02_Literature/04_泛化与鲁棒性|04_泛化与鲁棒性]] · [[../02_Literature/05_评价协议与可复现性|05_评价协议与可复现性]]

## 工作区

- 项目与实验：[[../01_Project|01_Project]] · 概念词典：[[../03_Concepts|03_Concepts]] · 章节笔记：[[../05_Chapter-Notes|05_Chapter-Notes]] · 草稿：[[../06_Drafts|06_Drafts]] · 日报周报：[[../08_Daily|08_Daily]]

## 参考

- 模板：`07_Templates/`（文献笔记 · 概念卡片 · 组会纪要 · 实验记录）
- 智能体技能：`team-skills/`（source-intake · vault-qa · team-digest）

## 最近建档

```dataview
TABLE authors AS 作者, year AS 年份, assignee AS 认领人, reading_status AS 状态
FROM "02_Literature"
SORT created DESC
LIMIT 10
```
