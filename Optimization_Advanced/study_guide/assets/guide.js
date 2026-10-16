/* ============================================================
   LSD study guide · shared behaviour
   Loaded (defer) by every page after KaTeX + auto-render.
   Exposes window.LSD = { macros, svg helpers, scales, plotting,
   controls binding, colours, toast } for page-specific widgets.
   ============================================================ */
(function () {
  'use strict';

  /* ---------- KaTeX ---------- */
  var MACROS = {
    "\\R": "\\mathbb{R}", "\\N": "\\mathbb{N}", "\\Z": "\\mathbb{Z}",
    "\\H": "\\mathcal{H}", "\\G": "\\mathcal{G}", "\\K": "\\mathcal{K}",
    "\\ps": "\\langle #1\\,|\\,#2\\rangle", "\\norm": "\\lVert #1\\rVert", "\\abs": "\\lvert #1\\rvert",
    "\\le": "\\leqslant", "\\leq": "\\leqslant", "\\ge": "\\geqslant", "\\geq": "\\geqslant",
    "\\Id": "\\mathrm{Id}", "\\prox": "\\operatorname{prox}", "\\rprox": "\\operatorname{rprox}",
    "\\Argmin": "\\operatorname{Argmin}", "\\argmin": "\\operatorname*{arg\\,min}", "\\argmax": "\\operatorname*{arg\\,max}",
    "\\dom": "\\operatorname{dom}", "\\epi": "\\operatorname{epi}", "\\lev": "\\operatorname{lev}",
    "\\Fix": "\\operatorname{Fix}", "\\zer": "\\operatorname{zer}", "\\ran": "\\operatorname{ran}", "\\Ker": "\\operatorname{ker}",
    "\\inte": "\\operatorname{int}", "\\sgn": "\\operatorname{sign}", "\\diag": "\\operatorname{diag}",
    "\\Gz": "\\Gamma_0(#1)", "\\ind": "\\iota", "\\env": "{}^{#1}\\!#2",
    "\\Lip": "\\operatorname{Lip}", "\\gra": "\\operatorname{gra}", "\\tr": "\\operatorname{tr}",
    "\\eps": "\\varepsilon", "\\ol": "\\overline{#1}", "\\wto": "\\rightharpoonup", "\\xhat": "\\hat{x}",
    "\\B": "\\mathcal{B}", "\\Lag": "\\mathcal{L}", "\\PC": "P_{C}", "\\NC": "N_{C}", "\\one": "\\mathbf{1}"
  };
  var mathDone = false;
  function renderMaths(root) {
    if (typeof window.renderMathInElement !== 'function') return;
    try {
      window.renderMathInElement(root || document.body, {
        delimiters: [{ left: '$$', right: '$$', display: true }, { left: '$', right: '$', display: false },
                     { left: '\\(', right: '\\)', display: false }, { left: '\\[', right: '\\]', display: true }],
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option', 'svg'],
        throwOnError: false, strict: 'ignore', macros: MACROS
      });
    } catch (e) { if (window.console) console.warn('KaTeX render failed', e); }
  }
  function renderAll() { if (mathDone) return; mathDone = true; renderMaths(document.body); document.dispatchEvent(new CustomEvent('lsd:mathdone')); }
  document.addEventListener('DOMContentLoaded', renderAll);
  window.addEventListener('load', renderAll);

  /* ---------- theme ---------- */
  var root = document.documentElement;
  function getTheme() { try { return localStorage.getItem('lsd-theme') || 'auto'; } catch (e) { return 'auto'; } }
  function applyTheme(t) {
    if (t === 'auto') root.removeAttribute('data-theme'); else root.setAttribute('data-theme', t);
    document.querySelectorAll('.theme-toggle').forEach(function (b) {
      b.textContent = t === 'dark' ? '☀ Light' : (t === 'light' ? '◐ Auto' : '☾ Dark');
    });
    document.dispatchEvent(new CustomEvent('lsd:theme'));
  }
  applyTheme(getTheme());
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.theme-toggle'); if (!b) return;
    var t = getTheme(); var next = t === 'auto' ? 'dark' : (t === 'dark' ? 'light' : 'auto');
    try { localStorage.setItem('lsd-theme', next); } catch (err) {}
    applyTheme(next);
  });

  /* ---------- TOC highlighting ---------- */
  function initToc() {
    var links = Array.prototype.slice.call(document.querySelectorAll('.toc a.l[href^="#"]'));
    if (!links.length) return;
    var map = {}; links.forEach(function (a) { var id = a.getAttribute('href').slice(1); var el = document.getElementById(id); if (el) map[id] = a; });
    var ids = Object.keys(map); if (!ids.length) return;
    var current = null;
    function setOn(id) { if (current === id) return; current = id; links.forEach(function (a) { a.classList.remove('on'); }); if (map[id]) map[id].classList.add('on'); }
    function update() {
      var y = window.scrollY + 90, best = null;
      for (var i = 0; i < ids.length; i++) { var el = document.getElementById(ids[i]); if (el && el.getBoundingClientRect().top + window.scrollY <= y) best = ids[i]; }
      if (best) setOn(best);
    }
    window.addEventListener('scroll', update, { passive: true }); window.addEventListener('resize', update); update();
    /* close mobile TOC after click */
    links.forEach(function (a) { a.addEventListener('click', function () { var d = document.getElementById('toc-det'); if (d && window.innerWidth <= 980) d.removeAttribute('open'); }); });
  }
  document.addEventListener('DOMContentLoaded', initToc);

  /* ---------- page strip: bring the current page into view when the strip scrolls (phones) ---------- */
  document.addEventListener('DOMContentLoaded', function () {
    var strip = document.querySelector('.site .strip'), on = strip && strip.querySelector('a.on');
    if (!strip || !on || strip.scrollWidth <= strip.clientWidth) return;
    var li = on.parentElement || on;
    strip.scrollLeft = Math.max(0, li.offsetLeft - strip.offsetLeft - (strip.clientWidth - li.offsetWidth) / 2);
  });

  /* ---------- TOC collapsed on phones, always open on desktop ---------- */
  /* On phones the TOC body is hidden by CSS unless the reader opened it (class user-open), so it never
     flashes open on load; on desktop the details element is always open. */
  var TOC_MQ = window.matchMedia ? window.matchMedia('(max-width: 980px)') : null;
  function syncTocOpen() {
    var d = document.getElementById('toc-det'); if (!d) return;
    d.classList.remove('user-open');
    if (TOC_MQ && TOC_MQ.matches) d.removeAttribute('open'); else d.setAttribute('open', '');
  }
  document.addEventListener('DOMContentLoaded', function () {
    var d = document.getElementById('toc-det');
    syncTocOpen();
    if (d) d.addEventListener('toggle', function () { if (TOC_MQ && TOC_MQ.matches) d.classList.toggle('user-open', d.open); });
    try { TOC_MQ.addEventListener('change', syncTocOpen); } catch (e) { window.addEventListener('resize', syncTocOpen); }
  });

  /* ---------- expand/collapse proofs ---------- */
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-toggle-details]'); if (!b) return;
    var sel = b.getAttribute('data-toggle-details') || 'details.proof';
    var open = b.getAttribute('aria-pressed') !== 'true';
    document.querySelectorAll(sel).forEach(function (d) { if (open) d.setAttribute('open', ''); else d.removeAttribute('open'); });
    b.setAttribute('aria-pressed', open ? 'true' : 'false');
    var lab = b.getAttribute('data-label-open'), lab2 = b.getAttribute('data-label-closed');
    if (lab && lab2) b.textContent = open ? lab : lab2;
  });

  /* ---------- spoilers, flashcards, known-checkboxes ---------- */
  document.addEventListener('click', function (e) {
    var s = e.target.closest && e.target.closest('.spoiler > button');
    if (s) { var sp = s.parentElement; sp.classList.toggle('open'); if (sp.classList.contains('open')) renderMaths(sp); return; }
    var f = e.target.closest && e.target.closest('.flash');
    if (f && !(e.target.closest('a'))) { f.classList.toggle('flipped'); return; }
  });
  document.addEventListener('keydown', function (e) {
    if ((e.key === ' ' || e.key === 'Enter') && e.target.classList && e.target.classList.contains('flash')) { e.preventDefault(); e.target.classList.toggle('flipped'); }
  });
  function knownKey() { return 'lsd-known:' + (location.pathname.split('/').pop() || 'index'); }
  function loadKnown() { try { return JSON.parse(localStorage.getItem(knownKey()) || '{}'); } catch (e) { return {}; } }
  function saveKnown(k) { try { localStorage.setItem(knownKey(), JSON.stringify(k)); } catch (e) {} }
  document.addEventListener('DOMContentLoaded', function () {
    var known = loadKnown();
    document.querySelectorAll('.card[id]').forEach(function (card) {
      var head = card.querySelector('.card-head'); if (!head) return;
      var lab = document.createElement('label'); lab.className = 'check'; lab.title = 'Tick when you can restate this result and its proof idea from memory';
      var cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = !!known[card.id];
      lab.appendChild(cb); lab.appendChild(document.createTextNode('known'));
      head.appendChild(lab);
      if (cb.checked) card.classList.add('known');
      cb.addEventListener('change', function () { known[card.id] = cb.checked; if (!cb.checked) delete known[card.id]; saveKnown(known); card.classList.toggle('known', cb.checked); updateKnownCount(); });
    });
    updateKnownCount();
    function updateKnownCount() {
      var out = document.getElementById('known-count'); if (!out) return;
      var all = document.querySelectorAll('.card[id] .check input'); var n = 0; all.forEach(function (c) { if (c.checked) n++; });
      out.textContent = n + ' / ' + all.length + ' cards marked known';
    }
    var reset = document.getElementById('known-reset');
    if (reset) reset.addEventListener('click', function () { known = {}; saveKnown(known); document.querySelectorAll('.card[id] .check input').forEach(function (c) { c.checked = false; c.closest('.card').classList.remove('known'); }); updateKnownCount(); });
  });

  /* ---------- xref popovers (registry-driven) ---------- */
  var pop = null, cur = null, pinned = false, timer = null;
  function ensurePop() {
    if (pop) return pop;
    pop = document.createElement('div'); pop.className = 'xpop'; pop.hidden = true; pop.setAttribute('role', 'dialog');
    pop.innerHTML = '<button class="xpop-x" aria-label="close">×</button><div class="xpop-h"><span class="xpop-k"></span><span class="xpop-t"></span><a class="xpop-go" href="#">open ↗</a></div><div class="xpop-b"></div>';
    document.body.appendChild(pop);
    pop.addEventListener('mouseleave', function () { if (!pinned) timer = setTimeout(hidePop, 200); });
    pop.addEventListener('mouseenter', function () { clearTimeout(timer); });
    pop.querySelector('.xpop-go').addEventListener('click', function () { pinned = false; setTimeout(hidePop, 50); });
    return pop;
  }
  var KIND = { def: 'Definition', thm: 'Theorem', prop: 'Proposition', lemma: 'Lemma', cor: 'Corollary', algo: 'Algorithm', ex: 'Exercise', rem: 'Remark', lab: 'Lab', trick: 'Trick', sec: 'Section' };
  function showPop(el) {
    var id = el.getAttribute('data-id'); var R = window.LSD_REGISTRY || {}; var r = R[id];
    if (!r) return;
    ensurePop();
    if (cur) cur.classList.remove('on'); cur = el; el.classList.add('on');
    pop.querySelector('.xpop-k').textContent = KIND[r.k] || r.k || '';
    pop.querySelector('.xpop-t').textContent = r.t || id;
    var go = pop.querySelector('.xpop-go'); var here = (location.pathname.split('/').pop() || 'index.html');
    go.href = (r.p === here ? '' : r.p) + '#' + id; go.hidden = false;
    var b = pop.querySelector('.xpop-b'); b.innerHTML = r.s || ''; renderMaths(b);
    pop.hidden = false;
    var rect = el.getBoundingClientRect(); var sx = window.scrollX, sy = window.scrollY;
    var w = pop.offsetWidth, h = pop.offsetHeight;
    var left = rect.left + sx; if (left + w > sx + window.innerWidth - 12) left = Math.max(sx + 12, sx + window.innerWidth - 12 - w);
    var top = rect.bottom + sy + 8; if (rect.bottom + 8 + h > window.innerHeight && rect.top - 8 - h > 0) top = rect.top + sy - 8 - h;
    pop.style.left = left + 'px'; pop.style.top = top + 'px';
  }
  function hidePop() { if (!pop) return; pop.hidden = true; pinned = false; if (cur) { cur.classList.remove('on'); cur = null; } }
  document.addEventListener('mouseover', function (e) { var el = e.target.closest && e.target.closest('.xref[data-id]'); if (!el || pinned) return; clearTimeout(timer); showPop(el); });
  document.addEventListener('mouseout', function (e) { var el = e.target.closest && e.target.closest('.xref[data-id]'); if (!el || pinned) return; timer = setTimeout(function () { if (pop && !pop.matches(':hover') && !pinned) hidePop(); }, 250); });
  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('.xref[data-id]');
    if (el) {
      var R = window.LSD_REGISTRY || {}; if (!R[el.getAttribute('data-id')]) return; /* no registry entry: behave as a normal link */
      e.preventDefault(); if (cur === el && pinned) { hidePop(); } else { showPop(el); pinned = true; } return;
    }
    if (e.target.closest && e.target.closest('.xpop')) { if (e.target.classList.contains('xpop-x')) hidePop(); return; }
    hidePop();
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hidePop(); });

  /* ---------- hash → open the enclosing details ---------- */
  function openTarget() {
    var id = location.hash.slice(1); if (!id) return; var el = document.getElementById(id); if (!el) return;
    var p = el.parentElement; while (p) { if (p.tagName === 'DETAILS') p.setAttribute('open', ''); p = p.parentElement; }
    if (el.tagName === 'DETAILS') el.setAttribute('open', '');
  }
  window.addEventListener('hashchange', openTarget); document.addEventListener('DOMContentLoaded', openTarget);

  /* ---------- toast ---------- */
  var toastEl = null, toastT = null;
  function toast(msg) {
    if (!toastEl) { toastEl = document.createElement('div'); toastEl.className = 'toast'; document.body.appendChild(toastEl); }
    toastEl.textContent = msg; toastEl.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove('on'); }, 1800);
  }

  /* ---------- SVG / plotting helpers for widgets ---------- */
  var NS = 'http://www.w3.org/2000/svg';
  function el(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) if (Object.prototype.hasOwnProperty.call(attrs, k) && attrs[k] != null) {
      if (k === 'text') e.textContent = attrs[k]; else if (k === 'class') e.setAttribute('class', attrs[k]); else e.setAttribute(k, attrs[k]);
    }
    if (parent) parent.appendChild(e);
    return e;
  }
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }
  function fmt(x, d) { if (d == null) d = 2; if (!isFinite(x)) return x > 0 ? '+∞' : (x < 0 ? '−∞' : 'NaN'); var v = Math.abs(x) < Math.pow(10, -d) / 2 ? 0 : x; return v.toFixed(d).replace('-', '−'); }
  /* linear scale: domain [d0,d1] → range [r0,r1]; returns function with .inv */
  function scale(d0, d1, r0, r1) { var f = function (x) { return r0 + (x - d0) * (r1 - r0) / (d1 - d0); }; f.inv = function (y) { return d0 + (y - r0) * (d1 - d0) / (r1 - r0); }; f.d = [d0, d1]; f.r = [r0, r1]; return f; }
  /* niceTicks: ~n ticks between a and b */
  function ticks(a, b, n) { n = n || 5; var span = b - a; if (span <= 0) return [a]; var step = Math.pow(10, Math.floor(Math.log10(span / n))); var err = span / n / step; if (err >= 7.5) step *= 10; else if (err >= 3.5) step *= 5; else if (err >= 1.5) step *= 2; var out = []; for (var v = Math.ceil(a / step) * step; v <= b + 1e-9; v += step) out.push(Math.abs(v) < 1e-12 ? 0 : v); return out; }
  /* axes(svg, X, Y, opts): draws axes through origin (or at borders if origin not in view) with tick labels */
  function axes(svg, X, Y, o) {
    o = o || {}; var g = el('g', { class: 'axes' }, svg);
    var x0 = (X.d[0] <= 0 && X.d[1] >= 0) ? X(0) : X(X.d[0]); var y0 = (Y.d[0] <= 0 && Y.d[1] >= 0) ? Y(0) : Y(Y.d[0]);
    el('line', { x1: X(X.d[0]), x2: X(X.d[1]), y1: y0, y2: y0, class: 's-mut', 'stroke-width': 1 }, g);
    el('line', { x1: x0, x2: x0, y1: Y(Y.d[0]), y2: Y(Y.d[1]), class: 's-mut', 'stroke-width': 1 }, g);
    if (o.grid !== false) {
      ticks(X.d[0], X.d[1], o.nx || 6).forEach(function (t) { if (Math.abs(t) > 1e-12 || o.zeroLabel) { el('line', { x1: X(t), x2: X(t), y1: y0 - 3, y2: y0 + 3, class: 's-mut' }, g); el('text', { x: X(t), y: y0 + 14, 'text-anchor': 'middle', text: fmt(t, o.dx != null ? o.dx : 1), class: 'f-mut' }, g); } });
      ticks(Y.d[0], Y.d[1], o.ny || 5).forEach(function (t) { if (Math.abs(t) > 1e-12 || o.zeroLabel) { el('line', { x1: x0 - 3, x2: x0 + 3, y1: Y(t), y2: Y(t), class: 's-mut' }, g); el('text', { x: x0 - 6, y: Y(t) + 4, 'text-anchor': 'end', text: fmt(t, o.dy != null ? o.dy : 1), class: 'f-mut' }, g); } });
    }
    if (o.xlabel) el('text', { x: X(X.d[1]) - 2, y: y0 - 6, 'text-anchor': 'end', text: o.xlabel, class: 'tm f-ink2' }, g);
    if (o.ylabel) el('text', { x: x0 + 6, y: Y(Y.d[1]) + 12, text: o.ylabel, class: 'tm f-ink2' }, g);
    return g;
  }
  /* plotFn(svg, fn, X, Y, attrs, n): polyline of y=fn(x); breaks at non-finite values; clips to Y range */
  function plotFn(svg, fn, X, Y, attrs, n) {
    n = n || 240; var pts = [], segs = []; var lo = Math.min(Y.d[0], Y.d[1]), hi = Math.max(Y.d[0], Y.d[1]); var pad = (hi - lo) * 0.6;
    for (var i = 0; i <= n; i++) { var x = X.d[0] + (X.d[1] - X.d[0]) * i / n; var y = fn(x); if (!isFinite(y) || y > hi + pad || y < lo - pad) { if (pts.length) segs.push(pts); pts = []; continue; } pts.push(X(x).toFixed(2) + ',' + Y(Math.max(lo - pad, Math.min(hi + pad, y))).toFixed(2)); }
    if (pts.length) segs.push(pts);
    var g = el('g', null, svg);
    segs.forEach(function (s) { var a = Object.assign({ points: s.join(' '), fill: 'none', 'stroke-width': 2, class: 's-ink' }, attrs || {}); el('polyline', a, g); });
    return g;
  }
  function dot(svg, x, y, r, cls) { return el('circle', { cx: x, cy: y, r: r || 4, class: cls || 'f-acc' }, svg); }
  function line(svg, x1, y1, x2, y2, cls, extra) { return el('line', Object.assign({ x1: x1, y1: y1, x2: x2, y2: y2, class: cls || 's-ink', 'stroke-width': 1.5 }, extra || {}), svg); }
  function text(svg, x, y, s, cls, extra) { return el('text', Object.assign({ x: x, y: y, text: s, class: cls || 'f-ink2' }, extra || {}), svg); }
  function arrowDefs(svg, id, cls) { var d = svg.querySelector('defs') || el('defs', null, svg); var m = el('marker', { id: id, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' }, d); el('path', { d: 'M0,0 L10,5 L0,10 z', class: cls || 'f-ink2' }, m); return 'url(#' + id + ')'; }
  /* bindRange(id, cb): slider with <output id=id+'-v'>; calls cb(value) on input and once now */
  function bindRange(id, cb, fmtd) {
    var r = document.getElementById(id); if (!r) return null; var o = document.getElementById(id + '-v');
    function go() { var v = parseFloat(r.value); if (o) o.textContent = fmtd ? fmtd(v) : fmt(v, (r.step && r.step.indexOf('.') >= 0) ? r.step.split('.')[1].length : 0); cb(v); }
    r.addEventListener('input', go); go(); return r;
  }
  /* bindSeg(containerId, cb): segmented buttons with data-v; calls cb(value) */
  function bindSeg(id, cb) {
    var c = document.getElementById(id); if (!c) return null; var bs = c.querySelectorAll('button');
    bs.forEach(function (b) { b.addEventListener('click', function () { bs.forEach(function (x) { x.setAttribute('aria-pressed', 'false'); }); b.setAttribute('aria-pressed', 'true'); cb(b.getAttribute('data-v')); }); });
    var on = c.querySelector('button[aria-pressed="true"]') || bs[0]; if (on) { on.setAttribute('aria-pressed', 'true'); cb(on.getAttribute('data-v')); }
    return c;
  }
  function cssVar(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
  /* lerp colour helper not needed: use classes .s-1 … .s-5 */

  window.LSD = { macros: MACROS, renderMaths: renderMaths, toast: toast, el: el, clear: clear, fmt: fmt, scale: scale, ticks: ticks, axes: axes, plotFn: plotFn, dot: dot, line: line, text: text, arrowDefs: arrowDefs, bindRange: bindRange, bindSeg: bindSeg, cssVar: cssVar };
})();
