---
name: swihub-ppt-template
description: >
  Swihub Solutions LLC business presentation template. Professional financial-services
  deck with serif titles, gold accent cards, and illustrated content layouts.
  Use when creating Swihub-branded pitch decks, investor presentations, board materials,
  or employee handbooks with a polished corporate aesthetic.
---

# Swihub PPT Template — Complete Design System

Template: `assets/template.pptx` (10.00" × 5.62", 16:9, 1 layout: DEFAULT, 0 placeholders)

## Extracted Assets

| File | Source | Dimensions | Size | Purpose |
|------|--------|-----------|------|---------|
| `assets/template.pptx` | Original deck | — | — | 32-slide template |
| `assets/background.png` | Picture 4 | 658×1425 | 245KB | Full-bleed background on every slide |
| `assets/logo.png` | 图片 9 | 1126×291 RGBA | 305KB | Transparent logo — cover slide only |

## Design DNA (from PPTX shape audit)

> **Full design specification** (17 sections, 477 lines) at:
> `openclaw-imports/ppt-master/templates/layouts/swihub_yellow/design_spec.md`
> Covers Core Design Principles, Signature Design Elements, Common Components (SVG recipes),
> Chart Specifications, Asset Specification, Icon Usage, Color Application Examples, and Usage Instructions.
> The inline summary below is the operational condensed version.

### Typography System

| Role | Font | Size | Weight | Color |
|------|------|------|--------|-------|
| Page Title | Playfair Display | 24-25pt | Bold | `#333333` |
| Cover Title | Playfair Display | 25pt | Bold | `#333333` |
| Gold Emphasis | Playfair Display | 15-17pt | Bold | `#D4AF37` |
| Section Quote | Playfair Display | 13-14pt | Bold | (varies) |
| Tagline / Body Lead | Open Sans | 14pt | Regular | `#333333` |
| Body Text | Open Sans | 9-11pt | Regular | `#333333` |
| Section Label | Open Sans | 10pt | Bold | `#7F8C8D` or `#D4AF37` |
| Card Title | Open Sans | 10pt | Bold | `#D4AF37` |
| Numeric KPI | Open Sans | 10-11pt | Bold | (varies) |
| Small Body | Open Sans | 9pt | Regular | `#333333` |
| Footer Conclusion | Playfair Display | 13pt | Bold | (light on dark bg) |

