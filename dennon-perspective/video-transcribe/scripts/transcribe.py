#!/usr/bin/env python3
"""
Transcribe video/audio file to text using faster-whisper.
Saves timestamped transcript as .md in the Downloads directory.

Usage: python3 transcribe.py <video_path> [--model small|medium|large-v3] [--language en|zh|auto] [--output-dir DIR]
"""
import sys
import os
import subprocess
import argparse
import datetime
from pathlib import Path


def ensure_deps():
    """Ensure faster-whisper and ffmpeg are available."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: ffmpeg not found. Install with: brew install ffmpeg")
        sys.exit(1)

    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        print("Installing faster-whisper...", flush=True)
        env = os.environ.copy()
        for key in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
            env.pop(key, None)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "faster-whisper", "socksio"],
            check=True, capture_output=True, env=env
        )


def format_timestamp(seconds):
    """Format seconds to HH:MM:SS.ss."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:05.2f}"
    return f"{m:02d}:{s:05.2f}"


def format_timestamp_short(seconds):
    """Format seconds to compact short form."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    if h > 0:
        return f"{h}h{m:02d}m{s:04.1f}s"
    return f"{m:02d}m{s:04.1f}s"


def save_markdown(segments, metadata, output_path):
    """Save transcript as formatted markdown file."""
    lines = []
    lines.append(f"# 视频转录 — {metadata['source_name']}")
    lines.append("")
    lines.append(f"- **文件**: `{metadata['source_path']}`")
    lines.append(f"- **语言**: {metadata['language']} (置信度 {metadata['language_prob']:.0%})")
    lines.append(f"- **时长**: {format_timestamp_short(metadata['duration'])}")
    lines.append(f"- **模型**: {metadata['model']}")
    lines.append(f"- **转录时间**: {metadata['timestamp']}")
    lines.append("")

    # Group into speaker-friendly paragraphs — combine short adjacent segs
    lines.append("---")
    lines.append("")

    for seg in segments:
        lines.append(f"> **{format_timestamp(seg['start'])} — {format_timestamp(seg['end'])}**")
        lines.append("")
        lines.append(seg["text"])
        lines.append("")
        lines.append("---")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def transcribe(video_path, model_name="small", language=None, output_dir=None):
    """Run faster-whisper transcription and save result."""
    import faster_whisper

    env = os.environ.copy()
    for key in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        env.pop(key, None)

    print(f"Loading faster-whisper {model_name} model...", flush=True)
    model = faster_whisper.WhisperModel(
        model_name, device="cpu", compute_type="int8",
        download_root=os.path.expanduser("~/.cache/faster-whisper")
    )

    print("Transcribing...", flush=True)
    segments_iter, info = model.transcribe(
        video_path,
        language=language if language and language != "auto" else None,
        beam_size=5
    )

    print(f"\nDetected language: {info.language} (p={info.language_probability:.2f})")
    print(f"Duration: {info.duration:.1f}s")
    print("=" * 60)

    # Collect segments and print to stdout
    all_segments = []
    for segment in segments_iter:
        start = segment.start
        end = segment.end
        text = segment.text.strip()
        if text:
            all_segments.append({"start": start, "end": end, "text": text})
            print(f"[{start:.1f}s -> {end:.1f}s] {text}")

    print("\nDone!")

    # Save markdown
    source_path = Path(video_path)
    output_dir = Path(output_dir) if output_dir else Path.home() / "Downloads"
    output_dir.mkdir(parents=True, exist_ok=True)
    md_name = source_path.stem + "_transcript.md"
    md_path = output_dir / md_name

    metadata = {
        "source_name": source_path.name,
        "source_path": str(source_path.resolve()),
        "language": info.language,
        "language_prob": info.language_probability,
        "duration": info.duration,
        "model": model_name,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    save_markdown(all_segments, metadata, md_path)
    print(f"\nTranscript saved: {md_path}")


def main():
    parser = argparse.ArgumentParser(description="Transcribe video/audio to text")
    parser.add_argument("video_path", help="Path to video or audio file")
    parser.add_argument("--model", default="small",
                        choices=["tiny", "base", "small", "medium", "large-v3"],
                        help="Whisper model size (default: small)")
    parser.add_argument("--language", default="auto",
                        help="Language code: en, zh, or auto (default: auto-detect)")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory for .md transcript (default: ~/Downloads)")
    args = parser.parse_args()

    path = Path(args.video_path)
    if not path.exists():
        print(f"ERROR: File not found: {args.video_path}")
        sys.exit(1)

    ensure_deps()
    transcribe(str(path), args.model, args.language, args.output_dir)


if __name__ == "__main__":
    main()
