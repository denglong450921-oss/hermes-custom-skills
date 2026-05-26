#!/usr/bin/env python3
"""Promote a local skill into a global registry and fan it out with symlinks."""

import argparse
import shutil
import sys
import time
from pathlib import Path
from typing import Iterable, List, Optional


DEFAULT_GLOBAL_REGISTRY = Path.home() / ".agents" / "skills"
DEFAULT_WRAPPER_BIN = Path.home() / ".local" / "bin"
DEFAULT_SEARCH_ROOTS = [
    Path.home() / ".trae" / "skills",
    Path.home() / ".trae-cn" / "skills",
    Path.home() / ".claude" / "skills",
    Path.home() / ".hermes" / "skills",
    Path.home() / ".cursor" / "skills",
    DEFAULT_GLOBAL_REGISTRY,
]
DEFAULT_LINK_ROOTS = {
    "Trae": Path.home() / ".trae" / "skills",
    "Trae CN": Path.home() / ".trae-cn" / "skills",
    "Claude Code": Path.home() / ".claude" / "skills",
    "Hermes": Path.home() / ".hermes" / "skills",
    "Cursor": Path.home() / ".cursor" / "skills",
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Move a skill into the global registry, create IDE symlinks, and optionally create a CLI wrapper."
    )
    parser.add_argument("--skill-name", required=True, help="Skill directory name.")
    parser.add_argument("--source-dir", default="", help="Explicit source directory for the skill.")
    parser.add_argument(
        "--global-registry",
        default=str(DEFAULT_GLOBAL_REGISTRY),
        help="Global skill registry. Default: ~/.agents/skills",
    )
    parser.add_argument(
        "--entry-script",
        default="",
        help="Relative path to a runnable script inside the skill, used to create a CLI wrapper.",
    )
    parser.add_argument(
        "--wrapper-bin-dir",
        default=str(DEFAULT_WRAPPER_BIN),
        help="Directory for generated CLI wrappers. Default: ~/.local/bin",
    )
    parser.add_argument(
        "--skip-wrapper",
        action="store_true",
        help="Skip creating the CLI wrapper even if --entry-script is provided.",
    )
    parser.add_argument(
        "--link-targets",
        default="Trae,Trae CN,Claude Code,Hermes,Cursor",
        help="Comma-separated target IDE groups. Supported: Trae, Trae CN, Claude Code, Hermes, Cursor",
    )
    parser.add_argument(
        "--on-conflict",
        choices=["error", "overwrite", "rename", "skip"],
        default="error",
        help="How to handle conflicts when the skill already exists in the global registry."
    )
    return parser.parse_args()


def normalize_label(label: str) -> str:
    """Normalize a link target label."""
    return " ".join(label.strip().split())


def supported_link_roots(selected_labels: Iterable[str]) -> List[Path]:
    """Resolve requested label names into link directories."""
    resolved: List[Path] = []
    for raw_label in selected_labels:
        label = normalize_label(raw_label)
        if not label:
            continue
        if label not in DEFAULT_LINK_ROOTS:
            raise ValueError(f"Unsupported link target: {label}")
        resolved.append(DEFAULT_LINK_ROOTS[label])
    return resolved


def find_source_dir(skill_name: str, explicit_source_dir: str, global_registry: Path) -> Path:
    """Find the most appropriate source directory for the skill."""
    if explicit_source_dir:
        source_dir = Path(explicit_source_dir).expanduser().resolve()
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory does not exist: {source_dir}")
        return source_dir

    target_dir = global_registry / skill_name
    if target_dir.exists():
        return target_dir

    for root in DEFAULT_SEARCH_ROOTS:
        candidate = root / skill_name
        if candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(f"Could not locate skill '{skill_name}' in default search roots.")


def timestamp_suffix() -> str:
    """Build a backup timestamp."""
    return time.strftime("%Y%m%d-%H%M%S")


def backup_path(path: Path) -> Path:
    """Return a backup path next to the existing path."""
    return path.with_name(f"{path.name}.bak-{timestamp_suffix()}")


def same_target(link_path: Path, target_dir: Path) -> bool:
    """Return whether a path already resolves to the requested target."""
    if not (link_path.exists() or link_path.is_symlink()):
        return False
    try:
        return link_path.resolve() == target_dir.resolve()
    except FileNotFoundError:
        return False


