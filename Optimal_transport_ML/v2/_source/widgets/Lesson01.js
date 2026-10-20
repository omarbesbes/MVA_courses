// widgets/Lesson01.js — interactive figures of Lesson 1 (Monge's problem).
// This file is inserted by build.mjs inside the scope of app.js: it uses el, fmt, Plot, scaffold, slider, select,
// button, checkbox, readout, legend, addSvg, svgPoint, mulberry32, gpdf, updf, Line1D, MQ, quantiles,
// densityFromQ, mmul, msym, msqrt, minv, bures, ellipsePts, hungarian and redrawers, and registers its widgets
// in WIDGETS. Its own helpers are prefixed "l1".

  /* ---------------- helpers of this page ---------------- */
  function l1orient(a, b, c) { return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]); }
  // Proper crossing of the segments [a, b] and [c, d]: the relative interiors meet, the supporting lines differ.
  function l1cross(a, b, c, d) {
    var o1 = l1orient(a, b, c), o2 = l1orient(a, b, d), o3 = l1orient(c, d, a), o4 = l1orient(c, d, b);
    return o1 * o2 < 0 && o3 * o4 < 0;
  }
  function l1meet(a, b, c, d) { // intersection of the lines (a, b) and (c, d)
    var den = (a[0] - b[0]) * (c[1] - d[1]) - (a[1] - b[1]) * (c[0] - d[0]);
    var t = ((a[0] - c[0]) * (c[1] - d[1]) - (a[1] - c[1]) * (c[0] - d[0])) / den;
    return [a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])];
  }
  function l1group(x) { return String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, " "); }
  function l1fact(n) { var f = 1; for (var k = 2; k <= n; k++) f *= k; return f; }
  function l1clamp(v, a, b) { return Math.min(Math.max(v, a), b); }
  function l1mat(M) { return "[[" + fmt(M[0], 3) + ", " + fmt(M[1], 3) + "], [" + fmt(M[2], 3) + ", " + fmt(M[3], 3) + "]]"; }
  function l1tr(M) { return [M[0], M[2], M[1], M[3]]; }
  function l1eig(M) { // eigenvalues of a symmetric 2 x 2 matrix, increasing
    var m = (M[0] + M[3]) / 2, r = Math.sqrt((M[0] - M[3]) * (M[0] - M[3]) / 4 + M[1] * M[1]);
    return [m - r, m + r];
  }
  // Arrow from (x1, y1) to (x2, y2), in the coordinates of the Plot P, with a filled triangular head.
  // With gap > 0 the arrow stops gap pixels before (x2, y2), outside a dot drawn there.
  function l1arrow(P, x1, y1, x2, y2, cls, head, gap) {
    var X1 = P.tx(x1), Y1 = P.ty(y1), X2 = P.tx(x2), Y2 = P.ty(y2), L = Math.hypot(X2 - X1, Y2 - Y1);
    if (L < 1 + 2 * (gap || 0)) return;
    var ux = (X2 - X1) / L, uy = (Y2 - Y1) / L;
    if (gap) { X1 += gap * ux; Y1 += gap * uy; X2 -= gap * ux; Y2 -= gap * uy; L -= 2 * gap; }
    var h = Math.min(8, 0.45 * L), w = 0.42 * h;
    el("line", { x1: X1.toFixed(1), y1: Y1.toFixed(1), x2: (X2 - 0.8 * h * ux).toFixed(1), y2: (Y2 - 0.8 * h * uy).toFixed(1), "class": cls }, P.g);
    el("path", { d: "M" + X2.toFixed(1) + " " + Y2.toFixed(1) + "L" + (X2 - h * ux - w * uy).toFixed(1) + " " + (Y2 - h * uy + w * ux).toFixed(1) +
      "L" + (X2 - h * ux + w * uy).toFixed(1) + " " + (Y2 - h * uy - w * ux).toFixed(1) + "Z", "class": head }, P.g);
  }
  // Points that can be dragged: getPts() returns their positions [x, y] in the coordinates of P;
  // onMove(k, x, y) receives the new position of point k.
  function l1drag(svg, P, getPts, onMove) {
    var active = -1;
    svg.addEventListener("pointerdown", function (e) {
      var q = svgPoint(svg, e), best = -1, bd = 24;
      getPts().forEach(function (p, k) {
        var d = Math.hypot(P.tx(p[0]) - q.x, P.ty(p[1]) - q.y);
        if (d < bd) { bd = d; best = k; }
      });
      if (best < 0) return;
      active = best; e.preventDefault();
      try { svg.setPointerCapture(e.pointerId); } catch (err) {}
    });
    svg.addEventListener("pointermove", function (e) {
      if (active < 0) return;
      e.preventDefault();
      var q = svgPoint(svg, e);
      onMove(active, P.ix(q.x), P.iy(q.y));
    });
    function stop() { active = -1; }
    svg.addEventListener("pointerup", stop);
    svg.addEventListener("pointercancel", stop);
  }
  // The part of the convex polygon poly where <n, p> >= c (one step of Sutherland-Hodgman clipping).
  function l1half(poly, n, c) {
    var out = [], m = poly.length;
    for (var i = 0; i < m; i++) {
      var p = poly[i], q = poly[(i + 1) % m];
      var fp = n[0] * p[0] + n[1] * p[1] - c, fq = n[0] * q[0] + n[1] * q[1] - c;
      if (fp >= 0) out.push(p);
      if ((fp >= 0) !== (fq >= 0)) { var t = fp / (fp - fq); out.push([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])]); }
    }
    return out;
  }
  var l1permCache = {};
  function l1perms(n) { // all permutations of 0..n-1 (n <= 7), cached
    if (l1permCache[n]) return l1permCache[n];
    var out = [[]];
    for (var k = 0; k < n; k++) {
      var next = [];
      out.forEach(function (q) { for (var j = 0; j <= q.length; j++) { var r = q.slice(); r.splice(j, 0, k); next.push(r); } });
      out = next;
    }
    l1permCache[n] = out;
    return out;
  }
  function l1centroid(poly) {
    var x = 0, y = 0;
    poly.forEach(function (p) { x += p[0]; y += p[1]; });
    return [x / poly.length, y / poly.length];
  }

  /* --- 1. Optimal assignment in the plane, for the cost |x - y|^p (§2) --- */
  WIDGETS.l1assign = function (box) {
    var s = scaffold(box, "Optimal assignment in the plane for the cost ‖x − y‖ᵖ — drag any point");
    var P = new Plot(s.svg, { x: [0, 1.6], y: [0, 0.9], w: 680, h: 393, pad: { l: 12, r: 12, t: 12, b: 12 }, label: "Sources (orange), targets (blue) and the optimal assignment (green segments)" });
    var pS = slider(s.controls, "exponent p", 0.25, 3, 0.05, 2, draw);
    var nS = slider(s.controls, "n", 2, 12, 1, 8, function () { cloud(); });
    button(s.controls, "New cloud", function () { seed++; cloud(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "sources xᵢ (numbered)"], ["--s1", "targets yⱼ"], ["--s3", "optimal pairing"], ["--s4", "pairs that cross"]]);
    var seed = 5, X = [], Y = [];
    function cloud() {
      var rng = mulberry32(9001 + 7919 * seed), n = nS.get();
      X = []; Y = [];
      for (var i = 0; i < n; i++) {
        X.push([0.08 + 1.44 * rng(), 0.07 + 0.76 * rng()]);
        Y.push([0.08 + 1.44 * rng(), 0.07 + 0.76 * rng()]);
      }
      draw();
    }
    l1drag(s.svg, P, function () { return X.concat(Y); }, function (k, x, y) {
      var q = [l1clamp(x, 0.02, 1.58), l1clamp(y, 0.02, 0.88)];
      if (k < X.length) X[k] = q; else Y[k - X.length] = q;
      draw();
    });
    function draw() {
      var p = pS.get(), n = X.length, i, j;
      pS.out.textContent = fmt(p, 2); nS.out.textContent = n;
      var C = X.map(function (x) { return Y.map(function (y) { return Math.pow(Math.hypot(x[0] - y[0], x[1] - y[1]), p); }); });
      var a = hungarian(C), cost = 0, crossing = [], hot = new Uint8Array(n);
      for (i = 0; i < n; i++) cost += C[i][a[i]];
      for (i = 0; i < n; i++) for (j = i + 1; j < n; j++)
        if (l1cross(X[i], Y[a[i]], X[j], Y[a[j]])) { crossing.push([i, j]); hot[i] = 1; hot[j] = 1; }
      P.clear();
      el("rect", { x: P.tx(0), y: P.ty(0.9), width: P.tx(1.6) - P.tx(0), height: P.ty(0) - P.ty(0.9), "class": "gr nofill" }, P.g);
      for (i = 0; i < n; i++) if (!hot[i]) P.seg(X[i][0], X[i][1], Y[a[i]][0], Y[a[i]][1], "ln c3");
      for (i = 0; i < n; i++) if (hot[i]) P.seg(X[i][0], X[i][1], Y[a[i]][0], Y[a[i]][1], "ln c4", { style: "stroke-width: 3.6px" });
      crossing.forEach(function (c) {
        var z = l1meet(X[c[0]], Y[a[c[0]]], X[c[1]], Y[a[c[1]]]);
        P.dot(z[0], z[1], 4.5, "fk");
      });
      Y.forEach(function (y) { P.dot(y[0], y[1], 7, "f1 drag"); });
      X.forEach(function (x, k) {
        P.dot(x[0], x[1], 7, "f2 drag");
        P.text(x[0], x[1], String(k + 1), "tx-s", "middle", 0, -11);
      });
      var lines = ["p = " + fmt(p, 2) + ":  total cost of the optimal pairing = " + fmt(cost, 3) +
        "   (Hungarian method, about n³ = " + l1group(n * n * n) + " elementary steps)"];
      if (Math.abs(p - 1) < 1e-9) {
        lines.push("proper crossings: " + crossing.length + (crossing.length === 0 ? "  — as Proposition 1.5 guarantees for the distance cost" : "  (numerical tie)"));
      } else if (crossing.length) {
        lines.push("proper crossings: " + crossing.length + "  (ochre: sources " + crossing.map(function (c) { return (c[0] + 1) + " & " + (c[1] + 1); }).join(", ") +
          ") — allowed for p ≠ 1; set p = 1 and they disappear");
      } else {
        lines.push("proper crossings: 0 on this cloud — for p ≠ 1 crossings are allowed: try other clouds or drag points");
      }
      lines.push("pairings of n = " + n + " points: n! = " + l1group(l1fact(n)) + " — none of them had to be tried");
      ro.textContent = lines.join("\n");
    }
    cloud(); redrawers.push(draw);
  };

  /* --- 2. Points on a line: sorting against the optimum, for |x - y|^p (§3) --- */
  WIDGETS.l1line = function (box) {
    var s = scaffold(box, "Points on a line: the optimal pairing for |x − y|ᵖ against the sorted pairing — drag the points");
    var YS = 0.8, YT = 0.2;
    var P = new Plot(s.svg, { x: [-0.3, 6.3], y: [0, 1], w: 680, h: 200, pad: { l: 72, r: 18, t: 14, b: 30 }, label: "Sources on the top line, targets on the bottom line, optimal and sorted pairings" });
    var preSel = select(s.controls, "points", [["rand", "random, 7 + 7"], ["two", "worked example {0, 1} → {1, 2}"], ["book", "book-shifting {1, 2, 3, 4} → {3, 4, 5, 6}"]], "rand", load);
    var pS = slider(s.controls, "exponent p", 0.25, 3, 0.05, 0.5, draw);
    button(s.controls, "New random points", function () { seed++; preSel.value = "rand"; load(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "sources (top line)"], ["--s1", "targets (bottom line)"], ["--s3", "optimal pairing"], ["--muted", "sorted pairing (dashed)"]]);
    var seed = 18, xs = [], ys = [];
    function load() {
      var v = preSel.value;
      if (v === "two") { xs = [0, 1]; ys = [1, 2]; P.o.x = [-0.4, 2.4]; }
      else if (v === "book") { xs = [1, 2, 3, 4]; ys = [3, 4, 5, 6]; P.o.x = [0.5, 6.5]; }
      else {
        var rng = mulberry32(4242 + 7919 * seed);
        xs = []; ys = [];
        for (var i = 0; i < 7; i++) { xs.push(6 * rng()); ys.push(6 * rng()); }
        P.o.x = [-0.3, 6.3];
      }
      draw();
    }
    l1drag(s.svg, P, function () {
      return xs.map(function (x) { return [x, YS]; }).concat(ys.map(function (y) { return [y, YT]; }));
    }, function (k, x) {
      var v = l1clamp(x, P.o.x[0] + 0.05, P.o.x[1] - 0.05);
      if (k < xs.length) xs[k] = v; else ys[k - xs.length] = v;
      draw();
    });
    function draw() {
      var p = pS.get(), n = xs.length, i, k;
      pS.out.textContent = fmt(p, 2);
      var C = xs.map(function (x) { return ys.map(function (y) { return Math.pow(Math.abs(x - y), p); }); });
      var a = hungarian(C);
      var ix = xs.map(function (v, i) { return i; }).sort(function (u, v) { return xs[u] - xs[v]; });
      var iy = ys.map(function (v, i) { return i; }).sort(function (u, v) { return ys[u] - ys[v]; });
      var srt = new Int32Array(n);
      for (k = 0; k < n; k++) srt[ix[k]] = iy[k];
      var copt = 0, csrt = 0, same = true;
      for (i = 0; i < n; i++) { copt += C[i][a[i]]; csrt += C[i][srt[i]]; if (a[i] !== srt[i]) same = false; }
      P.clear();
      var lo = P.o.x[0], hi = P.o.x[1];
      P.seg(lo, YS, hi, YS, "gr"); P.seg(lo, YT, hi, YT, "gr");
      P.seg(lo, 0, hi, 0, "ax");
      for (var t = Math.ceil(lo); t <= hi; t++) {
        P.seg(t, 0, t, 0.03, "ax");
        P.text(t, 0, String(t), "tx-s", "middle", 0, 15);
      }
      P.text(lo, YS, "sources", "tx-s t2", "end", -8, 4);
      P.text(lo, YT, "targets", "tx-s t1", "end", -8, 4);
      for (i = 0; i < n; i++) P.seg(xs[i], YS, ys[srt[i]], YT, "ln cm thin dash");
      for (i = 0; i < n; i++) P.seg(xs[i], YS, ys[a[i]], YT, "ln c3");
      xs.forEach(function (x) { P.dot(x, YS, 7, "f2 drag"); });
      ys.forEach(function (y) { P.dot(y, YT, 7, "f1 drag"); });
      var lines = ["p = " + fmt(p, 2) + ":  optimal pairing (Hungarian method) costs " + fmt(copt, 4) + ";  sorted pairing costs " + fmt(csrt, 4)];
      var rel = (csrt - copt) / Math.max(copt, 1e-12);
      if (rel > 1e-9) {
        lines.push("→ sorting is not optimal: it costs " + fmt(100 * rel, 1) + " % more" + (p < 1 ? " (p < 1: a concave cost rewards one long and one short move — nested or crossing segments)" : ""));
      } else if (Math.abs(p - 1) < 1e-9 && !same) {
        lines.push("→ a tie: the solver returned another pairing with the same cost as the sorted one (|x − y| is convex, not strictly)");
      } else if (p > 1) {
        lines.push("→ the sorted pairing is optimal, and for p > 1 it is the only optimum (Proposition 1.2)");
      } else {
        lines.push("→ the sorted pairing is optimal on these points");
      }
      if (n <= 7) {
        var nopt = 0;
        l1perms(n).forEach(function (q) {
          var c = 0;
          for (var i = 0; i < n; i++) c += C[i][q[i]];
          if (c <= copt * (1 + 1e-9) + 1e-12) nopt++;
        });
        lines.push("optimal pairings: " + nopt + " of the n! = " + l1group(l1fact(n)) + (nopt > 1 ? " — a tie" : " — a unique optimum"));
      }
      if (n <= 4) lines.push("the solver's pairing: " + xs.map(function (x, i) { return fmt(x, 2) + " → " + fmt(ys[a[i]], 2); }).join(",  "));
      ro.textContent = lines.join("\n");
    }
    load(); redrawers.push(draw);
  };

  /* --- 3. Push-forward of a density: histogram of T(X), Jacobian formula and naive guess (§5) --- */
  WIDGETS.l1push = function (box) {
    var s = scaffold(box, "Push-forward of a density: histogram of T(X), the Jacobian formula and the naive guess");
    var top = new Plot(s.svg, { x: [0, 1], y: [0, 1.05], w: 680, h: 200, pad: { l: 46, r: 16, t: 24, b: 28 }, label: "Graph of the map T on [0, 1]" });
    var botSvg = addSvg(box, s.svg);
    var bot = new Plot(botSvg, { x: [0, 1], y: [0, 2], w: 680, h: 250, pad: { l: 46, r: 16, t: 14, b: 30 }, label: "Source density, histogram of T(X), Jacobian formula and naive guess" });
    var mapSel = select(s.controls, "map T", [["comp", "compression at ½"], ["quad", "(x + x²)/2, the figure above"], ["affine", "2x + 1, a stretch"], ["square", "x², crushes 0"], ["fold", "(2x − 1)², two-to-one"]], "comp", resample);
    var srcSel = select(s.controls, "source α", [["unif", "𝒰[0, 1]"], ["beta", "density 6x(1 − x)"]], "unif", resample);
    var kS = slider(s.controls, "strength s", 0, 0.95, 0.01, 0.8, resample);
    var x0S = slider(s.controls, "point x₀", 0.02, 0.98, 0.01, 0.4, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "source density ρα"], ["--muted", "histogram of T(X), 20 000 samples"], ["--s3", "Jacobian formula"], ["--text", "naive guess (dashed)"]]);
    var NS = 20000, XS = new Float64Array(NS), YSm = new Float64Array(NS), src = "";
    function rho(x) {
      if (x < 0 || x > 1) return 0;
      return srcSel.value === "beta" ? 6 * x * (1 - x) : 1;
    }
    function mapDef() {
      var k = kS.get(), TP = 2 * Math.PI;
      switch (mapSel.value) {
        case "affine": return { T: function (x) { return 2 * x + 1; }, dT: function () { return 2; }, txt: "T(x) = 2x + 1" };
        case "square": return { T: function (x) { return x * x; }, dT: function (x) { return 2 * x; }, txt: "T(x) = x²" };
        case "quad": return { T: function (x) { return (x + x * x) / 2; }, dT: function (x) { return 0.5 + x; }, txt: "T(x) = (x + x²)/2" };
        case "fold": return { T: function (x) { return (2 * x - 1) * (2 * x - 1); }, dT: function (x) { return 4 * (2 * x - 1); }, fold: true, txt: "T(x) = (2x − 1)²" };
        default: return { T: function (x) { return x + k * Math.sin(TP * x) / TP; }, dT: function (x) { return 1 + k * Math.cos(TP * x); }, txt: "T(x) = x + s·sin(2πx)/(2π), T′(x) = 1 + s·cos(2πx)" };
      }
    }
    function inverse(M, y) { // T is increasing on [0, 1]
      var a = 0, b = 1;
      for (var it = 0; it < 50; it++) { var m = (a + b) / 2; if (M.T(m) < y) a = m; else b = m; }
      return (a + b) / 2;
    }
    function resample() {
      var key = srcSel.value, i;
      if (key !== src) {
        var rng = mulberry32(20260930);
        for (i = 0; i < NS; i++) {
          if (key === "beta") { // the median of three uniforms has density 6x(1 - x)
            var u = rng(), v = rng(), w = rng();
            XS[i] = Math.max(Math.min(u, v), Math.min(Math.max(u, v), w));
          } else XS[i] = rng();
        }
        src = key;
      }
      var M = mapDef();
      for (i = 0; i < NS; i++) YSm[i] = M.T(XS[i]);
      kS.input.disabled = mapSel.value !== "comp";
      draw();
    }
    function draw() {
      var M = mapDef(), x0 = x0S.get(), i;
      kS.out.textContent = mapSel.value === "comp" ? fmt(kS.get(), 2) : "—";
      x0S.out.textContent = fmt(x0, 2);
      var ylo = M.fold ? 0 : M.T(0), yhi = M.fold ? 1 : M.T(1);
      // top panel: the graph of T
      top.o.y = [Math.min(0, ylo), Math.max(1.05, yhi * 1.04)];
      top.clear();
      top.axes({ xticks: [0, 0.5, 1], yticks: yhi > 1.5 ? [0, 1, 2, 3] : [0, 0.5, 1], xfmt: function (v) { return fmt(v, v % 1 ? 1 : 0); }, yfmt: function (v) { return fmt(v, v % 1 ? 1 : 0); } });
      top.fn(M.T, "ln c3", 300, 0, 1);
      var T0 = M.T(x0);
      top.seg(x0, top.o.y[0], x0, T0, "ln c2 thin dot");
      top.seg(0, T0, x0, T0, "ln c3 thin dot");
      top.dot(x0, T0, 4.5, "f3");
      top.text(0, top.o.y[1], M.txt, "tx-s t3", "start", 0, -9);
      // bottom panel: densities
      var span = Math.max(1, yhi) - Math.min(0, ylo);
      bot.o.x = [Math.min(0, ylo) - 0.04 * span, Math.max(1, yhi) + 0.04 * span];
      var NB = 40, hb = (yhi - ylo) / NB, cnt = new Float64Array(NB);
      for (i = 0; i < NS; i++) { var b = Math.floor((YSm[i] - ylo) / hb); if (b >= NB) b = NB - 1; if (b >= 0) cnt[b]++; }
      var hist = [], hmax = 0;
      for (i = 0; i < NB; i++) { var h = cnt[i] / (NS * hb); hist.push(h); hmax = Math.max(hmax, h); }
      function jac(y) {
        if (M.fold) { var r = Math.sqrt(Math.max(y, 0)); return (rho((1 + r) / 2) + rho((1 - r) / 2)) / (4 * r); }
        var x = inverse(M, y); return rho(x) / Math.abs(M.dT(x));
      }
      function naive(y) {
        if (M.fold) { var r = Math.sqrt(Math.max(y, 0)); return rho((1 + r) / 2) / (4 * r); }
        return rho(inverse(M, y));
      }
      var ys = [], jmax = 0;
      for (i = 1; i < 400; i++) { var yy = ylo + (yhi - ylo) * i / 400; ys.push(yy); if (i > 12 && i < 388) jmax = Math.max(jmax, jac(yy)); }
      var ytop = l1clamp(1.15 * Math.max(hmax, jmax, 1.2), 1.3, 4.5);
      bot.o.y = [0, ytop];
      bot.clear();
      var ticks = [];
      for (var t = Math.ceil(bot.o.x[0] * 2) / 2; t <= bot.o.x[1]; t += 0.5) ticks.push(t);
      var yt = []; for (t = 0; t <= ytop; t += ytop > 3 ? 1 : 0.5) yt.push(t);
      bot.axes({ xticks: ticks, yticks: yt, xfmt: function (v) { return fmt(v, v % 1 ? 1 : 0); }, yfmt: function (v) { return fmt(v, v % 1 ? 1 : 0); } });
      bot.clip();
      for (i = 0; i < NB; i++) {
        var x1 = ylo + i * hb;
        el("rect", { x: bot.tx(x1) + 0.5, y: bot.ty(hist[i]), width: Math.max(bot.tx(x1 + hb) - bot.tx(x1) - 1, 0.5), height: bot.ty(0) - bot.ty(hist[i]), "class": "am" }, bot.g);
      }
      var srcPts = [];
      for (i = 0; i <= 200; i++) srcPts.push([i / 200, rho(i / 200)]);
      bot.poly([[0, 0]].concat(srcPts, [[1, 0]]), "a2");
      bot.poly([[0, 0]].concat(srcPts, [[1, 0]]), "ln c2 thin");
      bot.poly(ys.map(function (y) { return [y, naive(y)]; }), "ln ck thin dash");
      bot.poly(ys.map(function (y) { return [y, jac(y)]; }), "ln c3");
      bot.dot(x0, rho(x0), 4.5, "f2");
      var jy = M.fold ? (rho(x0) + rho(1 - x0)) / Math.abs(M.dT(x0)) : rho(x0) / Math.abs(M.dT(x0));
      if (isFinite(jy) && jy < ytop) bot.dot(T0, jy, 4.5, "f3");
      bot.unclip();
      // masses, by the change of variables y = T(x) on a fine grid of [0, 1]
      var mNaive = 0, NQ = 4000;
      for (i = 0; i < NQ; i++) {
        var xm = (i + 0.5) / NQ;
        if (M.fold) { if (xm > 0.5) mNaive += rho(xm) / NQ; } else mNaive += rho(xm) * Math.abs(M.dT(xm)) / NQ;
      }
      var lines = [M.txt + ";   samples X ∼ α, then the histogram of T(X)"];
      if (M.fold) {
        lines.push("at x₀ = " + fmt(x0, 2) + ": T(x₀) = " + fmt(T0, 3) + " has two preimages, x₀ and 1 − x₀, with |T′| = " + fmt(Math.abs(M.dT(x0)), 3) +
          "; ρβ(T(x₀)) = (ρα(x₀) + ρα(1 − x₀)) / |T′(x₀)| = " + fmt(jy, 3));
        lines.push("Jacobian formula summed over both preimages: mass 1.  Dashed, one preimage only: mass " + fmt(mNaive, 3) + " — half of it");
      } else {
        lines.push("at x₀ = " + fmt(x0, 2) + ": T′(x₀) = " + fmt(M.dT(x0), 3) + ", so ρβ(T(x₀)) = ρα(x₀) / T′(x₀) = " + fmt(rho(x0), 3) + " / " + fmt(M.dT(x0), 3) + " = " + fmt(jy, 3) +
          (M.dT(x0) < 0.5 ? "  — T′ small: the mass piles up" : (M.dT(x0) > 1.5 ? "  — T′ large: the mass is spread out" : "")));
        lines.push("mass of the Jacobian formula: 1 (each ρα(x)dx is kept).  Mass of the naive guess ρα∘T⁻¹: ∫ρα(x)T′(x)dx = " + fmt(mNaive, 3) +
          (Math.abs(mNaive - 1) > 5e-3 ? " ≠ 1: not even a probability density" : " — here it happens to be 1, yet its shape misses the histogram"));
      }
      ro.textContent = lines.join("\n");
    }
    resample(); redrawers.push(draw);
  };

  /* --- 4. Two sources, two targets, squared cost: the half-plane of Exercise 2 (§7) --- */
  WIDGETS.l1swap = function (box) {
    var s = scaffold(box, "Swap test for the squared cost: where must z lie for x₁ → y₁, z → y₂ to beat the swap?");
    var XR = [-3, 3], YR = [-1.8, 1.8];
    var P = new Plot(s.svg, { x: XR, y: YR, w: 680, h: 418, pad: { l: 12, r: 12, t: 12, b: 12 }, label: "Half-plane of the positions of z where the pairing Id beats the swap" });
    var names = ["x1", "z", "y1", "y2"], init = { x1: [-1.6, -0.6], z: [-0.9, 0.9], y1: [1.7, -0.9], y2: [1.1, 1.15] }, pts = {};
    button(s.controls, "Reset", function () { reset(); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "sources x₁ and z"], ["--s1", "targets y₁ and y₂"], ["--s3", "optimal pairing; green: Id wins"], ["--muted", "other pairing; grey: Swap wins"]]);
    function reset() { names.forEach(function (k) { pts[k] = init[k].slice(); }); }
    reset();
    l1drag(s.svg, P, function () { return names.map(function (k) { return pts[k]; }); }, function (k, x, y) {
      pts[names[k]] = [l1clamp(x, XR[0] + 0.1, XR[1] - 0.1), l1clamp(y, YR[0] + 0.1, YR[1] - 0.1)];
      draw();
    });
    function sq(a, b) { return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]); }
    function draw() {
      var x1 = pts.x1, z = pts.z, y1 = pts.y1, y2 = pts.y2;
      var nv = [y2[0] - y1[0], y2[1] - y1[1]], c = nv[0] * x1[0] + nv[1] * x1[1];
      var rect = [[XR[0], YR[0]], [XR[1], YR[0]], [XR[1], YR[1]], [XR[0], YR[1]]];
      var idR = l1half(rect, nv, c), swR = l1half(rect, [-nv[0], -nv[1]], -c);
      var cId = sq(x1, y1) + sq(z, y2), cSw = sq(x1, y2) + sq(z, y1);
      var ip = 2 * ((x1[0] - z[0]) * (y1[0] - y2[0]) + (x1[1] - z[1]) * (y1[1] - y2[1]));
      var idWins = cSw - cId >= 0;
      P.clear();
      if (idR.length > 2) P.poly(idR.concat([idR[0]]), "a3");
      if (swR.length > 2) P.poly(swR.concat([swR[0]]), "am");
      var L = Math.hypot(nv[0], nv[1]);
      if (L > 1e-9) {
        var d = [-nv[1] / L, nv[0] / L];
        P.clip();
        P.seg(x1[0] - 10 * d[0], x1[1] - 10 * d[1], x1[0] + 10 * d[0], x1[1] + 10 * d[1], "ln c3 thin dash");
        P.unclip();
        [[idR, "Id wins", "tx-b t3"], [swR, "Swap wins", "tx-b"]].forEach(function (r) {
          if (r[0].length < 3) return;
          var g = l1centroid(r[0]);
          P.text(g[0], g[1], r[1], r[2], "middle");
        });
      }
      var win = idWins ? [[x1, y1], [z, y2]] : [[x1, y2], [z, y1]], lose = idWins ? [[x1, y2], [z, y1]] : [[x1, y1], [z, y2]];
      lose.forEach(function (e) { l1arrow(P, e[0][0], e[0][1], e[1][0], e[1][1], "ln cm thin dash", "fm", 10); });
      win.forEach(function (e) { l1arrow(P, e[0][0], e[0][1], e[1][0], e[1][1], "ln c3", "f3", 10); });
      [["x1", "x₁", "f2"], ["z", "z", "f2"], ["y1", "y₁", "f1"], ["y2", "y₂", "f1"]].forEach(function (q) {
        var p = pts[q[0]];
        P.dot(p[0], p[1], 7.5, q[2] + " drag");
        P.text(p[0], p[1], q[1], "tx-i", "middle", 0, -13);
      });
      ro.textContent = "cost(Id)   = ‖x₁ − y₁‖² + ‖z − y₂‖² = " + fmt(sq(x1, y1), 3) + " + " + fmt(sq(z, y2), 3) + " = " + fmt(cId, 3) +
        "\ncost(Swap) = ‖x₁ − y₂‖² + ‖z − y₁‖² = " + fmt(sq(x1, y2), 3) + " + " + fmt(sq(z, y1), 3) + " = " + fmt(cSw, 3) +
        "\ncost(Swap) − cost(Id) = " + fmt(cSw - cId, 3) + "   and   2 (x₁ − z)·(y₁ − y₂) = " + fmt(ip, 3) +
        "\n→ z is in the " + (idWins ? "green half-plane: Id is optimal" : "grey half-plane: Swap is optimal") +
        " (the boundary is the line through x₁ orthogonal to y₁ − y₂)";
    }
    draw(); redrawers.push(draw);
  };

  /* --- 5. Brenier map between two Gaussians in the plane, the Bures term and McCann's interpolation (§8) --- */
  WIDGETS.l1gauss = function (box) {
    var s = scaffold(box, "The Brenier map between two Gaussians: T(x) = mβ + A(x − mα), with A symmetric positive definite");
    var XR = [-4.5, 6.5], YR = [-3, 4];
    var P = new Plot(s.svg, { x: XR, y: YR, w: 680, h: 445, pad: { l: 10, r: 10, t: 10, b: 15 }, label: "Ellipses of two Gaussians, arrows of the optimal affine map and of an admissible non-optimal map" });
    var s1S = slider(s.controls, "σ₁ of β", 0.3, 3, 0.05, 1, draw);
    var s2S = slider(s.controls, "σ₂ of β", 0.3, 3, 0.05, 2, draw);
    var thS = slider(s.controls, "angle of β", 0, 180, 1, 0, draw);
    var tS = slider(s.controls, "McCann t", 0, 1, 0.01, 0, draw);
    var cmp = checkbox(s.controls, "compare with A′ = Σβ<sup>½</sup>Σα<sup>−½</sup>", false, draw);
    button(s.controls, "Worked example", function () { s1S.set(1); s2S.set(2); thS.set(0); tS.set(0); mA = [0, 0]; mB = [2, 1]; draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "α = 𝒩(mα, Σα): 0.5 and 1 std"], ["--s1", "β = 𝒩(mβ, Σβ)"], ["--s3", "x → T(x); 𝒩(mₜ, Σₜ)"], ["--muted", "x → A′ map (compare)"]]);
    var SA = [2, 1, 1, 2], mA = [0, 0], mB = [2, 1];
    l1drag(s.svg, P, function () { return [mA, mB]; }, function (k, x, y) {
      var q = [l1clamp(x, XR[0] + 0.3, XR[1] - 0.3), l1clamp(y, YR[0] + 0.3, YR[1] - 0.3)];
      if (k === 0) mA = q; else mB = q;
      draw();
    });
    function draw() {
      var s1 = s1S.get(), s2 = s2S.get(), th = thS.get() * Math.PI / 180, t = tS.get();
      s1S.out.textContent = fmt(s1, 2); s2S.out.textContent = fmt(s2, 2); thS.out.textContent = thS.get() + "°"; tS.out.textContent = fmt(t, 2);
      var c = Math.cos(th), sn = Math.sin(th), R = [c, -sn, sn, c];
      var SB = msym(mmul(mmul(R, [s1 * s1, 0, 0, s2 * s2]), l1tr(R)));
      var rA = msqrt(SA), irA = minv(rA);
      var A = msym(mmul(mmul(irA, msqrt(msym(mmul(mmul(rA, SB), rA)))), irA));
      var Ap = mmul(msqrt(SB), irA);
      var dm = [mB[0] - mA[0], mB[1] - mA[1]], dm2 = dm[0] * dm[0] + dm[1] * dm[1];
      var B2 = Math.pow(bures(SA, SB), 2);
      var IAp = [1 - Ap[0], -Ap[1], -Ap[2], 1 - Ap[3]], E = mmul(mmul(IAp, SA), l1tr(IAp));
      var costAp = dm2 + E[0] + E[3];
      var Mt = [(1 - t) + t * A[0], t * A[1], t * A[2], (1 - t) + t * A[3]], St = msym(mmul(mmul(Mt, SA), Mt));
      var mt = [(1 - t) * mA[0] + t * mB[0], (1 - t) * mA[1] + t * mB[1]];
      function T(x) { var u = [x[0] - mA[0], x[1] - mA[1]]; return [mB[0] + A[0] * u[0] + A[1] * u[1], mB[1] + A[2] * u[0] + A[3] * u[1]]; }
      function Tp(x) { var u = [x[0] - mA[0], x[1] - mA[1]]; return [mB[0] + Ap[0] * u[0] + Ap[1] * u[1], mB[1] + Ap[2] * u[0] + Ap[3] * u[1]]; }
      P.clear();
      P.clip();
      P.seg(XR[0], 0, XR[1], 0, "gr"); P.seg(0, YR[0], 0, YR[1], "gr");
      P.poly(ellipsePts(mA, SA, 1), "a2");
      P.poly(ellipsePts(mA, SA, 1), "ln c2");
      P.poly(ellipsePts(mA, SA, 0.5), "ln c2 thin");
      P.poly(ellipsePts(mB, SB, 1), "a1");
      P.poly(ellipsePts(mB, SB, 1), "ln c1");
      P.poly(ellipsePts(mB, SB, 0.5), "ln c1 thin");
      var src = [], k;
      [0.5, 1].forEach(function (r) {
        var e = ellipsePts(mA, SA, r);
        for (k = 0; k < 96; k += 12) src.push(e[k]);
      });
      if (cmp.checked) src.forEach(function (x) { var y = Tp(x); l1arrow(P, x[0], x[1], y[0], y[1], "ln cm thin dash", "fm"); });
      src.forEach(function (x) { var y = T(x); l1arrow(P, x[0], x[1], y[0], y[1], "ln c3 thin", "f3"); });
      if (t > 0) {
        P.poly(ellipsePts(mt, St, 1), "ln c3");
        P.poly(ellipsePts(mt, St, 0.5), "ln c3 thin");
        src.forEach(function (x) { var y = T(x); P.dot((1 - t) * x[0] + t * y[0], (1 - t) * x[1] + t * y[1], 3, "f3"); });
      }
      src.forEach(function (x) { P.dot(x[0], x[1], 2.6, "f2"); });
      P.dot(mA[0], mA[1], 6.5, "f2 drag"); P.dot(mB[0], mB[1], 6.5, "f1 drag");
      P.text(mA[0], mA[1], "mα", "tx-s", "middle", 0, 18);
      P.text(mB[0], mB[1], "mβ", "tx-s", "middle", 0, 18);
      P.unclip();
      var ev = l1eig(A), chk = msym(mmul(mmul(A, SA), A));
      var lines = ["Σα = " + l1mat(SA) + "   Σβ = " + l1mat(SB),
        "A = " + l1mat(A) + "   eigenvalues " + fmt(ev[0], 3) + ", " + fmt(ev[1], 3) + " (> 0: T = ∇φ with φ convex);   AΣαA = " + l1mat(chk),
        "‖mα − mβ‖² = " + fmt(dm2, 3) + "   𝔅²(Σα, Σβ) = " + fmt(B2, 3) + "   W₂² = " + fmt(dm2 + B2, 3)];
      if (cmp.checked) lines.push("A′ = " + l1mat(Ap) + (Math.abs(Ap[1] - Ap[2]) > 1e-6 ? " (not symmetric)" : " (symmetric: here A′ = A)") +
        ": admissible, its cost is " + fmt(costAp, 3) + (costAp - dm2 - B2 > 1e-6 ? " > " + fmt(dm2 + B2, 3) : " = W₂²"));
      if (t > 0) lines.push("t = " + fmt(t, 2) + ": mₜ = (" + fmt(mt[0], 2) + ", " + fmt(mt[1], 2) + "), Σₜ = " + l1mat(St) + " — the green ellipse");
      ro.textContent = lines.join("\n");
    }
    draw(); redrawers.push(draw);
  };

  /* --- 6. One dimension: the quantile map T = Cβ⁻¹ ∘ Cα, W₁ and W₂ by quantiles, McCann's interpolation (§9) --- */
  function l1Phi(x) { // CDF of N(0, 1) (Abramowitz-Stegun 7.1.26, error < 1.5e-7)
    var z = Math.abs(x) / Math.SQRT2, t = 1 / (1 + 0.3275911 * z);
    var y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-z * z);
    return x >= 0 ? 0.5 * (1 + y) : 0.5 * (1 - y);
  }
  function l1Phinv(p) { // inverse of l1Phi (Acklam's rational approximation, relative error < 1.2e-9)
    var a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00];
    var b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01];
    var c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00];
    var d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00];
    var q, r;
    if (p < 0.02425 || p > 0.97575) {
      q = Math.sqrt(-2 * Math.log(p < 0.5 ? p : 1 - p));
      var v = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
      return p < 0.5 ? v : -v;
    }
    q = p - 0.5; r = q * q;
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
  }
  function l1mix(w, m, sd) { return function (x) { var v = 0; for (var i = 0; i < w.length; i++) v += w[i] * gpdf(x, m[i], sd[i]); return v; }; }
  var L1PAIRS = {
    modes: { L: -4, R: 4, a: l1mix([0.46, 0.54], [-1.45, 0.78], [0.34, 0.43]), b: l1mix([0.24, 0.43, 0.33], [-2.02, 0.05, 1.92], [0.24, 0.39, 0.28]),
      xr: [-3.4, 3.4], tx: [-3.4, 3.4], ty: [-3.4, 3.4], ticks: [-3, -2, -1, 0, 1, 2, 3], tt: [-3, 0, 3] },
    expo: { L: -0.5, R: 10, a: function (x) { return updf(x, 0, 1); }, b: function (x) { return x >= 0 ? Math.exp(-x) : 0; },
      qa: function (r) { return r; }, qb: function (r) { return -Math.log(1 - r); },
      Ca: function (x) { return l1clamp(x, 0, 1); }, Cb: function (x) { return x > 0 ? 1 - Math.exp(-x) : 0; },
      xr: [-0.3, 4.5], tx: [-0.1, 1.1], ty: [-0.3, 4.5], ticks: [0, 1, 2, 3, 4], tt: [0, 1, 2, 3, 4] },
    gauss: { L: -5, R: 11, a: function (x) { return gpdf(x, 0, 1); }, b: function (x) { return gpdf(x, 3, 2); },
      qa: function (r) { return l1Phinv(r); }, qb: function (r) { return 3 + 2 * l1Phinv(r); },
      Ca: function (x) { return l1Phi(x); }, Cb: function (x) { return l1Phi((x - 3) / 2); },
      xr: [-3.5, 9], tx: [-3.2, 3.2], ty: [-4, 10], ticks: [-2, 0, 2, 4, 6, 8], tt: [-3, 0, 3, 6, 9] }
  };
  function l1cdfAt(line, x) { // tabulated CDF, linear interpolation
    var xs = line.xs, n = xs.length, h = xs[1] - xs[0], i = Math.floor((x - xs[0]) / h);
    if (i < 0) return 0;
    if (i >= n - 1) return 1;
    var f = (x - xs[i]) / h;
    return line.c[i] + f * (line.c[i + 1] - line.c[i]);
  }
  function l1qAt(line, r) { // generalized inverse of the tabulated CDF at the level r
    var c = line.c, a = 0, b = c.length - 1;
    while (b - a > 1) { var m = (a + b) >> 1; if (c[m] < r) a = m; else b = m; }
    var c0 = c[a], c1 = c[b];
    return c1 > c0 ? line.xs[a] + (r - c0) / (c1 - c0) * (line.xs[b] - line.xs[a]) : line.xs[b];
  }
  WIDGETS.l1quantile = function (box) {
    var s = scaffold(box, "The one-dimensional Monge map T = Cβ⁻¹ ∘ Cα: equal levels of mass, and McCann's interpolation");
    var top = new Plot(s.svg, { x: [-3.4, 3.4], y: [0, 1], w: 680, h: 200, pad: { l: 40, r: 16, t: 14, b: 26 }, label: "Densities of alpha, beta, McCann's interpolation and the mixture" });
    var botSvg = addSvg(box, s.svg);
    var cdfP = new Plot(botSvg, { x: [-3.4, 3.4], y: [0, 1.02], w: 680, h: 262, pad: { l: 40, r: 286, t: 22, b: 30 }, label: "The two CDFs and the path through the level r" });
    var tP = new Plot(botSvg, { x: [-3.4, 3.4], y: [-3.4, 3.4], w: 680, h: 262, pad: { l: 462, r: 14, t: 22, b: 30 }, label: "Graph of the map T" });
    var pairSel = select(s.controls, "laws", [["modes", "two modes → three modes (figure)"], ["expo", "𝒰[0, 1] → Exp(1)"], ["gauss", "𝒩(0, 1) → 𝒩(3, 4)"]], "modes", prep);
    var rS = slider(s.controls, "level r", 0.01, 0.99, 0.01, 0.3, draw);
    var tS = slider(s.controls, "McCann t", 0, 1, 0.01, 0.5, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "α"], ["--s1", "β"], ["--s3", "McCann interpolation αₜ; map T"], ["--muted", "mixture (1 − t)α + tβ (dashed)"]]);
    var D = null, la = null, lb = null, qa = null, qb = null, ymax = 1, W1q = 0, W1c = 0, W2 = 0, QA, QB;
    function prep() {
      D = L1PAIRS[pairSel.value];
      la = new Line1D(D.L, D.R, 4201, D.a); lb = new Line1D(D.L, D.R, 4201, D.b);
      qa = quantiles(la.xs, la.c); qb = quantiles(lb.xs, lb.c);
      // exact quantile functions and CDFs when known, tabulated ones otherwise
      QA = D.qa || function (r) { return l1qAt(la, r); }; QB = D.qb || function (r) { return l1qAt(lb, r); };
      var CA = D.Ca || function (x) { return l1cdfAt(la, x); }, CB = D.Cb || function (x) { return l1cdfAt(lb, x); };
      // (2.11) with the levels r = 3v² − 2v³ (dr = 6v(1 − v) dv), which tames the tails; (2.12) by trapezoids
      var i, s1 = 0, s2 = 0, sc = 0, K = 20000;
      for (i = 0; i < K; i++) {
        var v = (i + 0.5) / K, rr = v * v * (3 - 2 * v), wv = 6 * v * (1 - v), d = Math.abs(QA(rr) - QB(rr));
        s1 += wv * d; s2 += wv * d * d;
      }
      W1q = s1 / K; W2 = Math.sqrt(s2 / K);
      var hx = (D.R - D.L) / K, prev = Math.abs(CA(D.L) - CB(D.L));
      for (i = 1; i <= K; i++) { var cur = Math.abs(CA(D.L + i * hx) - CB(D.L + i * hx)); sc += 0.5 * hx * (prev + cur); prev = cur; }
      W1c = sc;
      ymax = 0;
      for (i = 0; i < la.xs.length; i++) if (la.xs[i] >= D.xr[0] && la.xs[i] <= D.xr[1]) ymax = Math.max(ymax, la.d[i], lb.d[i]);
      for (var k = 1; k < 10; k++) {
        var q = new Float64Array(MQ);
        for (i = 0; i < MQ; i++) q[i] = (1 - k / 10) * qa[i] + k / 10 * qb[i];
        densityFromQ(q).forEach(function (p) { if (isFinite(p[1]) && p[0] >= D.xr[0] && p[0] <= D.xr[1]) ymax = Math.max(ymax, p[1]); });
      }
      top.o.x = D.xr; top.o.y = [0, 1.12 * ymax];
      cdfP.o.x = D.xr; tP.o.x = D.tx; tP.o.y = D.ty;
      draw();
    }
    function draw() {
      var r = rS.get(), t = tS.get(), i;
      rS.out.textContent = fmt(r, 2); tS.out.textContent = fmt(t, 2);
      // top: densities, McCann interpolation and mixture
      top.clear();
      top.axes({ xticks: D.ticks, yticks: [], nogrid: true });
      top.clip();
      var pa = [], pb = [], pm = [];
      for (i = 0; i < la.xs.length; i += 2) {
        var x = la.xs[i];
        if (x < D.xr[0] - 0.1 || x > D.xr[1] + 0.1) continue;
        pa.push([x, la.d[i]]); pb.push([x, lb.d[i]]); pm.push([x, (1 - t) * la.d[i] + t * lb.d[i]]);
      }
      top.poly([[pa[0][0], 0]].concat(pa, [[pa[pa.length - 1][0], 0]]), "a2");
      top.poly(pa, "ln c2 thin");
      top.poly([[pb[0][0], 0]].concat(pb, [[pb[pb.length - 1][0], 0]]), "a1");
      top.poly(pb, "ln c1 thin");
      if (t > 0 && t < 1) top.poly(pm, "ln cm thin dash");
      var qt = new Float64Array(MQ);
      for (i = 0; i < MQ; i++) qt[i] = (1 - t) * qa[i] + t * qb[i];
      top.poly(densityFromQ(qt), "ln c3");
      top.unclip();
      top.text(D.xr[0], top.o.y[1], "densities; green: αₜ at t = " + fmt(t, 2), "tx-s", "start", 4, 12);
      // bottom left: the CDFs and the path through the level r
      var x0 = QA(r), y0 = QB(r);
      while (botSvg.firstChild) botSvg.removeChild(botSvg.firstChild);
      cdfP.g = el("g", {}, botSvg);
      cdfP.axes({ xticks: D.ticks, yticks: [0, 0.5, 1], xfmt: function (v) { return fmt(v, 0); }, yfmt: function (v) { return fmt(v, v % 1 ? 1 : 0); } });
      cdfP.clip();
      var ca = [], cb = [];
      for (i = 0; i < la.xs.length; i += 2) { ca.push([la.xs[i], la.c[i]]); cb.push([lb.xs[i], lb.c[i]]); }
      cdfP.poly(ca, "ln c2"); cdfP.poly(cb, "ln c1");
      cdfP.seg(x0, 0, x0, r, "ln c3 thin dot");
      cdfP.seg(x0, r, y0, r, "ln c3 thin dot");
      cdfP.seg(y0, r, y0, 0, "ln c3 thin dot");
      cdfP.dot(x0, r, 3.5, "f2"); cdfP.dot(y0, r, 3.5, "f1");
      cdfP.dot(x0, 0, 5, "f2"); cdfP.dot(y0, 0, 5, "f1");
      cdfP.unclip();
      cdfP.text(D.xr[0], 1.02, "CDFs Cα (orange), Cβ (blue)", "tx-s", "start", 2, -8);
      cdfP.text(x0, 0, "x", "tx-s t2", "middle", 0, -9);
      cdfP.text(y0, 0, "T(x)", "tx-s t1", "middle", 0, -9);
      // bottom right: the graph of T
      tP.g = el("g", {}, botSvg);
      tP.axes({ xticks: D.tt.filter(function (v) { return v >= D.tx[0] && v <= D.tx[1]; }), yticks: D.tt, xfmt: function (v) { return fmt(v, 0); }, yfmt: function (v) { return fmt(v, 0); } });
      tP.clip();
      tP.seg(Math.max(D.tx[0], D.ty[0]), Math.max(D.tx[0], D.ty[0]), Math.min(D.tx[1], D.ty[1]), Math.min(D.tx[1], D.ty[1]), "gr");
      var gp = [];
      for (i = 0; i < MQ; i += 3) gp.push([qa[i], qb[i]]);
      tP.poly(gp, "ln c3");
      tP.seg(x0, D.ty[0], x0, y0, "ln c2 thin dot");
      tP.seg(D.tx[0], y0, x0, y0, "ln c1 thin dot");
      tP.dot(x0, y0, 5, "f3");
      tP.unclip();
      tP.text(D.tx[0], D.ty[1], "graph of T", "tx-s", "start", 4, -8);
      // check of T'(x) = rho_alpha(x) / rho_beta(T(x)) by finite differences in the level
      var dr = 0.004, r1 = Math.max(r - dr, 0.001), r2 = Math.min(r + dr, 0.999);
      var dT = (QB(r2) - QB(r1)) / (QA(r2) - QA(r1));
      var ra = D.a(x0), rb = D.b(y0);
      ro.textContent = "level r = " + fmt(r, 2) + ":  x = Cα⁻¹(r) = " + fmt(x0, 3) + "   T(x) = Cβ⁻¹(r) = " + fmt(y0, 3) +
        "\ncheck: T′(x) ≈ " + fmt(dT, 3) + " (finite difference)   ρα(x) / ρβ(T(x)) = " + fmt(ra, 3) + " / " + fmt(rb, 3) + " = " + fmt(ra / rb, 3) +
        "\nW₁ by (2.11): ∫|Cα⁻¹ − Cβ⁻¹| dr = " + fmt(W1q, 3) + "   by (2.12): ∫|Cα − Cβ| dx = " + fmt(W1c, 3) +
        "\nW₂ by (2.11): (∫|Cα⁻¹ − Cβ⁻¹|² dr)^½ = " + fmt(W2, 3) + "   W₂² = " + fmt(W2 * W2, 3);
    }
    prep(); redrawers.push(draw);
  };
