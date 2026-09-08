#!/usr/bin/env python3
from pathlib import Path
from tempfile import TemporaryDirectory

from vault_qa import check_concept, check_note


def main() -> None:
    with TemporaryDirectory() as tmp:
        theme = Path(tmp) / "03_检测方法"
        theme.mkdir()
        note = theme / "Test_2025_Example.md"
        note.write_text(
            """---
title: Example
source_id: doi:10.1234/example
source_type: article
authors: Test
year: 2025
theme: 03_检测方法
reading_status: finished
screening_status: included
created: 2026-08-30
assignee: tester
source_url: https://example.org/paper
pdf_url:
---
## 证据与页码索引
| 证据 | 位置 | 跳转 |
| --- | --- | --- |
| 核心结论 | 第 5 页 | [打开](https://example.org/paper.pdf) |
""",
            encoding="utf-8",
        )
        issues, _ = check_note(note)
        assert not issues, issues

        note.write_text(note.read_text(encoding="utf-8").replace("第 5 页", "第 N 页"), encoding="utf-8")
        issues, _ = check_note(note)
        assert any("缺少带页码的证据" in message for _, message in issues), issues

        # 模板式行内注释：Obsidian/YAML 解析为字段值，质检不得误报
        survey_dir = Path(tmp) / "01_综述论文"
        survey_dir.mkdir()
        survey = survey_dir / "Doe_2024_Example_Survey.md"
        survey.write_text(
            """---
title: Example Survey
aliases: []
tags: []
created: 2026-08-31
assignee:                # 认领人标识：建议统一使用真实中文姓名（一人一标识，全库一致），一篇笔记只有一个认领人
reading_status: unread   # unread | reading | finished | excluded
screening_status: candidate # included | candidate | excluded
source_id: doi:10.1234/survey
source_type: article     # article | conference | book | chapter | report | dataset | web | thesis | other
doi:
source_url: https://example.org/survey#abstract
pdf_url:                 # 团队文件库中的 PDF 稳定链接；没有则留空
authors: Doe; Roe        # 如：Khan; Yu; Wang
year: 2024
source: Example Journal
theme: 01_综述论文        # 归档主题（01_综述论文 … 05_评价协议与可复现性 之一）
study_area: 未核验
---
""",
            encoding="utf-8",
        )
        issues, fm = check_note(survey)
        assert fm.get("reading_status") == "unread", fm
        assert fm.get("screening_status") == "candidate", fm
        assert fm.get("source_type") == "article", fm
        assert fm.get("theme") == "01_综述论文", fm
        assert not any("非法" in message or "不是 HTTP(S)" in message for _, message in issues), issues
        assert any("assignee" in message for _, message in issues), issues  # 空值+注释 → 未填 WARN

        # finished 但未终检通过（screening_status 仍为 candidate）→ ERR
        survey.write_text(
            survey.read_text(encoding="utf-8").replace(
                "reading_status: unread   #", "reading_status: finished  #"
            ),
            encoding="utf-8",
        )
        issues, _ = check_note(survey)
        assert any("screening_status 应为 included" in message for _, message in issues), issues

        # 概念卡片：基础字段齐全 → 无 ERR
        concepts = Path(tmp) / "03_Concepts"
        concepts.mkdir()
        concept = concepts / "cross-dataset-generalization.md"
        concept.write_text(
            """---
title: 跨数据集泛化
tags: [concept]
created: 2026-08-31
assignee: tester
related_sources: [doi:10.1234/survey]
---
## 定义
在训练集之外的数据集上仍保持检测性能的能力。
""",
            encoding="utf-8",
        )
        # 语法检查：包含 ': ' 但未加双引号 → ERR
        survey.write_text(
            survey.read_text(encoding="utf-8").replace(
                "title: Example Survey",
                "title: Example Survey: Datasets and Methods",
            ),
            encoding="utf-8",
        )
        issues, _ = check_note(survey)
        assert any("未加双引号" in message for _, message in issues), issues

        # 加上双引号后 → 消除该 ERR
        survey.write_text(
            survey.read_text(encoding="utf-8").replace(
                "title: Example Survey: Datasets and Methods",
                'title: "Example Survey: Datasets and Methods"',
            ),
            encoding="utf-8",
        )
        issues, _ = check_note(survey)
        assert not any("未加双引号" in message for _, message in issues), issues

    print("vault-qa self-check passed")


if __name__ == "__main__":
    main()
