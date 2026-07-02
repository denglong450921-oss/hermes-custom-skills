#!/usr/bin/env python3
"""Generate a MarketForge stock-analysis report from local API data."""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_API_URL = os.environ.get("MARKETFORGE_API_URL", "http://localhost:8000")


class ApiError(RuntimeError):
    def __init__(self, method: str, url: str, message: str) -> None:
        super().__init__(f"{method} {url}: {message}")
        self.method = method
        self.url = url
        self.message = message


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def safe_filename(symbol: str) -> str:
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    return "".join(char if char in allowed else "_" for char in symbol.upper())


def make_url(api_url: str, endpoint: str, params: dict[str, Any] | None = None) -> str:
    base = api_url.rstrip("/")
    path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
    if base.endswith("/api") and path.startswith("/api/"):
        path = path[4:]
    url = f"{base}{path}"
    if params:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if query:
            url = f"{url}?{query}"
    return url


def request_json(
    api_url: str,
    method: str,
    endpoint: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    timeout: int = 20,
) -> Any:
    url = make_url(api_url, endpoint, params)
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise ApiError(method, url, f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ApiError(method, url, str(exc.reason)) from exc
    except TimeoutError as exc:
        raise ApiError(method, url, "request timed out") from exc

    if not payload:
        return None
    try:
        return json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ApiError(method, url, f"invalid JSON: {exc}") from exc


def call(
    bundle: dict[str, Any],
    key: str,
    method: str,
    endpoint: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> Any:
    try:
        data = request_json(bundle["api_url"], method, endpoint, params=params, body=body)
    except ApiError as exc:
        bundle["errors"].append({"key": key, "error": str(exc)})
        bundle[key] = None
        return None
    bundle[key] = data
    return data


def listify(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def dictify(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def get_path(value: Any, *path: str, default: Any = None) -> Any:
    current = value
    for part in path:
        if not isinstance(current, dict):
            return default
        current = current.get(part)
    return default if current is None else current


def fmt_value(value: Any, suffix: str = "") -> str:
    if value is None or value == "":
        return "n/a"
    return f"{value}{suffix}"


def fmt_pct(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return str(value)


def bullet(items: list[Any], limit: int = 8) -> list[str]:
    output: list[str] = []
    for item in items[:limit]:
        if isinstance(item, dict):
            text = item.get("summary") or item.get("note") or item.get("title") or json.dumps(item, ensure_ascii=False)
        else:
            text = str(item)
        output.append(f"- {text}")
    return output or ["- n/a"]


def find_symbol(items: list[Any], symbol: str) -> dict[str, Any] | None:
    for item in items:
        if isinstance(item, dict) and str(item.get("symbol", "")).upper() == symbol:
            return item
    return None


def select_symbol_items(items: list[Any], symbol: str) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, dict) and str(item.get("symbol", "")).upper() == symbol:
            selected.append(item)
    return selected


def select_symbol_operations(ledger: dict[str, Any], symbol: str) -> list[dict[str, Any]]:
    operations = listify(ledger.get("operations"))
    return select_symbol_items(operations, symbol)


def select_symbol_positions(ledger: dict[str, Any], symbol: str) -> list[dict[str, Any]]:
    positions = listify(ledger.get("positions"))
    return select_symbol_items(positions, symbol)


def latest_candle(candles: dict[str, Any]) -> dict[str, Any]:
    points = listify(candles.get("candles"))
    return dictify(points[-1]) if points else {}


def endpoint_status(bundle: dict[str, Any]) -> list[str]:
    rows = []
    for key in [
        "system_status",
        "provider_status",
        "watchlist",
        "candles",
        "trade_plan",
        "screener",
        "reviews",
        "review_briefing",
        "ledger",
        "risk",
        "news",
        "rules",
        "data_sources",
    ]:
        state = "ok" if bundle.get(key) is not None else "missing"
        rows.append(f"- `{key}`: {state}")
    return rows


def summarize_data_quality(bundle: dict[str, Any]) -> list[str]:
    candles = dictify(bundle.get("candles"))
    freshness = dictify(candles.get("freshness"))
    provider = dictify(bundle.get("provider_status"))
    system_status = dictify(bundle.get("system_status"))
    backend_status = get_path(system_status, "backend", "status") or get_path(system_status, "backend", "detail")
    rows = [
        f"- API URL: `{bundle['api_url']}`",
        f"- System state: {fmt_value(system_status.get('state') or system_status.get('status') or backend_status)}",
        f"- Provider: {fmt_value(provider.get('provider') or provider.get('name'))}",
        f"- Candle source: {fmt_value(freshness.get('source'))}",
        f"- Data time: {fmt_value(freshness.get('data_time'))}",
        f"- Fetched at: {fmt_value(freshness.get('fetched_at'))}",
        f"- Quality: {fmt_value(freshness.get('quality_grade'))} / {fmt_value(freshness.get('verification'))} / {fmt_value(freshness.get('layer'))}",
        f"- Fallback candles: {fmt_value(candles.get('fallback'))}",
    ]
    errors = bundle.get("errors") or []
    if errors:
        rows.append("- Endpoint errors:")
        rows.extend(f"  - {item['key']}: {item['error']}" for item in errors[:8])
    return rows


def build_bull_bear(bundle: dict[str, Any], symbol: str) -> tuple[list[str], list[str]]:
    trade_plan = dictify(bundle.get("trade_plan"))
    candles = dictify(bundle.get("candles"))
    candidate = dictify(trade_plan.get("candidate")) or dictify(find_symbol(listify(get_path(bundle, "screener", "candidates", default=[])), symbol))
    assessment = dictify(candles.get("assessment"))
    risk = dictify(bundle.get("risk"))

    bull: list[str] = []
    bear: list[str] = []

    if trade_plan.get("executable"):
        bull.append(f"Trade plan is executable with status `{trade_plan.get('status')}`.")
    else:
        bear.append(f"Trade plan is not executable or missing; status `{fmt_value(trade_plan.get('status'))}`.")

    if candidate:
        if candidate.get("allowed_to_buy"):
            bull.append(f"Screener allows buying, rank {fmt_value(candidate.get('rank'))}, total score {fmt_value(candidate.get('total_score'))}.")
        else:
            bear.append(f"Screener does not allow buying; decision `{fmt_value(candidate.get('decision'))}`.")
        bull.extend(str(x) for x in listify(candidate.get("passed_rules"))[:3])
        bear.extend(str(x) for x in listify(candidate.get("blocked_rules"))[:4])

    if assessment:
        trend_label = assessment.get("trend_label")
        action_bias = assessment.get("action_bias")
        if action_bias in {"允许试仓", "等待突破"} or trend_label in {"多头趋势", "转强观察"}:
            bull.append(f"Technical bias: {fmt_value(trend_label)} / {fmt_value(action_bias)}.")
        else:
            bear.append(f"Technical bias: {fmt_value(trend_label)} / {fmt_value(action_bias)}.")
        bear.extend(str(x) for x in listify(assessment.get("risk_notes"))[:3])

    if candles.get("fallback"):
        bear.append("Candle data is fallback; confidence must be reduced.")

    risk_status = risk.get("status")
    if risk_status in {"橙色", "红色"}:
        bear.append(f"Risk center status is {risk_status}.")
    elif risk_status:
        bull.append(f"Risk center status is {risk_status}.")

    if not bull:
        bull.append("No strong bullish evidence was found in the current local dataset.")
    if not bear:
        bear.append("No blocking bearish evidence was found, but this is not a buy recommendation.")
    return [f"- {item}" for item in bull[:8]], [f"- {item}" for item in bear[:8]]


def build_report(bundle: dict[str, Any], symbol: str, args: argparse.Namespace) -> str:
    stock = dictify(bundle.get("stock"))
    candles = dictify(bundle.get("candles"))
    trade_plan = dictify(bundle.get("trade_plan"))
    candidate = dictify(trade_plan.get("candidate")) or dictify(find_symbol(listify(get_path(bundle, "screener", "candidates", default=[])), symbol))
    assessment = dictify(candles.get("assessment"))
    ledger = dictify(bundle.get("ledger"))
    reviews = dictify(bundle.get("reviews"))
    briefing = dictify(bundle.get("review_briefing"))
    risk = dictify(bundle.get("risk"))
    latest = latest_candle(candles)
    operations = select_symbol_operations(ledger, symbol)
    positions = select_symbol_positions(ledger, symbol)
    review_items = select_symbol_items(listify(reviews.get("operation_items")), symbol)
    bull, bear = build_bull_bear(bundle, symbol)

    title_name = stock.get("name") or trade_plan.get("name") or candles.get("name") or symbol
    generated_at = now_utc()
    refresh_note = "targeted refresh requested" if args.refresh else "read-only fetch"
    if args.full_refresh:
        refresh_note = f"{refresh_note}; full refresh requested"

    lines: list[str] = [
        f"# Stock Analysis: {symbol} {title_name}",
        "",
        f"- Generated at: {generated_at}",
        f"- Mode: {refresh_note}",
        f"- Period / limit: {args.period} / {args.limit}",
        f"- Research boundary: This report is decision support, not guaranteed investment advice.",
        "",
        "## Executive Snapshot",
        "",
        f"- Market: {fmt_value(stock.get('market') or trade_plan.get('market') or candles.get('market'))}",
        f"- Last close: {fmt_value(latest.get('close'))}",
        f"- Current price: {fmt_value(trade_plan.get('current_price') or stock.get('price'))}",
        f"- Trade plan status: {fmt_value(trade_plan.get('status'))}; executable: {fmt_value(trade_plan.get('executable'))}",
        f"- Screener decision: {fmt_value(candidate.get('decision'))}; allowed to buy: {fmt_value(candidate.get('allowed_to_buy'))}",
        f"- Timing: {fmt_value(assessment.get('trend_label'))} / {fmt_value(assessment.get('action_bias'))} / score {fmt_value(assessment.get('timing_score'))}",
        f"- Risk center: {fmt_value(risk.get('status'))} - {fmt_value(risk.get('status_note'))}",
        f"- Review briefing: {fmt_value(briefing.get('decision'))}; confidence {fmt_value(briefing.get('confidence_score'))}",
        "",
        "## Data Quality",
        "",
        *summarize_data_quality(bundle),
        "",
        "## Trade Plan",
        "",
        f"- Entry trigger: {fmt_value(trade_plan.get('entry_trigger'))}",
        f"- Stop loss: {fmt_value(trade_plan.get('stop_loss'))}",
        f"- Take profit: {fmt_value(trade_plan.get('take_profit'))}",
        f"- Risk reward: {fmt_value(trade_plan.get('risk_reward'))}",
        f"- Initial position: {fmt_pct(trade_plan.get('initial_position_pct'))}; max position: {fmt_pct(trade_plan.get('max_position_pct'))}; risk budget: {fmt_pct(trade_plan.get('risk_budget_pct'))}",
        f"- Position note: {fmt_value(trade_plan.get('position_note'))}",
        "",
        "### Checklist",
        "",
    ]

    checklist = listify(trade_plan.get("checklist"))
    if checklist:
        lines.extend(
            f"- [{'x' if item.get('passed') else ' '}] {fmt_value(item.get('item'))} ({fmt_value(item.get('severity'))}): {fmt_value(item.get('note'))}"
            for item in checklist[:12]
            if isinstance(item, dict)
        )
    else:
        lines.append("- n/a")

    lines.extend(
        [
            "",
            "### Entry Rules",
            "",
            *bullet(listify(trade_plan.get("entry_rules")) or listify(assessment.get("entry_rules"))),
            "",
            "### Exit And Invalidation",
            "",
            *bullet(listify(trade_plan.get("exit_rules")) + listify(trade_plan.get("invalidation_rules"))),
            "",
            "## Technical Evidence",
            "",
            f"- Summary: {fmt_value(assessment.get('summary'))}",
            "",
            *bullet(listify(assessment.get("evidence"))),
            "",
            "## Bull Case",
            "",
            *bull,
            "",
            "## Bear Case / Invalidation",
            "",
            *bear,
            "",
            "## Portfolio And Operation Review",
            "",
            f"- Total operations: {fmt_value(ledger.get('operation_count'))}; symbol operations: {len(operations)}; symbol positions: {len(positions)}",
        ]
    )

    if positions:
        lines.append("")
        lines.append("### Current Positions")
        lines.append("")
        for position in positions[:5]:
            lines.append(
                "- Qty {quantity}, avg cost {average_cost}, market value {market_value}, total PnL {total_pnl}, unrealized {unrealized_pct}".format(
                    quantity=fmt_value(position.get("quantity")),
                    average_cost=fmt_value(position.get("average_cost")),
                    market_value=fmt_value(position.get("market_value")),
                    total_pnl=fmt_value(position.get("total_pnl")),
                    unrealized_pct=fmt_value(position.get("unrealized_pct")),
                )
            )

    if operations:
        lines.append("")
        lines.append("### Recent Operations")
        lines.append("")
        for operation in operations[-8:]:
            lines.append(
                f"- {fmt_value(operation.get('occurred_at'))}: {fmt_value(operation.get('action'))} "
                f"{fmt_value(operation.get('quantity'))} @ {fmt_value(operation.get('price'))}; "
                f"strategy `{fmt_value(operation.get('strategy'))}`, emotion `{fmt_value(operation.get('emotion'))}`"
            )

    if review_items:
        lines.append("")
        lines.append("### Rule Execution Review")
        lines.append("")
        for item in review_items[:8]:
            attributions = ", ".join(
                f"{attr.get('dimension')}:{attr.get('level')}/{attr.get('score')}"
                for attr in listify(item.get("attributions"))
                if isinstance(attr, dict)
            )
            lines.append(
                f"- {fmt_value(item.get('action'))} {fmt_value(item.get('occurred_at'))}: "
                f"rule {fmt_value(item.get('rule_adherence_score'))}, timing {fmt_value(item.get('timing_score'))}, "
                f"position {fmt_value(item.get('position_score'))}, emotion risk {fmt_value(item.get('emotion_risk_score'))}, "
                f"data {fmt_value(item.get('data_quality_score'))}. {fmt_value(item.get('summary'))}"
            )
            if attributions:
                lines.append(f"  - Attribution: {attributions}")
    else:
        lines.append("- No operation review item for this symbol yet.")

    lines.extend(
        [
            "",
            "## Review Briefing",
            "",
            f"- Headline: {fmt_value(briefing.get('headline'))}",
            f"- Mode: {fmt_value(briefing.get('mode'))}; AI configured: {fmt_value(briefing.get('ai_configured'))}",
            "",
        ]
    )
    for finding in listify(briefing.get("findings"))[:6]:
        if isinstance(finding, dict):
            lines.append(
                f"- {fmt_value(finding.get('title'))} [{fmt_value(finding.get('focus'))}/{fmt_value(finding.get('severity'))}]: "
                f"{fmt_value(finding.get('summary'))} Recommendation: {fmt_value(finding.get('recommendation'))}"
            )
    if not listify(briefing.get("findings")):
        lines.append("- n/a")

    lines.extend(
        [
            "",
            "## Risk And Events",
            "",
        ]
    )
    alerts = listify(risk.get("alerts"))
    if alerts:
        for alert in alerts[:8]:
            if isinstance(alert, dict):
                lines.append(
                    f"- {fmt_value(alert.get('level'))} {fmt_value(alert.get('category'))}: "
                    f"{fmt_value(alert.get('title'))}. Mitigation: {fmt_value(alert.get('mitigation'))}"
                )
    else:
        lines.append("- No risk alerts returned.")

    news = listify(bundle.get("news"))
    lines.extend(["", "## Latest News Snapshot", ""])
    if news:
        for item in news[:8]:
            if isinstance(item, dict):
                lines.append(
                    f"- {fmt_value(item.get('published_at'))}: {fmt_value(item.get('title'))} "
                    f"[{fmt_value(item.get('impact'))}/{fmt_value(item.get('credibility'))}] {fmt_value(item.get('summary'))}"
                )
    else:
        lines.append("- No news endpoint data returned.")

    lines.extend(
        [
            "",
            "## Next Website Data Actions",
            "",
        ]
    )
    if not stock:
        lines.append("- Add this symbol to the watchlist before expecting normal website panels to update.")
    if candles.get("fallback"):
        lines.append("- Refresh or improve the market provider for this symbol; current candle data is fallback.")
    if args.refresh:
        lines.append("- Targeted candle refresh was requested for this symbol.")
    else:
        lines.append("- Re-run with `--refresh` when you need a targeted candle update.")
    lines.append("- Use `--full-refresh` only for a broad market refresh; it is intentionally separate from single-stock analysis.")
    if not operations:
        lines.append("- Add operation records for this symbol if you want rule-adherence and deviation attribution.")
    if not briefing.get("ai_configured"):
        lines.append("- Configure DeepSeek later if you want an AI-written review layer; keep source facts in this report.")

    lines.extend(["", "## Endpoint Status", "", *endpoint_status(bundle), ""])
    return "\n".join(lines)


def write_json_snapshot(path: Path, bundle: dict[str, Any]) -> Path:
    raw_path = path.with_suffix(".raw.json")
    raw_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return raw_path


def maybe_write_journal(bundle: dict[str, Any]) -> None:
    trade_plan = dictify(bundle.get("trade_plan"))
    draft = dictify(trade_plan.get("journal_draft"))
    if not draft:
        bundle["journal_write"] = {"ok": False, "message": "trade plan did not include journal_draft"}
        return
    created = call(bundle, "journal_write", "POST", "/api/journal", body=draft)
    bundle["journal_write"] = {"ok": created is not None, "created": created}


def collect_data(args: argparse.Namespace) -> dict[str, Any]:
    symbol = normalize_symbol(args.symbol)
    bundle: dict[str, Any] = {
        "symbol": symbol,
        "api_url": args.api_url,
        "generated_at": now_utc(),
        "errors": [],
        "refreshes": [],
    }

    call(bundle, "system_status", "GET", "/api/system/status")
    call(bundle, "provider_status", "GET", "/api/market/provider/status")
    call(bundle, "watchlist", "GET", "/api/watchlist")
    stock = find_symbol(listify(bundle.get("watchlist")), symbol)
    bundle["stock"] = stock

    if args.full_refresh:
        refresh = call(bundle, "full_refresh", "POST", "/api/market/refresh/full")
        bundle["refreshes"].append({"scope": "full", "result": refresh})

    if args.refresh:
        refresh = call(
            bundle,
            "targeted_candle_refresh",
            "POST",
            f"/api/market/candles/{urllib.parse.quote(symbol)}/refresh",
            params={"period": args.period, "limit": args.limit},
        )
        bundle["refreshes"].append({"scope": "candles", "symbol": symbol, "result": refresh})

    call(
        bundle,
        "candles",
        "GET",
        f"/api/market/candles/{urllib.parse.quote(symbol)}",
        params={"period": args.period, "limit": args.limit},
    )
    call(bundle, "trade_plan", "GET", f"/api/trade-plan/{urllib.parse.quote(symbol)}")
    call(bundle, "screener", "GET", "/api/screener", params={"limit": 100})
    call(bundle, "reviews", "GET", "/api/reviews")
    call(bundle, "review_briefing", "GET", "/api/reviews/briefing")
    call(bundle, "ledger", "GET", "/api/portfolio/ledger")
    call(bundle, "risk", "GET", "/api/risk/early-warning")
    call(bundle, "news", "GET", "/api/news")
    call(bundle, "rules", "GET", "/api/rules")
    call(bundle, "data_sources", "GET", "/api/data-sources")

    if args.write_journal:
        maybe_write_journal(bundle)

    return bundle


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a targeted stock analysis report from a local MarketForge backend."
    )
    parser.add_argument("symbol", help="Symbol to analyze, for example 688981.SH, 600519.SH, NVDA, or 00700.HK")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="MarketForge API base URL. Default: env MARKETFORGE_API_URL or http://localhost:8000")
    parser.add_argument("--period", default="daily", choices=["daily", "weekly", "monthly"], help="Candle period")
    parser.add_argument("--limit", default=120, type=int, help="Candle limit, 5-500")
    parser.add_argument("--refresh", action="store_true", help="Refresh only this symbol's candle data before analysis")
    parser.add_argument("--full-refresh", action="store_true", help="Run the broad market refresh pipeline before analysis")
    parser.add_argument("--output", help="Markdown output path. Default: analysis_out/<symbol>-<timestamp>.md")
    parser.add_argument("--raw-json", action="store_true", help="Also write the collected raw API JSON next to the report")
    parser.add_argument("--write-journal", action="store_true", help="POST the trade-plan journal draft to /api/journal. This modifies app data.")
    args = parser.parse_args(argv)
    if args.limit < 5 or args.limit > 500:
        parser.error("--limit must be between 5 and 500")
    return args


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return Path(args.output).expanduser().resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path.cwd() / "analysis_out" / f"{safe_filename(args.symbol)}-{stamp}.md"


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    args.symbol = normalize_symbol(args.symbol)
    bundle = collect_data(args)
    report = build_report(bundle, args.symbol, args)
    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    raw_path = write_json_snapshot(path, bundle) if args.raw_json else None

    errors = listify(bundle.get("errors"))
    summary = textwrap.dedent(
        f"""
        Wrote analysis report: {path}
        Symbol: {args.symbol}
        Endpoint errors: {len(errors)}
        Mode: {'targeted refresh + analysis' if args.refresh else 'analysis only'}
        """
    ).strip()
    if raw_path:
        summary += f"\nWrote raw JSON snapshot: {raw_path}"
    print(summary)
    if bundle.get("system_status") is None:
        print("System status endpoint failed; check that the backend is running.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
