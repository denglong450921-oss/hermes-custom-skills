# <ComponentName> Specification

## Overview
- **Target file:** `src/components/<ComponentName>.tsx`
- **Screenshot:** `docs/design-references/<screenshot-name>.png`
- **Interaction model:** <static | click-driven | scroll-driven | time-driven>

## Props Interface

Define the exact React component's props TypeScript interface. This is the contract the builder must implement — without it, builders create hardcoded components.

```typescript
interface ComponentNameProps {
  heading?: string;
  subtitle?: string;
  ctaText?: string;
  ctaHref?: string;
  images?: { src: string; alt: string }[];
  cards?: SupportCardData[];
}
```

**Required:** The builder MUST accept these props with sensible defaults so the component works both standalone and driven by `page.tsx` data flow. Mark props as `optional` (with `?`) when the original data lives in the component but could be overridden.

## DOM Structure
<Describe the element hierarchy — what contains what>

## Computed Styles (exact values from getComputedStyle)

### Container
- display: ...
- padding: ...
- maxWidth: ...

### <Child element 1>
- fontSize: ...
- color: ...

## States & Behaviors

### <Behavior name>
- **Trigger:** <exact mechanism — scroll position 50px, IntersectionObserver rootMargin "-30% 0px", click on .tab-button, hover>
- **State A (before):** maxWidth: 100vw, boxShadow: none, borderRadius: 0
- **State B (after):** maxWidth: 1200px, boxShadow: 0 4px 20px rgba(0,0,0,0.1), borderRadius: 16px
- **Transition:** transition: all 0.3s ease
- **Implementation approach:** <CSS transition + scroll listener | IntersectionObserver | CSS animation-timeline | etc.>

### Hover states
- **<Element>:** <property>: <before> → <after>, transition: <value>

## Per-State Content (if applicable)

### State: "Featured"
- Title: "..."
- Cards: [{ title, description, image, link }, ...]

## Assets
- Background image: `public/images/<file>.webp`
- Icons used: <ArrowIcon>, <SearchIcon> from icons.tsx

## Text Content (verbatim)
<All text content, copy-pasted from the live site>

## Implementation Notes
- **Customizations applied:** <describe any user-requested changes>
- **Layout deviations:** <if user requested layout changes, document them>
- **Inverted CTA button:** if this section has a colored background, note inverted button style
- **Known limitations:** <anything the builder should know>

## Responsive Behavior
- **Desktop (1440px):** <layout description>
- **Tablet (768px):** <what changes>
- **Mobile (390px):** <what changes>
- **Breakpoint:** layout switches at ~<N>px
