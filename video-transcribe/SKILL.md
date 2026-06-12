---
name: video-transcribe
description: >
  Transcribe speech from a video or audio file into Chinese or English text with timestamps.
  Use when the user provides a video/audio file path (MP4, MOV, MKV, MP3, WAV, M4A, etc.)
  and asks you to extract speech, transcribe, convert speech to text, or get the transcript.
  Supports Chinese (zh) and English (en) with auto-detection.
  Outputs timestamped text segments. Make sure to use this skill whenever the user
  mentions transcribing, extracting text from, or getting a transcript of any media file.
---

# Video/Audio Transcription Skill

Extract speech from video/audio files into timestamped text using faster-whisper.

## Prerequisites

- `ffmpeg` — install via `brew install ffmpeg` if missing
- `faster-whisper` + `socksio` — auto-installed by the bundled script
- Model files auto-download from HuggingFace (~500MB for `small` on first run)

**Proxy note:** Script clears proxy env vars during HF downloads automatically.

## Workflow

### 1. Verify file exists
```bash
ls -la "<file_path>"
```
Always quote paths — filenames may contain Chinese, `#`, `[]`, spaces.

🔴 CHECKPOINT: If `ls` shows "No such file" or stderr, do NOT proceed. Ask the user for the correct path. The error-handling table below has the recovery flow.

### 2. Run the bundled script

```bash
python3 <skill_dir>/scripts/transcribe.py "<file_path>" [options]
```

**Options:**
- `--model tiny|base|small|medium|large-v3` — size vs accuracy (default: small)
- `--language en|zh|auto` — force language or auto-detect (default: auto)

**Recommendations:**
- Quick draft / short clips → `small` (default, good balance)
- Full lectures / important content → `medium` (much better Chinese accuracy)
- Maximum accuracy → `large-v3` (slow, ~0.5x realtime on M3 Pro)
- Short English clips → `base` works fine

**Examples:**
```bash
# Chinese video, auto-detect, small model (good default)
python3 <skill_dir>/scripts/transcribe.py "~/Downloads/lecture.mp4"

# English podcast, better accuracy
python3 <skill_dir>/scripts/transcribe.py "podcast.mp3" --model medium --language en

# Quick test with tiny model
python3 <skill_dir>/scripts/transcribe.py "clip.mp4" --model tiny
```

🔴 CHECKPOINT: If the script exits with code 124 (timeout) or shows a `Traceback`, consult the Error handling & fallback table below. Do not present the user with a truncated or failed output.

### 3. Present output

The script prints timestamped segments directly to stdout:
```
[0.7s -> 1.4s] 哈喽各位家长
[1.4s -> 3.6s] 又到了我们10分钟长科普的环节
[3.6s -> 6.6s] 运动到底是如何刺激骨头长高的
```

Present this output to the user as-is. The timestamps let them jump to specific parts. If the transcript is long (>100 lines), offer to save it instead (Step 4).

🔴 CHECKPOINT: Review the output before presenting. If it contains only silence/garble or a crash traceback, consult the Error handling & fallback table. Never deliver a failed transcript to the user.

### 4. (Optional) Save transcript

If user wants the transcript saved, write as `.txt` next to the video file.

## Performance reference (M3 Pro, CPU int8)

| Model   | 8min video speed | Chinese accuracy |
|---------|-----------------|------------------|
| tiny    | ~3min (2.7x)    | Poor — many errors |
| base    | ~4min (2.0x)    | Fair |
| small   | ~6min (1.3x)    | Good ← default |
| medium  | ~8min (1.0x)    | Very good |
| large-v3 | ~15min (0.5x)  | Best |

## Error handling & fallback

When transcription fails, use the table below to diagnose and recover. Each failure mode has a first-line fix and a last-resort fallback.

| Trigger | First-line fix | Still fails → fallback |
|---------|---------------|----------------------|
| `File not found` | Verify path with `ls -la "<path>"`. Quoted path may need unquoting. | Ask user for the correct absolute path |
| `ffmpeg not found` | Run `brew install ffmpeg` | Use `pip3 install ffmpeg-python` as alternative decoder |
| `No speech detected` | Confirm the file has audible speech, not just music/silence | Try `--model medium` (small models miss quiet speech) |
| `Out of memory` | Re-run with `--model base` or `--model tiny` | Split audio into shorter clips with ffmpeg `-t 120` |
| `HF download fails` | Script auto-clears proxy vars. Check network. | Pre-download model: `python3 -c "from faster_whisper import WhisperModel; WhisperModel('small')"` |
| `whisper produces garbled text` | Force language with `--language zh` or `--language en` | Try `--model medium` for better Chinese accuracy |
| Script exits with code 124 (timeout) | Video may be too long (>30 min). Split or use `--model tiny` | Background the task via terminal with timeout 900s

## Harness (Self-Eval)

The harness validates that the skill produces correct timestamped transcripts for Chinese and English audio.

### Cases

| ID | Scenario |
|----|----------|
| `case_001` | Chinese video clip → timestamped transcript with Chinese keywords |
| `case_002` | English audio file → timestamped transcript with English keywords |
| `case_003` | Audio with `--language en` flag → correct English transcript |

### Checks

| Check | What it detects |
|-------|----------------|
| `has_timestamp_format` | Output lines use `[Xs -> Ys]` format |
| `has_chinese_keywords` | Contains expected Chinese words (家长, 运动, 骨头) |
| `has_english_words` | Contains expected English words (hello, exercise, transcription) |
| `covers_duration` | Final segment timestamp ≥ 50s for a 60s clip |
| `language_detected_en` | Language correctly identified as English |
| `no_crash` | No Traceback/Error in output |

### Run

```bash
# Check one output file against all checks
python3 evals/grader.py <output-file> '<checks-json>'

# Full harness (runs transcribe on each case, grades, prints trace)
python3 evals/run_harness.py
```

### Honesty & Truthfulness

Report results exactly as they are:
- Test failed → state "failed" with the actual evidence
- Skipped verification → say "not verified", don't imply it passed
- No defensive disclaimers on correct results ("but this might not be correct")
- No false success — if output shows failure, don't claim "all passed"

## 反例与危险操作 (Anti-Patterns)

下列操作不仅无效，还可能造成不良后果。避免使用。

| 反模式 | 为什么危险 | 替代做法 |
|--------|-----------|---------|
| 跳过文件存在性检查直接跑脚本 | 路径含特殊字符(中文/#/[])时脚本报错，用户以为出了问题 | 先 `ls -la "<path>"` 确认，再执行转录 |
| 不检查 ffmpeg 安装直接转录 | ffmpeg 缺失时 faster-whisper 无法解码音频，报错不友好 | 让脚本的 ensure_deps() 检查或手动 `brew install ffmpeg` |
| 用 tiny/base 模型转写重要中文内容 | 中文同音字多，小模型产生大量错误（我们实测 tiny 出现"幸好→信号、股头→骨头"等错误） | 中文内容至少用 `small` 模型，重要内容用 `medium` |
| 用 large-v3 模型转写几秒的短音频 | 模型下载 ~3GB，耗时远超实际转录时间，大炮打蚊子 | 短音频用 `base` 或 `small` 即可 |
