/**
 * CSS Verification Checklist
 * Run on BOTH the original site and the clone. Compare JSON output to catch mismatches.
 * Output: key CSS values for critical elements.
 */
JSON.stringify({
  h1FontSize: getComputedStyle(document.querySelector('h1')).fontSize,
  h1FontWeight: getComputedStyle(document.querySelector('h1')).fontWeight,
  h2s: [...document.querySelectorAll('h2')].map(h => ({
    text: h.textContent?.trim().slice(0, 25),
    size: getComputedStyle(h).fontSize,
    weight: getComputedStyle(h).fontWeight
  })),
  bodyFont: getComputedStyle(document.body).fontFamily,
  bodyBg: getComputedStyle(document.body).backgroundColor,
  btnBg: getComputedStyle(document.querySelector('a[href*="register"], .cta-signup, .btn')).backgroundColor,
  btnColor: getComputedStyle(document.querySelector('a[href*="register"], .cta-signup, .btn')).color,
  btnPadding: getComputedStyle(document.querySelector('a[href*="register"], .cta-signup, .btn')).padding,
  btnRadius: getComputedStyle(document.querySelector('a[href*="register"], .cta-signup, .btn')).borderRadius
});
