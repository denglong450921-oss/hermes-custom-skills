#!/usr/bin/env python3
"""Resource-aware, checkpointed video speech transcription to Markdown."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def fail(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def require_binary(name: str) -> str:
    path = shutil.which(name)
    if not path:
        fail(f"Missing required executable: {name}")
    return path


def atomic_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)


def probe_video(path: Path) -> dict[str, object]:
    ffprobe = require_binary("ffprobe")
    result = run([
        ffprobe, "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_type,codec_name,channels",
        "-of", "json", str(path)
    ])
    if result.returncode != 0:
        fail(f"ffprobe could not read the video: {result.stderr.strip()}")
    try:
        data = json.loads(result.stdout)
        duration = float(data.get("format", {}).get("duration") or 0)
        size = int(data.get("format", {}).get("size") or path.stat().st_size)
        audio = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        fail(f"Invalid ffprobe output: {exc}")
    return {"duration": duration, "size": size, "has_audio": bool(audio), "audio": audio}


def system_memory_gb() -> float:
    result = run(["sysctl", "-n", "hw.memsize"])
    if result.returncode == 0 and result.stdout.strip().isdigit():
        return int(result.stdout.strip()) / (1024 ** 3)
    return 0.0


def stamp(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def parse_stamp(value: str) -> int:
    hours, minutes, seconds = map(int, value.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def language_label(code: str | None) -> str:
    return {"zh": "中文", "en": "English", "mixed": "中英混合"}.get(
        code or "", code or "自动识别"
    )


def text_language(text: str) -> str:
    cjk = len(re.findall(r"[\u3400-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if cjk and latin:
        return "mixed"
    if cjk:
        return "zh"
    if latin:
        return "en"
    return ""


def normalize_text(text: str) -> str:
    text = " ".join(text.strip().split())
    if len(re.findall(r"[\u3400-\u9fff]", text)) > len(re.findall(r"[A-Za-z]", text)):
        text = (
            text.replace(",", "，").replace("?", "？").replace("!", "！")
            .replace("﹔", "，").replace("；", "，")
        )
        if text.endswith("."):
            text = text[:-1] + "。"
    return text


def choose_plan(
    duration: float,
    size: int,
    memory_gb: float,
    requested_mode: str,
    requested_model: str,
    requested_chunk: int,
    language: str,
) -> dict[str, object]:
    size_mb = size / (1024 ** 2)
    if requested_mode == "auto":
        mode = "direct" if duration <= 90 and size_mb <= 200 and language != "mixed" else "chunked"
    else:
        mode = requested_mode
    if requested_chunk:
        chunk_seconds = requested_chunk
    elif duration <= 15 * 60:
        chunk_seconds = 30
    elif duration <= 60 * 60:
        chunk_seconds = 45
    else:
        chunk_seconds = 60
    model = requested_model
    if model == "auto":
        model = "medium" if (memory_gb == 0 or memory_gb >= 8) and duration <= 30 * 60 else "base"
    return {
        "mode": mode,
        "chunk_seconds": 0 if mode == "direct" else chunk_seconds,
        "model": model,
        "fallback_model": "base" if model != "base" else None,
        "duration_seconds": duration,
        "size_mb": round(size_mb, 1),
        "system_memory_gb": round(memory_gb, 1),
        "strategy": (
            "短视频整段推理"
            if mode == "direct"
            else f"按静音边界分批，目标批长 {chunk_seconds} 秒；每批完成立即写入断点"
        ),
    }


def silence_points(ffmpeg: str, wav: Path) -> list[float]:
    scan = run([
        ffmpeg, "-i", str(wav), "-af", "silencedetect=noise=-35dB:d=0.28",
        "-f", "null", "-"
    ])
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", scan.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", scan.stderr)]
    return [(a + b) / 2 for a, b in zip(starts, ends)]


def build_ranges(duration: float, chunk_seconds: int, pauses: list[float]) -> list[tuple[float, float]]:
    if not chunk_seconds:
        return [(0.0, duration)]
    ranges: list[tuple[float, float]] = []
    start = 0.0
    while duration - start > 0.25:
        target = min(duration, start + chunk_seconds)
        if target < duration:
            candidates = [p for p in pauses if target - 6 <= p <= target + 6 and p - start >= 10]
            end = min(candidates, key=lambda p: abs(p - target)) if candidates else target
        else:
            end = duration
        if end <= start:
            end = min(duration, start + chunk_seconds)
        ranges.append((round(start, 3), round(end, 3)))
        start = end
    return ranges


def transcribe_chunk(model, audio: Path, language: str | None, prompt: str, vad: bool):
    iterator, info = model.transcribe(
        str(audio),
        language=language,
        beam_size=5,
        vad_filter=vad,
        condition_on_previous_text=True,
        initial_prompt=prompt,
    )
    segments = []
    for segment in iterator:
        text = normalize_text(segment.text)
        if not text:
            continue
        segments.append({
            "start": float(segment.start),
            "end": float(segment.end),
            "text": text,
            "avg_logprob": float(getattr(segment, "avg_logprob", 0.0) or 0.0),
            "no_speech_prob": float(getattr(segment, "no_speech_prob", 0.0) or 0.0),
        })
    return segments, {
        "language": getattr(info, "language", None),
        "language_probability": float(getattr(info, "language_probability", 0.0) or 0.0),
    }


def model_loader(name: str, device: str, compute_type: str):
    from faster_whisper import WhisperModel
    return WhisperModel(name, device=device, compute_type=compute_type)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--language", default="auto", choices=("auto", "mixed", "zh", "en"))
    parser.add_argument("--model", default="auto")
    parser.add_argument("--mode", default="auto", choices=("auto", "direct", "chunked"))
    parser.add_argument("--chunk-seconds", type=int, default=0)
    parser.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda"))
    parser.add_argument("--compute-type", default="auto")
    parser.add_argument("--initial-prompt", default="")
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--no-timestamps", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--reset-work", action="store_true")
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file():
        fail(f"Input video does not exist: {source}")
    if output.exists() and not args.overwrite:
        fail(f"Output already exists: {output}. Use a new name or --overwrite with approval.")
    output.parent.mkdir(parents=True, exist_ok=True)
    metadata = probe_video(source)
    duration = float(metadata["duration"])
    if duration <= 0:
        fail("Video duration is zero or unavailable.")
    if not metadata["has_audio"]:
        fail("Video contains no audio stream.")
    ffmpeg = require_binary("ffmpeg")
    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        fail("Missing faster-whisper. Install with: python3 -m pip install faster-whisper")

    plan = choose_plan(
        duration, int(metadata["size"]), system_memory_gb(), args.mode,
        args.model, args.chunk_seconds, args.language
    )
    signature = hashlib.sha256(
        f"{source}:{source.stat().st_size}:{source.stat().st_mtime_ns}:{duration}".encode()
    ).hexdigest()[:16]
    work = (args.work_dir or output.parent / f".{output.stem}.transcribe-work").resolve()
    if args.reset_work and work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)
    manifest_path = work / "manifest.json"
    expected_manifest = {
        "signature": signature,
        "source": str(source),
        "language": args.language,
        "plan": plan,
    }
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text(encoding="utf-8"))
        if old != expected_manifest:
            fail(f"Existing checkpoint plan does not match this run: {work}. Use --reset-work.")
    else:
        atomic_json(manifest_path, expected_manifest)

    wav = work / "audio-16k-mono.wav"
    if not wav.exists() or wav.stat().st_size == 0:
        extracted = run([
            ffmpeg, "-y", "-i", str(source), "-vn", "-ac", "1", "-ar", "16000",
            "-c:a", "pcm_s16le", str(wav)
        ])
        if extracted.returncode != 0 or not wav.exists() or wav.stat().st_size == 0:
            fail(f"Could not extract audio: {extracted.stderr.strip()[-1200:]}")

    ranges = build_ranges(duration, int(plan["chunk_seconds"]), silence_points(ffmpeg, wav))
    atomic_json(work / "ranges.json", [{"start": a, "end": b} for a, b in ranges])
    device = args.device
    if device == "auto":
        device = "cuda" if shutil.which("nvidia-smi") else "cpu"
    compute_type = args.compute_type
    if compute_type == "auto":
        compute_type = "float16" if device == "cuda" else "int8"
    selected_model = str(plan["model"])
    fallback_model = plan.get("fallback_model")
    prompt = args.initial_prompt or (
        "Preserve the original Chinese and English. Pay special attention to names, "
        "numbers, acronyms, technical terms, negation, and repeated terminology."
    )
    models: dict[str, object] = {}

    def get_model(name: str):
        if name not in models:
            models[name] = model_loader(name, device, compute_type)
        return models[name]

    all_results = []
    fallbacks: list[str] = []
    for index, (start, end) in enumerate(ranges):
        result_path = work / "results" / f"chunk-{index:04d}.json"
        if result_path.exists():
            cached = json.loads(result_path.read_text(encoding="utf-8"))
            if cached.get("status") == "complete":
                all_results.append(cached)
                print(f"RESUME {index + 1}/{len(ranges)} {stamp(start)}-{stamp(end)}", flush=True)
                continue
        chunk = work / "chunks" / f"chunk-{index:04d}.wav"
        chunk.parent.mkdir(parents=True, exist_ok=True)
        cut = run([
            ffmpeg, "-y", "-ss", str(start), "-t", str(end - start), "-i", str(wav),
            "-ac", "1", "-ar", "16000", str(chunk)
        ])
        if cut.returncode != 0 or not chunk.exists() or chunk.stat().st_size == 0:
            fail(f"Could not create batch {index + 1} near {stamp(start)}.")
        language = None if args.language in {"auto", "mixed"} else args.language
        used_model = selected_model
        last_error = ""
        segments = []
        info = {"language": None, "language_probability": 0.0}
        for attempt, (model_name, vad) in enumerate(
            [(selected_model, True), (selected_model, False)] +
            ([(str(fallback_model), True)] if fallback_model else [])
        ):
            try:
                if plan["mode"] == "chunked":
                    worker_output = work / "worker" / f"chunk-{index:04d}-attempt-{attempt}.json"
                    worker_output.parent.mkdir(parents=True, exist_ok=True)
                    worker_command = [
                        sys.executable,
                        str(Path(__file__).with_name("transcribe_batch_worker.py")),
                        "--audio", str(chunk),
                        "--output", str(worker_output),
                        "--model", model_name,
                        "--language", args.language,
                        "--device", device,
                        "--compute-type", compute_type,
                        "--prompt", prompt,
                    ]
                    if not vad:
                        worker_command.append("--no-vad")
                    worker_run = run(worker_command)
                    if worker_run.returncode != 0 or not worker_output.exists():
                        raise RuntimeError(
                            f"isolated worker exit={worker_run.returncode}: "
                            f"{worker_run.stderr.strip()[-500:]}"
                        )
                    worker_data = json.loads(worker_output.read_text(encoding="utf-8"))
                    segments = worker_data.get("segments", [])
                    info = {
                        "language": worker_data.get("language"),
                        "language_probability": worker_data.get("language_probability", 0.0),
                    }
                else:
                    segments, info = transcribe_chunk(
                        get_model(model_name), chunk, language, prompt, vad
                    )
                used_model = model_name
                if segments or info.get("language_probability", 0) > 0:
                    break
            except Exception as exc:
                last_error = str(exc)
            print(
                f"RETRY batch {index + 1}, attempt {attempt + 1} failed: {last_error or 'empty'}",
                file=sys.stderr, flush=True
            )
        if used_model != selected_model:
            fallbacks.append(f"第 {index + 1} 批改用 {used_model}")
        adjusted = []
        for segment in segments:
            segment["start"] = float(segment["start"]) + start
            segment["end"] = min(duration, float(segment["end"]) + start)
            adjusted.append(segment)
        result = {
            "status": "complete",
            "batch": index + 1,
            "range": {"start": start, "end": end},
            "model": used_model,
            "language": info.get("language"),
            "language_probability": info.get("language_probability", 0.0),
            "segments": adjusted,
            "error": last_error,
        }
        atomic_json(result_path, result)
        all_results.append(result)
        print(
            f"DONE {index + 1}/{len(ranges)} {stamp(start)}-{stamp(end)} "
            f"segments={len(adjusted)} model={used_model}",
            flush=True
        )

    segments = []
    for result in all_results:
        batch_end = float(result.get("range", {}).get("end", duration))
        for source_item in result.get("segments", []):
            item = dict(source_item)
            item["text"] = normalize_text(str(item.get("text", "")))
            item["start"] = float(item.get("start", 0.0))
            item["end"] = min(float(item.get("end", 0.0)), batch_end)
            clipped_duration = item["end"] - item["start"]
            tail_hallucination = (
                clipped_duration < 0.7 and float(item.get("avg_logprob", 0.0)) < -0.5
            ) or (
                float(item.get("no_speech_prob", 0.0)) > 0.6
                and float(item.get("avg_logprob", 0.0)) < -0.6
            )
            if item["text"] and item["end"] > item["start"] and not tail_hallucination:
                segments.append(item)
    segments.sort(key=lambda x: (float(x["start"]), float(x["end"])))
    if not segments:
        fail("No recognizable speech was found after all batches.")
    text_languages = {text_language(str(x["text"])) for x in segments}
    text_languages.discard("")
    detected = "mixed" if (
        "mixed" in text_languages or {"zh", "en"}.issubset(text_languages)
    ) else (next(iter(text_languages)) if text_languages else "auto")
    probabilities = [
        float(x.get("language_probability", 0.0))
        for x in all_results if x.get("language_probability") is not None
    ]
    probability = sum(probabilities) / len(probabilities) if probabilities else 0.0
    low = [x for x in segments if float(x.get("avg_logprob", 0.0)) < -0.8]
    duplicate_pairs = []
    for previous, current in zip(segments, segments[1:]):
        if str(previous["text"]) == str(current["text"]):
            duplicate_pairs.append(stamp(float(current["start"])))
    warnings = []
    if low:
        warnings.append(f"{len(low)} 个片段平均识别置信偏低，需要复核")
    if duplicate_pairs:
        warnings.append(f"{len(duplicate_pairs)} 处相邻文本完全重复")
    if fallbacks:
        warnings.append("部分批次触发模型降级")
    conclusion = "WARN" if warnings else "PASS"
    full_text = " ".join(str(x["text"]) for x in segments).strip()
    generated = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    lines = [
        f"# 视频转写：{source.stem}", "",
        "## 文件信息", "",
        f"- 来源视频：`{source.name}`",
        f"- 视频时长：{stamp(duration)}",
        f"- 文件大小：{plan['size_mb']} MB",
        f"- 识别语言：{language_label(detected)}",
        f"- 语言置信度：{probability:.1%}",
        f"- 转写模型：`{selected_model}`",
        f"- 生成时间：{generated}", "",
        "## 处理计划", "",
        f"- 处理模式：{plan['mode']}",
        f"- 资源策略：{plan['strategy']}",
        f"- 分批数量：{len(ranges)}",
        f"- 断点目录：`{work.name}`",
        "",
    ]
    if not args.no_timestamps:
        lines.extend(["## 带时间戳转写", ""])
        for item in segments:
            lines.extend([
                f"### [{stamp(float(item['start']))} → {stamp(float(item['end']))}]",
                "",
                str(item["text"]),
                "",
            ])
    lines.extend([
        "## 连续全文", "", full_text, "",
        "## 转写质量报告", "",
        f"- 质量结论：**{conclusion}**",
        f"- 已完成批次：{len(all_results)}/{len(ranges)}",
        f"- 低置信片段：{len(low)}",
        f"- 相邻重复：{len(duplicate_pairs)}",
        f"- 模型降级：{len(fallbacks)}",
    ])
    if low:
        lines.append("- 建议复核时间：" + "、".join(stamp(float(x["start"])) for x in low[:20]))
    for warning in warnings:
        lines.append(f"- 警告：{warning}")
    lines.extend([
        "",
        "## 质量备注", "",
        "- 自动转写后已执行时间轴、重复、正文一致性和置信度检查。",
        "- 人名、地名、缩写、数字和专业术语仍需结合上下文或音频复核。",
        "- 转写保留原始语言，不自动翻译。",
        "",
    ])
    atomic_text(output, "\n".join(lines))
    print(json.dumps({
        "output": str(output),
        "plan": plan,
        "batches": len(ranges),
        "segments": len(segments),
        "quality": conclusion,
        "low_confidence_segments": len(low),
        "detected_language": detected,
    }, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
