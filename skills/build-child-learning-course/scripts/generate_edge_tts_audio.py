#!/usr/bin/env python3
"""Generate deterministic local word and phrase MP3 files with Microsoft Edge TTS."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import edge_tts
except ImportError as exc:
    raise SystemExit(
        "edge-tts is required. Install it with: python -m pip install edge-tts"
    ) from exc


COURSE_DATA_PATTERN = re.compile(
    r'<script\s+id=["\']course-data["\']\s+type=["\']application/json["\']\s*>'
    r"(?P<data>[\s\S]*?)</script>",
    re.IGNORECASE,
)
SAFE_KEY_PATTERN = re.compile(r"[^a-z0-9]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate <key>-word.mp3 and <key>-phrase.mp3 with Edge TTS."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--manifest", type=Path, help="JSON manifest containing an items array.")
    source.add_argument(
        "--html",
        type=Path,
        help="HTML containing <script id='course-data' type='application/json'>.",
    )
    parser.add_argument("--output", type=Path, required=True, help="Destination audio folder.")
    parser.add_argument("--voice", default="en-US-AnaNeural")
    parser.add_argument("--rate", default="-5%")
    parser.add_argument("--pitch", default="+0Hz")
    parser.add_argument("--volume", default="+0%")
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--force", action="store_true", help="Regenerate existing non-empty files.")
    return parser.parse_args()


def load_source(args: argparse.Namespace) -> list[dict[str, str]]:
    if args.manifest:
        payload: Any = json.loads(args.manifest.read_text(encoding="utf-8"))
        raw_items = payload["items"] if isinstance(payload, dict) else payload
    else:
        html = args.html.read_text(encoding="utf-8")
        match = COURSE_DATA_PATTERN.search(html)
        if not match:
            raise ValueError("Could not find the course-data JSON script in the HTML.")
        payload = json.loads(match.group("data"))
        raw_items = [
            item
            for day in payload
            for item in day.get("words", day.get("items", []))
        ]

    items: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in raw_items:
        word = str(raw.get("word", raw.get("w", ""))).strip()
        phrase = str(raw.get("phrase", raw.get("p", ""))).strip()
        raw_key = str(raw.get("key", word)).strip().lower()
        key = SAFE_KEY_PATTERN.sub("-", raw_key).strip("-")
        if not key or not word or not phrase:
            raise ValueError(f"Every item requires key/word/phrase values: {raw!r}")
        if key in seen:
            raise ValueError(f"Duplicate audio key: {key}")
        seen.add(key)
        items.append({"key": key, "word": word, "phrase": phrase})
    if not items:
        raise ValueError("The source contains no learning items.")
    return items


async def generate_one(
    *,
    text: str,
    path: Path,
    voice: str,
    rate: str,
    pitch: str,
    volume: str,
    force: bool,
    semaphore: asyncio.Semaphore,
) -> str:
    if path.exists() and path.stat().st_size > 0 and not force:
        return "skipped"
    async with semaphore:
        await edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume,
        ).save(str(path))
    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"Edge TTS created an empty or missing file: {path}")
    return "generated"


async def run(args: argparse.Namespace, items: list[dict[str, str]]) -> dict[str, Any]:
    if args.concurrency < 1:
        raise ValueError("--concurrency must be at least 1.")
    args.output.mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(args.concurrency)
    jobs = []
    audio_map: dict[str, dict[str, str]] = {}
    for item in items:
        word_name = f"{item['key']}-word.mp3"
        phrase_name = f"{item['key']}-phrase.mp3"
        audio_map[item["key"]] = {"word": word_name, "phrase": phrase_name}
        jobs.extend(
            [
                generate_one(
                    text=item["word"],
                    path=args.output / word_name,
                    voice=args.voice,
                    rate=args.rate,
                    pitch=args.pitch,
                    volume=args.volume,
                    force=args.force,
                    semaphore=semaphore,
                ),
                generate_one(
                    text=item["phrase"],
                    path=args.output / phrase_name,
                    voice=args.voice,
                    rate=args.rate,
                    pitch=args.pitch,
                    volume=args.volume,
                    force=args.force,
                    semaphore=semaphore,
                ),
            ]
        )
    results = await asyncio.gather(*jobs)
    metadata = {
        "provider": "Microsoft Edge TTS",
        "voice": args.voice,
        "rate": args.rate,
        "pitch": args.pitch,
        "volume": args.volume,
        "itemCount": len(items),
        "fileCount": len(results),
        "generated": results.count("generated"),
        "skipped": results.count("skipped"),
        "audio": audio_map,
    }
    (args.output / "audio-map.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> int:
    args = parse_args()
    try:
        items = load_source(args)
        metadata = asyncio.run(run(args, items))
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
