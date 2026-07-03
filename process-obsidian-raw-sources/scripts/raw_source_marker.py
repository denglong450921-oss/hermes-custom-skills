#!/usr/bin/env python3
"""Track processed raw source Markdown files in an Obsidian LLM Wiki vault."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_VAULT = Path(
    "/Users/f/Documents/dennon_obsidian_vault_important/den-llm-wiki/llm_wiki_knowledge"
)
PROCESSOR_NAME = "process-obsidian-raw-sources"
MARKER_KEYS = {
    "llm_wiki_processed",
    "llm_wiki_processed_at",
    "llm_wiki_processor",
    "llm_wiki_outputs",
}
FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(?P<yaml>.*?)(?:\r?\n)---[ \t]*(?:\r?\n|$)", re.S)
HTML_MARKER_RE = re.compile(r"<!--\s*llm-wiki-processed\s*:\s*true\s*-->", re.I)


@dataclass
class Frontmatter:
    data: dict[str, Any]
    block: str
    body_start: int


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> Frontmatter:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return Frontmatter({}, "", 0)

    block = match.group("yaml")
    lines = block.splitlines()
    data: dict[str, Any] = {}
    index = 0

    while index < len(lines):
        line = lines[index]
        pair = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not pair:
            index += 1
            continue

        key, raw_value = pair.group(1), pair.group(2)
        if raw_value.strip():
            data[key] = parse_scalar(raw_value)
            index += 1
            continue

        values: list[Any] = []
        cursor = index + 1
        while cursor < len(lines):
            item = re.match(r"^\s+-\s*(.*)$", lines[cursor])
            if not item:
                break
            values.append(parse_scalar(item.group(1)))
            cursor += 1

        data[key] = values if values else ""
        index = cursor

    return Frontmatter(data, block, match.end())


def first_heading(text: str) -> str:
    body = text[parse_frontmatter(text).body_start :]
    match = re.search(r"^#\s+(.+)$", body, re.M)
    return match.group(1).strip() if match else ""


def resolve_vault(vault_arg: str | None) -> Path:
    candidates = []
    if vault_arg:
        candidates.append(Path(vault_arg).expanduser())
    candidates.extend([Path.cwd(), DEFAULT_VAULT])

    for candidate in candidates:
        raw_dir = candidate / "08_sources_raw"
        if raw_dir.is_dir():
            return candidate.resolve()

    raise SystemExit(
        "Could not locate a vault with 08_sources_raw/. Pass --vault /path/to/vault."
    )


def relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def source_files(vault: Path) -> list[Path]:
    raw_dir = vault / "08_sources_raw"
    files = []
    for path in raw_dir.rglob("*.md"):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        if str(frontmatter.data.get("type", "")).lower() == "index":
            continue
        files.append(path)
    return sorted(files)


def normalize_outputs(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def status_for_file(vault: Path, source: Path) -> dict[str, Any]:
    text = source.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    processed = bool(frontmatter.data.get("llm_wiki_processed")) or bool(
        HTML_MARKER_RE.search(text)
    )
    return {
        "path": relpath(source, vault),
        "title": str(frontmatter.data.get("title") or first_heading(text) or source.stem),
        "processed": processed,
        "processed_at": str(frontmatter.data.get("llm_wiki_processed_at") or ""),
        "processor": str(frontmatter.data.get("llm_wiki_processor") or ""),
        "outputs": normalize_outputs(frontmatter.data.get("llm_wiki_outputs")),
    }


def print_status(rows: list[dict[str, Any]], as_json: bool) -> None:
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    if not rows:
        print("No raw source Markdown files found.")
        return

    for row in rows:
        label = "PROCESSED" if row["processed"] else "UNPROCESSED"
        suffix = ""
        if row["processed_at"]:
            suffix += f" at {row['processed_at']}"
        if row["outputs"]:
            suffix += " -> " + ", ".join(row["outputs"])
        print(f"{label:<11} {row['path']}{suffix}")


def resolve_source(vault: Path, source_arg: str) -> Path:
    source = Path(source_arg).expanduser()
    candidates = []

    if source.is_absolute():
        candidates.append(source)
    else:
        candidates.append(vault / source)
        candidates.append(vault / "08_sources_raw" / source)

    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    raise SystemExit(f"Source not found: {source_arg}")


def quote_yaml(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def marker_block(outputs: list[str]) -> str:
    lines = [
        "llm_wiki_processed: true",
        f"llm_wiki_processed_at: {quote_yaml(datetime.now().astimezone().isoformat(timespec='seconds'))}",
        f"llm_wiki_processor: {quote_yaml(PROCESSOR_NAME)}",
        "llm_wiki_outputs:",
    ]
    if outputs:
        lines.extend(f"  - {quote_yaml(output)}" for output in outputs)
    else:
        lines.append('  - ""')
    return "\n".join(lines)


def remove_marker_lines(block: str) -> str:
    lines = block.splitlines()
    kept: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        key_match = re.match(r"^([A-Za-z0-9_-]+):", line)
        key = key_match.group(1) if key_match else ""

        if key in MARKER_KEYS:
            index += 1
            if key == "llm_wiki_outputs":
                while index < len(lines) and re.match(r"^\s+-\s*", lines[index]):
                    index += 1
            continue

        kept.append(line)
        index += 1

    while kept and not kept[-1].strip():
        kept.pop()
    return "\n".join(kept)


def write_frontmatter(text: str, new_block: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return f"---\n{new_block}\n---\n\n{text.lstrip()}"

    return f"---\n{new_block}\n---\n{text[match.end():]}"


def command_status(args: argparse.Namespace) -> int:
    vault = resolve_vault(args.vault)
    rows = [status_for_file(vault, path) for path in source_files(vault)]
    print_status(rows, args.json)
    return 0


def command_list(args: argparse.Namespace) -> int:
    vault = resolve_vault(args.vault)
    rows = [status_for_file(vault, path) for path in source_files(vault)]

    if not args.all:
        if args.processed:
            rows = [row for row in rows if row["processed"]]
        else:
            rows = [row for row in rows if not row["processed"]]

    print_status(rows, args.json)
    return 0


def command_next(args: argparse.Namespace) -> int:
    vault = resolve_vault(args.vault)
    rows = [status_for_file(vault, path) for path in source_files(vault)]
    unprocessed = [row for row in rows if not row["processed"]]
    if not unprocessed:
        print("No unprocessed raw sources.")
        return 1

    row = unprocessed[0]
    if args.json:
        print(json.dumps(row, ensure_ascii=False, indent=2))
    else:
        print(row["path"])
    return 0


def command_mark(args: argparse.Namespace) -> int:
    vault = resolve_vault(args.vault)
    source = resolve_source(vault, args.source)
    text = source.read_text(encoding="utf-8")
    current = status_for_file(vault, source)

    if current["processed"] and not args.force:
        print(f"Already processed: {current['path']}")
        if current["outputs"]:
            print("Outputs: " + ", ".join(current["outputs"]))
        return 0

    existing = parse_frontmatter(text).block
    cleaned = remove_marker_lines(existing)
    outputs = [relpath((vault / output).resolve(), vault) if not Path(output).is_absolute() else relpath(Path(output), vault) for output in args.output]
    parts = [part for part in [cleaned, marker_block(outputs)] if part.strip()]
    source.write_text(write_frontmatter(text, "\n".join(parts)), encoding="utf-8")
    print(f"Marked processed: {relpath(source, vault)}")
    return 0


def command_unmark(args: argparse.Namespace) -> int:
    vault = resolve_vault(args.vault)
    source = resolve_source(vault, args.source)
    text = source.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)

    if not frontmatter.block and not HTML_MARKER_RE.search(text):
        print(f"No marker found: {relpath(source, vault)}")
        return 0

    cleaned = remove_marker_lines(frontmatter.block)
    rewritten = write_frontmatter(text, cleaned) if frontmatter.block else text
    rewritten = HTML_MARKER_RE.sub("", rewritten)
    source.write_text(rewritten, encoding="utf-8")
    print(f"Removed processed marker: {relpath(source, vault)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", help="Path to the Obsidian vault root.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Show processing status for all raw sources.")
    status.add_argument("--json", action="store_true", help="Print JSON.")
    status.set_defaults(func=command_status)

    list_cmd = subparsers.add_parser("list", help="List unprocessed raw sources by default.")
    list_cmd.add_argument("--all", action="store_true", help="Show processed and unprocessed sources.")
    list_cmd.add_argument("--processed", action="store_true", help="Show only processed sources.")
    list_cmd.add_argument("--json", action="store_true", help="Print JSON.")
    list_cmd.set_defaults(func=command_list)

    next_cmd = subparsers.add_parser("next", help="Print the next unprocessed raw source path.")
    next_cmd.add_argument("--json", action="store_true", help="Print JSON.")
    next_cmd.set_defaults(func=command_next)

    mark = subparsers.add_parser("mark", help="Mark a raw source as processed.")
    mark.add_argument("--source", required=True, help="Raw source path.")
    mark.add_argument("--output", action="append", default=[], help="Output path. Repeatable.")
    mark.add_argument("--force", action="store_true", help="Overwrite an existing processed marker.")
    mark.set_defaults(func=command_mark)

    unmark = subparsers.add_parser("unmark", help="Remove processed marker fields.")
    unmark.add_argument("--source", required=True, help="Raw source path.")
    unmark.set_defaults(func=command_unmark)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
