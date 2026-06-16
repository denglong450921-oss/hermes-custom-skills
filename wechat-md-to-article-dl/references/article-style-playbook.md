# WeChat Article Style Playbook

Use this reference before rewriting Markdown into a public-account article. The
goal is focused copywriting first, polished HTML second.

## Public-account quality bar

A good WeChat article should give the reader a fast reason to keep reading and
a concrete payoff for finishing.

- **One promise:** the article answers one reader question or delivers one usable
  framework. Remove secondary theses.
- **Strong first screen:** title, summary, first paragraph, and first H2 explain
  what the reader will gain.
- **Mobile rhythm:** short paragraphs, clear H2s, frequent but meaningful breaks.
- **Evidence and scenes:** each key claim needs a case, data point, mechanism, or
  concrete scenario.
- **Usable ending:** close with a checklist, decision rule, next action, or
  transferable mental model.
- **Trust boundary:** business/health/technical articles must state assumptions,
  limits, risks, or applicability.
- **No generic filler:** delete motivational slogans, vague adjectives, repeated
  setup, and AI-like summary phrases.

## Style profiles

| Profile | Use for | Opening move | Structure |
|---|---|---|---|
| `explainer` 清晰科普 | General public explanation | Misunderstanding -> clear judgment | problem, concept, why it matters, how to judge, action |
| `opinion` 观点专栏 | Cognition, trends, strong claims | Contrarian judgment -> boundary | thesis, misconception, evidence, framework, closing line |
| `story` 故事叙事 | Case, memoir, brand story | Concrete scene -> conflict | scene, conflict, turn, method, takeaway |
| `framework` 方法框架 | How-to, productivity, learning | Reader outcome -> framework map | problem, map, steps, mistakes, checklist |
| `business` 商业分析 | Strategy, growth, wealth | Conclusion -> assumptions | conclusion, variables, opportunity, risk, execution |
| `technical` 技术深度 | AI, software, architecture | Engineering problem -> reader payoff | problem, goals, mechanism, implementation, boundary |
| `health` 健康科普 | Health, wellness, psychology | Reassure -> clarify evidence | misconception, facts, risk signals, daily advice, seek help |

## Rewrite moves

### Title

- Prefer promise + tension: "X 不是 Y，而是 Z".
- Prefer specific objects over big abstractions.
- Avoid stacked nouns, empty labels, and all-purpose "深度解析".
- Keep one clear hook; do not cram every keyword into the title.

### Opening

Choose exactly one opening pattern:

- **Question:** "为什么你越努力，反而越难..."
- **Scene:** "上周和一个创业者聊天，他卡在..."
- **Contrarian:** "真正的问题不是工具太少，而是..."
- **Result promise:** "读完这篇，你会拿到一套..."
- **Misconception:** "很多人把 X 理解成 Y，但..."

Keep the opening under 150 Chinese characters when possible. The first screen
should not spend all its space on background.

### Section Design

- H2 headings should sound like reader questions or argument steps.
- Each H2 should move the article forward: do not repeat the title in different
  wording.
- Use lists for frameworks and checklists, but explain why each item matters.
- Use callouts only for core judgments, risk warnings, or reusable methods.

### Paragraph and Sentence Rhythm

- One paragraph = one beat.
- Prefer 1-3 sentences per paragraph on mobile.
- Cut throat-clearing phrases: "众所周知", "在当今时代", "值得注意的是".
- Replace abstract adjectives with mechanisms: not "非常重要", but "它决定了
  后续动作能否被验证".

### Ending

Use one of these endings:

- **Checklist:** "下次遇到 X，先问自己三件事..."
- **Decision rule:** "如果 A，就做 B；如果 C，先暂停。"
- **Action path:** "今天可以先完成一个最小动作..."
- **Synthesis:** "所以 X 的本质不是..., 而是..."

## Profile-specific cautions

- `business`: no guaranteed wealth claims; name assumptions and downside.
- `health`: no diagnosis or treatment certainty; add "不能替代专业医疗建议" when
  relevant.
- `technical`: do not show code before explaining the problem it solves.
- `opinion`: every sharp sentence needs a reason; avoid slogan-only paragraphs.
- `story`: do not over-explain the moral before the story has earned it.
- `framework`: every step needs an observable action or output.

## Marker usage before conversion

Use the converter's markers sparingly:

- `==core concept==` for definitions and key terms.
- `^^key judgment^^` for one-line arguments.
- `!!must-not-miss point!!` for emphasis without color.
- `:::problem`, `:::strategy`, `:::thinking`, `:::key` for 1-2 important blocks per
  major section.

Do not mark more than 10-15% of the prose. If everything is highlighted, nothing
is highlighted.
