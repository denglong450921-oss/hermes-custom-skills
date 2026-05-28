#!/usr/bin/env python3
"""Inject 5-module harness into a target skill. Supports --check mode and non-HTML skills."""

import json, sys, os, re, shutil, argparse
from pathlib import Path

HERE = Path(__file__).parent.parent
TEMPLATE = HERE / "references/templates/evals-template.json"

# Standard harness checklist
HARNESS_CHECKS = [
    ("evals/", "dir"),
    ("evals/evals.json", "file"),
    ("evals/grader.py", "file"),
    ("evals/run_harness.py", "file"),
    ("SKILL.md", "file"),
]


def check_skill(skill_path):
    """Check if skill already has harness components. Returns (present, missing)."""
    skill = Path(skill_path).expanduser()
    present = []
    missing = []
    
    for path, check_type in HARNESS_CHECKS:
        full_path = skill / path
        if check_type == "dir" and full_path.is_dir():
            present.append(path)
        elif check_type == "file" and full_path.is_file():
            present.append(path)
        else:
            missing.append(path)
    
    # Check Harness section in SKILL.md
    skmd = skill / "SKILL.md"
    harness_has_section = False
    honesty_has_section = False
    if skmd.is_file():
        content = skmd.read_text(encoding="utf-8", errors="replace")
        harness_has_section = bool(re.search(r"## Harness", content))
        honesty_has_section = bool(re.search(r"防止模型说谎|Honesty.*Truthfulness", content))
    
    return {
        "present": present,
        "missing": missing,
        "has_harness_section": harness_has_section,
        "has_honesty_section": honesty_has_section,
    }


