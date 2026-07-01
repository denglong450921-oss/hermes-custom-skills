---
name: draft-to-high-quality-prose
description: Transform rough drafts, notes, academic prose, essays, articles, speeches, scripts, reports, emails, or bilingual Chinese/English text into clear, fluent, high-quality prose. Use when the user asks to polish, rewrite, smooth, tighten, improve readability, remove AI-flavored or bureaucratic writing, strengthen sentence and paragraph flow, diagnose why prose feels stiff or scattered, or apply Liu Junqiang's "flow" method from Writing Is a Craft.
---

# Draft To High Quality Prose

Rewrite drafts by rebuilding the reader's path. Do not merely beautify wording. Preserve the user's meaning, facts, stance, names, numbers, citations, and necessary terminology while improving clarity, flow, structure, and rhythm.

This skill uses a harness extracted from Liu Junqiang's "flow" framework in `references/liu-flow-framework.md`. Read that reference when the request is substantial, the draft is more than a few paragraphs, the user asks for diagnosis, or the prose has academic, bureaucratic, AI-flavored, or structural problems.

## Default Response Contract

For ordinary rewrite requests, return:

```markdown
## 改写稿
<rewritten prose>

## 关键改动
- <3-6 notes on the structural changes that most improved the prose>

## 仍需确认
- <only include if audience, facts, tone, or missing context materially affect the rewrite>
```

If the user asks for only the revised text, return only the revised text. If the user asks for diagnosis, diagnose before rewriting and wait if they asked to review first.

## Rewrite Harness

Use this sequence unless the user specifies a narrower edit.

1. **Lock invariants**: Identify facts, claims, names, numbers, citations, voice constraints, audience, format, and any forbidden changes.
2. **Find the main line**: State internally what the piece is really trying to say. Rebuild around that line.
3. **Choose mode**:
   - `transparent-glass`: clear public explanation, report, article, educational prose.
   - `academic-clarity`: paper, proposal, literature review, research memo; preserve precision and hedging.
   - `public-essay`: newsletter, post, speech, op-ed; sharpen rhythm without sacrificing accuracy.
   - `minimal-edit`: preserve the author's voice and only fix clarity blockers.
4. **Diagnose by layer**: Check word abstraction, sentence trunk, sentence chaining, rhythm, paragraph job, section route, and layout.
5. **Rewrite structurally**: Move, split, combine, concretize, and re-sequence before polishing word choice.
6. **Verify**: Confirm the rewrite preserves meaning, reduces friction, and makes the reader's route visible.

## Core Moves

- **Lower empty abstractions**: Replace vague nouns and verbs with concrete actors, actions, mechanisms, examples, or stakes.
- **Expose sentence trunks**: Keep concrete subjects near observable verbs; move heavy conditions after the main clause.
- **Chain sentences**: Start with old or familiar information, end with new information, and let the next sentence pick it up.
- **Vary rhythm**: Split blocked long sentences; combine choppy short ones; land key points with shorter sentences.
- **One paragraph, one job**: Give each paragraph one purpose and make the first sentence carry the point when possible.
- **Make sections navigable**: Use headings, topic sentences, and signposts when they reduce reader effort.

## Guardrails

- Do not invent evidence, examples, citations, statistics, or claims.
- Do not flatten the user's distinctive voice unless clarity requires it.
- Do not over-polish into slogans, generic inspirational prose, or "AI essay" symmetry.
- Do not replace domain terms that are necessary for precision; define or scaffold them instead.
- Do not explain every micro-edit unless the user asks for an edit memo.

## Quick Diagnostic

When prose still feels wrong, check in this order:

1. Does the piece know what it wants?
2. Can the reader follow one main path?
3. Are key claims too abstract or unsupported?
4. Can the reader quickly find who does what?
5. Does each sentence hand something to the next?
6. Does old information come before new information?
7. Are sentence lengths controlled and varied?
8. Does each paragraph do one job?
9. Can a skim reader understand the argument from headings and first sentences?

## Reference Loading

Load `references/liu-flow-framework.md` for:

- detailed rewrite rules and decision tables
- Chinese prose revision heuristics
- academic and bureaucratic prose cleanup
- paragraph and section restructuring
- a ready-to-use prompt template

