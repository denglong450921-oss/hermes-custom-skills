#!/usr/bin/env python3
"""Generate a local MP3 with Microsoft Edge TTS for an IELTS lesson."""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
import tempfile

import edge_tts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="English text to synthesize")
    source.add_argument("--text-file", type=Path, help="UTF-8 file containing English text")
    parser.add_argument("--output", type=Path, required=True, help="Destination .mp3 path")
    parser.add_argument("--voice", default="en-US-AriaNeural", help="Microsoft Edge neural voice")
    parser.add_argument("--rate", default="+0%", help="Edge TTS generation rate, e.g. -10%%")
    parser.add_argument("--volume", default="+0%", help="Edge TTS volume, e.g. +0%%")
    parser.add_argument("--pitch", default="+0Hz", help="Edge TTS pitch, e.g. +0Hz")
    return parser.parse_args()


async def synthesize(args: argparse.Namespace, text: str, temporary: Path) -> None:
    communicate = edge_tts.Communicate(
        text=text,
        voice=args.voice,
        rate=args.rate,
        volume=args.volume,
        pitch=args.pitch,
    )
    await communicate.save(str(temporary))


def main() -> None:
    args = parse_args()
    text = args.text if args.text is not None else args.text_file.read_text(encoding="utf-8")
    text = " ".join(text.split())
    if not text:
        raise SystemExit("English transcript is empty.")
    if args.output.suffix.lower() != ".mp3":
        raise SystemExit("--output must use the .mp3 extension.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{args.output.stem}-", suffix=".mp3", dir=args.output.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        asyncio.run(synthesize(args, text, temporary))
        if not temporary.exists() or temporary.stat().st_size == 0:
            raise RuntimeError("Edge TTS returned an empty audio file.")
        os.replace(temporary, args.output)
    finally:
        temporary.unlink(missing_ok=True)

    print(f"Generated {args.output} with {args.voice} ({args.output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
