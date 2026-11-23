// app.js — theme, folds, active table of contents and interactive figures of Speculative_decoding_LLM.
// (Same skeleton as Optimal_transport_ML/v2; the helpers of the widgets are those this guide needs:
//  probability vectors on a small vocabulary, bar charts with a hover layer, a table view for every chart.)
(function () {
  "use strict";

  /* ---------------- theme ---------------- */
  var root = document.documentElement;
  function currentTheme() {
    var t = root.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-action]");
    if (!b) return;
    var a = b.getAttribute("data-action");
    if (a === "theme") {
      var t = currentTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", t);
      try { localStorage.setItem("sd-guide-theme", t); } catch (err) {}
      redrawAll();
    } else if (a === "expand" || a === "collapse") {
      document.querySelectorAll("main details.fold").forEach(function (d) { d.open = a === "expand"; });
    }
  });
  if (window.matchMedia) {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    if (mq.addEventListener) mq.addEventListener("change", function () { redrawAll(); });
  }

  /* ---------------- printing: open every fold ---------------- */
  var printOpened = [];
  window.addEventListener("beforeprint", function () {
    printOpened = [];
    document.querySelectorAll("details.fold:not([open])").forEach(function (d) { d.open = true; printOpened.push(d); });
  });
  window.addEventListener("afterprint", function () { printOpened.forEach(function (d) { d.open = false; }); });

  /* ---------------- open the fold targeted by an anchor ---------------- */
  function openTarget() {
    if (!location.hash) return;
    var t = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    while (t) { if (t.tagName === "DETAILS") t.open = true; t = t.parentElement; }
  }
  window.addEventListener("hashchange", openTarget);
  openTarget();

  /* ---------------- display formulas wider than the column: mark them (right-edge shadow) ---------------- */
  function markScrolling() {
    document.querySelectorAll(".math-display").forEach(function (d) { d.classList.toggle("scrolls", d.scrollWidth > d.clientWidth + 2); });
  }
  markScrolling();
  window.addEventListener("resize", markScrolling);
  document.addEventListener("toggle", markScrolling, true);

  /* ---------------- table of contents folded on small screens ---------------- */
  if (window.innerWidth < 1100) document.querySelectorAll(".toc-box").forEach(function (d) { d.open = false; });

  /* ---------------- active entry of the table of contents ---------------- */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a[href^='#']"));
  if ("IntersectionObserver" in window && tocLinks.length) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var obs = new IntersectionObserver(function () {
      var heads = document.querySelectorAll("main h2[id], main h3[id]");
      var current = null;
      for (var i = 0; i < heads.length; i++) {
        if (heads[i].getBoundingClientRect().top < window.innerHeight * 0.35) current = heads[i].id; else break;
      }
      tocLinks.forEach(function (a) { a.classList.remove("active"); });
      if (current && byId[current]) byId[current].classList.add("active");
    }, { rootMargin: "0px 0px -60% 0px" });
    document.querySelectorAll("main h2[id], main h3[id]").forEach(function (h) { obs.observe(h); });
  }

  /* ======================================================================
     A small SVG plotting library
     ====================================================================== */
  var NS = "http://www.w3.org/2000/svg";
  function el(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function fmt(x, d) {
    if (d === undefined) d = 2;
    if (Number.isNaN(x)) return "—";
    if (!isFinite(x)) return x < 0 ? "−∞" : "∞";
    var s = x.toFixed(d);
    if (/^-0\.?0*$/.test(s)) s = s.slice(1);
    return s;
  }
  function pct(x, d) { return fmt(100 * x, d === undefined ? 0 : d) + "%"; }
  function Plot(svg, o) {
    this.svg = svg; this.o = o;
    this.W = o.w || 560; this.H = o.h || 360;
    this.pad = o.pad || { l: 46, r: 16, t: 26, b: 36 };
    svg.setAttribute("viewBox", "0 0 " + this.W + " " + this.H);
    svg.setAttribute("role", "img");
    if (o.label) svg.setAttribute("aria-label", o.label);
    this.clear();
  }
  Plot.prototype.clear = function () {
    while (this.svg.firstChild) this.svg.removeChild(this.svg.firstChild);
    this.g = el("g", {}, this.svg);
  };
  Plot.prototype.tx = function (x) {
    var o = this.o, a = o.x[0], b = o.x[1];
    if (o.xlog) { x = Math.log10(x); a = Math.log10(a); b = Math.log10(b); }
    return this.pad.l + (x - a) / (b - a) * (this.W - this.pad.l - this.pad.r);
  };
  Plot.prototype.ty = function (y) {
    var o = this.o, a = o.y[0], b = o.y[1];
    if (o.ylog) { y = Math.log10(Math.max(y, 1e-12)); a = Math.log10(a); b = Math.log10(b); }
    return this.H - this.pad.b - (y - a) / (b - a) * (this.H - this.pad.t - this.pad.b);
  };
  Plot.prototype.ix = function (px) { // pixel -> x (linear axes only)
    var o = this.o;
    return o.x[0] + (px - this.pad.l) / (this.W - this.pad.l - this.pad.r) * (o.x[1] - o.x[0]);
  };
  Plot.prototype.iy = function (py) {
    var o = this.o;
    return o.y[0] + (this.H - this.pad.b - py) / (this.H - this.pad.t - this.pad.b) * (o.y[1] - o.y[0]);
  };
  // Axes: solid hairline grid, tick labels in text colour. opt.xnames replaces numeric x ticks by category names.
  Plot.prototype.axes = function (opt) {
    opt = opt || {};
    var o = this.o, g = el("g", {}, this.g), self = this;
    var xt = opt.xticks || [], yt = opt.yticks || [];
    xt.forEach(function (v, k) {
      var X = self.tx(v);
      if (!opt.nogrid && !opt.noxgrid) el("line", { x1: X, x2: X, y1: self.pad.t, y2: self.H - self.pad.b, "class": "gr" }, g);
      var t = el("text", { x: X, y: self.H - self.pad.b + 16, "text-anchor": "middle", "class": "tx" }, g);
      t.textContent = opt.xnames ? opt.xnames[k] : (opt.xfmt ? opt.xfmt(v) : fmt(v, opt.xd || 0));
    });
    yt.forEach(function (v) {
      var Y = self.ty(v);
      if (!opt.nogrid) el("line", { x1: self.pad.l, x2: self.W - self.pad.r, y1: Y, y2: Y, "class": "gr" }, g);
      var t = el("text", { x: self.pad.l - 6, y: Y + 4, "text-anchor": "end", "class": "tx" }, g);
      t.textContent = opt.yfmt ? opt.yfmt(v) : fmt(v, opt.yd || 0);
    });
    var x0 = opt.cross ? Math.min(Math.max(0, o.x[0]), o.x[1]) : o.x[0];
    var y0 = opt.cross ? Math.min(Math.max(0, o.y[0]), o.y[1]) : o.y[0];
    if (o.ylog) y0 = o.y[0];
    if (o.xlog) x0 = o.x[0];
    el("line", { x1: this.pad.l, x2: this.W - this.pad.r, y1: this.ty(y0), y2: this.ty(y0), "class": "ax" }, g);
    if (!opt.noyaxis) el("line", { x1: this.tx(x0), x2: this.tx(x0), y1: this.pad.t, y2: this.H - this.pad.b, "class": "ax" }, g);
    if (opt.xlabel) { var a = el("text", { x: this.W - this.pad.r, y: this.H - 4, "text-anchor": "end", "class": "tx" }, g); a.textContent = opt.xlabel; }
    if (opt.ylabel) { var b = el("text", { x: this.pad.l, y: Math.max(12, this.pad.t - 10), "class": "tx" }, g); b.textContent = opt.ylabel; }
  };
  Plot.prototype.poly = function (pts, cls, extra) {
    var self = this, d = "", pen = false;
    pts.forEach(function (p) {
      if (p === null || !isFinite(p[0]) || !isFinite(p[1])) { pen = false; return; }
      d += (pen ? "L" : "M") + self.tx(p[0]).toFixed(2) + " " + self.ty(p[1]).toFixed(2);
      pen = true;
    });
    var a = { d: d, "class": cls };
    for (var k in extra || {}) a[k] = extra[k];
    return el("path", a, this.g);
  };
  Plot.prototype.area = function (pts, cls) { // closed polygon down to y = 0
    if (!pts.length) return null;
    var closed = [[pts[0][0], 0]].concat(pts, [[pts[pts.length - 1][0], 0]]);
    return this.poly(closed, cls);
  };
  Plot.prototype.fn = function (f, cls, n, x0, x1) {
    var o = this.o, pts = [];
    n = n || 400; x0 = x0 === undefined ? o.x[0] : x0; x1 = x1 === undefined ? o.x[1] : x1;
    for (var i = 0; i <= n; i++) {
      var x = o.xlog ? Math.pow(10, Math.log10(x0) + (Math.log10(x1) - Math.log10(x0)) * i / n) : x0 + (x1 - x0) * i / n;
      var y = f(x);
      var lo = o.y[0] - (o.y[1] - o.y[0]) * 2, hi = o.y[1] + (o.y[1] - o.y[0]) * 2;
      pts.push(isFinite(y) ? [x, Math.min(Math.max(y, lo), hi)] : null);
    }
    return this.poly(pts, cls);
  };
  // A marker with a 2px ring in the surface colour, so it stays legible on a line.
  Plot.prototype.dot = function (x, y, r, cls) { return el("circle", { cx: this.tx(x), cy: this.ty(y), r: r || 4, "class": cls + " ring" }, this.g); };
  Plot.prototype.seg = function (x1, y1, x2, y2, cls, extra) {
    var a = { x1: this.tx(x1), y1: this.ty(y1), x2: this.tx(x2), y2: this.ty(y2), "class": cls };
    for (var k in extra || {}) a[k] = extra[k];
    return el("line", a, this.g);
  };
  Plot.prototype.text = function (x, y, s, cls, anchor, dx, dy) {
    var t = el("text", { x: this.tx(x) + (dx || 0), y: this.ty(y) + (dy || 0), "class": cls || "tx", "text-anchor": anchor || "start" }, this.g);
    t.textContent = s; return t;
  };
  // A column from the baseline (y = 0) to y, centred at pixel offset dx from data x = xc. Thin (at most 24 px),
  // rounded at the data end only, square on the baseline.
  Plot.prototype.bar = function (xc, dx, wpx, y, cls, base) {
    var w = Math.min(wpx, 24), X = this.tx(xc) + (dx || 0) - w / 2, Y0 = this.ty(base || 0), Y1 = this.ty(y);
    var h = Y0 - Y1, r = Math.max(0, Math.min(4, w / 2, Math.abs(h))), sgn = h >= 0 ? 1 : -1;
    var d = "M" + X.toFixed(2) + " " + Y0.toFixed(2) + "V" + (Y1 + sgn * r).toFixed(2) +
      "Q" + X.toFixed(2) + " " + Y1.toFixed(2) + " " + (X + r).toFixed(2) + " " + Y1.toFixed(2) +
      "H" + (X + w - r).toFixed(2) +
      "Q" + (X + w).toFixed(2) + " " + Y1.toFixed(2) + " " + (X + w).toFixed(2) + " " + (Y1 + sgn * r).toFixed(2) +
      "V" + Y0.toFixed(2) + "Z";
    return el("path", { d: d, "class": cls }, this.g);
  };
  Plot.prototype.clip = function () {
    var id = "clip" + Math.random().toString(36).slice(2);
    var cp = el("clipPath", { id: id }, this.svg);
    el("rect", { x: this.pad.l, y: this.pad.t, width: this.W - this.pad.l - this.pad.r, height: this.H - this.pad.t - this.pad.b }, cp);
    this.g = el("g", { "clip-path": "url(#" + id + ")" }, this.svg);
  };
  Plot.prototype.unclip = function () { this.g = el("g", {}, this.svg); };
  // Hover layer of a line chart: a vertical hairline snaps to the nearest of the data positions xs, and one
  // tooltip lists every series there. rowsAt(i) returns { title, rows: [[cssVar | null, label, value], ...] }.
  // Arrow keys move the hairline when the plot has the focus.
  Plot.prototype.crosshair = function (xs, rowsAt) {
    var self = this, svg = this.svg, cur = -1;
    var line = el("line", { "class": "cross", y1: this.pad.t, y2: this.H - this.pad.b, visibility: "hidden" }, svg);
    var hit = el("rect", { x: this.pad.l, y: this.pad.t, width: this.W - this.pad.l - this.pad.r, height: this.H - this.pad.t - this.pad.b, "class": "hit", tabindex: 0 }, svg);
    hit.setAttribute("aria-label", "Plot area: use the left and right arrow keys to read the values");
    function at(i, px, py) {
      cur = i;
      var X = self.tx(xs[i]);
      line.setAttribute("x1", X); line.setAttribute("x2", X); line.setAttribute("visibility", "visible");
      var d = rowsAt(i);
      if (px === undefined) { var r = svg.getBoundingClientRect(); px = r.left + window.scrollX + X / self.W * r.width; py = r.top + window.scrollY + self.pad.t / self.H * r.height; }
      tipShow(px, py, d.title, d.rows);
    }
    function off() { line.setAttribute("visibility", "hidden"); tipHide(); }
    hit.addEventListener("pointermove", function (e) {
      var p = svgPoint(svg, e), best = 0, bd = Infinity;
      for (var i = 0; i < xs.length; i++) { var dd = Math.abs(self.tx(xs[i]) - p.x); if (dd < bd) { bd = dd; best = i; } }
      at(best, e.pageX, e.pageY);
    });
    hit.addEventListener("pointerleave", off);
    hit.addEventListener("focus", function () { at(cur < 0 ? Math.floor(xs.length / 2) : cur); });
    hit.addEventListener("blur", off);
    hit.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { at(Math.max(0, cur - 1)); e.preventDefault(); }
      if (e.key === "ArrowRight") { at(Math.min(xs.length - 1, cur + 1)); e.preventDefault(); }
    });
    return hit;
  };

  function svgPoint(svg, evt) {
    var r = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal;
    return { x: (evt.clientX - r.left) / r.width * vb.width, y: (evt.clientY - r.top) / r.height * vb.height };
  }

  /* ---------------- tooltip (it enhances: every value is also in the read-out or the table view) ---------------- */
  var tipEl = null;
  function tipShow(pageX, pageY, title, rows) { // rows: [[cssVar | null, label, value], ...]; value first, label after
    if (!tipEl) { tipEl = document.createElement("div"); tipEl.className = "viz-tip"; tipEl.setAttribute("role", "status"); document.body.appendChild(tipEl); }
    tipEl.textContent = "";
    if (title) { var h = document.createElement("div"); h.className = "viz-tip-h"; h.textContent = title; tipEl.appendChild(h); }
    rows.forEach(function (r) {
      var d = document.createElement("div"); d.className = "viz-tip-r";
      var k = document.createElement("i"); if (r[0]) k.style.background = "var(" + r[0] + ")"; d.appendChild(k);
      var v = document.createElement("b"); v.textContent = r[2]; d.appendChild(v);
      var l = document.createElement("span"); l.textContent = r[1]; d.appendChild(l);
      tipEl.appendChild(d);
    });
    tipEl.style.display = "block";
    var w = tipEl.offsetWidth, hgt = tipEl.offsetHeight;
    var left = pageX + 14, top = pageY + 14;
    if (left + w > window.scrollX + document.documentElement.clientWidth - 8) left = Math.max(window.scrollX + 8, pageX - w - 14);
    if (top + hgt > window.scrollY + window.innerHeight - 8) top = pageY - hgt - 10;
    tipEl.style.left = left + "px"; tipEl.style.top = top + "px";
  }
  function tipHide() { if (tipEl) tipEl.style.display = "none"; }
  // Makes an SVG node a hover and keyboard-focus target. info() returns { title, rows }; marks lift while pointed at.
  // noFocus = true: hover only (use it for a second target that repeats the information of a focusable one).
  function hoverable(node, info, marks, noFocus) {
    marks = marks || [];
    if (!noFocus) {
      node.setAttribute("tabindex", "0");
      var d0 = info();
      node.setAttribute("aria-label", (d0.title ? d0.title + ": " : "") + d0.rows.map(function (r) { return r[1] + " " + r[2]; }).join(", "));
    }
    function show(x, y) { var d = info(); tipShow(x, y, d.title, d.rows); marks.forEach(function (m) { m.classList.add("lift"); }); }
    function hide() { tipHide(); marks.forEach(function (m) { m.classList.remove("lift"); }); }
    node.addEventListener("pointerenter", function (e) { show(e.pageX, e.pageY); });
    node.addEventListener("pointermove", function (e) { show(e.pageX, e.pageY); });
    node.addEventListener("pointerleave", hide);
    node.addEventListener("focus", function () { var r = node.getBoundingClientRect(); show(r.left + r.width / 2 + window.scrollX, r.top + window.scrollY); });
    node.addEventListener("blur", hide);
    return node;
  }

  /* ---------------- building blocks of the widgets ---------------- */
  function scaffold(box, title) {
    var first = box.firstChild;
    if (title) { var h = document.createElement("p"); h.className = "w-title"; h.textContent = title; box.insertBefore(h, first); }
    var svg = el("svg", {});
    box.insertBefore(svg, first);
    var legend = document.createElement("div"); legend.className = "legend"; box.insertBefore(legend, first);
    var controls = document.createElement("div"); controls.className = "controls"; box.insertBefore(controls, first);
    var ns = box.querySelector(".w-noscript"); if (ns) ns.remove();
    return { svg: svg, controls: controls, legend: legend };
  }
  function slider(controls, label, min, max, step, value, onInput) {
    var lab = document.createElement("label");
    var span = document.createElement("span"); span.innerHTML = label;
    var inp = document.createElement("input");
    inp.type = "range"; inp.min = min; inp.max = max; inp.step = step; inp.value = value;
    var out = document.createElement("span"); out.className = "readout";
    lab.appendChild(span); lab.appendChild(inp); lab.appendChild(out);
    controls.appendChild(lab);
    inp.addEventListener("input", onInput);
    return { input: inp, out: out, get: function () { return parseFloat(inp.value); }, set: function (v) { inp.value = v; } };
  }
  function select(controls, label, options, value, onChange) {
    var lab = document.createElement("label");
    var span = document.createElement("span"); span.innerHTML = label;
    var sel = document.createElement("select");
    options.forEach(function (o) { var op = document.createElement("option"); op.value = o[0]; op.textContent = o[1]; sel.appendChild(op); });
    sel.value = value;
    lab.appendChild(span); lab.appendChild(sel); controls.appendChild(lab);
    sel.addEventListener("change", onChange);
    return sel;
  }
  function button(controls, label, onClick) {
    var b = document.createElement("button"); b.type = "button"; b.textContent = label;
    controls.appendChild(b); b.addEventListener("click", onClick); return b;
  }
  function checkbox(controls, label, checked, onChange) {
    var lab = document.createElement("label");
    var inp = document.createElement("input"); inp.type = "checkbox"; inp.checked = !!checked;
    var span = document.createElement("span"); span.innerHTML = label;
    lab.appendChild(inp); lab.appendChild(span); controls.appendChild(lab);
    inp.addEventListener("change", onChange);
    return inp;
  }
  function readout(controls) {
    var s = document.createElement("div"); s.className = "readout"; s.style.flexBasis = "100%";
    controls.appendChild(s); return s;
  }
  // Legend: items are [cssVar, label] (a line key), or [cssVar, label, kind] with kind "bar" (a square key, for bars
  // and areas), "dot" (a round marker) or "dash" (a dashed threshold line).
  function legend(box, items) {
    box.innerHTML = "";
    items.forEach(function (it) {
      var s = document.createElement("span"); s.style.setProperty("--lc", "var(" + it[0] + ")"); s.textContent = it[1];
      if (it[2] === "bar") s.className = "sq";
      if (it[2] === "dash") s.className = "dsh";
      if (it[2] === "dot") s.className = "dt";
      box.appendChild(s);
    });
  }
  // Table view of a chart: a folded table under the widget, refreshed by the returned function.
  function tableView(box, label) {
    var d = document.createElement("details"); d.className = "w-table";
    var s = document.createElement("summary"); s.textContent = label || "Show the numbers"; d.appendChild(s);
    var t = document.createElement("table"); d.appendChild(t);
    box.appendChild(d);
    return function (head, rows) {
      t.textContent = "";
      var tr = t.insertRow();
      head.forEach(function (h) { var th = document.createElement("th"); th.textContent = h; tr.appendChild(th); });
      rows.forEach(function (r) { var tr2 = t.insertRow(); r.forEach(function (c) { tr2.insertCell().textContent = c; }); });
    };
  }

  var WIDGETS = {};
  var redrawers = [];
  function redrawAll() { redrawers.forEach(function (f) { f(); }); }

  /* ======================================================================
     Shared helpers for the interactive figures of all the pages
     ====================================================================== */

  /* ---------------- small utilities ---------------- */
  // Small fractions for the worked examples (1/8, 3/8…), decimals otherwise.
  function frac(x) {
    if (Math.abs(x) < 1e-12) return "0";
    for (var q = 1; q <= 64; q++) {
      var p = Math.round(x * q);
      if (Math.abs(p / q - x) < 1e-9) return q === 1 ? String(p) : p + "/" + q;
    }
    return fmt(x, 3);
  }
  // Deterministic pseudo-random numbers, so that "random" examples can be reproduced.
  function mulberry32(a) {
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      var t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function gaussRand(rng) { var u = 1 - rng(), v = rng(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  function addSvg(box, after) {
    var svg = el("svg", {});
    after.parentNode.insertBefore(svg, after.nextSibling);
    return svg;
  }

  /* ---------------- probability vectors on a small vocabulary ---------------- */
  function normalize(a) { var s = 0, i; for (i = 0; i < a.length; i++) s += a[i]; return a.map(function (v) { return s > 0 ? v / s : 1 / a.length; }); }
  function overlap(p, q) { var s = 0; for (var i = 0; i < p.length; i++) s += Math.min(p[i], q[i]); return s; } // = 1 - TV(p, q)
  function tvDist(p, q) { var s = 0; for (var i = 0; i < p.length; i++) s += Math.abs(p[i] - q[i]); return s / 2; }
  function klDiv(p, q) { // natural logarithm; infinite when q = 0 < p
    var s = 0;
    for (var i = 0; i < p.length; i++) if (p[i] > 0) s += q[i] > 0 ? p[i] * Math.log(p[i] / q[i]) : Infinity;
    return s;
  }
  function jsDiv(p, q) { var m = p.map(function (v, i) { return (v + q[i]) / 2; }); return 0.5 * klDiv(p, m) + 0.5 * klDiv(q, m); }
  function entropy(p) { var s = 0; for (var i = 0; i < p.length; i++) if (p[i] > 0) s -= p[i] * Math.log(p[i]); return s; }
  function argmaxIndex(p) { var b = 0; for (var i = 1; i < p.length; i++) if (p[i] > p[b]) b = i; return b; }
  function sampleIndex(p, rng) { var u = rng(), c = 0; for (var i = 0; i < p.length; i++) { c += p[i]; if (u < c) return i; } return p.length - 1; }
  // The residual distribution of exact speculative sampling: norm(max(0, p - q)); null when p = q.
  function residual(p, q) {
    var r = p.map(function (v, i) { return Math.max(0, v - q[i]); }), s = 0;
    r.forEach(function (v) { s += v; });
    return s > 1e-12 ? r.map(function (v) { return v / s; }) : null;
  }
  // Sets entry i of a probability vector to v and rescales the other entries so that the total stays 1.
  function setBar(dist, i, v) {
    v = Math.min(0.97, Math.max(0.005, v));
    var rest = 1 - dist[i], out = dist.slice();
    for (var k = 0; k < dist.length; k++) out[k] = k === i ? v : (rest > 1e-9 ? dist[k] * (1 - v) / rest : (1 - v) / (dist.length - 1));
    return out;
  }
  // Lets the reader reshape distributions by dragging the tops of their bars. targets() returns the current
  // draggable columns as [{ x: pixel centre, w: pixel width, s: series index, i: category index }]; onSet(s, i, value)
  // is called with the value under the pointer (data units). The dragged columns need the class "drag" (touch).
  function dragBars(svg, plot, targets, onSet) {
    var active = null;
    function pick(e) {
      var p = svgPoint(svg, e), best = null, bd = Infinity;
      targets().forEach(function (t) { var d = Math.abs(p.x - t.x); if (d < bd && d <= Math.max(t.w / 2 + 3, 9)) { bd = d; best = t; } });
      return { t: best, p: p };
    }
    function apply(e) { var p = svgPoint(svg, e); onSet(active.s, active.i, plot.iy(p.y)); }
    svg.addEventListener("pointerdown", function (e) {
      var k = pick(e);
      if (!k.t || k.p.y < plot.pad.t - 6 || k.p.y > plot.H - plot.pad.b + 6) return;
      active = k.t; e.preventDefault();
      try { svg.setPointerCapture(e.pointerId); } catch (err) {}
      apply(e);
    });
    svg.addEventListener("pointermove", function (e) { if (active) { e.preventDefault(); apply(e); } });
    function end() { active = null; }
    svg.addEventListener("pointerup", end);
    svg.addEventListener("pointercancel", end);
  }

  /* ======================================================================
     Widgets of the page (widgets/<page>.js, inserted here by build.mjs)
     ====================================================================== */
  /* @@PAGE_WIDGETS@@ */

  document.querySelectorAll("[data-widget]").forEach(function (box) {
    var f = WIDGETS[box.getAttribute("data-widget")];
    if (f) { try { f(box); } catch (e) { box.insertAdjacentHTML("afterbegin", "<p class='small muted'>Figure unavailable: " + e.message + "</p>"); } }
  });
})();
