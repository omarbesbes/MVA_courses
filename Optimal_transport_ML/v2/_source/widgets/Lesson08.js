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
    var enSel = select(s.controls, "Energy", [["heat", "entropy → heat"], ["fp", "KL to 𝒩(0,1) → Fokker–Planck"]], "heat", setup);
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
    attract: { label: "attraction", formula: "W = ½|z|²", W: function (r2) { return 0.5 * r2; }, dW: function (r2) { return 1; } },
    coulomb: { label: "attraction + Coulomb", formula: "W = ½|z|² − log|z|",
      W: function (r2) { return 0.5 * r2 - 0.5 * Math.log(r2 + 1e-4); }, dW: function (r2) { return 1 - 1 / (r2 + 1e-4); } },
    gauss: { label: "attraction + Gaussian", formula: "W = ½|z|² + 3 exp(−|z|²/0.18)",
      W: function (r2) { return 0.5 * r2 + 3 * Math.exp(-r2 / 0.18); }, dW: function (r2) { return 1 - (3 / 0.09) * Math.exp(-r2 / 0.18); } },
    ring: { label: "ring potential + repulsion", formula: "V = ¼(|x|² − 1)², W = exp(−|z|²/0.08)", ext: true,
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
      var cap = el("text", { x: cx0, y: cy0 - 10, "class": "tx-s" }, g); cap.textContent = "energy f(αₜ) along the flow (it decreases)";
      var t1 = el("text", { x: cx0 + cw, y: cy0 + ch + 14, "class": "tx-s", "text-anchor": "end" }, g); t1.textContent = "t = " + fmt(t, 2);
      var t2 = el("text", { x: cx0 - 4, y: cy0 + 8, "class": "tx-s", "text-anchor": "end" }, g); t2.textContent = fmt(hi, 2);
      var t3 = el("text", { x: cx0 - 4, y: cy0 + ch, "class": "tx-s", "text-anchor": "end" }, g); t3.textContent = fmt(lo, 2);
      // radial statistics around the mean
      var R = X.map(function (p) { return Math.hypot(p[0] - mx, p[1] - my); }), rmax = Math.max.apply(null, R);
      var f05 = R.filter(function (r) { return r < 0.5; }).length / n, f075 = R.filter(function (r) { return r < 0.75; }).length / n;
      var lines = ["t = " + fmt(t, 2) + "   f(αₜ) = " + fmt(hist[hist.length - 1][1], 4), "mean (black circle) = (" + fmt(mx, 3) + ", " + fmt(my, 3) + ")",
        "largest distance to the mean = " + fmt(rmax, 3), "fraction within 0.5 of the mean = " + fmt(f05, 3), "fraction within 0.75 of the mean = " + fmt(f075, 3)];
      lines.forEach(function (L, k) { var tt = el("text", { x: cx0, y: cy0 + ch + 40 + 17 * k, "class": "tx-s" }, g); tt.textContent = L; });
      ro.textContent = P.formula + ";  explicit Euler steps of size " + dt + " on the n coupled ODEs ẋᵢ = −(1/n) Σⱼ ∇W(xᵢ − xⱼ)" + (P.ext ? " − ∇V(xᵢ)" : "") + ".  Press Run.";
    }
    reset();
    redrawers.push(draw);
  };

  /* --- 3. Langevin particles against the Fokker–Planck density (§6) --- */
  function l8thomas(sub, diag, sup, d) { // general tridiagonal system: row i = sub[i] x[i-1] + diag[i] x[i] + sup[i] x[i+1]
    var n = diag.length, c = new Float64Array(n), e = new Float64Array(n), x = new Float64Array(n), i;
    c[0] = sup[0] / diag[0]; e[0] = d[0] / diag[0];
    for (i = 1; i < n; i++) { var m = diag[i] - sub[i] * c[i - 1]; c[i] = i < n - 1 ? sup[i] / m : 0; e[i] = (d[i] - sub[i] * e[i - 1]) / m; }
    x[n - 1] = e[n - 1];
    for (i = n - 2; i >= 0; i--) x[i] = e[i] - c[i] * x[i + 1];
    return x;
  }
  // Implicit finite volumes for d rho/dt = d/dx( e^{-V} d/dx( rho e^{V} ) ): zero flux at the ends, e^{-V} is exactly stationary.
  function L8FokkerPlanck(V, L, N, dt) {
    this.x = new Float64Array(N); this.dx = 2 * L / (N - 1); this.dt = dt;
    var i, dx2 = this.dx * this.dx;
    for (i = 0; i < N; i++) this.x[i] = -L + i * this.dx;
    var a = new Float64Array(N - 1), b = new Float64Array(N - 1);
    for (i = 0; i < N - 1; i++) {
      var vh = V(0.5 * (this.x[i] + this.x[i + 1]));
      a[i] = Math.exp(V(this.x[i]) - vh) / dx2; b[i] = Math.exp(V(this.x[i + 1]) - vh) / dx2;
    }
    this.sub = new Float64Array(N); this.diag = new Float64Array(N); this.sup = new Float64Array(N);
    for (i = 0; i < N; i++) {
      var dg = 0;
      if (i < N - 1) { dg += a[i]; this.sup[i] = -dt * b[i]; }
      if (i > 0) { dg += b[i - 1]; this.sub[i] = -dt * a[i - 1]; }
      this.diag[i] = 1 + dt * dg;
    }
  }
  L8FokkerPlanck.prototype.step = function (rho) { return l8thomas(this.sub, this.diag, this.sup, rho); };
  L8FokkerPlanck.prototype.quantiles = function (rho, levels) {
    var N = rho.length, c = new Float64Array(N), i, out = [];
    for (i = 1; i < N; i++) c[i] = c[i - 1] + 0.5 * (rho[i] + rho[i - 1]) * this.dx;
    var tot = c[N - 1], j = 0;
    levels.forEach(function (u) {
      var target = u * tot;
      while (j < N - 2 && c[j + 1] < target) j++;
      out.push(this.x[j] + (target - c[j]) / Math.max(c[j + 1] - c[j], 1e-300) * this.dx);
    }, this);
    return out;
  };
  WIDGETS.l8langevin = function (box) {
    var s = scaffold(box, "Langevin particles (purple) against the Fokker–Planck density (green): one curve of measures, two particle pictures");
    var T = 8;
    var top = new Plot(s.svg, { x: [-3.5, 3.5], y: [0, 0.8], w: 680, h: 240, pad: { l: 40, r: 16, t: 14, b: 28 }, label: "Histogram of the Langevin particles and the Fokker-Planck density" });
    var botSvg = addSvg(box, s.svg);
    var bot = new Plot(botSvg, { x: [0, T], y: [-3.5, 3.5], w: 680, h: 230, pad: { l: 40, r: 16, t: 16, b: 34 }, label: "Paths of Langevin particles and quantile curves of the density" });
    var tgtSel = select(s.controls, "Target", [["ou", "𝒩(0,1), from two bumps"], ["dw", "double well (x² − 1)²"]], "ou", reset);
    var hSel = select(s.controls, "Euler–Maruyama step h", [["0.01", "0.01"], ["0.05", "0.05"], ["0.1", "0.1"], ["0.2", "0.2"], ["0.4", "0.4"]], "0.1", reset);
    var runBtn = button(s.controls, "Run", function () { running = !running; runBtn.textContent = running ? "Pause" : "Run"; if (running) loop(); });
    button(s.controls, "Reset", reset);
    var ro = readout(s.controls);
    legend(s.legend, [["--s5", "Langevin particles (histogram, 6 paths)"], ["--s3", "Fokker–Planck density, its quantile curves"], ["--s1", "target e⁻ⱽ/Z"], ["--s2", "initial law"]]);
    var NP = 2000, X, rng, t, h, fpS, rho, rho0, Vf, Vp, paths, qpaths, running = false, seed = 21, LV = [0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9], dtp = 0.002;
    function reset() {
      running = false; runBtn.textContent = "Run";
      var ou = tgtSel.value === "ou", i;
      h = parseFloat(hSel.value);
      Vf = ou ? function (x) { return 0.5 * x * x; } : function (x) { var q = x * x - 1; return q * q; };
      Vp = ou ? function (x) { return x; } : function (x) { return 4 * x * (x * x - 1); };
      var init = ou ? { w: [0.5, 0.5], m: [-2, 2], s: [0.3, 0.3] } : { w: [1], m: [1.5], s: [0.25] };
      top.o.y = [0, ou ? 0.8 : 1.7];
      fpS = new L8FokkerPlanck(Vf, ou ? 4.5 : 2.6, ou ? 301 : 261, dtp);
      rho = new Float64Array(fpS.x.length);
      for (i = 0; i < rho.length; i++) rho[i] = l8mixPdf(init, fpS.x[i]);
      rho0 = Float64Array.from(rho);
      rng = mulberry32(seed);
      X = new Float64Array(NP);
      for (i = 0; i < NP; i++) {
        var u = rng(), k = 0, acc = init.w[0];
        while (u > acc && k < init.w.length - 1) { k++; acc += init.w[k]; }
        X[i] = init.m[k] + init.s[k] * gaussRand(rng);
      }
      t = 0;
      paths = []; for (i = 0; i < 6; i++) paths.push([[0, X[i * 37]]]);
      qpaths = LV.map(function () { return []; });
      var q = fpS.quantiles(rho, LV); q.forEach(function (v, j) { qpaths[j].push([0, v]); });
      draw();
    }
    function advance() {
      var i, sq = Math.sqrt(2 * h);
      for (i = 0; i < NP; i++) X[i] = X[i] - h * Vp(X[i]) + sq * gaussRand(rng);
      var tn = t + h, tp = t;
      while (tp < tn - 1e-12) { rho = fpS.step(rho); tp += dtp; }
      t = tn;
      for (i = 0; i < 6; i++) paths[i].push([t, X[i * 37]]);
      var q = fpS.quantiles(rho, LV); q.forEach(function (v, j) { qpaths[j].push([t, v]); });
    }
    function loop() {
      if (!running) return;
      var target = t + 0.05;
      while (t < target - 1e-12 && t < T) advance();
      draw();
      if (t >= T - 1e-9) { running = false; runBtn.textContent = "Run"; return; }
      requestAnimationFrame(loop);
    }
    function stats(arr) { var m = 0, v = 0, i; for (i = 0; i < arr.length; i++) m += arr[i]; m /= arr.length; for (i = 0; i < arr.length; i++) v += (arr[i] - m) * (arr[i] - m); return [m, v / arr.length]; }
    function draw() {
      var i, ou = tgtSel.value === "ou";
      top.clear();
      top.axes({ xticks: [-3, -2, -1, 0, 1, 2, 3], yticks: [], nogrid: true, noyaxis: true });
      top.clip();
      var nb = 70, bw = 7 / nb, cnt = new Float64Array(nb);
      for (i = 0; i < NP; i++) { var b = Math.floor((X[i] + 3.5) / bw); if (b >= 0 && b < nb) cnt[b]++; }
      for (i = 0; i < nb; i++) if (cnt[i] > 0) {
        var x0 = -3.5 + i * bw, hh = cnt[i] / (NP * bw);
        top.poly([[x0, 0], [x0, hh], [x0 + bw, hh], [x0 + bw, 0]], "a5");
      }
      var Z = 0, gpts = [], ipts = [], fpts = [];
      for (i = 0; i < fpS.x.length; i++) Z += Math.exp(-Vf(fpS.x[i])) * fpS.dx;
      for (i = 0; i < fpS.x.length; i++) { gpts.push([fpS.x[i], Math.exp(-Vf(fpS.x[i])) / Z]); ipts.push([fpS.x[i], rho0[i]]); fpts.push([fpS.x[i], rho[i]]); }
      top.poly(ipts, "ln c2 thin dash");
      top.poly(gpts, "ln c1 thin dash");
      top.poly(fpts, "ln c3");
      top.unclip();
      bot.clear();
      bot.axes({ xticks: [0, 2, 4, 6, 8], yticks: [-3, -2, -1, 0, 1, 2, 3], xlabel: "time t", ylabel: "position" });
      bot.clip();
      paths.forEach(function (p) { bot.poly(p, "ln c5 hair"); });
      qpaths.forEach(function (p) { bot.poly(p, "ln c3 thin"); });
      bot.seg(t, -3.5, t, 3.5, "ln cm thin dash");
      bot.unclip();
      var sp = stats(X), mf = 0, vf = 0, mass = 0, left = 0;
      for (i = 0; i < fpS.x.length; i++) { var w = rho[i] * fpS.dx; mass += w; mf += w * fpS.x[i]; if (fpS.x[i] < 0) left += w; }
      mf /= mass; for (i = 0; i < fpS.x.length; i++) vf += rho[i] * fpS.dx * (fpS.x[i] - mf) * (fpS.x[i] - mf); vf /= mass;
      var lp = 0; for (i = 0; i < NP; i++) if (X[i] < 0) lp++;
      ro.textContent = "t = " + fmt(t, 2) + "   particles: mean " + fmt(sp[0], 3) + ", variance " + fmt(sp[1], 3) + "   |   Fokker–Planck: mean " + fmt(mf, 3) + ", variance " + fmt(vf, 3) +
        (ou ? "\nEuler–Maruyama with step h is biased: its stationary variance for this target is 1/(1 − h/2) = " + fmt(1 / (1 - h / 2), 4) + " instead of 1"
            : "\nmass left of the barrier: particles " + fmt(lp / NP, 3) + ", Fokker–Planck " + fmt(left / mass, 3) + "  (equilibrium 0.5)") +
        "\n" + NP + " particles: Monte Carlo fluctuations of the order of 1/√" + NP + " ≈ " + fmt(1 / Math.sqrt(NP), 3);
    }
    reset();
    redrawers.push(draw);
  };

  /* --- 4. A two-layer ReLU network trained by gradient descent: neurons as particles (§10) --- */
  // Neuron x = (u, v), u in R^2 inner weights, v outer weight; network G(z) = (1/n) sum_i v_i relu(<u_i, z>);
  // risk f = 1/2 E (G(z) - y(z))^2 over m fixed inputs z ~ N(0, I); particle flow x_i' = -grad_W f(x_i) (explicit steps).
  WIDGETS.l8neurons = function (box) {
    var s = scaffold(box, "Training a two-layer ReLU network: each neuron is a particle, drawn at |v|·u (green: v > 0, purple: v < 0)");
    var W = 680, H = 360;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Neurons of a two-layer network moving in the plane, the risk along training and the optimality certificate");
    var initSel = select(s.controls, "Initialisation", [["spread", "spread: all directions"], ["point", "one point + small noise"]], "spread", reset);
    var runBtn = button(s.controls, "Run", function () { running = !running; runBtn.textContent = running ? "Pause" : "Run"; if (running) loop(); });
    button(s.controls, "Reset", reset);
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "neuron with v > 0"], ["--s5", "neuron with v < 0"], ["--s1", "teacher directions"], ["--muted", "risk, certificate g(θ)"]]);
    var M = 200, NN = 40, dt = 1.0, MAXSTEP = 3000, TA = [0.4, 2.4, 4.4], TV = [1, 1, -1];
    var rngD = mulberry32(77), Zx = new Float64Array(M), Zy = new Float64Array(M), Yt = new Float64Array(M), i, k;
    for (i = 0; i < M; i++) {
      Zx[i] = gaussRand(rngD); Zy[i] = gaussRand(rngD);
      var yy = 0; for (k = 0; k < 3; k++) yy += TV[k] * Math.max(0, Math.cos(TA[k]) * Zx[i] + Math.sin(TA[k]) * Zy[i]);
      Yt[i] = yy / 3;
    }
    var U, V, step, hist, trails, running = false, R = new Float64Array(M);
    function residual() {
      for (var a = 0; a < M; a++) {
        var g = 0;
        for (var j = 0; j < NN; j++) { var l = U[j][0] * Zx[a] + U[j][1] * Zy[a]; if (l > 0) g += V[j] * l; }
        R[a] = g / NN - Yt[a];
      }
    }
    function risk() { var e = 0; for (var a = 0; a < M; a++) e += R[a] * R[a]; return 0.5 * e / M; }
    function gradStep() {
      residual();
      for (var j = 0; j < NN; j++) {
        var gx = 0, gy = 0, gv = 0;
        for (var a = 0; a < M; a++) {
          var l = U[j][0] * Zx[a] + U[j][1] * Zy[a];
          if (l > 0) { gx += R[a] * Zx[a]; gy += R[a] * Zy[a]; gv += R[a] * l; }
        }
        U[j][0] -= dt * V[j] * gx / M; U[j][1] -= dt * V[j] * gy / M; V[j] -= dt * gv / M;
      }
      step++;
    }
    function certificate() { // g(theta) = E[(G - y) relu(<u_theta, z>)] on 180 directions
      var out = [];
      for (var q = 0; q < 180; q++) {
        var th = 2 * Math.PI * q / 180, c = Math.cos(th), sn = Math.sin(th), g = 0;
        for (var a = 0; a < M; a++) { var l = c * Zx[a] + sn * Zy[a]; if (l > 0) g += R[a] * l; }
        out.push([th, g / M]);
      }
      return out;
    }
    function reset() {
      running = false; runBtn.textContent = "Run";
      var r = mulberry32(initSel.value === "spread" ? 13 : 17);
      U = []; V = [];
      for (var j = 0; j < NN; j++) {
        if (initSel.value === "spread") { var a = 2 * Math.PI * r(); U.push([0.3 * Math.cos(a), 0.3 * Math.sin(a)]); V.push(0.3 * gaussRand(r)); }
        else { U.push([0.3 * Math.cos(1) + 0.01 * gaussRand(r), 0.3 * Math.sin(1) + 0.01 * gaussRand(r)]); V.push(0.35 + 0.01 * gaussRand(r)); }
      }
      step = 0; residual(); hist = [[0, risk()]];
      trails = U.map(function (u, j) { return [[Math.abs(V[j]) * u[0], Math.abs(V[j]) * u[1]]]; });
      draw();
    }
    function loop() {
      if (!running) return;
      for (var q = 0; q < 20 && step < MAXSTEP; q++) gradStep();
      residual(); hist.push([step, risk()]);
      U.forEach(function (u, j) { trails[j].push([Math.abs(V[j]) * u[0], Math.abs(V[j]) * u[1]]); });
      draw();
      if (step >= MAXSTEP) { running = false; runBtn.textContent = "Run"; return; }
      requestAnimationFrame(loop);
    }
    var P = { x0: 10, y0: 10, w: 340, h: 340, r: 2.2 };
    function PX(x) { return P.x0 + (x + P.r) / (2 * P.r) * P.w; }
    function PY(y) { return P.y0 + (P.r - y) / (2 * P.r) * P.h; }
    function draw() {
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg), j, q;
      var cp = el("clipPath", { id: "l8neurons-clip" }, s.svg);
      el("rect", { x: P.x0, y: P.y0, width: P.w, height: P.h }, cp);
      var gc = el("g", { "clip-path": "url(#l8neurons-clip)" }, s.svg);
      el("rect", { x: P.x0, y: P.y0, width: P.w, height: P.h, "class": "ln cm hair nofill" }, g);
      TA.forEach(function (a, k2) {
        el("line", { x1: PX(0), y1: PY(0), x2: PX(2.1 * Math.cos(a)), y2: PY(2.1 * Math.sin(a)), "class": "ln c1 thin dash" }, gc);
        var t = el("text", { x: PX(1.25 * Math.cos(a)) + 8, y: PY(1.25 * Math.sin(a)) - 4, "class": "tx-s t1" }, gc); t.textContent = TV[k2] > 0 ? "v* > 0" : "v* < 0";
      });
      trails.forEach(function (tr, j2) {
        var d = tr.map(function (p, q2) { return (q2 ? "L" : "M") + PX(p[0]).toFixed(1) + " " + PY(p[1]).toFixed(1); }).join("");
        el("path", { d: d, "class": "ln " + (V[j2] >= 0 ? "c3" : "c5") + " hair", "stroke-opacity": 0.45 }, gc);
      });
      for (j = 0; j < NN; j++) el("circle", { cx: PX(Math.abs(V[j]) * U[j][0]), cy: PY(Math.abs(V[j]) * U[j][1]), r: 3.4, "class": V[j] >= 0 ? "f3" : "f5" }, gc);
      el("circle", { cx: PX(0), cy: PY(0), r: 2, "class": "fm" }, gc);
      // risk (log scale)
      var cx0 = 420, cy0 = 26, cw = 240, ch = 120, lo = -8, hi = 0;
      function RX(st) { return cx0 + st / MAXSTEP * cw; }
      function RY(v) { return cy0 + ch - (Math.log10(Math.max(v, 1e-8)) - lo) / (hi - lo) * ch; }
      el("rect", { x: cx0, y: cy0, width: cw, height: ch, "class": "ln cm hair nofill" }, g);
      [0, -4, -8].forEach(function (e) {
        el("line", { x1: cx0, x2: cx0 + cw, y1: RY(Math.pow(10, e)), y2: RY(Math.pow(10, e)), "class": "gr" }, g);
        var tt = el("text", { x: cx0 - 4, y: RY(Math.pow(10, e)) + 4, "class": "tx-s", "text-anchor": "end" }, g); tt.textContent = e === 0 ? "1" : "1e" + e;
      });
      el("path", { d: hist.map(function (h, q2) { return (q2 ? "L" : "M") + RX(h[0]).toFixed(1) + " " + RY(h[1]).toFixed(1); }).join(""), "class": "ln c3 thin" }, g);
      var c1 = el("text", { x: cx0, y: cy0 - 8, "class": "tx-s" }, g); c1.textContent = "risk f(αₖ) (log scale) over " + MAXSTEP + " steps";
      // certificate g(theta)
      residual();
      var cert = certificate(), gmax = 0, thmax = 0;
      cert.forEach(function (c) { if (Math.abs(c[1]) > Math.abs(gmax)) { gmax = c[1]; thmax = c[0]; } });
      var dy0 = 210, dh = 110, sc = Math.max(0.02, Math.abs(gmax) * 1.1);
      function CX(th) { return cx0 + th / (2 * Math.PI) * cw; }
      function CY(v) { return dy0 + dh / 2 - v / sc * dh / 2; }
      el("rect", { x: cx0, y: dy0, width: cw, height: dh, "class": "ln cm hair nofill" }, g);
      el("line", { x1: cx0, x2: cx0 + cw, y1: CY(0), y2: CY(0), "class": "ax" }, g);
      TA.forEach(function (a) { el("line", { x1: CX(a), x2: CX(a), y1: dy0, y2: dy0 + dh, "class": "ln c1 hair dash" }, g); });
      el("path", { d: cert.map(function (c, q2) { return (q2 ? "L" : "M") + CX(c[0]).toFixed(1) + " " + CY(c[1]).toFixed(1); }).join(""), "class": "ln cm thin" }, g);
      var c2 = el("text", { x: cx0, y: dy0 - 8, "class": "tx-s" }, g); c2.textContent = "certificate g(θ), θ ∈ [0, 2π)";
      var c3 = el("text", { x: cx0 + cw, y: dy0 + dh + 14, "class": "tx-s", "text-anchor": "end" }, g); c3.textContent = "scale ±" + l8sci(sc, 3);
      var neg = 0; for (j = 0; j < NN; j++) if (V[j] < 0) neg++;
      ro.textContent = "step " + step + " (step size " + dt + ")   risk = " + l8sci(hist[hist.length - 1][1]) + "   neurons with v < 0: " + neg + " of " + NN +
        "\nlargest |g(θ)| = " + l8sci(Math.abs(gmax)) + " at θ = " + fmt(thmax, 2) + " rad (teacher directions: 0.4, 2.4, 4.4)" +
        "\nglobal optimality certificate: g ≡ 0 on the circle. A nonzero g(θ) means that a new neuron in direction θ, with outer weight of sign −g(θ), would lower the risk.";
    }
    reset();
    redrawers.push(draw);
  };

  /* --- 5. Tokens on the circle under self-attention: clusters, then consensus (§11) --- */
  // theta_i' = sum_j w_ij sin(theta_j - theta_i), w_ij = softmax_j( cos(theta_j - theta_i) / eps ): normalised attention
  // (Q = K = V = Id) projected on the circle, i.e. mean shift with the Gaussian kernel exp(-|x - y|^2 / (2 eps)).
  function l8clusters(th, tol) { // number of groups of angles on the circle (single linkage, gap > tol)
    var a = Array.prototype.slice.call(th).map(function (v) { v = v % (2 * Math.PI); return v < 0 ? v + 2 * Math.PI : v; }).sort(function (x, y) { return x - y; });
    var n = a.length, gaps = 0;
    for (var i = 0; i < n; i++) { var g = (i < n - 1 ? a[i + 1] - a[i] : a[0] + 2 * Math.PI - a[n - 1]); if (g > tol) gaps++; }
    return Math.max(1, gaps);
  }
  WIDGETS.l8tokens = function (box) {
    var s = scaffold(box, "Tokens on the circle moved by attention: fast clustering, very slow merging (time on a log scale)");
    var W = 680, H = 330;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Tokens on a circle and the space-time plot of their angles under attention dynamics");
    var epsSel = select(s.controls, "temperature ε", [["1", "1"], ["0.5", "0.5"], ["0.25", "0.25"], ["0.1", "0.1"], ["0.05", "0.05"]], "0.1", reset);
    var nSel = select(s.controls, "tokens n", [["16", "16"], ["32", "32"], ["64", "64"]], "32", reset);
    var runBtn = button(s.controls, "Run", function () { running = !running; runBtn.textContent = running ? "Pause" : "Run"; if (running) loop(); });
    button(s.controls, "Reset", reset);
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "tokens"], ["--s2", "initial tokens"], ["--muted", "number of clusters (right panel, top)"]]);
    var th, th0, t, eps, n, hist, events, running = false, TMAX = 1e4, LT0 = -2, LT1 = 4;
    function speeds() {
      var v = new Float64Array(n), i, j;
      for (i = 0; i < n; i++) {
        var num = 0, den = 0;
        for (j = 0; j < n; j++) { var d = th[j] - th[i], w = Math.exp((Math.cos(d) - 1) / eps); num += w * Math.sin(d); den += w; }
        v[i] = num / den;
      }
      return v;
    }
    function reset() {
      running = false; runBtn.textContent = "Run";
      eps = parseFloat(epsSel.value); n = parseInt(nSel.value, 10);
      var r = mulberry32(31);
      th = new Float64Array(n); for (var i = 0; i < n; i++) th[i] = 2 * Math.PI * r();
      th0 = Float64Array.from(th); t = 0;
      hist = [[0.01, Float64Array.from(th)]]; events = [[0, l8clusters(th, 0.05)]];
      draw();
    }
    function loop() {
      if (!running) return;
      var target = Math.min(TMAX, Math.max(t * 1.06, t + 0.02));
      while (t < target) {
        var v = speeds(), vm = 0, i;
        for (i = 0; i < n; i++) vm = Math.max(vm, Math.abs(v[i]));
        var dt = Math.min(0.5, 0.02 / Math.max(vm, 1e-12), target - t);
        for (i = 0; i < n; i++) th[i] += dt * v[i];
        t += dt;
      }
      hist.push([Math.max(t, 0.01), Float64Array.from(th)]);
      var c = l8clusters(th, 0.05);
      if (c !== events[events.length - 1][1]) events.push([t, c]);
      draw();
      if (t >= TMAX - 1e-9) { running = false; runBtn.textContent = "Run"; return; }
      requestAnimationFrame(loop);
    }
    var C = { cx: 150, cy: 160, r: 120 };
    function draw() {
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg), i;
      el("circle", { cx: C.cx, cy: C.cy, r: C.r, "class": "ln cm thin nofill" }, g);
      for (i = 0; i < n; i++) el("circle", { cx: C.cx + C.r * Math.cos(th0[i]), cy: C.cy - C.r * Math.sin(th0[i]), r: 3, "class": "f2", "fill-opacity": 0.45 }, g);
      for (i = 0; i < n; i++) el("circle", { cx: C.cx + (C.r - 12) * Math.cos(th[i]), cy: C.cy - (C.r - 12) * Math.sin(th[i]), r: 4, "class": "f3" }, g);
      var lab = el("text", { x: C.cx, y: C.cy + 4, "class": "tx-s", "text-anchor": "middle" }, g); lab.textContent = "t = " + (t < 10 ? fmt(t, 2) : t.toExponential(2));
      // space-time plot: angle (unwrapped to [0, 2pi)) against log10 t
      var x0 = 330, y0 = 40, w = 330, h = 250;
      function TX(tt) { return x0 + (Math.log10(Math.max(tt, 1e-2)) - LT0) / (LT1 - LT0) * w; }
      function AY(a) { a = a % (2 * Math.PI); if (a < 0) a += 2 * Math.PI; return y0 + h - a / (2 * Math.PI) * h; }
      el("rect", { x: x0, y: y0, width: w, height: h, "class": "ln cm hair nofill" }, g);
      for (var e = LT0; e <= LT1; e++) {
        el("line", { x1: TX(Math.pow(10, e)), x2: TX(Math.pow(10, e)), y1: y0, y2: y0 + h, "class": "gr" }, g);
        var tl = el("text", { x: TX(Math.pow(10, e)), y: y0 + h + 14, "class": "tx-s", "text-anchor": "middle" }, g); tl.textContent = e === 0 ? "1" : "10" + (e < 0 ? "⁻" : "") + "⁰¹²³⁴"[Math.abs(e)];
      }
      var xl = el("text", { x: x0 + w, y: y0 + h + 28, "class": "tx-s", "text-anchor": "end" }, g); xl.textContent = "time t (log scale)";
      var yl = el("text", { x: x0, y: y0 - 6, "class": "tx-s" }, g); yl.textContent = "angle of each token (0 to 2π)";
      for (i = 0; i < n; i++) {
        var d = "", prev = null;
        hist.forEach(function (hh) {
          var a = hh[1][i] % (2 * Math.PI); if (a < 0) a += 2 * Math.PI;
          var X = TX(hh[0]), Y = AY(a);
          d += (prev !== null && Math.abs(a - prev) < Math.PI ? "L" : "M") + X.toFixed(1) + " " + Y.toFixed(1); prev = a;
        });
        el("path", { d: d, "class": "ln c3 hair" }, g);
      }
      events.forEach(function (ev) {
        if (ev[0] <= 0) return;
        var X = TX(ev[0]);
        el("line", { x1: X, x2: X, y1: y0, y2: y0 + 10, "class": "ln cm thin" }, g);
        var tt = el("text", { x: X, y: y0 + 22, "class": "tx-s", "text-anchor": "middle" }, g); tt.textContent = ev[1];
      });
      var cnow = l8clusters(th, 0.05);
      ro.textContent = "ε = " + eps + ", n = " + n + "   t = " + (t < 10 ? fmt(t, 2) : t.toExponential(2)) + "   clusters (gaps > 0.05 rad): " + cnow +
        "\nchanges of the number of clusters at t ≈ " + events.slice(1).map(function (ev) { return (ev[0] < 10 ? fmt(ev[0], 2) : ev[0].toExponential(1)) + " → " + ev[1]; }).join(",  ");
    }
    reset();
    redrawers.push(draw);
  };
