#!/usr/bin/env python3
from pathlib import Path
from tempfile import TemporaryDirectory

from vault_qa import check_note


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

    print("vault-qa self-check passed")


if __name__ == "__main__":
    main()
