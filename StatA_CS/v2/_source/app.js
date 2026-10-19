// app.js — thème, dépliage, sommaire actif et figures interactives de StatA_CS v2.
(function () {
  "use strict";

  /* ---------------- thème ---------------- */
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
      try { localStorage.setItem("statA-v2-theme", t); } catch (err) {}
      redrawAll();
    } else if (a === "expand" || a === "collapse") {
      document.querySelectorAll("main details.fold").forEach(function (d) { d.open = a === "expand"; });
    }
  });

  /* ---------------- impression : tout déplier ---------------- */
  var printOpened = [];
  window.addEventListener("beforeprint", function () {
    printOpened = [];
    document.querySelectorAll("details.fold:not([open])").forEach(function (d) { d.open = true; printOpened.push(d); });
  });
  window.addEventListener("afterprint", function () { printOpened.forEach(function (d) { d.open = false; }); });

  /* ---------------- ouvrir le repliable visé par une ancre ---------------- */
  function openTarget() {
    if (!location.hash) return;
    var t = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    while (t) { if (t.tagName === "DETAILS") t.open = true; t = t.parentElement; }
  }
  window.addEventListener("hashchange", openTarget);
  openTarget();

  /* ---------------- sommaire replié sur petit écran ---------------- */
  if (window.innerWidth < 1100) document.querySelectorAll(".toc-box").forEach(function (d) { d.open = false; });

  /* ---------------- sommaire actif ---------------- */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a[href^='#']"));
  if ("IntersectionObserver" in window && tocLinks.length) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var visible = {};
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting; });
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
     Petite bibliothèque de tracé SVG
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
    return s.replace(".", ",");
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
  Plot.prototype.ix = function (px) { // pixel -> x (linéaire seulement)
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
      el("line", { x1: X, x2: X, y1: self.pad.t, y2: self.H - self.pad.b, "class": "gr" }, g);
      var t = el("text", { x: X, y: self.H - self.pad.b + 16, "text-anchor": "middle", "class": "tx" }, g);
      t.textContent = opt.xfmt ? opt.xfmt(v) : fmt(v, opt.xd || 0);
    });
    yt.forEach(function (v) {
      var Y = self.ty(v);
      el("line", { x1: self.pad.l, x2: self.W - self.pad.r, y1: Y, y2: Y, "class": "gr" }, g);
      var t = el("text", { x: self.pad.l - 6, y: Y + 4, "text-anchor": "end", "class": "tx" }, g);
      t.textContent = opt.yfmt ? opt.yfmt(v) : fmt(v, opt.yd || 0);
    });
    var x0 = opt.cross ? Math.min(Math.max(0, o.x[0]), o.x[1]) : o.x[0];
    var y0 = opt.cross ? Math.min(Math.max(0, o.y[0]), o.y[1]) : o.y[0];
    if (o.ylog) y0 = o.y[0];
    if (o.xlog) x0 = o.x[0];
    el("line", { x1: this.pad.l, x2: this.W - this.pad.r, y1: this.ty(y0), y2: this.ty(y0), "class": "ax" }, g);
    el("line", { x1: this.tx(x0), x2: this.tx(x0), y1: this.pad.t, y2: this.H - this.pad.b, "class": "ax" }, g);
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

  /* ---------------- construction des widgets ---------------- */
  function scaffold(box, title) {
    var first = box.firstChild;
    if (title) { var h = document.createElement("p"); h.className = "w-title"; h.textContent = title; box.insertBefore(h, first); }
    var svg = el("svg", {});
    box.insertBefore(svg, first);
    var legend = document.createElement("div"); legend.className = "legend"; box.insertBefore(legend, first);
    var controls = document.createElement("div"); controls.className = "controls"; box.insertBefore(controls, first);
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
    return { input: inp, out: out, get: function () { return parseFloat(inp.value); } };
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
  function soft(b, t) { return Math.sign(b) * Math.max(Math.abs(b) - t, 0); }

  var WIDGETS = {};
  var redrawers = [];
  function redrawAll() { redrawers.forEach(function (f) { f(); }); }

  /* --- 1. Seuillage doux, rétrécissement (Ridge), seuillage dur, sur une coordonnée --- */
  WIDGETS.seuillage = function (box) {
    var s = scaffold(box, box.getAttribute("data-title") || "Une coordonnée : seuillage doux (Lasso) contre rétrécissement (Ridge)");
    var showHard = box.getAttribute("data-hard") === "1";
    // data-seuil="demi" : convention ‖Y − Xβ‖² + λ‖β‖₁ avec XᵀX = I (diapos 26–27) → seuil λ/2.
    var half = box.getAttribute("data-seuil") === "demi";
    var th = function (L) { return half ? L / 2 : L; };
    var p = new Plot(s.svg, { x: [-3, 3], y: [-3, 3], w: 560, h: 380, label: "Courbes de seuillage" });
    var lam = slider(s.controls, "λ", 0, 2.5, 0.05, parseFloat(box.getAttribute("data-lambda") || "1"), draw);
    var bsl = slider(s.controls, "b", -3, 3, 0.05, 1.6, draw);
    var ro = readout(s.controls);
    var items = [["--muted", "identité a = b (moindres carrés)"], ["--s1", "Ridge : b / (1 + λ)"], ["--s2", "Lasso : seuillage doux au seuil " + (half ? "λ/2" : "λ")]];
    if (showHard) items.push(["--s3", "ℓ0 : seuillage dur"]);
    legend(s.legend, items);
    function draw() {
      var L = lam.get(), b = bsl.get();
      lam.out.textContent = fmt(L); bsl.out.textContent = fmt(b);
      p.clear();
      p.axes({ xticks: [-3, -2, -1, 0, 1, 2, 3], yticks: [-3, -2, -1, 1, 2, 3], cross: true, xlabel: "b (coefficient des moindres carrés)", ylabel: "â (coefficient estimé)" });
      p.fn(function (x) { return x; }, "ln cm thin dash");
      p.fn(function (x) { return x / (1 + L); }, "ln c1");
      var T = th(L), lab = half ? "λ/2" : "λ";
      if (showHard) p.fn(function (x) { return Math.abs(x) > T ? x : NaN; }, "ln c3", 800);
      p.fn(function (x) { return soft(x, T); }, "ln c2");
      if (T > 0) {
        p.poly([[-T, -3], [-T, 3]], "ln cm thin dash"); p.poly([[T, -3], [T, 3]], "ln cm thin dash");
        p.text(T, -2.75, "+" + lab, "tx", "start", 4); p.text(-T, -2.75, "−" + lab, "tx", "end", -4);
      }
      p.dot(b, b / (1 + L), 5, "f1"); p.dot(b, soft(b, T), 5, "f2");
      if (showHard) p.dot(b, Math.abs(b) > T ? b : 0, 4, "f3");
      ro.textContent = "b = " + fmt(b) + "  →  Ridge " + fmt(b / (1 + L)) + "   ·   Lasso " + fmt(soft(b, T)) +
        (Math.abs(b) <= T ? "  (exactement 0 : |b| ≤ " + lab + ")" : "  (b rapproché de 0 de " + lab + ")") +
        (showHard ? "   ·   dur " + fmt(Math.abs(b) > T ? b : 0) : "");
    }
    draw(); redrawers.push(draw);
  };

  /* --- 2. Boules ℓ1 / ℓ2 et ellipses des moindres carrés (p = 2) --- */
  function projL1(v, t) {
    var a = Math.abs(v[0]) + Math.abs(v[1]);
    if (a <= t) return v.slice();
    var u = [Math.abs(v[0]), Math.abs(v[1])].sort(function (x, y) { return y - x; });
    var cs = 0, theta = 0;
    for (var j = 0; j < u.length; j++) {
      cs += u[j];
      var th = (cs - t) / (j + 1);
      if (u[j] - th > 0) theta = th;
    }
    return [soft(v[0], theta), soft(v[1], theta)];
  }
  function projL2(v, r) { var n = Math.hypot(v[0], v[1]); return n <= r ? v.slice() : [v[0] * r / n, v[1] * r / n]; }
  function solveConstrained(G, b, proj) {
    var x = [0, 0], eta = 0.2;
    for (var k = 0; k < 4000; k++) {
      var d0 = x[0] - b[0], d1 = x[1] - b[1];
      var g0 = G[0][0] * d0 + G[0][1] * d1, g1 = G[1][0] * d0 + G[1][1] * d1;
      x = proj([x[0] - eta * g0, x[1] - eta * g1]);
    }
    return x;
  }
  function quad(G, b, x) { var d0 = x[0] - b[0], d1 = x[1] - b[1]; return G[0][0] * d0 * d0 + 2 * G[0][1] * d0 * d1 + G[1][1] * d1 * d1; }
  function eig2(G) {
    var a = G[0][0], c = G[1][1], bb = G[0][1];
    var tr = a + c, det = a * c - bb * bb, disc = Math.sqrt(tr * tr / 4 - det);
    var l1 = tr / 2 + disc, l2 = tr / 2 - disc;
    var v1 = Math.abs(bb) > 1e-12 ? [l1 - c, bb] : [1, 0];
    var n = Math.hypot(v1[0], v1[1]); v1 = [v1[0] / n, v1[1] / n];
    return { l: [l1, l2], v: [v1, [-v1[1], v1[0]]] };
  }
  function ellipse(p, G, b, level, cls) {
    var E = eig2(G), pts = [];
    for (var i = 0; i <= 120; i++) {
      var th = 2 * Math.PI * i / 120;
      var a1 = Math.sqrt(level / E.l[0]) * Math.cos(th), a2 = Math.sqrt(level / E.l[1]) * Math.sin(th);
      pts.push([b[0] + a1 * E.v[0][0] + a2 * E.v[1][0], b[1] + a1 * E.v[0][1] + a2 * E.v[1][1]]);
    }
    return p.poly(pts, cls);
  }
  WIDGETS.l1l2 = function (box) {
    var s = scaffold(box, box.getAttribute("data-title") || "p = 2 : où l'ellipse des moindres carrés touche-t-elle la contrainte ?");
    var G = JSON.parse(box.getAttribute("data-gram") || "[[4,1.4],[1.4,1]]");
    var b = JSON.parse(box.getAttribute("data-b") || "[2,3]");
    var p = new Plot(s.svg, { x: [-2.5, 4.5], y: [-2.5, 4.5], w: 460, h: 460, pad: { l: 30, r: 10, t: 10, b: 26 }, label: "Boules l1 et l2 et ellipses" });
    var tS = slider(s.controls, "t", 0.2, 3, 0.05, parseFloat(box.getAttribute("data-t") || "1"), draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "Lasso : ‖β‖₁ ≤ t"], ["--s1", "Ridge : ‖β‖₂² ≤ t"], ["--text", "β̂ MCO (à déplacer)"]]);
    var hint = document.createElement("div"); hint.className = "w-caption"; hint.textContent = "Faites glisser le point noir β̂ (moindres carrés) ; les ellipses sont les lignes de niveau de ‖Y − Xβ‖².";
    s.controls.appendChild(hint);
    function draw() {
      var t = tS.get(); tS.out.textContent = fmt(t);
      var bl = solveConstrained(G, b, function (v) { return projL1(v, t); });
      var br = solveConstrained(G, b, function (v) { return projL2(v, Math.sqrt(t)); });
      p.clear();
      p.axes({ xticks: [-2, -1, 0, 1, 2, 3, 4], yticks: [-2, -1, 1, 2, 3, 4], cross: true, xlabel: "β₁", ylabel: "β₂" });
      p.clip();
      p.poly([[t, 0], [0, t], [-t, 0], [0, -t], [t, 0]], "ln c2 a2");
      var r = Math.sqrt(t), circ = [];
      for (var i = 0; i <= 100; i++) circ.push([r * Math.cos(2 * Math.PI * i / 100), r * Math.sin(2 * Math.PI * i / 100)]);
      p.poly(circ, "ln c1 a1");
      var ql = quad(G, b, bl), qr = quad(G, b, br);
      [0.15, 0.6].forEach(function (f) { ellipse(p, G, b, f * Math.min(ql, qr), "ln cm thin"); });
      ellipse(p, G, b, ql, "ln c2 thin dash");
      ellipse(p, G, b, qr, "ln c1 thin dash");
      p.unclip();
      p.dot(bl[0], bl[1], 5.5, "f2"); p.dot(br[0], br[1], 5.5, "f1");
      var h = p.dot(b[0], b[1], 7, "fk drag");
      h.addEventListener("pointerdown", startDrag);
      var zero = Math.abs(bl[0]) < 1e-3 ? "β₁" : (Math.abs(bl[1]) < 1e-3 ? "β₂" : null);
      ro.textContent = "Lasso : (" + fmt(bl[0]) + " ; " + fmt(bl[1]) + ")" + (zero ? " → " + zero + " = 0 exactement (coin)" : " → aucune coordonnée nulle") +
        "    Ridge : (" + fmt(br[0]) + " ; " + fmt(br[1]) + ")";
    }
    var dragging = false;
    function startDrag(e) { dragging = true; e.preventDefault(); s.svg.setPointerCapture && s.svg.setPointerCapture(e.pointerId); }
    s.svg.addEventListener("pointermove", function (e) {
      if (!dragging) return;
      var q = svgPoint(s.svg, e);
      b = [Math.max(-2.3, Math.min(4.3, p.ix(q.x))), Math.max(-2.3, Math.min(4.3, p.iy(q.y)))];
      draw();
    });
    s.svg.addEventListener("pointerup", function () { dragging = false; });
    s.svg.addEventListener("pointercancel", function () { dragging = false; });
    draw(); redrawers.push(draw);
  };

  /* --- 3. Chemin de régularisation en design orthogonal --- */
  WIDGETS.chemin = function (box) {
    var s = scaffold(box, box.getAttribute("data-title") || "Chemin du Lasso quand XᵀX = I : chaque coefficient descend en ligne droite puis s'arrête à 0");
    var b = JSON.parse(box.getAttribute("data-b") || "[2.4,-1.6,1.0,0.4]");
    var Lmax = 2 * Math.max.apply(null, b.map(Math.abs)) + 0.4;
    var p = new Plot(s.svg, { x: [0, Lmax], y: [-2, 2.6], w: 560, h: 340, label: "Chemin du Lasso" });
    var ridge = false;
    var lam = slider(s.controls, "λ", 0, Lmax, 0.02, 1.2, draw);
    checkbox(s.controls, "comparer avec Ridge", false, function (e) { ridge = e.target.checked; draw(); });
    var ro = readout(s.controls);
    var cols = ["--s1", "--s2", "--s3", "--s5", "--s4", "--s6"];
    legend(s.legend, b.map(function (v, j) { return [cols[j % 6], "β̂" + (j + 1) + " (b" + (j + 1) + " = " + fmt(v, 1) + ")"]; }));
    function draw() {
      var L = lam.get(); lam.out.textContent = fmt(L);
      p.clear();
      var tk = []; for (var k = 0; k <= Lmax; k += 1) tk.push(k);
      p.axes({ xticks: tk, yticks: [-2, -1, 1, 2], cross: true, xlabel: "λ", ylabel: "β̂ⱼ(λ)" });
      b.forEach(function (v, j) {
        var c = ["c1", "c2", "c3", "c5", "c4", "c6"][j % 6];
        p.fn(function (l) { return soft(v, l / 2); }, "ln " + c);
        if (ridge) p.fn(function (l) { return v / (1 + l); }, "ln thin dash " + c);
        p.dot(2 * Math.abs(v), 0, 3, "fm");
      });
      p.poly([[L, -2], [L, 2.6]], "ln cm thin dash");
      var act = [];
      b.forEach(function (v, j) { var x = soft(v, L / 2); p.dot(L, x, 4.5, ["f1", "f2", "f3", "f5", "f4", "f6"][j % 6]); if (x !== 0) act.push(j + 1); });
      ro.textContent = "λ = " + fmt(L) + " : ensemble actif {" + act.join(", ") + "}  (" + act.length + " variable" + (act.length > 1 ? "s" : "") + ")   ·   la coordonnée j sort en λ = 2|bⱼ|";
    }
    draw(); redrawers.push(draw);
  };

  /* --- 4. Biais, variance, risque du Ridge en fonction de λ --- */
  WIDGETS.biaisvariance = function (box) {
    var s = scaffold(box, box.getAttribute("data-title") || "Ridge : biais² + variance = risque, en fonction de λ");
    var mu = JSON.parse(box.getAttribute("data-mu") || "[10,3,1,0.1,0.01]");
    var th = JSON.parse(box.getAttribute("data-theta") || "[1,1,1,1,1]");
    var sig2 = parseFloat(box.getAttribute("data-sigma2") || "1");
    function parts(L) {
      var B = 0, V = 0;
      mu.forEach(function (m, j) { B += Math.pow(L / (m + L), 2) * th[j] * th[j]; V += sig2 * m / Math.pow(m + L, 2); });
      return [B, V, B + V];
    }
    var p = new Plot(s.svg, { x: [1e-3, 1e3], y: [1e-2, 1e3], xlog: true, ylog: true, w: 560, h: 340, label: "Biais variance Ridge" });
    var lam = slider(s.controls, "log₁₀ λ", -3, 3, 0.05, 0, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "biais²"], ["--s2", "variance"], ["--text", "risque E‖β̂ − β*‖²"]]);
    function draw() {
      var L = Math.pow(10, lam.get()); lam.out.textContent = "λ = " + fmt(L, L < 0.1 ? 3 : 2);
      p.clear();
      var pw = function (v) { return "10" + ({ "-3": "⁻³", "-2": "⁻²", "-1": "⁻¹", "0": "⁰", "1": "¹", "2": "²", "3": "³" })[v]; };
      p.axes({ xticks: [1e-3, 1e-2, 1e-1, 1, 10, 100, 1000], yticks: [1e-2, 1e-1, 1, 10, 100, 1000], xfmt: function (v) { return pw(Math.round(Math.log10(v))); }, yfmt: function (v) { return pw(Math.round(Math.log10(v))); }, xlabel: "λ" });
      p.fn(function (l) { return parts(l)[0]; }, "ln c1");
      p.fn(function (l) { return parts(l)[1]; }, "ln c2");
      p.fn(function (l) { return parts(l)[2]; }, "ln ck");
      var best = 1e-3, bv = Infinity;
      for (var i = 0; i <= 600; i++) { var l = Math.pow(10, -3 + 6 * i / 600), v = parts(l)[2]; if (v < bv) { bv = v; best = l; } }
      p.poly([[L, 1e-2], [L, 1e3]], "ln cm thin dash");
      var q = parts(L);
      p.dot(L, q[2], 4.5, "fk"); p.dot(best, bv, 4, "f3");
      var q0 = parts(1e-12);
      ro.textContent = "λ = " + fmt(L, 3) + " : biais² " + fmt(q[0]) + " + variance " + fmt(q[1]) + " = " + fmt(q[2]) +
        "    (MCO, λ = 0 : " + fmt(q0[2], 1) + " ; meilleur λ ≈ " + fmt(best, 2) + " → " + fmt(bv) + ")";
    }
    draw(); redrawers.push(draw);
  };

  /* --- 5. Erreur d'apprentissage, erreur de prédiction, Cp/AIC et BIC --- */
  WIDGETS.optimisme = function (box) {
    var s = scaffold(box, box.getAttribute("data-title") || "Modèles emboîtés de dimension d : l'erreur d'apprentissage ment, Cp/AIC corrige");
    var D = 30, sig2 = 1;
    function bias(d) { return 3 * Math.exp(-d / 2.5); }
    var p = new Plot(s.svg, { x: [0, D], y: [0, 4.2], w: 560, h: 340, label: "Optimisme" });
    var nS = slider(s.controls, "n", 20, 400, 5, 60, draw);
    var bic = false;
    checkbox(s.controls, "afficher BIC", false, function (e) { bic = e.target.checked; draw(); });
    var ro = readout(s.controls);
    function draw() {
      var n = nS.get(); nS.out.textContent = n;
      legend(s.legend, [["--s1", "erreur d'apprentissage E‖Y − Xβ̂‖²ₙ"], ["--s2", "erreur de prédiction + σ²"], ["--s3", "Cp/AIC : apprentissage + 2σ²d/n"]].concat(bic ? [["--s5", "BIC : apprentissage + σ² log(n) d/n"]] : []));
      p.clear();
      p.axes({ xticks: [0, 5, 10, 15, 20, 25, 30], yticks: [0, 1, 2, 3, 4], xlabel: "dimension d du modèle", yd: 0 });
      var tr = function (d) { return bias(d) + sig2 * (1 - d / n); };
      var te = function (d) { return bias(d) + sig2 + sig2 * d / n; };
      var pts = function (f) { var a = []; for (var d = 0; d <= D; d++) a.push([d, f(d)]); return a; };
      p.poly(pts(tr), "ln c1"); p.poly(pts(te), "ln c2");
      p.poly(pts(function (d) { return tr(d) + 2 * sig2 * d / n; }), "ln c3 dash");
      if (bic) p.poly(pts(function (d) { return tr(d) + sig2 * Math.log(n) * d / n; }), "ln c5 dash");
      var am = function (f) { var bd = 0, bv = Infinity; for (var d = 0; d <= D; d++) { var v = f(d); if (v < bv) { bv = v; bd = d; } } return bd; };
      var dA = am(te), dB = am(function (d) { return tr(d) + sig2 * Math.log(n) * d / n; });
      p.dot(dA, te(dA), 5, "f2");
      if (bic) p.dot(dB, tr(dB) + sig2 * Math.log(n) * dB / n, 5, "f5");
      ro.textContent = "n = " + n + " : l'erreur d'apprentissage décroît toujours (meilleure en d = " + D + ") ; Cp/AIC (vert) recouvre exactement l'erreur de prédiction (orange) en moyenne et est minimal en d = " + dA +
        (bic ? " ; BIC choisit d = " + dB + " (log n = " + fmt(Math.log(n), 2) + " > 2)" : "");
    }
    draw(); redrawers.push(draw);
  };

  /* --- 6. Boules « bridge » ‖β‖γ ≤ 1 --- */
  WIDGETS.bridge = function (box) {
    var s = scaffold(box, box.getAttribute("data-title") || "La boule {|β₁|^γ + |β₂|^γ ≤ 1} selon γ");
    var p = new Plot(s.svg, { x: [-1.4, 1.4], y: [-1.4, 1.4], w: 400, h: 400, pad: { l: 26, r: 10, t: 10, b: 24 }, label: "Boules bridge" });
    var g = slider(s.controls, "γ", 0.2, 4, 0.05, 0.5, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s5", "γ choisi"], ["--s2", "γ = 1 (Lasso)"], ["--s1", "γ = 2 (Ridge)"]]);
    function ball(gm) {
      var pts = [];
      for (var i = 0; i <= 400; i++) {
        var t = 2 * Math.PI * i / 400, c = Math.cos(t), sn = Math.sin(t);
        pts.push([Math.sign(c) * Math.pow(Math.abs(c), 2 / gm), Math.sign(sn) * Math.pow(Math.abs(sn), 2 / gm)]);
      }
      return pts;
    }
    function draw() {
      var gm = g.get(); g.out.textContent = fmt(gm);
      p.clear(); p.axes({ xticks: [-1, 1], yticks: [-1, 1], cross: true });
      p.poly(ball(1), "ln c2 thin dash"); p.poly(ball(2), "ln c1 thin dash");
      p.poly(ball(gm), "ln c5 a5");
      ro.textContent = gm < 1 ? "γ < 1 : boule NON convexe (étoilée), pointes très marquées sur les axes → très parcimonieux mais problème difficile" :
        (gm === 1 ? "γ = 1 : convexe ET pointue sur les axes → parcimonieux et calculable" :
          "γ " + (gm > 1 ? "> 1" : "") + " : convexe et lisse (pas de coin) → aucun zéro exact en général");
    }
    draw(); redrawers.push(draw);
  };

  /* --- 7. Sous-gradient de |u| --- */
  WIDGETS.sousgradient = function (box) {
    var s = scaffold(box, box.getAttribute("data-title") || "Sous-gradient de φ(u) = |u| : une droite qui passe par (u₀, |u₀|) et reste sous le graphe");
    var p = new Plot(s.svg, { x: [-2, 2], y: [-1, 2.2], w: 520, h: 320, label: "Sous-gradient" });
    var u0 = slider(s.controls, "u₀", -1.5, 1.5, 0.05, 0, draw);
    var gs = slider(s.controls, "pente g", -2, 2, 0.05, 0.5, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--text", "φ(u) = |u|"], ["--s3", "droite valide (g ∈ ∂φ(u₀))"], ["--s2", "droite non valide"]]);
    function draw() {
      var a = u0.get(), g = gs.get(); u0.out.textContent = fmt(a); gs.out.textContent = fmt(g);
      var ok;
      if (a > 1e-9) ok = Math.abs(g - 1) < 1e-9; else if (a < -1e-9) ok = Math.abs(g + 1) < 1e-9; else ok = Math.abs(g) <= 1 + 1e-9;
      p.clear(); p.axes({ xticks: [-2, -1, 0, 1, 2], yticks: [-1, 1, 2], cross: true });
      p.fn(function (u) { return Math.abs(u); }, "ln ck");
      p.fn(function (u) { return Math.abs(a) + g * (u - a); }, "ln " + (ok ? "c3" : "c2"));
      p.dot(a, Math.abs(a), 5, "fk");
      var sd = a > 1e-9 ? "{1}" : (a < -1e-9 ? "{−1}" : "[−1, 1]");
      ro.textContent = "∂|·|(" + fmt(a) + ") = " + sd + "  ·  g = " + fmt(g) + (ok ? "  ✓ la droite reste sous le graphe" : "  ✗ la droite passe au-dessus du graphe quelque part");
    }
    draw(); redrawers.push(draw);
  };

  /* --- 8. Maximum de p gaussiennes : pourquoi √(2 log p) --- */
  function gauss() { var u = 1 - Math.random(), v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  WIDGETS.maxgauss = function (box) {
    var s = scaffold(box, box.getAttribute("data-title") || "Le maximum de p gaussiennes N(0,1) indépendantes grandit comme √(2 log p) : très lentement");
    var ps = [1, 3, 10, 30, 100, 300, 1000, 3000, 10000];
    var p = new Plot(s.svg, { x: [0.7, 15000], y: [0, 5], xlog: true, w: 560, h: 330, label: "Maximum de gaussiennes" });
    var R = 40, data = null;
    var btn = document.createElement("button"); btn.type = "button"; btn.className = "tool-btn"; btn.textContent = "Nouveau tirage";
    btn.addEventListener("click", function () { simulate(); draw(); });
    s.controls.appendChild(btn);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "max |Zⱼ| sur 40 tirages (un point = un tirage)"], ["--s2", "√(2 log p)"], ["--s3", "√(2 log(2p))"]]);
    function simulate() {
      data = ps.map(function (pp) {
        var r = [];
        for (var k = 0; k < R; k++) { var m = 0; for (var j = 0; j < pp; j++) { var z = Math.abs(gauss()); if (z > m) m = z; } r.push(m); }
        return r;
      });
    }
    function draw() {
      if (!data) simulate();
      p.clear();
      p.axes({ xticks: [1, 10, 100, 1000, 10000], yticks: [1, 2, 3, 4, 5], xfmt: function (v) { return String(v).replace(/(\d)(?=(\d{3})+$)/g, "$1 "); }, xlabel: "p (nombre de variables, échelle log)" });
      p.fn(function (x) { return Math.sqrt(2 * Math.log(Math.max(x, 1))); }, "ln c2", 200);
      p.fn(function (x) { return Math.sqrt(2 * Math.log(2 * x)); }, "ln c3 dash", 200);
      var above = 0, tot = 0;
      data.forEach(function (r, i) {
        r.forEach(function (m, k) {
          var jit = Math.pow(10, (k / R - 0.5) * 0.12);
          p.dot(ps[i] * jit, m, 2.2, "f1");
          tot++; if (m > Math.sqrt(2 * Math.log(2 * ps[i]))) above++;
        });
      });
      ro.textContent = above + " tirage(s) sur " + tot + " dépassent √(2 log(2p)). Le maximum grandit, mais très lentement : comme √(log p).";
    }
    draw(); redrawers.push(draw);
  };

  /* --- 9. Fonction logistique --- */
  WIDGETS.logistique = function (box) {
    var s = scaffold(box, box.getAttribute("data-title") || "Régression logistique : P(Y = 1 | x) = 1 / (1 + exp(−(β₀ + β₁x)))");
    var p = new Plot(s.svg, { x: [-4, 4], y: [-0.1, 1.1], w: 560, h: 300, label: "Fonction logistique" });
    var b0 = slider(s.controls, "β₀", -3, 3, 0.1, 0, draw);
    var b1 = slider(s.controls, "β₁", -4, 4, 0.1, 1.5, draw);
    var ro = readout(s.controls);
    var xs = [-3.2, -2.5, -2.1, -1.4, -0.9, -0.5, -0.2, 0.3, 0.6, 1.1, 1.5, 2.2, 2.8, 3.3];
    var ys = [0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1];
    legend(s.legend, [["--s1", "μ(x) = P(Y = 1 | x)"], ["--s2", "droite β₀ + β₁x (ce que verrait un modèle linéaire)"], ["--text", "observations (0 ou 1)"]]);
    function draw() {
      var a = b0.get(), c = b1.get(); b0.out.textContent = fmt(a, 1); b1.out.textContent = fmt(c, 1);
      p.clear(); p.axes({ xticks: [-4, -2, 0, 2, 4], yticks: [0, 0.5, 1], yd: 1, xlabel: "x" });
      p.clip();
      p.fn(function (x) { return a + c * x; }, "ln c2 thin dash");
      p.unclip();
      p.fn(function (x) { return 1 / (1 + Math.exp(-(a + c * x))); }, "ln c1");
      var ll = 0;
      xs.forEach(function (x, i) {
        p.dot(x, ys[i], 4, "fk");
        var m = 1 / (1 + Math.exp(-(a + c * x)));
        ll += ys[i] ? Math.log(m) : Math.log(1 - m);
      });
      ro.textContent = "log-vraisemblance des 14 points : " + fmt(ll) + "  (plus elle est grande, mieux la courbe explique les données)";
    }
    draw(); redrawers.push(draw);
  };

  /* --- 10. Règles de seuillage des variantes du Lasso (design orthonormé) --- */
  WIDGETS.variantes = function (box) {
    var s = scaffold(box, box.getAttribute("data-title") || "Design orthonormé : chaque variante du Lasso est une règle b ↦ β̂ coordonnée par coordonnée");
    var p = new Plot(s.svg, { x: [-3, 3], y: [-3, 3], w: 560, h: 400, label: "Règles de seuillage" });
    var lam = slider(s.controls, "λ", 0.2, 3, 0.05, 2, draw);
    var del = slider(s.controls, "δ (relaxé)", 0, 1, 0.05, 0.3, draw);
    var l2 = slider(s.controls, "λ₂ (elastic net)", 0, 2, 0.05, 0.5, draw);
    var rules = [
      { k: "lasso", name: "Lasso", c: "c2", v: "--s2", on: true, f: function (b, L) { return soft(b, L / 2); } },
      { k: "ls", name: "LSLasso = relaxé δ = 0 (dur)", c: "c3", v: "--s3", on: true, f: function (b, L) { return Math.abs(b) > L / 2 ? b : 0; } },
      { k: "relax", name: "Lasso relaxé (δ)", c: "c4", v: "--s4", on: false, f: function (b, L, d) { return Math.abs(b) > L / 2 ? soft(b, d * L / 2) : 0; } },
      { k: "adapt", name: "Lasso adaptatif (ωⱼ = 1/|bⱼ|)", c: "c5", v: "--s5", on: false, f: function (b, L) { return b === 0 ? 0 : soft(b, L / (2 * Math.abs(b))); } },
      { k: "enet", name: "Elastic net", c: "c6", v: "--s6", on: false, f: function (b, L, d, m) { return soft(b, L / 2) / (1 + m); } },
      { k: "ridge", name: "Ridge", c: "c1", v: "--s1", on: false, f: function (b, L) { return b / (1 + L); } },
    ];
    var boxes = document.createElement("div"); boxes.className = "controls";
    rules.forEach(function (r) { checkbox(boxes, '<span style="color:var(' + r.v + ');font-weight:700">■</span> ' + r.name, r.on, function (e) { r.on = e.target.checked; draw(); }); });
    s.controls.appendChild(boxes);
    var ro = readout(s.controls);
    function draw() {
      var L = lam.get(), d = del.get(), m = l2.get();
      lam.out.textContent = fmt(L); del.out.textContent = fmt(d); l2.out.textContent = fmt(m);
      p.clear(); p.axes({ xticks: [-3, -2, -1, 0, 1, 2, 3], yticks: [-3, -2, -1, 1, 2, 3], cross: true, xlabel: "b = Xⱼᵀ Y (moindres carrés)", ylabel: "β̂ⱼ" });
      p.fn(function (x) { return x; }, "ln cm thin dash");
      rules.forEach(function (r) { if (r.on) p.fn(function (b) { return r.f(b, L, d, m); }, "ln " + r.c, 1200); });
      ro.textContent = "Pointillés gris : l'identité (aucun biais). Plus une courbe colle à l'identité pour les grands |b|, moins elle biaise les gros coefficients.";
    }
    draw(); redrawers.push(draw);
  };

  /* --- 11. Ellipses et cône : la condition de valeurs propres restreintes en dimension 2 --- */
  WIDGETS.cone = function (box) {
    var s = scaffold(box, box.getAttribute("data-title") || "Le cône « ‖δ hors de J₀‖₁ ≤ c ‖δ dans J₀‖₁ » avec J₀ = {1}, en dimension 2");
    var p = new Plot(s.svg, { x: [-2, 2], y: [-2, 2], w: 420, h: 420, pad: { l: 26, r: 10, t: 10, b: 24 }, label: "Cône" });
    var cS = slider(s.controls, "c", 0.5, 5, 0.1, 3, draw);
    var aS = slider(s.controls, "direction du noyau de X (degrés)", 0, 180, 1, 80, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "cône : |δ₂| ≤ c|δ₁|"], ["--s2", "noyau de X (Xδ = 0)"]]);
    function draw() {
      var c = cS.get(), a = aS.get() * Math.PI / 180; cS.out.textContent = fmt(c, 1); aS.out.textContent = Math.round(aS.get()) + "°";
      p.clear(); p.axes({ xticks: [-1, 1], yticks: [-1, 1], cross: true, xlabel: "δ₁ (dans J₀)", ylabel: "δ₂ (hors J₀)" });
      p.clip();
      p.poly([[0, 0], [3, 3 * c], [3, -3 * c], [0, 0]], "ln c3 a3 thin");
      p.poly([[0, 0], [-3, 3 * c], [-3, -3 * c], [0, 0]], "ln c3 a3 thin");
      p.poly([[-3 * Math.cos(a), -3 * Math.sin(a)], [3 * Math.cos(a), 3 * Math.sin(a)]], "ln c2");
      p.unclip();
      var inCone = Math.abs(Math.sin(a)) <= c * Math.abs(Math.cos(a)) + 1e-9;
      var inOther = Math.abs(Math.cos(a)) <= c * Math.abs(Math.sin(a)) + 1e-9; // cône de J₀ = {2}
      ro.textContent = inCone ? "Le noyau entre dans le cône de J₀ = {1} : un δ ≠ 0 de ce cône vérifie Xδ = 0, donc κ = 0 et RE échoue." :
        "Pour J₀ = {1}, le noyau évite le cône : sur ce cône, ‖Xδ‖ ne s'annule qu'en 0. Mais RE exige cela pour TOUS les J₀ de taille ≤ s" +
        (inOther ? " : ici le noyau est dans le cône de J₀ = {2} (|δ₁| ≤ c|δ₂|), donc RE(1, c) échoue quand même. En dimension 2 avec c ≥ 1, les deux cônes recouvrent le plan : RE n'a d'intérêt qu'en grande dimension." :
          " ; ici il évite aussi le cône de J₀ = {2} (possible seulement si c < 1), donc RE(1, c) est satisfaite bien que X ne soit pas injective.");
    }
    draw(); redrawers.push(draw);
  };

  document.querySelectorAll("[data-widget]").forEach(function (box) {
    var f = WIDGETS[box.getAttribute("data-widget")];
    if (f) { try { f(box); } catch (e) { box.insertAdjacentHTML("afterbegin", "<p class='small muted'>Figure indisponible : " + e.message + "</p>"); } }
  });
})();
