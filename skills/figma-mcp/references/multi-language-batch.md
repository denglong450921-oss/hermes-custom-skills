# Multi-Language Batch Translation & Export

## Clone-Family Recognition

Cloned templates follow a naming pattern:
```
Original:    1, 2, 3           (English templates)
             M1, M2, M3        (English M-series variants)

Spanish:     4xiban, 5xiban, 6xiban    (direct translations)
             M1spanish, M2spanish, M3spanish

Arabic:      7abaric, 8abaric, 9abaric
             M1abaric, M2abaric, M3abaric

French:      10French, 11French, 12French
             M1French, M2French, M3Franch

Portuguese:  13pt, 14pt, 15pt
             M1pt, M2pt, M3pt
```

## Translation Strategy

1. **Identify the clone family**: each numbered page maps to the same template
2. **Use consistent translations**: same term across all clones of the same language
3. **Reuse text styles**: styles created for one page work on all clones — don't recreate
4. **Font thresholds are language-specific, not page-specific**: Spanish 4xiban heading = same adjustment as M1spanish heading

## Batch Export

When user wants all pages exported:

```
# Create organized directory
mkdir -p all_pngs/{originals,spanish,arabic,french,portuguese}

# Export in batches of 10 (save_screenshots limit)
# Then zip:
cd all_pngs && zip -r ../all_pngs.zip .
```

## Common Font Adjustments (by font family)

| Font | Original | Spanish | French | Portuguese | Arabic |
|------|----------|---------|--------|------------|--------|
| Inknut Antiqua | 40px | 32px | 34px | 34px | 40px (fits) |
| Holtwood One SC | 60px | 48px | 48px | 48px | 60px (fits) |
| Inder | 50px | 34px | 34px | 34px | 50px (fits) |
| DIN Alternate | 80px | 80px (condensed) | 48px | 48px | 80px (fits) |
| Inter (col headers) | 32px | 22px | 22px | 22px | 32px (fits) |
| Inter (description) | 35px | 26px | 26px | 26px | 35px (fits) |
| Inter (body) | 24px | 18-20px | 18-20px | 18-20px | 24px (fits) |

## Non-Template / Custom Font Families

Many Figma frames use fonts NOT in the template table above (Montagu Slab, Montserrat, Poppins, Inria Serif, etc.). For these, you cannot rely on a pre-computed reduction table. Use the **parent-container bounds check** instead (see main SKILL.md "General overflow detection").

### Empirical Portuguese thresholds (commission-table group: 4 frames × 1086px wide)

| Font + Style | Original Size | Portuguese Overflow | Adjusted Size |
|---|---|---|---|
| Montagu Slab Bold (heading) | 45px | Fits single-line (lineH 32px, text bottom < container) | Keep 45px |
| Montserrat Bold (col header) | 24px | YES — 96px tall in 97px sub-header bg, extends 14px below | 20px (56px fits) |
| Montserrat Bold (section labels) | 26px | Fits single-line | Keep 26px |
| Poppins SemiBold (descriptions) | 25px | 46px (2 lines @ 23px lineH), fits 374px-wide container | Keep 25px |

**Key takeaway:** Montserrat Bold is the overflow-prone font for Portuguese — the words "Porcentagem", "Número", "Tamanho" are wider than their English counterparts, often pushing text to 3+ wrapped lines at 24px. Reduce to 20px (lineH 28px) when wrapping exceeds 2 lines.

## Group-of-Frames Structure (Non-Cloned)

Sometimes the "PTGroup" or "ESGroup" is not a clone family but a GROUP node with 4+ heterogeneous frames inside. Recognition — it looks like:

```
PTGroup 1321316058          (GROUP)
├── Frame "5"               (Affiliate Referral Commissions table)
├── Frame "6"               (Daily Team Performance Bonuses)
├── Frame "7"               (Promotional Monthly Base Salary)
└── Frame "8"               (duplicate of frame "5")
```

Each frame has its own background rectangles, column headers, and table data. Unlike cloned templates where font adjustments are uniform, each frame may need independent evaluation. Use `get_design_context(depth=2)` to see the full structure in one shot before translating.

## Common Translations (English → Portuguese)

For commission/reward table structures:

| English | Portuguese | Preserved Content |
|---------|-----------|-------------------|
| Affiliate Referral Commissions | Comissões de Indicação de Afiliados | Full commission name |
| Daily Team Performance Bonuses | Bônus de Desempenho da Equipe Diário | "Daily" included |
| Promotional Monthly Base Salary | Salário Base Mensal Promocional | "Promotional" included |
| level | nível | — |
| Bonus percentage | Porcentagem de Bônus | Full; requires font reduction in 149px cols |
| Daily income | Renda Diária | — |
| Team size | Tamanho da Equipe | — |
| Monthly salary | Salário Mensal | — |
| Company / Position | Cargo na / Empresa | Multi-line preserved |
| margin | margem | — |
| Number of tasks | Número de Tarefas | — |
| unit / price | preço / unitário | Multi-line preserved |
| Monthly / income | Renda / Mensal | Multi-line preserved |
| Annual / income | Renda / Anual | Multi-line preserved |
| Grade A/B/C | Grau A/B/C | Keeps letter suffix |
| Intern | Estagiário | — |
| Intern Assistant | Assistente Estagiário | — |
| Official Assistant | Assistente Oficial | — |
| Junior Supervisor | Supervisor Júnior | — |
| Head of Marketing | Chefe de Marketing | — |
| Junior Manager | Gerente Júnior | — |
| Marketing Director | Diretor de Marketing | — |
| Shareholder Partners | Sócios Acionistas | — |
| A team of X people with Y A-level members. | Uma equipe de X pessoas com Y membros de nível A. | Numbers preserved exactly; about 2× longer than English, still fits in 374px × 46px at Poppins 25px |