def inject(skill_path, with_feedback=False, with_honesty=False, force=False):
    skill = Path(skill_path).expanduser()
    skill_md = skill / "SKILL.md"
    evals_dir = skill / "evals"
    feedback_dir = skill / "feedback"

    if not skill_md.exists():
        print(f"❌ SKILL.md not found at {skill_md}")
        return False

    # 0. Check existing harness
    status = check_skill(skill_path)
    
    # Determine injection mode based on skill type
    is_html = False
    if skill_md.is_file():
        content = skill_md.read_text(encoding="utf-8", errors="replace")
        is_html = bool(re.search(r'\.container|output\.css|HTML|html|class="', content, re.I))
    
    mode = "html" if is_html else "non-html"
    
    print(f"  Target: {skill.name} ({skill})")
    print(f"  Mode:   {mode}")
    
    if status["missing"]:
        print(f"  Missing: {', '.join(status['missing'])}")
    if status["present"]:
        print(f"  Has:     {', '.join(status['present'])}")
    if status["has_harness_section"]:
        print(f"  Harness section: ✅")
    if status["has_honesty_section"]:
        print(f"  Honesty section: ✅")
    
    # Skip if fully harnessed and not forced
    if (not status["missing"] and status["has_harness_section"]) and not force:
        print(f"\n  ⏭️  Skill already has full harness. Use --force to re-inject.")
        return True
    
    # 1. Read existing SKILL.md
    content = skill_md.read_text(encoding="utf-8", errors="replace")
    name = skill.name
    # Try to get name from frontmatter
    for line in content.split("\n"):
        if line.startswith("name:"):
            name = line.split("name:")[1].strip()
            break

    # 2. Create evals/ directory
    evals_dir.mkdir(exist_ok=True)
    
    if mode == "html":
        # Copy from html-output (CSS class checks)
        ref_grader = HERE.parent / "html-output/evals/grader.py"
        ref_runner = HERE.parent / "html-output/evals/run_harness.py"
    else:
        # Copy generic reference from within skill-harness
        ref_grader = HERE / "references/templates/generic_grader.py"
        ref_runner = HERE / "references/templates/generic_runner.py"
        
        # Create generic templates if they don't exist
        HERE.joinpath("references/templates").mkdir(parents=True, exist_ok=True)
        if not ref_grader.exists():
            ref_grader.write_text(_GENERIC_GRADER_TEMPLATE)
        if not ref_runner.exists():
            ref_runner.write_text(_GENERIC_RUNNER_TEMPLATE)
    
    for src, dst_name in [(ref_grader, "grader.py"), (ref_runner, "run_harness.py")]:
        if src.exists():
            dst = evals_dir / dst_name
            shutil.copy(src, dst)
            print(f"  ✅ {dst_name} copied ({mode} mode)")
        else:
            print(f"  ⚠️  {src} not found, skipping")

    # 3. Generate evals.json from template or create minimal
    if TEMPLATE.exists():
        evals_json = json.loads(TEMPLATE.read_text())
        evals_json["skill_name"] = name
        evals_json["description"] = f"Harness for {name} skill"
        print(f"  ✅ evals.json template created (needs real tasks filled in)")
    else:
        evals_json = {
            "skill_name": name,
            "description": f"Harness for {name} skill",
            "harness_version": "1.0",
            "evals": [
                {
                    "id": "case_001",
                    "task": f"Realistic task for {name} — replace with actual prompt",
                    "environment": {"files": [], "tools_available": []},
                    "tools": [],
                    "grader": {"must_use": [], "must_have": [], "must_not_have": []},
                },
                {
                    "id": "case_002",
                    "task": f"Another distinct task for {name}",
                    "environment": {"files": [], "tools_available": []},
                    "tools": [],
                    "grader": {"must_use": [], "must_have": [], "must_not_have": []},
                },
                {
                    "id": "case_003",
                    "task": f"A third distinct task for {name}",
                    "environment": {"files": [], "tools_available": []},
                    "tools": [],
                    "grader": {"must_use": [], "must_have": [], "must_not_have": []},
                },
            ],
        }

    (evals_dir / "evals.json").write_text(
        json.dumps(evals_json, indent=2, ensure_ascii=False)
    )
    print(f"  📄 evals/evals.json")

    # 4. Patch SKILL.md with Harness section
    harness_section = _build_harness_section(name, mode, with_honesty)

    if "## Harness" not in content:
        content = content.rstrip() + "\n" + harness_section
        skill_md.write_text(content)
        print(f"  ✅ Harness section added to SKILL.md")
    else:
        print(f"  ⏭️  Harness section already exists, skipped")

    # 5. Optional: Scaffold feedback/ directory
    if with_feedback:
        _scaffold_feedback(feedback_dir)

    print(f"\n  Done. Next steps:")
    print(f"  1. Edit evals/evals.json — fill in real tasks")
    print(f"  2. {'Edit grader.py with domain-specific checks' if mode == 'non-html' else 'Verify grader.py checks match your HTML classes'}")
    print(f"  3. Run: python3 evals/run_harness.py <output>")
    
    if not status["has_honesty_section"] and with_honesty:
        print(f"  ⚠️  --with-honesty was specified but skill already has Honesty section")
    
    return True


def _build_harness_section(name, mode, with_honesty):
    """Build the Harness section for SKILL.md."""
    is_html = mode == "html"
    
    checks_table = """| Check | Detects |
|-------|---------|
| has_class_container | `.container` CSS class |
| has_table | `<table>` with `<thead>` |
| has_callout | `.callout` class |
| has_steps | `.steps` class |
| has_details | `<details>`/`<summary>` elements |
| has_highlight | `.highlight` stat block |
| has_tag | `.tag` pill label |
| has_meta | `.meta` class |
| has_insight | `.insight` class |
| has_hr | `<hr>` element |"""
    
    if not is_html:
        checks_table = """| Check | Detects |
|-------|---------|
| `script_ran_successfully` | No fatal errors in output |
| `manifest_created` | Output manifest referenced |
| `file_generated` | Expected output files mentioned |
| `output_directory_listed` | Output directory path |"""
    
    honesty_section = f"""\n| `reports_failure_honestly` | Failure details not masked |
| `no_defensive_disclaimers` | Correct results not undermined |
| `no_false_success` | No false success claims |""" if with_honesty else ""
    
    return f"""
## Harness (Self-Eval)

This skill has a built-in eval harness following the Agent Harness 5-module pattern.

### Task (what to test)
Define 3+ eval cases in `evals/evals.json` — each with task, environment, tools, grader.

### Environment
- `{'references/output.css' if is_html else 'scripts/<main-script>.py'}` — {'layout stylesheet' if is_html else 'main orchestrator'}
- Document any config or dependencies

### Tools
{'`scripts/<main_script>.py` — customize per skill' if not is_html else '`.container` `.card-grid` `.card` `.num` `.tag` `.callout` `.insight` `.highlight` `.steps` `details`/`summary` `table` `blockquote` `.meta`'}

### Grader
Run the harness on any generated output:

```bash
# Full harness run (tests all 3 cases against one output)
python3 evals/run_harness.py <output-file>

# Or run individual checks
python3 evals/grader.py <output-file> '<checks-json>'
```

### Checks

{checks_table}{honesty_section}

### Eval flow
1. Define cases in evals/evals.json
2. Follow skill instructions to produce output
3. Run grader to verify assertions
4. Fix failures, re-output, re-check
"""


