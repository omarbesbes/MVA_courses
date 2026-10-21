// widgets/Reminders.js — interactive figures of the Reminders page.
// Inserted by build.mjs inside the scope of app.js: it uses el, fmt, Plot, scaffold, slider, select, button,
// readout, legend, addSvg, mulberry32 and redrawers, and registers its widgets in WIDGETS. Own helpers are prefixed "rem".

  /* ---------------- small numerical helpers ---------------- */
  function remErf(x) { // Abramowitz-Stegun 7.1.26, absolute error < 1.5e-7
    var s = x < 0 ? -1 : 1, a = Math.abs(x), t = 1 / (1 + 0.3275911 * a);
    var y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-a * a);
    return s * y;
  }
  function remPhi(z) { return 0.5 * (1 + remErf(z / Math.SQRT2)); }
  function remBisect(C, t, lo, hi) { // smallest x with C(x) >= t, C non-decreasing
    for (var k = 0; k < 64; k++) { var m = 0.5 * (lo + hi); if (C(m) >= t) hi = m; else lo = m; }
    return hi;
  }

  /* --- 1. CDF and quantile function: generalized inverse and inverse-transform sampling (§2) --- */
  var REM_EMP = [-1.2, -0.3, 0.4, 0.9, 2.1];
  var REM_LAWS = {
    mixed: {
      label: "¼δ₀ + ½𝒰[1,2] + ¼δ₃", L: -0.8, R: 3.8, lx: 0, xt: [0, 1, 2, 3],
      atoms: [[0, 0.25], [3, 0.25]], qjumps: [0.25, 0.75],
      C: function (x) { var v = 0; if (x >= 0) v += 0.25; if (x >= 1) v += 0.5 * Math.min(1, x - 1); if (x >= 3) v += 0.25; return v; },
      Q: function (t) { return t <= 0.25 ? 0 : (t <= 0.75 ? 1 + 2 * (t - 0.25) : 3); }
    },
    gmix: {
      label: "0.3 𝒩(−1.5, 0.5²) + 0.7 𝒩(1, 0.8²)", L: -3.5, R: 4, xt: [-3, -2, -1, 0, 1, 2, 3, 4],
      atoms: [], qjumps: [],
      C: function (x) { return 0.3 * remPhi((x + 1.5) / 0.5) + 0.7 * remPhi((x - 1) / 0.8); },
      Q: null
    },
    emp: {
      label: "empirical measure of 5 points", L: -2, R: 3, xt: [-2, -1, 0, 1, 2, 3],
      atoms: REM_EMP.map(function (x) { return [x, 0.2]; }), qjumps: [0.2, 0.4, 0.6, 0.8],
      C: function (x) { var k = 0; for (var i = 0; i < 5; i++) if (REM_EMP[i] <= x) k++; return k / 5; },
      Q: function (t) { return REM_EMP[Math.min(4, Math.max(0, Math.ceil(5 * t - 1e-9) - 1))]; }
    },
    expo: {
      label: "exponential law, density e⁻ˣ on [0, ∞)", L: -0.5, R: 5, lx: 0, xt: [0, 1, 2, 3, 4, 5],
      atoms: [], qjumps: [],
      C: function (x) { return x < 0 ? 0 : 1 - Math.exp(-x); },
      Q: function (t) { return -Math.log(1 - t); }
    }
  };
  REM_LAWS.gmix.Q = function (t) { return remBisect(REM_LAWS.gmix.C, t, -12, 12); };

  WIDGETS.remQuantile = function (box) {
    var s = scaffold(box, "CDF and quantile function: the generalized inverse, and sampling by C⁻¹(U)");
    var top = new Plot(s.svg, { x: [-0.8, 3.8], y: [-0.22, 1.08], w: 680, h: 250, pad: { l: 44, r: 16, t: 16, b: 30 }, label: "Cumulative distribution function with a level line" });
    var botSvg = addSvg(box, s.svg);
    var bot = new Plot(botSvg, { x: [0, 1], y: [-0.8, 3.8], w: 680, h: 230, pad: { l: 44, r: 16, t: 14, b: 30 }, label: "Quantile function" });
    var lawSel = select(s.controls, "Measure", [["mixed", "worked example"], ["gmix", "Gaussian mixture"], ["emp", "5 points"], ["expo", "exponential"]], "mixed", function () { samples = []; draw(); });
    var tS = slider(s.controls, "level t", 0.01, 0.99, 0.01, 0.4, draw);
    button(s.controls, "Draw 40 samples C⁻¹(U)", function () {
      samples = [];
      for (var i = 0; i < 40; i++) samples.push(rng());
      draw();
    });
    button(s.controls, "Clear samples", function () { samples = []; draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "C (top) and C⁻¹ (bottom)"], ["--s3", "the level t and C⁻¹(t)"], ["--muted", "uniform levels U and the samples C⁻¹(U)"]]);
    var rng = mulberry32(2026), samples = [];

    function draw() {
      var D = REM_LAWS[lawSel.value], t = tS.get(), i, k;
      tS.out.textContent = fmt(t, 2);
      var q = D.Q(t);
      // ---- top: the CDF
      top.o.x = [D.L, D.R];
      top.clear();
      top.axes({ xticks: D.xt, yticks: [0, 0.25, 0.5, 0.75, 1], yfmt: function (v) { return fmt(v, 2); }, cross: true });
      var cuts = [D.L].concat(D.atoms.map(function (a) { return a[0]; }), [D.R]);
      for (k = 0; k + 1 < cuts.length; k++) {
        var a = cuts[k], b = cuts[k + 1], pts = [];
        for (i = 0; i <= 200; i++) { var x = a + (b - a) * i / 200; pts.push([x, D.C(i === 200 ? b - 1e-9 : x)]); }
        top.poly(pts, "ln c2");
      }
      D.atoms.forEach(function (at) {
        var hi = D.C(at[0]), lo = hi - at[1];
        top.seg(at[0], lo, at[0], hi, "ln c2 hair", { "stroke-dasharray": "2 3" });
        top.dot(at[0], lo, 4, "fs ln c2 thin");
        top.dot(at[0], hi, 4, "f2");
      });
      // samples: horizontal level u, then down to C^{-1}(u)
      var counts = {};
      samples.forEach(function (u) {
        var x = D.Q(u), key = x.toFixed(6);
        counts[key] = (counts[key] || 0) + 1;
        top.seg(D.L, u, x, u, "ln cm hair", { "stroke-opacity": 0.45 });
        top.seg(x, u, x, -0.04, "ln cm hair", { "stroke-opacity": 0.3 });
        var stack = D.atoms.length ? counts[key] - 1 : 0;
        top.dot(x, -0.06 - 0.016 * Math.min(stack, 9), 2.6, "fm");
      });
      // the level t
      top.seg(D.L, t, q, t, "ln c3 thin dash");
      top.seg(q, t, q, 0, "ln c3 thin dash");
      top.dot(q, t, 5, "f3");
      top.text(q, 0, "C⁻¹(t) = " + fmt(q, 2), "tx-s t3", "start", 4, -6);
      top.text(D.L, t, "t", "tx-s t3", "start", 4, -5);
      top.text(D.lx != null ? D.lx : D.L, 1.08, "α = " + D.label, "tx-s t2", "start", 6, 10);
      // ---- bottom: the quantile function
      var lo = Infinity, hi = -Infinity;
      for (i = 1; i < 200; i++) { var v = D.Q(i / 200); lo = Math.min(lo, v); hi = Math.max(hi, v); }
      bot.o.y = [Math.min(lo, D.L), Math.max(hi, D.R)];
      bot.clear();
      bot.axes({ xticks: [0, 0.25, 0.5, 0.75, 1], yticks: D.xt.filter(function (v) { return v >= bot.o.y[0] && v <= bot.o.y[1]; }), xfmt: function (v) { return fmt(v, 2); }, cross: true });
      bot.clip();
      var tc = [0.0015].concat(D.qjumps, [0.9985]);
      for (k = 0; k + 1 < tc.length; k++) {
        var p = [], ta = tc[k], tb = tc[k + 1];
        for (i = 0; i <= 200; i++) { var tt = ta + (tb - ta) * i / 200; p.push([tt, D.Q(i === 0 ? tt + 1e-9 : tt)]); }
        bot.poly(p, "ln c2");
      }
      bot.unclip();
      D.qjumps.forEach(function (tj) {
        var below = D.Q(tj), above = D.Q(tj + 1e-9);
        bot.seg(tj, below, tj, above, "ln c2 hair", { "stroke-dasharray": "2 3" });
        bot.dot(tj, below, 4, "f2");
        bot.dot(tj, above, 4, "fs ln c2 thin");
      });
      bot.seg(t, bot.o.y[0], t, q, "ln c3 thin dash");
      bot.seg(0, q, t, q, "ln c3 thin dash");
      bot.dot(t, q, 5, "f3");
      // ---- readout
      var Cq = D.C(q), txt = "t = " + fmt(t, 2) + "   C⁻¹(t) = " + fmt(q, 3) + "  (the smallest x with C(x) ≥ t)   C(C⁻¹(t)) = " + fmt(Cq, 3);
      if (Cq > t + 1e-6) txt += "\n" + "C(C⁻¹(t)) > t: the level t falls inside a jump of C, i.e. inside an atom (all levels of the jump give the same point).";
      else if (D.qjumps.length) txt += "\n" + "Atoms of α ↔ flat pieces of C⁻¹;  gaps of the support (flat pieces of C) ↔ jumps of C⁻¹.";
      else txt += "\n" + "Here C is continuous and increasing on the support: C⁻¹ is the ordinary inverse function.";
      if (samples.length) {
        if (D.atoms.length) {
          var parts = D.atoms.map(function (at) {
            var n = samples.filter(function (u) { return Math.abs(D.Q(u) - at[0]) < 1e-9; }).length;
            return "at " + fmt(at[0], 1) + ": " + n + "/" + samples.length;
          });
          txt += "\n" + samples.length + " samples C⁻¹(Uᵢ), Uᵢ uniform: " + parts.join(",  ") + "   (expected fraction: the mass of each atom)";
        } else {
          var m = samples.reduce(function (acc, u) { return acc + D.Q(u); }, 0) / samples.length;
          txt += "\n" + samples.length + " samples C⁻¹(Uᵢ): they pile up where C is steep (high density). Sample mean " + fmt(m, 3) + ".";
        }
      }
      ro.textContent = txt;
    }
    draw(); redrawers.push(draw);
  };

  /* --- 2. The Legendre–Fenchel transform as a family of supporting lines (§5) --- */
  var REM_XG = (function () { var a = []; for (var i = 0; i <= 6000; i++) a.push(-3 + i / 1000); return a; })();
  function remWell(x) { var u = x * x - 1; return u * u; }
  function remWellConj(y) { // max over the grid of (xy - f(x)), with all maximizers
    var best = -Infinity, arg = [];
    for (var i = 0; i < REM_XG.length; i++) {
      var x = REM_XG[i], v = x * y - remWell(x);
      if (v > best + 1e-9) { best = v; arg = [x]; } else if (v > best - 1e-9) arg.push(x);
    }
    return { v: best, x: arg.filter(function (z, j) { return j === 0 || z - arg[j - 1] > 0.05; }) };
  }
  var REM_FUNS = {
    quad: { label: "f(x) = x²/2", f: function (x) { return x * x / 2; },
      conj: function (y) { return { v: y * y / 2, x: [y] }; }, fsLabel: "f*(y) = y²/2: self-conjugate" },
    exp: { label: "f(x) = eˣ", f: Math.exp,
      conj: function (y) {
        if (y < 0) return { v: Infinity, x: [], why: "a line of negative slope goes to +∞ as x → −∞ while eˣ → 0: it cannot stay below the graph" };
        if (y === 0) return { v: 0, x: [], why: "the horizontal line at height 0 stays below eˣ but touches it only at x = −∞" };
        return { v: y * Math.log(y) - y, x: [Math.log(y)] };
      }, fsLabel: "f*(y) = y log y − y (y > 0), f*(0) = 0, +∞ for y < 0" },
    abs: { label: "f(x) = |x|", f: Math.abs,
      conj: function (y) {
        if (Math.abs(y) > 1 + 1e-12) return { v: Infinity, x: [], why: "a line steeper than |x| eventually crosses it" };
        if (Math.abs(y) > 1 - 1e-12) return { v: 0, x: [0], why: "slope ±1: the line touches along a whole half-line" };
        return { v: 0, x: [0] };
      }, fsLabel: "f*(y) = 0 on [−1, 1], +∞ outside (an indicator)" },
    quart: { label: "f(x) = x⁴/4", f: function (x) { return x * x * x * x / 4; },
      conj: function (y) { var x = Math.sign(y) * Math.pow(Math.abs(y), 1 / 3); return { v: 0.75 * Math.pow(Math.abs(y), 4 / 3), x: [x] }; },
      fsLabel: "f*(y) = ¾ |y| ∛|y|  (the pair p = 4, q = 4/3 of the table: 1/p + 1/q = 1)" },
    well: { label: "f(x) = (x² − 1)²  (not convex)", f: remWell, conj: remWellConj,
      env: function (x) { return Math.abs(x) <= 1 ? 0 : remWell(x); }, fsLabel: "f* computed numerically; f** = convex envelope (dashed)" }
  };

  WIDGETS.remLegendre = function (box) {
    var s = scaffold(box, "The Legendre transform: for each slope y, the highest line of slope y below the graph");
    var left = new Plot(s.svg, { x: [-3, 3], y: [-2.2, 4.6], w: 680, h: 300, pad: { l: 40, r: 16, t: 14, b: 28 }, label: "A function and its supporting line of slope y" });
    var rSvg = addSvg(box, s.svg);
    var right = new Plot(rSvg, { x: [-2.5, 2.5], y: [-1.6, 4.2], w: 680, h: 220, pad: { l: 40, r: 16, t: 14, b: 28 }, label: "The conjugate function" });
    var fSel = select(s.controls, "Function", [["quad", "x²/2"], ["exp", "eˣ"], ["abs", "|x|"], ["quart", "x⁴/4"], ["well", "(x² − 1)², not convex"]], "exp", draw);
    var yS = slider(s.controls, "slope y", -2.5, 2.5, 0.05, 1.5, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "f (top)"], ["--s3", "highest line of slope y below f; dot: contact point"], ["--muted", "the line y·x through 0"], ["--text", "f* (bottom)"]]);

    function draw() {
      var F = REM_FUNS[fSel.value], y = Math.round(yS.get() * 100) / 100, c = F.conj(y), i;
      yS.out.textContent = fmt(y, 2);
      left.clear();
      left.axes({ xticks: [-3, -2, -1, 0, 1, 2, 3], yticks: [-2, -1, 0, 1, 2, 3, 4], cross: true });
      left.clip();
      if (F.env) left.fn(F.env, "ln c3 thin dash", 600);
      left.fn(F.f, "ln c1", 600);
      left.fn(function (x) { return y * x; }, "ln cm hair", 2);
      if (isFinite(c.v)) {
        left.fn(function (x) { return y * x - c.v; }, "ln c3", 2);
        left.dot(0, -c.v, 4.5, "fs ln c3 thin");
        c.x.forEach(function (xs) { left.dot(xs, F.f(xs), 5, "f3"); });
      }
      left.unclip();
      left.text(-2.95, 4.25, F.label, "tx-b t1", "start");
      // the conjugate
      right.clear();
      right.axes({ xticks: [-2, -1, 0, 1, 2], yticks: [-1, 0, 1, 2, 3, 4], cross: true });
      right.clip();
      right.fn(function (u) { return F.conj(Math.round(u * 1000) / 1000).v; }, "ln ck", 500);
      right.unclip();
      if (fSel.value === "abs") {
        [-1, 1].forEach(function (b) { right.seg(b, 0, b, 4.2, "ln ck thin", { "stroke-dasharray": "2 3" }); });
        right.text(1.05, 3.6, "+∞ outside [−1, 1]", "tx-s", "start");
      }
      if (fSel.value === "exp") right.text(-2.45, 3.6, "+∞ for y < 0", "tx-s", "start");
      if (isFinite(c.v)) right.dot(y, c.v, 5, "f3");
      right.text(-2.45, -1.35, F.fsLabel, "tx-s", "start");
      // readout
      var txt = "slope y = " + fmt(y, 2) + "    f*(y) = sup over x of (x·y − f(x)) = ";
      if (!isFinite(c.v)) txt += "+∞: " + c.why + ".";
      else {
        txt += fmt(c.v, 3);
        if (c.x.length) {
          var xs = c.x[0];
          txt += "   attained at x* = " + c.x.map(function (z) { return fmt(z, 3); }).join(" and ") +
            "\nsupporting line ℓ(x) = " + fmt(y, 2) + "·x " + (c.v <= 0 ? "+ " : "− ") + fmt(Math.abs(c.v), 3) + "  (intercept −f*(y), open dot)" +
            "\nFenchel–Young: f(x*) + f*(y) = " + fmt(F.f(xs) + c.v, 3) + " = x*·y = " + fmt(xs * y, 3) + "  (equality exactly at contact points)";
          if (c.why) txt += "\n" + c.why + ".";
        } else txt += "\n" + c.why + ".";
        if (F.env && c.x.length > 1) txt += "\nTwo contact points: the line bridges the non-convex part; f** (dashed) follows this bridge.";
        else if (F.env) txt += "\nf is not convex: f** (dashed) is its convex envelope, and f*** = f*. The lines only see f**.";
      }
      ro.textContent = txt;
    }
    draw(); redrawers.push(draw);
  };
