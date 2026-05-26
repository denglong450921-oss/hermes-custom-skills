#!/usr/bin/env python3
"""Inject 5-module harness into a target skill. Generates evals/ + patches SKILL.md."""

import json, sys, os, re, shutil
from pathlib import Path

HERE = Path(__file__).parent.parent
TEMPLATE = HERE / "references/templates/evals-template.json"

def inject(skill_path, with_feedback=False):
    skill = Path(skill_path).expanduser()
    skill_md = skill / "SKILL.md"
    evals_dir = skill / "evals"
    feedback_dir = skill / "feedback"

    if not skill_md.exists():
        print(f"❌ SKILL.md not found at {skill_md}")
        return False

    # 1. Read existing SKILL.md
    content = skill_md.read_text()
    name = "unknown"
    for line in content.split("\n"):
        if line.startswith("name:"):
            name = line.split("name:")[1].strip()

    print(f"  Target: {name} ({skill})")

    # 2. Create evals/ directory + copy grader + runner from reference skill
    evals_dir.mkdir(exist_ok=True)

    # Copy grader.py and run_harness.py from html-output skill
    ref_grader = HERE.parent / "html-output/evals/grader.py"
    ref_runner = HERE.parent / "html-output/evals/run_harness.py"
    if ref_grader.exists():
        shutil.copy(ref_grader, evals_dir / "grader.py")
        print(f"  ✅ grader.py copied")
    if ref_runner.exists():
        shutil.copy(ref_runner, evals_dir / "run_harness.py")
        print(f"  ✅ run_harness.py copied")

    # 3. Generate evals.json from template
    if TEMPLATE.exists():
        evals_json = json.loads(TEMPLATE.read_text())
        evals_json["skill_name"] = name
        evals_json["description"] = f"Harness for {name} skill"
        print(f"  ✅ evals.json created (needs task editing)")
    else:
        evals_json = {"skill_name": name, "evals": []}

    (evals_dir / "evals.json").write_text(json.dumps(evals_json, indent=2, ensure_ascii=False))
    print(f"  📄 evals/evals.json")

    # 4. Patch SKILL.md with Harness section
    harness_section = f"""
## Harness (Self-Eval)

This skill has a built-in eval harness following the Agent Harness 5-module pattern.

### Task (what to test)
Define 3+ eval cases in `evals/evals.json` — each with task, environment, tools, grader.

### Environment
- Files and tools available at runtime
- Document any config or dependencies

### Tools
List the tools/classes/capabilities this skill provides.

### Trace
Each run produces a JSON trace: task → tools called → result → grade.

### Grader
Run the grader on any output:
```bash
python3 evals/grader.py <output-file> '<checks-json>'
python3 evals/run_harness.py <output-file>
```
Checks available: has_class_container, has_table, has_callout, has_steps, has_details, has_highlight, has_tag, has_meta, has_insight, has_hr

### Eval flow
1. Define cases in evals/evals.json
2. Follow skill instructions to produce output
3. Run grader to verify assertions
4. Fix failures, re-output, re-check
"""

    if "## Harness" not in content:
        content = content.rstrip() + "\n" + harness_section
        skill_md.write_text(content)
        print(f"  ✅ Harness section added to SKILL.md")
    else:
        print(f"  ⏭️  Harness section already exists, skipped")

    # 5. Optional: Scaffold feedback/ directory for feedback loop
    if with_feedback:
        feedback_dir.mkdir(exist_ok=True)

        # Create empty failures.jsonl
        failures_file = feedback_dir / "failures.jsonl"
        if not failures_file.exists():
            failures_file.touch()
            print(f"  ✅ failures.jsonl created")

        # Copy distill.py and ftpr.py from this skill's scripts
        ref_distill = HERE / "scripts/distill.py"
        ref_ftpr = HERE / "scripts/ftpr.py"
        for src in [ref_distill, ref_ftpr]:
            if src.exists():
                dst = feedback_dir / src.name
                shutil.copy(src, dst)
                print(f"  ✅ {src.name} copied to feedback/")

        # Create empty rules.md
        rules_md = feedback_dir / "rules.md"
        if not rules_md.exists():
            rules_md.write_text("# Harness-Distilled Rules\n\n"
                                "(Rules will be populated by distill.py)\n")
            print(f"  ✅ rules.md created")

        print(f"  📄 feedback/ directory scaffolded")
        print(f"  📄  ├── failures.jsonl    (append-only error log)")
        print(f"  📄  ├── distill.py        (error distiller)")
        print(f"  📄  ├── ftpr.py           (FTPR calculator)")
        print(f"  📄  └── rules.md          (distilled rules)")
        print(f"")
        print(f"  To use the feedback loop:")
        print(f"  1. Run harness: python3 evals/run_harness.py <output>")
        print(f"  2. Distill:     python3 feedback/distill.py feedback/failures.jsonl")
        print(f"  3. Check FTPR:  python3 feedback/ftpr.py feedback/failures.jsonl --total-runs <N>")
        print(f"")

    print(f"\n  Done. Next steps:")
    print(f"  1. Edit evals/evals.json — fill in __EVAL_TASK_1__ etc with real prompts")
    print(f"  2. Update grader checks to match this skill's actual outputs")
    print(f"  3. Run: python3 evals/run_harness.py <output>")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/inject.py ~/.hermes/skills/<target-skill> [--with-feedback]")
        print("")
        print("Injects a 5-module Agent Harness into any skill:")
        print("  1. Creates evals/ directory with grader.py + run_harness.py")
        print("  2. Generates evals.json template (needs real prompts filled in)")
        print("  3. Adds Harness section to SKILL.md")
        print("  4. (--with-feedback) Scaffolds feedback/ directory for feedback loop")
        sys.exit(1)

    feedback = "--with-feedback" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    inject(args[0], with_feedback=feedback)
