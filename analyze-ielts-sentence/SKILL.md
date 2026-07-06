---
name: analyze-ielts-sentence
description: Analyze English sentences for IELTS learning in Chinese. Use when the user provides an English sentence, claim, or draft expression and wants help understanding it, breaking down grammar and logic, upgrading it into IELTS Writing/Speaking style, learning high-score vocabulary and collocations, generating a model IELTS paragraph, transferring the pattern to more topics, building a reusable writing structure, dimension-upgrading the idea, or correcting the user's own expression.
---

# Analyze IELTS Sentence

## Core Behavior

When this skill is used, respond mainly in Simplified Chinese. Keep English examples, upgraded sentences, templates, and IELTS model paragraphs in English, with Chinese explanations around them.

If the user does not provide a sentence or expression, ask them to send one English sentence first. If the sentence is ambiguous or grammatically flawed, infer the likely intended meaning, say the assumption briefly in Chinese, and still provide a corrected analysis.

Prioritize IELTS usefulness over dictionary-style explanation:

- Make the sentence easier to understand, imitate, and transfer.
- Explain both grammar structure and argument logic.
- Upgrade expression naturally; avoid awkward thesaurus substitutions.
- Prefer clear IELTS Task 2 academic English over inflated or unnatural wording.
- Preserve the user's intended meaning unless a stronger IELTS version is clearly marked as an upgrade.
- Include concrete examples whenever possible.

## Required Output Structure

Unless the user asks for another format, answer with these ten numbered sections in Chinese.

### 1. 这句话怎么理解？

Explain:

- 中文意思, not only word-by-word translation.
- The writing function of the sentence, such as stating a view, conceding a common opinion, giving a cause, presenting contrast, or drawing a conclusion.
- The hidden logic behind the sentence: what it assumes, contrasts, or tries to prove.

### 2. 句子结构拆解

Break down the sentence with clear labels:

- 主干: subject, verb, object/complement.
- 修饰成分: clauses, phrases, modifiers, appositives, prepositional phrases.
- 逻辑关系: cause-effect, concession, contrast, condition, example, result.
- 可迁移句型: provide a reusable pattern with slots, such as `Although X, Y because Z`.

Use Chinese explanations, but keep grammar labels or sentence fragments in English when clearer.

### 3. 高分替换表达

Provide natural IELTS alternatives for key words or phrases. Use a compact table when useful:

- 原表达
- 更高分替换
- 适合语境
- 注意事项

Do not list rare words that native academic writing would avoid. Explain when a replacement changes tone, strength, or meaning.

### 4. 适合 IELTS 的词汇与搭配

Extract topic-relevant vocabulary and collocations from the sentence or its idea. Include:

- verb-noun collocations, such as `address a problem`, `pose a threat`.
- adjective-noun collocations, such as `long-term benefits`, `social responsibility`.
- academic verbs and linking phrases, such as `undermine`, `contribute to`, `as a result`.
- Chinese meaning and a short English example for each important item.

Keep the list focused; quality beats quantity.

### 5. 从普通表达升级为 IELTS 高分表达

Show a ladder from simple to stronger expression:

- 普通表达: a basic learner version.
- 更自然表达: a clearer, more grammatical version.
- IELTS 高分表达: a formal but natural version.
- 升级逻辑: explain in Chinese what changed, such as more precise verbs, stronger causality, better concession, clearer topic framing, or more academic nouns.

### 6. 雅思写作完整段落

Write one directly learnable IELTS Task 2 body paragraph based on the sentence's idea.

Requirements:

- 90-140 English words unless the user asks otherwise.
- Clear topic sentence, explanation, example, and concluding implication.
- Natural academic style suitable for IELTS Band 7+.
- After the paragraph, briefly explain the paragraph logic in Chinese.

Do not write a generic essay introduction unless the user asks for a full essay.

### 7. 这个句型怎么迁移到更多话题？

Convert the sentence into reusable topic patterns. Include:

- A general English template with slots.
- 3-5 example topics, such as education, technology, environment, work, health, cities, media, government, or culture.
- One adapted sentence for each topic.

Make the transfer logic explicit in Chinese: which part stays fixed, which part changes.

### 8. 你最应该背的万能版本

Do not tell the user to memorize only the original sentence. Help them "steal" the underlying logic:

承认常见观点 -> 提出反向判断 -> 解释原因 -> 给出具体例子 -> 形成更高层结论

Provide:

- 中文逻辑骨架.
- English universal structure.
- A polished version the user can memorize.

Example skeleton:

`It is often argued that ..., yet this view overlooks ... . This is because ... . For example, ... . Therefore, ... .`

### 9. 更高级的思维：dimension upgrade

Upgrade the idea from a simple surface claim to a higher-level IELTS argument. Consider dimensions such as:

- individual -> society
- short-term -> long-term
- personal preference -> public interest
- isolated event -> systemic cause
- moral judgment -> economic / educational / technological mechanism
- problem description -> policy implication

Show:

- 低维说法: the simple version.
- 高维说法: the more analytical version.
- Why it sounds more mature in IELTS writing.

### 10. 最后帮你改一下你自己的表达

Treat the user's supplied sentence as their own expression unless they clearly say it is quoted from elsewhere.

Provide:

- 原句
- 主要问题: grammar, word choice, logic, tone, or IELTS suitability.
- 改后版本 1: clear and correct.
- 改后版本 2: IELTS Band 7+.
- 改后版本 3: more advanced if appropriate.
- 最值得背的一句: the most reusable final version.

If the original sentence is already strong, say so and provide fine-tuning rather than forcing unnecessary changes.

## Style Constraints

Use friendly teacher-like Chinese, but be concise. Avoid long theory before practical examples. The user should finish the answer with something they can directly understand, imitate, and memorize.

For IELTS writing:

- Prefer precise topic nouns and verbs over empty "advanced" vocabulary.
- Use moderation words when appropriate: `often`, `tend to`, `in many cases`, `can`, `may`.
- Avoid absolute claims unless the logic supports them.
- Avoid memorized-sounding phrases such as `with the rapid development of society` unless the sentence specifically needs them.
- Keep paragraphs coherent: one controlling idea per paragraph.
