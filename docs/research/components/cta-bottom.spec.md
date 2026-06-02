# Component Spec: CTA Bottom

> High-fidelity reconstruction spec for the bottom call-to-action section.

## Metadata
- **Component ID:** `cta-bottom`
- **Source of Truth:** `docs/research/pages/ecwid-home/SOURCE_OF_TRUTH.md`
- **Screenshot:** `docs/design-references/desktop-1440-full.png`

## Props Interface
```typescript
interface CTABottomProps {
  heading: string;
  cta: { label: string; href: string };
}
```

## Layout Pattern
- **Pattern:** Centered CTA
- **Hierarchy:**
  - `section.cta-bottom` (bg: #fff, text-center)
    - `div.container` (max-width)
      - `h2.title`
      - `a.cta-button`

## Computed CSS (Desktop)
- **Padding:** `120px 20px`
- **Heading:** `fontSize: 56px, fontWeight: 800, color: #191919, marginBottom: 40px`
- **CTA Button:** `bg: #000, color: #fff, padding: 20px 40px, borderRadius: 8px, fontSize: 20px`

## Text Content
- `开始在线销售`
- `创建商店` (CTA)

## Responsive Behavior
- **Mobile (< 768px):**
  - Heading font-size: `36px`.
  - Padding: `80px 20px`.

## Implementation Checklist
- [ ] Button centered correctly.
- [ ] Hover states match Hero button.
