# Customization Worked Example

User says: "Clone this but change primary color to blue (#3B82F6)."

1. Extract all colors via getComputedStyle(). Map to CSS variables:
```css
:root {
  --color-primary: #FF5733;
  --color-primary-foreground: #FFFFFF;
  --color-accent: #FF8C00;
}
```

2. Create override block below the original:
```css
:root {
  --color-primary: #3B82F6;
  --color-primary-hover: #2563EB;
}
```

3. In each spec file's Implementation Notes: "primary color: #FF5733 → #3B82F6"

4. In builder prompts: "Use bg-[var(--color-primary)] not bg-[#FF5733]"

5. For icons.tsx: replace hardcoded `fill="#FF5733"` with `fill="var(--color-primary)"`