def ensure_global_home(source_dir: Path, target_dir: Path, on_conflict: str = "error") -> Optional[Path]:
    """Ensure the skill lives in the global registry.
    Returns the resolved target directory, or None if skipped."""
    if source_dir.resolve() == target_dir.resolve():
        return target_dir

    if target_dir.exists() or target_dir.is_symlink():
        if on_conflict == "error":
            raise FileExistsError(f"Global target already exists and differs from source: {target_dir}")
        elif on_conflict == "skip":
            print(f"Skipping copy due to conflict. Keeping existing: {target_dir}")
            return None
        elif on_conflict == "overwrite":
            print(f"Overwriting existing target: {target_dir}")
            if target_dir.is_symlink() or target_dir.is_file():
                target_dir.unlink()
            else:
                shutil.rmtree(target_dir)
        elif on_conflict == "rename":
            original_name = target_dir.name
            counter = 1
            while target_dir.exists() or target_dir.is_symlink():
                target_dir = target_dir.with_name(f"{original_name}-local{counter}")
                counter += 1
            print(f"Renamed target to avoid conflict: {target_dir}")

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source_dir), str(target_dir))
    return target_dir


def replace_with_symlink(link_path: Path, target_dir: Path) -> Optional[Path]:
    """Create or refresh a symlink. Backup conflicting content instead of deleting it."""
    if same_target(link_path, target_dir):
        return None

    if link_path.exists() or link_path.is_symlink():
        if link_path.is_symlink() or link_path.is_file():
            backup = backup_path(link_path)
            link_path.rename(backup)
            link_path.symlink_to(target_dir, target_is_directory=True)
            return backup
        backup = backup_path(link_path)
        link_path.rename(backup)
        link_path.symlink_to(target_dir, target_is_directory=True)
        return backup

    link_path.symlink_to(target_dir, target_is_directory=True)
    return None


def create_symlinks(skill_name: str, target_dir: Path, link_roots: Iterable[Path]) -> List[str]:
    """Create symlinks for the skill in each requested IDE directory."""
    summaries: List[str] = []
    for root in link_roots:
        if not root.parent.exists():
            summaries.append(f"SKIP {root} (parent missing)")
            continue
        root.mkdir(parents=True, exist_ok=True)
        link_path = root / skill_name
        if link_path == target_dir:
            summaries.append(f"KEEP {link_path} (global source)")
            continue
        backup = replace_with_symlink(link_path, target_dir)
        if backup:
            summaries.append(f"LINK {link_path} -> {target_dir} (backup: {backup.name})")
        else:
            summaries.append(f"LINK {link_path} -> {target_dir}")
    return summaries


def create_wrapper(skill_name: str, target_dir: Path, entry_script: str, wrapper_bin_dir: Path) -> Path:
    """Create an executable wrapper in ~/.local/bin."""
    if not entry_script:
        raise ValueError("Cannot create wrapper without --entry-script.")
    script_path = target_dir / entry_script
    if not script_path.exists():
        raise FileNotFoundError(f"Entry script not found: {script_path}")

    wrapper_bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper_path = wrapper_bin_dir / skill_name
    wrapper_text = "\n".join(
        [
            "#!/bin/bash",
            "set -euo pipefail",
            f'EXEC_SCRIPT="{script_path}"',
            'if [ ! -f "$EXEC_SCRIPT" ]; then',
            '  echo "Skill entry script not found: $EXEC_SCRIPT" >&2',
            "  exit 1",
            "fi",
            'exec python3 "$EXEC_SCRIPT" "$@"',
            "",
        ]
    )
    wrapper_path.write_text(wrapper_text, encoding="utf-8")
    current_mode = wrapper_path.stat().st_mode
    wrapper_path.chmod(current_mode | 0o111)
    return wrapper_path


def print_summary(title: str, items: Iterable[str]) -> None:
    """Print readable summary lines."""
    print(title)
    for item in items:
        print(f"- {item}")


def main() -> int:
    """Run the global deployment workflow."""
    args = parse_args()

    global_registry = Path(args.global_registry).expanduser().resolve()
    target_dir = global_registry / args.skill_name
    link_roots = supported_link_roots(args.link_targets.split(","))
    source_dir = find_source_dir(args.skill_name, args.source_dir, global_registry)

    final_target = ensure_global_home(source_dir, target_dir, args.on_conflict)
    
    if final_target is None:
        print_summary("Deployment skipped", [f"Conflict encountered for {args.skill_name} and --on-conflict=skip was used."])
        return 0

    link_summary = create_symlinks(final_target.name, final_target, link_roots)

    wrapper_path = None
    if not args.skip_wrapper and args.entry_script:
        wrapper_bin_dir = Path(args.wrapper_bin_dir).expanduser().resolve()
        wrapper_path = create_wrapper(final_target.name, final_target, args.entry_script, wrapper_bin_dir)

    print_summary("Deployment complete", [f"Global source: {final_target}"])
    print_summary("Symlink status", link_summary)
    if wrapper_path:
        print_summary("Wrapper", [str(wrapper_path)])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
