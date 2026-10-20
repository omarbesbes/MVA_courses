// widgets/Lesson04.js — interactive figures of Lesson 4 (duality).
// Inserted by build.mjs inside the scope of app.js: uses el, Plot, scaffold, slider, select, button, checkbox, readout,
// legend, fmt, frac, matStr, mulberry32, gaussRand, svgPoint, addSvg, Line1D, quantiles, w2q, densityFromQ, curve,
// areaPts, MQ, US, gpdf, redrawers, WIDGETS. Helpers of this file are prefixed l4.

  /* ---------- small numerical helpers (prefixed, to avoid clashes with other pages) ---------- */
  function l4erf(x) { // Abramowitz-Stegun 7.1.26, |error| < 1.5e-7
    var s = x < 0 ? -1 : 1; x = Math.abs(x);
    var t = 1 / (1 + 0.3275911 * x);
    var y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
    return s * y;
  }
  function l4Phi(z) { return 0.5 * (1 + l4erf(z / Math.SQRT2)); }
  function l4sign(v, tol) { return v > tol ? 1 : (v < -tol ? -1 : 0); }
  function l4clear(svg) { while (svg.firstChild) svg.removeChild(svg.firstChild); return el("g", {}, svg); }
  function l4txt(g, x, y, s, cls, anchor) { var t = el("text", { x: x, y: y, "class": cls || "tx-s", "text-anchor": anchor || "start" }, g); t.textContent = s; return t; }

  /* =====================================================================================
     1. The discrete dual: prices, admissibility, complementary slackness (section 1)
     ===================================================================================== */
  WIDGETS.l4dual = function (box) {
    var s = scaffold(box, "A price list below the costs: the bill is a lower bound, equal to the optimal cost exactly on the contacts");
    var W = 680, H = 300;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Table of routes with costs, prices and slacks, and a gauge comparing the bill with the optimal cost");
    var EX = {
      ship: { C: [[4, 8, 2], [6, 7, 8], [5, 4, 3]], a: [0.5, 0.3, 0.2], b: [0.4, 0.4, 0.2], P: [[0.3, 0, 0.2], [0.1, 0.2, 0], [0, 0.2, 0]], L: 4.4, f: [1, 3, 0], g: [3, 4, 1] },
      degen: { C: [[1, 3], [2, 5]], a: [0.5, 0.5], b: [0.5, 0.5], P: [[0, 0.5], [0.5, 0]], L: 2.5, f: [0, 1.5], g: [0.5, 3] }
    };
    var exSel = select(s.controls, "Example", [["ship", "shipping (3 × 3)"], ["degen", "degenerate (2 × 2)"]], "ship", function () { setEx(); });
    var modeSel = select(s.controls, "Delivery prices g", [["best", "best response g = f^C"], ["free", "free (sliders)"]], "best", function () { showSliders(); draw(); });
    var fS = [], gS = [], k;
    for (k = 0; k < 3; k++) fS.push(slider(s.controls, "f<sub>" + (k + 1) + "</sub>", -2, 6, 0.1, 0, draw));
    for (k = 0; k < 3; k++) gS.push(slider(s.controls, "g<sub>" + (k + 1) + "</sub>", -2, 8, 0.1, 0, draw));
    button(s.controls, "Optimal prices", function () { var E = EX[exSel.value]; E.f.forEach(function (v, i) { fS[i].set(v); }); E.g.forEach(function (v, j) { gS[j].set(v); }); draw(); });
    button(s.controls, "Zero prices", function () { fS.forEach(function (x) { x.set(0); }); gS.forEach(function (x) { x.set(0); }); draw(); });
    button(s.controls, "f ← best response to g", function () {
      var E = EX[exSel.value], g = cur().g;
      E.a.forEach(function (_, i) { var m = Infinity; E.b.forEach(function (__, j) { m = Math.min(m, E.C[i][j] - g[j]); }); fS[i].set(Math.round(m * 10) / 10); });
      draw();
    });
    button(s.controls, "Gauge: f + 1, g − 1", function () { var E = EX[exSel.value], c = cur(); E.a.forEach(function (_, i) { fS[i].set(c.f[i] + 1); }); E.b.forEach(function (_, j) { gS[j].set(c.g[j] - 1); }); if (modeSel.value === "best") modeSel.value = "free"; showSliders(); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "contact: fᵢ + gⱼ = Cᵢⱼ"], ["--s2", "route billed above its cost (refused)"], ["--text", "dots: the optimal plan P*"]]);
    function showSliders() {
      var E = EX[exSel.value];
      fS.forEach(function (x, i) { x.input.parentNode.style.display = i < E.a.length ? "" : "none"; });
      gS.forEach(function (x, j) { x.input.parentNode.style.display = (modeSel.value === "free" && j < E.b.length) ? "" : "none"; });
    }
    function cur() {
      var E = EX[exSel.value], f = [], g = [], i, j;
      for (i = 0; i < E.a.length; i++) f.push(fS[i].get());
      if (modeSel.value === "best") {
        for (j = 0; j < E.b.length; j++) { var m = Infinity; for (i = 0; i < E.a.length; i++) m = Math.min(m, E.C[i][j] - f[i]); g.push(m); gS[j].set(m); }
      } else for (j = 0; j < E.b.length; j++) g.push(gS[j].get());
      return { f: f, g: g };
    }
    function setEx() { var E = EX[exSel.value]; E.a.forEach(function (_, i) { fS[i].set(0); }); E.b.forEach(function (_, j) { gS[j].set(0); }); showSliders(); draw(); }
    function draw() {
      var E = EX[exSel.value], c = cur(), f = c.f, g = c.g, n = E.a.length, m = E.b.length, i, j;
      fS.forEach(function (x, ii) { x.out.textContent = ii < n ? fmt(x.get(), 1) : ""; });
      gS.forEach(function (x, jj) { x.out.textContent = jj < m ? fmt(x.get(), 1) : ""; });
      var gg = l4clear(s.svg);
      var x0 = 120, y0 = 54, cw = 118, ch = 74;
      var bill = 0, gap = 0, bad = [], contacts = 0, onContacts = true;
      for (i = 0; i < n; i++) bill += f[i] * E.a[i];
      for (j = 0; j < m; j++) bill += g[j] * E.b[j];
      for (j = 0; j < m; j++) {
        var hx = x0 + j * cw + cw / 2;
        l4txt(gg, hx, 18, "F" + "₁₂₃"[j], "tx-b", "middle");
        l4txt(gg, hx, 33, "b = " + fmt(E.b[j], 1), "tx-s t1", "middle");
        l4txt(gg, hx, 47, "g = " + fmt(g[j], 1), "tx-s t1", "middle");
      }
      for (i = 0; i < n; i++) {
        var hy = y0 + i * ch + ch / 2;
        l4txt(gg, 60, hy - 10, "W" + "₁₂₃"[i], "tx-b", "middle");
        l4txt(gg, 60, hy + 5, "a = " + fmt(E.a[i], 1), "tx-s t2", "middle");
        l4txt(gg, 60, hy + 19, "f = " + fmt(f[i], 1), "tx-s t2", "middle");
        for (j = 0; j < m; j++) {
          var sl = E.C[i][j] - f[i] - g[j], X = x0 + j * cw, Y = y0 + i * ch;
          var st = Math.abs(sl) < 1e-9 ? "contact" : (sl < 0 ? "bad" : "ok");
          if (st === "contact") contacts++;
          if (st === "bad") bad.push("W" + (i + 1) + "→F" + (j + 1));
          gap += E.P[i][j] * sl;
          if (E.P[i][j] > 1e-12 && st !== "contact") onContacts = false;
          el("rect", { x: X + 3, y: Y + 3, width: cw - 6, height: ch - 6, rx: 6, "class": st === "contact" ? "a3" : (st === "bad" ? "a2" : "am") }, gg);
          el("rect", { x: X + 3, y: Y + 3, width: cw - 6, height: ch - 6, rx: 6, "class": "ln nofill " + (st === "contact" ? "c3" : (st === "bad" ? "c2" : "cm hair")), "stroke-width": st === "ok" ? 0.9 : 2 }, gg);
          l4txt(gg, X + 14, Y + 26, String(E.C[i][j]), "tx-b", "start");
          l4txt(gg, X + 14, Y + 44, "f + g = " + fmt(f[i] + g[j], 1), "tx-s", "start");
          l4txt(gg, X + 14, Y + 60, "slack " + fmt(sl, 1), "tx-s", "start");
          if (E.P[i][j] > 1e-12) {
            el("circle", { cx: X + cw - 26, cy: Y + 28, r: (4 + 16 * Math.sqrt(E.P[i][j])).toFixed(1), "class": "fk", "fill-opacity": 0.85 }, gg);
            l4txt(gg, X + cw - 26, Y + 62, frac(E.P[i][j]), "tx-s", "middle");
          }
        }
      }
      // gauge
      var gx = 520, gw = 46, gy0 = 40, gh = 220, top = Math.max(E.L * 1.25, bill * 1.05, 1);
      var Yg = function (v) { return gy0 + gh - Math.max(0, Math.min(v, top)) / top * gh; };
      el("rect", { x: gx, y: gy0, width: gw, height: gh, "class": "ln cm hair nofill" }, gg);
      var feas = bad.length === 0;
      el("rect", { x: gx + 6, y: Yg(bill), width: gw - 12, height: Math.max(0, gy0 + gh - Yg(bill)), "class": feas ? "f3" : "f2", "fill-opacity": 0.8 }, gg);
      el("line", { x1: gx - 8, x2: gx + gw + 8, y1: Yg(E.L), y2: Yg(E.L), "class": "ln ck thin dash" }, gg);
      l4txt(gg, gx + gw + 12, Yg(E.L) + 4, "optimal cost " + fmt(E.L, 1), "tx-s", "start");
      l4txt(gg, gx + gw + 12, Math.min(Yg(bill), gy0 + gh - 8) + (Math.abs(Yg(bill) - Yg(E.L)) < 16 ? 18 : 4), "bill " + fmt(bill, 2), feas ? "tx-s t3" : "tx-s t2", "start");
      l4txt(gg, gx + gw / 2, gy0 + gh + 18, "bill", "tx-s", "middle");
      var txt = "bill ⟨f,a⟩ + ⟨g,b⟩ = " + fmt(bill, 2) + "   ·   optimal cost L_C = " + fmt(E.L, 1);
      if (feas) {
        txt += "\nadmissible prices (every slack ≥ 0): the bill is a lower bound, " + fmt(bill, 2) + " ≤ " + fmt(E.L, 1) +
          ".  Gap Σ P*ᵢⱼ·slackᵢⱼ = " + fmt(gap, 2) + (onContacts && Math.abs(gap) < 1e-9 ? "  → zero gap: the plan lives on contacts, both are optimal ✓" : "  → the optimal plan uses routes with positive slack");
      } else {
        txt += "\nNOT admissible: " + bad.join(", ") + " billed above cost. The operator refuses; such a bill proves nothing.";
      }
      txt += "\ncontacts: " + contacts + " of " + (n * m) + " routes";
      ro.textContent = txt;
    }
    setEx(); redrawers.push(draw);
  };

  /* =====================================================================================
     2. The c-transform in 1D: lower envelope, double transform, idempotence (section 3)
     ===================================================================================== */
  WIDGETS.l4ctrans = function (box) {
    var s = scaffold(box, "c-transforms in 1D: drag the prices f(xₖ); the transform is the lower envelope, the double transform raises useless prices");
    var top = new Plot(s.svg, { x: [-2.2, 2.2], y: [-1.8, 2.8], w: 680, h: 230, pad: { l: 40, r: 16, t: 16, b: 26 }, label: "Source side: prices f at seven points and the double transform" });
    var botSvg = addSvg(box, s.svg);
    var bot = new Plot(botSvg, { x: [-2.2, 2.2], y: [-2.8, 2.6], w: 680, h: 230, pad: { l: 40, r: 16, t: 16, b: 26 }, label: "Target side: sections and their lower envelope f^c" });
    var costSel = select(s.controls, "Cost", [["sq", "c = |x − y|²"], ["abs", "c = |x − y|"], ["bil", "c = −x·y"]], "sq", draw);
    var secChk = checkbox(s.controls, "show the sections", true, draw);
    button(s.controls, "Replace f by f^cc̄", function () { var r = compute(); for (var k = 0; k < K; k++) F[k] = Math.round(r.fccAt[k] * 1000) / 1000; draw(); });
    button(s.controls, "Random f", function () { var rng = mulberry32(seed++); for (var k = 0; k < K; k++) F[k] = Math.round((-1 + 2.6 * rng()) * 100) / 100; draw(); });
    button(s.controls, "Reset", function () { F = F0.slice(); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "prices f(xₖ) (drag)"], ["--muted", "sections y ↦ c(xₖ, y) − f(xₖ)"], ["--s1", "f^c (lower envelope)"], ["--s3", "f^cc̄ (double transform)"]]);
    var K = 7, XK = [], k, seed = 5;
    for (k = 0; k < K; k++) XK.push(-1.8 + 3.6 * k / (K - 1));
    var F0 = [0.2, 1.1, -0.3, 0.9, 0.4, 1.6, -0.1], F = F0.slice();
    var N = 441, GR = [];
    for (k = 0; k < N; k++) GR.push(-2.2 + 4.4 * k / (N - 1));
    function cost(x, y) { var c = costSel.value; return c === "sq" ? (x - y) * (x - y) : (c === "abs" ? Math.abs(x - y) : -x * y); }
    function compute() {
      var fc = new Float64Array(N), fcc = new Float64Array(N), fccc = new Float64Array(N), i, j, kk, v, m;
      for (j = 0; j < N; j++) { m = Infinity; for (kk = 0; kk < K; kk++) { v = cost(XK[kk], GR[j]) - F[kk]; if (v < m) m = v; } fc[j] = m; }
      for (i = 0; i < N; i++) { m = Infinity; for (j = 0; j < N; j++) { v = cost(GR[i], GR[j]) - fc[j]; if (v < m) m = v; } fcc[i] = m; }
      var fccAt = [];
      for (kk = 0; kk < K; kk++) { m = Infinity; for (j = 0; j < N; j++) { v = cost(XK[kk], GR[j]) - fc[j]; if (v < m) m = v; } fccAt.push(m); }
      for (j = 0; j < N; j++) { m = Infinity; for (i = 0; i < N; i++) { v = cost(GR[i], GR[j]) - fcc[i]; if (v < m) m = v; } fccc[j] = m; }
      return { fc: fc, fcc: fcc, fccc: fccc, fccAt: fccAt };
    }
    var drag = -1;
    s.svg.addEventListener("pointerdown", function (e) {
      var p = svgPoint(s.svg, e), best = -1, bd = 22;
      for (var kk = 0; kk < K; kk++) { var d = Math.hypot(p.x - top.tx(XK[kk]), p.y - top.ty(F[kk])); if (d < bd) { bd = d; best = kk; } }
      if (best >= 0) { drag = best; e.preventDefault(); try { s.svg.setPointerCapture(e.pointerId); } catch (err) {} }
    });
    s.svg.addEventListener("pointermove", function (e) {
      if (drag < 0) return;
      e.preventDefault();
      var p = svgPoint(s.svg, e);
      F[drag] = Math.max(-1.6, Math.min(2.6, Math.round(top.iy(p.y) * 100) / 100));
      draw();
    });
    function endDrag() { drag = -1; }
    s.svg.addEventListener("pointerup", endDrag); s.svg.addEventListener("pointercancel", endDrag);
    function draw() {
      var r = compute(), i, kk;
      // top: source side
      top.clear();
      top.axes({ xticks: [-2, -1, 0, 1, 2], yticks: [-1, 0, 1, 2], xfmt: function (v) { return fmt(v, 0); }, yfmt: function (v) { return fmt(v, 0); } });
      top.clip();
      var pts = []; for (i = 0; i < N; i++) pts.push([GR[i], r.fcc[i]]);
      top.poly(pts, "ln c3");
      top.unclip();
      var raised = [];
      for (kk = 0; kk < K; kk++) {
        var gap = r.fccAt[kk] - F[kk];
        if (gap > 2e-3) { top.seg(XK[kk], F[kk], XK[kk], r.fccAt[kk], "ln c3 thin dot"); raised.push("x" + "₁₂₃₄₅₆₇"[kk] + " (+" + fmt(gap, 2) + ")"); }
        top.dot(XK[kk], r.fccAt[kk], 4.5, "fs");
        el("circle", { cx: top.tx(XK[kk]), cy: top.ty(r.fccAt[kk]), r: 4.5, "class": "ln c3 thin nofill" }, top.g);
        top.dot(XK[kk], F[kk], 6.5, "f2 drag");
      }
      top.text(-2.15, 2.5, "source side: f (dots) and f^cc̄ (green), on 𝒳", "tx-s", "start");
      // bottom: target side
      bot.clear();
      bot.axes({ xticks: [-2, -1, 0, 1, 2], yticks: [-2, -1, 0, 1, 2], xfmt: function (v) { return fmt(v, 0); }, yfmt: function (v) { return fmt(v, 0); } });
      bot.clip();
      if (secChk.checked) for (kk = 0; kk < K; kk++) bot.fn(function (y) { return cost(XK[kk], y) - F[kk]; }, "ln cm thin dash", 200);
      pts = []; for (i = 0; i < N; i++) pts.push([GR[i], r.fc[i]]);
      bot.poly(pts, "ln c1");
      bot.unclip();
      if (costSel.value !== "bil") for (kk = 0; kk < K; kk++) bot.dot(XK[kk], -F[kk], 4, "f2");
      bot.text(-2.15, 2.25, "target side: f^c(y) = minₖ c(xₖ, y) − f(xₖ), on 𝒴", "tx-s", "start");
      var maxId = 0, minGap = Infinity;
      for (i = 0; i < N; i++) maxId = Math.max(maxId, Math.abs(r.fccc[i] - r.fc[i]));
      for (kk = 0; kk < K; kk++) minGap = Math.min(minGap, r.fccAt[kk] - F[kk]);
      var t = "min over the seven points of f^cc̄ − f = " + fmt(minGap, 3) + "  (≥ 0: identity (ii))";
      t += "\nraised prices: " + (raised.length ? raised.join(", ") + " — these values of f were not c-concave" : "none — f is c-concave (f = f^cc̄ on the seven points)");
      t += "\nmax over y of |f^cc̄c − f^c| = " + (maxId < 5e-4 ? "0.000" : fmt(maxId, 3)) + "  (identity (iv); computed on a grid of " + N + " points)";
      if (costSel.value === "abs") t += "\nwith c = |x − y|: f^c is 1-Lipschitz and f^cc̄ = −f^c";
      if (costSel.value === "bil") t += "\nwith c = −xy: f^c is concave, piecewise linear (an infimum of lines)";
      ro.textContent = t;
    }
    draw(); redrawers.push(draw);
  };

  /* =====================================================================================
     3. W1 on the line: area between CDFs, optimal 1-Lipschitz witness (section 5)
     ===================================================================================== */
  function l4cdfComp(comps, x) {
    var s = 0;
    comps.forEach(function (c) {
      if (c.t === "d") s += x >= c.x ? c.w : 0;
      else if (c.t === "g") s += c.w * l4Phi((x - c.m) / c.s);
      else s += c.w * Math.min(1, Math.max(0, (x - c.a) / (c.b - c.a)));
    });
    return s;
  }
  function l4pdfComp(comps, x) {
    var s = 0;
    comps.forEach(function (c) {
      if (c.t === "g") s += c.w * gpdf(x, c.m, c.s);
      else if (c.t === "u") s += x >= c.a && x <= c.b ? c.w / (c.b - c.a) : 0;
    });
    return s;
  }
  function l4shift(comps, t) {
    return comps.map(function (c) {
      if (c.t === "d") return { t: "d", x: c.x + t, w: c.w };
      if (c.t === "g") return { t: "g", m: c.m + t, s: c.s, w: c.w };
      return { t: "u", a: c.a + t, b: c.b + t, w: c.w };
    });
  }
  WIDGETS.l4w1 = function (box) {
    var s = scaffold(box, "W₁ on the line: the area between the CDFs, and the 1-Lipschitz witness that certifies it");
    var PRE = {
      atoms: { L: -2.5, R: 5.5, ymax: 1.25, a: [{ t: "d", x: 0, w: 0.5 }, { t: "d", x: 3, w: 0.5 }], b: [{ t: "u", a: 1, b: 2, w: 1 }] },
      gauss: { L: -4.5, R: 6, ymax: 0.75, a: [{ t: "g", m: 0, s: 0.6, w: 1 }], b: [{ t: "g", m: 1, s: 1.3, w: 1 }] },
      bimodal: { L: -4.5, R: 5.5, ymax: 0.9, a: [{ t: "g", m: -1.5, s: 0.4, w: 0.5 }, { t: "g", m: 1.5, s: 0.4, w: 0.5 }], b: [{ t: "g", m: 0, s: 0.7, w: 1 }] }
    };
    var mk = function (lab) { return { pad: { l: 40, r: 16, t: 12, b: 24 }, label: lab }; };
    var o1 = mk("The two measures"); o1.x = [0, 1]; o1.y = [0, 1]; o1.w = 680; o1.h = 150;
    var top = new Plot(s.svg, o1);
    var midSvg = addSvg(box, s.svg), botSvg = addSvg(box, midSvg);
    var o2 = mk("CDFs and the area between them"); o2.x = [0, 1]; o2.y = [-0.05, 1.08]; o2.w = 680; o2.h = 170;
    var mid = new Plot(midSvg, o2);
    var o3 = mk("The optimal 1-Lipschitz witness"); o3.x = [0, 1]; o3.y = [-1, 1]; o3.w = 680; o3.h = 150;
    var bot = new Plot(botSvg, o3);
    var preSel = select(s.controls, "Pair", [["atoms", "½δ₀ + ½δ₃ vs 𝒰[1,2]"], ["gauss", "two Gaussians"], ["bimodal", "two bumps vs one"]], "atoms", function () { tS.set(0); draw(); });
    var tS = slider(s.controls, "shift β by", -3, 3, 0.05, 0, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "α, C_α"], ["--s1", "β (shifted), C_β"], ["--s3", "area |C_α − C_β|, witness f"]]);
    function ticks(L, R) { var t = [], v; for (v = Math.ceil(L); v <= R; v++) t.push(v); return t; }
    function draw() {
      var P = PRE[preSel.value], t = tS.get(), A = P.a, B = l4shift(P.b, t), i;
      tS.out.textContent = fmt(t, 2);
      var N = 2400, L = P.L, R = P.R, h = (R - L) / N, xs = [], Fa = [], Fb = [];
      for (i = 0; i <= N; i++) { var x = L + i * h; xs.push(x); Fa.push(l4cdfComp(A, x)); Fb.push(l4cdfComp(B, x)); }
      var W1 = 0, f = [0], changes = 0, prevS = 0;
      for (i = 0; i < N; i++) {
        var d = Fa[i] - Fb[i], sg = l4sign(d, 1e-9);
        W1 += Math.abs(d) * h;
        f.push(f[i] - sg * h);
        if (sg !== 0 && prevS !== 0 && sg !== prevS) changes++;
        if (sg !== 0) prevS = sg;
      }
      var check = 0;
      for (i = 0; i < N; i++) check += 0.5 * (f[i] + f[i + 1]) * ((Fa[i + 1] - Fb[i + 1]) - (Fa[i] - Fb[i]));
      // top: measures
      top.o.x = [L, R]; top.o.y = [0, P.ymax];
      top.clear();
      top.axes({ xticks: ticks(L, R), yticks: [], nogrid: true, noyaxis: true });
      top.clip();
      [[A, "2"], [B, "1"]].forEach(function (pair) {
        var comps = pair[0], c = pair[1], cont = comps.some(function (q) { return q.t !== "d"; });
        if (cont) {
          var pts = [];
          for (var j = 0; j <= 600; j++) { var x = L + (R - L) * j / 600; pts.push([x, l4pdfComp(comps, x)]); }
          top.poly(areaPts(pts), "a" + c); top.poly(pts, "ln thin c" + c);
        }
        comps.forEach(function (q) { if (q.t === "d") { top.seg(q.x, 0, q.x, q.w * 1.6 * P.ymax / 1.25, "ln c" + c); top.dot(q.x, q.w * 1.6 * P.ymax / 1.25, 5, "f" + c); } });
      });
      top.unclip();
      // middle: CDFs and area
      mid.o.x = [L, R];
      mid.clear();
      mid.axes({ xticks: ticks(L, R), yticks: [0, 0.5, 1], yfmt: function (v) { return fmt(v, 1); }, nogrid: true });
      var up = [], dn = [];
      for (i = 0; i <= N; i += 4) { up.push([xs[i], Math.max(Fa[i], Fb[i])]); dn.push([xs[i], Math.min(Fa[i], Fb[i])]); }
      mid.poly(up.concat(dn.reverse()), "a3");
      var pa = [], pb = [];
      for (i = 0; i <= N; i += 2) { pa.push([xs[i], Fa[i]]); pb.push([xs[i], Fb[i]]); }
      mid.poly(pa, "ln c2"); mid.poly(pb, "ln c1");
      // bottom: witness, centred
      var fmin = Math.min.apply(null, f), fmax = Math.max.apply(null, f), c0 = (fmin + fmax) / 2, span = Math.max((fmax - fmin) / 2, 0.5) * 1.15;
      bot.o.x = [L, R]; bot.o.y = [-span, span];
      bot.clear();
      bot.axes({ xticks: ticks(L, R), yticks: [], nogrid: true });
      var wp = []; for (i = 0; i <= N; i += 2) wp.push([xs[i], f[i] - c0]);
      bot.poly(wp, "ln c3");
      bot.text(L + 0.1, span * 0.78, "witness f (slope ±1), shifted to be centred", "tx-s", "start");
      ro.textContent = "W₁ = ∫ |C_α − C_β| dx = " + fmt(W1, 3) + "      ∫ f d(α − β) = " + fmt(check, 3) + "  (equal: the witness certifies W₁)" +
        "\nsign changes of C_α − C_β: " + changes + (changes === 0 ? "  → the witness is a single line of slope ±1: every unit of mass moves the same way" : "  → the witness bends where the CDFs cross");
    }
    draw(); redrawers.push(draw);
  };

  /* =====================================================================================
     4. Divergences versus W1 along a translation (section 6)
     ===================================================================================== */
  WIDGETS.l4divs = function (box) {
    var s = scaffold(box, "Translate the model: which discrepancies keep telling a generator where the data are?");
    var top = new Plot(s.svg, { x: [-4, 5], y: [0, 1.25], w: 680, h: 130, pad: { l: 40, r: 16, t: 10, b: 24 }, label: "Data (blue) and translated model (orange-red)" });
    var botSvg = addSvg(box, s.svg);
    var bot = new Plot(botSvg, { x: [-3, 3], y: [0, 3.2], w: 680, h: 270, pad: { l: 40, r: 16, t: 16, b: 30 }, label: "Discrepancies as functions of the shift t" });
    var famSel = select(s.controls, "Family", [["unif", "two uniform laws"], ["gauss", "two Gaussians"], ["dirac", "two Diracs"]], "unif", setup);
    var tS = slider(s.controls, "shift t", -3, 3, 0.01, 1.5, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "W₁"], ["--muted", "‖·‖_TV"], ["--s5", "JS²"], ["--s6", "KL(model | data)"], ["--s4", "MMD (Gaussian kernel, σ = 1)"]]);
    var LN2 = Math.log(2);
    function vals(fam, t) {
      var a = Math.abs(t), v = { w1: a };
      if (fam === "dirac") {
        v.tv = a < 1e-9 ? 0 : 2; v.js = a < 1e-9 ? 0 : LN2; v.kl = a < 1e-9 ? 0 : Infinity; v.mmd = Math.sqrt(Math.max(0, 2 - 2 * Math.exp(-t * t / 2)));
      } else if (fam === "unif") {
        var m1 = Math.min(a, 1);
        v.tv = 2 * m1; v.js = m1 * LN2; v.kl = a < 1e-9 ? 0 : Infinity;
        var n = 200, ekk = 0, ekxy = 0, h = 2 / n;
        for (var i = 0; i <= n; i++) { var d = -1 + i * h, wgt = (i === 0 || i === n) ? 0.5 : 1, tri = 1 - Math.abs(d); ekk += wgt * tri * Math.exp(-d * d / 2) * h; ekxy += wgt * tri * Math.exp(-(d - t) * (d - t) / 2) * h; }
        v.mmd = Math.sqrt(Math.max(0, 2 * ekk - 2 * ekxy));
      } else {
        v.kl = t * t / 2; v.tv = 2 * (2 * l4Phi(a / 2) - 1);
        var lo = -8, hi = 8 + a, nn = 800, hh = (hi - lo) / nn, js = 0;
        for (var j = 0; j <= nn; j++) {
          var x = lo + j * hh, p = gpdf(x, 0, 1), q = gpdf(x, t, 1), mm = (p + q) / 2, w2 = (j === 0 || j === nn) ? 0.5 : 1, term = 0;
          if (p > 1e-300) term += 0.5 * p * Math.log(p / mm);
          if (q > 1e-300) term += 0.5 * q * Math.log(q / mm);
          js += w2 * term * hh;
        }
        v.js = js;
        v.mmd = Math.sqrt(Math.max(0, 2 * Math.sqrt(1 / 3) * (1 - Math.exp(-t * t / 6))));
      }
      return v;
    }
    var curves = null;
    function setup() {
      var fam = famSel.value, ts = [], k;
      for (k = 0; k <= 240; k++) ts.push(-3 + 6 * k / 240);
      curves = { ts: ts, v: ts.map(function (t) { return vals(fam, t); }) };
      draw();
    }
    function draw() {
      var fam = famSel.value, t = tS.get(), v = vals(fam, t), i;
      tS.out.textContent = fmt(t, 2);
      // top
      top.clear();
      top.axes({ xticks: [-4, -2, 0, 2, 4], yticks: [], nogrid: true, noyaxis: true });
      top.clip();
      if (fam === "unif") {
        top.poly([[0, 0], [0, 1], [1, 1], [1, 0]], "a1"); top.poly([[0, 0], [0, 1], [1, 1], [1, 0]], "ln c1 thin");
        top.poly([[t, 0], [t, 1], [t + 1, 1], [t + 1, 0]], "a2"); top.poly([[t, 0], [t, 1], [t + 1, 1], [t + 1, 0]], "ln c2 thin");
      } else if (fam === "gauss") {
        top.fn(function (x) { return gpdf(x, 0, 1) * 2.2; }, "ln c1", 300); top.fn(function (x) { return gpdf(x, t, 1) * 2.2; }, "ln c2", 300);
      } else {
        top.seg(0, 0, 0, 1, "ln c1"); top.dot(0, 1, 5, "f1"); top.seg(t, 0, t, 0.9, "ln c2"); top.dot(t, 0.9, 5, "f2");
      }
      top.unclip();
      top.text(-3.9, 1.08, "data β (blue) at 0, model α (orange-red) shifted by t", "tx-s", "start");
      // bottom
      bot.clear();
      bot.axes({ xticks: [-3, -2, -1, 0, 1, 2, 3], yticks: [0, 1, 2, 3], xlabel: "t", xfmt: function (x) { return fmt(x, 0); } });
      bot.clip();
      var keys = [["tv", "ln cm"], ["js", "ln c5"], ["mmd", "ln c4"], ["w1", "ln c3"]];
      keys.forEach(function (kc) { bot.poly(curves.ts.map(function (tt, j) { return [tt, curves.v[j][kc[0]]]; }), kc[1]); });
      if (fam === "gauss") bot.poly(curves.ts.map(function (tt, j) { return [tt, curves.v[j].kl]; }), "ln c6 dash");
      else { bot.seg(-3, 3.05, -0.02, 3.05, "ln c6 dash"); bot.seg(0.02, 3.05, 3, 3.05, "ln c6 dash"); bot.dot(0, 0, 4, "f6"); }
      bot.unclip();
      if (fam !== "gauss") bot.text(2.95, 3.05, "KL = +∞ for t ≠ 0", "tx-s", "end", 0, -6);
      [["tv", "fm"], ["js", "f5"], ["mmd", "f4"], ["w1", "f3"]].forEach(function (kc) { var y = v[kc[0]]; if (y <= 3.2) bot.dot(t, y, 4.5, kc[1]); });
      if (isFinite(v.kl) && v.kl <= 3.2) bot.dot(t, v.kl, 4.5, "f6");
      bot.seg(t, 0, t, 3.2, "ln cm hair dot");
      // slopes by finite differences
      var e = 1e-3, vp = vals(fam, t + e), vm = vals(fam, t - e);
      function sl(k) { var a = vp[k], b = vm[k]; if (!isFinite(a) || !isFinite(b)) return "—"; var d = (a - b) / (2 * e); return (d >= 0 ? "+" : "") + fmt(d, 2); }
      ro.textContent = "at t = " + fmt(t, 2) + ":  W₁ = " + fmt(v.w1, 3) + "   TV = " + fmt(v.tv, 3) + "   JS² = " + fmt(v.js, 4) + "   MMD = " + fmt(v.mmd, 3) + "   KL = " + (isFinite(v.kl) ? fmt(v.kl, 3) : "+∞") +
        "\nslopes d/dt:  W₁ " + sl("w1") + "   TV " + sl("tv") + "   JS² " + sl("js") + "   MMD " + sl("mmd") + "   KL " + sl("kl") +
        "\n" + (Math.abs(t) < 1e-9 ? "t = 0: all discrepancies vanish." : (fam === "gauss" ? "Overlapping densities: everything is finite, but JS² and TV flatten as |t| grows; KL grows like t²/2." :
          (fam === "unif" && Math.abs(t) < 1 ? "Supports still overlap: JS² and TV still move — until |t| = 1." : "Disjoint supports: JS² = log 2 and TV = 2 are flat (zero slope), KL = +∞; only W₁ (and, weakly, MMD) still point back to the data.")));
    }
    setup(); redrawers.push(draw);
  };

  /* =====================================================================================
     5. Semi-discrete transport in 2D: Laguerre cells, gradient and stochastic ascent, Lloyd (section 7)
     ===================================================================================== */
  function l4clipPoly(poly, a, b, c) { // keep a x + b y <= c
    var out = [], n = poly.length;
    for (var k = 0; k < n; k++) {
      var P = poly[k], Q = poly[(k + 1) % n], fp = a * P[0] + b * P[1] - c, fq = a * Q[0] + b * Q[1] - c;
      if (fp <= 0) out.push(P);
      if (fp * fq < 0) { var t = fp / (fp - fq); out.push([P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])]); }
    }
    return out;
  }
  function l4polyArea(P) { var s = 0; for (var k = 0; k < P.length; k++) { var q = P[(k + 1) % P.length]; s += P[k][0] * q[1] - q[0] * P[k][1]; } return Math.abs(s) / 2; }
  function l4polyCentroid(P) {
    var A = 0, cx = 0, cy = 0;
    for (var k = 0; k < P.length; k++) { var q = P[(k + 1) % P.length], cr = P[k][0] * q[1] - q[0] * P[k][1]; A += cr; cx += (P[k][0] + q[0]) * cr; cy += (P[k][1] + q[1]) * cr; }
    return A === 0 ? null : [cx / (3 * A), cy / (3 * A)];
  }
  function l4polySq(P, y) { // integral of |x - y|^2 over a convex polygon (exact: edge-midpoint rule on triangles)
    if (P.length < 3) return 0;
    var s = 0, p0 = P[0];
    for (var k = 1; k < P.length - 1; k++) {
      var p1 = P[k], p2 = P[k + 1];
      var A = Math.abs((p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])) / 2;
      var ms = [[(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2], [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2], [(p0[0] + p2[0]) / 2, (p0[1] + p2[1]) / 2]];
      var t = 0; ms.forEach(function (m) { t += (m[0] - y[0]) * (m[0] - y[0]) + (m[1] - y[1]) * (m[1] - y[1]); });
      s += A / 3 * t;
    }
    return s;
  }
  WIDGETS.l4laguerre = function (box) {
    var s = scaffold(box, "Semi-discrete transport: weights move the walls of the Laguerre cells until each cell captures its mass");
    var W = 680, H = 420;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Power diagram of six atoms in the unit square, with bars comparing captured and prescribed masses");
    var denSel = select(s.controls, "Source α", [["unif", "uniform on the square"], ["blobs", "two Gaussian blobs"]], "unif", function () { stop(); g = zeros(); hist = []; mode = "ot"; draw(); });
    var bSel = select(s.controls, "Target masses b", [["eq", "equal (1/6 each)"], ["uneq", "unequal"]], "uneq", function () { stop(); g = zeros(); hist = []; mode = "ot"; draw(); });
    button(s.controls, "Gradient step", function () { stop(); mode = "ot"; gradStep(); draw(); });
    button(s.controls, "Run", function () { stop(); mode = "ot"; runGrad(); });
    button(s.controls, "Stochastic", function () { stop(); mode = "ot"; runSto(); });
    button(s.controls, "Weights to 0", function () { stop(); g = zeros(); hist = []; mode = "ot"; draw(); });
    button(s.controls, "Lloyd step", function () { stop(); lloydStep(); });
    button(s.controls, "New atoms", function () { stop(); newSites(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--text", "atoms yⱼ (drag)"], ["--s3", "captured mass α(Lⱼ)"], ["--muted", "prescribed mass bⱼ (outline)"]]);
    var M = 6, seedS = 21, timer = null, busy = false;
    var Y0 = [[0.22, 0.25], [0.7, 0.18], [0.5, 0.5], [0.2, 0.75], [0.78, 0.72], [0.48, 0.88]];
    var Y = Y0.map(function (p) { return p.slice(); });
    var BS = { eq: [1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6], uneq: [0.10, 0.15, 0.30, 0.15, 0.20, 0.10] };
    function zeros() { return [0, 0, 0, 0, 0, 0]; }
    var g = zeros(), hist = [], mode = "ot", lloydCount = 0, stoCount = 0, gbar = null;
    var NG = 90, GX = [], GW = [];
    function buildGrid() {
      GX = []; GW = []; var tot = 0;
      for (var i = 0; i < NG; i++) for (var j = 0; j < NG; j++) {
        var x = (i + 0.5) / NG, y = (j + 0.5) / NG, w;
        if (denSel.value === "unif") w = 1;
        else w = 0.55 * Math.exp(-((x - 0.28) * (x - 0.28) + (y - 0.3) * (y - 0.3)) / (2 * 0.12 * 0.12)) + 0.45 * Math.exp(-((x - 0.72) * (x - 0.72) + (y - 0.7) * (y - 0.7)) / (2 * 0.14 * 0.14)) + 0.03;
        GX.push([x, y]); GW.push(w); tot += w;
      }
      for (var k = 0; k < GW.length; k++) GW[k] /= tot;
    }
    function cellsOf(gv) {
      var out = [];
      for (var j = 0; j < M; j++) {
        var poly = [[0, 0], [1, 0], [1, 1], [0, 1]];
        for (var k = 0; k < M && poly.length >= 3; k++) {
          if (k === j) continue;
          var a = 2 * (Y[k][0] - Y[j][0]), b = 2 * (Y[k][1] - Y[j][1]);
          var c = Y[k][0] * Y[k][0] + Y[k][1] * Y[k][1] - Y[j][0] * Y[j][0] - Y[j][1] * Y[j][1] - gv[k] + gv[j];
          poly = l4clipPoly(poly, a, b, c);
        }
        out.push(poly);
      }
      return out;
    }
    function evalAt(gv) { // masses, dual value, centroids
      var b = BS[bSel.value], cells = cellsOf(gv), mass = [], E = 0, cent = [], j;
      if (denSel.value === "unif") {
        for (j = 0; j < M; j++) {
          var A = cells[j].length >= 3 ? l4polyArea(cells[j]) : 0;
          mass.push(A); E += (cells[j].length >= 3 ? l4polySq(cells[j], Y[j]) : 0) - gv[j] * A;
          cent.push(A > 1e-12 ? l4polyCentroid(cells[j]) : null);
        }
      } else {
        var sx = zeros(), sy = zeros();
        mass = zeros();
        for (var i = 0; i < GX.length; i++) {
          var x = GX[i], best = 0, bv = Infinity;
          for (j = 0; j < M; j++) { var dx = x[0] - Y[j][0], dy = x[1] - Y[j][1], v = dx * dx + dy * dy - gv[j]; if (v < bv) { bv = v; best = j; } }
          mass[best] += GW[i]; E += GW[i] * bv; sx[best] += GW[i] * x[0]; sy[best] += GW[i] * x[1];
        }
        for (j = 0; j < M; j++) cent.push(mass[j] > 1e-12 ? [sx[j] / mass[j], sy[j] / mass[j]] : null);
      }
      for (j = 0; j < M; j++) E += gv[j] * b[j];
      return { cells: cells, mass: mass, E: E, cent: cent };
    }
    var tau = 0.3;
    function gradStep() {
      var b = BS[bSel.value], cur = evalAt(g), step = tau, j, tries = 0;
      while (tries < 12) {
        var gn = g.map(function (v, k) { return v + step * (b[k] - cur.mass[k]); });
        var nx = evalAt(gn);
        if (nx.E >= cur.E - 1e-12) { g = gn; hist.push(nx.E); return nx; }
        step /= 2; tries++;
      }
      return cur;
    }
    function maxErr(r) { var b = BS[bSel.value], m = 0; for (var j = 0; j < M; j++) m = Math.max(m, Math.abs(r.mass[j] - b[j])); return m; }
    function stop() { if (timer) { clearTimeout(timer); timer = null; } busy = false; }
    function runGrad() {
      var n = 0;
      if (!hist.length) hist.push(evalAt(g).E);
      (function loop() {
        var r = gradStep(); n++;
        draw();
        if (n < 400 && maxErr(r) > 2e-4) timer = setTimeout(loop, 30); else timer = null;
      })();
    }
    function sampleAlpha(rng) {
      if (denSel.value === "unif") return [rng(), rng()];
      var u = rng(), cum = 0;
      for (var i = 0; i < GW.length; i++) { cum += GW[i]; if (cum >= u) return [GX[i][0] + (rng() - 0.5) / NG, GX[i][1] + (rng() - 0.5) / NG]; }
      return GX[GX.length - 1];
    }
    function runSto() {
      var rng = mulberry32(seedS * 7 + 3), b = BS[bSel.value], frames = 0;
      stoCount = 0; gbar = zeros(); hist = [evalAt(g).E];
      (function loop() {
        for (var r = 0; r < 60; r++) {
          var x = sampleAlpha(rng), best = 0, bv = Infinity;
          for (var j = 0; j < M; j++) { var dx = x[0] - Y[j][0], dy = x[1] - Y[j][1], v = dx * dx + dy * dy - g[j]; if (v < bv) { bv = v; best = j; } }
          var st = 0.08 / Math.sqrt(1 + stoCount / 30);
          for (j = 0; j < M; j++) g[j] += st * (b[j] - (j === best ? 1 : 0));
          stoCount++;
          for (j = 0; j < M; j++) gbar[j] += (g[j] - gbar[j]) / stoCount;
        }
        hist.push(evalAt(g).E);
        frames++;
        draw();
        if (frames < 100) timer = setTimeout(loop, 40); else timer = null;
      })();
    }
    function lloydStep() {
      mode = "lloyd"; g = zeros(); hist = []; gbar = null;
      var r = evalAt(g), from = Y.map(function (p) { return p.slice(); }), to = Y.map(function (p, j) { return r.cent[j] ? r.cent[j] : p; });
      var t0 = null, dur = 450; busy = true;
      function frame(ts) {
        if (t0 === null) t0 = ts;
        var u = Math.min(1, (ts - t0) / dur), e = u * u * (3 - 2 * u);
        for (var j = 0; j < M; j++) Y[j] = [from[j][0] + e * (to[j][0] - from[j][0]), from[j][1] + e * (to[j][1] - from[j][1])];
        draw();
        if (u < 1 && busy) requestAnimationFrame(frame); else { busy = false; lloydCount++; draw(); }
      }
      requestAnimationFrame(frame);
    }
    function newSites() {
      var rng = mulberry32(seedS++);
      Y = []; for (var j = 0; j < M; j++) Y.push([0.1 + 0.8 * rng(), 0.1 + 0.8 * rng()]);
      g = zeros(); hist = []; mode = "ot"; lloydCount = 0; gbar = null; draw();
    }
    // dragging atoms
    var SQ = { x: 10, y: 10, s: 400 };
    function PX(x) { return SQ.x + SQ.s * x; } function PY(y) { return SQ.y + SQ.s * (1 - y); }
    var drag = -1;
    s.svg.addEventListener("pointerdown", function (e) {
      var p = svgPoint(s.svg, e), best = -1, bd = 16;
      for (var j = 0; j < M; j++) { var d = Math.hypot(p.x - PX(Y[j][0]), p.y - PY(Y[j][1])); if (d < bd) { bd = d; best = j; } }
      if (best >= 0) { stop(); drag = best; e.preventDefault(); try { s.svg.setPointerCapture(e.pointerId); } catch (err) {} }
    });
    s.svg.addEventListener("pointermove", function (e) {
      if (drag < 0) return; e.preventDefault();
      var p = svgPoint(s.svg, e);
      Y[drag] = [Math.min(0.98, Math.max(0.02, (p.x - SQ.x) / SQ.s)), Math.min(0.98, Math.max(0.02, 1 - (p.y - SQ.y) / SQ.s))];
      hist = []; draw();
    });
    function endDrag() { drag = -1; }
    s.svg.addEventListener("pointerup", endDrag); s.svg.addEventListener("pointercancel", endDrag);
    var FILL = ["a1", "a2", "a3", "a4", "a5", "am"], DOT = ["f1", "f2", "f3", "f4", "f5", "fm"];
    function draw() {
      var b = BS[bSel.value], r = evalAt(g), gg = l4clear(s.svg), j;
      // density shading for the blobs
      if (denSel.value === "blobs") {
        var cs = SQ.s / NG, mx = Math.max.apply(null, GW);
        for (var i = 0; i < GX.length; i += 1) {
          var o = GW[i] / mx;
          if (o > 0.06) el("rect", { x: (PX(GX[i][0]) - cs / 2).toFixed(1), y: (PY(GX[i][1]) - cs / 2).toFixed(1), width: cs.toFixed(2), height: cs.toFixed(2), "class": "fk", "fill-opacity": (0.32 * o).toFixed(3) }, gg);
        }
      }
      r.cells.forEach(function (P, jj) {
        if (P.length < 3) return;
        var d = "M" + P.map(function (p) { return PX(p[0]).toFixed(1) + " " + PY(p[1]).toFixed(1); }).join("L") + "Z";
        el("path", { d: d, "class": FILL[jj] }, gg);
        el("path", { d: d, "class": "ln ck thin nofill", "stroke-opacity": 0.55 }, gg);
      });
      el("rect", { x: SQ.x, y: SQ.y, width: SQ.s, height: SQ.s, "class": "ln cm thin nofill" }, gg);
      for (j = 0; j < M; j++) {
        el("circle", { cx: PX(Y[j][0]), cy: PY(Y[j][1]), r: 7, "class": "fk drag" }, gg);
        el("circle", { cx: PX(Y[j][0]), cy: PY(Y[j][1]), r: 4, "class": DOT[j] }, gg);
        l4txt(gg, PX(Y[j][0]) + 10, PY(Y[j][1]) - 8, "y" + "₁₂₃₄₅₆"[j], "tx-s", "start");
      }
      // bars
      var bx = 440, by = 24, bw = 200, bh = 18, maxb = 0.5;
      l4txt(gg, bx, by - 8, mode === "ot" ? "cell masses α(Lⱼ) vs prescribed bⱼ" : "Voronoi cell masses (free)", "tx-s", "start");
      for (j = 0; j < M; j++) {
        var yy = by + 6 + j * (bh + 8);
        l4txt(gg, bx - 6, yy + 13, "y" + "₁₂₃₄₅₆"[j], "tx-s", "end");
        el("rect", { x: bx, y: yy, width: (bw * Math.min(r.mass[j], maxb) / maxb).toFixed(1), height: bh, "class": DOT[j], "fill-opacity": 0.55 }, gg);
        if (mode === "ot") el("rect", { x: bx, y: yy, width: (bw * b[j] / maxb).toFixed(1), height: bh, "class": "ln ck thin nofill" }, gg);
        l4txt(gg, bx + bw + 6, yy + 13, fmt(r.mass[j], 3), "tx-s", "start");
      }
      // history of the dual value (or energy)
      var hx = 440, hy = 205, hw = 210, hh = 150;
      el("rect", { x: hx, y: hy, width: hw, height: hh, "class": "ln cm hair nofill" }, gg);
      l4txt(gg, hx, hy - 8, mode === "ot" ? "dual value 𝓔₀(g) along the iterations" : "Lloyd: positions only (weights 0)", "tx-s", "start");
      if (mode === "ot" && hist.length > 1) {
        var lo = Math.min.apply(null, hist), hi = Math.max.apply(null, hist), span = Math.max(hi - lo, 1e-6), n = Math.max(hist.length - 1, 4);
        var d2 = hist.map(function (v, k) { return (k ? "L" : "M") + (hx + 4 + k / n * (hw - 8)).toFixed(1) + " " + (hy + hh - 8 - (v - lo) / span * (hh - 16)).toFixed(1); }).join("");
        el("path", { d: d2, "class": "ln c3 thin" }, gg);
        l4txt(gg, hx + hw - 4, hy + 14, "max " + fmt(hi, 5), "tx-s", "end");
        l4txt(gg, hx + hw - 4, hy + hh - 4, "min " + fmt(lo, 5), "tx-s", "end");
      }
      var err = maxErr(r);
      var txt;
      if (mode === "ot") {
        txt = "dual value 𝓔₀(g) = ∫ minⱼ(|x − yⱼ|² − gⱼ) dα + ⟨g, b⟩ = " + fmt(r.E, 5) + "    max |α(Lⱼ) − bⱼ| = " + fmt(err, 4) +
          "\nweights g = (" + g.map(function (v) { return fmt(v, 3); }).join(", ") + ")" + (err < 1e-3 ? "   — balanced: the map Lⱼ → yⱼ is optimal and 𝓔₀(g) = W₂²" : "");
        if (gbar) txt += "\nstochastic ascent: " + stoCount + " samples, step 0.08/√(1 + ℓ/30); averaged weights give 𝓔₀(ḡ) = " + fmt(evalAt(gbar).E, 5);
      } else {
        var en = 0;
        if (denSel.value === "unif") r.cells.forEach(function (P, jj) { en += l4polySq(P, Y[jj]); });
        else en = r.E;
        txt = "Lloyd (k-means): weights 0, Voronoi cells; step " + lloydCount + ", energy ∫ minⱼ |x − yⱼ|² dα = " + fmt(en, 5) +
          "\neach step moves every atom to the centroid of its cell; the energy never increases.";
      }
      ro.textContent = txt;
    }
    buildGrid();
    denSel.addEventListener("change", function () { buildGrid(); draw(); });
    draw(); redrawers.push(draw);
  };

  /* =====================================================================================
     6. OT between Gaussian mixtures: component-wise (MW2) versus true W2 (section 8)
     ===================================================================================== */
  WIDGETS.l4gmm = function (box) {
    var s = scaffold(box, "Two Gaussian mixtures: transporting components (MW₂) versus transporting the densities (W₂)");
    var plot = new Plot(s.svg, { x: [-4.5, 4.5], y: [0, 1], w: 680, h: 300, pad: { l: 40, r: 16, t: 16, b: 28 }, label: "Interpolations between two Gaussian mixtures" });
    var PRE = {
      one: { A: [[1, 0, 1]], B: [[0.5, -1, 0.5], [0.5, 1, 0.5]], P: [[0.5, 0.5]], L: -4.5, R: 4.5, ymax: 0.9 },
      two: { A: [[0.5, -2, 0.5], [0.5, 2, 0.5]], B: [[0.25, -1, 0.5], [0.75, 1.5, 1]], P: [[0.25, 0.25], [0, 0.5]], L: -5, R: 6, ymax: 0.6 },
      three: { A: [[0.2, -2, 0.3], [0.6, 0, 0.8], [0.2, 2, 0.3]], B: [[0.45, -2.2, 0.3], [0.1, 0, 0.25], [0.45, 2.2, 0.3]], P: [[0.2, 0, 0], [0.25, 0.1, 0.25], [0, 0, 0.2]], L: -4.5, R: 4.5, ymax: 0.85 }
    };
    var preSel = select(s.controls, "Mixtures", [["one", "𝒩(0,1) vs two bumps"], ["two", "two vs two components"], ["three", "three vs three"]], "one", setup);
    var tS = slider(s.controls, "t", 0, 1, 0.01, 0.5, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "ᾱ (t = 0)"], ["--s1", "β̄ (t = 1)"], ["--s3", "MW₂ path (components travel)"], ["--s5", "W₂ path (densities)"], ["--muted", "mixture (1 − t)ᾱ + tβ̄"]]);
    var D = null;
    function mixPdf(M, x) { var v = 0; M.forEach(function (c) { v += c[0] * gpdf(x, c[1], c[2]); }); return v; }
    function setup() {
      var P = PRE[preSel.value], N = 3001;
      var LA = new Line1D(P.L - 3, P.R + 3, N, function (x) { return mixPdf(P.A, x); });
      var LB = new Line1D(P.L - 3, P.R + 3, N, function (x) { return mixPdf(P.B, x); });
      var qa = quantiles(LA.xs, LA.c), qb = quantiles(LB.xs, LB.c);
      var mw = 0;
      P.A.forEach(function (ca, i) { P.B.forEach(function (cb, j) { mw += P.P[i][j] * ((ca[1] - cb[1]) * (ca[1] - cb[1]) + (ca[2] - cb[2]) * (ca[2] - cb[2])); }); });
      D = { P: P, qa: qa, qb: qb, w2: Math.pow(w2q(qa, qb), 2), mw2: mw };
      draw();
    }
    function draw() {
      var P = D.P, t = tS.get(), i;
      tS.out.textContent = fmt(t, 2);
      plot.o.x = [P.L, P.R]; plot.o.y = [0, P.ymax];
      plot.clear();
      var ticks = []; for (i = Math.ceil(P.L); i <= P.R; i++) ticks.push(i);
      plot.axes({ xticks: ticks, yticks: [], nogrid: true, noyaxis: true });
      plot.clip();
      plot.fn(function (x) { return mixPdf(P.A, x); }, "ln c2 thin dash", 400);
      plot.fn(function (x) { return mixPdf(P.B, x); }, "ln c1 thin dash", 400);
      plot.fn(function (x) { return (1 - t) * mixPdf(P.A, x) + t * mixPdf(P.B, x); }, "ln cm", 400);
      var qt = new Float64Array(MQ);
      for (i = 0; i < MQ; i++) qt[i] = (1 - t) * D.qa[i] + t * D.qb[i];
      plot.poly(densityFromQ(qt), "ln c5 dash");
      var comps = [];
      P.A.forEach(function (ca, ii) { P.B.forEach(function (cb, jj) { var w = P.P[ii][jj]; if (w > 1e-12) comps.push([w, (1 - t) * ca[1] + t * cb[1], (1 - t) * ca[2] + t * cb[2]]); }); });
      plot.fn(function (x) { return mixPdf(comps, x); }, "ln c3", 500);
      plot.unclip();
      var plan = "[" + P.P.map(function (r) { return "[" + r.map(frac).join(", ") + "]"; }).join(", ") + "]";
      ro.textContent = "MW₂² = Σ Pᵢⱼ [(mᵢ − nⱼ)² + (σᵢ − τⱼ)²] = " + fmt(D.mw2, 4) + "   ≥   W₂²(ᾱ, β̄) = " + fmt(D.w2, 4) + "   (ratio " + fmt(D.mw2 / D.w2, 1) + ")" +
        "\noptimal component plan P* (rows: components of ᾱ) = " + plan +
        "\nthe green path is a mixture of at most " + comps.length + " Gaussians at every t; the purple one may split a component.";
    }
    setup(); redrawers.push(draw);
  };
