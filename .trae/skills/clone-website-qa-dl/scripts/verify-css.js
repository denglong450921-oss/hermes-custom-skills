/**
 * CSS Verification Checklist
 * Run on BOTH the original site and the clone. Compare JSON output to catch mismatches.
 * Output: key CSS values for critical elements.
 */
const style = (selector) => {
  const el = document.querySelector(selector);
  return el ? getComputedStyle(el) : null;
};
const h1 = style('h1');
const btn = style('a[href*="register"], .cta-signup, .btn, button');
JSON.stringify({
  h1FontSize: h1?.fontSize || null,
  h1FontWeight: h1?.fontWeight || null,
  h2s: [...document.querySelectorAll('h2')].map(h => ({
    text: h.textContent?.trim().slice(0, 25),
    size: getComputedStyle(h).fontSize,
    weight: getComputedStyle(h).fontWeight
  })),
  bodyFont: getComputedStyle(document.body).fontFamily,
  bodyBg: getComputedStyle(document.body).backgroundColor,
  btnBg: btn?.backgroundColor || null,
  btnColor: btn?.color || null,
  btnPadding: btn?.padding || null,
  btnRadius: btn?.borderRadius || null
});
