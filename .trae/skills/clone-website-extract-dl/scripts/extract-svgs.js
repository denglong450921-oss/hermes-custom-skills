#!/usr/bin/env node
// extract-inline-svgs.js — Extract and deduplicate inline SVGs from page HTML
// Usage: cat page.html | node extract-inline-svgs.js
// Output: JSON with unique SVGs as React components

const fs = require('fs');

let html = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => html += chunk);
process.stdin.on('end', () => {
  // Find all inline <svg> elements
  const svgRegex = /<svg[^>]*>[\s\S]*?<\/svg>/gi;
  const svgs = html.match(svgRegex) || [];

  // Deduplicate by normalized inner content
  const seen = new Map();
  const unique = [];

  for (const svg of svgs) {
    const norm = svg.replace(/\s+/g, ' ').trim();
    const key = norm.slice(0, 200); // fingerprint
    if (!seen.has(key)) {
      seen.set(key, { count: 0, svg: norm });
    }
    seen.get(key).count++;
  }

  for (const [key, val] of seen) {
    // Extract viewBox and inner content
    const viewBoxMatch = val.svg.match(/viewBox="([^"]*)"/);
    const viewBox = viewBoxMatch ? viewBoxMatch[1] : '0 0 24 24';
    
    // Generate component name from content hash
    const hash = key.length.toString(36) + key.slice(10, 20).replace(/[^a-zA-Z0-9]/g, '');
    const name = `SvgIcon_${hash}`;

    // Compress: strip unnecessary attributes, keep only viewBox and essentials
    const compressed = val.svg
      .replace(/\s+/g, ' ')
      .replace(/>\s+</g, '><')
      .replace(/xmlns="[^"]*"/g, '')
      .replace(/version="[^"]*"/g, '')
      .replace(/enable-background="[^"]*"/g, '')
      .trim();

    unique.push({
      name,
      viewBox,
      count: val.count,
      svg: compressed.slice(0, 1000), // cap at 1000 chars
      component: `function ${name}({ size = 24, className = '' }) {\n  return (\n    <svg viewBox="${viewBox}" width={size} height={size} className={className} fill="currentColor">\n${compressed.replace(/^<svg[^>]*>/, '').replace(/<\/svg>$/, '').trim()}\n    </svg>\n  );\n}`
    });
  }

  // Output summary
  console.log(JSON.stringify({
    total_raw: svgs.length,
    unique_count: unique.length,
    savings: `Raw: ${svgs.length} → Unique: ${unique.length} (${Math.round((1 - unique.length/svgs.length)*100)}% reduction)`,
    icons: unique.sort((a,b) => b.count - a.count)
  }, null, 2));
});
