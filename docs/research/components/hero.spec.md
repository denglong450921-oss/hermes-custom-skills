# Component Spec: Hero

> High-fidelity reconstruction spec for the Hero section.

## Metadata
- **Component ID:** `hero`
- **Source of Truth:** `docs/research/pages/ecwid-home/SOURCE_OF_TRUTH.md`
- **Screenshot:** `docs/design-references/desktop-1440-full.png`

## Props Interface
```typescript
interface HeroProps {
  heading: string;
  subheading: string;
  cta: { label: string; href: string };
  image: { src: string; alt: string };
}
```

## Layout Pattern
- **Pattern:** Hero
- **Hierarchy:**
  - `section.hero` (flex-col, center)
    - `div.content` (max-width, text-center)
      - `h1.title`
      - `p.description`
      - `a.cta-button`
    - `div.visual`
      - `img.hero-illustration`

## Computed CSS (Desktop)
- **Padding:** `100px 20px`
- **Heading:** `fontSize: 64px, fontWeight: 800, lineHeight: 1.1, color: #191919`
- **Description:** `fontSize: 20px, lineHeight: 1.6, color: #4b4b4b, maxWidth: 800px`
- **CTA Button:** `bg: #000, color: #fff, padding: 18px 36px, borderRadius: 8px, fontSize: 18px`

## Text Content
- `开始销售 Instagram`
- `没有技术或设计技能？没问题！轻松打造一个既美观又易用的在线商店——并享受零交易手续费。`
- `创建商店` (CTA)

## Assets
- `hero-image`: `https://don16obqbay2c.cloudfront.net/wp-content/themes/ecwid/images/hpc/zh-CN/png_illustrations/Website_mob.png`

## Responsive Behavior
- **Mobile (< 768px):**
  - Padding: `60px 20px`.
  - Heading font-size: `40px`.
  - Image stacks below text.

## Implementation Checklist
- [ ] Text wrapping matches screenshot.
- [ ] Button hover effect (slight scale or opacity).
- [ ] Animation: Initial fade-in of text and image.
