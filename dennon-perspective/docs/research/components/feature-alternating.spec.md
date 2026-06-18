# Component Spec: Feature (Alternating Row)

> High-fidelity reconstruction spec for alternating feature sections.

## Metadata
- **Component ID:** `feature-sell`, `feature-grow`, `feature-manage`
- **Source of Truth:** `docs/research/pages/ecwid-home/SOURCE_OF_TRUTH.md`
- **Screenshot:** `docs/design-references/desktop-1440-full.png`

## Props Interface
```typescript
interface FeatureProps {
  heading: string;
  description: string;
  cta: { label: string; href: string };
  image: { src: string; alt: string };
  reverse?: boolean;
}
```

## Layout Pattern
- **Pattern:** Alternating row
- **Hierarchy:**
  - `section.feature` (flex, items-center, gap-10)
    - `div.text-content` (flex-1)
      - `h2.title`
      - `p.description`
      - `a.link`
    - `div.visual-content` (flex-1)
      - `img.feature-image`

## Computed CSS (Desktop)
- **Padding:** `80px 0`
- **Heading:** `fontSize: 48px, fontWeight: 700, color: #191919`
- **Description:** `fontSize: 18px, lineHeight: 1.6, color: #4b4b4b`
- **Link:** `color: #000, fontWeight: 600, borderBottom: 2px solid #000`

## Responsive Behavior
- **Mobile (< 1024px):**
  - Change `flex-direction` to `column`.
  - Always show image above text or below text consistently.
  - Text alignment: `center`.

## Implementation Checklist
- [ ] `reverse` prop correctly swaps image/text order.
- [ ] Responsive stack order.
- [ ] Link hover effect.
