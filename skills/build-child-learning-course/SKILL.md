---
name: build-child-learning-course
description: Develop and critique concept-only designs for child-friendly learning games and game-based courses across English, mathematics, Chinese, and other subjects. Use whenever a user asks for children's educational game ideas, an engaging learning-game concept, a playful course proposal, game mechanics children will readily accept, motivation or replayability methods, or a high-level game-based learning plan. Return only design philosophies, concepts, proposals, and methods—not HTML, code, assets, prototypes, production files, or implementation work.
---

# Build Child Learning Course

Design learning games that children can understand quickly, choose willingly, and enjoy replaying. Present the thinking behind the experience rather than building the experience itself.

## Scope

This is a concept-design skill. Produce prose, tables, and simple text diagrams only when they clarify a design relationship.

Stay at these levels:

- design philosophy and rationale;
- learner and context assumptions;
- game concepts, themes, mechanics, and learning actions;
- high-level course or session proposals;
- progression, motivation, feedback, and replayability methods;
- accessibility, safety, and concept-validation methods;
- tradeoffs and recommendations.

Do not produce or modify:

- HTML, CSS, JavaScript, application code, or technical architecture;
- interactive prototypes, runnable courseware, or detailed UI specifications;
- images, audio, animation files, datasets, or other assets;
- folder structures, ZIP packages, deployment instructions, or browser tests;
- claims that a proposed game has been implemented or validated with children.

If the user asks for a finished digital product, provide a concept specification that another implementation workflow can use. Keep this skill's own response conceptual.

## Route the references

- Read [references/learning-science.md](references/learning-science.md) before proposing the learning loop.
- Read [references/game-patterns.md](references/game-patterns.md) before selecting mechanics. Treat it as a library of learner actions and evidence types, not as a software specification.
- Read the relevant part of [references/subject-patterns.md](references/subject-patterns.md) when the request names a school subject. Extract only the learning representations and activity ideas.
- Do not use the implementation specification, QA checklist, visual build rules, or bundled scripts for this concept-only workflow.

## 1. Frame the child and the play context

Determine or reasonably infer:

- age and developmental stage;
- prior knowledge, language, and reading level;
- interests, familiar play patterns, and likely sources of hesitation;
- whether play is solo, cooperative, family-supported, classroom-based, physical, digital, or mixed;
- session length, environment, accessibility needs, and available materials;
- the observable learning outcome.

Ask only when an unknown would materially change the proposal. Otherwise state the assumption and continue.

Avoid treating “children” as one audience. A mechanic that delights a five-year-old may feel babyish, confusing, or socially risky to a ten-year-old.

## 2. Write the fun promise

Express in one sentence what the child gets to do and why that action is enjoyable.

A useful fun promise describes:

- an appealing role or fantasy;
- a clear, concrete action;
- a satisfying change caused by the child's decision;
- a reason to try again.

Prefer promises such as “build a creature by solving shape puzzles” over adult-facing goals such as “practice geometry through gamification.” The learning objective guides the design, but the child experiences agency, curiosity, mastery, expression, humor, discovery, or connection.

## 3. Make the play action carry the learning

Choose a core game verb that exercises the target skill directly: match, sort, build, predict, explain, imitate, sequence, compare, search, or decide.

For each proposed mechanic, connect:

| Design question | Required answer |
|---|---|
| What does the child do? | One observable play action |
| What must the child think about? | The knowledge or strategy being retrieved |
| What changes because of the choice? | A meaningful game consequence |
| What shows learning? | Recognition, production, explanation, construction, or transfer evidence |
| Why repeat it? | A new challenge, strategy, combination, story consequence, or expressive choice |

If the entertaining action and the learning action are separate, redesign the loop. A quiz followed by an unrelated animation is a reward wrapper, not an integrated learning game.

## 4. Design for ready acceptance

Reduce the distance between first contact and successful play:

