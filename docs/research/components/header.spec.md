# Component Spec: Header

> High-fidelity reconstruction spec for the site navigation header.

## Metadata
- **Component ID:** `header`
- **Source of Truth:** `docs/research/pages/ecwid-home/SOURCE_OF_TRUTH.md`
- **Screenshot:** `docs/design-references/desktop-1440-full.png`

## Props Interface
```typescript
interface HeaderProps {
  navLinks: Array<{ label: string; href: string }>;
  cta: { label: string; href: string };
}
```

## Layout Pattern
- **Pattern:** Sticky-scroll header
- **Hierarchy:**
  - `header` (sticky, flex)
    - `div.container` (max-width, flex-between)
      - `a.logo`
      - `nav` (desktop: flex-gap, mobile: hidden/drawer)
      - `div.actions` (login + start button)

## Computed CSS (Desktop)
- **Background:** `#ffffff`
- **Height:** `80px`
- **Padding:** `0 20px`
- **Box Shadow:** `0 2px 4px rgba(0,0,0,0.05)` (when sticky)
- **Font Family:** `-apple-system, BlinkMacSystemFont, ...`
- **Link Color:** `#191919`
- **CTA Button:** `bg: #000, color: #fff, padding: 10px 20px, borderRadius: 4px`

## Text Content
- `销售`
- `推广`
- `管理`
- `登录`
- `开始` (CTA)

## Assets
- `logo`: `/assets/ecwid-logo.svg`

## Responsive Behavior
- **Mobile (< 1024px):**
  - Hide main `nav`.
  - Show hamburger menu icon.
  - Keep logo and "开始" CTA visible if space permits.

## Implementation Checklist
- [ ] Sticky positioning works.
- [ ] Hover states for links.
- [ ] Mobile drawer functionality.
