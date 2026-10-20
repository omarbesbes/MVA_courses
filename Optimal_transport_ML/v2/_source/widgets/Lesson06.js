// widgets/Lesson06.js — interactive figures of Lesson 6 (dynamic OT, flow matching, diffusion models).
// Inserted by build.mjs inside the scope of app.js: it uses el, fmt, scaffold, slider, select, button, checkbox,
// readout, legend, mulberry32, gaussRand, hungarian, MQ, US, densityFromQ, msqrt, mmul, minv, msym, redrawers,
// and registers its widgets in WIDGETS. Its own helpers are prefixed l6.

  /* ---------------- helpers of this page ---------------- */
  // A panel inside an SVG: data coordinates -> viewBox coordinates, and a few drawing primitives.
  function l6panel(g, box, xr, yr) {
    var P = { g: g, x0: box[0], y0: box[1], w: box[2], h: box[3], xr: xr, yr: yr };
    P.X = function (x) { return P.x0 + (x - P.xr[0]) / (P.xr[1] - P.xr[0]) * P.w; };
    P.Y = function (y) { return P.y0 + P.h - (y - P.yr[0]) / (P.yr[1] - P.yr[0]) * P.h; };
    P.path = function (pts, cls, extra) {
      var d = "", pen = false;
      pts.forEach(function (p) {
        if (!p || !isFinite(p[0]) || !isFinite(p[1])) { pen = false; return; }
        d += (pen ? "L" : "M") + P.X(p[0]).toFixed(1) + " " + P.Y(p[1]).toFixed(1); pen = true;
      });
      var a = { d: d, "class": cls }; for (var k in extra || {}) a[k] = extra[k];
      return el("path", a, P.g);
    };
    P.area = function (pts, cls) {
      var q = pts.filter(function (p) { return p && isFinite(p[1]); });
      if (!q.length) return null;
      return P.path([[q[0][0], P.yr[0]]].concat(q, [[q[q.length - 1][0], P.yr[0]]]), cls);
    };
    P.line = function (x1, y1, x2, y2, cls, extra) {
      var a = { x1: P.X(x1).toFixed(1), y1: P.Y(y1).toFixed(1), x2: P.X(x2).toFixed(1), y2: P.Y(y2).toFixed(1), "class": cls };
      for (var k in extra || {}) a[k] = extra[k];
      return el("line", a, P.g);
    };
    P.circle = function (x, y, r, cls, extra) {
      var a = { cx: P.X(x).toFixed(1), cy: P.Y(y).toFixed(1), r: r, "class": cls };
      for (var k in extra || {}) a[k] = extra[k];
      return el("circle", a, P.g);
    };
    P.text = function (x, y, s, cls, anchor, dx, dy) {
      var t = el("text", { x: (P.X(x) + (dx || 0)).toFixed(1), y: (P.Y(y) + (dy || 0)).toFixed(1), "class": cls || "tx-s", "text-anchor": anchor || "start" }, P.g);
      t.textContent = s; return t;
    };
    P.frame = function (cls) { return el("rect", { x: P.x0, y: P.y0, width: P.w, height: P.h, "class": cls || "ln cm hair nofill" }, P.g); };
    P.xticks = function (vals, fmtf, dy) {
      vals.forEach(function (v) { P.text(v, P.yr[0], fmtf ? fmtf(v) : String(v), "tx-s", "middle", 0, dy || 14); });
    };
    P.yticks = function (vals, fmtf) {
      vals.forEach(function (v) { P.text(P.xr[0], v, fmtf ? fmtf(v) : String(v), "tx-s", "end", -5, 4); });
    };
    return P;
  }
  // An arrow-head marker (fill class f3, theme-aware) in the defs of an SVG; returns its id.
  function l6marker(svg, cls) {
    var id = "l6m" + Math.random().toString(36).slice(2);
    var defs = el("defs", {}, svg);
    var m = el("marker", { id: id, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 6, markerHeight: 6, orient: "auto-start-reverse" }, defs);
    el("path", { d: "M0,0 L10,5 L0,10 z", "class": cls || "f3" }, m);
    return id;
  }
  function l6clear(svg) { while (svg.firstChild) svg.removeChild(svg.firstChild); }
  // Standard normal CDF (complementary error function, W. J. Cody's rational approximations via Numerical Recipes erfc).
  function l6erfc(x) {
    var z = Math.abs(x), t = 1 / (1 + 0.5 * z);
    var r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 +
      t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
    return x >= 0 ? r : 2 - r;
  }
  function l6Phi(x) { return 0.5 * l6erfc(-x / Math.SQRT2); }
  // Inverse standard normal CDF (P. J. Acklam's algorithm, relative error below 1.2e-9).
  function l6Phiinv(p) {
    var a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.3577518672690, -30.66479806614716, 2.506628277459239];
    var b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572];
    var c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783];
    var d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416];
    var q, r;
    if (p < 0.02425) { q = Math.sqrt(-2 * Math.log(p)); return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1); }
    if (p > 1 - 0.02425) { q = Math.sqrt(-2 * Math.log(1 - p)); return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1); }
    q = p - 0.5; r = q * q;
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
  }
  function l6npdf(x, m, s) { var z = (x - m) / s; return Math.exp(-0.5 * z * z) / (s * 2.5066282746310002); }
  // Quantile function of a 1D Gaussian mixture at the levels US (bisection on the CDF).
  function l6mixQuantiles(comp) {
    var q = new Float64Array(MQ);
    function F(x) { var s = 0; comp.forEach(function (c) { s += c[0] * l6Phi((x - c[1]) / c[2]); }); return s; }
    for (var i = 0; i < MQ; i++) {
      var lo = -12, hi = 12;
      for (var it = 0; it < 60; it++) { var mid = 0.5 * (lo + hi); if (F(mid) < US[i]) lo = mid; else hi = mid; }
      q[i] = 0.5 * (lo + hi);
    }
    return q;
  }
  function l6mixPdf(comp, x) { var s = 0; comp.forEach(function (c) { s += c[0] * l6npdf(x, c[1], c[2]); }); return s; }

  /* --- 1. Particles carried by a velocity field; the density follows the continuity equation (§1) --- */
  WIDGETS.l6continuity = function (box) {
    var s = scaffold(box, "Lagrangian particles and the Eulerian density: the continuity equation at work");
    var W = 680, H = 470;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Density of moving particles at time t, velocity arrows, and the space-time trajectories of the particles");
    var FIELDS = {
      translation: { label: "translation, v = 2.5", comp: [[0.5, -2.6, 0.45], [0.5, -1.0, 0.35]], win: [-2.2, -0.8],
        v: function (t, x) { return 2.5; } },
      expansion: { label: "expansion, v = x/(1+t)", comp: [[1, 0, 0.6]], win: [0.3, 1.1],
        v: function (t, x) { return x / (1 + t); } },
      clustering: { label: "clustering (sine field)", comp: [[1, 0, 1.3]], win: [-0.6, 0.6],
        v: function (t, x) { return -1.6 * Math.sin(2 * Math.PI * x / 3); } },
      optimal: { label: "optimal (McCann) field", comp: [[0.5, -2.4, 0.45], [0.5, -0.2, 0.35]], comp1: [[1, 2.2, 0.55]], win: [-1.2, 0.4] }
    };
    var fieldSel = select(s.controls, "Velocity field", Object.keys(FIELDS).map(function (k) { return [k, FIELDS[k].label]; }), "optimal", setup);
    var tS = slider(s.controls, "t", 0, 1, 0.01, 0, draw);
    var playing = false, raf = null;
    var playB = button(s.controls, "Play", function () {
      if (playing) { playing = false; playB.textContent = "Play"; return; }
      if (tS.get() >= 1) tS.set(0);
      playing = true; playB.textContent = "Pause";
      var t0 = null, start = tS.get();
      function frame(ts) {
        if (!playing) return;
        if (t0 === null) t0 = ts;
        var t = Math.min(1, start + (ts - t0) / 4000);
        tS.set(t); draw();
        if (t < 1) raf = requestAnimationFrame(frame); else { playing = false; playB.textContent = "Play"; }
      }
      raf = requestAnimationFrame(frame);
    });
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "α₀ (t = 0)"], ["--s3", "density αₜ and its particles"], ["--s1", "α₁ (t = 1)"], ["--muted", "window [a, b] for the mass balance"]]);
    var NT = 100, F, traj, vel, marker;
    function setup() {
      F = FIELDS[fieldSel.value];
      var q0 = l6mixQuantiles(F.comp), i, k;
      traj = []; vel = [];
      if (F.comp1) { // McCann: straight lines between quantiles, constant velocities
        var q1 = l6mixQuantiles(F.comp1);
        for (k = 0; k <= NT; k++) {
          var t = k / NT, row = new Float64Array(MQ), vr = new Float64Array(MQ);
          for (i = 0; i < MQ; i++) { row[i] = (1 - t) * q0[i] + t * q1[i]; vr[i] = q1[i] - q0[i]; }
          traj.push(row); vel.push(vr);
        }
      } else { // RK4 along the field, 4 sub-steps per frame
        var x = Float64Array.from(q0), sub = 4, h = 1 / (NT * sub);
        for (k = 0; k <= NT; k++) {
          var row2 = Float64Array.from(x), vr2 = new Float64Array(MQ), tk = k / NT;
          for (i = 0; i < MQ; i++) vr2[i] = F.v(tk, x[i]);
          traj.push(row2); vel.push(vr2);
          if (k === NT) break;
          for (var sstep = 0; sstep < sub; sstep++) {
            var tt = tk + sstep * h;
            for (i = 0; i < MQ; i++) {
              var xi = x[i], k1 = F.v(tt, xi), k2 = F.v(tt + h / 2, xi + h / 2 * k1), k3 = F.v(tt + h / 2, xi + h / 2 * k2), k4 = F.v(tt + h, xi + h * k3);
              x[i] = xi + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4);
            }
          }
        }
      }
      draw();
    }
    function Fcdf(q, x) { // CDF of the particle measure, linearly interpolated between the sorted particles
      if (x <= q[0]) return 0; if (x >= q[MQ - 1]) return 1;
      var lo = 0, hi = MQ - 1;
      while (hi - lo > 1) { var mid = (lo + hi) >> 1; if (q[mid] <= x) lo = mid; else hi = mid; }
      return US[lo] + (x - q[lo]) / (q[hi] - q[lo]) * (US[hi] - US[lo]);
    }
    function vAt(k, x) { // Eulerian velocity at x, frame k: interpolate the particle velocities
      var q = traj[k], v = vel[k];
      if (x <= q[0]) return v[0]; if (x >= q[MQ - 1]) return v[MQ - 1];
      var lo = 0, hi = MQ - 1;
      while (hi - lo > 1) { var mid = (lo + hi) >> 1; if (q[mid] <= x) lo = mid; else hi = mid; }
      var r = (x - q[lo]) / (q[hi] - q[lo]); return (1 - r) * v[lo] + r * v[hi];
    }
    function draw() {
      var t = tS.get(), k = Math.round(t * NT), i;
      tS.out.textContent = fmt(t, 2);
      l6clear(s.svg);
      marker = l6marker(s.svg, "f3");
      var g = el("g", {}, s.svg);
      var xr = [-5, 5];
      // top: densities
      var top = l6panel(g, [40, 16, 620, 170], xr, [0, 1.15]);
      var dens = densityFromQ(traj[k]);
      var ymax = 0; dens.forEach(function (p) { if (isFinite(p[1]) && p[1] > ymax) ymax = p[1]; });
      top.yr = [0, Math.max(1.0, ymax * 1.08)];
      var d0 = densityFromQ(traj[0]), d1 = densityFromQ(traj[NT]);
      var capY = function (d) { return d.map(function (p) { return [p[0], Math.min(p[1], top.yr[1])]; }); };
      top.path(capY(d0), "ln c2 thin dash"); top.path(capY(d1), "ln c1 thin dash");
      var w = F.win;
      top.line(w[0], 0, w[0], top.yr[1], "ln cm thin dash"); top.line(w[1], 0, w[1], top.yr[1], "ln cm thin dash");
      top.text(w[0], top.yr[1], "a", "tx-i", "end", -4, 10); top.text(w[1], top.yr[1], "b", "tx-i", "start", 4, 10);
      top.area(dens, "a3"); top.path(dens, "ln c3");
      top.line(xr[0], 0, xr[1], 0, "ax");
      // particles on the axis, and velocity arrows below
      for (i = 10; i < MQ; i += 20) top.circle(traj[k][i], 0, 2.6, "f3");
      var ay = 200;
      for (var xa = -4.5; xa <= 4.51; xa += 0.75) {
        var va = vAt(k, xa), L = 0.18 * va;
        if (Math.abs(L) < 0.02) { el("circle", { cx: top.X(xa), cy: ay, r: 1.8, "class": "fm" }, g); continue; }
        el("line", { x1: top.X(xa), y1: ay, x2: top.X(xa + L), y2: ay, "class": "ln c3 thin", "marker-end": "url(#" + marker + ")" }, g);
      }
      el("text", { x: 40, y: ay + 4, "class": "tx-s", "text-anchor": "end" }, g).textContent = "v";
      // bottom: space-time trajectories
      var bot = l6panel(g, [40, 228, 620, 210], xr, [0, 1]);
      bot.frame();
      for (i = 15; i < MQ; i += 40) {
        var pts = []; for (var kk = 0; kk <= NT; kk += 2) pts.push([traj[kk][i], kk / NT]);
        bot.path(pts, "ln c3 hair", { "stroke-opacity": 0.75 });
      }
      bot.line(xr[0], t, xr[1], t, "ln ck thin");
      for (i = 15; i < MQ; i += 40) bot.circle(traj[k][i], t, 2.6, "f3");
      bot.line(w[0], 0, w[0], 1, "ln cm hair dash"); bot.line(w[1], 0, w[1], 1, "ln cm hair dash");
      bot.xticks([-4, -2, 0, 2, 4]);
      bot.text(xr[0], 0, "t = 0", "tx-s", "end", -5, 4); bot.text(xr[0], 1, "t = 1", "tx-s", "end", -5, 4);
      bot.text(xr[1], t, "t", "tx-i", "start", 5, 4);
      // mass balance in the window and kinetic energy
      var km = Math.max(1, Math.min(NT - 1, k));
      var mass = function (kk) { return Fcdf(traj[kk], w[1]) - Fcdf(traj[kk], w[0]); };
      var dmdt = (mass(km + 1) - mass(km - 1)) / (2 / NT);
      var hd = 0.04;
      var rho = function (kk, x) { return (Fcdf(traj[kk], x + hd) - Fcdf(traj[kk], x - hd)) / (2 * hd); };
      var flux = rho(km, w[0]) * vAt(km, w[0]) - rho(km, w[1]) * vAt(km, w[1]);
      var E = 0; for (i = 0; i < MQ; i++) E += vel[k][i] * vel[k][i]; E /= MQ;
      ro.textContent = "t = " + fmt(t, 2) + "    mass in [a, b]: " + fmt(mass(k), 4) +
        "\nbalance at t = " + fmt(km / NT, 2) + ":  d/dt(mass) = " + fmt(dmdt, 3) + "    ρv(a) − ρv(b) = " + fmt(flux, 3) + "  (flux in − flux out)" +
        "\nkinetic energy ∫|v|² dαₜ = " + fmt(E, 3) + (F.comp1 ? "  (constant in time: this is W₂²(α₀, α₁))" : "");
    }
    setup();
    redrawers.push(draw);
  };

  /* --- 2. Kinetic energy of paths between two Gaussians (§2) --- */
  WIDGETS.l6energy = function (box) {
    var s = scaffold(box, "Paths from N(0, 1) to N(m₁, σ₁²): which one costs the least kinetic energy?");
    var W = 680, H = 400;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "A path in the plane of means and standard deviations, the density at time t, and the kinetic energy along the path");
    var pathSel = select(s.controls, "Path", [["geo", "straight (displacement)"], ["td", "translate, then dilate"], ["dt", "dilate, then translate"],
      ["bent", "bent path"], ["clock", "straight, clock t²"], ["mix", "mixture of densities"]], "geo", draw);
    var mS = slider(s.controls, "m₁", -3, 5, 0.1, 4, draw);
    var sS = slider(s.controls, "σ₁", 0.4, 3, 0.05, 2, draw);
    var bS = slider(s.controls, "bend", -0.4, 1.5, 0.05, 0.5, draw);
    var tS = slider(s.controls, "t", 0, 1, 0.01, 0.5, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "α₀ = N(0, 1)"], ["--s1", "α₁ = N(m₁, σ₁²)"], ["--s3", "geodesic (displacement interpolation)"], ["--s5", "chosen path"]]);
    function msig(kind, t, m1, s1, b) { // mean and standard deviation along a Gaussian path
      if (kind === "geo") return [t * m1, 1 + t * (s1 - 1)];
      if (kind === "td") return t < 0.5 ? [2 * t * m1, 1] : [m1, 1 + (2 * t - 1) * (s1 - 1)];
      if (kind === "dt") return t < 0.5 ? [0, 1 + 2 * t * (s1 - 1)] : [(2 * t - 1) * m1, s1];
      if (kind === "bent") return [t * m1, 1 + t * (s1 - 1) + 4 * b * t * (1 - t)];
      if (kind === "clock") return [t * t * m1, 1 + t * t * (s1 - 1)];
      return null;
    }
    function gaussEnergy(kind, t, m1, s1, b) {
      var h = 1e-5, a = msig(kind, Math.max(0, t - h), m1, s1, b), c = msig(kind, Math.min(1, t + h), m1, s1, b);
      var dt = Math.min(1, t + h) - Math.max(0, t - h);
      var dm = (c[0] - a[0]) / dt, ds = (c[1] - a[1]) / dt;
      return dm * dm + ds * ds;
    }
    // mixture path: flux m = F0 - F1, energy at t = int (F0 - F1)^2 / rho_t ; action with the logarithmic mean
    function mixGrid(m1, s1) {
      var lo = Math.min(-7, m1 - 7 * s1), hi = Math.max(7, m1 + 7 * s1), n = 3000, xs = [], dx = (hi - lo) / (n - 1);
      for (var i = 0; i < n; i++) xs.push(lo + i * dx);
      var r0 = [], r1 = [], fl = [];
      xs.forEach(function (x) {
        r0.push(l6npdf(x, 0, 1)); r1.push(l6npdf(x, m1, s1));
        var a = x < 0.5 * m1 ? l6Phi(x) - l6Phi((x - m1) / s1) : l6Phi(-(x - m1) / s1) - l6Phi(-x);
        fl.push(a);
      });
      return { xs: xs, dx: dx, r0: r0, r1: r1, fl: fl };
    }
    function mixEnergy(G, t) {
      var e = 0;
      for (var i = 0; i < G.xs.length; i++) { var r = (1 - t) * G.r0[i] + t * G.r1[i]; if (r > 1e-300) e += G.fl[i] * G.fl[i] / r; }
      return e * G.dx;
    }
    function mixAction(G) {
      var e = 0;
      for (var i = 0; i < G.xs.length; i++) {
        var a = G.r0[i], b = G.r1[i], lm;
        if (a <= 0 || b <= 0) continue;
        var d = Math.log(a) - Math.log(b);
        lm = Math.abs(d) > 1e-10 ? (a - b) / d : a;
        e += G.fl[i] * G.fl[i] / lm;
      }
      return e * G.dx;
    }
    function draw() {
      var kind = pathSel.value, m1 = mS.get(), s1 = sS.get(), b = bS.get(), t = tS.get(), i;
      mS.out.textContent = fmt(m1, 1); sS.out.textContent = fmt(s1, 2); bS.out.textContent = fmt(b, 2); tS.out.textContent = fmt(t, 2);
      bS.input.parentNode.style.display = kind === "bent" ? "" : "none";
      var W22 = m1 * m1 + (s1 - 1) * (s1 - 1);
      l6clear(s.svg);
      var g = el("g", {}, s.svg);
      // (m, sigma) plane
      var mlo = Math.min(0, m1) - 0.8, mhi = Math.max(0, m1) + 0.8;
      var pl = l6panel(g, [52, 30, 250, 300], [mlo, mhi], [0, 3.6]);
      pl.frame();
      for (var gy = 1; gy <= 3; gy++) { pl.line(mlo, gy, mhi, gy, "gr"); pl.text(mlo, gy, String(gy), "tx-s", "end", -5, 4); }
      var ticks = []; for (var gx = Math.ceil(mlo); gx <= mhi; gx++) ticks.push(gx);
      ticks.forEach(function (v) { pl.line(v, 0, v, 3.6, "gr"); });
      pl.xticks(ticks);
      pl.text(mhi, 0, "mean m", "tx-s", "end", 0, 28);
      pl.text(mlo, 3.6, "st. dev. σ", "tx-s", "start", 4, -6);
      pl.line(0, 1, m1, s1, "ln c3");
      var cur = null;
      if (kind !== "mix") {
        var pts = []; for (i = 0; i <= 200; i++) pts.push(msig(kind, i / 200, m1, s1, b));
        pl.path(pts, "ln c5");
        cur = msig(kind, t, m1, s1, b);
        pl.circle(cur[0], cur[1], 5, "f5");
      } else {
        pl.text(0.5 * (mlo + mhi), 3.2, "the mixture is not a Gaussian:", "tx-s t5", "middle");
        pl.text(0.5 * (mlo + mhi), 3.2, "no point in this plane", "tx-s t5", "middle", 0, 14);
      }
      pl.circle(0, 1, 5, "f2"); pl.circle(m1, s1, 5, "f1");
      // densities at t
      var xlo = Math.min(-4, m1 - 3.5 * s1), xhi = Math.max(4, m1 + 3.5 * s1);
      var dp = l6panel(g, [340, 22, 320, 150], [xlo, xhi], [0, 0.45]);
      var f0 = [], f1 = [], ft = [], n = 300;
      var G = kind === "mix" ? mixGrid(m1, s1) : null;
      for (i = 0; i <= n; i++) {
        var x = xlo + (xhi - xlo) * i / n;
        f0.push([x, l6npdf(x, 0, 1)]); f1.push([x, l6npdf(x, m1, s1)]);
        ft.push([x, kind === "mix" ? (1 - t) * l6npdf(x, 0, 1) + t * l6npdf(x, m1, s1) : l6npdf(x, cur[0], cur[1])]);
      }
      var ym = 0; ft.concat(f0, f1).forEach(function (p) { ym = Math.max(ym, p[1]); });
      dp.yr = [0, ym * 1.1];
      dp.path(f0, "ln c2 thin dash"); dp.path(f1, "ln c1 thin dash");
      dp.area(ft, "a5"); dp.path(ft, "ln c5");
      dp.line(xlo, 0, xhi, 0, "ax");
      var tk = []; for (var u = Math.ceil(xlo / 2) * 2; u <= xhi; u += 2) tk.push(u);
      dp.xticks(tk);
      dp.text(xlo, dp.yr[1], "density at time t", "tx-s", "start", 2, 10);
      // kinetic energy along the path
      var ep = l6panel(g, [340, 212, 320, 150], [0, 1], [0, 1]);
      var E = [], act = 0, len = 0, NN = 400;
      for (i = 0; i <= NN; i++) {
        var tt = Math.min(0.9995, Math.max(0.0005, i / NN));
        var e = kind === "mix" ? mixEnergy(G, tt) : gaussEnergy(kind, i / NN, m1, s1, b);
        E.push([i / NN, e]);
      }
      for (i = 0; i < NN; i++) { // trapezoid for the action and the length
        act += 0.5 * (E[i][1] + E[i + 1][1]) / NN;
        len += 0.5 * (Math.sqrt(E[i][1]) + Math.sqrt(E[i + 1][1])) / NN;
      }
      if (kind === "mix") act = mixAction(G);
      var top = Math.max(2.2 * W22, 1);
      ep.yr = [0, top];
      ep.frame();
      ep.line(0, W22, 1, W22, "ln c3 dash");
      ep.text(1, W22, "W₂² = " + fmt(W22, 2), "tx-s t3", "end", -4, -5);
      ep.path(E.map(function (p) { return p[1] <= top ? p : [p[0], top]; }), "ln c5");
      var et = kind === "mix" ? mixEnergy(G, Math.min(0.9995, Math.max(0.0005, t))) : gaussEnergy(kind, t, m1, s1, b);
      if (et <= top) ep.circle(t, et, 4, "f5");
      ep.xticks([0, 0.25, 0.5, 0.75, 1], function (v) { return fmt(v, 2); });
      ep.text(0, top, "kinetic energy ∫|vₜ|² dαₜ along the path", "tx-s", "start", 2, 10);
      ep.text(1, 0, "t", "tx-i", "end", 0, 30);
      ro.textContent = "action ∫₀¹ (kinetic energy) dt = " + fmt(act, 3) + "    W₂²(α₀, α₁) = " + fmt(W22, 3) + "    ratio " + fmt(act / W22, 3) +
        "\nlength ∫₀¹ √(kinetic energy) dt = " + fmt(len, 3) + "    W₂ = " + fmt(Math.sqrt(W22), 3) +
        (kind === "geo" ? "\nconstant speed along a straight line: action = length² = W₂² (Benamou–Brenier)." :
          kind === "clock" ? "\nsame curve as the geodesic (length W₂), run at a non-constant speed: the action is 4/3 of W₂²." :
          kind === "mix" ? "\nthe energy blows up near t = 0 and t = 1 (mass must appear where the other density is tiny); off the chart." :
          "\nthe action is at least length², with equality only at constant speed; the length is at least W₂.");
    }
    draw();
    redrawers.push(draw);
  };

  /* --- 3. Flow matching in 2D: independent versus (minibatch) optimal-transport couplings (§8) --- */
  WIDGETS.l6fm2d = function (box) {
    var s = scaffold(box, "Flow matching in 2D: the coupling decides how straight the paths are");
    var W = 680, H = 430;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Training pairs, generated trajectories and generated samples of a flow-matching model in the plane");
    var targetSel = select(s.controls, "Data", [["ring", "8 Gaussians (ring)"], ["moons", "two moons"], ["blobs", "3 unequal blobs"]], "ring", retrain);
    var coupSel = select(s.controls, "Coupling", [["ind", "independent"], ["b8", "minibatch OT (8)"], ["b50", "minibatch OT (50)"], ["full", "OT on all 400"]], "ind", retrain);
    var KS = [1, 2, 3, 4, 6, 8, 12, 20, 50];
    var kS = slider(s.controls, "Euler steps K", 0, KS.length - 1, 1, 2, generate);
    var pairChk = checkbox(s.controls, "show training pairs", true, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "noise samples X₀ ~ N(0, I)"], ["--s1", "data samples"], ["--muted", "40 training pairs (X₀, X₁)"], ["--s3", "generated: Euler trajectories and end points"]]);
    var M = 400, NG = 150, hbw = 0.35, X0, X1, Xt0, Xt1, pair, gen = null, tgtTest, cache = {};
    function sampleTarget(kind, rng, n) {
      var out = [], i;
      for (i = 0; i < n; i++) {
        if (kind === "ring") {
          var k = Math.floor(rng() * 8), a = 2 * Math.PI * k / 8;
          out.push([3.2 * Math.cos(a) + 0.22 * gaussRand(rng), 3.2 * Math.sin(a) + 0.22 * gaussRand(rng)]);
        } else if (kind === "moons") {
          var th = Math.PI * rng();
          if (rng() < 0.5) out.push([2.2 * Math.cos(th) - 1.1 + 0.15 * gaussRand(rng), 2.2 * Math.sin(th) - 0.5 + 0.15 * gaussRand(rng)]);
          else out.push([2.2 - 2.2 * Math.cos(th) - 1.1 + 0.15 * gaussRand(rng), 0.5 - 2.2 * Math.sin(th) + 0.15 * gaussRand(rng)]);
        } else {
          var u = rng(), c = u < 0.6 ? [-2.2, 1.6] : (u < 0.85 ? [2.6, 1.2] : [0.6, -2.8]);
          var sd = u < 0.6 ? 0.55 : 0.3;
          out.push([c[0] + sd * gaussRand(rng), c[1] + sd * gaussRand(rng)]);
        }
      }
      return out;
    }
    function d2(a, b) { var dx = a[0] - b[0], dy = a[1] - b[1]; return dx * dx + dy * dy; }
    function retrain() {
      var kind = targetSel.value, cp = coupSel.value, key = kind + "|" + cp, i, j;
      var rng = mulberry32(2026);
      X0 = []; for (i = 0; i < M; i++) X0.push([gaussRand(rng), gaussRand(rng)]);
      X1 = sampleTarget(kind, mulberry32(7 + kind.length), M);
      tgtTest = sampleTarget(kind, mulberry32(99 + kind.length), NG);
      if (!cache[key]) {
        var perm = [];
        for (i = 0; i < M; i++) perm.push(i);
        if (cp !== "ind") {
          var B = cp === "b8" ? 8 : (cp === "b50" ? 50 : M);
          for (var st = 0; st < M; st += B) {
            var C = [];
            for (i = 0; i < B; i++) { C.push([]); for (j = 0; j < B; j++) C[i].push(d2(X0[st + i], X1[st + j])); }
            var a = hungarian(C);
            for (i = 0; i < B; i++) perm[st + i] = st + a[i];
          }
        }
        cache[key] = perm;
      }
      pair = cache[key];
      Xt0 = X0; Xt1 = pair.map(function (j) { return X1[j]; });
      generate();
    }
    function velocity(t, x) { // kernel (Nadaraya–Watson) estimate of E[X1 - X0 | X_t = x] from the training pairs
      var best = Infinity, i, ds = new Float64Array(M);
      for (i = 0; i < M; i++) {
        var px = (1 - t) * Xt0[i][0] + t * Xt1[i][0], py = (1 - t) * Xt0[i][1] + t * Xt1[i][1];
        var dx = x[0] - px, dy = x[1] - py; ds[i] = dx * dx + dy * dy; if (ds[i] < best) best = ds[i];
      }
      var sw = 0, vx = 0, vy = 0;
      for (i = 0; i < M; i++) {
        var w = Math.exp(-(ds[i] - best) / (2 * hbw * hbw));
        sw += w; vx += w * (Xt1[i][0] - Xt0[i][0]); vy += w * (Xt1[i][1] - Xt0[i][1]);
      }
      return [vx / sw, vy / sw];
    }
    function generate() {
      var K = KS[kS.get()], rng = mulberry32(31), i, k;
      kS.out.textContent = String(K);
      gen = [];
      for (i = 0; i < NG; i++) {
        var x = [gaussRand(rng), gaussRand(rng)], path = [x.slice()];
        for (k = 0; k < K; k++) {
          var v = velocity(k / K, x);
          x = [x[0] + v[0] / K, x[1] + v[1] / K]; path.push(x.slice());
        }
        gen.push(path);
      }
      draw();
    }
    function draw() {
      if (!gen) return;
      var K = KS[kS.get()], i, k;
      l6clear(s.svg);
      var g = el("g", {}, s.svg);
      var P = l6panel(g, [10, 10, 410, 410], [-5.2, 5.2], [-5.2, 5.2]);
      P.frame();
      tgtTest.forEach(function (p) { P.circle(p[0], p[1], 2.2, "f1", { "fill-opacity": 0.45 }); });
      if (pairChk.checked) for (i = 0; i < 40; i++) P.line(Xt0[i][0], Xt0[i][1], Xt1[i][0], Xt1[i][1], "ln cm hair", { "stroke-opacity": 0.55 });
      gen.forEach(function (path) { P.path(path, "ln c3 hair", { "stroke-opacity": 0.7 }); });
      gen.forEach(function (path) { P.circle(path[0][0], path[0][1], 1.8, "f2", { "fill-opacity": 0.6 }); });
      gen.forEach(function (path) { var e = path[path.length - 1]; P.circle(e[0], e[1], 2.6, "f3"); });
      // statistics: transport cost of the generated map, straightness, W2 to fresh data samples
      var cost = 0, curv = 0, C = [];
      gen.forEach(function (path) {
        var a = path[0], b = path[path.length - 1], L = 0;
        for (k = 1; k < path.length; k++) L += Math.sqrt(d2(path[k], path[k - 1]));
        var ch = Math.sqrt(d2(a, b)); cost += ch * ch; curv += ch > 1e-9 ? L / ch - 1 : 0;
      });
      cost /= NG; curv /= NG;
      for (i = 0; i < NG; i++) { C.push([]); for (k = 0; k < NG; k++) C[i].push(d2(gen[i][gen[i].length - 1], tgtTest[k])); }
      var asg = hungarian(C), w2 = 0; for (i = 0; i < NG; i++) w2 += C[i][asg[i]]; w2 = Math.sqrt(w2 / NG);
      var pc = 0; for (i = 0; i < M; i++) pc += d2(Xt0[i], Xt1[i]); pc /= M;
      // side text
      var tx = 440, ty = 40;
      function line(sv, cls) { var e = el("text", { x: tx, y: ty, "class": cls || "tx-s" }, g); e.textContent = sv; ty += 18; }
      line("Training pairs (" + M + "):", "tx-b");
      line("mean |X₁ − X₀|² = " + fmt(pc, 2));
      ty += 8;
      line("Generated (" + NG + " samples, K = " + K + "):", "tx-b");
      line("mean |end − start|² = " + fmt(cost, 2));
      line("extra path length = " + fmt(100 * curv, 1) + "%");
      line("W₂(generated, data) = " + fmt(w2, 3));
      ty += 8;
      line("The velocity is a kernel average of", "tx-s");
      line("X₁ − X₀ over the pairs near x at time t", "tx-s");
      line("(a stand-in for the neural network).", "tx-s");
      ro.textContent = "Coupling: " + coupSel.options[coupSel.selectedIndex].text + ".  With K = 1 step, each sample moves once along v₀(x) ≈ E[X₁ − X₀ | X₀ = x]." +
        (coupSel.value === "ind" ? "\nIndependent pairs: v₀(x) ≈ E[X₁] − x, so K = 1 sends every sample to the data mean; many steps are needed." :
          coupSel.value === "full" ? "\nOT pairs do not cross: the paths are nearly straight, and a few Euler steps already land near the data." :
          "\nMinibatch OT pairs do not cross inside a minibatch, but pairs of different minibatches still can: the paths straighten as the minibatch grows.");
    }
    retrain();
    redrawers.push(draw);
  };

  /* --- 4. Noising a 1D distribution, and the probability-flow ODE back to the data (§7) --- */
  WIDGETS.l6diffusion = function (box) {
    var s = scaffold(box, "From noise to data in 1D: noised densities, probability-flow trajectories, and where they land");
    var W = 680, H = 440;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Space-time picture: densities of the noised data at several times and trajectories of the probability-flow ODE");
    var DATA = {
      two: { label: "two atoms", comp: [[0.3, -2, 0], [0.7, 1, 0]] },
      three: { label: "three atoms", comp: [[1 / 3, -2.5, 0], [1 / 3, 0, 0], [1 / 3, 2, 0]] },
      mix: { label: "smooth mixture", comp: [[0.4, -1.8, 0.4], [0.6, 1.5, 0.7]] }
    };
    var dataSel = select(s.controls, "Data", Object.keys(DATA).map(function (k) { return [k, DATA[k].label]; }), "two", draw);
    var schSel = select(s.controls, "Schedule", [["lin", "linear (flow matching)"], ["vp", "variance-preserving"]], "lin", draw);
    var sdeChk = checkbox(s.controls, "stochastic sampler (reverse SDE)", false, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "noise N(0, 1) at t = 0"], ["--s1", "data at t = 1"], ["--s5", "density of X_t"], ["--s3", "probability-flow trajectories"]]);
    function sched(kind, t) { // [a, b, a', b']: X_t = a X1 + b X0, X1 data, X0 noise
      if (kind === "lin") return [t, 1 - t, 1, -1];
      var c = Math.cos(Math.PI * t / 2), sn = Math.sin(Math.PI * t / 2);
      return [sn, c, Math.PI / 2 * c, -Math.PI / 2 * sn];
    }
    function postMean(comp, lam, y) { // E[X | lam X + Z = y], X ~ mixture, Z ~ N(0,1)
      var lw = [], mx = -Infinity, mu = [];
      comp.forEach(function (c) {
        var v = lam * lam * c[2] * c[2] + 1, r = y - lam * c[1];
        var l = Math.log(c[0]) - 0.5 * r * r / v - 0.5 * Math.log(v);
        lw.push(l); if (l > mx) mx = l;
        mu.push(c[1] + lam * c[2] * c[2] / v * r);
      });
      var sw = 0, sm = 0;
      for (var k = 0; k < comp.length; k++) { var w = Math.exp(lw[k] - mx); sw += w; sm += w * mu[k]; }
      return sm / sw;
    }
    var LAM = (function () { var a = [], i; for (i = 0; i <= 100; i++) a.push(2 * i / 100); for (i = 1; i <= 300; i++) a.push(2 * Math.pow(200, i / 300)); return a; })();
    function solveY(comp, z) { // y(lam) on the grid LAM, RK4
      var ys = [z], y = z;
      for (var i = 0; i < LAM.length - 1; i++) {
        var l0 = LAM[i], h = LAM[i + 1] - l0;
        var k1 = postMean(comp, l0, y), k2 = postMean(comp, l0 + h / 2, y + h / 2 * k1), k3 = postMean(comp, l0 + h / 2, y + h / 2 * k2), k4 = postMean(comp, l0 + h, y + h * k3);
        y += h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); ys.push(y);
      }
      return ys;
    }
    function interpY(ys, lam) {
      if (lam >= LAM[LAM.length - 1]) return ys[ys.length - 1] * lam / LAM[LAM.length - 1];
      var lo = 0, hi = LAM.length - 1;
      while (hi - lo > 1) { var mid = (lo + hi) >> 1; if (LAM[mid] <= lam) lo = mid; else hi = mid; }
      var r = (lam - LAM[lo]) / (LAM[hi] - LAM[lo]); return (1 - r) * ys[lo] + r * ys[hi];
    }
    function endPoint(ys) { return ys[ys.length - 1] / LAM[LAM.length - 1]; }
    function draw() {
      var D = DATA[dataSel.value], comp = D.comp, kind = schSel.value, i, k;
      l6clear(s.svg);
      var g = el("g", {}, s.svg);
      var P = l6panel(g, [72, 40, 580, 364], [-4.2, 4.2], [0, 1]);
      // ridgeline densities of X_t at 9 times
      var NR = 8;
      for (k = 0; k <= NR; k++) {
        var t = k / NR, sc = sched(kind, t), pts = [];
        for (i = 0; i <= 240; i++) {
          var x = -4.2 + 8.4 * i / 240, dsum = 0;
          comp.forEach(function (c) { var sd = Math.sqrt(sc[0] * sc[0] * c[2] * c[2] + sc[1] * sc[1]); if (sd > 1e-3) dsum += c[0] * l6npdf(x, sc[0] * c[1], sd); });
          pts.push([x, t + Math.min(dsum, 2.2) * 0.07]);
        }
        if (k < NR || comp[0][2] > 0) {
          P.path(pts.concat([[4.2, t], [-4.2, t]]), k === 0 ? "a2" : "a5");
          P.path(pts, k === 0 ? "ln c2 thin" : "ln c5 hair");
        }
        P.line(-4.2, t, 4.2, t, "gr");
        P.text(-4.2, t, "t = " + fmt(t, 3).replace(/0+$/, "").replace(/\.$/, ""), "tx-s", "end", -4, 4);
      }
      // data at the top
      var maxw = 0; comp.forEach(function (c) { if (c[0] > maxw) maxw = c[0]; });
      comp.forEach(function (c) {
        if (c[2] === 0) { var hh = 1 + 0.075 * c[0] / maxw; P.line(c[1], 1, c[1], hh, "ln c1"); P.circle(c[1], hh, 4, "f1"); }
      });
      // probability-flow trajectories from 24 noise quantiles
      var NP = 24, ends = [];
      for (i = 0; i < NP; i++) {
        var z = l6Phiinv((i + 0.5) / NP), ys = solveY(comp, z), path = [];
        for (k = 0; k <= 200; k++) {
          var tt = Math.min(k / 200, 0.999), sc2 = sched(kind, tt);
          path.push([sc2[1] * interpY(ys, sc2[0] / sc2[1]), tt]);
        }
        var e = endPoint(ys); ends.push(e); path.push([e, 1]);
        if (!sdeChk.checked) P.path(path, "ln c3 thin");
        P.circle(z, 0, 2.6, "f2");
      }
      // reverse SDE with the same marginals: dX = [v + g^2/2 * score] dt + g dB, g = 0.7 b_t
      if (sdeChk.checked) {
        var rng = mulberry32(5), NS = 400;
        for (i = 0; i < NP; i++) {
          var xx = l6Phiinv((i + 0.5) / NP), pth = [[xx, 0]];
          for (k = 0; k < NS; k++) {
            var t0 = k / NS, sc3 = sched(kind, t0), a = sc3[0], b = sc3[1], da = sc3[2], db = sc3[3];
            var lam = a / b, m = postMean(comp, lam, xx / b);       // E[X1 | X_t = x]
            var ez = (xx - a * m) / b, v = da * m + db * ez;        // velocity of the interpolant
            var score = (a * m - xx) / (b * b), gg = 0.7 * b;
            xx += (v + 0.5 * gg * gg * score) / NS + gg * Math.sqrt(1 / NS) * gaussRand(rng);
            if (k % 2 === 1) pth.push([xx, (k + 1) / NS]);
          }
          P.path(pth, "ln c3 hair");
        }
      }
      P.xticks([-4, -2, 0, 2, 4], null, 16);
      P.text(4.2, 0, "noise", "tx-s t2", "end", 0, 30);
      P.text(4.2, 1, "data", "tx-s t1", "end", 0, -8);
      // where the deterministic flow lands, against the monotone (optimal) map
      var txt = "";
      if (comp[0][2] === 0) {
        var counts = comp.map(function () { return 0; }), NQ = 400, bnd = [], cum = 0;
        for (i = 0; i < NQ; i++) {
          var e2 = endPoint(solveY(comp, l6Phiinv((i + 0.5) / NQ))), best = 0;
          comp.forEach(function (c, j) { if (Math.abs(c[1] - e2) < Math.abs(comp[best][1] - e2)) best = j; });
          counts[best]++;
        }
        for (k = 0; k < comp.length - 1; k++) { // boundary between atoms k and k+1 by bisection
          var lo = -6, hi = 6, mid2 = (comp[k][1] + comp[k + 1][1]) / 2;
          for (var it = 0; it < 40; it++) { var mm = 0.5 * (lo + hi); if (endPoint(solveY(comp, mm)) < mid2) lo = mm; else hi = mm; }
          cum += comp[k][0]; bnd.push([0.5 * (lo + hi), l6Phiinv(cum)]);
        }
        txt = "shares of 400 noise quantiles per atom: " + counts.map(function (c) { return fmt(c / NQ, 3); }).join(", ") +
          "   (weights " + comp.map(function (c) { return fmt(c[0], 3); }).join(", ") + ")" +
          "\nflow boundaries: " + bnd.map(function (bb) { return fmt(bb[0], 4); }).join(", ") +
          "    monotone map, Φ⁻¹(cumulative weights): " + bnd.map(function (bb) { return fmt(bb[1], 4); }).join(", ");
        bnd.forEach(function (bb) { P.line(bb[0], 0, bb[0], 0.05, "ln ck thin"); });
      } else {
        txt = "smooth data: the flow sends the noise quantiles to the data quantiles (a monotone map, hence optimal in 1D).";
      }
      ro.textContent = txt + (sdeChk.checked ? "\nStochastic sampler: random paths with the same densities at every time; the end point is random, the deterministic map is lost." :
        "\nThe two schedules draw different trajectories but land at the same points: in 1D both give the monotone map.");
    }
    draw();
    redrawers.push(draw);
  };

  /* --- 5. Gaussian flow matching: the flow map versus the Brenier map (§8) --- */
  WIDGETS.l6gaussfm = function (box) {
    var s = scaffold(box, "Flow matching between two centred Gaussians: optimal only when the covariances commute");
    var W = 680, H = 380;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Source and target ellipses, the flow-matching map and the Brenier map of twelve points");
    var thS = slider(s.controls, "rotation θ of Σ₁ (degrees)", 0, 90, 1, 45, draw);
    var tS = slider(s.controls, "t", 0, 1, 0.01, 1, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "α₀ = N(0, Σ₀), Σ₀ = diag(4, 1)"], ["--s1", "α₁ = N(0, Σ₁), Σ₁ = R diag(3, 1) Rᵀ"], ["--s3", "flow matching (independent coupling)"], ["--text", "Brenier map (circles)"]]);
    function sq(A) { return msqrt(A); }
    function inv(A) { return minv(A); }
    function lin(a, A, b, B) { return [a * A[0] + b * B[0], a * A[1] + b * B[1], a * A[2] + b * B[2], a * A[3] + b * B[3]]; }
    function app(A, v) { return [A[0] * v[0] + A[1] * v[1], A[2] * v[0] + A[3] * v[1]]; }
    function draw() {
      var th = thS.get() * Math.PI / 180, t = tS.get(), i;
      thS.out.textContent = String(thS.get()) + "°"; tS.out.textContent = fmt(t, 2);
      var c = Math.cos(th), sn = Math.sin(th), R = [c, -sn, sn, c], RT = [c, sn, -sn, c];
      var S0 = [4, 0, 0, 1], S1 = msym(mmul(mmul(R, [3, 0, 0, 1]), RT));
      var r0 = sq(S0), ir0 = inv(r0), C = msym(mmul(mmul(ir0, S1), ir0));
      function Tfm(tt) { return mmul(mmul(r0, sq(msym(lin((1 - tt) * (1 - tt), [1, 0, 0, 1], tt * tt, C)))), ir0); }
      var Tot = mmul(mmul(ir0, sq(msym(mmul(mmul(r0, S1), r0)))), ir0);
      var T1 = Tfm(1), Tt = Tfm(t);
      l6clear(s.svg);
      var g = el("g", {}, s.svg);
      var P = l6panel(g, [10, 10, 400, 360], [-2.9, 2.9], [-2.61, 2.61]);
      P.frame();
      P.line(-2.9, 0, 2.9, 0, "gr"); P.line(0, -2.61, 0, 2.61, "gr");
      var e0 = [], e1 = [], et = [], St = lin((1 - t) * (1 - t), S0, t * t, S1);
      for (i = 0; i <= 96; i++) {
        var a = 2 * Math.PI * i / 96, u = [Math.cos(a), Math.sin(a)];
        e0.push(app(r0, u)); e1.push(app(sq(S1), u)); et.push(app(sq(msym(St)), u));
      }
      P.path(e0, "ln c2 thin"); P.path(e1, "ln c1 thin"); P.path(et, "ln c3 thin dash");
      for (i = 0; i < 12; i++) {
        var ang = 2 * Math.PI * i / 12, p = app(r0, [Math.cos(ang), Math.sin(ang)]), tr = [];
        for (var k = 0; k <= 50; k++) tr.push(app(Tfm(k / 50 * t), p));
        P.path(tr, "ln c3 hair");
        var q = app(Tt, p), o = app(Tot, p);
        P.circle(p[0], p[1], 2.6, "f2");
        P.circle(o[0], o[1], 4, "ln ck thin nofill");
        P.circle(q[0], q[1], 3.4, "f3");
      }
      function cost(T) { var D = lin(1, T, -1, [1, 0, 0, 1]), M2 = mmul(mmul(D, S0), [D[0], D[2], D[1], D[3]]); return M2[0] + M2[3]; }
      var cf = cost(T1), co = cost(Tot), comm = mmul(S0, S1), comm2 = mmul(S1, S0);
      var cn = Math.hypot(comm[0] - comm2[0], comm[1] - comm2[1], comm[2] - comm2[2], comm[3] - comm2[3]);
      var tx = 432, ty = 40;
      function line(sv, cls) { var e = el("text", { x: tx, y: ty, "class": cls || "tx-s" }, g); e.textContent = sv; ty += 18; }
      line("At t = 1:", "tx-b");
      line("T₁ᶠᴹ = [[" + fmt(T1[0], 3) + ", " + fmt(T1[1], 3) + "], [" + fmt(T1[2], 3) + ", " + fmt(T1[3], 3) + "]]");
      line("Tᴼᵀ  = [[" + fmt(Tot[0], 3) + ", " + fmt(Tot[1], 3) + "], [" + fmt(Tot[2], 3) + ", " + fmt(Tot[3], 3) + "]]");
      ty += 6;
      line("cost of the flow map: " + fmt(cf, 4), "tx-s t3");
      line("W₂² (Brenier map): " + fmt(co, 4));
      line("excess: " + fmt(100 * (cf / co - 1), 2) + "%");
      ty += 6;
      line("‖Σ₀Σ₁ − Σ₁Σ₀‖ = " + fmt(cn, 3));
      line("asymmetry of T₁ᶠᴹ: |T₁₂ − T₂₁|/2 = " + fmt(Math.abs(T1[1] - T1[2]) / 2, 3));
      ro.textContent = "Green: the flow-matching trajectories, and the points Tₜᶠᴹ(x) at time t." +
        "\nDashed green ellipse: N(0, Σₜ), Σₜ = (1 − t)²Σ₀ + t²Σ₁ (smaller in the middle: independent coupling)." +
        "\nAt θ = 0° or 90° the covariances commute and the flow map is the Brenier map;" +
        "\nin between, it carries a rotation and costs more.";
    }
    draw();
    redrawers.push(draw);
  };
