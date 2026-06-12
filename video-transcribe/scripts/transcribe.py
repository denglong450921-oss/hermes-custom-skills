#!/usr/bin/env python3
"""
Transcribe video/audio file to text using faster-whisper.
Usage: python3 transcribe.py <video_path> [--model small|medium|large-v3] [--language en|zh|auto]
"""
import sys
import os
import subprocess
import argparse
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


def transcribe(video_path, model_name="small", language=None):
    """Run faster-whisper transcription."""
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
    segments, info = model.transcribe(
        video_path,
        language=language if language and language != "auto" else None,
        beam_size=5
    )

    print(f"\nDetected language: {info.language} (p={info.language_probability:.2f})")
    print(f"Duration: {info.duration:.1f}s")
    print("=" * 60)

    for segment in segments:
        start = segment.start
        end = segment.end
        text = segment.text.strip()
        if text:
            print(f"[{start:.1f}s -> {end:.1f}s] {text}")

    print("\nDone!")


def main():
    parser = argparse.ArgumentParser(description="Transcribe video/audio to text")
    parser.add_argument("video_path", help="Path to video or audio file")
    parser.add_argument("--model", default="small",
                        choices=["tiny", "base", "small", "medium", "large-v3"],
                        help="Whisper model size (default: small)")
    parser.add_argument("--language", default="auto",
                        help="Language code: en, zh, or auto (default: auto-detect)")
    args = parser.parse_args()

    path = Path(args.video_path)
    if not path.exists():
        print(f"ERROR: File not found: {args.video_path}")
        sys.exit(1)

    ensure_deps()
    transcribe(str(path), args.model, args.language)


if __name__ == "__main__":
    main()
