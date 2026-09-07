---
name: source-intake
description: 将 DOI、来源 URL、PDF 链接或人工元数据整理为 TeamVault 文献笔记。用于新来源建档、按 source_id 查重、补全已有来源和认领前准备；不上传、移动或删除团队文件库中的文件。
---

# source-intake

把一个来源整理成可查重、可认领、可追溯的 `02_Literature` 笔记。

## 来源标识

按以下优先级生成 `source_id`：

1. 有 DOI：`doi:<小写 DOI>`，去掉 `https://doi.org/`、`doi:` 与首尾空白。
2. 无 DOI 但有稳定来源页：`url:<规范化 URL>`，移除跟踪参数和片段。
3. 两者都没有：`manual:<UUID>`。

写入前必须用 `rg` 在 `02_Literature` 搜索完整 `source_id`；已存在时补全原笔记，不创建副本。原笔记已有其他 `assignee` 时只报告位置，不修改。

## 建档流程

1. 读取 vault 根目录的 `AGENTS.md` 与 `07_Templates/文献笔记模板.md`。
2. 从用户提供的 DOI、URL、PDF 或元数据提取可核验字段；标题若含冒号（`: `）等特殊字符必须用双引号包裹（如 `title: "..."`）以防 YAML 报错；无法核验的内容写“未核验”，不猜测。
3. 按主要贡献选择唯一主题目录，文件名使用 `作者_年份_短标题.md`。
4. 新笔记默认 `reading_status: unread`、`screening_status: candidate`；只有用户明确认领时才填写 `assignee` 并改为 `reading`。
5. `source_url` 保存来源主页，`pdf_url` 保存团队文件库中的稳定链接。没有 PDF 链接可以留空，不得把 PDF 复制进 Git。
6. 运行 `team-skills/vault-qa/scripts/vault_qa.py --vault <vault>`；有 ERR 时修复自己新建或认领的笔记后再提交。

## 边界

- 不上传、移动或删除团队文件库文件，除非用户明确要求并提供对应权限。
- 不批量改写已有笔记；批量导入须先取得团队确认。
- 不修改 `04_Tables` 派生页。
- 证据必须记录页码并链接 `pdf_url` 或 `source_url`；未读到的内容不补造。
