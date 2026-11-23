// app.js — theme, folds, active table of contents and interactive figures of the Rabbit Hull study guide.
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
      try { localStorage.setItem("rh-guide-theme", t); } catch (err) {}
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
  Plot.prototype.axes = function (opt) {
    opt = opt || {};
    var o = this.o, g = el("g", {}, this.g), self = this;
    var xt = opt.xticks || [], yt = opt.yticks || [];
    xt.forEach(function (v) {
      var X = self.tx(v);
      if (!opt.nogrid) el("line", { x1: X, x2: X, y1: self.pad.t, y2: self.H - self.pad.b, "class": "gr" }, g);
      var t = el("text", { x: X, y: self.H - self.pad.b + 16, "text-anchor": "middle", "class": "tx" }, g);
      t.textContent = opt.xfmt ? opt.xfmt(v) : fmt(v, opt.xd || 0);
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
    if (opt.ylabel) { var b = el("text", { x: this.tx(x0) + 6, y: Math.max(12, this.pad.t - 10), "class": "tx" }, g); b.textContent = opt.ylabel; }
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
  Plot.prototype.dot = function (x, y, r, cls) { return el("circle", { cx: this.tx(x), cy: this.ty(y), r: r || 4, "class": cls }, this.g); };
  Plot.prototype.seg = function (x1, y1, x2, y2, cls, extra) {
    var a = { x1: this.tx(x1), y1: this.ty(y1), x2: this.tx(x2), y2: this.ty(y2), "class": cls };
    for (var k in extra || {}) a[k] = extra[k];
    return el("line", a, this.g);
  };
  Plot.prototype.text = function (x, y, s, cls, anchor, dx, dy) {
    var t = el("text", { x: this.tx(x) + (dx || 0), y: this.ty(y) + (dy || 0), "class": cls || "tx", "text-anchor": anchor || "start" }, this.g);
    t.textContent = s; return t;
  };
  Plot.prototype.clip = function () {
    var id = "clip" + Math.random().toString(36).slice(2);
    var cp = el("clipPath", { id: id }, this.svg);
    el("rect", { x: this.pad.l, y: this.pad.t, width: this.W - this.pad.l - this.pad.r, height: this.H - this.pad.t - this.pad.b }, cp);
    this.g = el("g", { "clip-path": "url(#" + id + ")" }, this.svg);
  };
  Plot.prototype.unclip = function () { this.g = el("g", {}, this.svg); };

  function svgPoint(svg, evt) {
    var r = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal;
    return { x: (evt.clientX - r.left) / r.width * vb.width, y: (evt.clientY - r.top) / r.height * vb.height };
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
  function legend(box, items) {
    box.innerHTML = "";
    items.forEach(function (it) {
      var s = document.createElement("span"); s.style.setProperty("--lc", "var(" + it[0] + ")"); s.textContent = it[1]; box.appendChild(s);
    });
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
  function matStr(M) { return "[" + M.map(function (r) { return "[" + r.map(frac).join(", ") + "]"; }).join(", ") + "]"; }
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

  /* ---------------- planar convex geometry ---------------- */
  // Convex hull of 2-D points (Andrew's monotone chain): counter-clockwise, first point not repeated.
  function convexHull(pts) {
    var p = pts.slice().sort(function (u, v) { return u[0] - v[0] || u[1] - v[1]; });
    if (p.length < 3) return p;
    function cross(o, a, b) { return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]); }
    var lo = [], up = [], i;
    for (i = 0; i < p.length; i++) { while (lo.length >= 2 && cross(lo[lo.length - 2], lo[lo.length - 1], p[i]) <= 1e-12) lo.pop(); lo.push(p[i]); }
    for (i = p.length - 1; i >= 0; i--) { while (up.length >= 2 && cross(up[up.length - 2], up[up.length - 1], p[i]) <= 1e-12) up.pop(); up.push(p[i]); }
    lo.pop(); up.pop();
    return lo.concat(up);
  }
  // Minkowski sum of two convex polygons given by their vertices: the hull of all pairwise sums.
  function minkowskiSum(A, B) {
    var s = [];
    A.forEach(function (a) { B.forEach(function (b) { s.push([a[0] + b[0], a[1] + b[1]]); }); });
    return convexHull(s);
  }
  function polyArea(P) { var s = 0; for (var i = 0; i < P.length; i++) { var q = P[(i + 1) % P.length]; s += P[i][0] * q[1] - q[0] * P[i][1]; } return s / 2; }
  function pointInConvex(P, q) { // P counter-clockwise
    for (var i = 0; i < P.length; i++) {
      var a = P[i], b = P[(i + 1) % P.length];
      if ((b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]) < -1e-9) return false;
    }
    return true;
  }
  function supportFn(P, u) { var m = -Infinity; P.forEach(function (p) { m = Math.max(m, p[0] * u[0] + p[1] * u[1]); }); return m; }
  // softmax(x / tau), computed stably.
  function softmaxT(x, tau) {
    var m = Math.max.apply(null, x), e = x.map(function (v) { return Math.exp((v - m) / tau); }), s = 0;
    e.forEach(function (v) { s += v; });
    return e.map(function (v) { return v / s; });
  }
  // Convex (or any linear) combination sum_j w_j V_j of 2-D points.
  function combo(V, w) { var x = 0, y = 0; V.forEach(function (v, j) { x += w[j] * v[0]; y += w[j] * v[1]; }); return [x, y]; }
  // Points that can be dragged in a Plot. pts: array of [x, y] (mutated); onMove(i) is called after each move.
  // opts.clamp(i, x, y) may return the corrected position. Returns { active } with the index being dragged.
  function draggable(plot, pts, onMove, opts) {
    opts = opts || {};
    var svg = plot.svg, st = { active: -1 };
    function pick(e) {
      var p = svgPoint(svg, e), best = -1, bd = (opts.radius || 22);
      pts.forEach(function (q, i) {
        if (opts.fixed && opts.fixed(i)) return;
        var dx = plot.tx(q[0]) - p.x, dy = plot.ty(q[1]) - p.y, dd = Math.sqrt(dx * dx + dy * dy);
        if (dd < bd) { bd = dd; best = i; }
      });
      return best;
    }
    function move(e) {
      var p = svgPoint(svg, e), x = plot.ix(p.x), y = plot.iy(p.y);
      x = Math.min(Math.max(x, plot.o.x[0]), plot.o.x[1]); y = Math.min(Math.max(y, plot.o.y[0]), plot.o.y[1]);
      var q = opts.clamp ? opts.clamp(st.active, x, y) : [x, y];
      pts[st.active][0] = q[0]; pts[st.active][1] = q[1];
      onMove(st.active);
    }
    svg.addEventListener("pointerdown", function (e) {
      var i = pick(e); if (i < 0) return;
      st.active = i; e.preventDefault();
      try { svg.setPointerCapture(e.pointerId); } catch (err) {}
      move(e);
    });
    svg.addEventListener("pointermove", function (e) { if (st.active >= 0) { e.preventDefault(); move(e); } });
    function end() { st.active = -1; }
    svg.addEventListener("pointerup", end); svg.addEventListener("pointercancel", end);
    return st;
  }

  /* ---------------- 2 x 2 symmetric matrices, stored row-major [a, b, c, d] ---------------- */
  function mmul(A, B) { return [A[0] * B[0] + A[1] * B[2], A[0] * B[1] + A[1] * B[3], A[2] * B[0] + A[3] * B[2], A[2] * B[1] + A[3] * B[3]]; }
  function msym(A) { var o = (A[1] + A[2]) / 2; return [A[0], o, o, A[3]]; }
  function msqrt(A) { // square root of a symmetric positive semi-definite 2 x 2 matrix: (A + sI) / sqrt(tr A + 2s), s = sqrt(det A)
    var s = Math.sqrt(Math.max(A[0] * A[3] - A[1] * A[2], 0)), t = Math.sqrt(A[0] + A[3] + 2 * s);
    return [(A[0] + s) / t, A[1] / t, A[2] / t, (A[3] + s) / t];
  }
  function minv(A) { var det = A[0] * A[3] - A[1] * A[2]; return [A[3] / det, -A[1] / det, -A[2] / det, A[0] / det]; }
  function ellipsePts(m, S, scale) {
    var r = msqrt(S), pts = [];
    for (var i = 0; i <= 96; i++) {
      var a = 2 * Math.PI * i / 96, c = Math.cos(a) * scale, d = Math.sin(a) * scale;
      pts.push([m[0] + r[0] * c + r[1] * d, m[1] + r[2] * c + r[3] * d]);
    }
    return pts;
  }

  /* ---------------- a triangle to choose three weights by dragging a dot ---------------- */
  function WeightTriangle(svg, box, names, onChange) { // box = [x0, y0, w, h] in viewBox units
    this.V = [[box[0], box[1] + box[3]], [box[0] + box[2], box[1] + box[3]], [box[0] + box[2] / 2, box[1]]];
    this.lam = [1 / 3, 1 / 3, 1 / 3]; this.names = names; this.svg = svg;
    var self = this, dragging = false;
    function update(e) {
      var p = svgPoint(svg, e), V = self.V;
      var det = (V[1][1] - V[2][1]) * (V[0][0] - V[2][0]) + (V[2][0] - V[1][0]) * (V[0][1] - V[2][1]);
      var l1 = ((V[1][1] - V[2][1]) * (p.x - V[2][0]) + (V[2][0] - V[1][0]) * (p.y - V[2][1])) / det;
      var l2 = ((V[2][1] - V[0][1]) * (p.x - V[2][0]) + (V[0][0] - V[2][0]) * (p.y - V[2][1])) / det;
      var l = [Math.max(l1, 0), Math.max(l2, 0), Math.max(1 - l1 - l2, 0)], s = l[0] + l[1] + l[2];
      self.lam = [l[0] / s, l[1] / s, l[2] / s];
      onChange();
    }
    function inside(e) {
      var p = svgPoint(svg, e), V = self.V;
      return p.x > V[0][0] - 20 && p.x < V[1][0] + 20 && p.y > V[2][1] - 20 && p.y < V[0][1] + 20;
    }
    svg.addEventListener("pointerdown", function (e) {
      if (!inside(e)) return;
      dragging = true; e.preventDefault();
      try { svg.setPointerCapture(e.pointerId); } catch (err) {}
      update(e);
    });
    svg.addEventListener("pointermove", function (e) { if (dragging) { e.preventDefault(); update(e); } });
    svg.addEventListener("pointerup", function () { dragging = false; });
    svg.addEventListener("pointercancel", function () { dragging = false; });
  }
  WeightTriangle.prototype.draw = function (g) {
    var V = this.V, lam = this.lam, self = this;
    el("path", { d: "M" + V[0].join(" ") + "L" + V[1].join(" ") + "L" + V[2].join(" ") + "Z", "class": "am ln cm thin" }, g);
    var pos = [lam[0] * V[0][0] + lam[1] * V[1][0] + lam[2] * V[2][0], lam[0] * V[0][1] + lam[1] * V[1][1] + lam[2] * V[2][1]];
    V.forEach(function (v, k) {
      el("circle", { cx: v[0], cy: v[1], r: 5, "class": "f1" }, g);
      var t = el("text", { x: v[0], y: v[1] + (k === 2 ? -9 : 17), "class": "tx-s", "text-anchor": "middle" }, g);
      t.textContent = self.names[k] + ": " + fmt(lam[k], 2);
    });
    el("circle", { cx: pos[0], cy: pos[1], r: 8, "class": "f3 drag" }, g);
    var cap = el("text", { x: (V[0][0] + V[1][0]) / 2, y: V[0][1] + 34, "class": "tx-s", "text-anchor": "middle" }, g);
    cap.textContent = "drag the dot: weights λ₁, λ₂, λ₃";
  };

  /* ======================================================================
     Widgets of the page (widgets/<page>.js, inserted here by build.mjs)
     ====================================================================== */
  /* @@PAGE_WIDGETS@@ */

  document.querySelectorAll("[data-widget]").forEach(function (box) {
    var f = WIDGETS[box.getAttribute("data-widget")];
    if (f) { try { f(box); } catch (e) { box.insertAdjacentHTML("afterbegin", "<p class='small muted'>Figure unavailable: " + e.message + "</p>"); } }
  });
})();
