#!/usr/bin/env python3
"""Batch deploy custom skills, auto-fix links, refresh baselines, and generate inventory reports."""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from install_global_skill import (
    DEFAULT_GLOBAL_REGISTRY,
    DEFAULT_LINK_ROOTS,
    DEFAULT_SEARCH_ROOTS,
    DEFAULT_WRAPPER_BIN,
    create_symlinks,
    create_wrapper,
    find_source_dir,
    same_target,
    supported_link_roots,
    ensure_global_home,
)


DEFAULT_REPORT_DIR = DEFAULT_GLOBAL_REGISTRY / "global-skill-deployer" / "reports"
DEFAULT_BASELINE_FILE = (
    DEFAULT_GLOBAL_REGISTRY / "global-skill-deployer" / "references" / "official-skills.txt"
)
CUSTOM_MANIFEST_NAME = ".custom-skill-manifest.json"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Batch deploy custom skills and generate inventory reports."
    )
    parser.add_argument(
        "--skill-names",
        default="",
        help="Comma-separated skill names to deploy in batch.",
    )
    parser.add_argument(
        "--scan-local-skills",
        action="store_true",
        help="Scan local skill folders for custom skills that are not yet globally linked.",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Skip deployment and only generate inventory reports.",
    )
    parser.add_argument(
        "--global-registry",
        default=str(DEFAULT_GLOBAL_REGISTRY),
        help="Global skill registry. Default: ~/.agents/skills",
    )
    parser.add_argument(
        "--wrapper-bin-dir",
        default=str(DEFAULT_WRAPPER_BIN),
        help="Wrapper bin directory. Default: ~/.local/bin",
    )
    parser.add_argument(
        "--link-targets",
        default="Trae,Trae CN,Claude Code,Hermes,Cursor",
        help="Comma-separated target IDE groups.",
    )
    parser.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory for generated inventory reports.",
    )
    parser.add_argument(
        "--create-wrappers",
        action="store_true",
        help="Try to create CLI wrappers for deployed skills when an entry script can be detected.",
    )
    parser.add_argument(
        "--custom-only",
        action="store_true",
        help="Limit reports and auto-fix actions to custom skills outside the official baseline.",
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Automatically fix missing links, broken links, and detectable wrappers for eligible skills.",
    )
    parser.add_argument(
        "--official-baseline-file",
        default=str(DEFAULT_BASELINE_FILE),
        help="Official skill baseline file used to identify custom skills.",
    )
    parser.add_argument(
        "--refresh-baseline",
        action="store_true",
        help="Rewrite the official baseline file from current global skills excluding manifest-marked custom skills.",
    )
    parser.add_argument(
        "--on-conflict",
        choices=["error", "overwrite", "rename", "skip"],
        default="error",
        help="How to handle conflicts when the skill already exists in the global registry.",
    )
    return parser.parse_args()


def parse_skill_names(raw_value: str) -> List[str]:
    """Parse a comma-separated skill list."""
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def iter_skill_directories(root: Path) -> Iterable[Path]:
    """Yield skill directories containing a SKILL.md file."""
    if not root.exists():
        return []
    return [
        item
        for item in root.iterdir()
        if item.is_dir() and (item / "SKILL.md").exists()
    ]


def scan_local_custom_skills(global_registry: Path) -> List[str]:
    """Find custom local skills that are not already symlinked to the global registry."""
    discovered: List[str] = []
    for root in DEFAULT_SEARCH_ROOTS:
        if not root.exists() or root.resolve() == global_registry.resolve():
            continue
        for skill_dir in iter_skill_directories(root):
            if skill_dir.is_symlink():
                continue
            target_dir = global_registry / skill_dir.name
            if target_dir.exists():
                continue
            if skill_dir.name not in discovered:
                discovered.append(skill_dir.name)
    return sorted(discovered)


