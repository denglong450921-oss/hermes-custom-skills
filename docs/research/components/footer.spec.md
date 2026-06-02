# Component Spec: Footer

> High-fidelity reconstruction spec for the site footer.

## Metadata
- **Component ID:** `footer`
- **Source of Truth:** `docs/research/pages/ecwid-home/SOURCE_OF_TRUTH.md`
- **Screenshot:** `docs/design-references/desktop-1440-full.png`

## Props Interface
```typescript
interface FooterProps {
  sections: Array<{
    title: string;
    links: Array<{ label: string; href: string }>;
  }>;
  bottomLinks: Array<{ label: string; href: string }>;
  copyright: string;
}
```

## Layout Pattern
- **Pattern:** Multi-column footer
- **Hierarchy:**
  - `footer` (bg: #f5f5f5, padding-top: 60px)
    - `div.container` (grid, grid-cols-4)
      - `div.column` (link lists)
    - `div.bottom-bar` (flex-between, border-t)
      - `div.copyright`
      - `div.legal-links`
      - `div.social-icons`

## Computed CSS (Desktop)
- **Background:** `#f5f5f5`
- **Color:** `#191919`
- **Font Size:** `14px` (links), `16px` (titles)
- **Column Gap:** `40px`

## Text Content
- `在线销售`
- `到处销售`
- `在 Facebook 上销售`
- `帮助中心`
- `© 2026 Ecwid by Lightspeed`
- `Privacy Policy`

## Assets
- `app-store`: `/assets/black-app-store.svg`
- `google-play`: `/assets/black-google.svg`

## Responsive Behavior
- **Mobile (< 768px):**
  - Stack columns vertically.
  - Text alignment: `left`.
  - Accordion style for columns (optional but common).

## Implementation Checklist
- [ ] Grid layout works on desktop.
- [ ] Responsive stack on mobile.
- [ ] Social icons correctly rendered.
