// app.js — theme, folds, active table of contents and interactive figures of Opti_CS/LP v2.
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
      try { localStorage.setItem("lp-v2-theme", t); } catch (err) {}
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
      if (Math.abs(p / q - x) < 1e-9) return (q === 1 ? String(p) : p + "/" + q).replace("-", "−");
    }
    return fmt(x, 3).replace("-", "−");
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
  // All the k-element subsets of {0, …, n−1}, in lexicographic order.
  function combinations(n, k) {
    var out = [], cur = [];
    (function rec(start) {
      if (cur.length === k) { out.push(cur.slice()); return; }
      for (var i = start; i <= n - (k - cur.length); i++) { cur.push(i); rec(i + 1); cur.pop(); }
    })(0);
    return out;
  }

  /* ---------------- exact rational numbers ---------------- */
  // Fr(7, 2) is 7/2. Fr.of(x) accepts a Fr, an integer or a decimal with a small denominator (0.5, 1/3 ≈ 0.3333…).
  // Operations return new numbers: a.add(b), a.sub(b), a.mul(b), a.div(b), a.neg(), a.cmp(b) (−1, 0, 1), a.sign(),
  // a.isZero(), a.val() (float), a.str() ("−7/2", Unicode minus). Fine for the small examples of the course.
  function gcd(a, b) { a = Math.abs(a); b = Math.abs(b); while (b) { var t = a % b; a = b; b = t; } return a || 1; }
  function Fr(n, d) {
    if (!(this instanceof Fr)) return new Fr(n, d);
    if (d === undefined) d = 1;
    if (d === 0) throw new Error("Fr: zero denominator");
    if (d < 0) { n = -n; d = -d; }
    var g = gcd(n, d); this.n = n / g; this.d = d / g;
  }
  Fr.of = function (x) {
    if (x instanceof Fr) return x;
    if (Number.isInteger(x)) return new Fr(x, 1);
    for (var q = 2; q <= 1000; q++) { var p = Math.round(x * q); if (Math.abs(p / q - x) < 1e-9) return new Fr(p, q); }
    throw new Error("Fr.of: " + x + " is not a simple fraction");
  };
  Fr.prototype.add = function (b) { b = Fr.of(b); return new Fr(this.n * b.d + b.n * this.d, this.d * b.d); };
  Fr.prototype.sub = function (b) { b = Fr.of(b); return new Fr(this.n * b.d - b.n * this.d, this.d * b.d); };
  Fr.prototype.mul = function (b) { b = Fr.of(b); return new Fr(this.n * b.n, this.d * b.d); };
  Fr.prototype.div = function (b) { b = Fr.of(b); return new Fr(this.n * b.d, this.d * b.n); };
  Fr.prototype.neg = function () { return new Fr(-this.n, this.d); };
  Fr.prototype.sign = function () { return this.n > 0 ? 1 : this.n < 0 ? -1 : 0; };
  Fr.prototype.cmp = function (b) { return this.sub(b).sign(); };
  Fr.prototype.isZero = function () { return this.n === 0; };
  Fr.prototype.val = function () { return this.n / this.d; };
  Fr.prototype.str = function () { return ((this.d === 1 ? String(this.n) : this.n + "/" + this.d)).replace("-", "−"); };
  Fr.prototype.toString = Fr.prototype.str;
  function frMat(M) { return M.map(function (r) { return r.map(Fr.of); }); }
  function frVec(v) { return v.map(Fr.of); }
  // Determinant of a square matrix, exact (Gaussian elimination on fractions).
  function frDet(M) {
    var A = frMat(M), n = A.length, det = Fr(1);
    for (var k = 0; k < n; k++) {
      var p = k; while (p < n && A[p][k].isZero()) p++;
      if (p === n) return Fr(0);
      if (p !== k) { var t = A[p]; A[p] = A[k]; A[k] = t; det = det.neg(); }
      det = det.mul(A[k][k]);
      for (var i = k + 1; i < n; i++) {
        var f = A[i][k].div(A[k][k]);
        for (var j = k; j < n; j++) A[i][j] = A[i][j].sub(f.mul(A[k][j]));
      }
    }
    return det;
  }
  // Solves B z = r exactly (B square); returns null if B is singular.
  function frSolve(B, r) {
    var n = B.length, A = frMat(B).map(function (row, i) { return row.concat([Fr.of(r[i])]); });
    for (var k = 0; k < n; k++) {
      var p = k; while (p < n && A[p][k].isZero()) p++;
      if (p === n) return null;
      var t = A[p]; A[p] = A[k]; A[k] = t;
      for (var i = 0; i < n; i++) if (i !== k && !A[i][k].isZero()) {
        var f = A[i][k].div(A[k][k]);
        for (var j = k; j <= n; j++) A[i][j] = A[i][j].sub(f.mul(A[k][j]));
      }
    }
    return A.map(function (row, i) { return row[n].div(row[i]); });
  }

  /* ---------------- linear programs in standard form: min c·x, Ax = b, x ≥ 0 ---------------- */
  // The basic solution of the columns `cols` (m indices): {x, status} with status "singulière" (B not invertible),
  // "non admissible" (some x_B < 0), "admissible" or "dégénérée" (admissible with some x_B = 0). x is null if singular.
  function basicSolution(A, b, cols) {
    var m = A.length, n = A[0].length;
    var B = A.map(function (row) { return cols.map(function (j) { return row[j]; }); });
    var xb = frSolve(B, b);
    if (!xb) return { x: null, status: "singulière" };
    var x = []; for (var j = 0; j < n; j++) x.push(Fr(0));
    cols.forEach(function (j, i) { x[j] = xb[i]; });
    var neg = xb.some(function (v) { return v.sign() < 0; }), zero = xb.some(function (v) { return v.isZero(); });
    return { x: x, status: neg ? "non admissible" : zero ? "dégénérée" : "admissible" };
  }
  // The simplex method of the course, in exact arithmetic, from an admissible basis `basis` (m column indices).
  // opts.rule: "dantzig" (the most negative reduced cost, as in the course; default) or "bland" (smallest index).
  // Returns {status: "optimal" | "unbounded" | "maxiter", steps}. Each step describes one vertex:
  //   basis (column indices, in the order of the rows), x (Fr, length n), cost (Fr), reduced (Fr, length n, 0 on
  //   the basis), entering (column index, −1 at the optimum), dir (Fr, length m: B⁻¹ a_entering, so that
  //   x_B(ε) = x_B − ε·dir), ratios (Fr or null for each row: x_B,i / dir_i when dir_i > 0), leaving (row index
  //   or −1), eps (Fr: the step ε_k, null if unbounded), T (Fr m×n: B⁻¹A) and xB (Fr m: B⁻¹b).
  function simplex(A, b, c, basis, opts) {
    opts = opts || {};
    var m = A.length, n = A[0].length, maxIter = opts.maxIter || 50;
    var cF = frVec(c), bas = basis.slice();
    var T = frMat(A), rhs = frVec(b);
    // Gauss–Jordan on the basis columns: T = B⁻¹A, rhs = B⁻¹b.
    for (var k = 0; k < m; k++) {
      var col = bas[k], p = k;
      while (p < m && T[p][col].isZero()) p++;
      if (p === m) throw new Error("simplex: the initial basis is singular");
      var t = T[p]; T[p] = T[k]; T[k] = t; var tr = rhs[p]; rhs[p] = rhs[k]; rhs[k] = tr;
      pivot(k, col);
    }
    if (rhs.some(function (v) { return v.sign() < 0; })) throw new Error("simplex: the initial basis is not admissible");
    function pivot(r, col) {
      var piv = T[r][col], j, i;
      for (j = 0; j < n; j++) T[r][j] = T[r][j].div(piv);
      rhs[r] = rhs[r].div(piv);
      for (i = 0; i < m; i++) if (i !== r && !T[i][col].isZero()) {
        var f = T[i][col];
        for (j = 0; j < n; j++) T[i][j] = T[i][j].sub(f.mul(T[r][j]));
        rhs[i] = rhs[i].sub(f.mul(rhs[r]));
      }
    }
    var steps = [];
    for (var it = 0; it <= maxIter; it++) {
      var x = [], j, i; for (j = 0; j < n; j++) x.push(Fr(0));
      bas.forEach(function (col, r) { x[col] = rhs[r]; });
      var cost = Fr(0); for (j = 0; j < n; j++) cost = cost.add(cF[j].mul(x[j]));
      var red = [];
      for (j = 0; j < n; j++) {
        var z = Fr(0); for (i = 0; i < m; i++) z = z.add(cF[bas[i]].mul(T[i][j]));
        red.push(bas.indexOf(j) >= 0 ? Fr(0) : cF[j].sub(z));
      }
      var step = { basis: bas.slice(), x: x, cost: cost, reduced: red, entering: -1, dir: null, ratios: null, leaving: -1, eps: null,
        T: T.map(function (r) { return r.slice(); }), xB: rhs.slice() };
      steps.push(step);
      var e = -1;
      for (j = 0; j < n; j++) if (red[j].sign() < 0) {
        if (e < 0) { e = j; if (opts.rule === "bland") break; } else if (red[j].cmp(red[e]) < 0) e = j;
      }
      if (e < 0) return { status: "optimal", steps: steps };
      step.entering = e;
      step.dir = T.map(function (r) { return r[e]; });
      step.ratios = step.dir.map(function (d, r) { return d.sign() > 0 ? rhs[r].div(d) : null; });
      var lr = -1;
      step.ratios.forEach(function (q, r) {
        if (q === null) return;
        if (lr < 0 || q.cmp(step.ratios[lr]) < 0 || (q.cmp(step.ratios[lr]) === 0 && bas[r] < bas[lr])) lr = r;
      });
      if (lr < 0) return { status: "unbounded", steps: steps };
      step.leaving = lr; step.eps = step.ratios[lr];
      pivot(lr, e); bas[lr] = e;
    }
    return { status: "maxiter", steps: steps };
  }

  /* ---------------- the plane: polygons of constraints a·x + b·y ≤ r ---------------- */
  // cons = [[a, b, r], …]; box = [x0, x1, y0, y1]. Returns the vertices of {a x + b y ≤ r for all} ∩ box, in order
  // (Sutherland–Hodgman clipping of the box); [] if empty.
  function halfPlanePolygon(cons, box) {
    var P = [[box[0], box[2]], [box[1], box[2]], [box[1], box[3]], [box[0], box[3]]];
    cons.forEach(function (h) {
      var out = [], a = h[0], bb = h[1], r = h[2];
      for (var i = 0; i < P.length; i++) {
        var p = P[i], q = P[(i + 1) % P.length];
        var fp = a * p[0] + bb * p[1] - r, fq = a * q[0] + bb * q[1] - r;
        if (fp <= 1e-12) out.push(p);
        if ((fp < -1e-12 && fq > 1e-12) || (fp > 1e-12 && fq < -1e-12)) {
          var t = fp / (fp - fq); out.push([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])]);
        }
      }
      P = out;
    });
    return P;
  }
  // The part of the line a x + b y = r inside box = [x0, x1, y0, y1]: [[x, y], [x, y]] or null.
  function lineInBox(a, b, r, box) {
    var pts = [];
    if (Math.abs(b) > 1e-12) [box[0], box[1]].forEach(function (x) { var y = (r - a * x) / b; if (y >= box[2] - 1e-9 && y <= box[3] + 1e-9) pts.push([x, y]); });
    if (Math.abs(a) > 1e-12) [box[2], box[3]].forEach(function (y) { var x = (r - b * y) / a; if (x >= box[0] - 1e-9 && x <= box[1] + 1e-9) pts.push([x, y]); });
    if (pts.length < 2) return null;
    var best = [pts[0], pts[1]], d = -1;
    for (var i = 0; i < pts.length; i++) for (var j = i + 1; j < pts.length; j++) {
      var dd = Math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]); if (dd > d) { d = dd; best = [pts[i], pts[j]]; }
    }
    return best;
  }

  /* ---------------- graphs: arrows, arcs and nodes (in viewBox units) ---------------- */
  // An arrow-head marker filled with class `cls` (e.g. "f1"); returns "url(#id)" for marker-end.
  function arrowMarker(svg, cls) {
    var defs = svg.querySelector("defs") || el("defs", {}, svg);
    var id = "arr-" + cls + "-" + Math.random().toString(36).slice(2, 8);
    var mk = el("marker", { id: id, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse" }, defs);
    el("path", { d: "M0,0 L10,5 L0,10 z", "class": cls }, mk);
    return "url(#" + id + ")";
  }
  // An arc from p to q ([x, y]) stopping at distance r of both centres, bent by `bend` (0 = straight; ±0.2 to separate
  // the arcs i→j and j→i). Returns {path, mid} where mid is the point where a label can go.
  function drawArc(g, p, q, opt) {
    opt = opt || {};
    var r = opt.r || 14, bend = opt.bend || 0;
    var dx = q[0] - p[0], dy = q[1] - p[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L;
    var cx = (p[0] + q[0]) / 2 - uy * bend * L, cy = (p[1] + q[1]) / 2 + ux * bend * L;
    function towards(a, b, d) { var vx = b[0] - a[0], vy = b[1] - a[1], l = Math.hypot(vx, vy); return [a[0] + vx / l * d, a[1] + vy / l * d]; }
    var s = towards(p, bend ? [cx, cy] : q, r), e = towards(q, bend ? [cx, cy] : p, r + 2);
    var d = bend ? "M" + s[0] + " " + s[1] + "Q" + cx + " " + cy + " " + e[0] + " " + e[1] : "M" + s[0] + " " + s[1] + "L" + e[0] + " " + e[1];
    var path = el("path", { d: d, "class": opt.cls || "ln", fill: "none", "marker-end": opt.marker, style: opt.style }, g);
    var mid = bend ? [0.25 * s[0] + 0.5 * cx + 0.25 * e[0], 0.25 * s[1] + 0.5 * cy + 0.25 * e[1]] : [(s[0] + e[0]) / 2, (s[1] + e[1]) / 2];
    if (opt.label !== undefined) {
      var off = opt.labelOffset === undefined ? 10 : opt.labelOffset, side = bend < 0 ? -1 : 1;
      var t = el("text", { x: mid[0] - uy * off * side, y: mid[1] + ux * off * side + 4, "class": opt.labelCls || "tx-s", "text-anchor": "middle" }, g);
      t.textContent = opt.label;
    }
    return { path: path, mid: mid };
  }
  function drawNode(g, p, label, opt) {
    opt = opt || {};
    var c = el("circle", { cx: p[0], cy: p[1], r: opt.r || 14, "class": opt.cls || "f1" }, g);
    var t = el("text", { x: p[0], y: p[1] + 4.5, "class": opt.textCls || "tx-b on-fill", "text-anchor": "middle" }, g);
    t.textContent = label;
    return c;
  }

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

  /* ======================================================================
     Widgets of the page (widgets/<page>.js, inserted here by build.mjs)
     ====================================================================== */
  /* @@PAGE_WIDGETS@@ */

  document.querySelectorAll("[data-widget]").forEach(function (box) {
    var f = WIDGETS[box.getAttribute("data-widget")];
    if (f) { try { f(box); } catch (e) { box.insertAdjacentHTML("afterbegin", "<p class='small muted'>Figure indisponible : " + e.message + "</p>"); } }
  });
})();
