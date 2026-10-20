// widgets/Lesson08.js — interactive figures of Lesson 8 (Wasserstein gradient flows).
// Inserted by build.mjs inside the scope of app.js: it uses el, Plot, scaffold, slider, select, button, checkbox,
// readout, legend, fmt, addSvg, mulberry32, gaussRand, redrawers, and registers its widgets in WIDGETS.
// All the helpers of this file are prefixed by l8.

  /* ---------------- small numerical helpers ---------------- */
  function l8erfc(x) { // complementary error function, fractional error < 1.2e-7 (Numerical Recipes erfcc)
    var z = Math.abs(x), t = 1 / (1 + 0.5 * z);
    var r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 +
      t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
    return x >= 0 ? r : 2 - r;
  }
  function l8Phi(x) { return 0.5 * l8erfc(-x / Math.SQRT2); }
  function l8npdf(x, m, s) { var z = (x - m) / s; return Math.exp(-0.5 * z * z) / (s * Math.sqrt(2 * Math.PI)); }
  // a Gaussian mixture {w, m, s}: density, CDF and quantiles (bisection)
  function l8mixPdf(mx, x) { var v = 0; for (var k = 0; k < mx.w.length; k++) v += mx.w[k] * l8npdf(x, mx.m[k], mx.s[k]); return v; }
  function l8mixCdf(mx, x) { var v = 0; for (var k = 0; k < mx.w.length; k++) v += mx.w[k] * l8Phi((x - mx.m[k]) / mx.s[k]); return v; }
  function l8mixQuant(mx, levels) {
    var out = new Float64Array(levels.length), lo0 = -40;
    for (var i = 0; i < levels.length; i++) {
      var lo = lo0, hi = 40, u = levels[i];
      for (var it = 0; it < 64; it++) { var mid = 0.5 * (lo + hi); if (l8mixCdf(mx, mid) < u) lo = mid; else hi = mid; }
      out[i] = 0.5 * (lo + hi); lo0 = lo - 1e-9;
    }
    return out;
  }
  // symmetric tridiagonal solve (Thomas): diag b, off-diagonal c (c[i] couples i and i+1), right-hand side d
  function l8tridiag(b, c, d) {
    var n = b.length, cp = new Float64Array(n), dp = new Float64Array(n), x = new Float64Array(n), i;
    cp[0] = c[0] / b[0]; dp[0] = d[0] / b[0];
    for (i = 1; i < n; i++) {
      var m = b[i] - c[i - 1] * cp[i - 1];
      cp[i] = i < n - 1 ? c[i] / m : 0; dp[i] = (d[i] - c[i - 1] * dp[i - 1]) / m;
    }
    x[n - 1] = dp[n - 1];
    for (i = n - 2; i >= 0; i--) x[i] = dp[i] - cp[i] * x[i + 1];
    return x;
  }
  function l8w2pts(a, b) { var s = 0; for (var i = 0; i < a.length; i++) s += (a[i] - b[i]) * (a[i] - b[i]); return Math.sqrt(s / a.length); }
  function l8levels(N) { var u = new Float64Array(N); for (var i = 0; i < N; i++) u[i] = (i + 0.5) / N; return u; }
  function l8sci(x, d) { return Math.abs(x) >= 0.01 || x === 0 ? fmt(x, d === undefined ? 4 : d) : x.toExponential(2); }

  /* --- 1. JKO steps against the exact flow, in quantile coordinates (§2) --- */
  // Particles x_1 < ... < x_N at the quantile levels (j - 1/2)/N. One JKO step of f = entropy (+ potential x^2/2)
  // minimises G(x) = sum (x_i - y_i)^2 / (2 tau) - sum log(x_{i+1} - x_i) (+ sum x_i^2 / 2): Newton, tridiagonal Hessian.
  function l8jkoStep(y, tau, fp) {
    var N = y.length, x = Float64Array.from(y), i, it;
    for (it = 0; it < 60; it++) {
      var g = new Float64Array(N), b = new Float64Array(N), c = new Float64Array(N);
      for (i = 0; i < N; i++) { g[i] = (x[i] - y[i]) / tau + (fp ? x[i] : 0); b[i] = 1 / tau + (fp ? 1 : 0); }
      for (i = 0; i < N - 1; i++) { var e = 1 / (x[i + 1] - x[i]); g[i] += e; g[i + 1] -= e; b[i] += e * e; b[i + 1] += e * e; c[i] = -e * e; }
      var p = l8tridiag(b, c, g), s = 1, dec = 0;
      for (i = 0; i < N; i++) dec += g[i] * p[i];
      for (var bt = 0; bt < 60; bt++) {
        var ok = true;
        for (i = 0; i < N - 1; i++) if (x[i + 1] - s * p[i + 1] <= x[i] - s * p[i]) { ok = false; break; }
        if (ok) break;
        s *= 0.5;
      }
      for (i = 0; i < N; i++) x[i] -= s * p[i];
      if (dec < 1e-20) break;
    }
    return x;
  }
  WIDGETS.l8jko = function (box) {
    var s = scaffold(box, "JKO steps (purple) against the exact gradient flow (green), with particles at the quantile levels");
    var top = new Plot(s.svg, { x: [-3.6, 3.6], y: [0, 1.05], w: 680, h: 250, pad: { l: 40, r: 16, t: 14, b: 28 }, label: "Densities: initial, exact flow at time t, JKO iterate" });
    var botSvg = addSvg(box, s.svg);
    var bot = new Plot(botSvg, { x: [0, 2], y: [-3.6, 3.6], w: 680, h: 250, pad: { l: 40, r: 16, t: 16, b: 34 }, label: "Quantile trajectories: exact flow and JKO iterates" });
    var enSel = select(s.controls, "Energy", [["heat", "entropy ∫ρ log ρ → heat equation"], ["fp", "KL(·|𝒩(0,1)) → Fokker–Planck"]], "heat", setup);
    var TAUS = [0.01, 0.025, 0.05, 0.1, 0.2, 0.25, 0.5];
    var tauS = slider(s.controls, "step τ", 0, TAUS.length - 1, 1, 4, setup);
    var tS = slider(s.controls, "time t", 0, 2, 0.01, 1, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "α₀ (two bumps)"], ["--s3", "exact flow αₜ"], ["--s5", "JKO iterate α⁽ˡ⁾, ℓτ ≤ t"], ["--s1", "target 𝒩(0,1) (Fokker–Planck)"]]);
    var MIX = { w: [0.6, 0.4], m: [-1.2, 1.0], s: [0.25, 0.35] }, N = 160, LEV = l8levels(N), T = 2;
    var x0 = l8mixQuant(MIX, LEV), iters = [], tau, fp, paths = [], PATH_IDX = [], PT = 81, i, k;
    for (i = 4; i < N; i += 10) PATH_IDX.push(i);
    function comps(t) {
      var m = [], sd = [];
      for (var j = 0; j < 2; j++) {
        if (fp) { var e = Math.exp(-t); m.push(MIX.m[j] * e); sd.push(Math.sqrt(MIX.s[j] * MIX.s[j] * e * e + 1 - e * e)); }
        else { m.push(MIX.m[j]); sd.push(Math.sqrt(MIX.s[j] * MIX.s[j] + 2 * t)); }
      }
      return { w: MIX.w, m: m, s: sd };
    }
    var explicitInfo = "";
    function setup() {
      fp = enSel.value === "fp"; tau = TAUS[Math.round(tauS.get())];
      tauS.out.textContent = fmt(tau, 3);
      iters = [x0];
      for (k = 1; k * tau <= T + 1e-9; k++) iters.push(l8jkoStep(iters[k - 1], tau, fp));
      // exact quantile trajectories of a few levels
      var lv = PATH_IDX.map(function (j) { return LEV[j]; });
      paths = PATH_IDX.map(function () { return []; });
      for (k = 0; k < PT; k++) {
        var t = T * k / (PT - 1), q = l8mixQuant(comps(t), lv);
        for (var j = 0; j < lv.length; j++) paths[j].push([t, q[j]]);
      }
      // explicit Euler of the same particle system, with the same step
      var x = Float64Array.from(x0), crossed = -1, K = Math.round(T / tau);
      for (k = 0; k < K; k++) {
        var v = new Float64Array(N);
        for (i = 0; i < N - 1; i++) { var e = 1 / (x[i + 1] - x[i]); v[i] -= e; v[i + 1] += e; }
        for (i = 0; i < N; i++) x[i] += tau * (v[i] - (fp ? x[i] : 0));
        var bad = false;
        for (i = 0; i < N - 1; i++) if (!(x[i + 1] > x[i])) { bad = true; break; }
        if (bad) { crossed = k + 1; break; }
      }
      var g0 = Infinity; for (i = 0; i < N - 1; i++) g0 = Math.min(g0, x0[i + 1] - x0[i]);
      explicitInfo = "explicit Euler of the same particles with this τ: " + (crossed > 0 ? "particles cross at step " + crossed + " (unstable)" : "stable up to t = 2") +
        "; stability needs τ ≲ ½·(smallest gap)² = " + (0.5 * g0 * g0).toExponential(1);
      draw();
    }
    function draw() {
      var t = tS.get(), l = Math.min(iters.length - 1, Math.floor(t / tau + 1e-9)), tl = l * tau;
      tS.out.textContent = fmt(t, 2);
      var ex = comps(t), exl = comps(tl), qex = l8mixQuant(exl, LEV);
      // top: densities
      top.clear();
      top.axes({ xticks: [-3, -2, -1, 0, 1, 2, 3], yticks: [], nogrid: true, noyaxis: true });
      top.clip();
      top.fn(function (x) { return l8mixPdf(MIX, x); }, "ln c2 thin dash", 400);
      if (fp) top.fn(function (x) { return l8npdf(x, 0, 1); }, "ln c1 thin dash", 300);
      var exPts = []; for (i = 0; i <= 400; i++) { var xx = -3.6 + 7.2 * i / 400; exPts.push([xx, l8mixPdf(ex, xx)]); }
      top.poly([[-3.6, 0]].concat(exPts, [[3.6, 0]]), "a3");
      top.poly(exPts, "ln c3");
      var X = iters[l], jk = [];
      for (i = 0; i < N - 1; i++) { var d = X[i + 1] - X[i], h = 1 / (N * d); jk.push([X[i], h]); jk.push([X[i + 1], h]); }
      top.poly(jk, "ln c5 thin");
      top.unclip();
      // bottom: quantile trajectories
      bot.clear();
      bot.axes({ xticks: [0, 0.5, 1, 1.5, 2], yticks: [-3, -2, -1, 0, 1, 2, 3], xfmt: function (v) { return fmt(v, 1); }, xlabel: "time t", ylabel: "position" });
      bot.clip();
      paths.forEach(function (p) { bot.poly(p, "ln c3 thin"); });
      for (k = 0; k < iters.length; k++) PATH_IDX.forEach(function (j) { bot.dot(k * tau, iters[k][j], 2.4, "f5"); });
      bot.seg(t, -3.6, t, 3.6, "ln cm thin dash");
      bot.unclip();
      var w0 = l8w2pts(x0, l8mixQuant(ex, LEV));
      ro.textContent = "τ = " + fmt(tau, 3) + "   JKO iterate ℓ = " + l + " (time ℓτ = " + fmt(tl, 3) + ")   W₂(JKO iterate, exact flow at ℓτ) = " + l8sci(l8w2pts(X, qex)) +
        "\ndistance travelled by the exact flow, W₂(α₀, αₜ) = " + fmt(w0, 3) + "\n" + explicitInfo;
    }
    setup(); redrawers.push(draw);
  };

  /* --- 2. Interacting particles in the plane: potential + interaction energies (§5) --- */
  // f(alpha) = 1/2 iint W(x - y) dalpha dalpha + int V dalpha; particles x_i' = -(1/n) sum_{j != i} grad W(x_i - x_j) - grad V(x_i).
  var L8_PRESETS = {
    attract: { label: "attraction W = ½|z|²", W: function (r2) { return 0.5 * r2; }, dW: function (r2) { return 1; } },
    coulomb: { label: "attraction + Coulomb repulsion W = ½|z|² − log|z|",
      W: function (r2) { return 0.5 * r2 - 0.5 * Math.log(r2 + 1e-4); }, dW: function (r2) { return 1 - 1 / (r2 + 1e-4); } },
    gauss: { label: "attraction + Gaussian repulsion W = ½|z|² + 3e^(−|z|²/0.18)",
      W: function (r2) { return 0.5 * r2 + 3 * Math.exp(-r2 / 0.18); }, dW: function (r2) { return 1 - (3 / 0.09) * Math.exp(-r2 / 0.18); } },
    ring: { label: "potential V = ¼(|x|² − 1)² + Gaussian repulsion", ext: true,
      W: function (r2) { return Math.exp(-r2 / 0.08); }, dW: function (r2) { return -(1 / 0.04) * Math.exp(-r2 / 0.08); } }
  };
  // grad of W(z) as a function of z is dW(|z|^2) * z (W radial)
  WIDGETS.l8particles = function (box) {
    var s = scaffold(box, "Interacting particles: each one moves with velocity −∇W averaged over the others (and −∇V)");
    var W = 680, H = 400;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Particles in the plane under an interaction energy, and the energy along the flow");
    var preSel = select(s.controls, "Energy", Object.keys(L8_PRESETS).map(function (k) { return [k, L8_PRESETS[k].label]; }), "coulomb", reset);
    var nSel = select(s.controls, "particles n", [["100", "100"], ["300", "300"], ["600", "600"]], "300", reset);
    var runBtn = button(s.controls, "Run", function () { running = !running; runBtn.textContent = running ? "Pause" : "Run"; if (running) loop(); });
    button(s.controls, "Reset", reset);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "initial particles"], ["--s3", "particles at time t"], ["--muted", "unit circle"]]);
    var X, X0, t, hist, running = false, n, P, dt = 0.01, seed = 5;
    var main = { x0: 10, y0: 10, w: 380, h: 380, r: 2.2 };
    function MX(x) { return main.x0 + (x + main.r) / (2 * main.r) * main.w; }
    function MY(y) { return main.y0 + (main.r - y) / (2 * main.r) * main.h; }
    function energy() {
      var e = 0, i, j;
      for (i = 0; i < n; i++) for (j = i + 1; j < n; j++) {
        var dx = X[i][0] - X[j][0], dy = X[i][1] - X[j][1]; e += P.W(dx * dx + dy * dy);
      }
      e /= n * n; // 1/2 * 2 * sum_{i<j} / n^2
      if (P.ext) for (i = 0; i < n; i++) { var q = X[i][0] * X[i][0] + X[i][1] * X[i][1] - 1; e += 0.25 * q * q / n; }
      return e;
    }
    function step() {
      var V = [], i, j;
      for (i = 0; i < n; i++) V.push([0, 0]);
      for (i = 0; i < n; i++) for (j = i + 1; j < n; j++) {
        var dx = X[i][0] - X[j][0], dy = X[i][1] - X[j][1], g = P.dW(dx * dx + dy * dy);
        V[i][0] -= g * dx; V[i][1] -= g * dy; V[j][0] += g * dx; V[j][1] += g * dy;
      }
      for (i = 0; i < n; i++) {
        var vx = V[i][0] / n, vy = V[i][1] / n;
        if (P.ext) { var q = X[i][0] * X[i][0] + X[i][1] * X[i][1] - 1; vx -= q * X[i][0]; vy -= q * X[i][1]; }
        X[i][0] += dt * vx; X[i][1] += dt * vy;
      }
      t += dt;
    }
    function reset() {
      running = false; runBtn.textContent = "Run";
      P = L8_PRESETS[preSel.value]; n = parseInt(nSel.value, 10);
      var rng = mulberry32(seed);
      X = []; for (var i = 0; i < n; i++) X.push([0.6 + 0.6 * gaussRand(rng), -0.3 + 0.6 * gaussRand(rng)]);
      X0 = X.map(function (p) { return p.slice(); });
      t = 0; hist = [[0, energy()]];
      draw();
    }
    function loop() {
      if (!running) return;
      var k = 0, budget = n > 400 ? 2 : 5;
      for (k = 0; k < budget; k++) step();
      hist.push([t, energy()]);
      draw();
      if (t >= 30) { running = false; runBtn.textContent = "Run"; return; }
      requestAnimationFrame(loop);
    }
    function draw() {
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg), i;
      el("rect", { x: main.x0, y: main.y0, width: main.w, height: main.h, "class": "ln cm hair nofill" }, g);
      var circ = []; for (i = 0; i <= 96; i++) { var a = 2 * Math.PI * i / 96; circ.push((i ? "L" : "M") + MX(Math.cos(a)).toFixed(1) + " " + MY(Math.sin(a)).toFixed(1)); }
      el("path", { d: circ.join(""), "class": "ln cm thin dash" }, g);
      X0.forEach(function (p) { el("circle", { cx: MX(p[0]), cy: MY(p[1]), r: 1.8, "class": "f2", "fill-opacity": 0.35 }, g); });
      var mx = 0, my = 0;
      X.forEach(function (p) { mx += p[0] / n; my += p[1] / n; });
      X.forEach(function (p) { if (Math.abs(p[0]) < main.r && Math.abs(p[1]) < main.r) el("circle", { cx: MX(p[0]), cy: MY(p[1]), r: 2.6, "class": "f3" }, g); });
      el("circle", { cx: MX(mx), cy: MY(my), r: 4, "class": "ln ck thin nofill" }, g);
      // energy along the flow
      var cx0 = 450, cy0 = 40, cw = 210, ch = 150, T = Math.max(2, t), lo = Infinity, hi = -Infinity;
      hist.forEach(function (h) { lo = Math.min(lo, h[1]); hi = Math.max(hi, h[1]); });
      if (hi - lo < 1e-9) hi = lo + 1;
      el("rect", { x: cx0, y: cy0, width: cw, height: ch, "class": "ln cm hair nofill" }, g);
      var d = hist.map(function (h, k) { return (k ? "L" : "M") + (cx0 + h[0] / T * cw).toFixed(1) + " " + (cy0 + ch - (h[1] - lo) / (hi - lo) * ch).toFixed(1); }).join("");
      el("path", { d: d, "class": "ln c3 thin" }, g);
      var cap = el("text", { x: cx0, y: cy0 - 10, "class": "tx-s" }, g); cap.textContent = "energy f(αₜ) along the flow (it can only decrease)";
      var t1 = el("text", { x: cx0 + cw, y: cy0 + ch + 14, "class": "tx-s", "text-anchor": "end" }, g); t1.textContent = "t = " + fmt(t, 2);
      var t2 = el("text", { x: cx0 - 4, y: cy0 + 8, "class": "tx-s", "text-anchor": "end" }, g); t2.textContent = fmt(hi, 2);
      var t3 = el("text", { x: cx0 - 4, y: cy0 + ch, "class": "tx-s", "text-anchor": "end" }, g); t3.textContent = fmt(lo, 2);
      // radial statistics around the mean
      var R = X.map(function (p) { return Math.hypot(p[0] - mx, p[1] - my); }), rmax = Math.max.apply(null, R);
      var f05 = R.filter(function (r) { return r < 0.5; }).length / n, f075 = R.filter(function (r) { return r < 0.75; }).length / n;
      var lines = ["t = " + fmt(t, 2) + "   f(αₜ) = " + fmt(hist[hist.length - 1][1], 4), "mean (black circle) = (" + fmt(mx, 3) + ", " + fmt(my, 3) + ")",
        "largest distance to the mean = " + fmt(rmax, 3), "fraction within 0.5 of the mean = " + fmt(f05, 3), "fraction within 0.75 of the mean = " + fmt(f075, 3)];
      lines.forEach(function (L, k) { var tt = el("text", { x: cx0, y: cy0 + ch + 40 + 17 * k, "class": "tx-s" }, g); tt.textContent = L; });
      ro.textContent = "explicit Euler steps of size " + dt + " on the n coupled ODEs ẋᵢ = −(1/n) Σⱼ ∇W(xᵢ − xⱼ)" + (P.ext ? " − ∇V(xᵢ)" : "") + ".  Press Run.";
    }
    reset();
    redrawers.push(draw);
  };