def _scaffold_feedback(feedback_dir):
    """Scaffold the feedback/ directory for the feedback loop."""
    feedback_dir.mkdir(exist_ok=True)
    
    # Create empty failures.jsonl
    failures_file = feedback_dir / "failures.jsonl"
    if not failures_file.exists():
        failures_file.touch()
        print(f"  ✅ failures.jsonl created")
    
    # Copy distill.py and ftpr.py from this skill's scripts
    for name in ["distill.py", "ftpr.py"]:
        src = HERE / "scripts" / name
        if src.exists():
            dst = feedback_dir / name
            shutil.copy(src, dst)
            print(f"  ✅ {name} copied to feedback/")
    
    # Create empty rules.md
    rules_md = feedback_dir / "rules.md"
    if not rules_md.exists():
        rules_md.write_text("# Harness-Distilled Rules\n\n(Rules will be populated by distill.py)\n")
        print(f"  ✅ rules.md created")
    
    print(f"  📄 feedback/ directory scaffolded")
    print(f"  To use the feedback loop:")
    print(f"  1. Run harness: python3 evals/run_harness.py <output>")
    print(f"  2. Distill:     python3 feedback/distill.py feedback/failures.jsonl")
    print(f"  3. Check FTPR:  python3 feedback/ftpr.py feedback/failures.jsonl --total-runs <N>")


# Templates for non-HTML skills
_GENERIC_GRADER_TEMPLATE = HERE / "references/templates/generic_grader.py"
_GENERIC_RUNNER_TEMPLATE = HERE / "references/templates/generic_runner.py"


def main():
    parser = argparse.ArgumentParser(
        description="Inject 5-module Agent Harness into a skill, or check existing harness."
    )
    parser.add_argument("skill_path", help="Path to skill directory")
    parser.add_argument("--check", action="store_true",
                        help="Check harness compliance without modifying anything")
    parser.add_argument("--with-feedback", action="store_true",
                        help="Scaffold feedback/ directory for evolution engine")
    parser.add_argument("--with-honesty", action="store_true",
                        help="Include honesty/truthfulness constraints section")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Re-inject even if harness already exists")
    
    args = parser.parse_args()
    
    skill_path = Path(args.skill_path).expanduser()
    if not skill_path.is_dir():
        print(f"❌ Not a directory: {skill_path}", file=sys.stderr)
        sys.exit(1)
    
    if args.check:
        # Run check mode
        from importlib.util import spec_from_file_location, module_from_spec
        check_path = HERE / "scripts" / "check_harness.py"
        spec = spec_from_file_location("check_harness", check_path)
        mod = module_from_spec(spec)
        sys.argv = ["check_harness.py", str(skill_path)]
        spec.loader.exec_module(mod)
        return
    
    # Inject mode
    inject(
        skill_path,
        with_feedback=args.with_feedback,
        with_honesty=args.with_honesty,
        force=args.force,
    )


if __name__ == "__main__":
    main()
