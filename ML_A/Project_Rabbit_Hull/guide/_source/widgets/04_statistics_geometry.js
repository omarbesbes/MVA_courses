// widgets/04_statistics_geometry.js — interactive figures of page 4. Own helpers are prefixed "p4".

  /* --- 1. p4energy: simulated concepts, frequency vs conditional energy, with dense outliers --- */
  WIDGETS.p4energy = function (box) {
    var s = scaffold(box, "Frequency against conditional energy for 600 simulated concepts, plus dense concepts");
    var N = 600, TOK = 3.654e8;
    var P = new Plot(s.svg, { x: [3, 9], y: [0, 5], w: 680, h: 340, pad: { l: 46, r: 16, t: 20, b: 44 }, label: "Scatter of conditional energy against log10 of the number of firings" });
    var rnd = mulberry32(11), pts = [];
    for (var i = 0; i < N; i++) {
      var lf = 3.2 + rnd() * 3.5;            // log10 of firing count, 1.6e3 .. 5e6
      var emax = 5.2 - 0.62 * (lf - 3.2);       // envelope: top edge decreases with count
      var emin = 0.3 + 0.1 * (lf - 3.2);
      pts.push([lf, emin + (emax - emin) * Math.pow(rnd(), 1.3)]);
    }
    var nd = slider(s.controls, "dense concepts", 0, 3, 1, 3, draw);
    var fr = slider(s.controls, "fraction of tokens", 0.05, 0.45, 0.01, 0.29, draw);
    var kk = slider(s.controls, "k", 4, 32, 1, 8, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "selective concepts (toy)"], ["--s2", "dense concepts"]]);
    function draw() {
      P.clear();
      for (var v = 0; v <= 5; v++) { P.seg(3, v, 9, v, v === 0 ? "ax" : "gr"); P.text(3, v, String(v), "tx-s", "end", -6, 4); }
      for (var e = 3; e <= 9; e++) { P.seg(e, 0, e, 5, "gr"); P.text(e, 0, "10" + "⁰¹²³⁴⁵⁶⁷⁸⁹"[e], "tx-s", "middle", 0, 16); }
      P.text(9, 0, "number of firings (tokens)", "tx-s", "end", 0, 34);
      P.text(3, 5, "conditional energy E[Zᵢ | Zᵢ > 0]", "tx-s", "start", 0, -6);
      pts.forEach(function (p) { P.dot(p[0], p[1], 2.6, "f1"); });
      var n = nd.get(), f = fr.get(), k = kk.get(), lf = Math.log10(f * TOK);
      for (var j = 0; j < n; j++) {
        var y = 1.0 + 0.3 * j, xx = lf + 0.22 * (j - 1);
        P.dot(xx, y, 6, "f2");
        P.text(xx, y, String(j + 1), "tx-b", "middle", 0, -11);
      }
      nd.out.textContent = n; fr.out.textContent = fmt(f, 2); kk.out.textContent = k;
      ro.textContent = "each dense concept fires about " + fmt(f * TOK / 1e8, 2) + "e8 times (" + fmt(100 * f, 0) + "% of 3.65e8 tokens)\n" +
        "slots taken per token: " + fmt(n * f, 2) + " of " + k + "   →   share of all activations: " + fmt(100 * n * f / k, 1) + "%";
    }
    draw(); redrawers.push(draw);
  };

  /* --- 2. p4spectrum: singular values of a c x d unit-row dictionary vs anisotropy --- */
  function p4jacobiEig(S, n) { // symmetric matrix (array of rows) -> eigenvalues, cyclic Jacobi
    var a = S.map(function (r) { return r.slice(); });
    for (var sweep = 0; sweep < 12; sweep++) {
      var off = 0;
      for (var p = 0; p < n; p++) for (var q = p + 1; q < n; q++) off += a[p][q] * a[p][q];
      if (off < 1e-14) break;
      for (var p2 = 0; p2 < n - 1; p2++) for (var q2 = p2 + 1; q2 < n; q2++) {
        var apq = a[p2][q2]; if (Math.abs(apq) < 1e-15) continue;
        var th = (a[q2][q2] - a[p2][p2]) / (2 * apq);
        var t = (th >= 0 ? 1 : -1) / (Math.abs(th) + Math.sqrt(th * th + 1));
        var c = 1 / Math.sqrt(t * t + 1), s = t * c;
        for (var k = 0; k < n; k++) { var akp = a[k][p2], akq = a[k][q2]; a[k][p2] = c * akp - s * akq; a[k][q2] = s * akp + c * akq; }
        for (var k2 = 0; k2 < n; k2++) { var apk = a[p2][k2], aqk = a[q2][k2]; a[p2][k2] = c * apk - s * aqk; a[q2][k2] = s * apk + c * aqk; }
      }
    }
    return a.map(function (r, i) { return r[i]; });
  }
  WIDGETS.p4spectrum = function (box) {
    var s = scaffold(box, "Singular values of a dictionary of c = 160 unit atoms in d = 32 dimensions");
    var C = 160, D = 32;
    var P = new Plot(s.svg, { x: [0, D + 1], y: [0, 6], w: 680, h: 340, pad: { l: 46, r: 16, t: 20, b: 44 }, label: "Singular values of the dictionary against their index, with the tight-frame level and the Marchenko-Pastur band" });
    var rnd = mulberry32(5), G = [];
    for (var i = 0; i < C; i++) { var r = []; for (var j = 0; j < D; j++) r.push(gaussRand(rnd)); G.push(r); }
    var al = slider(s.controls, "anisotropy", 0, 2, 0.05, 0.8, draw);
    button(s.controls, "Uniform", function () { al.set(0); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "singular values of D"], ["--text-2", "tight-frame level √(c/d)"], ["--s1", "Marchenko–Pastur band"]]);
    function draw() {
      var a = al.get(), M = [];
      for (var i = 0; i < C; i++) {
        var row = G[i].map(function (g, j) { return g * Math.pow(j + 1, -a / 2); });
        var nrm = Math.sqrt(row.reduce(function (u, v) { return u + v * v; }, 0));
        M.push(row.map(function (v) { return v / nrm; }));
      }
      var S = [];
      for (var p = 0; p < D; p++) { S.push(new Array(D).fill(0)); }
      M.forEach(function (row) { for (var p2 = 0; p2 < D; p2++) for (var q = p2; q < D; q++) { S[p2][q] += row[p2] * row[q]; } });
      for (var p3 = 0; p3 < D; p3++) for (var q3 = 0; q3 < p3; q3++) S[p3][q3] = S[q3][p3];
      var ev = p4jacobiEig(S, D).map(function (v) { return Math.sqrt(Math.max(v, 0)); }).sort(function (u, v) { return v - u; });
      var lvl = Math.sqrt(C / D), lo = lvl * (1 - Math.sqrt(D / C)), hi = lvl * (1 + Math.sqrt(D / C));
      P.clear();
      for (var v = 0; v <= 6; v++) { P.seg(0, v, D + 1, v, v === 0 ? "ax" : "gr"); P.text(0, v, String(v), "tx-s", "end", -6, 4); }
      P.poly([[0, lo], [D + 1, lo], [D + 1, hi], [0, hi]], "a1");
      P.seg(0, lvl, D + 1, lvl, "ln c6 dash", ' style="stroke-width:2.2"');
      P.text(D + 1, lvl, "√(c/d) = " + fmt(lvl, 2), "tx-s", "end", -4, -6);
      P.poly(ev.map(function (v, i) { return [i + 1, v]; }), "ln c2");
      ev.forEach(function (v, i) { P.dot(i + 1, v, 3, "f2"); });
      P.text(D + 1, 0, "index of the singular value", "tx-s", "end", 0, 34);
      var ss = ev.reduce(function (u, v) { return u + v * v; }, 0);
      al.out.textContent = fmt(a, 2);
      ro.textContent = "σ₁ = " + fmt(ev[0], 2) + "   σ_d = " + fmt(ev[D - 1], 2) + "   band = [" + fmt(lo, 2) + ", " + fmt(hi, 2) + "]\n" +
        "Σσ² = " + fmt(ss, 1) + " (= c = " + C + ")   σ₁²/(c/d) = " + fmt(ev[0] * ev[0] / (C / D), 2);
    }
    draw(); redrawers.push(draw);
  };

  /* --- 3. p4antipodal: a signed feature carried by non-negative codes on two atoms --- */
  WIDGETS.p4antipodal = function (box) {
    var s = scaffold(box, "Reconstructing x·u with non-negative codes on two atoms");
    var P = new Plot(s.svg, { x: [-3.4, 3.4], y: [-2.2, 2.2], w: 680, h: 340, pad: { l: 20, r: 20, t: 20, b: 20 }, label: "Plane with two atoms from the origin, the target point and its non-negative reconstruction" });
    var xs = slider(s.controls, "signed feature x", -3, 3, 0.1, -1.5, draw);
    var an = slider(s.controls, "angle between atoms (°)", 60, 180, 5, 180, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "atoms D₁, D₂"], ["--s3", "target x·u"], ["--s2", "reconstruction z₁D₁ + z₂D₂"]]);
    function draw() {
      var x = xs.get(), ph = an.get() * Math.PI / 180;
      var d1 = [1, 0], d2 = [Math.cos(ph), Math.sin(ph)], t = [x, 0];
      var sol = [[0, 0]];  // candidates: z=(0,0), single atoms, both atoms
      var z1 = Math.max(0, t[0] * d1[0] + t[1] * d1[1]), z2 = Math.max(0, t[0] * d2[0] + t[1] * d2[1]);
      var cands = [[0, 0], [z1, 0], [0, z2]];
      var det = d1[0] * d2[1] - d1[1] * d2[0];
      if (Math.abs(det) > 1e-9) {
        var a = (t[0] * d2[1] - t[1] * d2[0]) / det, b = (d1[0] * t[1] - d1[1] * t[0]) / det;
        if (a >= 0 && b >= 0) cands.push([a, b]);
      }
      var best = null, be = 1e9;
      cands.forEach(function (c) {
        var r = [c[0] * d1[0] + c[1] * d2[0], c[0] * d1[1] + c[1] * d2[1]];
        var e = Math.hypot(r[0] - t[0], r[1] - t[1]);
        if (e < be - 1e-9) { be = e; best = { z: c, r: r }; }
      });
      P.clear();
      P.seg(-3.4, 0, 3.4, 0, "ax"); P.seg(0, -2.2, 0, 2.2, "ax");
      var a1 = [3.2 * d1[0], 3.2 * d1[1]], a2 = [3.2 * d2[0], 3.2 * d2[1]];
      P.seg(0, 0, a1[0], a1[1], "ln c1", ' style="stroke-width:2.5"');
      P.seg(0, 0, a2[0], a2[1], "ln c1", ' style="stroke-width:2.5"');
      P.text(a1[0], a1[1], "D₁", "tx-b", "end", -4, -8);
      P.text(a2[0], a2[1], "D₂", "tx-b", ph > 3.0 ? "start" : "end", ph > 3.0 ? 4 : -4, -8);
      P.dot(t[0], t[1], 6, "f3"); P.text(t[0], t[1], "x·u", "tx", "middle", 0, 20);
      P.dot(best.r[0], best.r[1], 4, "f2");
      xs.out.textContent = fmt(x, 1); an.out.textContent = fmt(an.get(), 0) + "°";
      ro.textContent = "codes z = (" + fmt(best.z[0], 2) + ", " + fmt(best.z[1], 2) + ")  all ≥ 0\n" +
        "error = " + fmt(be, 2) + "     cos(D₁, D₂) = " + fmt(Math.cos(ph), 2) + "     |⟨D₁, D₂⟩| = " + fmt(Math.abs(Math.cos(ph)), 2);
    }
    draw(); redrawers.push(draw);
  };

  /* --- 4. p4position: a 16x16 position basis morphing from a place code to a two-axis code --- */
  WIDGETS.p4position = function (box) {
    var s = scaffold(box, "Position code of a 16×16 grid: from one direction per position to two coordinate axes");
    var P = new Plot(s.svg, { x: [-1.15, 1.15], y: [-1.15, 1.15], w: 420, h: 420, pad: { l: 10, r: 10, t: 10, b: 10 }, label: "Two coordinates of the 256 position vectors, coloured by grid position" });
    var n = 16, N = 256, W = 40;   // W: squared norm of each axis column relative to the place code
    var rnd = mulberry32(21), g1 = [], g2 = [];
    for (var i = 0; i < N; i++) { g1.push(gaussRand(rnd)); g2.push(gaussRand(rnd)); }
    var m = slider(s.controls, "axis-code share", 0, 1, 0.01, 0.0, draw);
    button(s.controls, "Place code", function () { m.set(0); draw(); });
    button(s.controls, "Axis code", function () { m.set(1); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "position vectors (colour = grid position)"]]);
    function draw() {
      var a = m.get();
      // P = [(1-a) I | a sqrt(W) (row ramp, column ramp)] ; centred; eigenvalues: 2 x ((1-a)^2 + a^2 W), 253 x (1-a)^2
      var lr = (1 - a) * (1 - a) + a * a * W, lo = (1 - a) * (1 - a);
      var tot = 253 * lo + 2 * lr, top = Math.max(lr, lo);
      var sr = tot / top, r2 = 2 * top / tot;
      P.clear();
      P.seg(-1.15, 0, 1.15, 0, "gr"); P.seg(0, -1.15, 0, 1.15, "gr");
      var sc = 1.0 / Math.sqrt(lr + 1e-9);
      for (var i = 0; i < n; i++) for (var j = 0; j < n; j++) {
        var p = i * n + j, ri = (i - 7.5) / 7.5, cj = (j - 7.5) / 7.5;
        var x = (a * Math.sqrt(W) * cj * 0.9 + (1 - a) * g1[p] * 0.35) * sc;
        var y = (a * Math.sqrt(W) * ri * 0.9 + (1 - a) * g2[p] * 0.35) * sc;
        var col = "rgb(" + Math.round(255 * (1 - j / 15)) + "," + Math.round(200 * i / 15) + "," + Math.round(255 * (j / 15)) + ")";
        el("circle", { cx: P.tx(x), cy: P.ty(-y), r: 4.2, fill: col, stroke: "none" }, P.g);
      }
      m.out.textContent = fmt(a, 2);
      ro.textContent = "stable rank = " + fmt(sr, 1) + "    R² of the top-2 components = " + fmt(r2, 3) + "\n" +
        (a < 0.05 ? "place code: 255 equal directions, nothing to compress" : a > 0.95 ? "axis code: two coordinates, a flat sheet" : "mixture: two strong directions above 253 weak ones");
    }
    draw(); redrawers.push(draw);
  };
