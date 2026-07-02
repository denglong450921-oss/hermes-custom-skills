# MarketForge API Reference For Stock Analysis Runner

Use this reference only when extending the runner or debugging API coverage.

## Base URL

Default base URL:

```bash
http://localhost:8000
```

Override with:

```bash
MARKETFORGE_API_URL=http://localhost:8000
```

The runner accepts both `http://localhost:8000` and `http://localhost:8000/api`.

## Single-Symbol Workflow

For normal analysis, do a targeted workflow:

1. `GET /api/system/status`
2. `GET /api/market/provider/status`
3. `GET /api/watchlist`
4. Optional targeted refresh: `POST /api/market/candles/{symbol}/refresh?period=daily&limit=120`
5. `GET /api/market/candles/{symbol}?period=daily&limit=120`
6. `GET /api/trade-plan/{symbol}`
7. `GET /api/screener?limit=100`
8. `GET /api/reviews`
9. `GET /api/reviews/briefing`
10. `GET /api/portfolio/ledger`
11. `GET /api/risk/early-warning`
12. `GET /api/news`
13. `GET /api/rules`
14. `GET /api/data-sources`

Do not run `POST /api/market/refresh/full` for a single stock unless the user explicitly asks for broad market refresh.

## Data Quality Rules

Always surface:

- API health and provider state.
- Candle `freshness.source`, `data_time`, `fetched_at`, `quality_grade`, `verification`, and `layer`.
- `fallback: true` warnings.
- Endpoint errors.
- Missing watchlist membership.

When data is fallback, stale, missing, or from a limited provider, lower confidence and avoid executable buy/sell wording.

## Mutating Operations

The runner can modify app data only when explicitly requested:

- `--refresh` calls the targeted candle refresh endpoint for one symbol.
- `--full-refresh` calls the broad refresh pipeline.
- `--write-journal` posts the trade-plan journal draft to `POST /api/journal`.

Without those flags, the runner should behave as a read-only analysis tool.

## Report Expectations

A useful report includes:

- Executive snapshot.
- Data quality and fallback warnings.
- Trade plan, checklist, entry/exit/invalidation rules.
- Technical evidence.
- Bull and bear cases.
- Portfolio positions and operation records.
- Rule execution review and deviation attribution.
- Risk alerts and news snapshot.
- Next website data actions.

The report is research support. It must not promise gains, guaranteed signals, or direct personalized financial advice.
