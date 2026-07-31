#!/usr/bin/env python3
"""Isolated faster-whisper worker for one audio batch."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def normalize(text: str) -> str:
    text = " ".join(text.strip().split())
    if sum("\u3400" <= c <= "\u9fff" for c in text) > sum(c.isascii() and c.isalpha() for c in text):
        text = text.replace(",", "，").replace("?", "？").replace("!", "！")
        if text.endswith("."):
            text = text[:-1] + "。"
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--language", default="auto")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--compute-type", default="int8")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--no-vad", action="store_true")
    args = parser.parse_args()
    from faster_whisper import WhisperModel
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
    iterator, info = model.transcribe(
        str(args.audio),
        language=None if args.language in {"auto", "mixed"} else args.language,
        beam_size=5,
        vad_filter=not args.no_vad,
        condition_on_previous_text=True,
        initial_prompt=args.prompt,
    )
    segments = []
    for segment in iterator:
        text = normalize(segment.text)
        if text:
            segments.append({
                "start": float(segment.start),
                "end": float(segment.end),
                "text": text,
                "avg_logprob": float(getattr(segment, "avg_logprob", 0.0) or 0.0),
                "no_speech_prob": float(getattr(segment, "no_speech_prob", 0.0) or 0.0),
            })
    data = {
        "segments": segments,
        "language": getattr(info, "language", None),
        "language_probability": float(getattr(info, "language_probability", 0.0) or 0.0),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_suffix(args.output.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
