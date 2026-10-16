#!/usr/bin/env node
/* Validate one or more study-guide pages in headless Chromium (Playwright).
   Usage (from the study_guide folder):
     node tools/validate.js 03_proximity_operator.html [other.html …]
     node tools/validate.js --all
     node tools/validate.js --no-shots 03_proximity_operator.html
   Reports: console errors / page errors, KaTeX errors, widgets with empty SVG, controls that throw,
   horizontal overflow at 390px, and writes a screenshot of every widget to
   $SHOTS/<page>/<widget-id>.png (SHOTS defaults to the session scratchpad). Exit code 1 on blocking problems. */
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const PAGES = ['index.html', '01_convex_analysis.html', '02_subdifferential_conjugate.html', '03_proximity_operator.html',
  '04_fixed_point_forward_backward.html', '05_douglas_rachford_ppxa.html', '06_duality_admm_primal_dual.html',
  '07_majorization_minimization.html', '08_labs.html', '09_toolbox.html', '10_memorize.html'];
const SHOTS = process.env.SHOTS || '/tmp/claude-0/-home-user-MVA-courses/f24c33d9-fb2f-5d73-b038-590fc5d05386/scratchpad/shots';

async function validate(browser, page_name, opts) {
  const file = path.join(ROOT, page_name);
  const report = { page: page_name, consoleErrors: [], pageErrors: [], katexErrors: [], widgets: [], overflow: null, blocking: 0, warnings: 0 };
  if (!fs.existsSync(file)) { report.pageErrors.push('file not found'); report.blocking++; return report; }
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  page.on('console', m => { if (m.type() === 'error') report.consoleErrors.push(m.text()); });
  page.on('pageerror', e => report.pageErrors.push(String(e && e.message || e)));
  await page.goto('file://' + file, { waitUntil: 'load' });
  await page.waitForTimeout(1200);
  // KaTeX errors
  const kx = await page.evaluate(() => Array.from(document.querySelectorAll('.katex-error')).slice(0, 40).map(e => (e.getAttribute('title') || e.textContent || '').slice(0, 160)));
  report.katexErrors = kx;
  const rawDollars = await page.evaluate(() => {
    // leftover '$' pairs in text nodes outside code/pre/svg/script = unrendered maths
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, { acceptNode: n => { let p = n.parentElement; while (p) { if (/^(SCRIPT|STYLE|PRE|CODE|SVG|TEXTAREA)$/.test(p.tagName)) return NodeFilter.FILTER_REJECT; p = p.parentElement; } return NodeFilter.FILTER_ACCEPT; } });
    const out = []; let n; while ((n = w.nextNode())) { const t = n.nodeValue; if (/\$[^$]{1,200}\$/.test(t)) out.push(t.trim().slice(0, 120)); if (out.length > 15) break; } return out;
  });
  report.unrendered = rawDollars;
  // widgets
  const widgets = await page.evaluate(() => Array.from(document.querySelectorAll('.widget')).map(w => ({ id: w.id || null, svgs: Array.from(w.querySelectorAll('svg')).map(s => ({ id: s.id || null, children: s.children.length })), canvases: w.querySelectorAll('canvas').length, ranges: Array.from(w.querySelectorAll('input[type=range]')).map(r => r.id), buttons: Array.from(w.querySelectorAll('button')).map((b, i) => b.id || (w.id + ':btn' + i)) })));
  for (const w of widgets) {
    const wr = { id: w.id, emptySvgs: w.svgs.filter(s => s.children === 0).map(s => s.id), interactErrors: [] };
    if (!w.id) { wr.interactErrors.push('widget without id'); }
    // exercise the controls
    const before = report.pageErrors.length + report.consoleErrors.length;
    for (const rid of w.ranges) {
      if (!rid) continue;
      try {
        await page.evaluate((id) => { const r = document.getElementById(id); if (!r) return; const min = parseFloat(r.min), max = parseFloat(r.max); [min, (min + max) / 2, max, parseFloat(r.defaultValue || r.value)].forEach(v => { r.value = String(v); r.dispatchEvent(new Event('input', { bubbles: true })); r.dispatchEvent(new Event('change', { bubbles: true })); }); }, rid);
      } catch (e) { wr.interactErrors.push('range ' + rid + ': ' + e.message); }
    }
    if (w.id) {
      try {
        await page.evaluate((wid) => { const w = document.getElementById(wid); if (!w) return; w.querySelectorAll('button').forEach(b => { try { b.click(); } catch (e) { console.error('click error in ' + wid + ': ' + e.message); } }); }, w.id);
      } catch (e) { wr.interactErrors.push('buttons: ' + e.message); }
      await page.waitForTimeout(150);
      // reset first segmented button if any
      await page.evaluate((wid) => { const w = document.getElementById(wid); if (!w) return; const b = w.querySelector('.seg button'); if (b) b.click(); }, w.id);
    }
    const after = report.pageErrors.length + report.consoleErrors.length;
    if (after > before) wr.interactErrors.push((after - before) + ' error(s) raised while exercising controls (see console/page errors)');
    const svgsAfter = w.id ? await page.evaluate((wid) => Array.from(document.getElementById(wid).querySelectorAll('svg')).map(s => ({ id: s.id || null, children: s.children.length })), w.id) : w.svgs;
    wr.emptySvgs = svgsAfter.filter(s => s.children === 0).map(s => s.id || '(no id)');
    if (w.svgs.length === 0 && w.canvases === 0) wr.interactErrors.push('no <svg> or <canvas> inside the widget');
    if (wr.emptySvgs.length) report.blocking++;
    if (wr.interactErrors.length) report.blocking++;
    // screenshot
    if (opts.shots && w.id) {
      try {
        const dir = path.join(SHOTS, page_name.replace(/\.html$/, ''));
        fs.mkdirSync(dir, { recursive: true });
        const h = await page.$('#' + CSS_escape(w.id));
        if (h) { await h.scrollIntoViewIfNeeded(); await page.waitForTimeout(80); await h.screenshot({ path: path.join(dir, w.id + '.png') }); wr.shot = path.join(dir, w.id + '.png'); }
      } catch (e) { wr.interactErrors.push('screenshot failed: ' + e.message); }
    }
    report.widgets.push(wr);
  }
  // flashcards flip & spoilers (smoke)
  await page.evaluate(() => { document.querySelectorAll('.spoiler > button').forEach(b => b.click()); document.querySelectorAll('.flash').forEach(f => f.click()); });
  await page.waitForTimeout(100);
  // dark mode render smoke
  await page.evaluate(() => { document.documentElement.setAttribute('data-theme', 'dark'); });
  await page.waitForTimeout(100);
  await page.evaluate(() => { document.documentElement.removeAttribute('data-theme'); });
  // mobile overflow
  await page.setViewportSize({ width: 390, height: 800 });
  await page.waitForTimeout(300);
  const ov = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: window.innerWidth, culprits: Array.from(document.querySelectorAll('body *')).filter(e => { const r = e.getBoundingClientRect(); return r.right > window.innerWidth + 2 && r.width > 40 && getComputedStyle(e).position !== 'fixed'; }).slice(0, 8).map(e => (e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ')[0] : ''))) }));
  report.overflow = ov.sw > ov.iw + 2 ? ov : null;
  if (report.overflow) report.warnings++;
  // full page screenshot (top) for a visual sanity check
  if (opts.shots) {
    try { const dir = path.join(SHOTS, page_name.replace(/\.html$/, '')); fs.mkdirSync(dir, { recursive: true }); await page.setViewportSize({ width: 1280, height: 900 }); await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(250); await page.screenshot({ path: path.join(dir, '_page_top.png'), fullPage: false }); } catch (e) { }
  }
  report.blocking += report.pageErrors.length + report.consoleErrors.length + report.katexErrors.length;
  report.warnings += report.unrendered.length;
  await ctx.close();
  return report;
}

function CSS_escape(s) { return s.replace(/([^a-zA-Z0-9_-])/g, '\\$1'); }

(async () => {
  const args = process.argv.slice(2);
  const shots = !args.includes('--no-shots');
  let pages = args.filter(a => !a.startsWith('--'));
  if (args.includes('--all')) pages = PAGES.filter(p => fs.existsSync(path.join(ROOT, p)));
  if (!pages.length) { console.error('usage: node tools/validate.js [--all] [--no-shots] page.html …'); process.exit(2); }
  const browser = await chromium.launch();
  let exit = 0;
  for (const p of pages) {
    const r = await validate(browser, p, { shots });
    const lines = [];
    lines.push(`== ${p}: ${r.blocking} blocking, ${r.warnings} warning(s)`);
    r.pageErrors.forEach(e => lines.push('  [PAGE ERROR] ' + e));
    r.consoleErrors.forEach(e => lines.push('  [CONSOLE ERROR] ' + e));
    r.katexErrors.forEach(e => lines.push('  [KATEX ERROR] ' + e));
    r.unrendered.forEach(e => lines.push('  [unrendered $…$] ' + e));
    r.widgets.forEach(w => {
      const bad = w.emptySvgs.length || w.interactErrors.length;
      lines.push(`  ${bad ? '[WIDGET PROBLEM]' : '[widget ok]'} ${w.id}${w.emptySvgs.length ? ' empty svg: ' + w.emptySvgs.join(',') : ''}${w.interactErrors.length ? ' ' + w.interactErrors.join('; ') : ''}${w.shot ? ' -> ' + w.shot : ''}`);
    });
    if (r.overflow) lines.push(`  [overflow at 390px] scrollWidth ${r.overflow.sw} > ${r.overflow.iw}; culprits: ${r.overflow.culprits.join(', ')}`);
    console.log(lines.join('\n'));
    if (r.blocking) exit = 1;
  }
  await browser.close();
  process.exit(exit);
})();
