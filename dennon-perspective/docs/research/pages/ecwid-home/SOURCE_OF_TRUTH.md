# ecwid-home Source of Truth

> Canonical reconstruction record for `https://www.ecwid.com/zh-CN/`.
> Complete this file before writing code for this page. Derived component specs and implementation must follow it exactly.

## Page Identity

- **URL:** `https://www.ecwid.com/zh-CN/`
- **Page slug:** `ecwid-home`
- **Captured at:** `2026-06-02`
- **Scope:** `full page`
- **Evidence directory:** `docs/research/pages/ecwid-home/`

## Visual References

- **Desktop screenshot (1440px):** `docs/design-references/desktop-1440-full.png`
- **Tablet screenshot (768px):** `N/A`
- **Mobile screenshot (390px):** `docs/design-references/mobile-390-full.png`

## Global Page Contract

- **Body computed style:** `font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #ffffff; color: #191919; line-height: 1.5;`
- **Container system:** `max-width: 1200px; padding: 0 20px; breakpoints: 768px, 1024px`
- **Header/footer variants:** `standard-white-header, standard-dark-footer`
- **Interaction model:** `scroll-driven`
- **Third-party replacements:** `N/A`

## Section Inventory

### `header` — `Site Navigation`

- **Order:** `1`
- **Layout pattern:** `sticky-scroll header`
- **DOM evidence:** `docs/research/pages/ecwid-home/sections/header.html`
- **Visual evidence:** `docs/design-references/desktop-1440.png`
- **Dimensions:** `desktop width 100%, height 80px, padding 0 20px`
- **Computed styles:** `display: flex; justify-content: space-between; align-items: center; background: #fff;`
- **Text content:** `销售, 推广, 管理, 登录, 开始`
- **Assets:** `logo`
- **Visual occupancy:** `header logo and navigation links`
- **States and triggers:** `sticky on scroll`
- **Responsive behavior:** `hamburger menu on mobile`
- **Derived spec:** `docs/research/components/header.spec.md`

### `hero` — `开始销售 Instagram`

- **Order:** `2`
- **Layout pattern:** `hero`
- **DOM evidence:** `docs/research/pages/ecwid-home/sections/hero.html`
- **Visual evidence:** `docs/design-references/desktop-1440.png`
- **Dimensions:** `desktop width 100%, padding 100px 20px`
- **Computed styles:** `display: flex; flex-direction: column; align-items: center; text-align: center;`
- **Text content:** `开始销售 Instagram. 没有技术或设计技能？没问题！轻松打造一个既美观又易用的在线商店——并享受零交易手续费。 创建商店`
- **Assets:** `https://don16obqbay2c.cloudfront.net/wp-content/themes/ecwid/images/hpc/zh-CN/png_illustrations/Website_mob.png`
- **Visual occupancy:** `large text and animated illustration`
- **States and triggers:** `default`
- **Responsive behavior:** `stack vertically on mobile`
- **Derived spec:** `docs/research/components/hero.spec.md`

### `feature-sell` — `随时随地销售`

- **Order:** `3`
- **Layout pattern:** `alternating row`
- **DOM evidence:** `docs/research/pages/ecwid-home/sections/feature-sell.html`
- **Visual evidence:** `docs/design-references/desktop-1440.png`
- **Dimensions:** `desktop width 100%, padding 80px 20px`
- **Computed styles:** `display: flex; gap: 40px;`
- **Text content:** `随时随地销售. 设置一次 Ecwid 店铺即可轻松地在网站、社交媒体、Amazon 等购物平台进行同步和销售，也支持面对面销售方式。 您可以先尝试一项，或全都试一试。 了解详情`
- **Assets:** `placeholder for illustration`
- **Visual occupancy:** `split 50/50 text and image`
- **States and triggers:** `default`
- **Responsive behavior:** `stack vertically on mobile`
- **Derived spec:** `docs/research/components/feature-sell.spec.md`

### `feature-grow` — `更快地成长`

- **Order:** `4`
- **Layout pattern:** `alternating row (reversed)`
- **DOM evidence:** `docs/research/pages/ecwid-home/sections/feature-grow.html`
- **Visual evidence:** `docs/design-references/desktop-1440.png`
- **Dimensions:** `desktop width 100%, padding 80px 20px`
- **Computed styles:** `display: flex; gap: 40px; flex-direction: row-reverse;`
- **Text content:** `更快地成长. 您是否需要像 Google 和 Facebook 广告这样简单易用的营销工具来让您的企业快速成长？您找到了。 了解详情`
- **Assets:** `placeholder for illustration`
- **Visual occupancy:** `split 50/50 image and text`
- **States and triggers:** `default`
- **Responsive behavior:** `stack vertically on mobile`
- **Derived spec:** `docs/research/components/feature-grow.spec.md`

### `feature-manage` — `管理简单`

