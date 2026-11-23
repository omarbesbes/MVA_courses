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
      P.text(3, 5, "conditional energy", "tx-s", "start", 4, 12);
      pts.forEach(function (p) { P.dot(p[0], p[1], 2.6, "f1"); });
      var n = nd.get(), f = fr.get(), k = kk.get(), lf = Math.log10(f * TOK);
      for (var j = 0; j < n; j++) {
        var y = 1.1 + 0.15 * j;
        P.dot(lf + 0.04 * (j - 1), y, 6, "f2");
        P.text(lf + 0.04 * (j - 1), y, String(j + 1), "tx-b", "middle", 0, -10);
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
    var al = slider(s.controls, "anisotropy", 0, 2, 0.05, 1.2, draw);
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
      P.seg(0, lvl, D + 1, lvl, "ln dash");
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