def load_official_baseline(baseline_file: Path) -> List[str]:
    """Load the official skill baseline file."""
    if not baseline_file.exists():
        return []
    return [
        line.strip()
        for line in baseline_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def utc_now_iso() -> str:
    """Return a stable UTC timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def custom_manifest_path(skill_dir: Path) -> Path:
    """Return the manifest path for a custom skill."""
    return skill_dir / CUSTOM_MANIFEST_NAME


def load_custom_manifest(skill_dir: Path) -> Dict[str, object]:
    """Load a custom manifest if present."""
    manifest_file = custom_manifest_path(skill_dir)
    if not manifest_file.exists():
        return {}
    return json.loads(manifest_file.read_text(encoding="utf-8"))


def save_custom_manifest(skill_dir: Path, payload: Dict[str, object]) -> Path:
    """Persist a custom manifest."""
    manifest_file = custom_manifest_path(skill_dir)
    manifest_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest_file


def upsert_custom_manifest(
    skill_dir: Path,
    skill_name: str,
    entry_script: str,
    source_dir: str,
    wrapper_path: str,
    event: str,
) -> Path:
    """Create or update the custom manifest for a skill."""
    existing = load_custom_manifest(skill_dir)
    now = utc_now_iso()
    payload = {
        "skill_name": skill_name,
        "managed_by": "global-skill-deployer",
        "is_custom": True,
        "global_source": str(skill_dir),
        "entry_script": entry_script or existing.get("entry_script", ""),
        "source_dir": source_dir or existing.get("source_dir", ""),
        "wrapper_path": wrapper_path or existing.get("wrapper_path", ""),
        "first_managed_at": existing.get("first_managed_at", now),
        "last_updated_at": now,
        "last_event": event,
    }
    return save_custom_manifest(skill_dir, payload)


def auto_detect_entry_script(skill_dir: Path) -> str:
    """Try to infer a sensible CLI entry script for wrapper creation."""
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        candidates = sorted(
            path.relative_to(skill_dir)
            for path in scripts_dir.glob("*.py")
            if path.is_file()
        )
        if len(candidates) == 1:
            return str(candidates[0])

    root_candidates = sorted(
        path.relative_to(skill_dir)
        for path in skill_dir.glob("*.py")
        if path.is_file()
    )
    if len(root_candidates) == 1:
        return str(root_candidates[0])
    return ""


def deploy_skill(
    skill_name: str,
    global_registry: Path,
    link_roots: Sequence[Path],
    wrapper_bin_dir: Path,
    create_wrappers: bool,
    mark_custom: bool,
    on_conflict: str = "error",
) -> Dict[str, object]:
    """Deploy one skill and optionally create a wrapper."""
    source_dir = find_source_dir(skill_name, "", global_registry)
    target_dir = global_registry / skill_name
    moved = False
    if source_dir.resolve() != target_dir.resolve():
        resolved_target = ensure_global_home(source_dir, target_dir, on_conflict)
        if resolved_target is None:
            return {
                "skill_name": skill_name,
                "target_dir": str(target_dir),
                "source_dir": str(source_dir),
                "moved": False,
                "link_summary": [],
                "entry_script": "",
                "wrapper_path": "",
                "manifest_path": "",
                "skipped": True
            }
        target_dir = resolved_target
        moved = True

    link_summary = create_symlinks(skill_name, target_dir, link_roots)
    wrapper_path = None
    entry_script = ""
    if create_wrappers:
        entry_script = auto_detect_entry_script(target_dir)
        if entry_script:
            wrapper_path = create_wrapper(skill_name, target_dir, entry_script, wrapper_bin_dir)

    manifest_path = ""
    if mark_custom:
        manifest_path = str(
            upsert_custom_manifest(
                skill_dir=target_dir,
                skill_name=skill_name,
                entry_script=entry_script,
                source_dir=str(source_dir),
                wrapper_path=str(wrapper_path) if wrapper_path else "",
                event="deploy",
            )
        )

    return {
        "skill_name": skill_name,
        "target_dir": str(target_dir),
        "source_dir": str(source_dir),
        "moved": moved,
        "link_summary": link_summary,
        "entry_script": entry_script,
        "wrapper_path": str(wrapper_path) if wrapper_path else "",
        "manifest_path": manifest_path,
    }


def is_custom_skill(skill_name: str, official_baseline: Sequence[str]) -> bool:
    """Return whether a skill is considered custom."""
    return skill_name not in set(official_baseline)


def link_status(skill_name: str, target_dir: Path, root: Path) -> str:
    """Return a readable link status for one IDE directory."""
    skill_path = root / skill_name
    if not (skill_path.exists() or skill_path.is_symlink()):
        return "missing"
    if same_target(skill_path, target_dir):
        return "linked"
    if skill_path.is_symlink():
        return "points_elsewhere"
    if skill_path.is_dir():
        return "local_dir"
    return "file_conflict"


def wrapper_status(skill_name: str, wrapper_bin_dir: Path) -> Tuple[str, str]:
    """Check whether a CLI wrapper exists and is executable."""
    wrapper_path = wrapper_bin_dir / skill_name
    if not wrapper_path.exists():
        return "missing", str(wrapper_path)
    if wrapper_path.is_file() and wrapper_path.stat().st_mode & 0o111:
        return "ready", str(wrapper_path)
    return "not_executable", str(wrapper_path)


def fix_actions_for_item(item: Dict[str, object]) -> List[str]:
    """Describe fixable actions for one inventory item."""
    actions: List[str] = []
    if item["status"] == "local_only":
        actions.append("promote_to_global")
    for label, state in item["links"].items():
        if state != "linked":
            actions.append(f"fix_link:{label}")
    if item["wrapper_status"] != "ready":
        actions.append("create_wrapper_if_detectable")
    return actions


def should_mark_custom(skill_name: str, official_baseline: Sequence[str], existing_manifest: bool) -> bool:
    """Decide whether a skill should carry a custom manifest."""
    return existing_manifest or is_custom_skill(skill_name, official_baseline)


def discover_inventory_skill_names(global_registry: Path) -> List[str]:
    """Collect skill names from global and local roots for reporting."""
    names = set()
    for skill_dir in iter_skill_directories(global_registry):
        names.add(skill_dir.name)
    for root in DEFAULT_SEARCH_ROOTS:
        if not root.exists():
            continue
        for skill_dir in iter_skill_directories(root):
            names.add(skill_dir.name)
    return sorted(names)


def build_inventory(
    global_registry: Path,
    wrapper_bin_dir: Path,
    official_baseline: Sequence[str],
    custom_only: bool,
) -> Dict[str, object]:
    """Build a full skill inventory report."""
    items: List[Dict[str, object]] = []
    for skill_name in discover_inventory_skill_names(global_registry):
        target_dir = global_registry / skill_name
        manifest = load_custom_manifest(target_dir) if target_dir.exists() else {}
        custom_skill = should_mark_custom(skill_name, official_baseline, bool(manifest))
        if custom_only and not custom_skill:
            continue
        global_exists = target_dir.exists()
        link_map = {
            label: link_status(skill_name, target_dir, root)
            for label, root in DEFAULT_LINK_ROOTS.items()
        }
        wrapper_state, wrapper_path = wrapper_status(skill_name, wrapper_bin_dir)
        status = "global" if global_exists else "local_only"
        if global_exists and all(value == "linked" for value in link_map.values()):
            status = "healthy"
        elif global_exists:
            status = "needs_attention"

        items.append(
            {
                "skill_name": skill_name,
                "is_custom": custom_skill,
                "status": status,
                "global_source": str(target_dir) if global_exists else "",
                "links": link_map,
                "wrapper_status": wrapper_state,
                "wrapper_path": wrapper_path,
                "manifest_path": str(custom_manifest_path(target_dir)) if manifest else "",
                "manifest_exists": bool(manifest),
                "fix_actions": [],
                "fixable": False,
            }
        )

    for item in items:
        actions = fix_actions_for_item(item)
        item["fix_actions"] = actions
        item["fixable"] = bool(actions) and item["is_custom"]

    summary = {
        "total_skills": len(items),
        "healthy": sum(1 for item in items if item["status"] == "healthy"),
        "needs_attention": sum(1 for item in items if item["status"] == "needs_attention"),
        "local_only": sum(1 for item in items if item["status"] == "local_only"),
        "custom_skills": sum(1 for item in items if item["is_custom"]),
    }
    return {"summary": summary, "skills": items}


def inventory_file_names(custom_only: bool) -> Tuple[str, str]:
    """Return output filenames for inventory reports."""
    if custom_only:
        return "custom_skill_inventory.json", "custom_skill_inventory.md"
    return "global_skill_inventory.json", "global_skill_inventory.md"


def write_inventory_files(
    inventory: Dict[str, object],
    report_dir: Path,
    custom_only: bool,
) -> Tuple[Path, Path]:
    """Write inventory JSON and markdown reports."""
    report_dir.mkdir(parents=True, exist_ok=True)
    json_name, md_name = inventory_file_names(custom_only)
    json_path = report_dir / json_name
    md_path = report_dir / md_name

    json_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Custom Skill Inventory" if custom_only else "# Global Skill Inventory",
        "",
        "## Summary",
        "",
        f"- Total skills: {inventory['summary']['total_skills']}",
        f"- Custom skills: {inventory['summary']['custom_skills']}",
        f"- Healthy: {inventory['summary']['healthy']}",
        f"- Needs attention: {inventory['summary']['needs_attention']}",
        f"- Local only: {inventory['summary']['local_only']}",
        "",
        "## Skills",
        "",
        "| Skill | Custom | Status | Trae | Trae CN | Claude | Hermes | Cursor | Wrapper | Fixable |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in inventory["skills"]:
        links = item["links"]
        lines.append(
            "| {skill} | {custom} | {status} | {trae} | {traecn} | {claude} | {hermes} | {cursor} | {wrapper} | {fixable} |".format(
                skill=item["skill_name"],
                custom="yes" if item["is_custom"] else "no",
                status=item["status"],
                trae=links["Trae"],
                traecn=links["Trae CN"],
                claude=links["Claude Code"],
                hermes=links["Hermes"],
                cursor=links["Cursor"],
                wrapper=item["wrapper_status"],
                fixable="yes" if item["fixable"] else "no",
            )
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def auto_fix_inventory_items(
    inventory: Dict[str, object],
    global_registry: Path,
    link_roots: Sequence[Path],
    wrapper_bin_dir: Path,
    official_baseline: Sequence[str],
) -> List[Dict[str, object]]:
    """Apply auto-fix actions to eligible custom skills."""
    results: List[Dict[str, object]] = []
    for item in inventory["skills"]:
        if not item["fixable"]:
            continue

        skill_name = item["skill_name"]
        skill_result = deploy_skill(
            skill_name=skill_name,
            global_registry=global_registry,
            link_roots=link_roots,
            wrapper_bin_dir=wrapper_bin_dir,
            create_wrappers=True,
            mark_custom=should_mark_custom(skill_name, official_baseline, item["manifest_exists"]),
            on_conflict="overwrite",  # Auto-fix defaults to overwrite if re-deploying
        )
        results.append(
            {
                "skill_name": skill_name,
                "actions": item["fix_actions"],
                "wrapper_path": skill_result["wrapper_path"],
                "target_dir": skill_result["target_dir"],
            }
        )
    return results


def refresh_official_baseline(global_registry: Path, baseline_file: Path) -> Path:
    """Rewrite the official baseline file from current global skills excluding manifest-marked custom skills."""
    baseline_file.parent.mkdir(parents=True, exist_ok=True)
    official_skills = []
    for skill_dir in iter_skill_directories(global_registry):
        if load_custom_manifest(skill_dir):
            continue
        official_skills.append(skill_dir.name)
    baseline_file.write_text("\n".join(sorted(official_skills)) + "\n", encoding="utf-8")
    return baseline_file


def sync_manifests_for_detected_custom_skills(
    inventory: Dict[str, object],
    global_registry: Path,
) -> List[str]:
    """Backfill or enrich manifests for currently detected custom skills."""
    changed: List[str] = []
    for item in inventory["skills"]:
        if not item["is_custom"]:
            continue
        skill_dir = global_registry / item["skill_name"]
        entry_script = auto_detect_entry_script(skill_dir)
        existing = load_custom_manifest(skill_dir)
        source_dir = existing.get("source_dir", "") or str(skill_dir)
        wrapper_path = existing.get("wrapper_path", "")
        if item["wrapper_status"] == "ready":
            wrapper_path = item["wrapper_path"]

        needs_update = (
            not existing
            or not existing.get("entry_script")
            or not existing.get("source_dir")
            or (item["wrapper_status"] == "ready" and existing.get("wrapper_path") != item["wrapper_path"])
        )
        if not needs_update:
            continue
        manifest_path = upsert_custom_manifest(
            skill_dir=skill_dir,
            skill_name=item["skill_name"],
            entry_script=entry_script,
            source_dir=source_dir,
            wrapper_path=wrapper_path,
            event="baseline_refresh_sync",
        )
        changed.append(str(manifest_path))
    return changed


def main() -> int:
    """Run batch deployment and inventory generation."""
    args = parse_args()
    global_registry = Path(args.global_registry).expanduser().resolve()
    wrapper_bin_dir = Path(args.wrapper_bin_dir).expanduser().resolve()
    link_roots = supported_link_roots(args.link_targets.split(","))
    report_dir = Path(args.report_dir).expanduser().resolve()
    official_baseline_file = Path(args.official_baseline_file).expanduser().resolve()
    official_baseline = load_official_baseline(official_baseline_file)

    selected_skills = set(parse_skill_names(args.skill_names))
    if args.scan_local_skills:
        selected_skills.update(scan_local_custom_skills(global_registry))

    deployment_results: List[Dict[str, object]] = []
    if not args.report_only:
        for skill_name in sorted(selected_skills):
            custom_skill = is_custom_skill(skill_name, official_baseline)
            deployment_results.append(
                deploy_skill(
                    skill_name=skill_name,
                    global_registry=global_registry,
                    link_roots=link_roots,
                    wrapper_bin_dir=wrapper_bin_dir,
                    create_wrappers=args.create_wrappers,
                    mark_custom=custom_skill or args.custom_only,
                    on_conflict=args.on_conflict,
                )
            )

    inventory = build_inventory(
        global_registry=global_registry,
        wrapper_bin_dir=wrapper_bin_dir,
        official_baseline=official_baseline,
        custom_only=args.custom_only,
    )
    baseline_refresh_manifest_updates: List[str] = []
    if args.refresh_baseline:
        baseline_refresh_manifest_updates = sync_manifests_for_detected_custom_skills(
            inventory=inventory,
            global_registry=global_registry,
        )
        baseline_file = refresh_official_baseline(global_registry, official_baseline_file)
        official_baseline = load_official_baseline(baseline_file)
        inventory = build_inventory(
            global_registry=global_registry,
            wrapper_bin_dir=wrapper_bin_dir,
            official_baseline=official_baseline,
            custom_only=args.custom_only,
        )

    auto_fix_results: List[Dict[str, object]] = []
    if args.auto_fix:
        auto_fix_results = auto_fix_inventory_items(
            inventory=inventory,
            global_registry=global_registry,
            link_roots=link_roots,
            wrapper_bin_dir=wrapper_bin_dir,
            official_baseline=official_baseline,
        )
        inventory = build_inventory(
            global_registry=global_registry,
            wrapper_bin_dir=wrapper_bin_dir,
            official_baseline=official_baseline,
            custom_only=args.custom_only,
        )

    json_path, md_path = write_inventory_files(
        inventory=inventory,
        report_dir=report_dir,
        custom_only=args.custom_only,
    )

    print("Batch deployment complete")
    if deployment_results:
        for result in deployment_results:
            if result.get("skipped"):
                print(f"- skipped: {result['skill_name']} (conflict encountered)")
            else:
                print(f"- deployed: {result['skill_name']} -> {result['target_dir']}")
                if result.get("wrapper_path"):
                    print(f"  wrapper: {result['wrapper_path']}")
    else:
        print("- no deployment actions were run")
    if auto_fix_results:
        for result in auto_fix_results:
            print(f"- auto-fixed: {result['skill_name']} ({', '.join(result['actions'])})")
    if args.refresh_baseline:
        for manifest_path in baseline_refresh_manifest_updates:
            print(f"- manifest synced: {manifest_path}")
        print(f"- refreshed baseline: {official_baseline_file}")
    print(f"- inventory json: {json_path}")
    print(f"- inventory md: {md_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
