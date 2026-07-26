# Unified Paradigm UI design language

Use this reference when a child-facing HTML course needs a visually distinctive, reusable interface. The canonical source is the complete project in `assets/unified-paradigm-ui/`; copy that folder instead of reconstructing the UI from prose or screenshots.

## Primary principle

Treat visual appeal as the first learner-facing design principle and a completion criterion. The first viewport must feel like a finished story world a child wants to enter, while pedagogy, accessibility, offline reliability, and legibility remain non-negotiable.

## Direction: soft-clay picture-book post office

- Audience: young children learning through short daily missions.
- Mood: warm, optimistic, tactile, calm, and playful—not babyish.
- Signature: a little mail bird carries completed learning through a fold-out storybook map.
- Materials: cream paper, inked outlines, soft-clay pictures, sticker-like labels, and pressable card shadows.
- Restraint: let the storybook/post-office device carry the personality; keep instructional surfaces quiet.

## Copyable visual grammar

| Role | Token |
|---|---|
| Ink / muted ink | `#47394f` / `#75677d` |
| Paper / cream | `#fffdf7` / `#fff8e8` |
| Strawberry | `#ff7895` / `#d94f70` |
| Sky | `#83d8ff` / `#2c9bca` |
| Lemon | `#ffd65c` |
| Mint | `#8de2bf` / `#2f9d77` |
| Grape | `#9480df` / `#6550b3` |
| Peach | `#ffb887` |
| Outline / pop shadow | `3px solid #47394f` / `0 8px 0 rgba(71,57,79,.16)` |
| Radii | `18px`, `26px`, `36px`; mix corners on large story surfaces |

Use a characterful local handwriting/rounded display stack for titles, a rounded local body stack for teaching copy, and a compact utility stack for labels. Never add remote font dependencies.

## Canonical components

Preserve the component grammar while adapting the curriculum:

- mail-bird mini brand and tactile top bar;
- fold-out storybook hero and day-map cards;
- daily cover with one clear mission and visible 30/70 learning meter;
- six mission tabs matching the daily learning loop;
- paper activity card with one dominant child action;
- four-up image-choice grid on wide screens and two-up grid on mobile;
- semantic correct, retry, current, completed, and locked states;
- progressive flip-card grid with ratio-safe pictures;
- page-turner navigation and meaningful course-world progress.

Every learner action must have a large target, plain active-voice label, visible focus, and immediate specific feedback. Animate consequences rather than answer choices; honor reduced motion.

## Adaptation contract

Keep:

- the token names, component relationships, tactile outline/shadow logic, page hierarchy, responsive behavior, six-stage daily shell, and accessibility states;
- one coherent visual language across all days;
- ratio-safe images and local, versioned CSS/JavaScript.

Change:

- story theme, mascot details, curriculum data, semantic pictures, audio, labels, storage key, and accent balance when the learner contract calls for it;
- one signature element so it belongs to the new subject rather than reading as a recolor.

Reject:

- adult SaaS dashboards, generic component galleries, arbitrary gradients, emoji-only learning art, unrelated illustration styles, decoration without a learning purpose, and dense front-loaded instructions.

## Handoff to another AI agent

Give the agent these three artifacts together:

1. `assets/unified-paradigm-ui/` — executable canonical project;
2. this reference — design intent and adaptation rules;
3. `assets/unified-paradigm-ui/ui-style.json` — machine-readable tokens, components, and copy workflow.

Use this instruction:

> Copy the complete Unified Paradigm UI project. Preserve its design tokens, component grammar, interaction shell, accessibility states, responsive layout, and image-ratio contract. Replace the curriculum, story world, semantic assets, audio, storage key, and copy for the new learner. Make one subject-specific signature choice, then run `node tools/validate_template.js` before and after adaptation. Do not rebuild the visual system from a screenshot.