- begin with one visible goal and one obvious action;
- demonstrate through a playable first turn rather than a long explanation;
- use familiar interaction patterns and introduce novelty through content or consequence;
- give an early success without making the game feel fake;
- keep reading and working-memory demands appropriate for the age;
- let the child make a meaningful choice within the first minute;
- make mistakes safe, specific, and recoverable;
- preserve dignity by avoiding babyish language, public embarrassment, and punitive failure;
- offer accessible alternatives when speed, sound, speech, dragging, color, or fine motor control is not essential to the learning goal.

Acceptance is not the same as instant excitement. A calm puzzle, collaborative story, collecting system, or make-believe task may be more inviting than constant spectacle.

## 5. Sustain enjoyment without manipulation

Build enjoyment from competence, autonomy, curiosity, and connection:

- **Competence:** challenges are readable, feedback identifies the useful next action, and support fades as skill grows.
- **Autonomy:** offer bounded choices of path, tool, character, order, strategy, or expression.
- **Curiosity:** reveal consequences, patterns, story information, or new combinations through play.
- **Connection:** use cooperative goals, teach-back, shared discoveries, or a warm guide character when socially appropriate.
- **Meaning:** let progress change something the child cares about inside the game world.

Use celebration to acknowledge effort, strategy, and improvement. Do not rely on streak anxiety, loss pressure, endless variable rewards, shaming, deceptive scarcity, ads, purchases, or compulsive retention patterns.

## 6. Shape the core loop and progression

Describe the shortest satisfying loop:

1. Notice a goal or mystery.
2. Choose or perform a learning-relevant action.
3. See an immediate, understandable consequence.
4. Receive a useful clue, correction, or confirmation.
5. Decide whether to retry, vary the strategy, or advance.

Then show how the same familiar loop deepens:

- **Welcome:** teach the play language with low-risk success.
- **Explore:** introduce variation and meaningful choices.
- **Master:** reduce support and combine known elements.
- **Transfer:** use the skill in a new situation or representation.
- **Revisit:** create a fresh reason to replay rather than merely increasing quantity or speed.

For a multi-session course, prefer a small, coherent family of reusable mechanics. Familiarity lowers interface effort; novelty should come from decisions, content, combinations, and consequences.

## 7. Offer a small concept portfolio

When the request is open-ended, propose two or three genuinely different concepts. Compare them by:

- child appeal and age fit;
- strength of the learning-action connection;
- ease of understanding;
- replay potential;
- adult support required;
- accessibility and social-safety risks.

Recommend one concept and explain the tradeoff in plain language. Do not inflate minor theme changes into separate concepts.

When the user already has a clear direction, refine that direction instead of forcing alternatives.

## 8. Describe a concept-validation method

Propose lightweight ways to test the idea before implementation:

- explain the premise to a child and ask what they think they would do;
- run a paper or verbal first-turn walkthrough;
- observe time to first independent action;
- note voluntary replay, strategy changes, requests for help, confusion, and emotional recovery after mistakes;
- ask the child what they enjoyed, disliked, expected, and would change;
- check whether the child can demonstrate the target skill without the game fiction.

Separate evidence:

- **acceptance:** willingness to start and clarity about what to do;
- **enjoyment:** positive engagement, agency, curiosity, or voluntary return;
- **learning:** improved independent performance or transfer;
- **comfort:** absence of avoidable frustration, shame, overload, exclusion, or coercion.

Do not claim that engagement or learning is proven until relevant children have actually been observed.

## Response structure

Use the user's language and adapt the length to the request.

```markdown
# [Concept title]

## Learner and context
[Assumptions that shape the design]

## Design philosophy
[Why this approach should feel inviting and worthwhile]

## Fun promise
[One child-facing sentence]

## Recommended game concept
- Fantasy or role:
- Learning objective:
- Core game verb:
- Meaningful choices:
- Evidence of learning:

## Core loop
[Short numbered loop]

## Acceptance and enjoyment methods
[Onboarding, agency, challenge, feedback, dignity, accessibility]

## Progression and replay
[Welcome → explore → master → transfer → revisit]

## Concept-validation method
[What to observe before implementation]

## Alternatives and tradeoffs
[Include only when useful]
```

End with the clearest next design decision. Do not append code, production steps, or technical deliverables.
