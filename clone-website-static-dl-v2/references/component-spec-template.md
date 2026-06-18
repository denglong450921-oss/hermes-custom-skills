# <ComponentName> Static Clone Spec

## Overview

- **Target file:** `src/components/<ComponentName>.*`
- **Source of truth:** `docs/research/pages/<page-slug>/SOURCE_OF_TRUTH.md`
- **Source section ID:** `<section-id | header | footer>`
- **Screenshot:** `docs/design-references/<page>-<section>.png`
- **Component role:** `<header | footer | section | shared primitive>`

## Props Or Data Contract

Define the props or data object before implementation.

```ts
interface ComponentNameProps {
  className?: string;
}
```

Use optional props with defaults when the component should be reusable but still render the original clone by default.

## DOM Structure

Describe the element hierarchy and landmarks.

```text
<header>
  <a logo>
  <nav>
  <a cta>
</header>
```

## Text Content

Copy visible text verbatim.

## Assets

| Role | Local Path Or Placeholder | Source URL | Dimensions | Notes |
|---|---|---|---|---|
| `<hero image>` | `<public/assets/...>` | `<url>` | `<w x h>` | `<notes>` |

## Computed Styles

Record exact values from the rendered source page.

### Container

- `display`:
- `width`:
- `max-width`:
- `padding`:
- `margin`:
- `background`:
- `color`:

### Key Children

- `<selector or role>`:
  - `font-family`:
  - `font-size`:
  - `font-weight`:
  - `line-height`:
  - `color`:
  - `gap`:

## Static Replacement Contract

Use `N/A` when no motion or large media is involved.

- **Original behavior/media:** `<video | animation | carousel | canvas | none>`
- **Static treatment:** `<poster | first frame | placeholder | stable selected state>`
- **Reason:** `<no animation requested | over-budget | blocked | dynamic-only>`
- **Visual occupancy:** `<aspect ratio, size, background/color, label>`

## Responsive Behavior

- **Desktop 1440px:**
- **Tablet 768px:**
- **Mobile 390px:**
- **Breakpoint notes:**

## Tests And Checks

- **Before implementation:** `<command or checklist expected to fail/pass>`
- **After implementation:** `<command required to pass>`
- **Detector gate:** `<stage and report path>`

## Implementation Notes

- Keep this component independent from unrelated sections.
- Header/footer specs must not be duplicated into page sections.
- Avoid animation libraries and runtime motion code.
- Use local assets or documented placeholders only.