> **Font pairing principle**: Playfair Display (serif) → authority, prestige, financial trust. Open Sans (sans-serif) → readability, modern clarity. Gold accent (#D4AF37) reserved for key takeaway text — never for body paragraphs.

### Color Palette

| Role | HEX | Usage |
|------|-----|-------|
| Gold Accent | `#D4AF37` | Emphasis text, left-border bars, card titles, decorative strips |
| Dark Gold | `#BF9000` | Buttons, solid accent shapes, bottom bar fills |
| Title Text | `#333333` | Page titles, card body titles |
| Body Text | `#333333` | All body/description text |
| Label Gray | `#7F8C8D` | Section labels, metadata |
| Card Background | (shape fill) | Light cream/white rectangles with no outline |
| Bottom Bar Fill | (shape fill) | Colored rectangle spanning full width |
| White Text on Gold | `#FFFFFF` | Text on dark accent backgrounds |

### The Card DNA (Critical Pattern)

Every content card follows this exact structure — it's the atomic unit of this template:

```
Shape (rectangle, card background)        ← container, no outline, light fill
  Shape (0.10" wide gold bar on left)      ← #D4AF37 accent bar, same height as card
  Text (section label, 10pt Bold)          ← #7F8C8D label above body text
  Text (body text, 9-11pt)                 ← #333333 or #D4AF37 for emphasis
```

**Card construction recipe** (programmatic):
```python
# Create a card: background + gold left-bar + label + body
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def create_card(slide, x, y, w, h, label, body, gold_bar=True):
    """Create a Swihub-style card with gold left-border accent."""
    # Background rectangle
    bg = slide.shapes.add_shape(1, x, y, w, h)  # MSO_SHAPE.RECTANGLE = 1
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)  # or cream
    bg.line.fill.background()  # no outline
    
    if gold_bar:
        bar = slide.shapes.add_shape(1, x, y, Inches(0.10), h)
        bar.fill.solid()
        bar.fill.fore_color.rgb = RGBColor(0xD4, 0xAF, 0x37)
        bar.line.fill.background()
    
    # Label
    lbl = slide.shapes.add_textbox(x + Inches(0.30), y + Inches(0.10), w - Inches(0.40), Inches(0.30))
    lbl.text_frame.paragraphs[0].text = label
    lbl.text_frame.paragraphs[0].font.size = Pt(10)
    lbl.text_frame.paragraphs[0].font.bold = True
    lbl.text_frame.paragraphs[0].font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)
    
    # Body
    body_tf = slide.shapes.add_textbox(x + Inches(0.30), y + Inches(0.45), w - Inches(0.40), h - Inches(0.55))
    body_tf.text_frame.word_wrap = True
    body_tf.text_frame.paragraphs[0].text = body
    body_tf.text_frame.paragraphs[0].font.size = Pt(10)
    body_tf.text_frame.paragraphs[0].font.color.rgb = RGBColor(0x33, 0x33, 0x33)
```

### Grid Layouts (Exact Coordinates)

**4-Column Grid** (slides 2, CSR features):
| Column | x | y | w | h |
|--------|---|---|---|---|
| Col 1 | 0.50" | 2.66" | 2.10" | 1.20" |
| Col 2 | 2.75" | 2.66" | 2.10" | 1.20" |
| Col 3 | 5.00" | 2.66" | 2.10" | 1.20" |
| Col 4 | 7.25" | 2.66" | 2.10" | 1.20" |

**3-Column Grid** (slides 7-8, pain points):
| Column | x | y | w | h |
|--------|---|---|---|---|
| Col 1 | 0.50" | ~2.00" | 2.80" | varies |
| Col 2 | 3.60" | ~2.00" | 2.80" | varies |
| Col 3 | 6.70" | ~2.00" | 2.80" | varies |

**3-Column Card Grid** (slide 31, closing):
| Column | x | y | w | h |
|--------|---|---|---|---|
| Col 1 | 0.80" | 1.20" | 2.40" | varies |
| Col 2 | 3.80" | 1.20" | 2.40" | varies |
| Col 3 | 6.80" | 1.20" | 2.40" | varies |

**2×2 Feature Grid** (slides 24-26):
| Position | x | y | w | h |
|----------|---|---|---|---|
| Top-Left | 0.39" | 2.67" | 2.27" | 0.68" |
| Top-Right | 2.87" | 2.67" | 2.27" | 0.68" |
| Bottom-Left | 0.39" | 3.84" | 2.27" | 0.68" |
| Bottom-Right | 2.87" | 3.84" | 2.27" | 0.68" |

### Slide Types Reference

| Type | Source Slide | Key Elements | Duplicate From |
|------|-------------|--------------|----------------|
| Cover | 0 | Centered title + gold subtitle + logo + tagline | slide 0 |
| Content (left cards) | 1 | Title + gold accent cards with left border bars | slide 1 |
| 4-col feature grid | 2 | Title + 4 card grid + bottom conclusion bar | slide 2 |
| Split content (left/right) | 3 | Left content block + right image/decoration | slide 3 |
| Milestone | 4 | Title + left event block + right details + bottom bar | slide 4 |
| Location/HQ | 5-6 | Title + content with decorative element | slide 5 |
| 3-col challenge cards | 7 | Title + subtitle + 3 problem cards | slide 7 |
| 3-col solution cards | 8 | Title + 3 feature cards | slide 8 |
| Mechanism/Deposit | 9-10 | Title + details with card layout | slide 9 |
| Pricing card | 11-13 | Title + emoji KPI metrics + feature checklist | slide 11 |
| Team/Values grid | 14 | Title + 4 icon cards | slide 14 |
| Expansion/Map | 15 | Title + location list | slide 15 |
| Table view | 16 | Title + sectioned tables | slide 16 |
| Rewards system | 17-18 | Title + tier tables | slide 17 |
| Rules/Strategy | 19 | Title + rule boxes | slide 19 |
| Hierarchy (2 roles) | 20 | Title + 2 role cards (side by side) | slide 20 |
| Hierarchy (2 roles) | 21-22 | Title + 2 role cards | slide 21 |
| Hierarchy (1 role) | 23 | Title + single spotlight card | slide 23 |
| Feature 2×2 grid | 24-26 | Title + 2×2 capability cards | slide 24 |
| Team member | 27 | Title + profile card | slide 27 |
| Onboarding | 28 | Title + trial metrics + CTA | slide 28 |
| Withdrawal | 29 | Title + process steps | slide 29 |
| FAQ / Support | 30 | Title + support cards | slide 30 |
| Closing CTA | 31 | Lead-in + 3 value cards + quote + tagline + location | slide 31 |

### Full Slide Shape Catalog (All 32 Slides)

```
=== Slide 0: Cover ===
  Picture 4       (2.19,-2.19,5.62,10.00)  Full-bleed background image
  Picture 6       (2.19,-2.19,5.63,10.00)  Background overlay variant
  图片 9           (1.74,1.35,5.82,1.50)    Logo image (centered)
  矩形 7           (3.85,3.58,2.29,0.06)    Gold decorative line under subtitle
  Text 0          (0.50,2.81,9.00,0.80)    COMPANY NAME (Playfair 25pt Bold)
  Text 1          (3.57,3.61,2.85,0.40)    Subtitle (Playfair 15pt, gold)
  Text 4          (0.50,4.80,9.00,0.50)    Tagline (Open Sans 14pt)

=== Slide 1: Mission & Vision ===
  Picture 4       (2.19,-2.19,5.62,10.00)  Background image
  图片 23          (5.35,2.58,4.60,2.98)    Right decorative image
  Text 0          (0.43,0.22,9.00,0.50)    TITLE (Playfair 24pt Bold #333333)
  [Card pattern repeated 3 times:]
    Shape (bg)    (0.50,y,9.00,0.80)       White card background
    Shape (bar)   (0.50,y,0.10,0.80)       Gold left-border bar
    Text (label)  (0.80,y+0.04,...)         Section label (Open Sans 10pt #7F8C8D)
    Text (body)   (0.80,y+0.30,...)         Body (Playfair 17pt #D4AF37 or Open Sans 10pt #333333)
  [Capability cards at bottom with left accent bars:]
    Shape + bar + bold label + body text per row

=== Slide 2: CSR ===
  Picture 4       Background image
  Text 0          (0.50,0.20,9.00,0.60)    TITLE
  Text 1          (0.50,0.80,9.00,0.40)    Core concept (gold Open Sans 11pt)
  Text 2          (0.50,1.20,9.00,1.20)    Commitment text
  Text 3          (0.50,2.26,9.00,0.40)    Section header
  [4-column card grid at y=2.66:]
    Shape (bg) + icon image + gold title + small body per card
  Text 16         (0.50,4.00,9.00,0.70)    Investment areas
  Shape 17        (0.00,4.90,10.00,0.60)   Bottom conclusion bar
  Text 18         (0.00,4.90,10.00,0.60)   Conclusion text (Playfair 13pt Bold)

=== Slide 3: Philanthropy ===
  Picture 4       Background image
  Text 0          (0.50,0.20,9.00,0.50)    TITLE
  Text 1          (0.50,0.70,9.00,0.30)    Core concept (gold Open Sans)
  Shape 2         (0.50,1.10,4.30,2.30)    Left content block
    Text 3        (0.80,1.20,3.70,0.30)    Sub-header (Playfair 13pt)
    Text 4        (0.80,1.60,3.70,1.70)    Body text
  Text 5          (0.50,3.50,4.30,0.30)    Values header (Playfair 10pt #D4AF37)
  [Value rows: Shape bg + gold label (Open Sans 9pt Bold) + body (Open Sans 11pt)]

=== Slide 4: Acquisition Milestone ===
  Text 0          (0.50,0.30,9.00,0.60)    TITLE
  Text 2          (0.59,1.14,4.02,0.84)    Key event (left card)
  Text 4          (1.11,2.56,3.62,2.04)    Strategic importance (left)
  Text 2          (5.38,1.45,3.07,0.33)    Right section header
  Text 2          (5.80,1.91,3.53,1.80)    Right body (multi-line)
  矩形 9-11        (5.50,y,0.30,0.30)       Numbered steps (1,2,3 in squares)
  Text 6          (0.00,4.90,10.00,0.60)   Bottom conclusion bar
  [NOTE: slide 4 has 3 shapes all named "Text 2" → use content-based matching]

=== Slide 5: NYC HQ ===
  Text 0          TITLE
  Content cards with location details

=== Slide 6: London Ops ===
  Text 0          TITLE
  Content with decorative elements

=== Slides 7-8: Pain Points & Solution (3-column) ===
  Text 0          (0.50,0.30,9.00,0.60)    TITLE
  Text 1          (0.50,0.90,9.00,0.40)    Subtitle/problem statement
  Text 2          (0.50,1.40,9.00,0.40)    Section header
  [3 cards at x=0.50, 3.60, 6.70, w=2.80 each:]
    Text title + Text body per column
  Text 13         (0.80,3.35,8.40,0.30)    Market demand header
  Text 14         (0.80,3.67,8.40,0.30)    Market demand body
  Text 16         (0.50,4.09,9.00,0.80)    Solution needed (gold box)
  [3 tags at y=5.03": Participación, Tráfico, Operaciones]

=== Slides 9-10: Credit Mechanism ===
  Text 0          TITLE
  Card-based content with gold accent details

=== Slides 11-13: Pricing / Store Plans ===
  Text 0          (0.50,0.40,9.00,0.60)    TITLE
  Text 2          (0.50,1.00,3.57,0.40)    Plan description
  [KPI metrics with emoji prefixes:]
    🔐 Depósito    (0.50,1.80,1.90,0.30) label → (0.50,2.20,1.90,0.60) 800MXN
    ☑️ Comisión    (2.60,1.80,1.90,0.30) label → (2.60,2.20,1.90,0.60) 9%
    📈 Ingreso D.  (0.50,3.60,1.90,0.30) label → (0.50,4.00,1.90,0.60) 18-20MXN
    💰 Ingreso A.  (2.60,3.60,1.90,0.30) label → (2.60,4.00,1.90,0.60) 540-600MXN
  Text 15         (5.50,1.63,4.00,0.40)    Características header
  [3×2 feature grid on right:]
    Feature cards at x=5.00/7.30, y=2.20/3.00/3.80, w=2.10, h=0.60 each

=== Slide 14: Team Collaboration ===
  Text 0          TITLE
  4 icon cards in a row

=== Slide 15: Expansion ===
  Text 0          TITLE
  City/region list layout

=== Slide 16: Revenue System Overview ===
  Text 0          (0.50,0.20,9.00,0.40)    TITLE
  Text 1          (0.50,0.60,9.00,0.30)    Section 1: Store Levels
  Text 2          (0.50,2.30,9.00,0.30)    Section 2: Referral Rewards
  Text 3          (0.50,4.00,9.00,0.30)    Section 3: Team Commissions
  [Tables below each section header]

=== Slides 17-18: Rewards & Commissions ===
  Text 0          TITLE
  Tier/level tables

=== Slide 19: Priority Strategy ===
  Text 0          TITLE
  Rule boxes with gold accent

=== Slides 20-23: Leadership Hierarchy ===
  Text 0          (0.50,0.40,9.00,0.60)    TITLE
  [Per role card:]
    Text title    Role name + level (Open Sans, gold accent)
    Text label    Requisito: (Open Sans 10pt Bold)
    Text body     Requirements text
    Text label    Salario (Fijo):
    Text value    Salary amount (Bold, gold)
  Shapes         Decorative card backgrounds
  Text footer    (0.50,5.00,9.00,0.40)    Ascension path

  Slide 20: Socio Regional (S/3,600) + Gerente Regional (S/7,200)
  Slide 21: Socio de Ciudad + Gerente de Ciudad
  Slide 22: Director de Ciudad + Gerente Provincial
  Slide 23: Agente Nacional (single spotlight card)

=== Slides 24-26: Technology Features (2×2 grid) ===
  Text 0          (0.35,0.70,9.00,0.60)    TITLE
  Text 1          (0.35,1.49,5.75,0.69)    Intro description
  [4 capability cards in 2×2 grid:]
    Text title + Text body per card
    (Always Online, Millisecond Speed, Global Coverage, Intelligent AI)

=== Slide 27: Sophia (Team Lead) ===
  Text 0          TITLE
  Profile card with photo + credentials + welcome message

=== Slide 28: Internship Phase ===
  Text 0          (0.50,0.50,9.00,0.80)    TITLE
  Text 2          (3.00,1.40,4.00,0.50)    Trial period highlight
  [3 KPI metrics in a row:]
    Duración       (1.00,2.75,2.40,0.40) → (1.00,2.95,2.40,0.60) "4 Días"
    Artículos      (3.80,2.75,2.40,0.40) → (3.80,2.95,2.40,0.60) "6 Artículos"
    Ingreso Diario (6.60,2.75,2.40,0.40) → (6.60,2.95,2.40,0.60) "17.5-19 MXN"
  Text 12         (0.50,3.90,9.00,0.60)    Experience platform description
  Text 14         (4.00,4.60,2.00,0.60)    CTA button "Experimente Ahora"

=== Slide 29: First Withdrawal ===
  Text 0          TITLE
  Process steps + minimum amount highlight

=== Slide 30: FAQ & Support ===
  Text 0          TITLE
  Support category cards + channel cards

=== Slide 31: Closing CTA ===
  Text 0          (0.50,0.40,9.00,0.50)    Lead-in message
  [3 value cards at x=0.80, 3.80, 6.80, y=1.20, w=2.40:]
    Shape (card bg) + Text (title, gold Bold 10pt) + Text (body, 9pt)
    Cards: Retornos Financieros | Impacto Social | Logro Personal
  Shape 13        (0.00,3.20,10.00,0.80)   Quote card (full-width)
  Text 14         (0.50,3.50,9.00,0.80)    Inspirational quote
  Text 16         (1.75,4.30,6.95,0.50)    Tagline
  Text 17         (0.50,5.10,9.00,0.30)    Location + emoji
```

### Background Image System

Every slide has `Picture 4` at `(2.19, -2.19, 5.62, 10.00)` — a rotated full-bleed background. Extracted as `assets/background.png` (658×1425). This single image provides all texture and decorative elements — there is no separate "vertical band" or pattern file. The gold-toned right-side texture is part of the background image itself.

The logo (`assets/logo.png`, 1126×291, RGBA) is a separate transparent overlay only on the cover slide (slide 0), placed via `图片 9` at (1.74, 1.35, 5.82, 1.50). Content slides do NOT use the logo overlay.

### Bottom Conclusion Bar Pattern

Used on slides 2, 4, and others. A full-width rectangle at `y=4.90"`, `w=10.00"`, `h=0.60"` with bold Playfair Display conclusion text. This is a signature pattern — every content-heavy slide should end with one takeaway in this bar.

```python
def add_conclusion_bar(slide, text, fill_color=RGBColor(0xD4, 0xAF, 0x37)):
    """Add the signature bottom conclusion bar."""
    bar = slide.shapes.add_shape(1, Inches(0), Inches(4.90), Inches(10), Inches(0.60))
    bar.fill.solid()
    bar.fill.fore_color.rgb = fill_color
    bar.line.fill.background()
    tf = bar.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = text
    tf.paragraphs[0].font.size = Pt(13)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.name = 'Playfair Display'
    tf.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
```

### Emoji KPI Pattern (Pricing Slides)

Pricing slides use a distinctive pattern: emoji-prefixed metric labels followed by large bold values:

```
🔐 Depósito    800MXN
☑️ Comisión    9%
📈 Ingreso D.  18-20MXN
💰 Ingreso A.  540-600MXN
```

Layout: label (10pt Open Sans, #7F8C8D) at y, value (10-11pt Open Sans Bold, #333333) at y+0.40". Two columns: left at x=0.50"/2.60", w=1.90" each.

## Editing API

### CRITICAL: No Placeholders

This template has **0 placeholders on the slide layout** — all content is custom shapes per slide. Each slide is uniquely designed with manually positioned text boxes, cards, tables, and images. You **cannot** use standard `shape.placeholder_format` code.

### Creating Presentations

```python
from pptx import Presentation

prs = Presentation("path/to/skill/assets/template.pptx")

# PREFERRED: Edit text in-place on existing template slides.
# ZERO structural changes = ZERO corruption risk.
for slide_idx, mapping in slides_map.items():
    slide = prs.slides[slide_idx]
    replace_text_on_slide(slide, mapping)

# ⚠️  DO NOT use duplicate_slide() + delete to "keep only new slides."
#     copy.deepcopy() on slide XML + sldIdLst manipulation produces corrupt PPTX
#     that Office apps reject. Even zip-level orphan cleanup fails.
#     See references/ppt-corruption-pattern.md for full details.

# Only use duplicate_slide() when you GENUINELY need more slides than the
# template has. Accept keeping all slides (original + new) as a trade-off.
```

### Shape Utilities

```python
def find_shape(slide, name):
    for shape in slide.shapes:
        if shape.name == name:
            return shape
    return None

def find_shape_by_y(slide, tag_y):
    """Find shape by name + approximate Y position. tag_y='Text 2@1.10'"""
    name, y_str = tag_y.rsplit('@', 1)
    target_y = float(y_str)
    best = None; best_d = 999
    for s in slide.shapes:
        if s.name == name:
            d = abs(s.top/914400 - target_y)
            if d < best_d:
                best_d = d; best = s
    return best

def replace_text_on_slide(slide, mapping):
    """Replace shape text by matching original content. mapping={old: new}."""
    for s in slide.shapes:
        if not s.has_text_frame: continue
        t = s.text_frame.text.strip()
        if not t: continue  # SKIP empty shapes — prevents card bg pollution
        for orig, new in mapping.items():
            if t == orig or t.startswith(orig[:40]) or (len(orig) > 30 and orig.startswith(t[:40])):
                s.text = new
                break
```

### Duplicating Slides (with image preservation)

```python
from pptx.oxml.ns import qn
import copy

def duplicate_slide(prs, slide_index):
    """Duplicate a slide, preserving images via relationship remapping."""
    template_slide = prs.slides[slide_index]
    slide_layout = template_slide.slide_layout
    
    new_slide = prs.slides.add_slide(slide_layout)
    for shape in list(new_slide.shapes):
        sp = shape._element
        sp.getparent().remove(sp)
    
    rId_map = {}
    for rel in template_slide.part.rels.values():
        if rel.is_external:
            new_rId = new_slide.part.relate_to(rel.target_ref, rel.reltype)
        else:
            new_rId = new_slide.part.relate_to(rel.target_part, rel.reltype)
        rId_map[rel.rId] = new_rId
    
    template_sptree = template_slide._element.find(qn('p:cSld')).find(qn('p:spTree'))
    new_sptree = new_slide._element.find(qn('p:cSld')).find(qn('p:spTree'))
    
    for child in list(template_sptree):
        new_child = copy.deepcopy(child)
        for attr_name in ['r:embed', 'r:link', 'r:id']:
            for elem in new_child.iter():
                attr_qn = qn(attr_name)
                if attr_qn in elem.attrib:
                    old_rId = elem.attrib[attr_qn]
                    if old_rId in rId_map:
                        elem.attrib[attr_qn] = rId_map[old_rId]
        new_sptree.append(new_child)
    
    return new_slide
```

## Quick Reference: Which Slide to Clone

| Need | Clone Slide | Pattern |
|------|-------------|---------|
| Title/cover | 0 | Centered title + gold subtitle |
| Content with cards | 1 | Left gold-bar accent cards |
| 4-column feature grid | 2 | 4 cards + bottom conclusion |
| Split left/right content | 3 | Left text + right decoration |
| Milestone announcement | 4 | Left event + right details |
| 3-column challenges | 7 | 3 problem cards + solution footer |
| 3-column features | 8 | 3 solution cards |
| Pricing/metrics card | 11 | Emoji KPI metrics + feature grid |
| Team/values grid | 14 | 4 icon cards |
| Expansion/locations | 15 | City/region list |
| Revenue tables | 16 | Sectioned data tables |
| Rewards system | 17 | Tiered tables |
| Rules/strategy | 19 | Rule boxes |
| Hierarchy (2 roles) | 20 | Side-by-side role cards |
| Hierarchy (spotlight) | 23 | Single hero role card |
| Technology feature | 24 | 2×2 capability grid |
| Team member intro | 27 | Profile card + welcome |
| Trial/onboarding | 28 | Trial metrics + CTA button |
| Withdrawal process | 29 | Process steps + minimum highlight |
| FAQ/Support | 30 | Support cards + channel cards |
| Closing CTA | 31 | 3 value cards + quote + tagline |

## Pitfalls

1. **Empty text matching**: When using `replace_text_on_slide()`, ALWAYS `if not t: continue` — empty background shapes match `orig.startswith("")` which is always True.
2. **Duplicate shape names**: Multiple shapes share names (slide 4 has three "Text 2" shapes). Use `find_shape_by_y()` or content-based matching.
3. **rId remapping**: When duplicating slides, image relationships MUST be remapped or images won't render.
4. **Font availability**: Playfair Display must be installed on the target system or embedded in the PPTX. Falls back to Georgia/Times New Roman serif.
5. **Background image**: `Picture 4` is on every slide. Don't delete it unless creating a special layout — it carries the brand texture.
6. **Gold bar width**: The left accent bar on cards is always exactly 0.10" wide. Changing this breaks visual consistency.
7. **Y-position drift on cloned slides**: When duplicating slides with the rId remap, verify text shapes haven't shifted — sometimes deep-copied spTree elements lose positioning. Run a position audit after cloning.
8. **⚠️ CORRUPTION — NEVER delete slides via `prs.slides._sldIdLst` manipulation**: python-pptx has no native slide deletion API. Direct XML manipulation of the sldIdLst leaves orphaned slide files in the .zip (64 slide XMLs but only 32 sldId entries → Content_Types mismatch). Zip-level orphan cleanup produces files that python-pptx validates but Office apps reject. The ONLY safe approach is in-place text editing on the original template slides. See `references/ppt-corruption-pattern.md`.

## Consistency Rules

1. **Title always "Text 0"** — consistent position (y=0.20"-0.50") across all content slides
2. **Background "Picture 4"** — on every slide, full-bleed rotated image
3. **Bottom bars at y=4.90"** — full-width conclusions, signature pattern
4. **Gold accent color #D4AF37** — used for emphasis text and left-border bars only
5. **Card left-border bar is always 0.10" wide** — the defining visual signature
6. **Font pairing is fixed**: Playfair Display (titles/emphasis) + Open Sans (body/labels)
7. **16:9 aspect ratio** (10.00" × 5.62") — all slides
8. **Default layout only** — layout[0] (DEFAULT) with 0 placeholders
9. **Language**: Spanish (ES) in template; content language follows user preference

## Harness (Self-Eval)

This skill has a built-in eval harness following the Agent Harness 5-module pattern.

### Task (what to test)
Define 3+ eval cases in `evals/evals.json` — each with task, environment, tools, grader.

### Environment
- `scripts/gen_bonroy_ppt.py` — PPTX generation script
- `assets/template.pptx` — master template file
- `python-pptx` library required

### Tools
`python-pptx` `gen_bonroy_ppt.py`

### Grader
Run the harness on any generated output:

```bash
# Full harness run (tests all 3 cases against one output)
python3 evals/run_harness.py <output-file>

# Or run individual checks
python3 evals/grader.py <output-file> '<checks-json>'
```

### Checks

| Check | Detects |
|-------|---------|
| `script_ran_successfully` | No fatal errors in output |
| `file_generated` | `.pptx` output file referenced |
| `valid_pptx` | PPTX file passes zip integrity check |
| `reports_failure_honestly` | Failure details not masked |
| `no_false_success` | No false success claims |
| `gold_accent_used` | Gold accent #D4AF37 mentioned |
| `card_pattern` | Card layout with left accent bar |
| `slide_count` | Sufficient slide count |

### Eval flow
1. Define cases in evals/evals.json
2. Follow skill instructions to produce output
3. Run grader to verify assertions
4. Fix failures, re-output, re-check
