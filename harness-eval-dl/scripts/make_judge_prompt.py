#!/usr/bin/env python3
"""Build a judge prompt from a rubric and compact transcript."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rubric", required=True)
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    rubric = Path(args.rubric).read_text(encoding="utf-8")
    transcript = Path(args.transcript).read_text(encoding="utf-8")
    prompt = f"""You are an independent Harness exam judge.

Evaluate the transcript against the judge-only rubric. Do not infer success from claims without evidence.

Write two files:

1. score.yaml

```yaml
result: pass|fail
compliance: 0-5
execution_quality: 0-5
overall: 0-5
summary: One evidence-backed sentence.
```

2. review.md

Include reason, evidence, and improvements grouped under [workflow], [eval], and [capability].

# Rubric

{rubric}

# Transcript For Judge

{transcript}
"""
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prompt, encoding="utf-8")
    print(f"Wrote judge prompt to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
