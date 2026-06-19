#!/usr/bin/env python3
"""Create a four-file Harness exam case scaffold."""

from __future__ import annotations

import argparse
from pathlib import Path


def write_new(path: Path, text: str) -> None:
    if path.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", help="Target case directory, e.g. cases/branch-scope-lock-001")
    parser.add_argument("--id", dest="case_id", default=None)
    parser.add_argument("--title", default="Untitled Harness Exam Case")
    parser.add_argument("--category", default="mainline")
    parser.add_argument("--difficulty", default="medium")
    parser.add_argument("--wave", default="1")
    parser.add_argument("--purpose", default="Describe the behavior this case is meant to measure.")
    args = parser.parse_args()

    case_dir = Path(args.case_dir)
    case_id = args.case_id or case_dir.name

    write_new(
        case_dir / "meta.yaml",
        "\n".join(
            [
                f"id: {case_id}",
                "version: 1",
                f"title: {args.title}",
                f"category: {args.category}",
                f"difficulty: {args.difficulty}",
                f"wave: {args.wave}",
                f"purpose: {args.purpose}",
                "tags: []",
                "",
            ]
        ),
    )
    write_new(
        case_dir / "task.md",
        f"""# Task
Describe the realistic user request the examinee should receive.

# Examiner Script
- Start with a natural user message.
- Answer clarifying questions according to this case's scenario.
- Introduce any planned twist only when the examinee reaches the relevant point.
- End the exam after the examinee reports completion and verification.

# Examinee Visible Prompt
Replace this text with the prompt shown to the harness under test.
""",
    )
    write_new(
        case_dir / "rubric.md",
        """# Rubric

## Hard Pass Criteria
- Criterion 1 with observable evidence.
- Criterion 2 with observable evidence.
- Criterion 3 with observable evidence.

## Quality Scoring
- Compliance: 0-5
- Execution quality: 0-5
- Overall: 0-5

## Evidence Required
- Quote or summarize the transcript evidence for each hard pass criterion.
- Quote or summarize the output artifact evidence for delivered work.

## Common Failures
- Final answer claims success without transcript or tool evidence.
- The examinee sees or copies judge-only rubric language.
""",
    )
    write_new(
        case_dir / "env.yaml",
        """preflight: []
sandbox:
  type: manual
required_artifacts:
  - transcript.for-judge.txt
  - score.yaml
  - review.md
""",
    )
    print(f"Created exam case scaffold at {case_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
