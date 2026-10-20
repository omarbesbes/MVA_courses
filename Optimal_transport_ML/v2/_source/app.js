// app.js — theme, folds, active table of contents and interactive figures of Optimal_transport_ML v2.
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
      try { localStorage.setItem("ot-v2-theme", t); } catch (err) {}
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
    if (!isFinite(x)) return "∞";
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
     Interactive figures of the course pages
     ====================================================================== */

  /* ---------------- shared helpers ---------------- */
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
  // North-west corner rule on sorted points = the monotone plan, optimal on the line for |x - y|^p, p >= 1.
  function monotonePlan(a, b) {
    var n = a.length, m = b.length, P = [], i, j;
    for (i = 0; i < n; i++) { P.push([]); for (j = 0; j < m; j++) P[i].push(0); }
    var ra = a.slice(), rb = b.slice();
    i = 0; j = 0;
    while (i < n && j < m) {
      var t = Math.min(ra[i], rb[j]);
      P[i][j] += t; ra[i] -= t; rb[j] -= t;
      if (ra[i] <= 1e-12) i++; else j++;
    }
    return P;
  }
  function planCost(P, xs, ys, p) {
    var s = 0;
    for (var i = 0; i < P.length; i++) for (var j = 0; j < P[i].length; j++) s += P[i][j] * Math.pow(Math.abs(xs[i] - ys[j]), p);
    return s;
  }
  function addSvg(box, after) {
    var svg = el("svg", {});
    after.parentNode.insertBefore(svg, after.nextSibling);
    return svg;
  }

  /* --- 1. Gluing two plans through the middle measure (§2) --- */
  WIDGETS.gluing = function (box) {
    var s = scaffold(box, "Gluing two optimal plans: the mass at each point of β leaves in the proportions of the second plan");
    var W = 680, H = 340, yA = 52, yB = 170, yC = 284;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Three rows of weighted points (alpha, beta, gamma) and the transport plans between them");
    var EX = { x: [0, 2], a: [1 / 2, 1 / 2], y: [0, 1, 2], b: [1 / 4, 1 / 2, 1 / 4], z: [1, 3], c: [1 / 2, 1 / 2] };
    var data = EX, hover = -1, seed = 1, X = null;
    var modeSel = select(s.controls, "Show", [["paths", "glued paths x → y → z"], ["plans", "the two optimal plans"], ["glued", "glued plan vs optimal plan α → γ"]], "paths", draw);
    var pSel = select(s.controls, "p =", [["1", "1"], ["2", "2"], ["3", "3"]], "2", draw);
    button(s.controls, "Worked example", function () { data = EX; hover = -1; draw(); });
    button(s.controls, "Random histograms", function () { data = randomData(); hover = -1; draw(); });
    var ro = readout(s.controls);
    var SRC = ["c2", "c4", "c6", "c3", "c5"];

    function randomData() {
      var rng = mulberry32(1000 + 7919 * seed++);
      function hist(nmin, nmax) {
        var n = nmin + Math.floor(rng() * (nmax - nmin + 1)), all = [0, 1, 2, 3, 4, 5, 6], w = [], tot = 0, i;
        for (i = all.length - 1; i > 0; i--) { var j = Math.floor(rng() * (i + 1)), t = all[i]; all[i] = all[j]; all[j] = t; }
        var pos = all.slice(0, n).sort(function (u, v) { return u - v; });
        for (i = 0; i < n; i++) { w.push(1 + Math.floor(rng() * 4)); tot += w[i]; }
        return { pos: pos, w: w.map(function (v) { return v / tot; }) };
      }
      var A = hist(2, 3), B = hist(2, 4), C = hist(2, 3);
      return { x: A.pos, a: A.w, y: B.pos, b: B.w, z: C.pos, c: C.w };
    }
    function nearestB(e) {
      if (!X) return -1;
      var pt = svgPoint(s.svg, e), best = -1, bd = 26;
      data.y.forEach(function (v, j) { var d = Math.hypot(pt.x - X(v), pt.y - yB); if (d < bd) { bd = d; best = j; } });
      return best;
    }
    s.svg.addEventListener("pointermove", function (e) {
      if (e.pointerType !== "mouse") return;
      var j = nearestB(e);
      if (j !== hover && (j >= 0 || hover >= 0)) { hover = j; draw(); }
    });
    s.svg.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "mouse") return;
      var j = nearestB(e); hover = j === hover ? -1 : j; draw();
    });

    function draw() {
      var p = parseFloat(pSel.value), mode = modeSel.value, i, j, k;
      var nx = data.x.length, ny = data.y.length, nz = data.z.length;
      var all = data.x.concat(data.y, data.z), lo = Math.min.apply(null, all) - 0.6, hi = Math.max.apply(null, all) + 0.6;
      X = function (v) { return 70 + (v - lo) / (hi - lo) * (W - 100); };
      var P = monotonePlan(data.a, data.b), Q = monotonePlan(data.b, data.c), O = monotonePlan(data.a, data.c);
      var S = [], R = [];
      for (i = 0; i < nx; i++) {
        S.push([]); R.push([]);
        for (k = 0; k < nz; k++) R[i].push(0);
        for (j = 0; j < ny; j++) {
          S[i].push([]);
          for (k = 0; k < nz; k++) {
            var v = data.b[j] > 1e-12 ? P[i][j] * Q[j][k] / data.b[j] : 0;
            S[i][j].push(v); R[i][k] += v;
          }
        }
      }
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg);
      [yA, yB, yC].forEach(function (yy) { el("line", { x1: X(lo), x2: X(hi), y1: yy, y2: yy, "class": "gr" }, g); });
      for (var t = Math.ceil(lo); t <= hi; t++) {
        el("line", { x1: X(t), x2: X(t), y1: yC + 26, y2: yC + 34, "class": "ax" }, g);
        var tt = el("text", { x: X(t), y: H - 6, "class": "tx-s", "text-anchor": "middle" }, g); tt.textContent = t;
      }
      el("line", { x1: X(lo), x2: X(hi), y1: yC + 30, y2: yC + 30, "class": "ax" }, g);
      [["α", yA, "t2"], ["β", yB, "t1"], ["γ", yC, "t5"]].forEach(function (r) {
        var tx = el("text", { x: 22, y: r[1] + 5, "class": "tx-i" }, g); tx.textContent = r[0];
        tx.setAttribute("style", "fill: var(--" + { t2: "s2", t1: "s1", t5: "s5" }[r[2]] + ")");
      });
      function wid(m) { return (1.2 + 22 * m).toFixed(2); }
      if (mode === "plans") {
        for (i = 0; i < nx; i++) for (j = 0; j < ny; j++) if (P[i][j] > 1e-12)
          el("line", { x1: X(data.x[i]), y1: yA, x2: X(data.y[j]), y2: yB, "class": "ln c2", "stroke-width": wid(P[i][j]), "stroke-opacity": hover < 0 || j === hover ? 0.6 : 0.12 }, g);
        for (j = 0; j < ny; j++) for (k = 0; k < nz; k++) if (Q[j][k] > 1e-12)
          el("line", { x1: X(data.y[j]), y1: yB, x2: X(data.z[k]), y2: yC, "class": "ln c1", "stroke-width": wid(Q[j][k]), "stroke-opacity": hover < 0 || j === hover ? 0.6 : 0.12 }, g);
      } else if (mode === "paths") {
        for (i = 0; i < nx; i++) for (j = 0; j < ny; j++) for (k = 0; k < nz; k++) if (S[i][j][k] > 1e-12) {
          var off = (k - (nz - 1) / 2) * 4 + (i - (nx - 1) / 2) * 4;
          var d = "M" + X(data.x[i]).toFixed(1) + " " + yA + " L" + (X(data.y[j]) + off).toFixed(1) + " " + yB + " L" + X(data.z[k]).toFixed(1) + " " + yC;
          el("path", { d: d, "class": "ln " + SRC[i % SRC.length], "stroke-width": wid(S[i][j][k]), "stroke-opacity": hover < 0 ? 0.55 : (j === hover ? 0.9 : 0.07) }, g);
        }
      } else {
        for (i = 0; i < nx; i++) for (k = 0; k < nz; k++) {
          if (O[i][k] > 1e-12) el("line", { x1: X(data.x[i]), y1: yA, x2: X(data.z[k]), y2: yC, "class": "ln cm dash", "stroke-width": wid(O[i][k]), "stroke-opacity": 0.7 }, g);
          if (R[i][k] > 1e-12) el("line", { x1: X(data.x[i]) + 3, y1: yA, x2: X(data.z[k]) + 3, y2: yC, "class": "ln c3", "stroke-width": wid(R[i][k]), "stroke-opacity": 0.55 }, g);
        }
      }
      function row(xs, ws, yy, fcls, where, faded) {
        xs.forEach(function (v, i) {
          var r = 4 + 13 * Math.sqrt(ws[i]);
          el("circle", { cx: X(v), cy: yy, r: r.toFixed(1), "class": fcls, "fill-opacity": faded ? 0.3 : 0.92 }, g);
          var lab = el("text", { "class": "tx-s", "text-anchor": where === "right" ? "start" : "middle" }, g);
          if (where === "above") { lab.setAttribute("x", X(v)); lab.setAttribute("y", yy - r - 6); }
          else if (where === "below") { lab.setAttribute("x", X(v)); lab.setAttribute("y", yy + r + 13); }
          else { lab.setAttribute("x", X(v) + r + 4); lab.setAttribute("y", yy - r - 2); }
          lab.textContent = frac(ws[i]);
        });
      }
      row(data.x, data.a, yA, "f2", "above");
      row(data.y, data.b, yB, "f1", "right", mode === "glued");
      row(data.z, data.c, yC, "f5", "below");
      if (hover >= 0 && mode !== "glued") el("circle", { cx: X(data.y[hover]), cy: yB, r: (8 + 13 * Math.sqrt(data.b[hover])).toFixed(1), "class": "ln ck thin nofill" }, g);

      var wac = Math.pow(planCost(O, data.x, data.z, p), 1 / p), wg = Math.pow(planCost(R, data.x, data.z, p), 1 / p);
      var wab = Math.pow(planCost(P, data.x, data.y, p), 1 / p), wbc = Math.pow(planCost(Q, data.y, data.z, p), 1 / p);
      var txt = "p = " + p + ":  W_p(α,γ) = " + fmt(wac, 4) + "  ≤  glued plan " + fmt(wg, 4) +
        "  ≤  W_p(α,β) + W_p(β,γ) = " + fmt(wab, 4) + " + " + fmt(wbc, 4) + " = " + fmt(wab + wbc, 4);
      if (mode === "glued") {
        txt += "\nglued plan (rows α, columns γ) = " + matStr(R) + "     optimal plan = " + matStr(O);
      } else if (hover >= 0) {
        j = hover;
        txt += "\nThrough y = " + data.y[j] + " (mass b = " + frac(data.b[j]) + "):";
        for (i = 0; i < nx; i++) for (k = 0; k < nz; k++) if (S[i][j][k] > 1e-12)
          txt += "\n   path " + data.x[i] + " → " + data.y[j] + " → " + data.z[k] + ":  S = π_αβ × π_βγ / b = (" + frac(P[i][j]) + ") × (" + frac(Q[j][k]) + ") / (" + frac(data.b[j]) + ") = " + frac(S[i][j][k]);
      } else {
        txt += "\nHover (or tap) a point of β to see how the mass arriving there is split.";
      }
      ro.textContent = txt;
    }
    draw(); redrawers.push(draw);
  };

  /* --- 2. Three weakly convergent sequences: TV, W1, W2 (§5) --- */
  WIDGETS.zoo = function (box) {
    var s = scaffold(box, "Three sequences that converge weakly: what total variation, W₁ and W₂ say");
    var top = new Plot(s.svg, { x: [0, 1], y: [0, 1.3], w: 680, h: 210, pad: { l: 40, r: 20, t: 14, b: 28 }, label: "The measure alpha_n and its limit" });
    var botSvg = addSvg(box, s.svg);
    var bot = new Plot(botSvg, { x: [1, 1000], y: [1e-4, 3000], xlog: true, ylog: true, w: 680, h: 250, pad: { l: 52, r: 20, t: 16, b: 34 }, label: "TV, W1 and W2 as functions of n, log-log" });
    var seqSel = select(s.controls, "Sequence", [["dirac", "moving Dirac δ(1/n) → δ₀"], ["riemann", "Riemann sums → 𝒰[0,1]"], ["escape", "escaping mass → δ₀ (on ℝ)"]], "dirac", draw);
    var nS = slider(s.controls, "n", 0, 3, 0.005, 1, draw);
    var gS = slider(s.controls, "far atom at x = n^γ, γ =", 0, 1.5, 0.05, 1, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "αₙ (top)"], ["--s1", "limit α (top)"], ["--muted", "‖αₙ − α‖_TV"], ["--s4", "W₁(αₙ, α)"], ["--s5", "W₂(αₙ, α)"]]);
    function vals(seq, n, gam) {
      if (seq === "dirac") return { tv: 2, w1: 1 / n, w2: 1 / n };
      if (seq === "riemann") return { tv: 2, w1: 1 / (2 * n), w2: 1 / (Math.sqrt(3) * n) };
      return { tv: 2 / n, w1: Math.pow(n, gam - 1), w2: Math.pow(n, gam - 0.5) };
    }
    function sup(e) { var m = { "-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴" }; return "10" + String(e).split("").map(function (c) { return m[c]; }).join(""); }
    function draw() {
      var seq = seqSel.value, n = Math.max(1, Math.round(Math.pow(10, nS.get()))), gam = gS.get();
      nS.out.textContent = String(n); gS.out.textContent = fmt(gam, 2);
      gS.input.parentNode.style.display = seq === "escape" ? "" : "none";
      var v = vals(seq, n, gam), i;
      // top panel: the measures
      if (seq === "dirac") { top.o.x = [-0.1, 1.1]; top.o.y = [0, 1.3]; }
      else if (seq === "riemann") { top.o.x = [-0.05, 1.05]; top.o.y = [0, 1.3]; }
      else { top.o.x = [-0.5, 10.5]; top.o.y = [0, 1.3]; }
      top.clear();
      var ticks = seq === "escape" ? [0, 2, 4, 6, 8, 10] : [0, 0.25, 0.5, 0.75, 1];
      top.axes({ xticks: ticks, yticks: [], xfmt: function (t) { return fmt(t, seq === "escape" ? 0 : 2); }, noyaxis: true, nogrid: true });
      if (seq === "dirac") {
        top.seg(0, 0, 0, 1, "ln c1"); top.dot(0, 1, 6, "f1");
        top.seg(1 / n, 0, 1 / n, 1, "ln c2"); top.dot(1 / n, 1, 5, "f2");
        top.text(1 / n, 1, "δ(1/n)", "tx-s", "start", 8, -6);
      } else if (seq === "riemann") {
        top.poly([[0, 0], [0, 1], [1, 1], [1, 0]], "a1");
        top.poly([[0, 0], [0, 1], [1, 1], [1, 0]], "ln c1 thin");
        var op = n > 200 ? 0.35 : 0.9;
        for (i = 1; i <= n; i++) top.seg(i / n, 0, i / n, 0.8, "ln c2 " + (n > 60 ? "hair" : "thin"), { "stroke-opacity": op });
        if (n <= 60) for (i = 1; i <= n; i++) top.dot(i / n, 0.8, 3, "f2");
        top.text(0.5, 1, "density of 𝒰[0,1]", "tx-s", "middle", 0, -6);
        top.text(0.02, 0.8, "atoms k/n of mass 1/n each", "tx-s", "start", 0, -8);
      } else {
        var far = Math.pow(n, gam), small = Math.max(1 / n, 0.04);
        top.seg(0, 0, 0, 1, "ln c1"); top.dot(0, 1, 6, "f1");
        top.seg(0.12, 0, 0.12, 1 - 1 / n, "ln c2"); top.dot(0.12, 1 - 1 / n, 5, "f2");
        top.text(0.12, 1 - 1 / n, "mass 1 − 1/n", "tx-s", "start", 8, 4);
        var xf = far <= 10.2 ? far : 10.2;
        top.seg(xf, 0, xf, small, "ln c2"); top.dot(xf, small, 5, "f2");
        top.text(xf, small, far <= 10.2 ? "mass 1/n at x = " + fmt(far, 2) : "mass 1/n at x = " + fmt(far, 1) + " →", "tx-s", "end", -8, -6);
      }
      // bottom panel: the three distances against n
      bot.clear();
      bot.axes({ xticks: [1, 10, 100, 1000], yticks: [1e-4, 1e-3, 1e-2, 0.1, 1, 10, 100, 1000], xfmt: function (t) { return String(t); }, yfmt: function (t) { return sup(Math.round(Math.log10(t))); }, xlabel: "n" });
      bot.clip();
      bot.fn(function (m) { return vals(seq, m, gam).tv; }, "ln cm", 200);
      bot.fn(function (m) { return vals(seq, m, gam).w1; }, "ln c4", 200);
      bot.fn(function (m) { return vals(seq, m, gam).w2; }, "ln c5 dash", 200);
      bot.unclip();
      bot.dot(n, v.tv, 5, "fm"); bot.dot(n, v.w1, 5, "f4"); bot.dot(n, v.w2, 4, "f5");
      var verdict;
      if (seq === "escape") {
        verdict = "TV → 0 always (strong convergence!), W₁ → 0 iff γ < 1, W₂ → 0 iff γ < 1/2. Here: W₁ " + (gam < 1 ? "→ 0" : "does not → 0") + ", W₂ " + (gam < 0.5 ? "→ 0" : "does not → 0") + ".";
      } else {
        verdict = "TV stays at 2: no strong convergence. W₁ and W₂ → 0 like 1/n: weak convergence, measured.";
      }
      ro.textContent = "n = " + n + "   ‖αₙ − α‖_TV = " + fmt(v.tv, 4) + "   W₁ = " + (v.w1 < 0.01 ? v.w1.toExponential(2) : fmt(v.w1, 4)) + "   W₂ = " + (v.w2 < 0.01 ? v.w2.toExponential(2) : fmt(v.w2, 4)) + "\n" + verdict;
    }
    draw(); redrawers.push(draw);
  };

  /* ---------------- measures on the line: densities on a grid, CDFs, quantile functions ---------------- */
  var SQ2PI = Math.sqrt(2 * Math.PI);
  function gpdf(x, m, sd) { var z = (x - m) / sd; return Math.exp(-0.5 * z * z) / (sd * SQ2PI); }
  function updf(x, a, b) { return x >= a && x <= b ? 1 / (b - a) : 0; }
  function Line1D(L, R, N, f) { // a probability density f on [L, R], tabulated on N points
    this.xs = new Float64Array(N); this.d = new Float64Array(N); this.c = new Float64Array(N);
    var i, h = (R - L) / (N - 1);
    for (i = 0; i < N; i++) { this.xs[i] = L + h * i; this.d[i] = f(this.xs[i]); }
    for (i = 1; i < N; i++) this.c[i] = this.c[i - 1] + 0.5 * (this.d[i] + this.d[i - 1]) * h;
    var tot = this.c[N - 1];
    for (i = 0; i < N; i++) { this.c[i] /= tot; this.d[i] /= tot; }
  }
  var MQ = 1200, US = new Float64Array(MQ);
  for (var iu = 0; iu < MQ; iu++) US[iu] = (iu + 0.5) / MQ;
  function quantiles(xs, c) { // generalized inverse of a tabulated CDF, at the levels US
    var q = new Float64Array(MQ), j = 0;
    for (var i = 0; i < MQ; i++) {
      var u = US[i];
      while (j < c.length - 2 && c[j + 1] < u) j++;
      var c0 = c[j], c1 = c[j + 1];
      q[i] = c1 > c0 ? xs[j] + (u - c0) / (c1 - c0) * (xs[j + 1] - xs[j]) : xs[j + 1];
    }
    return q;
  }
  function w2q(q1, q2) { var s = 0; for (var i = 0; i < MQ; i++) { var d = q1[i] - q2[i]; s += d * d; } return Math.sqrt(s / MQ); }
  // Density of the measure with quantile function q, drawn as the curve (q(u), 1/q'(u)).
  function densityFromQ(q) {
    var pts = [], k = 6;
    pts.push([q[0], 0]);
    for (var i = k; i < MQ - k; i += 2) {
      var dq = q[i + k] - q[i - k];
      pts.push([q[i], dq > 1e-12 ? (2 * k / MQ) / dq : NaN]);
    }
    pts.push([q[MQ - 1], 0]);
    return pts;
  }
  function curve(line) { var pts = []; for (var i = 0; i < line.xs.length; i += 2) pts.push([line.xs[i], line.d[i]]); return pts; }
  function areaPts(pts) { var p = pts.filter(function (v) { return isFinite(v[1]); }); return [[p[0][0], 0]].concat(p, [[p[p.length - 1][0], 0]]); }

  var PAIRS1D = {
    gauss: { label: "two Gaussians", L: -4.5, R: 5.5, ymax: 0.95,
      a: function (x) { return gpdf(x, -2, 0.5); }, b: function (x) { return gpdf(x, 2, 1); } },
    bumps: { label: "one bump → two bumps", L: -4, R: 5, ymax: 1.1,
      a: function (x) { return gpdf(x, -1.5, 0.6); }, b: function (x) { return 0.5 * gpdf(x, 1, 0.35) + 0.5 * gpdf(x, 3.2, 0.35); } },
    unif: { label: "two uniform laws", L: -0.5, R: 4.5, ymax: 1.25,
      a: function (x) { return updf(x, 0, 1); }, b: function (x) { return updf(x, 2, 4); } },
    twobumps: { label: "two bumps and one bump", L: -4, R: 4.8, ymax: 0.95,
      a: function (x) { return 0.5 * gpdf(x, -2.5, 0.35) + 0.5 * gpdf(x, -0.5, 0.35); }, b: function (x) { return gpdf(x, 2.5, 0.6); } }
  };
  function prep1D(key) {
    var P = PAIRS1D[key], N = 2401;
    var A = new Line1D(P.L, P.R, N, P.a), B = new Line1D(P.L, P.R, N, P.b);
    return { P: P, A: A, B: B, qa: quantiles(A.xs, A.c), qb: quantiles(B.xs, B.c) };
  }

  /* --- 3. Mixture versus displacement interpolation on the line (§6) --- */
  WIDGETS.interp = function (box) {
    var s = scaffold(box, "Mixture (grey) versus displacement interpolation (green), from α to β");
    var plot = new Plot(s.svg, { x: [-4.5, 5.5], y: [0, 1], w: 680, h: 300, pad: { l: 40, r: 16, t: 16, b: 30 }, label: "Densities of the mixture and of the displacement interpolation" });
    var pairSel = select(s.controls, "Pair", [["gauss", "two Gaussians"], ["bumps", "one bump → two bumps"], ["unif", "two uniform laws"]], "gauss", setup);
    var tS = slider(s.controls, "t", 0, 1, 0.01, 0.5, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "α (t = 0)"], ["--s1", "β (t = 1)"], ["--muted", "mixture (1 − t)α + tβ"], ["--s3", "displacement interpolation α_t"]]);
    var D;
    function setup() { D = prep1D(pairSel.value); draw(); }
    function draw() {
      var t = tS.get(), P = D.P, i;
      tS.out.textContent = fmt(t, 2);
      plot.o.x = [P.L, P.R]; plot.o.y = [0, P.ymax];
      plot.clear();
      var ticks = []; for (i = Math.ceil(P.L); i <= P.R; i++) ticks.push(i);
      plot.axes({ xticks: ticks, yticks: [], nogrid: true, noyaxis: true });
      plot.clip();
      var mix = [];
      for (i = 0; i < D.A.xs.length; i += 2) mix.push([D.A.xs[i], (1 - t) * D.A.d[i] + t * D.B.d[i]]);
      plot.poly(areaPts(mix), "am");
      plot.poly(mix, "ln cm");
      plot.poly(curve(D.A), "ln c2 thin dash");
      plot.poly(curve(D.B), "ln c1 thin dash");
      var qt = new Float64Array(MQ);
      for (i = 0; i < MQ; i++) qt[i] = (1 - t) * D.qa[i] + t * D.qb[i];
      var dens = densityFromQ(qt);
      plot.poly(areaPts(dens), "a3");
      plot.poly(dens, "ln c3");
      plot.unclip();
      // distances, all through quantile functions
      var wab = w2q(D.qa, D.qb), wdisp = w2q(D.qa, qt);
      var cm = new Float64Array(D.A.c.length);
      for (i = 0; i < cm.length; i++) cm[i] = (1 - t) * D.A.c[i] + t * D.B.c[i];
      var qm = quantiles(D.A.xs, cm), wmix = w2q(D.qa, qm);
      ro.textContent = "t = " + fmt(t, 2) + "    W₂(α, α_t) / W₂(α, β) = " + fmt(wdisp / wab, 3) + "  (= t: constant speed)" +
        "\n          W₂(α, mixture) / W₂(α, β) = " + fmt(wmix / wab, 3) + (t > 0 && t < 1 ? "  (≠ t: the mixture is not a geodesic)" : "");
    }
    setup(); redrawers.push(draw);
  };

  /* --- 4. Barycenter of two measures on the line: average the quantiles (§8) --- */
  WIDGETS.bary1d = function (box) {
    var s = scaffold(box, "Barycenter on the line: average the quantile functions");
    var top = new Plot(s.svg, { x: [-0.5, 4.5], y: [0, 1.2], w: 680, h: 240, pad: { l: 40, r: 16, t: 14, b: 28 }, label: "Densities of the inputs, the barycenter and the mixture" });
    var botSvg = addSvg(box, s.svg);
    var bot = new Plot(botSvg, { x: [-0.5, 4.5], y: [0, 1.05], w: 680, h: 230, pad: { l: 40, r: 16, t: 14, b: 30 }, label: "Cumulative distribution functions and horizontal averaging" });
    var pairSel = select(s.controls, "Inputs", [["unif", "𝒰[0,1] and 𝒰[2,4]"], ["gauss", "two Gaussians"], ["twobumps", "two bumps and one bump"]], "unif", setup);
    var lS = slider(s.controls, "weight λ of β₂", 0, 1, 0.01, 0.5, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "β₁"], ["--s5", "β₂"], ["--s3", "barycenter (weights 1 − λ, λ)"], ["--muted", "mixture (dashed)"]]);
    var D;
    function setup() { D = prep1D(pairSel.value); draw(); }
    function draw() {
      var lam = lS.get(), P = D.P, i;
      lS.out.textContent = fmt(lam, 2);
      var ticks = []; for (i = Math.ceil(P.L); i <= P.R; i++) ticks.push(i);
      // densities
      top.o.x = [P.L, P.R]; top.o.y = [0, P.ymax];
      top.clear();
      top.axes({ xticks: ticks, yticks: [], nogrid: true, noyaxis: true });
      top.clip();
      top.poly(areaPts(curve(D.A)), "a1"); top.poly(curve(D.A), "ln c1 thin");
      top.poly(areaPts(curve(D.B)), "a5"); top.poly(curve(D.B), "ln c5 thin");
      var mix = [];
      for (i = 0; i < D.A.xs.length; i += 2) mix.push([D.A.xs[i], (1 - lam) * D.A.d[i] + lam * D.B.d[i]]);
      top.poly(mix, "ln cm dash");
      var qb = new Float64Array(MQ);
      for (i = 0; i < MQ; i++) qb[i] = (1 - lam) * D.qa[i] + lam * D.qb[i];
      var dens = densityFromQ(qb);
      top.poly(areaPts(dens), "a3"); top.poly(dens, "ln c3");
      top.unclip();
      // CDFs with horizontal averaging
      bot.o.x = [P.L, P.R];
      bot.clear();
      bot.axes({ xticks: ticks, yticks: [0, 0.2, 0.5, 0.8, 1], yfmt: function (v) { return fmt(v, 1); } });
      bot.clip();
      var cA = [], cB = [], cM = [];
      for (i = 0; i < D.A.xs.length; i += 4) { cA.push([D.A.xs[i], D.A.c[i]]); cB.push([D.B.xs[i], D.B.c[i]]); cM.push([D.A.xs[i], (1 - lam) * D.A.c[i] + lam * D.B.c[i]]); }
      bot.poly(cA, "ln c1 thin"); bot.poly(cB, "ln c5 thin"); bot.poly(cM, "ln cm dash");
      var cBar = [[P.L, 0]];
      for (i = 0; i < MQ; i += 3) cBar.push([qb[i], US[i]]);
      cBar.push([P.R, 1]);
      bot.poly(cBar, "ln c3");
      [0.2, 0.5, 0.8].forEach(function (u) {
        var k = Math.min(MQ - 1, Math.round(u * MQ - 0.5));
        bot.seg(D.qa[k], u, D.qb[k], u, "ln ck thin dot");
        bot.dot(D.qa[k], u, 3, "f1"); bot.dot(D.qb[k], u, 3, "f5"); bot.dot(qb[k], u, 5, "f3");
      });
      bot.unclip();
      var w = w2q(D.qa, D.qb);
      ro.textContent = "λ = " + fmt(lam, 2) + "   at each level t: q_bar(t) = (1 − λ)·q₁(t) + λ·q₂(t)   (dots on the dotted segments)" +
        "\nW₂(β₁, β₂) = " + fmt(w, 3) + "    W₂(β₁, bar) = λ·W₂ = " + fmt(w2q(D.qa, qb), 3) + "    W₂(bar, β₂) = (1 − λ)·W₂ = " + fmt(w2q(qb, D.qb), 3) +
        "\ncost (1 − λ)W₂²(bar, β₁) + λW₂²(bar, β₂) = λ(1 − λ)W₂²(β₁, β₂) = " + fmt(lam * (1 - lam) * w * w, 3);
    }
    setup(); redrawers.push(draw);
  };

  /* ---------------- 2 x 2 symmetric matrices, stored row-major [a, b, c, d] ---------------- */
  function mmul(A, B) { return [A[0] * B[0] + A[1] * B[2], A[0] * B[1] + A[1] * B[3], A[2] * B[0] + A[3] * B[2], A[2] * B[1] + A[3] * B[3]]; }
  function msym(A) { var o = (A[1] + A[2]) / 2; return [A[0], o, o, A[3]]; }
  function msqrt(A) { // square root of a symmetric positive semi-definite 2 x 2 matrix: (A + sI) / sqrt(tr A + 2s), s = sqrt(det A)
    var s = Math.sqrt(Math.max(A[0] * A[3] - A[1] * A[2], 0)), t = Math.sqrt(A[0] + A[3] + 2 * s);
    return [(A[0] + s) / t, A[1] / t, A[2] / t, (A[3] + s) / t];
  }
  function minv(A) { var det = A[0] * A[3] - A[1] * A[2]; return [A[3] / det, -A[1] / det, -A[2] / det, A[0] / det]; }
  function PsiMap(S, Ss, lam) { // Psi(S) = sum_k lam_k (S^1/2 S_k S^1/2)^1/2
    var r = msqrt(S), out = [0, 0, 0, 0];
    for (var k = 0; k < Ss.length; k++) {
      var R = msqrt(msym(mmul(mmul(r, Ss[k]), r)));
      for (var e = 0; e < 4; e++) out[e] += lam[k] * R[e];
    }
    return msym(out);
  }
  function aeStep(S, Ss, lam) { var ri = minv(msqrt(S)), P = PsiMap(S, Ss, lam); return msym(mmul(mmul(ri, mmul(P, P)), ri)); }
  function bures(S, L) {
    var rL = msqrt(L), M = msqrt(msym(mmul(mmul(rL, S), rL)));
    return Math.sqrt(Math.max(S[0] + S[3] + L[0] + L[3] - 2 * (M[0] + M[3]), 0));
  }
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

  /* --- 5. Barycenter of three Gaussians, and the two fixed-point iterations (§8) --- */
  WIDGETS.gauss = function (box) {
    var s = scaffold(box, "Barycenter of three Gaussians: drag the weights; compare the two fixed-point iterations");
    var W = 680, H = 400;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Three Gaussian ellipses, their Wasserstein barycenter, a weight triangle and a convergence plot");
    var ms = [[-2.3, 1.3], [2.3, 1.3], [0, -2.1]];
    var Ss = [[1.0, 0, 0, 0.1], [0.1, 0, 0, 1.0], [0.5, 0.4, 0.4, 0.5]];
    var showSel = select(s.controls, "Draw the iterates of", [["none", "nothing"], ["psi", "the board’s Σ ← Ψ(Σ)"], ["ae", "Álvarez-Esteban Σ ← Σ^-½ Ψ(Σ)² Σ^-½"]], "none", draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "inputs βₖ (1 st. dev. ellipses)"], ["--s3", "barycenter"], ["--muted", "Ψ iteration (dashed)"], ["--s3", "Álvarez-Esteban (solid)"]]);
    var main = { x0: 8, y0: 8, w: 400, h: 384, xr: [-4.6, 4.6] };
    main.k = main.w / (main.xr[1] - main.xr[0]);
    main.yc = 0; // y range centred so that the aspect ratio is 1
    function MX(x) { return main.x0 + (x - main.xr[0]) * main.k; }
    function MY(y) { return main.y0 + main.h / 2 - (y - main.yc) * main.k; }
    var tri = new WeightTriangle(s.svg, [476, 26, 160, 100], ["λ₁", "λ₂", "λ₃"], draw);
    function path(pts, cls, extra) {
      var d = pts.map(function (p, i) { return (i ? "L" : "M") + MX(p[0]).toFixed(1) + " " + MY(p[1]).toFixed(1); }).join("") + "Z";
      var a = { d: d, "class": cls }; for (var k in extra || {}) a[k] = extra[k];
      return a;
    }
    function draw() {
      var lam = tri.lam, k, l;
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg);
      el("rect", { x: main.x0, y: main.y0, width: main.w, height: main.h, "class": "ln cm hair nofill" }, g);
      // barycenter: mean of the means, covariance by the (provably convergent) Alvarez-Esteban iteration
      var m = [0, 0];
      for (k = 0; k < 3; k++) { m[0] += lam[k] * ms[k][0]; m[1] += lam[k] * ms[k][1]; }
      var Sst = [1, 0, 0, 1];
      for (l = 0; l < 200; l++) Sst = aeStep(Sst, Ss, lam);
      for (k = 0; k < 3; k++) {
        el("path", path(ellipsePts(ms[k], Ss[k], 1), "a1 ln c1 thin"), g);
        el("circle", { cx: MX(ms[k][0]), cy: MY(ms[k][1]), r: 3, "class": "f1" }, g);
        var t = el("text", { x: MX(ms[k][0]), y: MY(ms[k][1] + Math.sqrt(Ss[k][3])) - 7, "class": "tx-b t1", "text-anchor": "middle" }, g);
        t.textContent = "β" + "₁₂₃"[k];
      }
      var it = showSel.value;
      if (it !== "none") {
        var S = [1, 0, 0, 1];
        for (l = 0; l < 6; l++) {
          el("path", path(ellipsePts(m, S, 1), "ln " + (it === "psi" ? "cm dash" : "c3 thin"), { "stroke-opacity": (0.25 + 0.12 * l).toFixed(2) }), g);
          S = it === "psi" ? PsiMap(S, Ss, lam) : aeStep(S, Ss, lam);
        }
      }
      el("path", path(ellipsePts(m, Sst, 1), "a3 ln c3"), g);
      el("circle", { cx: MX(m[0]), cy: MY(m[1]), r: 4, "class": "f3" }, g);
      // weight triangle
      tri.draw(g);
      // convergence of the two iterations from Sigma^(0) = I
      var cx0 = 470, cy0 = 226, cw = 196, ch = 140, nIt = 14, lo = -9, hi = 1;
      function CX(i) { return cx0 + i / nIt * cw; }
      function CY(v) { return cy0 + ch - (Math.log10(Math.max(v, 1e-9)) - lo) / (hi - lo) * ch; }
      el("rect", { x: cx0, y: cy0, width: cw, height: ch, "class": "ln cm hair nofill" }, g);
      [0, -3, -6, -9].forEach(function (e) {
        el("line", { x1: cx0, x2: cx0 + cw, y1: CY(Math.pow(10, e)), y2: CY(Math.pow(10, e)), "class": "gr" }, g);
        var tt = el("text", { x: cx0 - 4, y: CY(Math.pow(10, e)) + 4, "class": "tx-s", "text-anchor": "end" }, g);
        tt.textContent = e === 0 ? "1" : "1e" + e;
      });
      [0, 5, 10].forEach(function (i) { var tt = el("text", { x: CX(i), y: cy0 + ch + 13, "class": "tx-s", "text-anchor": "middle" }, g); tt.textContent = i; });
      var cap = el("text", { x: cx0, y: cy0 - 8, "class": "tx-s" }, g); cap.textContent = "Bures distance to Σ* after ℓ iterations";
      var reached = { psi: -1, ae: -1 };
      [["psi", "ln cm dash"], ["ae", "ln c3"]].forEach(function (alg) {
        var S = [1, 0, 0, 1], d = "";
        for (var i = 0; i <= nIt; i++) {
          var b = bures(S, Sst);
          if (reached[alg[0]] < 0 && b < 1e-6) reached[alg[0]] = i;
          d += (i ? "L" : "M") + CX(i).toFixed(1) + " " + CY(b).toFixed(1);
          if (b < 1e-8) break; // below this, the Bures distance is rounding noise
          S = alg[0] === "psi" ? PsiMap(S, Ss, lam) : aeStep(S, Ss, lam);
        }
        el("path", { d: d, "class": alg[1] }, g);
      });
      var S2 = [1, 0, 0, 1], nPsi = 0;
      while (bures(S2, Sst) >= 1e-6 && nPsi < 500) { S2 = PsiMap(S2, Ss, lam); nPsi++; }
      ro.textContent = "λ = (" + lam.map(function (v) { return fmt(v, 2); }).join(", ") + ")    m* = (" + fmt(m[0], 2) + ", " + fmt(m[1], 2) + ")    Σ* = [[" + fmt(Sst[0], 3) + ", " + fmt(Sst[1], 3) + "], [" + fmt(Sst[2], 3) + ", " + fmt(Sst[3], 3) + "]]" +
        "\nfixed-point residual ‖Ψ(Σ*) − Σ*‖ = " + Math.hypot.apply(null, PsiMap(Sst, Ss, lam).map(function (v, i) { return v - Sst[i]; })).toExponential(1) +
        "    iterations from Σ⁽⁰⁾ = I to reach a Bures distance 1e-6:  board’s Ψ: " + nPsi + ",  Álvarez-Esteban: " + (reached.ae >= 0 ? reached.ae : "> " + nIt);
    }
    draw(); redrawers.push(draw);
  };

  /* ---------------- optimal assignment (Hungarian algorithm, O(n^3)) ---------------- */
  // C is an n x n cost matrix; returns a[i] = column assigned to row i, minimising sum_i C[i][a[i]].
  function hungarian(C) {
    var n = C.length, INF = 1e300, i, j;
    var u = new Float64Array(n + 1), v = new Float64Array(n + 1), p = new Int32Array(n + 1), way = new Int32Array(n + 1);
    for (i = 1; i <= n; i++) {
      p[0] = i;
      var j0 = 0, minv = new Float64Array(n + 1), used = new Uint8Array(n + 1);
      for (j = 0; j <= n; j++) minv[j] = INF;
      do {
        used[j0] = 1;
        var i0 = p[j0], delta = INF, j1 = 0;
        for (j = 1; j <= n; j++) if (!used[j]) {
          var cur = C[i0 - 1][j - 1] - u[i0] - v[j];
          if (cur < minv[j]) { minv[j] = cur; way[j] = j0; }
          if (minv[j] < delta) { delta = minv[j]; j1 = j; }
        }
        for (j = 0; j <= n; j++) { if (used[j]) { u[p[j]] += delta; v[j] -= delta; } else minv[j] -= delta; }
        j0 = j1;
      } while (p[j0] !== 0);
      do { var jj = way[j0]; p[j0] = p[jj]; j0 = jj; } while (j0);
    }
    var a = new Int32Array(n);
    for (j = 1; j <= n; j++) a[p[j] - 1] = j - 1;
    return a;
  }

  /* --- 6. The fixed-point algorithm on point clouds (§9) --- */
  WIDGETS.fixedpoint = function (box) {
    var s = scaffold(box, "The fixed-point algorithm on point clouds: match, average the partners, move");
    var W = 680, H = 420, n = 40, k, i;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Three input point clouds and the current barycenter estimate");
    var rng0 = mulberry32(3);
    var shapes = [[], [], []];
    for (i = 0; i < n; i++) { var a = 2 * Math.PI * (i + 0.5) / n; shapes[0].push([-2.9 + Math.cos(a), 1.9 + Math.sin(a)]); }
    for (i = 0; i < n; i++) {
      var side = Math.floor(i / (n / 4)), u = -1 + 2 * (i % (n / 4)) / (n / 4), q;
      q = side === 0 ? [u, -1] : side === 1 ? [1, u] : side === 2 ? [-u, 1] : [-1, -u];
      shapes[1].push([2.9 + 0.9 * q[0], 1.9 + 0.9 * q[1]]);
    }
    for (i = 0; i < n; i++) {
      var c = i < n / 2 ? [-0.8, 0.3] : [0.8, -0.3];
      shapes[2].push([c[0] + 0.18 * gaussRand(rng0), -2.3 + c[1] + 0.18 * gaussRand(rng0)]);
    }
    var COL = ["1", "5", "4"];
    var startSel = select(s.controls, "Start from", [["ring", "the ring β₁"], ["random", "a random cloud"]], "ring", reset);
    button(s.controls, "Step", function () { if (!busy) step(false); });
    button(s.controls, "Run to the fixed point", function () { if (!busy) step(true); });
    button(s.controls, "Reset", reset);
    var partChk = checkbox(s.controls, "show partners", true, function () { draw(X, last); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "β₁"], ["--s5", "β₂"], ["--s4", "β₃"], ["--s3", "current guess α⁽ˡ⁾"]]);
    var main = { x0: 8, y0: 8, w: 450, h: 404, xr: [-4.6, 4.6], yc: -0.35 };
    main.k = main.w / (main.xr[1] - main.xr[0]);
    function MX(x) { return main.x0 + (x - main.xr[0]) * main.k; }
    function MY(y) { return main.y0 + main.h / 2 - (y - main.yc) * main.k; }
    var tri = new WeightTriangle(s.svg, [500, 26, 144, 96], ["λ₁", "λ₂", "λ₃"], function () { reset(); });
    var X, ell, hist, last = null, busy = false, pendingReset = false, seed = 11, msg = "";

    function assign(Xc) { // optimal assignments to the three inputs, and the cost F
      var parts = [], Fv = 0;
      for (var kk = 0; kk < 3; kk++) {
        var Y = shapes[kk], C = Xc.map(function (x) { return Y.map(function (y) { var dx = x[0] - y[0], dy = x[1] - y[1]; return dx * dx + dy * dy; }); });
        var asg = hungarian(C), w = 0;
        for (var ii = 0; ii < n; ii++) w += C[ii][asg[ii]];
        parts.push(asg); Fv += tri.lam[kk] * w / n;
      }
      return { parts: parts, F: Fv };
    }
    function reset() {
      if (busy) { pendingReset = true; return; }
      if (startSel.value === "ring") X = shapes[0].map(function (p) { return p.slice(); });
      else { var r = mulberry32(seed++); X = []; for (var ii = 0; ii < n; ii++) X.push([2.2 * gaussRand(r), -0.3 + 1.8 * gaussRand(r)]); }
      ell = 0; last = assign(X); hist = [last.F]; msg = "ℓ = 0. Press Step: each green point moves to the weighted average of its three partners.";
      draw(X, last);
    }
    function step(run) {
      var A = last || assign(X), T = [];
      for (var ii = 0; ii < n; ii++) {
        var t = [0, 0];
        for (var kk = 0; kk < 3; kk++) { var y = shapes[kk][A.parts[kk][ii]]; t[0] += tri.lam[kk] * y[0]; t[1] += tri.lam[kk] * y[1]; }
        T.push(t);
      }
      var st = 0;
      for (ii = 0; ii < n; ii++) st += (X[ii][0] - T[ii][0]) * (X[ii][0] - T[ii][0]) + (X[ii][1] - T[ii][1]) * (X[ii][1] - T[ii][1]);
      st /= n;
      if (st < 1e-14) { msg = "ℓ = " + ell + ". Fixed point: the averaged map is the identity on the cloud (no point moves). F = " + fmt(A.F, 4) + "."; draw(X, A); return; }
      var X0 = X, t0 = null, dur = run ? 380 : 650;
      busy = true;
      function frame(ts) {
        if (t0 === null) t0 = ts;
        var r = Math.min(1, (ts - t0) / dur), e = r * r * (3 - 2 * r);
        draw(X0.map(function (p, j) { return [p[0] + e * (T[j][0] - p[0]), p[1] + e * (T[j][1] - p[1])]; }), A);
        if (r < 1) { requestAnimationFrame(frame); return; }
        X = T; ell++;
        if (pendingReset) { pendingReset = false; busy = false; reset(); return; }
        var B = assign(X), ok = B.F <= A.F - st + 1e-10;
        hist.push(B.F); last = B;
        msg = "ℓ = " + ell + ".  F before = " + fmt(A.F, 4) + "  →  F after = " + fmt(B.F, 4) + "   squared step = " + fmt(st, 4) +
          "\ndescent check  F_after ≤ F_before − step²:  " + fmt(B.F, 4) + " ≤ " + fmt(A.F - st, 4) + (ok ? "  ✓" : "  ✗");
        draw(X, B);
        busy = false;
        if (run && ell < 40) setTimeout(function () { step(true); }, 120);
      }
      requestAnimationFrame(frame);
    }
    function draw(Xd, A) {
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg), kk, ii;
      el("rect", { x: main.x0, y: main.y0, width: main.w, height: main.h, "class": "ln cm hair nofill" }, g);
      if (partChk.checked && A) for (kk = 0; kk < 3; kk++) for (ii = 0; ii < n; ii++) {
        var y = shapes[kk][A.parts[kk][ii]];
        el("line", { x1: MX(Xd[ii][0]), y1: MY(Xd[ii][1]), x2: MX(y[0]), y2: MY(y[1]), "class": "ln c" + COL[kk] + " hair", "stroke-opacity": 0.22 }, g);
      }
      for (kk = 0; kk < 3; kk++) shapes[kk].forEach(function (p) { el("circle", { cx: MX(p[0]), cy: MY(p[1]), r: 2.8, "class": "f" + COL[kk] }, g); });
      Xd.forEach(function (p) { el("circle", { cx: MX(p[0]), cy: MY(p[1]), r: 3.6, "class": "f3" }, g); });
      tri.draw(g);
      // cost along the iterations
      var cx0 = 506, cy0 = 238, cw = 150, ch = 120;
      el("rect", { x: cx0, y: cy0, width: cw, height: ch, "class": "ln cm hair nofill" }, g);
      var cap = el("text", { x: cx0, y: cy0 - 8, "class": "tx-s" }, g); cap.textContent = "cost F(α⁽ˡ⁾) along the iterations";
      if (hist && hist.length) {
        var lo = Math.min.apply(null, hist), hi = Math.max.apply(null, hist), span = Math.max(hi - lo, 1e-9), m = Math.max(hist.length - 1, 4);
        var d = hist.map(function (v, j) { return (j ? "L" : "M") + (cx0 + j / m * cw).toFixed(1) + " " + (cy0 + ch - 8 - (v - lo) / span * (ch - 16)).toFixed(1); }).join("");
        el("path", { d: d, "class": "ln c3 thin" }, g);
        hist.forEach(function (v, j) { el("circle", { cx: cx0 + j / m * cw, cy: cy0 + ch - 8 - (v - lo) / span * (ch - 16), r: 2.5, "class": "f3" }, g); });
        var t1 = el("text", { x: cx0 + cw, y: cy0 + ch + 14, "class": "tx-s", "text-anchor": "end" }, g); t1.textContent = "F = " + fmt(hist[hist.length - 1], 4);
      }
      ro.textContent = msg;
    }
    reset();
    redrawers.push(function () { draw(X, last); });
  };


  document.querySelectorAll("[data-widget]").forEach(function (box) {
    var f = WIDGETS[box.getAttribute("data-widget")];
    if (f) { try { f(box); } catch (e) { box.insertAdjacentHTML("afterbegin", "<p class='small muted'>Figure unavailable: " + e.message + "</p>"); } }
  });
})();
