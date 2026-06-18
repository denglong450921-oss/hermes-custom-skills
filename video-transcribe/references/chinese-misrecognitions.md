# Chinese Whisper Misrecognition Patterns

Whisper (especially `small` model) produces systematic errors for Chinese
homophones and domain-specific terms. These are not random — they follow
predictable phonetic confusion patterns.

## Common substitutions observed in practice

| Whisper output | Likely correct | Context |
|---------------|---------------|---------|
| 跳神 | 跳绳 | Sports/physical activity |
| 生长速度 | 生长激素 | Growth/endocrinology |
| 学习签设 | 学习天赋 / 学习潜能 | Learning ability |
| 渔月 | 愉悦 | Emotional state |
| 屏次 | 频率 | Frequency/speed |
| 过德思考 / 过度的思考 | 过度思考 | Psychology/overthinking |
| 走后 | 付诸 | Action (付诸实践) |
| 副粉溃 | 负担 / 负反馈 | Psychology/cognitive load |
| 身心去皮 | 身心俱疲 | Fatigue/exhaustion |
| 内好循环 | 内耗循环 | Psychology/internal friction |
| 注一地资源 | 注意力资源 | Cognitive science |
| 杂其杂罢 | 乱七八糟 | Miscellaneous/disorder |
| 信号 | 幸好 | Positive outcome |
| 股头 | 骨头 | Anatomy |
| 折腾反说 | 这很正常 | Common phrase |
| 渔月的反馈 | 愉悦的反馈 | Reward/pleasure feedback |
| 虚荣抵制 | 休学/排斥 / 系统性抵制 | Resistance to learning |
| 进入性能状态 | 进入心流状态 | Flow state / concentration |
| 复判 | 复盘 | Review/analysis |
| 硬试 | 应试 | Exam preparation |
| 学签 | 学习潜能 / 学习天赋 | Learning potential |
| 四维导图 | 思维导图 | Mind map |
| 撑周期 | 长周期 | Long cycle / extended period |
| 沉体系 | 成体系 | Systematic / forming a system |

## When to use this table

1. After running `transcribe.py`, scan the output for any of the Whisper
   output patterns above before presenting to the user.
2. If found, silently correct them in your summary / presentation to the
   user. Do NOT expose the raw Whisper error — just deliver the corrected
   version.
3. The auto-saved `.md` file retains the original Whisper output. If the
   user needs a corrected transcript for downstream use (e.g. as source
   material for article writing), copy the file and apply corrections.

## Pattern categories

**Homophones (same pronunciation, different meaning):**
- 神 → 绳, 速 → 激, 设 → 赋, 月 → 悦, 次 → 率, 后 → 诸
- Common for single-syllable words in fast speech

**Compound word splitting errors:**
- 学习签设 → 学习 + 天赋 (model splits compound incorrectly)
- 注一地资源 → 注意力 + 资源 (model merges/confuses adjacent words)

**Domain-specific terms:**
- Medical/sports terms (跳绳, 生长激素, 骨头) are prone to substitution
- Psychology terms (过度思考, 内耗, 愉悦) get replaced with phonetically
  similar but semantically different words

## Prevention

- Use `--model medium` for important Chinese content — reduces error rate
  significantly
- Force language with `--language zh` when content is clearly Chinese
- Short clips (<2 min) can use `small` model, but always manually review
  for the common errors above