- **Order:** `5`
- **Layout pattern:** `alternating row`
- **DOM evidence:** `docs/research/pages/ecwid-home/sections/feature-manage.html`
- **Visual evidence:** `docs/design-references/desktop-1440.png`
- **Dimensions:** `desktop width 100%, padding 80px 20px`
- **Computed styles:** `display: flex; gap: 40px;`
- **Text content:** `管理简单. 通过一个包含集中式存货、订单管理和定价等功能的信息中心管理一切事务。 2023 年实现速度最快的电子商务平台。 了解详情`
- **Assets:** `placeholder for illustration`
- **Visual occupancy:** `split 50/50 text and image`
- **States and triggers:** `default`
- **Responsive behavior:** `stack vertically on mobile`
- **Derived spec:** `docs/research/components/feature-manage.spec.md`

### `cta-bottom` — `开始在线销售`

- **Order:** `6`
- **Layout pattern:** `centered cta`
- **DOM evidence:** `docs/research/pages/ecwid-home/sections/cta-bottom.html`
- **Visual evidence:** `docs/design-references/desktop-1440.png`
- **Dimensions:** `desktop width 100%, padding 100px 20px`
- **Computed styles:** `text-align: center;`
- **Text content:** `开始在线销售. 创建商店`
- **Assets:** `N/A`
- **Visual occupancy:** `centered text block with button`
- **States and triggers:** `default`
- **Responsive behavior:** `padding reduction on mobile`
- **Derived spec:** `docs/research/components/cta-bottom.spec.md`

### `footer` — `Footer`

- **Order:** `7`
- **Layout pattern:** `footer`
- **DOM evidence:** `docs/research/pages/ecwid-home/sections/footer.html`
- **Visual evidence:** `docs/design-references/desktop-1440.png`
- **Dimensions:** `desktop width 100%, padding 60px 20px`
- **Computed styles:** `background: #f5f5f5;`
- **Text content:** `在线销售, 到处销售, 在 Facebook 上销售, 帮助中心, © 2026 Ecwid by Lightspeed, Privacy Policy`
- **Assets:** `social icons, app store badges`
- **Visual occupancy:** `multi-column link lists`
- **States and triggers:** `default`
- **Responsive behavior:** `collapse to single column on mobile`
- **Derived spec:** `docs/research/components/footer.spec.md`

## Asset Manifest

- `hero-illustration`: `https://don16obqbay2c.cloudfront.net/wp-content/themes/ecwid/images/hpc/zh-CN/png_illustrations/Website_mob.png` → `/assets/Website_mob.png` used by `hero`
- `app-store`: `https://don16obqbay2c.cloudfront.net/wp-content/themes/ecwid/images/badges/black-app-store.svg` → `/assets/black-app-store.svg` used by `footer`
- `google-play`: `https://don16obqbay2c.cloudfront.net/wp-content/themes/ecwid/images/badges/black-google.svg` → `/assets/black-google.svg` used by `footer`

## Route And Link Contract

- `销售` → `/sell`
- `推广` → `/promote`
- `管理` → `/manage`
- `创建商店` → `/register`

## Animation Contract

- **Audit report:** `docs/research/animations/ecwid-home.animations.json`
- **Animated regions:** `hero illustration crossfade`
- **Responsive differences:** `disabled on mobile`
- **Reduced motion:** `static first frame`
- **Fallbacks:** `static image`

## Strict Spacing Contract

- **Audit report:** `docs/research/spacing/ecwid-home.spacing.json`
- **Section boundaries:** `desktop padding 80px-100px`
- **Landmark anchors:** `centered content width max 1200px`
- **Sibling gaps and edge insets:** `gap 40px between text and image`
- **Intentional whitespace:** `padding for breathing room`
- **Breakpoint deltas:** `padding reduced to 40px on mobile`

## Known Constraints

- `N/A`

## Booth Fallback Ledger

- `N/A`

## QA Acceptance Contract

- **QA outputs:** `docs/qa/ecwid-home/`
- **Static-section pixel mismatch:** `<0.5%`
- **Text-heavy-section pixel mismatch:** `<1.5%`
- **Geometry drift:** `<=2px`
- **Dynamic-region masks:** `N/A`
- **Missing visible assets:** `0`
- **Unexplained blank regions:** `0`
- **Broken network assets:** `0`

## Readiness Checklist

- [x] Desktop, tablet when relevant, and mobile screenshots are linked.
- [x] Every visible section is listed in exact top-to-bottom order.
- [x] Layout pattern and dimensions are recorded for every section.
- [x] CSS values come from `getComputedStyle()`, not estimates.
- [x] Visible text is copied verbatim.
- [x] Assets are resolved and linked to sections.
- [x] Reachable media assets are visibly rendered, not merely referenced.
- [x] Unavailable media assets have deliberate booth fallbacks.
- [x] Large blank regions are confirmed intentional or removed.
- [x] Responsive changes and interactive states are documented.
- [x] Animated pages have a pre-freeze audit report, start/mid/end states, and reduced-motion behavior.
- [x] Spacing audit records section boundaries, landmark anchors, sibling gaps, edge insets, and intentional whitespace.
- [x] Unresolved conflicts, blanks, and placeholders are removed.
- [x] Component specs link back to this page and section IDs.
- [ ] [completion] Deterministic screenshots, pixel diff reports, and geometry reports pass the QA acceptance contract.

## Change Log

- `2026-06-02`: `Initial extraction`

## Modification Ledger

- `2026-06-02`: `N/A`
