---
name: stock-analysis-runner
description: Use this skill when the user wants Codex to analyze a stock with the local MarketForge website data, refresh only the required symbol data, generate a trade thesis, run bull/bear analysis, check buy/sell timing rules, audit data quality, or produce a structured stock-analysis markdown report.
---

# Stock Analysis Runner

## Purpose

Generate a focused stock-analysis report from the local MarketForge API while updating only the data the website needs.

This skill is for research support. Do not present the output as guaranteed investment advice, a promise of profit, or a direct order to buy or sell.

## Default Workflow

1. Identify the target symbol and normalize it to uppercase, for example `688981.SH`, `600519.SH`, `NVDA`, or `00700.HK`.
2. Check the MarketForge backend first with `/api/system/status`.
3. Fetch targeted single-symbol data and related context:
   - watchlist membership
   - candles and technical assessment
   - trade plan
   - screener candidate state
   - portfolio ledger and operation records
   - review board and review briefing
   - risk center, news, rules, and data-source health
4. Refresh only the symbol candles when the user asks for updated data or the analysis needs fresh candles. Use `--refresh`.
5. Avoid broad refresh unless the user explicitly asks for full market refresh. Use `--full-refresh` only then.
6. Write the markdown report to `analysis_out/` unless the user gives another path.

## Run The Bundled Script

Use the script instead of manually calling every endpoint:

```bash
python /Users/f/.codex/skills/stock-analysis-runner/scripts/run_stock_analysis.py 688981.SH --refresh
```

Use a custom backend URL:

```bash
MARKETFORGE_API_URL=http://localhost:8000 python /Users/f/.codex/skills/stock-analysis-runner/scripts/run_stock_analysis.py NVDA --output analysis_out/NVDA-analysis.md
```

Save raw API evidence next to the report:

```bash
python /Users/f/.codex/skills/stock-analysis-runner/scripts/run_stock_analysis.py 600519.SH --raw-json
```

Write the trade-plan journal draft only when explicitly requested:

```bash
python /Users/f/.codex/skills/stock-analysis-runner/scripts/run_stock_analysis.py 688981.SH --write-journal
```

## Output Requirements

A good report should include:

- Executive snapshot.
- Data source, freshness, fallback, and endpoint error warnings.
- Current trend and timing assessment.
- Trade plan, entry rules, exit rules, invalidation rules, and checklist.
- Bull case and bear case.
- Position and operation review.
- Rule-execution/deviation attribution when operation records exist.
- Risk alerts, latest news snapshot, and next website data actions.

## Guardrails

- If the backend is offline, say that clearly and do not invent data.
- If the symbol is not in the watchlist, report that the website may not update normally until it is added.
- If `fallback` is true, lower confidence and call out the limitation.
- If data is stale, single-source, or missing, make the report about what is known and what must be refreshed.
- Do not POST to `/api/journal` unless the user explicitly asked to write a journal entry or passed `--write-journal`.
- Do not run `/api/market/refresh/full` unless the user explicitly asked for broad/full refresh.

## Reference

Read `references/marketforge-api.md` only when extending the script or debugging endpoint behavior.
