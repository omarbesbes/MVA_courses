// widgets/Lesson05.js — interactive figures of Lesson 5 (sliced optimal transport).
// This file is inserted by build.mjs inside the scope of app.js: it uses el, fmt, Plot, scaffold, slider, select,
// button, checkbox, readout, legend, addSvg, svgPoint, mulberry32, gaussRand, hungarian and redrawers, and
// registers WIDGETS.l5slices, WIDGETS.l5gauss, WIDGETS.l5mc and WIDGETS.l5flow. Own helpers are prefixed l5.

  /* ---------------- helpers of this page ---------------- */
  function l5cmp(u, v) { return u - v; }
  function l5argsort(a) {
    var idx = a.map(function (v, i) { return i; });
    idx.sort(function (i, j) { return a[i] - a[j]; });
    return idx;
  }
  function l5proj(P, th) { return P.map(function (p) { return p[0] * th[0] + p[1] * th[1]; }); }
  function l5w22sorted(a, b) { // W2^2 between two uniform measures on n numbers: sort and match
    var x = a.slice().sort(l5cmp), y = b.slice().sort(l5cmp), s = 0;
    for (var i = 0; i < x.length; i++) s += (x[i] - y[i]) * (x[i] - y[i]);
    return s / x.length;
  }
  function l5w22exact(A, B) { // exact W2^2 between two uniform clouds of the same size (Hungarian)
    var C = A.map(function (a) { return B.map(function (b) { var dx = a[0] - b[0], dy = a[1] - b[1]; return dx * dx + dy * dy; }); });
    var asg = hungarian(C), s = 0;
    for (var i = 0; i < A.length; i++) s += C[i][asg[i]];
    return { cost: s / A.length, asg: asg };
  }
  function l5gamma(rng, k) { // Gamma(k, 1) variate (Marsaglia–Tsang; boost for k < 1)
    if (k < 1) return l5gamma(rng, k + 1) * Math.pow(rng(), 1 / k);
    var d = k - 1 / 3, c = 1 / Math.sqrt(9 * d);
    for (;;) {
      var x = gaussRand(rng), v = 1 + c * x;
      if (v <= 0) continue;
      v = v * v * v;
      var u = rng();
      if (u < 1 - 0.0331 * x * x * x * x) return d * v;
      if (Math.log(u) < 0.5 * x * x + d * (1 - v + Math.log(v))) return d * v;
    }
  }
  function l5theta12(rng, d) { // first two coordinates of a uniform direction of R^d (d >= 2)
    var g1 = gaussRand(rng), g2 = gaussRand(rng), S = d > 2 ? 2 * l5gamma(rng, (d - 2) / 2) : 0;
    var r = Math.sqrt(g1 * g1 + g2 * g2 + S);
    return [g1 / r, g2 / r];
  }
  function l5theta1(rng, d) { // first coordinate of a uniform direction of R^d
    if (d === 1) return rng() < 0.5 ? -1 : 1;
    var g = gaussRand(rng), S = 2 * l5gamma(rng, (d - 1) / 2);
    return g / Math.sqrt(g * g + S);
  }
  function l5sphereMean(f, d) { // E f(theta_1) for theta uniform on the sphere of R^d (quadrature in the polar angle)
    if (d === 1) return 0.5 * (f(1) + f(-1));
    var N = 4000, i, phi, lw, mx = -Infinity, ws = [], s = 0, z = 0;
    for (i = 0; i < N; i++) { phi = (i + 0.5) * Math.PI / N; lw = (d - 2) * Math.log(Math.sin(phi)); ws.push(lw); if (lw > mx) mx = lw; }
    for (i = 0; i < N; i++) { phi = (i + 0.5) * Math.PI / N; var w = Math.exp(ws[i] - mx); s += w * f(Math.cos(phi)); z += w; }
    return s / z;
  }
  function l5ticks(max) { // a few round ticks in [0, max]
    var raw = max / 4, p = Math.pow(10, Math.floor(Math.log10(raw))), m = raw / p;
    var step = (m < 1.5 ? 1 : m < 3.5 ? 2 : m < 7.5 ? 5 : 10) * p, t = [];
    for (var v = 0; v <= max + 1e-9; v += step) t.push(Math.round(v / step) * step);
    return t;
  }
  function l5niceTicks(lo, hi) { // round ticks inside [lo, hi]
    var raw = (hi - lo) / 4, p = Math.pow(10, Math.floor(Math.log10(raw))), m = raw / p;
    var step = (m < 1.5 ? 1 : m < 3.5 ? 2 : m < 7.5 ? 5 : 10) * p, t = [];
    for (var v = Math.ceil(lo / step - 1e-9) * step; v <= hi + 1e-9; v += step) t.push(Math.round(v / step) * step);
    return t;
  }
  function l5sup(e) { var m = { "-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹" }; return "10" + String(e).split("").map(function (c) { return m[c]; }).join(""); }
  function l5exp(v) { return v === 0 ? "0" : (Math.abs(v) >= 0.01 && Math.abs(v) < 1000 ? fmt(v, 4) : v.toExponential(2)); }
  function l5text(g, x, y, s, cls, anchor) {
    var t = el("text", { x: x, y: y, "class": cls || "tx-s", "text-anchor": anchor || "start" }, g);
    t.textContent = s; return t;
  }

  /* --- 1. Slices of two clouds and the profile of the slice costs (§4) --- */
  WIDGETS.l5slices = function (box) {
    var s = scaffold(box, "Slices of two clouds: the cost of each direction, its average SW₂² and its maximum");
    var W = 680, H = 440;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Two point clouds, their projections on a direction, and the cost of the sorted matching as a function of the direction");
    var PRE = {
      cross: { A: [[-1, 0], [1, 0]], B: [[0, -1], [0, 1]] },
      cw: { A: [[0, 0], [1, 1]], B: [[1, 0], [0, 1]] },
      pairs: { A: [[0, 0], [1, 3]], B: [[1, 0], [0, 3]] }
    };
    var presetSel = select(s.controls, "Clouds", [["cross", "the cross (§4)"], ["cw", "two diagonals (§5)"], ["pairs", "two pairs (sheet, Ex. 2)"], ["trans", "a translated copy"], ["random", "random clouds"]], "cross", setup);
    var phiS = slider(s.controls, "direction φ", 0, 179.5, 0.5, 25, draw);
    button(s.controls, "New random clouds", function () { seed++; presetSel.value = "random"; setup(); });
    var projChk = checkbox(s.controls, "projection lines", true, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "α"], ["--s1", "β"], ["--s3", "sorted matching; average = SW₂²"], ["--s4", "maximum = MaxSW₂²"], ["--muted", "W₂² and W₂²/2"]]);
    var seed = 1, A, B, prof = [], NP = 720, sw, mx, mxPhi, w2, cx, cy, sc, R;
    var LP = { x: 12, y: 30, w: 300, h: 300 }, TP = { x: 340, y: 30, w: 320, h: 120 }, PP = { x: 372, y: 196, w: 240, h: 196 };

    function makeData() {
      var key = presetSel.value, i, rng;
      if (PRE[key]) { A = PRE[key].A; B = PRE[key].B; return; }
      if (key === "trans") {
        rng = mulberry32(5);
        A = []; for (i = 0; i < 6; i++) A.push([0.6 * gaussRand(rng), 0.6 * gaussRand(rng)]);
        B = A.map(function (p) { return [p[0] + 1.2, p[1] + 0.5]; });
        return;
      }
      rng = mulberry32(1000 + 7919 * seed);
      A = []; B = [];
      var c = Math.cos(0.5), sn = Math.sin(0.5);
      for (i = 0; i < 8; i++) {
        var u = 0.9 * gaussRand(rng), v = 0.3 * gaussRand(rng);
        A.push([-0.5 + c * u - sn * v, sn * u + c * v]);
        B.push([0.7 + 0.5 * gaussRand(rng), 0.4 + 0.5 * gaussRand(rng)]);
      }
    }
    function setup() {
      makeData();
      prof = [];
      sw = 0; mx = -1; mxPhi = 0;
      for (var k = 0; k < NP; k++) {
        var ph = k * Math.PI / NP, th = [Math.cos(ph), Math.sin(ph)];
        var v = l5w22sorted(l5proj(A, th), l5proj(B, th));
        prof.push(v); sw += v;
        if (v > mx + 1e-12) { mx = v; mxPhi = ph; }
      }
      sw /= NP;
      w2 = l5w22exact(A, B).cost;
      var all = A.concat(B), x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      all.forEach(function (p) { x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0]); y0 = Math.min(y0, p[1]); y1 = Math.max(y1, p[1]); });
      cx = (x0 + x1) / 2; cy = (y0 + y1) / 2;
      var L = Math.max(x1 - x0, y1 - y0) / 2 * 1.3 + 0.25;
      sc = LP.w / (2 * L);
      R = 0; all.forEach(function (p) { R = Math.max(R, Math.hypot(p[0] - cx, p[1] - cy)); });
      R = R * 1.08 + 0.05;
      draw();
    }
    function PX(x) { return LP.x + LP.w / 2 + (x - cx) * sc; }
    function PY(y) { return LP.y + LP.h / 2 - (y - cy) * sc; }
    function draw() {
      var phiDeg = phiS.get(), ph = phiDeg * Math.PI / 180, th = [Math.cos(ph), Math.sin(ph)], i;
      phiS.out.textContent = fmt(phiDeg, 1) + "°";
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg);
      // left panel: clouds, the line through the centre, projections
      var cid = "l5sl" + Math.random().toString(36).slice(2);
      var cp = el("clipPath", { id: cid }, s.svg);
      el("rect", { x: LP.x, y: LP.y, width: LP.w, height: LP.h }, cp);
      el("rect", { x: LP.x, y: LP.y, width: LP.w, height: LP.h, "class": "ln cm hair nofill" }, g);
      var gl = el("g", { "clip-path": "url(#" + cid + ")" }, g);
      var big = 2 * LP.w / sc;
      el("line", { x1: PX(cx - big * th[0]), y1: PY(cy - big * th[1]), x2: PX(cx + big * th[0]), y2: PY(cy + big * th[1]), "class": "ln c3 thin" }, gl);
      function foot(p) { var t = (p[0] - cx) * th[0] + (p[1] - cy) * th[1]; return [cx + t * th[0], cy + t * th[1]]; }
      [[A, "2"], [B, "1"]].forEach(function (pair) {
        pair[0].forEach(function (p) {
          var q = foot(p);
          if (projChk.checked) el("line", { x1: PX(p[0]), y1: PY(p[1]), x2: PX(q[0]), y2: PY(q[1]), "class": "ln c" + pair[1] + " hair dash", "stroke-opacity": 0.6 }, gl);
          el("circle", { cx: PX(q[0]), cy: PY(q[1]), r: 2.6, "class": "f" + pair[1] }, gl);
        });
      });
      A.forEach(function (p) { el("circle", { cx: PX(p[0]), cy: PY(p[1]), r: 5.5, "class": "f2" }, gl); });
      B.forEach(function (p) { el("circle", { cx: PX(p[0]), cy: PY(p[1]), r: 5.5, "class": "f1" }, gl); });
      var tipx = PX(cx + 0.42 * LP.w / sc * th[0]), tipy = PY(cy + 0.42 * LP.w / sc * th[1]);
      l5text(g, tipx + 6, tipy - 4, "θ", "tx-i");
      l5text(g, LP.x + LP.w / 2, LP.y - 10, "the clouds and the line of direction θ", "tx-b", "middle");
      // top right: the two slices and the sorted matching
      l5text(g, TP.x + TP.w / 2, TP.y - 10, "the two slices (centred), matched by rank", "tx-b", "middle");
      function TX(v) { return TP.x + (v + R) / (2 * R) * TP.w; }
      var ya = TP.y + 35, yb = TP.y + 85;
      el("line", { x1: TP.x, x2: TP.x + TP.w, y1: (ya + yb) / 2, y2: (ya + yb) / 2, "class": "ax" }, g);
      var pa = A.map(function (p) { return (p[0] - cx) * th[0] + (p[1] - cy) * th[1]; });
      var pb = B.map(function (p) { return (p[0] - cx) * th[0] + (p[1] - cy) * th[1]; });
      var sa = pa.slice().sort(l5cmp), sb = pb.slice().sort(l5cmp);
      for (i = 0; i < sa.length; i++) el("line", { x1: TX(sa[i]), y1: ya, x2: TX(sb[i]), y2: yb, "class": "ln c3 thin" }, g);
      sa.forEach(function (v) { el("circle", { cx: TX(v), cy: ya, r: 4.5, "class": "f2" }, g); });
      sb.forEach(function (v) { el("circle", { cx: TX(v), cy: yb, r: 4.5, "class": "f1" }, g); });
      l5text(g, TP.x, ya - 10, "slice of α", "tx-s t2");
      l5text(g, TP.x, yb + 20, "slice of β", "tx-s t1");
      var vcur = l5w22sorted(pa, pb);
      // bottom right: the profile
      var ymax = Math.max(w2, mx) * 1.12;
      function QX(deg) { return PP.x + deg / 180 * PP.w; }
      function QY(v) { return PP.y + PP.h - v / ymax * PP.h; }
      l5text(g, PP.x + PP.w / 2 + 20, PP.y - 12, "W₂² between the slices, for every φ", "tx-b", "middle");
      el("line", { x1: PP.x, x2: PP.x + PP.w, y1: PP.y + PP.h, y2: PP.y + PP.h, "class": "ax" }, g);
      el("line", { x1: PP.x, x2: PP.x, y1: PP.y, y2: PP.y + PP.h, "class": "ax" }, g);
      [0, 45, 90, 135, 180].forEach(function (d) {
        el("line", { x1: QX(d), x2: QX(d), y1: PP.y, y2: PP.y + PP.h, "class": "gr" }, g);
        l5text(g, QX(d), PP.y + PP.h + 15, d + "°", "tx-s", "middle");
      });
      l5ticks(ymax).forEach(function (v) {
        if (v === 0) return;
        el("line", { x1: PP.x, x2: PP.x + PP.w, y1: QY(v), y2: QY(v), "class": "gr" }, g);
        l5text(g, PP.x - 5, QY(v) + 4, fmt(v, v < 1 ? 2 : 1), "tx-s", "end");
      });
      var lines = [[w2, "ln cm", "W₂²"], [w2 / 2, "ln cm dash", "W₂²/2"], [sw, "ln c3 dash", "SW₂²"], [mx, "ln c4 dot", "max"]];
      lines.forEach(function (L) { el("line", { x1: PP.x, x2: PP.x + PP.w, y1: QY(L[0]), y2: QY(L[0]), "class": L[1] }, g); });
      var d = "";
      for (i = 0; i <= NP; i++) d += (i ? "L" : "M") + QX(i * 180 / NP).toFixed(1) + " " + QY(prof[i % NP]).toFixed(1);
      el("path", { d: d, "class": "ln ck thin" }, g);
      el("line", { x1: QX(phiDeg), x2: QX(phiDeg), y1: PP.y, y2: PP.y + PP.h, "class": "ln c3 hair" }, g);
      el("circle", { cx: QX(phiDeg), cy: QY(vcur), r: 4.5, "class": "f3" }, g);
      // labels of the horizontal lines, pushed apart
      var labs = lines.map(function (L) { return { y: QY(L[0]) + 4, t: L[2], c: L[1].indexOf("c3") >= 0 ? "tx-s t3" : "tx-s" }; });
      labs.sort(function (a, b) { return a.y - b.y; });
      for (i = 1; i < labs.length; i++) if (labs[i].y - labs[i - 1].y < 11) labs[i].y = labs[i - 1].y + 11;
      labs.forEach(function (lb) { l5text(g, PP.x + PP.w + 4, lb.y, lb.t, lb.c, "start"); });
      ro.textContent = "φ = " + fmt(phiDeg, 1) + "°:  W₂² between the slices = " + fmt(vcur, 4) + "  (green segments: the sorted matching of this direction)" +
        "\naverage over all directions SW₂² = " + fmt(sw, 4) + "    maximum MaxSW₂² = " + fmt(mx, 4) + " (at φ = " + fmt(mxPhi * 180 / Math.PI, 1) + "°)" +
        "\nW₂² = " + fmt(w2, 4) + " (exact assignment)    SW₂²/W₂² = " + fmt(sw / w2, 3) + " ≤ 1/d = 0.5";
    }
    function setFromPointer(e) {
      var p = svgPoint(s.svg, e);
      if (p.x < PP.x - 4 || p.x > PP.x + PP.w + 4 || p.y < PP.y - 4 || p.y > PP.y + PP.h + 4) return false;
      var deg = Math.max(0, Math.min(179.5, Math.round((p.x - PP.x) / PP.w * 360) / 2));
      phiS.set(deg); draw(); return true;
    }
    var dragging = false;
    s.svg.addEventListener("pointerdown", function (e) { if (setFromPointer(e)) { dragging = true; e.preventDefault(); } });
    s.svg.addEventListener("pointermove", function (e) { if (dragging) setFromPointer(e); });
    s.svg.addEventListener("pointerup", function () { dragging = false; });
    s.svg.addEventListener("pointercancel", function () { dragging = false; });
    setup(); redrawers.push(draw);
  };

  /* --- 2. SW2 against W2 between Gaussians, as the dimension grows (§7) --- */
  WIDGETS.l5gauss = function (box) {
    var s = scaffold(box, "SW₂ and W₂ between two Gaussians as the dimension grows");
    var top = new Plot(s.svg, { x: [1, 1000], y: [1e-3, 60], xlog: true, ylog: true, w: 680, h: 260, pad: { l: 54, r: 120, t: 18, b: 34 }, label: "W2 and SW2 against the dimension, log-log" });
    var botSvg = addSvg(box, s.svg);
    var bot = new Plot(botSvg, { x: [0, 1], y: [0, 1], w: 680, h: 210, pad: { l: 54, r: 120, t: 22, b: 34 }, label: "Histogram of the per-direction costs" });
    var famSel = select(s.controls, "Pair", [["trans", "translation by a unit vector"], ["iso", "N(0, I) vs N(0, 4I)"], ["rank1", "N(0, e₁e₁ᵀ) vs N(0, e₂e₂ᵀ)"], ["stretch", "N(0, I) vs N(0, diag(4, 1, …, 1))"]], "trans", setup);
    var dS = slider(s.controls, "dimension d", 0, 3, 0.01, 1, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--muted", "W₂ (top), bound W₂/√d (dotted)"], ["--s3", "SW₂ (top); per-direction costs (bottom)"]]);
    var FAM = {
      trans: { dmin: 1, w2: function () { return 1; }, sw2: function (d) { return 1 / d; }, v: function (t) { return t[0] * t[0]; }, vmax: 1 },
      iso: { dmin: 1, w2: function (d) { return d; }, sw2: function () { return 1; }, v: function () { return 1; }, vmax: 1 },
      rank1: { dmin: 2, w2: function () { return 2; }, sw2: function (d) { return 2 * (1 - 2 / Math.PI) / d; }, v: function (t) { var a = Math.abs(t[0]) - Math.abs(t[1]); return a * a; }, vmax: 1 },
      stretch: { dmin: 1, w2: function () { return 1; }, sw2: function (d) { return l5sphereMean(function (t) { var a = Math.sqrt(1 + 3 * t * t) - 1; return a * a; }, d); }, v: function (t) { var a = Math.sqrt(1 + 3 * t[0] * t[0]) - 1; return a * a; }, vmax: 1 }
    };
    var F, grid = [], cache = {};
    function setup() {
      F = FAM[famSel.value];
      dS.input.min = Math.log10(F.dmin).toFixed(2);
      if (dS.get() < Math.log10(F.dmin)) dS.set(Math.log10(F.dmin));
      grid = [];
      for (var i = 0; i <= 60; i++) {
        var d = Math.max(F.dmin, Math.round(Math.pow(10, 3 * i / 60)));
        if (grid.length && grid[grid.length - 1][0] === d) continue;
        grid.push([d, Math.sqrt(F.w2(d)), Math.sqrt(F.sw2(d))]);
      }
      cache = {};
      draw();
    }
    function draw() {
      var d = Math.max(F.dmin, Math.round(Math.pow(10, dS.get()))), i;
      dS.out.textContent = String(d);
      var W2 = Math.sqrt(F.w2(d)), SW2sq = F.sw2(d), SW2 = Math.sqrt(SW2sq);
      top.clear();
      top.axes({ xticks: [1, 10, 100, 1000], yticks: [1e-3, 1e-2, 0.1, 1, 10], xfmt: function (t) { return String(t); }, yfmt: function (t) { return l5sup(Math.round(Math.log10(t))); }, xlabel: "dimension d" });
      top.clip();
      top.poly(grid.map(function (r) { return [r[0], r[1]]; }), "ln cm");
      top.poly(grid.map(function (r) { return [r[0], r[1] / Math.sqrt(r[0])]; }), "ln cm thin dot");
      top.poly(grid.map(function (r) { return [r[0], r[2]]; }), "ln c3");
      top.unclip();
      top.dot(d, W2, 5, "fm"); top.dot(d, SW2, 5, "f3");
      var last = grid[grid.length - 1];
      var labs = [[last[1], "W₂", "tx-b"], [last[2], "SW₂", "tx-b t3"], [last[1] / Math.sqrt(1000), "W₂/√d (dotted)", "tx-s"]].map(function (L) { return { y: top.ty(L[0]) + 4, t: L[1], c: L[2] }; });
      labs.sort(function (a, b) { return a.y - b.y; });
      for (i = 1; i < labs.length; i++) if (labs[i].y - labs[i - 1].y < 14) labs[i].y = labs[i - 1].y + 14;
      labs.forEach(function (L) { l5text(top.g, top.tx(1000) + 8, L.y, L.t, L.c, "start"); });
      // histogram of the per-direction costs at this dimension
      if (!cache[d]) {
        var rng = mulberry32(17 + d), vals = [];
        for (i = 0; i < 4000; i++) vals.push(F.v(d === 1 ? [rng() < 0.5 ? -1 : 1, 0] : l5theta12(rng, d)));
        cache[d] = vals;
      }
      var vals2 = cache[d], nb = 25, counts = [], mean = 0, small = 0;
      for (i = 0; i < nb; i++) counts.push(0);
      vals2.forEach(function (v) { counts[Math.min(nb - 1, Math.floor(v / F.vmax * nb))]++; mean += v; if (v < 0.01 * F.vmax) small++; });
      mean /= vals2.length;
      var cmax = Math.max.apply(null, counts) / vals2.length;
      bot.o.x = [0, F.vmax]; bot.o.y = [0, cmax * 1.12];
      bot.clear();
      bot.axes({ xticks: [0, 0.25, 0.5, 0.75, 1].map(function (t) { return t * F.vmax; }), yticks: [], xfmt: function (t) { return fmt(t, 2); }, nogrid: true, xlabel: "W₂² between the slices, for a random direction" });
      for (i = 0; i < nb; i++) {
        var f = counts[i] / vals2.length;
        if (f > 0) bot.poly([[i / nb * F.vmax, 0], [i / nb * F.vmax, f], [(i + 1) / nb * F.vmax, f], [(i + 1) / nb * F.vmax, 0]], "a3 ln c3 hair");
      }
      bot.seg(SW2sq, 0, SW2sq, cmax * 1.12, "ln c3 dash");
      bot.text(SW2sq, cmax * 1.12, "mean = SW₂²", "tx-s t3", SW2sq > 0.6 * F.vmax ? "end" : "start", SW2sq > 0.6 * F.vmax ? -4 : 4, 10);
      bot.text(F.vmax, cmax * 1.12, "histogram over", "tx-s", "start", 8, 10);
      bot.text(F.vmax, cmax * 1.12, "4 000 directions", "tx-s", "start", 8, 24);
      ro.textContent = "d = " + d + ":   W₂ = " + fmt(W2, 4) + "   SW₂ = " + fmt(SW2, 4) + "   SW₂/W₂ = " + fmt(SW2 / W2, 4) + "   (1/√d = " + fmt(1 / Math.sqrt(d), 4) + ")" +
        "\nmean of the sampled costs = " + fmt(mean, 4) + " (exact SW₂² = " + l5exp(SW2sq) + ");  directions seeing less than 1% of the largest possible cost: " + fmt(100 * small / vals2.length, 1) + "%";
    }
    setup(); redrawers.push(draw);
  };

  /* --- 3. Monte Carlo over directions: runs, bands, errors (§8) --- */
  WIDGETS.l5mc = function (box) {
    var s = scaffold(box, "Monte Carlo over directions: independent runs of the estimate of SW₂², and the error against K");
    var top = new Plot(s.svg, { x: [1, 4096], y: [0, 1], xlog: true, w: 680, h: 250, pad: { l: 58, r: 16, t: 18, b: 34 }, label: "Running estimates of SW2 squared against the number of directions" });
    var botSvg = addSvg(box, s.svg);
    var bot = new Plot(botSvg, { x: [1, 4096], y: [1e-6, 1], xlog: true, ylog: true, w: 680, h: 230, pad: { l: 58, r: 16, t: 18, b: 34 }, label: "Mean absolute error against the number of directions, log-log" });
    var pairSel = select(s.controls, "Pair", [["cross", "the cross (d = 2)"], ["cw", "two diagonals (d = 2)"], ["gauss", "N(0, I) vs N(e₁, diag(4, 1, …, 1))"]], "cross", setup);
    var dSel = select(s.controls, "dimension d", [["2", "2"], ["5", "5"], ["10", "10"], ["20", "20"], ["50", "50"], ["100", "100"]], "10", setup);
    var kS = slider(s.controls, "read at K =", 0, 12, 1, 6, draw);
    button(s.controls, "New runs", function () { seed++; simulate(); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--muted", "runs (grey); Var/K, as printed on the slide (dashed)"], ["--s3", "exact value and ±√(Var/K)"], ["--s2", "measured mean |error|"]]);
    var seed = 1, P, runs = 40, KMAX = 4096, Ks = [], paths = [], mae = [];
    (function () { var last = 0; for (var j = 0; j <= 96; j++) { var K = Math.round(Math.pow(2, j / 8)); if (K !== last) { Ks.push(K); last = K; } } })();
    function gaussF(t) { var a = Math.sqrt(1 + 3 * t * t) - 1; return t * t + a * a; }
    function setup() {
      var key = pairSel.value, d = parseInt(dSel.value, 10);
      dSel.parentNode.style.display = key === "gauss" ? "" : "none";
      if (key === "cross") P = { mean: 1 - 2 / Math.PI, vr: 0.5 - 4 / (Math.PI * Math.PI), draw: function (rng) { var a = 2 * Math.PI * rng(); return 1 - Math.abs(Math.sin(2 * a)); } };
      else if (key === "cw") P = { mean: 0.5 - 1 / Math.PI, vr: (0.5 - 4 / (Math.PI * Math.PI)) / 4, draw: function (rng) { var a = 2 * Math.PI * rng(), c = Math.cos(a), sn = Math.sin(a); return Math.min(c * c, sn * sn); } };
      else {
        var m = l5sphereMean(gaussF, d), m2 = l5sphereMean(function (t) { var v = gaussF(t); return v * v; }, d);
        P = { mean: m, vr: m2 - m * m, draw: function (rng) { return gaussF(l5theta1(rng, d)); } };
      }
      simulate(); draw();
    }
    function simulate() {
      var rng = mulberry32(4242 + 101 * seed), r, k, j;
      paths = []; mae = [];
      for (k = 0; k <= 12; k++) mae.push(0);
      for (r = 0; r < runs; r++) {
        var sum = 0, path = [], jj = 0;
        for (k = 1; k <= KMAX; k++) {
          sum += P.draw(rng);
          if (k === Ks[jj]) { path.push([k, sum / k]); jj++; }
          var lk = Math.log2(k);
          if (Math.abs(lk - Math.round(lk)) < 1e-9) mae[Math.round(lk)] += Math.abs(sum / k - P.mean) / runs;
        }
        paths.push(path);
      }
    }
    function draw() {
      var kk = Math.round(kS.get()), K = Math.pow(2, kk), sd = Math.sqrt(P.vr), j;
      kS.out.textContent = String(K);
      var lo = Math.max(0, P.mean - 2.4 * sd), hi = P.mean + 2.4 * sd;
      top.o.y = [lo, hi];
      top.clear();
      var yt = l5niceTicks(lo, hi);
      top.axes({ xticks: [1, 4, 16, 64, 256, 1024, 4096], yticks: yt, xfmt: function (t) { return String(t); }, yfmt: function (t) { return fmt(t, yt.length > 1 && yt[1] - yt[0] < 0.1 ? 2 : 1); }, xlabel: "number of directions K" });
      top.clip();
      var up = [], dn = [], up2 = [], dn2 = [];
      Ks.forEach(function (k) { up.push([k, P.mean + sd / Math.sqrt(k)]); dn.push([k, P.mean - sd / Math.sqrt(k)]); up2.push([k, P.mean + P.vr / k]); dn2.push([k, P.mean - P.vr / k]); });
      top.poly(up.concat(dn.slice().reverse()), "a3");
      paths.forEach(function (p) { top.poly(p, "ln cm hair", { "stroke-opacity": 0.55 }); });
      top.poly(up2, "ln cm dash"); top.poly(dn2, "ln cm dash");
      top.poly([[1, P.mean], [KMAX, P.mean]], "ln c3");
      top.poly([[K, lo], [K, hi]], "ln c2 hair");
      top.unclip();
      top.text(KMAX, P.mean, "SW₂² = " + fmt(P.mean, 4), "tx-s t3", "end", -4, -6);
      // errors
      bot.clear();
      bot.axes({ xticks: [1, 4, 16, 64, 256, 1024, 4096], yticks: [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 0.1, 1], xfmt: function (t) { return String(t); }, yfmt: function (t) { return l5sup(Math.round(Math.log10(t))); }, xlabel: "number of directions K" });
      bot.clip();
      bot.fn(function (k) { return Math.sqrt(P.vr / k); }, "ln c3", 100);
      bot.fn(function (k) { return P.vr / k; }, "ln cm dash", 100);
      var pts = mae.map(function (v, k) { return [Math.pow(2, k), v]; });
      bot.poly(pts, "ln c2 thin");
      bot.unclip();
      pts.forEach(function (p) { bot.dot(p[0], p[1], 3.5, "f2"); });
      bot.dot(K, mae[kk], 6, "ln c2 nofill");
      bot.text(4096, Math.sqrt(P.vr / 4096), "√(Var/K)", "tx-s t3", "end", -2, -8);
      var K0 = P.vr / 64 >= 5e-6 ? 64 : 16;   // label below the dashed line, ending at K0
      bot.text(K0, P.vr / K0, "Var/K, as on the slide", "tx-s", "end", -2, 14);
      ro.textContent = "K = " + K + ":   mean |error| over " + runs + " runs = " + l5exp(mae[kk]) + "    √(Var/K) = " + l5exp(Math.sqrt(P.vr / K)) + "    Var/K (slide 12/12) = " + l5exp(P.vr / K) +
        "\nexact SW₂² = " + fmt(P.mean, 4) + ",  Var of the cost of one random direction = " + l5exp(P.vr) + ",  ratio mean|error| / √(Var/K) = " + fmt(mae[kk] / Math.sqrt(P.vr / K), 2) + "  (√(2/π) ≈ 0.80)";
    }
    setup(); redrawers.push(draw);
  };

  /* --- 4. Iterated sliced matching: the sliced flow and IDT (§11) --- */
  WIDGETS.l5flow = function (box) {
    var s = scaffold(box, "Iterated sliced matching: sort along random directions, move each point to its partner");
    var W = 680, H = 420, n = 60;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "A moving point cloud, a target cloud, the paths of the points and the decrease of the sliced and Wasserstein distances");
    var dataSel = select(s.controls, "Clouds", [["ring", "blob → ring"], ["crescent", "two clusters → crescent"]], "ring", reset);
    var modeSel = select(s.controls, "Each step", [["rand", "16 random directions"], ["idt", "2 orthogonal directions (IDT)"]], "rand", function () { tauS.set(modeSel.value === "idt" ? 1 : 0.3); tauS.out.textContent = fmt(tauS.get(), 2); });
    var tauS = slider(s.controls, "step τ", 0.05, 1, 0.05, 0.3, function () { tauS.out.textContent = fmt(tauS.get(), 2); });
    tauS.out.textContent = "0.30";
    button(s.controls, "Step", function () { if (!busy) { doStep(); draw(); } });
    button(s.controls, "Run 40 steps", function () { if (!busy) run(40); });
    button(s.controls, "Reset", reset);
    var pathChk = checkbox(s.controls, "show paths", true, function () { draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "starting positions"], ["--s1", "target"], ["--s3", "moving cloud and its paths; SW₂² (right)"], ["--muted", "exact W₂² to the target (right)"]]);
    var X, X0, Y, paths, hist, ell, busy = false, rng, sig0, w0;
    var MP = { x: 8, y: 8, w: 450, h: 404, xr: [-2.5, 2.9] };
    MP.k = MP.w / (MP.xr[1] - MP.xr[0]);
    function MX(x) { return MP.x + (x - MP.xr[0]) * MP.k; }
    function MY(y) { return MP.y + MP.h / 2 - y * MP.k; }
    function makeData() {
      var r0 = mulberry32(dataSel.value === "ring" ? 21 : 33), i, a, r;
      X = []; Y = [];
      if (dataSel.value === "ring") {
        for (i = 0; i < n; i++) X.push([-0.55 + 0.3 * gaussRand(r0), 0.15 + 0.45 * gaussRand(r0)]);
        for (i = 0; i < n; i++) { a = 2 * Math.PI * r0(); r = 1.45 + 0.06 * gaussRand(r0); Y.push([0.25 + r * Math.cos(a), r * Math.sin(a)]); }
      } else {
        for (i = 0; i < n; i++) X.push(i < n / 2 ? [-1.6 + 0.25 * gaussRand(r0), 1.0 + 0.25 * gaussRand(r0)] : [-1.3 + 0.25 * gaussRand(r0), -1.1 + 0.25 * gaussRand(r0)]);
        for (i = 0; i < n; i++) { a = -Math.PI / 2 + Math.PI * r0(); r = 1.5 + 0.08 * gaussRand(r0); Y.push([0.6 + r * Math.cos(a), r * Math.sin(a)]); }
      }
    }
    function sw2quad(P, Q) { var sum = 0, M = 90; for (var k = 0; k < M; k++) { var ph = (k + 0.5) * Math.PI / M; sum += l5w22sorted(l5proj(P, [Math.cos(ph), Math.sin(ph)]), l5proj(Q, [Math.cos(ph), Math.sin(ph)])); } return sum / M; }
    function reset() {
      if (busy) { pendingReset = true; return; }
      makeData();
      X0 = X.map(function (p) { return p.slice(); });
      var e = l5w22exact(X, Y); sig0 = e.asg; w0 = e.cost;
      paths = X.map(function (p) { return [p.slice()]; });
      ell = 0; rng = mulberry32(3);
      hist = [[sw2quad(X, Y), w0]];
      draw();
    }
    var pendingReset = false;
    function doStep() {
      var dirs = [], k, i;
      if (modeSel.value === "idt") { var a = Math.PI * rng(); dirs = [[Math.cos(a), Math.sin(a)], [-Math.sin(a), Math.cos(a)]]; }
      else for (k = 0; k < 16; k++) { var b = 2 * Math.PI * rng(); dirs.push([Math.cos(b), Math.sin(b)]); }
      var V = X.map(function () { return [0, 0]; }), tau = tauS.get(), fac = tau * 2 / dirs.length;
      dirs.forEach(function (th) {
        var px = l5proj(X, th), py = l5proj(Y, th), ix = l5argsort(px), iy = l5argsort(py);
        for (var r = 0; r < n; r++) { var i0 = ix[r], dlt = py[iy[r]] - px[i0]; V[i0][0] += dlt * th[0]; V[i0][1] += dlt * th[1]; }
      });
      for (i = 0; i < n; i++) { X[i][0] += fac * V[i][0]; X[i][1] += fac * V[i][1]; paths[i].push(X[i].slice()); }
      ell++;
      hist.push([sw2quad(X, Y), l5w22exact(X, Y).cost]);
    }
    function run(m) {
      busy = true;
      var left = m;
      function tick() {
        if (pendingReset) { busy = false; pendingReset = false; reset(); return; }
        doStep(); draw(); left--;
        if (left > 0) setTimeout(tick, 60); else busy = false;
      }
      tick();
    }
    function draw() {
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg), i;
      el("rect", { x: MP.x, y: MP.y, width: MP.w, height: MP.h, "class": "ln cm hair nofill" }, g);
      Y.forEach(function (p) { el("circle", { cx: MX(p[0]), cy: MY(p[1]), r: 3, "class": "f1" }, g); });
      if (pathChk.checked) paths.forEach(function (pp) {
        el("path", { d: pp.map(function (p, j) { return (j ? "L" : "M") + MX(p[0]).toFixed(1) + " " + MY(p[1]).toFixed(1); }).join(""), "class": "ln c3 hair", "stroke-opacity": 0.6 }, g);
      });
      X0.forEach(function (p) { el("circle", { cx: MX(p[0]), cy: MY(p[1]), r: 2.4, "class": "f2", "fill-opacity": 0.55 }, g); });
      X.forEach(function (p) { el("circle", { cx: MX(p[0]), cy: MY(p[1]), r: 3.4, "class": "f3" }, g); });
      // distances against the iterations (log scale)
      var cx0 = 500, cy0 = 50, cw = 160, ch = 170, lo = -8, hi = 1, m = Math.max(hist.length - 1, 10);
      function CX(j) { return cx0 + j / m * cw; }
      function CY(v) { return cy0 + ch - (Math.max(lo, Math.min(hi, Math.log10(Math.max(v, 1e-12)))) - lo) / (hi - lo) * ch; }
      el("rect", { x: cx0, y: cy0, width: cw, height: ch, "class": "ln cm hair nofill" }, g);
      [0, -2, -4, -6, -8].forEach(function (e) {
        el("line", { x1: cx0, x2: cx0 + cw, y1: CY(Math.pow(10, e)), y2: CY(Math.pow(10, e)), "class": "gr" }, g);
        l5text(g, cx0 - 4, CY(Math.pow(10, e)) + 4, l5sup(e), "tx-s", "end");
      });
      l5text(g, cx0, cy0 - 10, "SW₂² and W₂² to the target", "tx-s");
      l5text(g, cx0 + cw, cy0 + ch + 14, "iteration " + m, "tx-s", "end");
      [[1, "ln cm"], [0, "ln c3"]].forEach(function (c) {
        el("path", { d: hist.map(function (h, j) { return (j ? "L" : "M") + CX(j).toFixed(1) + " " + CY(h[c[0]]).toFixed(1); }).join(""), "class": c[1] }, g);
      });
      var cur = hist[hist.length - 1];
      var msg = "ℓ = " + ell + "    SW₂² ≈ " + l5exp(cur[0]) + "    W₂² to the target = " + l5exp(cur[1]) + "    (start: W₂² = " + fmt(w0, 4) + ")";
      if (cur[1] < 1e-9 && ell > 0) {
        var agree = 0, cost = 0, used = {}, distinct = 0;
        for (i = 0; i < n; i++) {
          var best = 0, bd = Infinity;
          for (var j = 0; j < n; j++) { var dx = X[i][0] - Y[j][0], dy = X[i][1] - Y[j][1], dd = dx * dx + dy * dy; if (dd < bd) { bd = dd; best = j; } }
          if (best === sig0[i]) agree++;
          if (!used[best]) { used[best] = 1; distinct++; }
          cost += Math.pow(X0[i][0] - Y[best][0], 2) + Math.pow(X0[i][1] - Y[best][1], 2);
        }
        msg += "\nEvery point sits on a target point. The matching found by the flow agrees with the optimal assignment for " + agree + " of the " + n + " points" +
          (distinct === n ? " and costs " + fmt(cost / n, 4) + " (optimal: " + fmt(w0, 4) + ")." : ".");
      } else msg += "\nPress Step or Run. The cost of the optimal assignment from the start is " + fmt(w0, 4) + ".";
      ro.textContent = msg;
    }
    reset(); redrawers.push(draw);
  };
