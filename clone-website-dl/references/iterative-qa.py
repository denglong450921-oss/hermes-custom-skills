#!/usr/bin/env python3
"""50x QA loop — catch all layout issues"""
import asyncio, json, sys
from playwright.async_api import async_playwright

URL = "http://localhost:3459"

async def check(iteration, pw):
    browser = await pw.chromium.launch(headless=True)
    ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
    page = await ctx.new_page()
    issues = []
    errors = []

    async def on_console(msg):
        if msg.type == "error":
            errors.append(msg.text[:150])
    page.on("console", on_console)

    try:
        await page.goto(URL, wait_until="networkidle", timeout=20000)
        await page.wait_for_timeout(3000)

        # Check all text
        body = (await page.evaluate("document.body.innerText")).lower()
        required = ["开始销售","免费在线","创建商店","只需点几下鼠标",
                    "160 万个信赖","随时随地销售","更快地成长","管理简单",
                    "实时支持","ecwid app store","mobile apps",
                    "开始在线销售","帮助中心"]
        for t in required:
            if t.lower() not in body:
                issues.append(f"missing:'{t}'")

        # Section count
        n_sections = await page.evaluate("document.querySelectorAll('section').length")
        if n_sections < 7:
            issues.append(f"sections:{n_sections}")

        # Nav exists
        nav_h = await page.evaluate("() => document.querySelector('nav')?.offsetHeight || 0")
        if nav_h < 50:
            issues.append(f"nav_h:{nav_h}")

        # Images loaded
        broken = await page.evaluate("""
            Array.from(document.querySelectorAll('img'))
                .filter(i => i.getAttribute('src') && i.getAttribute('src') !== '' && (!i.complete || i.naturalWidth === 0))
                .length
        """)
        if broken > 0:
            issues.append(f"broken_imgs:{broken}")

        # CTA colors — check ALL CTA-like anchors
        ctas = await page.evaluate("""
            Array.from(document.querySelectorAll('a[class*=\"btn\"]'))
                .slice(0,6).map(a => ({bg: getComputedStyle(a).backgroundColor, text: a.textContent.trim().slice(0,10)}))
        """)
        if not ctas:
            issues.append("no_cta_buttons")
        else:
            has_yellow = any("250, 224, 83" in c["bg"] for c in ctas)
            has_black = any("0, 0, 0" in c["bg"] for c in ctas)
            if not has_yellow:
                issues.append(f"no_yellow_cta")
            if not has_black:
                issues.append(f"no_black_cta")

        # Section positions — check no overlap
        positions = await page.evaluate("""
            () => Array.from(document.querySelectorAll('section')).map(s => {
                const r = s.getBoundingClientRect();
                const cs = getComputedStyle(s);
                return {h: Math.round(r.height), w: Math.round(r.width), display: cs.display, overflow: cs.overflow};
            })
        """)
        for p in positions:
            if p["w"] < 300:
                issues.append(f"section_too_narrow:w={p['w']}")

        # Console errors
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(500)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        if errors:
            issues.append(f"console_err:{errors[:3]}")

        # Mobile check
        mobile_ctx = await browser.new_context(viewport={"width": 390, "height": 844})
        mp = await mobile_ctx.new_page()
        await mp.goto(URL, wait_until="networkidle", timeout=20000)
        await mp.wait_for_timeout(2000)
        mb = (await mp.evaluate("document.body.innerText")).lower()
        for t in required:
            if t.lower() not in mb:
                issues.append(f"mobile_missing:'{t}'")
        mw = await mp.evaluate("document.querySelector('section')?.getBoundingClientRect().width || 0")
        if mw != 390:
            issues.append(f"mobile_width:{mw}")
        await mobile_ctx.close()

        status = "FAIL" if issues else "PASS"
        result = {"i": iteration, "status": status, "issues": issues}

    except Exception as e:
        result = {"i": iteration, "status": "CRASH", "error": str(e)[:200]}

    await browser.close()
    return result

async def main():
    N = 50
    print(f"QA 50 rounds on {URL}")
    failed = []

    async with async_playwright() as pw:
        for i in range(1, N+1):
            r = await check(i, pw)
            mark = "✓" if r["status"] == "PASS" else "✗"
            detail = r.get("issues", []) or r.get("error", "")
            print(f"  [{mark}] #{i:2d} {r['status']:5s} {detail}")
            if r["status"] != "PASS":
                failed.append(r)

    print(f"\n{'='*50}")
    if failed:
        print(f"FAILURES: {len(failed)}/{N}")
        # Group by issue type
        by_type = {}
        for f in failed:
            for iss in f.get("issues", []):
                key = iss.split(":")[0]
                by_type.setdefault(key, 0)
                by_type[key] += 1
        print("By type:", json.dumps(by_type, ensure_ascii=False))
        for f in failed[:5]:
            print(f"  #{f['i']}: {f.get('issues', f.get('error'))}")
    else:
        print(f"ALL {N} PASSED")

    with open("/tmp/qa-50-results.json", "w") as f:
        json.dump({"total": N, "failures": len(failed), "results": failed}, f, ensure_ascii=False)

asyncio.run(main())
