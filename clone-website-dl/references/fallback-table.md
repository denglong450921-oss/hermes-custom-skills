# Fallback Decision Table

When something goes wrong, find your scenario:

| Trigger Condition | First-Line Fix | Escalation |
|---|---|---|
| Browser MCP fails to navigate | Check URL accessibility via curl; if blocked, ask user for VPN | Try Firecrawl scrape fallback; if also fails, abort |
| getComputedStyle() returns defaults | Page likely JS not executed. Wait 3s, re-run extraction | Switch to manual extraction: ask user to provide CSS |
| Asset download fails (404/CORS) | For icons: inline SVG data URI fallback. For photos: Unsplash placeholder | Ask user to provide critical assets manually |
| Builder returns compile errors | Check spec for missing imports, "use client", export style | Fix errors manually, re-run npx tsc --noEmit |
| Git worktree merge conflicts | Keep more complete version | Revert and re-dispatch with stricter boundaries |
| Visual QA finds discrepancies | Check spec first — was value extracted correctly? | If spec correct but builder deviated, fix component |
| User wants partial clone | Extract section CSS, write single spec, dispatch one builder | Skip Phase 4 assembly |
| User wants custom colors | Extract original to CSS vars, create --color-override block | For images containing brand colors, note "needs manual edit" |
| User wants layout changes | Document new layout in "Implementation Notes" | Adjust container grid/flex in component code |
| User wants content substitution | Put original in comments, replace with user's content | Ask user to provide replacement text in a document |
