// widgets/Lesson07.js — interactive figures of Lesson 7 (entropic regularization and Sinkhorn's algorithm).
// Inserted by build.mjs inside the scope of app.js: it uses el, fmt, Plot, scaffold, slider, select, button, checkbox,
// readout, legend, addSvg, svgPoint, mulberry32, gaussRand and redrawers, and registers its widgets in WIDGETS.
// Every helper defined here is prefixed with l7.

  /* ---------------- shared helpers of the page ---------------- */
  // the 1D histograms of the page (same formulas as figures_L07.py): N cells of [0,1], two pairs
  function l7hist(pair, N) {
    var t = [], a = [], b = [], i, sa = 0, sb = 0;
    function bump(x, m, s) { return Math.exp(-(x - m) * (x - m) / (2 * s * s)); }
    for (i = 0; i < N; i++) {
      var x = (i + 0.5) / N; t.push(x);
      if (pair === "shift") { a.push(bump(x, 0.3, 0.08)); b.push(bump(x, 0.7, 0.08)); }
      else { a.push(0.6 * bump(x, 0.22, 0.06) + 0.4 * bump(x, 0.55, 0.05)); b.push(bump(x, 0.7, 0.09)); }
    }
    var ma = Math.max.apply(null, a), mb = Math.max.apply(null, b);
    for (i = 0; i < N; i++) { a[i] += 0.01 * ma; b[i] += 0.01 * mb; sa += a[i]; sb += b[i]; }
    for (i = 0; i < N; i++) { a[i] /= sa; b[i] /= sb; }
    return { t: t, a: a, b: b };
  }
  function l7cost(xs, ys) {
    return xs.map(function (x) { return ys.map(function (y) { return (x - y) * (x - y); }); });
  }
  // log-domain Sinkhorn for min <C,P> + eps KL(P | a x b); iters full cycles; returns potentials, plan, row errors
  function l7sinkhorn(a, b, C, eps, iters, opt) {
    opt = opt || {};
    var n = a.length, m = b.length, i, j, it;
    var la = a.map(Math.log), lb = b.map(Math.log);
    var f = opt.f ? opt.f.slice() : new Array(n).fill(0), g = opt.g ? opt.g.slice() : new Array(m).fill(0);
    var errs = [], tol = opt.tol || 0, row = new Float64Array(m), col = new Float64Array(n);
    function err() {
      var e = 0;
      for (i = 0; i < n; i++) {
        var s = 0;
        for (j = 0; j < m; j++) s += Math.exp(la[i] + lb[j] + (f[i] + g[j] - C[i][j]) / eps);
        e += Math.abs(s - a[i]);
      }
      return e;
    }
    for (it = 1; it <= iters; it++) {
      for (i = 0; i < n; i++) {
        var mx = -Infinity;
        for (j = 0; j < m; j++) { row[j] = lb[j] + (g[j] - C[i][j]) / eps; if (row[j] > mx) mx = row[j]; }
        var s = 0; for (j = 0; j < m; j++) s += Math.exp(row[j] - mx);
        f[i] = -eps * (mx + Math.log(s));
      }
      for (j = 0; j < m; j++) {
        var mx2 = -Infinity;
        for (i = 0; i < n; i++) { col[i] = la[i] + (f[i] - C[i][j]) / eps; if (col[i] > mx2) mx2 = col[i]; }
        var s2 = 0; for (i = 0; i < n; i++) s2 += Math.exp(col[i] - mx2);
        g[j] = -eps * (mx2 + Math.log(s2));
      }
      if (opt.record || tol > 0) {
        var e = err(); if (opt.record) errs.push(e);
        if (tol > 0 && e < tol) break;
      }
    }
    var P = [];
    for (i = 0; i < n; i++) { P.push([]); for (j = 0; j < m; j++) P[i].push(Math.exp(la[i] + lb[j] + (f[i] + g[j] - C[i][j]) / eps)); }
    return { f: f, g: g, P: P, errs: errs, iters: Math.min(it, iters) };
  }
  function l7monotone(a, b) { // north-west corner rule on sorted points
    var n = a.length, m = b.length, P = [], i, j, ra = a.slice(), rb = b.slice();
    for (i = 0; i < n; i++) P.push(new Array(m).fill(0));
    i = 0; j = 0;
    while (i < n && j < m) { var t = Math.min(ra[i], rb[j]); P[i][j] += t; ra[i] -= t; rb[j] -= t; if (ra[i] <= 1e-15) i++; else j++; }
    return P;
  }
  function l7planStats(P, a, b, C) {
    var cost = 0, kl = 0, i, j;
    for (i = 0; i < P.length; i++) for (j = 0; j < P[i].length; j++) {
      cost += P[i][j] * C[i][j];
      if (P[i][j] > 0) kl += P[i][j] * Math.log(P[i][j] / (a[i] * b[j]));
    }
    var tot = 0; for (i = 0; i < P.length; i++) for (j = 0; j < P[i].length; j++) tot += P[i][j];
    return { cost: cost, kl: kl - tot + 1 };
  }
  // heat map of a matrix (rows top to bottom), runs of equal opacity level merged; gamma < 1 brightens small values
  function l7heat(g, M, x0, y0, w, h, cls, gamma, levels) {
    var n = M.length, m = M[0].length, mx = 0, i, j;
    for (i = 0; i < n; i++) for (j = 0; j < m; j++) if (M[i][j] > mx) mx = M[i][j];
    var cw = w / m, ch = h / n;
    levels = levels || 14;
    for (i = 0; i < n; i++) {
      j = 0;
      while (j < m) {
        var L = Math.round(Math.pow(M[i][j] / mx, gamma) * levels), k = j;
        while (k + 1 < m && Math.round(Math.pow(M[i][k + 1] / mx, gamma) * levels) === L) k++;
        if (L > 0) el("rect", { x: (x0 + j * cw).toFixed(2), y: (y0 + i * ch).toFixed(2), width: ((k - j + 1) * cw + 0.2).toFixed(2), height: (ch + 0.2).toFixed(2), "class": cls, "fill-opacity": (L / levels).toFixed(2) }, g);
        j = k + 1;
      }
    }
    el("rect", { x: x0, y: y0, width: w, height: h, "class": "ln cm hair nofill" }, g);
  }
  // second singular value of diag(a)^-1/2 P diag(b)^-1/2 (power iteration orthogonal to sqrt(b))
  function l7sigma2(P, a, b) {
    var n = a.length, m = b.length, i, j, it;
    var A = []; for (i = 0; i < n; i++) { A.push([]); for (j = 0; j < m; j++) A[i].push(P[i][j] / Math.sqrt(a[i] * b[j])); }
    var sb = b.map(Math.sqrt), x = [], rng = mulberry32(7);
    for (j = 0; j < m; j++) x.push(rng() - 0.5);
    function proj(v) { var d = 0, k; for (k = 0; k < m; k++) d += v[k] * sb[k]; for (k = 0; k < m; k++) v[k] -= d * sb[k]; return v; }
    function norm(v) { var s = 0, k; for (k = 0; k < v.length; k++) s += v[k] * v[k]; return Math.sqrt(s); }
    x = proj(x); var nx = norm(x); x = x.map(function (v) { return v / nx; });
    var lam = 0;
    for (it = 0; it < 4000; it++) {
      var y = new Array(n).fill(0), z = new Array(m).fill(0);
      for (i = 0; i < n; i++) for (j = 0; j < m; j++) y[i] += A[i][j] * x[j];
      for (j = 0; j < m; j++) for (i = 0; i < n; i++) z[j] += A[i][j] * y[i];
      z = proj(z); var nz = norm(z);
      if (nz === 0) return 0;
      var lnew = nz; x = z.map(function (v) { return v / nz; });
      if (Math.abs(lnew - lam) < 1e-13 * lnew && it > 20) { lam = lnew; break; }
      lam = lnew;
    }
    return Math.sqrt(lam); // lam = sigma_2^2
  }
  function l7exp(e) { // 1e-5 style
    if (!isFinite(e)) return String(e);
    if (e === 0) return "0";
    var s = e.toExponential(1).replace("e-", "e−").replace("e+", "e");
    return s;
  }

  /* --- 1. The entropic plan between two histograms: temperature, iterations, conditional laws (§3, §4) --- */
  WIDGETS.l7plan = function (box) {
    var s = scaffold(box, "Sinkhorn between two histograms: the plan blurs as ε grows, and sharpens towards the optimal plan as ε → 0");
    var W = 680, H = 380, N = 48;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Heat map of the entropic transport plan with its marginals, and the conditional law of one row");
    var pairSel = select(s.controls, "Histograms", [["split", "two bumps → one bump"], ["shift", "one bump → shifted bump"]], "split", setup);
    var eS = slider(s.controls, "ε", -3.3, 0, 0.01, -2, draw);
    var iS = slider(s.controls, "iterations ℓ", 0, 3.4, 0.01, 3, draw);
    var showOT = checkbox(s.controls, "show the exact optimal plan", true, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--text", "entropic plan P (grey levels)"], ["--s2", "a (rows)"], ["--s1", "b (columns)"], ["--s3", "barycentric projection"], ["--muted", "exact optimal plan (dashed)"]]);
    var D, C, P0, L0, sel = 10, X0 = 70, Y0 = 60, S = 270;
    function setup() {
      D = l7hist(pairSel.value, N); C = l7cost(D.t, D.t); P0 = l7monotone(D.a, D.b);
      L0 = l7planStats(P0, D.a, D.b, C).cost; draw();
    }
    function pick(e) {
      var pt = svgPoint(s.svg, e);
      if (pt.x < X0 - 30 || pt.x > X0 + S || pt.y < Y0 || pt.y > Y0 + S) return;
      var i = Math.max(0, Math.min(N - 1, Math.floor((pt.y - Y0) / S * N)));
      if (i !== sel) { sel = i; draw(); }
    }
    s.svg.addEventListener("pointermove", function (e) { if (e.pointerType === "mouse") pick(e); });
    s.svg.addEventListener("pointerdown", pick);
    function draw() {
      var eps = Math.pow(10, eS.get()), it = Math.max(1, Math.round(Math.pow(10, iS.get())));
      eS.out.textContent = eps < 0.01 ? eps.toExponential(1) : fmt(eps, 3); iS.out.textContent = String(it);
      var R = l7sinkhorn(D.a, D.b, C, eps, it, {});
      var P = R.P, i, j;
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg);
      l7heat(g, P, X0, Y0, S, S, "fk", 0.5, 14);
      // marginals: a on the left (bars to the left), b on top
      var ma = Math.max.apply(null, D.a), mb = Math.max.apply(null, D.b), da = "", db = "";
      for (i = 0; i < N; i++) da += (i ? "L" : "M") + (X0 - 4 - D.a[i] / ma * 40).toFixed(1) + " " + (Y0 + (i + 0.5) / N * S).toFixed(1);
      for (j = 0; j < N; j++) db += (j ? "L" : "M") + (X0 + (j + 0.5) / N * S).toFixed(1) + " " + (Y0 - 4 - D.b[j] / mb * 40).toFixed(1);
      el("path", { d: da, "class": "ln c2 thin" }, g); el("path", { d: db, "class": "ln c1 thin" }, g);
      // current marginals of P (after the column update the columns are exact; the rows are not)
      var rows = P.map(function (r) { return r.reduce(function (u, v) { return u + v; }, 0); });
      var dr = "";
      for (i = 0; i < N; i++) dr += (i ? "L" : "M") + (X0 - 4 - rows[i] / ma * 40).toFixed(1) + " " + (Y0 + (i + 0.5) / N * S).toFixed(1);
      el("path", { d: dr, "class": "ln ck hair dash" }, g);
      var t1 = el("text", { x: X0 - 46, y: Y0 - 8, "class": "tx-s t2" }, g); t1.textContent = "a";
      var t2 = el("text", { x: X0 + S + 6, y: Y0 - 8, "class": "tx-s t1" }, g); t2.textContent = "b";
      // exact optimal plan support
      if (showOT.checked) {
        var d0 = "";
        for (i = 0; i < N; i++) for (j = 0; j < N; j++) if (P0[i][j] > 1e-12) d0 += "M" + (X0 + (j + 0.5) / N * S).toFixed(1) + " " + (Y0 + (i + 0.5) / N * S).toFixed(1) + "h0.01";
        el("path", { d: d0, "class": "ln cm", "stroke-width": 3.2, "stroke-opacity": 0.55 }, g);
      }
      // barycentric projection T(x_i) = sum_j P_ij y_j / rows_i, drawn in plan coordinates
      var dT = "";
      for (i = 0; i < N; i++) {
        var Ti = 0; for (j = 0; j < N; j++) Ti += P[i][j] * D.t[j]; Ti /= rows[i];
        dT += (i ? "L" : "M") + (X0 + Ti * S).toFixed(1) + " " + (Y0 + (i + 0.5) / N * S).toFixed(1);
      }
      el("path", { d: dT, "class": "ln c3 thin" }, g);
      // selected row
      el("rect", { x: X0, y: (Y0 + sel / N * S).toFixed(1), width: S, height: (S / N).toFixed(2), "class": "ln c2 thin nofill" }, g);
      var lab = el("text", { x: X0 + S / 2, y: Y0 + S + 18, "class": "tx-s", "text-anchor": "middle" }, g);
      lab.textContent = "rows: source points xᵢ (top to bottom) · columns: target points yⱼ (left to right)";
      // right panel: conditional law of row sel
      var PX = 400, PW = 260, PY = 70, PH = 210;
      var cond = P[sel].map(function (v) { return v / rows[sel]; });
      var cmax = Math.max.apply(null, cond), mean = 0, vr = 0;
      for (j = 0; j < N; j++) mean += cond[j] * D.t[j];
      for (j = 0; j < N; j++) vr += cond[j] * (D.t[j] - mean) * (D.t[j] - mean);
      el("rect", { x: PX, y: PY, width: PW, height: PH, "class": "ln cm hair nofill" }, g);
      var dc = "M" + PX + " " + (PY + PH);
      for (j = 0; j < N; j++) dc += "L" + (PX + (j + 0.5) / N * PW).toFixed(1) + " " + (PY + PH - cond[j] / cmax * (PH - 20)).toFixed(1);
      dc += "L" + (PX + PW) + " " + (PY + PH) + "Z";
      el("path", { d: dc, "class": "a1 ln c1 thin" }, g);
      // Monge image of x_sel: the targets the exact plan sends row sel to
      var lo = 1, hi = 0;
      for (j = 0; j < N; j++) if (P0[sel][j] > 1e-12) { lo = Math.min(lo, D.t[j]); hi = Math.max(hi, D.t[j]); }
      el("rect", { x: (PX + (lo - 0.5 / N) * PW).toFixed(1), y: PY, width: Math.max(1.5, (hi - lo + 1 / N) * PW).toFixed(1), height: PH, "class": "am" }, g);
      el("line", { x1: PX + mean * PW, x2: PX + mean * PW, y1: PY, y2: PY + PH, "class": "ln c3" }, g);
      [0, 0.25, 0.5, 0.75, 1].forEach(function (v) { var tt = el("text", { x: PX + v * PW, y: PY + PH + 14, "class": "tx-s", "text-anchor": "middle" }, g); tt.textContent = fmt(v, 2); });
      var hdr = el("text", { x: PX, y: PY - 26, "class": "tx-b" }, g); hdr.textContent = "Conditional law of Y given X = x" + "ᵢ" + ", x = " + fmt(D.t[sel], 3);
      var sub = el("text", { x: PX, y: PY - 10, "class": "tx-s" }, g); sub.textContent = "(hover or tap a row of the plan to change it)";
      var nt = el("text", { x: PX + PW, y: PY + 14, "class": "tx-s t3", "text-anchor": "end" }, g); nt.textContent = "mean = T(x) = " + fmt(mean, 3);
      var nt2 = el("text", { x: PX + PW, y: PY + 28, "class": "tx-s", "text-anchor": "end" }, g); nt2.textContent = "std = " + fmt(Math.sqrt(vr), 3) + ",  √(ε/2) = " + fmt(Math.sqrt(eps / 2), 3);
      var nt3 = el("text", { x: PX + PW, y: PY + 42, "class": "tx-s", "text-anchor": "end" }, g); nt3.textContent = "grey band: where the exact plan sends x";
      // readout
      var st = l7planStats(P, D.a, D.b, C), e = 0;
      for (i = 0; i < N; i++) e += Math.abs(rows[i] - D.a[i]);
      ro.textContent = "ε = " + (eps < 0.01 ? eps.toExponential(2) : fmt(eps, 4)) + ",  ℓ = " + it + " cycles:  row error ‖P𝟙 − a‖₁ = " + l7exp(e) + "  (columns are exact after each cycle)" +
        "\n⟨C,P⟩ = " + fmt(st.cost, 5) + "   KL(P|a⊗b) = " + fmt(st.kl, 3) + "   L^ε = ⟨C,P⟩ + ε·KL = " + fmt(st.cost + eps * st.kl, 5) +
        "\nexact transport cost L_C = " + fmt(L0, 5) + "   bias L^ε − L_C = " + fmt(st.cost + eps * st.kl - L0, 5);
    }
    setup(); redrawers.push(draw);
  };

  /* --- 2. Convergence of Sinkhorn: marginal error against iterations, for several temperatures (§7) --- */
  WIDGETS.l7conv = function (box) {
    var s = scaffold(box, "How fast Sinkhorn converges: the row-marginal error after each cycle, for four temperatures (log scale)");
    var plot = new Plot(s.svg, { x: [0, 1000], y: [-13, 0.5], w: 680, h: 330, pad: { l: 52, r: 120, t: 18, b: 36 }, label: "Marginal error of Sinkhorn against the number of iterations" });
    var pairSel = select(s.controls, "Histograms", [["split", "two bumps → one bump"], ["shift", "one bump → shifted bump"]], "split", compute);
    var hSel = select(s.controls, "horizon", [["300", "300 cycles"], ["1000", "1000 cycles"], ["3000", "3000 cycles"]], "1000", draw);
    var pred = checkbox(s.controls, "show the predicted slopes σ²", true, draw);
    var ro = readout(s.controls);
    var EPS = [0.1, 0.03, 0.01, 0.003, 0.001], COLS = ["c2", "c4", "c3", "c1", "c5"], runs = [];
    legend(s.legend, EPS.map(function (e, k) { return ["--s" + COLS[k].slice(1), "ε = " + e]; }).concat([["--muted", "predicted slope σ_ε² (dashed)"]]));
    function compute() {
      var D = l7hist(pairSel.value, 48), C = l7cost(D.t, D.t);
      // Birkhoff: Delta = max over i,j,k,l of C_jk + C_il - C_ik - C_jl
      var n = 48, Delta = 0, i, j, k;
      for (i = 0; i < n; i++) for (j = 0; j < n; j++) {
        var m1 = -Infinity, m2 = -Infinity;
        for (k = 0; k < n; k++) { m1 = Math.max(m1, C[j][k] - C[i][k]); m2 = Math.max(m2, C[i][k] - C[j][k]); }
        Delta = Math.max(Delta, m1 + m2);
      }
      runs = EPS.map(function (eps) {
        var R = l7sinkhorn(D.a, D.b, C, eps, 3000, { record: true, tol: 1e-13 });
        var sig = l7sigma2(R.P, D.a, D.b);
        var hit = -1; for (k = 0; k < R.errs.length; k++) if (R.errs[k] < 1e-9) { hit = k + 1; break; }
        var e = R.errs, L = e.length, rate = L > 12 ? Math.pow(e[L - 1] / e[L - 11], 0.1) : NaN;
        var lam = Math.tanh(Delta / (4 * eps));
        return { eps: eps, errs: e, sig2: sig * sig, hit: hit, rate: rate, gain: 1 - lam * lam };
      });
      draw();
    }
    function draw() {
      var Hz = parseInt(hSel.value, 10);
      plot.o.x = [0, Hz];
      plot.clear();
      var xt = Hz === 300 ? [0, 100, 200, 300] : Hz === 1000 ? [0, 250, 500, 750, 1000] : [0, 1000, 2000, 3000];
      plot.axes({ xticks: xt, yticks: [0, -3, -6, -9, -12], yfmt: function (v) { return v === 0 ? "1" : "1e" + v; }, xlabel: "cycles ℓ" });
      plot.clip();
      runs.forEach(function (r, k) {
        var pts = [];
        for (var i = 0; i < r.errs.length && i < Hz; i++) pts.push([i + 1, Math.log10(Math.max(r.errs[i], 1e-16))]);
        plot.poly(pts, "ln " + COLS[k] + " thin");
        if (pred.checked && r.sig2 > 0 && r.errs.length > 2) {
          // line of slope log10(sigma^2) through the point where the error is about 1e-3 (or the first point)
          var i0 = 0; while (i0 < r.errs.length - 1 && r.errs[i0] > 1e-3) i0++;
          var y0 = Math.log10(r.errs[i0]), sl = Math.log10(r.sig2);
          plot.poly([[i0 + 1, y0 + 0.4], [Hz, y0 + 0.4 + sl * (Hz - i0 - 1)]], "ln cm thin dash");
        }
      });
      plot.unclip();
      runs.forEach(function (r, k) {
        var last = Math.min(r.errs.length, Hz) - 1, y = Math.log10(Math.max(r.errs[last], 1e-16));
        var yy = Math.max(-12.6, Math.min(0.2, y));
        plot.text(Hz, yy, "ε = " + r.eps, "tx-s t" + (COLS[k] === "c4" ? "2" : COLS[k].slice(1)), "start", 6, 4 + (k - 2) * 2);
      });
      var lines = runs.map(function (r) {
        return "ε = " + (r.eps + "      ").slice(0, 6) + "  cycles to 1e−9: " + (r.hit > 0 ? r.hit : "> 3000") + "   measured rate per cycle: " + fmt(r.rate, 4) +
          "   σ_ε² = " + fmt(r.sig2, 4) + "   Birkhoff guarantee 1 − λ² = " + l7exp(r.gain);
      });
      ro.textContent = lines.join("\n");
    }
    compute(); redrawers.push(draw);
  };

  /* --- 3. Plain Sinkhorn against log-domain Sinkhorn for small temperatures (§6) --- */
  WIDGETS.l7underflow = function (box) {
    var s = scaffold(box, "When ε is small, exp(−C/ε) underflows: the plain iteration breaks, the log-domain iteration does not");
    var W = 680, H = 330, n = 30;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "The Gibbs kernel with its underflowed entries, and the marginal errors of the two iterations");
    var eS = slider(s.controls, "ε", -4, -1, 0.01, -2.5, draw);
    var pSel = select(s.controls, "arithmetic", [["64", "double precision (float64)"], ["32", "single precision (float32, as on most GPUs)"]], "64", draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "entries of K that are exactly 0"], ["--muted", "plain iteration u ← a/Kv"], ["--s3", "log-domain iteration"]]);
    var xs = [], ys = [], a = [], b = [], i, j;
    for (i = 0; i < n; i++) { xs.push(0.35 * (i + 0.5) / n); ys.push(0.55 + 0.45 * (i + 0.5) / n); a.push(1 / n); b.push(1 / n); }
    var C = l7cost(xs, ys), ITER = 150;
    function draw() {
      var eps = Math.pow(10, eS.get()), f32 = pSel.value === "32";
      var R = f32 ? Math.fround : function (v) { return v; };
      eS.out.textContent = eps.toExponential(1);
      // Gibbs kernel in the chosen precision
      var K = [], zeros = 0, zrows = 0;
      for (i = 0; i < n; i++) {
        K.push([]); var rz = true;
        for (j = 0; j < n; j++) { var k = R(Math.exp(-C[i][j] / eps)); K[i].push(k); if (k === 0) zeros++; else rz = false; }
        if (rz) zrows++;
      }
      // plain Sinkhorn
      var u = new Array(n).fill(1), v = new Array(n).fill(1), plain = [], fail = -1, it;
      for (it = 1; it <= ITER; it++) {
        for (i = 0; i < n; i++) { var s1 = 0; for (j = 0; j < n; j++) s1 = R(s1 + R(K[i][j] * v[j])); u[i] = R(a[i] / s1); }
        for (j = 0; j < n; j++) { var s2 = 0; for (i = 0; i < n; i++) s2 = R(s2 + R(K[i][j] * u[i])); v[j] = R(b[j] / s2); }
        var e = 0;
        for (i = 0; i < n; i++) { var r = 0; for (j = 0; j < n; j++) r = R(r + R(R(u[i] * K[i][j]) * v[j])); e += Math.abs(r - a[i]); }
        if (!isFinite(e)) { fail = it; break; }
        plain.push(e);
      }
      // log-domain Sinkhorn in the same precision
      var f = new Array(n).fill(0), g = new Array(n).fill(0), logd = [], la = Math.log(1 / n);
      for (it = 1; it <= ITER; it++) {
        for (i = 0; i < n; i++) {
          var mx = -Infinity; for (j = 0; j < n; j++) mx = Math.max(mx, (g[j] - C[i][j]) / eps);
          var ss = 0; for (j = 0; j < n; j++) ss = R(ss + R(Math.exp(R((g[j] - C[i][j]) / eps - mx))));
          f[i] = R(-eps * (mx + Math.log(ss) + la));
        }
        for (j = 0; j < n; j++) {
          var mx2 = -Infinity; for (i = 0; i < n; i++) mx2 = Math.max(mx2, (f[i] - C[i][j]) / eps);
          var ss2 = 0; for (i = 0; i < n; i++) ss2 = R(ss2 + R(Math.exp(R((f[i] - C[i][j]) / eps - mx2))));
          g[j] = R(-eps * (mx2 + Math.log(ss2) + la));
        }
        var e2 = 0;
        for (i = 0; i < n; i++) { var r2 = 0; for (j = 0; j < n; j++) r2 = R(r2 + R(Math.exp(R(2 * la + (f[i] + g[j] - C[i][j]) / eps)))); e2 += Math.abs(r2 - a[i]); }
        logd.push(Math.max(e2, 1e-16));
      }
      // draw: kernel on the left
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var gr = el("g", {}, s.svg), X0 = 40, Y0 = 34, S = 240, cw = S / n;
      var floorLog = f32 ? 45.2 : 323.3; // -log10 of the smallest positive (subnormal) number
      for (i = 0; i < n; i++) for (j = 0; j < n; j++) {
        if (K[i][j] === 0) el("rect", { x: X0 + j * cw, y: Y0 + i * cw, width: cw + 0.2, height: cw + 0.2, "class": "f2", "fill-opacity": 0.75 }, gr);
        else {
          var op = 1 - (-Math.log10(K[i][j])) / floorLog;
          el("rect", { x: X0 + j * cw, y: Y0 + i * cw, width: cw + 0.2, height: cw + 0.2, "class": "fk", "fill-opacity": Math.max(0.04, op * 0.8).toFixed(2) }, gr);
        }
      }
      el("rect", { x: X0, y: Y0, width: S, height: S, "class": "ln cm hair nofill" }, gr);
      var tk = el("text", { x: X0 + S / 2, y: Y0 - 10, "class": "tx-b", "text-anchor": "middle" }, gr); tk.textContent = "K = exp(−C/ε), " + (f32 ? "float32" : "float64");
      var tk2 = el("text", { x: X0 + S / 2, y: Y0 + S + 16, "class": "tx-s", "text-anchor": "middle" }, gr); tk2.textContent = "rows: x in [0, 0.35] · columns: y in [0.55, 1]";
      var tk3 = el("text", { x: X0 + S / 2, y: Y0 + S + 30, "class": "tx-s", "text-anchor": "middle" }, gr); tk3.textContent = "grey level ∝ log K (darker = larger)";
      // errors on the right
      var P = new Plot(s.svg, { x: [0, ITER], y: [-16, 1], w: W, h: H, pad: { l: 360, r: 16, t: 34, b: 36 } });
      P.g = el("g", {}, s.svg);
      P.axes({ xticks: [0, 50, 100, 150], yticks: [0, -4, -8, -12, -16], yfmt: function (v) { return v === 0 ? "1" : "1e" + v; }, xlabel: "cycles" });
      P.clip();
      P.poly(plain.map(function (e, k) { return [k + 1, Math.log10(Math.max(e, 1e-16))]; }), "ln cm");
      P.poly(logd.map(function (e, k) { return [k + 1, Math.log10(e)]; }), "ln c3");
      P.unclip();
      var hd = el("text", { x: 360, y: 24, "class": "tx-b" }, s.svg); hd.textContent = "row-marginal error ‖P𝟙 − a‖₁";
      if (fail > 0) {
        var xf = P.tx(Math.min(fail, ITER)), yt = P.ty(0) + 16;
        el("line", { x1: xf, x2: xf, y1: P.ty(1), y2: P.ty(-16), "class": "ln c2 thin dash" }, s.svg);
        var tf = el("text", { x: Math.min(xf + 6, W - 150), y: yt + 14, "class": "tx-s t2" }, s.svg);
        tf.textContent = "plain: NaN / ∞ at cycle " + fail;
      }
      var minC = Infinity; for (j = 0; j < n; j++) minC = Math.min(minC, C[0][j]);
      var thr = f32 ? 103.28 : 744.44;
      ro.textContent = "ε = " + eps.toExponential(2) + ": " + zeros + " of " + n * n + " entries of K are exactly 0, " + zrows + " whole rows vanish" +
        "  (first row: smallest cost " + fmt(minC, 4) + ", so its row vanishes when ε < " + (minC / thr).toExponential(2) + ")" +
        "\nplain iteration: " + (fail > 0 ? "fails at cycle " + fail + " (division by 0 or overflow → ∞, then NaN)" : "error " + l7exp(plain[plain.length - 1]) + " after " + ITER + " cycles") +
        "\nlog-domain iteration: error " + l7exp(logd[logd.length - 1]) + " after " + ITER + " cycles";
    }
    draw(); redrawers.push(draw);
  };

  /* --- 4. The entropic bias and the Sinkhorn divergence, exactly, for Gaussians on the line (§9) --- */
  function l7k(sa, sb, eps) { return (Math.sqrt(eps * eps + 16 * sa * sa * sb * sb) - eps) / 4; }
  function l7L(ma, sa, mb, sb, eps) {
    var k = l7k(sa, sb, eps);
    return (ma - mb) * (ma - mb) + sa * sa + sb * sb - 2 * k - eps / 2 * Math.log(1 - k * k / (sa * sa * sb * sb));
  }
  function l7S(ma, sa, mb, sb, eps) { return l7L(ma, sa, mb, sb, eps) - 0.5 * l7L(ma, sa, ma, sa, eps) - 0.5 * l7L(mb, sb, mb, sb, eps); }
  WIDGETS.l7debias = function (box) {
    var s = scaffold(box, "Fitting β = N(m, s²) to α = N(0, 1): raw entropic cost against Sinkhorn divergence (exact formulas)");
    var plot = new Plot(s.svg, { x: [-2, 2], y: [0, 5], w: 680, h: 320, pad: { l: 50, r: 20, t: 20, b: 38 }, label: "Raw entropic cost, Sinkhorn divergence and W2 squared as functions of the parameter of beta" });
    var vSel = select(s.controls, "move", [["s", "the width s (m = 0)"], ["m", "the mean m (s = 1)"]], "s", draw);
    var eS = slider(s.controls, "ε", -2, 1.3, 0.01, -0.3, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "raw L^ε(α, β)"], ["--s3", "Sinkhorn divergence S_ε(α, β)"], ["--s1", "W₂²(α, β) (dashed)"], ["--muted", "bias level L^ε(α, α)"]]);
    function draw() {
      var eps = Math.pow(10, eS.get()), mode = vSel.value;
      eS.out.textContent = eps < 0.1 ? eps.toFixed(3) : fmt(eps, 2);
      var X = mode === "s" ? [0.02, 2.5] : [-2, 2];
      function F(x, which) {
        var m = mode === "s" ? 0 : x, sd = mode === "s" ? x : 1;
        if (which === "L") return l7L(0, 1, m, sd, eps);
        if (which === "S") return l7S(0, 1, m, sd, eps);
        return m * m + (1 - sd) * (1 - sd);
      }
      var xs = [], i; for (i = 0; i <= 300; i++) xs.push(X[0] + (X[1] - X[0]) * i / 300);
      var Lv = xs.map(function (x) { return F(x, "L"); }), Sv = xs.map(function (x) { return F(x, "S"); }), Wv = xs.map(function (x) { return F(x, "W"); });
      var top = Math.max(Math.max.apply(null, Lv), Math.max.apply(null, Wv)) * 1.08;
      plot.o.x = X; plot.o.y = [0, Math.min(top, 8)];
      plot.clear();
      var yt = []; var stp = top > 4 ? 1 : top > 2 ? 0.5 : 0.25; for (var v = 0; v <= plot.o.y[1]; v += stp) yt.push(v);
      plot.axes({ xticks: mode === "s" ? [0, 0.5, 1, 1.5, 2, 2.5] : [-2, -1, 0, 1, 2], yticks: yt, xfmt: function (t) { return fmt(t, 1); }, yfmt: function (t) { return fmt(t, 2); }, xlabel: mode === "s" ? "width s of β" : "mean m of β" });
      plot.clip();
      var bias = l7L(0, 1, 0, 1, eps);
      plot.seg(X[0], bias, X[1], bias, "ln cm thin dot");
      plot.poly(xs.map(function (x, k) { return [x, Wv[k]]; }), "ln c1 thin dash");
      plot.poly(xs.map(function (x, k) { return [x, Lv[k]]; }), "ln c2");
      plot.poly(xs.map(function (x, k) { return [x, Sv[k]]; }), "ln c3");
      plot.unclip();
      function argmin(arr) { var b = 0; for (var k = 1; k < arr.length; k++) if (arr[k] < arr[b]) b = k; return b; }
      var iL = argmin(Lv), iS2 = argmin(Sv);
      plot.dot(xs[iL], Lv[iL], 5, "f2"); plot.dot(xs[iS2], Sv[iS2], 5, "f3");
      plot.text(X[1], bias, "L^ε(α, α) = " + fmt(bias, 4), "tx-s", "end", -4, -5);
      var exact = mode === "s" ? (eps < 2 ? "√(1 − ε/2) = " + fmt(Math.sqrt(1 - eps / 2), 4) : "0 (collapse: ε ≥ 2)") : "0";
      ro.textContent = "ε = " + fmt(eps, 4) + ":  bias L^ε(α, α) = " + fmt(bias, 4) + "  (> 0, although β = α is the target)" +
        "\nraw cost minimized at " + (mode === "s" ? "s ≈ " : "m ≈ ") + fmt(xs[iL], 3) + (mode === "s" ? "   (exact value " + exact + ")" : "   (a translation does not change the bias)") +
        "\nSinkhorn divergence minimized at " + (mode === "s" ? "s ≈ " : "m ≈ ") + fmt(xs[iS2], 3) + ",  where it is 0:  S_ε(α, α) = 0";
    }
    draw(); redrawers.push(draw);
  };

  /* --- 5. Particles descending the raw entropic loss or the Sinkhorn divergence (§9, §11) --- */
  WIDGETS.l7flow = function (box) {
    var s = scaffold(box, "Fitting a cloud of particles to a target cloud: gradient steps on the raw loss or on the Sinkhorn divergence");
    var W = 680, H = 380;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Target cloud and moving particles");
    var lossSel = select(s.controls, "loss", [["raw", "raw entropic cost L^ε"], ["deb", "Sinkhorn divergence S_ε"]], "raw", reset);
    var eSel = select(s.controls, "ε", [["0.02", "0.02"], ["0.1", "0.1"], ["0.5", "0.5"], ["2", "2"]], "0.5", reset);
    button(s.controls, "Step", function () { if (!timer) { step(); draw(); } });
    var runB = button(s.controls, "Run 40 steps", function () { run(40); });
    button(s.controls, "Reset", reset);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "target β (fixed)"], ["--s2", "particles α (moving)"], ["--s3", "displacement of the last step"]]);
    var rng = mulberry32(17), Y = [], X0 = [], i, j, k;
    for (i = 0; i < 70; i++) { var c = i < 35 ? [-0.8, 0.35] : [0.75, -0.3]; Y.push([c[0] + 0.32 * gaussRand(rng), c[1] + 0.26 * gaussRand(rng)]); }
    for (i = 0; i < 50; i++) X0.push([0.6 * gaussRand(rng) - 0.1, 0.5 * gaussRand(rng) + 1.2]);
    var X, nstep, timer = null, last = null, potXY = null, potXX = null;
    function costM(A, B) { return A.map(function (p) { return B.map(function (q) { var dx = p[0] - q[0], dy = p[1] - q[1]; return 0.5 * (dx * dx + dy * dy); }); }); }
    function unif(nn) { return new Array(nn).fill(1 / nn); }
    function bary(A, B, eps, warm, sym) {
      var C = costM(A, B), n = A.length, m = B.length, a = unif(n), b = unif(m), R;
      if (sym) {
        // averaged symmetric updates for the self term (keeps f = g)
        var f = warm ? warm.f.slice() : new Array(n).fill(0), it, ii, jj;
        for (it = 0; it < 60; it++) {
          var fn = [];
          for (ii = 0; ii < n; ii++) {
            var mx = -Infinity, row = [];
            for (jj = 0; jj < n; jj++) { row.push(Math.log(1 / n) + (f[jj] - C[ii][jj]) / eps); if (row[jj] > mx) mx = row[jj]; }
            var ss = 0; for (jj = 0; jj < n; jj++) ss += Math.exp(row[jj] - mx);
            fn.push(-eps * (mx + Math.log(ss)));
          }
          for (ii = 0; ii < n; ii++) f[ii] = 0.5 * (f[ii] + fn[ii]);
        }
        R = { f: f, g: f };
      } else {
        R = l7sinkhorn(a, b, C, eps, 60, warm ? { f: warm.f, g: warm.g } : {});
      }
      var T = [];
      for (var p = 0; p < n; p++) {
        var w = 0, tx = 0, ty = 0;
        for (var q = 0; q < m; q++) { var pij = Math.exp((R.f[p] + R.g[q] - C[p][q]) / eps) / m; w += pij; tx += pij * B[q][0]; ty += pij * B[q][1]; }
        T.push([tx / w, ty / w]);
      }
      return { T: T, f: R.f, g: R.g };
    }
    function reset() {
      if (timer) { clearInterval(timer); timer = null; }
      X = X0.map(function (p) { return p.slice(); }); nstep = 0; last = null; potXY = null; potXX = null; draw();
    }
    function step() {
      var eps = parseFloat(eSel.value), tau = 0.5;
      var r1 = bary(X, Y, eps, potXY, false); potXY = { f: r1.f, g: r1.g };
      var Xn;
      if (lossSel.value === "raw") {
        Xn = X.map(function (p, q) { return [p[0] - tau * (p[0] - r1.T[q][0]), p[1] - tau * (p[1] - r1.T[q][1])]; });
      } else {
        var r2 = bary(X, X, eps, potXX, true); potXX = { f: r2.f, g: r2.g };
        Xn = X.map(function (p, q) { return [p[0] - tau * (r2.T[q][0] - r1.T[q][0]), p[1] - tau * (r2.T[q][1] - r1.T[q][1])]; });
      }
      last = X; X = Xn; nstep++;
    }
    function run(nn) {
      if (timer) return;
      var c = 0;
      timer = setInterval(function () { step(); draw(); c++; if (c >= nn) { clearInterval(timer); timer = null; } }, 60);
    }
    function spread(A) {
      var mx = 0, my = 0, v = 0; A.forEach(function (p) { mx += p[0]; my += p[1]; }); mx /= A.length; my /= A.length;
      A.forEach(function (p) { v += (p[0] - mx) * (p[0] - mx) + (p[1] - my) * (p[1] - my); }); return { v: v / A.length, m: [mx, my] };
    }
    var box2 = { x0: 20, y0: 10, w: 420, h: 360, xr: [-2.4, 2.4] };
    box2.k = box2.w / (box2.xr[1] - box2.xr[0]);
    function MX(x) { return box2.x0 + (x - box2.xr[0]) * box2.k; }
    function MY(y) { return box2.y0 + box2.h / 2 - (y - 0.15) * box2.k; }
    function draw() {
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg);
      el("rect", { x: box2.x0, y: box2.y0, width: box2.w, height: box2.h, "class": "ln cm hair nofill" }, g);
      Y.forEach(function (p) { el("circle", { cx: MX(p[0]), cy: MY(p[1]), r: 3.2, "class": "f1", "fill-opacity": 0.75 }, g); });
      if (last) X.forEach(function (p, q) { el("line", { x1: MX(last[q][0]), y1: MY(last[q][1]), x2: MX(p[0]), y2: MY(p[1]), "class": "ln c3 hair" }, g); });
      X.forEach(function (p) { el("circle", { cx: MX(p[0]), cy: MY(p[1]), r: 3.6, "class": "f2" }, g); });
      var sx = spread(X), sy = spread(Y);
      var lines = ["step " + nstep, "loss: " + (lossSel.value === "raw" ? "raw L^ε" : "Sinkhorn divergence S_ε"), "ε = " + eSel.value + ",  step τ = 0.5",
        "spread of α / spread of β:", "   " + fmt(sx.v / sy.v, 3), "mean of α: (" + fmt(sx.m[0], 2) + ", " + fmt(sx.m[1], 2) + ")", "mean of β: (" + fmt(sy.m[0], 2) + ", " + fmt(sy.m[1], 2) + ")",
        "update of particle i:", lossSel.value === "raw" ? "  xᵢ ← xᵢ − τ (xᵢ − ȳᵢ)" : "  xᵢ ← xᵢ − τ (x̄ᵢ − ȳᵢ)",
        "ȳᵢ: barycentric projection", "  of xᵢ through the plan α → β", lossSel.value === "raw" ? "" : "x̄ᵢ: same through the plan α → α"];
      lines.forEach(function (t, q) { var tt = el("text", { x: 460, y: 34 + 22 * q, "class": q === 0 ? "tx-b" : "tx-s" }, g); tt.textContent = t; });
      ro.textContent = "spread = mean squared distance to the mean (trace of the covariance). The raw loss pulls every particle to a blurred average of β; the divergence subtracts the self-transport α → α, and the blur cancels.";
    }
    reset();
    redrawers.push(draw);
  };

  /* --- 6. Softmax attention is one half-step of Sinkhorn (§6, In machine learning) --- */
  WIDGETS.l7attention = function (box) {
    var s = scaffold(box, "Attention weights: one row normalization (softmax) versus Sinkhorn's alternate normalization");
    var W = 680, H = 300, n = 6;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "A six by six attention matrix with its row and column sums");
    var hS = slider(s.controls, "half-steps", 1, 12, 1, 1, draw);
    var tS = slider(s.controls, "temperature", -1, 1, 0.01, 0, draw);
    var ro = readout(s.controls);
    var rng = mulberry32(42), Q = [], Kk = [], i, j;
    for (i = 0; i < n; i++) { Q.push([gaussRand(rng), gaussRand(rng)]); Kk.push([gaussRand(rng), gaussRand(rng)]); }
    var Sc = Q.map(function (q) { return Kk.map(function (k) { return q[0] * k[0] + q[1] * k[1]; }); });
    function draw() {
      var hs = Math.round(hS.get()), temp = Math.pow(10, tS.get());
      hS.out.textContent = String(hs); tS.out.textContent = fmt(temp, 2);
      // K = exp(S / temp); half-steps alternate row and column normalization (target sums 1)
      var M = Sc.map(function (r) { return r.map(function (v) { return Math.exp(v / temp); }); });
      for (var h = 0; h < hs; h++) {
        if (h % 2 === 0) M = M.map(function (r) { var su = r.reduce(function (u, v) { return u + v; }, 0); return r.map(function (v) { return v / su; }); });
        else { var cs = []; for (j = 0; j < n; j++) { cs.push(0); for (i = 0; i < n; i++) cs[j] += M[i][j]; } M = M.map(function (r) { return r.map(function (v, jj) { return v / cs[jj]; }); }); }
      }
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg), x0 = 150, y0 = 40, cs2 = 36;
      for (i = 0; i < n; i++) for (j = 0; j < n; j++) {
        el("rect", { x: x0 + j * cs2, y: y0 + i * cs2, width: cs2, height: cs2, "class": "fk", "fill-opacity": Math.min(0.85, M[i][j] * 0.85).toFixed(2) }, g);
        el("rect", { x: x0 + j * cs2, y: y0 + i * cs2, width: cs2, height: cs2, "class": "ln cm hair nofill" }, g);
        el("rect", { x: x0 + j * cs2 + 4, y: y0 + i * cs2 + 11, width: cs2 - 8, height: 14, rx: 3, "class": "fs", "fill-opacity": 0.85 }, g);
        var t = el("text", { x: x0 + j * cs2 + cs2 / 2, y: y0 + i * cs2 + 22, "class": "tx-s", "text-anchor": "middle" }, g); t.textContent = fmt(M[i][j], 2);
      }
      var rs = M.map(function (r) { return r.reduce(function (u, v) { return u + v; }, 0); }), csum = [];
      for (j = 0; j < n; j++) { csum.push(0); for (i = 0; i < n; i++) csum[j] += M[i][j]; }
      var er = 0, ec = 0;
      for (i = 0; i < n; i++) {
        er += Math.abs(rs[i] - 1);
        var tr = el("text", { x: x0 + n * cs2 + 8, y: y0 + i * cs2 + 22, "class": Math.abs(rs[i] - 1) < 5e-3 ? "tx-s t3" : "tx-s" }, g); tr.textContent = fmt(rs[i], 3);
      }
      for (j = 0; j < n; j++) {
        ec += Math.abs(csum[j] - 1);
        var tc = el("text", { x: x0 + j * cs2 + cs2 / 2, y: y0 + n * cs2 + 16, "class": Math.abs(csum[j] - 1) < 5e-3 ? "tx-s t3" : "tx-s", "text-anchor": "middle" }, g); tc.textContent = fmt(csum[j], 2);
      }
      var h1 = el("text", { x: x0 + n * cs2 / 2, y: y0 - 14, "class": "tx-b", "text-anchor": "middle" }, g);
      h1.textContent = hs === 1 ? "softmax attention (one row normalization)" : "after " + hs + " half-steps of Sinkhorn";
      var h2 = el("text", { x: x0 - 10, y: y0 + n * cs2 / 2, "class": "tx-s", "text-anchor": "end" }, g); h2.textContent = "queries i";
      var h3 = el("text", { x: x0 + n * cs2 + 8, y: y0 - 4, "class": "tx-s" }, g); h3.textContent = "row sums";
      var h4 = el("text", { x: x0 + n * cs2 / 2, y: y0 + n * cs2 + 32, "class": "tx-s", "text-anchor": "middle" }, g); h4.textContent = "keys j  ·  column sums (green when equal to 1)";
      ro.textContent = "row error Σ|row sum − 1| = " + l7exp(er) + "     column error Σ|column sum − 1| = " + l7exp(ec) +
        "\nscores ⟨qᵢ, kⱼ⟩ play the role of −C; the temperature plays the role of ε. Odd half-steps fix the rows, even half-steps the columns.";
    }
    draw(); redrawers.push(draw);
  };
