// widgets/Partie04.js — interactive figures of Partie 4 (interior point methods).
// Inserted by build.mjs inside the scope of app.js: uses el, fmt, Plot, scaffold, slider, select, button, checkbox,
// readout, legend, addSvg, svgPoint, arrowMarker and simplex. Every name defined here starts with p4.

  /* ---------------- shared helpers ---------------- */
  // French decimal comma; exponent notation 2,3·10⁻⁷ for small numbers.
  function p4f(x, d) { return fmt(x, d === undefined ? 3 : d).replace(".", ","); }
  function p4sup(n) { var m = { "-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹" }; return String(n).split("").map(function (c) { return m[c]; }).join(""); }
  function p4e(x, d) {
    if (!isFinite(x)) return fmt(x);
    if (x === 0) return "0";
    var a = Math.abs(x);
    if (a >= 0.01 && a < 1000) return p4f(x, d === undefined ? 3 : d);
    var e = Math.floor(Math.log10(a)), m = x / Math.pow(10, e);
    return p4f(m, 1) + "·10" + p4sup(e);
  }
  // A label "x^μ = …" in an SVG: base letter, superscript, then the rest (no "^" or "_" shown).
  function p4sup2(plot, x, y, base, sup, rest, cls, anchor, dx, dy) {
    var t = plot.text(x, y, base, cls, anchor, dx, dy);
    var ts = el("tspan", { "baseline-shift": "super", "font-size": "75%" }, t); ts.textContent = sup;
    if (rest) { var tr = el("tspan", {}, t); tr.textContent = rest; }
    return t;
  }
  function p4pt(u, d) { return "(" + p4f(u[0], d) + " ; " + p4f(u[1], d) + ")"; }

  // The polygon of Allaire, Ex. 4.2.1, in the plane u = (x1, x2): g_j·u ≤ r_j (x1 ≥ 0, x2 ≥ 0 and three rows).
  // Standard form: x = (x1, x2, x3, x4, x5) with x_{2+j} the slack of row j; n = 5, m = 3.
  var P4G = [[-1, 0], [0, -1], [-3, 2], [-1, 2], [1, 1]], P4R = [0, 0, 2, 4, 5];
  var P4V = [[0, 0], [5, 0], [2, 3], [1, 2.5], [0, 1]];
  var P4A = [[-3, 2, 1, 0, 0], [-1, 2, 0, 1, 0], [1, 1, 0, 0, 1]], P4B = [2, 4, 5];
  function p4slacks(u) { return P4G.map(function (g, j) { return P4R[j] - g[0] * u[0] - g[1] * u[1]; }); }
  function p4F(u, mu, c) {
    var s = p4slacks(u), v = c[0] * u[0] + c[1] * u[1];
    for (var j = 0; j < 5; j++) { if (!(s[j] > 0)) return Infinity; v -= mu * Math.log(s[j]); }
    return v;
  }
  // One Newton step on f_mu(u) = c·u − mu Σ log s_j(u). Damped: start with t = 1 and halve t while the point leaves
  // the polygon or f does not decrease. Returns {u, t, d, lam2 (Newton decrement² of f/mu), out (pure step outside)}.
  function p4step(u, mu, c, pure) {
    var s = p4slacks(u), g = [c[0], c[1]], H = [[0, 0], [0, 0]];
    for (var j = 0; j < 5; j++) {
      var a = P4G[j];
      g[0] += mu * a[0] / s[j]; g[1] += mu * a[1] / s[j];
      var w = mu / (s[j] * s[j]);
      H[0][0] += w * a[0] * a[0]; H[0][1] += w * a[0] * a[1]; H[1][1] += w * a[1] * a[1];
    }
    H[1][0] = H[0][1];
    var det = H[0][0] * H[1][1] - H[0][1] * H[1][0];
    var d = [-(H[1][1] * g[0] - H[0][1] * g[1]) / det, -(-H[1][0] * g[0] + H[0][0] * g[1]) / det];
    var lam2 = -(g[0] * d[0] + g[1] * d[1]) / mu, t = 1;
    var full = [u[0] + d[0], u[1] + d[1]];
    var out = p4slacks(full).some(function (v) { return !(v > 0); });
    if (!pure) {
      var f0 = p4F(u, mu, c);
      while (t > 1e-14 && !(p4F([u[0] + t * d[0], u[1] + t * d[1]], mu, c) < f0)) t /= 2;
    }
    return { u: [u[0] + t * d[0], u[1] + t * d[1]], t: t, d: d, lam2: lam2, out: out };
  }
  function p4center(mu, c, u0) {
    var u = u0.slice();
    for (var i = 0; i < 200; i++) { var r = p4step(u, mu, c); u = r.u; if (r.lam2 < 1e-13) break; }
    return u;
  }
  var P4AC = p4center(1, [0, 0], [2, 1]); // analytic centre: maximises the product of the five slacks
  // The central path for a cost c, from mu = 10^3 down to 10^-6 (warm starts).
  var p4pathCache = {};
  function p4path(c) {
    var key = c.join(",");
    if (p4pathCache[key]) return p4pathCache[key];
    var out = [], u = P4AC.slice();
    for (var k = 0; k <= 300; k++) { var mu = Math.pow(10, 3 - 9 * k / 300); u = p4center(mu, c, u); out.push([mu, u.slice()]); }
    p4pathCache[key] = out; return out;
  }
  // Standard-form point x (5 components) and the dual estimate p of the Newton system (normal equations
  // (A X² Aᵀ) p = A X² c − mu b), with s = c − Aᵀp. On the central path, s = mu/x exactly.
  function p4full(u) { var s = p4slacks(u); return [u[0], u[1], s[2], s[3], s[4]]; }
  function p4dual(u, mu, c) {
    var x = p4full(u), cf = [c[0], c[1], 0, 0, 0], M = [], r = [], i, j, k;
    for (i = 0; i < 3; i++) {
      M.push([]); var ri = -mu * P4B[i];
      for (k = 0; k < 5; k++) ri += P4A[i][k] * x[k] * x[k] * cf[k];
      r.push(ri);
      for (j = 0; j < 3; j++) { var v = 0; for (k = 0; k < 5; k++) v += P4A[i][k] * x[k] * x[k] * P4A[j][k]; M[i].push(v); }
    }
    for (k = 0; k < 3; k++) { // Gaussian elimination (M is symmetric positive definite)
      for (i = k + 1; i < 3; i++) { var f = M[i][k] / M[k][k]; for (j = k; j < 3; j++) M[i][j] -= f * M[k][j]; r[i] -= f * r[k]; }
    }
    var p = [0, 0, 0];
    for (i = 2; i >= 0; i--) { var t = r[i]; for (j = i + 1; j < 3; j++) t -= M[i][j] * p[j]; p[i] = t / M[i][i]; }
    var s = cf.map(function (cv, k) { return cv - (P4A[0][k] * p[0] + P4A[1][k] * p[1] + P4A[2][k] * p[2]); });
    var cx = cf.reduce(function (a, cv, k) { return a + cv * x[k]; }, 0), bp = P4B[0] * p[0] + P4B[1] * p[1] + P4B[2] * p[2];
    return { x: x, p: p, s: s, cx: cx, bp: bp, feasible: s.every(function (v) { return v >= 0; }) };
  }
  // Level lines of a function on a grid (marching squares): segments where val = level.
  function p4contours(plot, fn, box, nx, ny, levels, cls) {
    var X0 = box[0], X1 = box[1], Y0 = box[2], Y1 = box[3], V = [], i, j;
    for (j = 0; j <= ny; j++) { V.push([]); for (i = 0; i <= nx; i++) V[j].push(fn([X0 + (X1 - X0) * i / nx, Y0 + (Y1 - Y0) * j / ny])); }
    function P(i, j) { return [X0 + (X1 - X0) * i / nx, Y0 + (Y1 - Y0) * j / ny]; }
    levels.forEach(function (L) {
      var d = "";
      for (j = 0; j < ny; j++) for (i = 0; i < nx; i++) {
        var a = V[j][i], b = V[j][i + 1], cc = V[j + 1][i + 1], e = V[j + 1][i];
        if (!(isFinite(a) && isFinite(b) && isFinite(cc) && isFinite(e))) continue;
        var pts = [];
        function cut(v1, v2, p1, p2) { if ((v1 - L) * (v2 - L) < 0) { var t = (L - v1) / (v2 - v1); pts.push([p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1])]); } }
        cut(a, b, P(i, j), P(i + 1, j)); cut(b, cc, P(i + 1, j), P(i + 1, j + 1)); cut(cc, e, P(i + 1, j + 1), P(i, j + 1)); cut(e, a, P(i, j + 1), P(i, j));
        for (var k = 0; k + 1 < pts.length; k += 2)
          d += "M" + plot.tx(pts[k][0]).toFixed(1) + " " + plot.ty(pts[k][1]).toFixed(1) + "L" + plot.tx(pts[k + 1][0]).toFixed(1) + " " + plot.ty(pts[k + 1][1]).toFixed(1);
      }
      if (d) el("path", { d: d, "class": cls }, plot.g);
    });
  }
  function p4polygon(plot) {
    plot.poly(P4V.concat([P4V[0]]), "a1");
    plot.poly(P4V.concat([P4V[0]]), "ln c1 thin");
  }
  var P4BOX = [-0.4, 5.6, -0.4, 3.6];
  function p4plot(svg, label) {
    return new Plot(svg, { x: [P4BOX[0], P4BOX[1]], y: [P4BOX[2], P4BOX[3]], w: 680, h: 440, pad: { l: 40, r: 16, t: 16, b: 34 }, label: label });
  }
  function p4axes(plot) {
    plot.axes({ xticks: [0, 1, 2, 3, 4, 5], yticks: [0, 1, 2, 3], xlabel: "x₁", ylabel: "x₂", cross: true });
  }
  // The simplex path (exact, Dantzig's rule, from the slack basis) for a cost c = (c1, c2) on the polygon.
  function p4simplexPath(c) {
    var res = simplex(P4A, P4B, [c[0], c[1], 0, 0, 0], [2, 3, 4]);
    return res.steps.map(function (st) { return [st.x[0].val(), st.x[1].val()]; });
  }

  /* --- 1. The 1D barrier: f(x) = −mu log x + c x (§2) --- */
  WIDGETS.p4barriere1d = function (box) {
    var s = scaffold(box, "La fonction pénalisée f(x) = −μ log x + c x, pour le PL « min c x, x ≥ 0 »");
    var pl = new Plot(s.svg, { x: [0, 4], y: [-2, 4], w: 680, h: 330, pad: { l: 40, r: 16, t: 14, b: 34 }, label: "Graphe de la fonction pénalisée en dimension 1" });
    var muS = slider(s.controls, "log₁₀ μ", -2, 0.6, 0.01, 0, draw);
    var cS = slider(s.controls, "c", -1, 3, 0.05, 1, draw);
    var bar = checkbox(s.controls, "montrer la barrière seule −μ log x", false, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "f(x) = −μ log x + c x"], ["--muted", "c x (μ = 0)"], ["--s3", "minimum x(μ) = μ/c"], ["--s5", "barrière −μ log x"]]);
    function draw() {
      var mu = Math.pow(10, muS.get()), c = cS.get();
      if (Math.abs(c) < 0.025) c = 0;
      muS.out.textContent = "μ = " + p4f(mu, mu < 0.1 ? 3 : 2); cS.out.textContent = p4f(c, 2);
      pl.clear();
      pl.axes({ xticks: [0, 1, 2, 3, 4], yticks: [-2, -1, 0, 1, 2, 3, 4], xlabel: "x", cross: true });
      pl.clip();
      pl.poly([[0, -2], [0, 4]], "ln cm thin");
      pl.fn(function (x) { return c * x; }, "ln cm dash", 2);
      if (bar.checked) pl.fn(function (x) { return x > 0 ? -mu * Math.log(x) : NaN; }, "ln c5 thin", 600, 1e-4, 4);
      pl.fn(function (x) { return x > 0 ? -mu * Math.log(x) + c * x : NaN; }, "ln c2", 800, 1e-4, 4);
      var txt;
      if (c > 0) {
        var xm = mu / c, fm = mu - mu * Math.log(xm);
        pl.seg(xm, -2, xm, fm, "ln c3 thin dot");
        pl.dot(xm, fm, 6, "f3");
        pl.unclip();
        p4sup2(pl, xm, fm, "x", "μ", " = " + p4f(xm, 3), "tx t3", "start", 8, 18);
        txt = "f'(x) = −μ/x + c = 0  ⇔  x = μ/c.   x(μ) = " + p4f(mu, 3) + " / " + p4f(c, 2) + " = " + p4f(xm, 4) + ",  f(x(μ)) = μ − μ log(μ/c) = " + p4f(fm, 4) +
          "\nCoût c·x(μ) = μ = " + p4f(mu, 4) + " : c'est l'écart nμ avec n = 1 (l'optimum du PL est x = 0, de coût 0)." +
          "\nQuand μ → 0, x(μ) → 0 : le minimum glisse vers le bord, qui est la solution du PL.";
      } else if (c === 0) {
        pl.unclip();
        txt = "c = 0 : f(x) = −μ log x décroît vers −∞ quand x → +∞ : pas de minimum.\nPourtant le PL « min 0·x, x ≥ 0 » a des solutions (tous les x ≥ 0) : l'ensemble optimal n'est pas borné. C'est le phénomène de l'exercice 4.2.6.";
      } else {
        pl.unclip();
        txt = "c < 0 : le PL « min c x, x ≥ 0 » n'est pas borné (c x → −∞), et f → −∞ aussi : pas de minimum.";
      }
      ro.textContent = txt;
    }
    draw(); redrawers.push(draw);
  };

  /* --- 2. The central path on the polygon of Ex. 4.2.1 (§4) --- */
  WIDGETS.p4trajectoire = function (box) {
    var s = scaffold(box, "La trajectoire centrale du polygone de l'exercice 4.2.1 (forme standard : n = 5 variables)");
    var pl = p4plot(s.svg, "Polygone, trajectoire centrale, lignes de niveau de la fonction pénalisée");
    var muS = slider(s.controls, "log₁₀ μ", -3, 2, 0.01, 0, draw);
    var cSel = select(s.controls, "coût", [["12", "c = (−1, −2) : optimum unique (2, 3)"], ["11", "c = (−1, −1) : toute une arête est optimale"]], "12", draw);
    var lev = checkbox(s.controls, "lignes de niveau de μπ + c·x", true, draw);
    var sim = checkbox(s.controls, "chemin du simplexe", true, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "ensemble admissible"], ["--text", "trajectoire centrale"], ["--s2", "niveaux de la fonction pénalisée"], ["--s3", "simplexe, optimum"]]);
    function draw() {
      var mu = Math.pow(10, muS.get()), c = cSel.value === "12" ? [-1, -2] : [-1, -1];
      muS.out.textContent = "μ = " + p4e(mu, 3);
      var path = p4path(c), k = 0;
      for (var i = 0; i < path.length; i++) if (Math.abs(Math.log10(path[i][0] / mu)) < Math.abs(Math.log10(path[k][0] / mu))) k = i;
      var u = p4center(mu, c, path[k][1]);
      pl.clear(); p4axes(pl); p4polygon(pl);
      if (lev.checked) {
        var f0 = p4F(u, mu, c);
        p4contours(pl, function (v) { return p4F(v, mu, c); }, [-0.05, 5.05, -0.05, 3.05], 110, 66, [0.5, 1.5, 4, 10, 25].map(function (L) { return f0 + mu * L; }), "ln c2 hair");
      }
      var opt = c[1] === -2 ? [[2, 3]] : null;
      pl.poly(path.map(function (q) { return q[1]; }).concat(opt ? opt : []), "ln ck thin");
      if (sim.checked) {
        var sp = p4simplexPath(c), mk = arrowMarker(s.svg, "f3");
        for (var j = 0; j + 1 < sp.length; j++) pl.seg(sp[j][0], sp[j][1], sp[j + 1][0], sp[j + 1][1], "ln c3 dash", { "marker-end": mk });
        sp.forEach(function (q) { pl.dot(q[0], q[1], 3.5, "f3"); });
      }
      if (opt) { pl.dot(2, 3, 6, "f3"); pl.text(2, 3, "optimum (2, 3)", "tx t3", "end", -10, -6); }
      else { pl.seg(5, 0, 2, 3, "ln c3", { style: "stroke-width:4px" }); pl.text(3.6, 1.4, "arête optimale", "tx t3", "start", 10, 4); }
      pl.dot(P4AC[0], P4AC[1], 4, "ln ck thin nofill");
      pl.dot(u[0], u[1], 6, "fk");
      p4sup2(pl, u[0], u[1], "x", "μ", "", "tx-b", "start", 9, -6);
      var D = p4dual(u, mu, c), prods = D.x.map(function (xi, i) { return xi * D.s[i]; });
      ro.textContent = "μ = " + p4e(mu, 4) + "   x(μ) = " + p4pt(u, 4) + "   (forme standard : x₃, x₄, x₅ = " + D.x.slice(2).map(function (v) { return p4f(v, 3); }).join(" ; ") + ")" +
        "\nc·x(μ) = " + p4f(D.cx, 5) + "   b·p(μ) = " + p4f(D.bp, 5) + "   écart c·x(μ) − b·p(μ) = " + p4e(D.cx - D.bp, 4) + "   nμ = 5μ = " + p4e(5 * mu, 4) +
        "\nproduits x_i s_i / μ (i = 1…5) : " + prods.map(function (v) { return p4f(v / mu, 4); }).join("  ") +
        "\np(μ) = (" + D.p.map(function (v) { return p4f(v, 4); }).join(" ; ") + ")" + (c[1] === -2 ? "   (optimum dual : (0 ; −1/3 ; −4/3))" : "");
    }
    draw(); redrawers.push(draw);
  };

  /* --- 3. Newton's method on the barrier, mu fixed (§5) --- */
  WIDGETS.p4newton = function (box) {
    var s = scaffold(box, "La méthode de Newton sur la fonction pénalisée, μ fixé : cliquez dans le polygone pour choisir le départ");
    var pl = p4plot(s.svg, "Itérés de Newton vers le minimum de la fonction pénalisée");
    var c = [-1, -2];
    var muS = slider(s.controls, "log₁₀ μ", -2, 1, 0.01, -1, reset);
    var pure = checkbox(s.controls, "pas pur (t = 1, sans amortissement)", false, reset);
    button(s.controls, "Un pas de Newton", function () { stepN(1); });
    button(s.controls, "Cinq pas", function () { stepN(5); });
    button(s.controls, "Départ : centre analytique", function () { start = P4AC.slice(); reset(); });
    button(s.controls, "Départ : près du bord (4,8 ; 0,1)", function () { start = [4.8, 0.1]; reset(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s4", "itérés de Newton"], ["--text", "minimum x(μ) (cible)"], ["--s2", "niveaux de la fonction pénalisée"], ["--s6", "pas pur hors du polygone"]]);
    var start = P4AC.slice(), its, info, outPt, conv;
    function reset() { its = [start.slice()]; info = []; outPt = null; conv = false; draw(); }
    function stepN(n) {
      var mu = Math.pow(10, muS.get());
      for (var i = 0; i < n; i++) {
        if (outPt) break;
        var u = its[its.length - 1], r = p4step(u, mu, c, pure.checked);
        if (pure.checked && r.out) { outPt = r.u; info.push({ t: 1, out: true }); break; }
        if (r.t < 1e-10 || r.lam2 < 1e-24) { conv = true; break; }
        its.push(r.u); info.push({ t: r.t, lam2: r.lam2 });
      }
      draw();
    }
    s.svg.addEventListener("pointerdown", function (e) {
      var q = svgPoint(s.svg, e), u = [pl.ix(q.x), pl.iy(q.y)];
      if (p4slacks(u).every(function (v) { return v > 1e-3; })) { start = u; reset(); }
    });
    function draw() {
      var mu = Math.pow(10, muS.get());
      muS.out.textContent = "μ = " + p4e(mu, 3);
      var target = p4center(mu, c, p4path(c)[0][1]);
      target = p4center(mu, c, target);
      pl.clear(); p4axes(pl); p4polygon(pl);
      var f0 = p4F(target, mu, c);
      p4contours(pl, function (v) { return p4F(v, mu, c); }, [-0.05, 5.05, -0.05, 3.05], 110, 66, [0.5, 1.5, 4, 10, 25].map(function (L) { return f0 + mu * L; }), "ln c2 hair");
      pl.dot(target[0], target[1], 7, "ln ck nofill");
      p4sup2(pl, target[0], target[1], "x", "μ", "", "tx-b", "start", 10, 14);
      pl.clip();
      var mk = arrowMarker(s.svg, "f4");
      for (var i = 0; i + 1 < its.length; i++) {
        var a = its[i], b = its[i + 1];
        if (Math.hypot(pl.tx(b[0]) - pl.tx(a[0]), pl.ty(b[1]) - pl.ty(a[1])) > 9) pl.seg(a[0], a[1], b[0], b[1], "ln c4 thin", { "marker-end": mk });
      }
      if (outPt) {
        var mk6 = arrowMarker(s.svg, "f6"), a2 = its[its.length - 1];
        pl.seg(a2[0], a2[1], outPt[0], outPt[1], "ln c6 thin dash", { "marker-end": mk6 });
        pl.dot(outPt[0], outPt[1], 5, "f6");
      }
      pl.unclip();
      its.forEach(function (u, i) { pl.dot(u[0], u[1], i === 0 ? 5 : 3.5, "f4"); });
      var lines = ["μ = " + p4e(mu, 4) + "   cible x(μ) = " + p4pt(target, 6) + "   départ x₀ = " + p4pt(its[0], 3)];
      var first = Math.max(0, its.length - 8);
      for (var k = first; k < its.length; k++) {
        var e = Math.hypot(its[k][0] - target[0], its[k][1] - target[1]);
        lines.push("k = " + k + " :  x = " + p4pt(its[k], 8) + "   erreur ‖x − x(μ)‖ = " + p4e(e, 2) + (k > 0 ? "   pas t = " + p4f(info[k - 1].t, info[k - 1].t < 0.01 ? 4 : 3) : ""));
      }
      if (outPt) lines.push("Le pas pur mène en " + p4pt(outPt, 3) + ", hors du polygone : la barrière n'y est pas définie. Décochez « pas pur ».");
      else if (conv) lines.push("Convergé : en arithmétique flottante, plus aucun pas ne fait diminuer la fonction.");
      else if (its.length === 1) lines.push("Cliquez « Un pas de Newton ».");
      ro.textContent = lines.join("\n");
    }
    reset(); redrawers.push(draw);
  };

  /* --- 4. The path-following algorithm (§5) --- */
  WIDGETS.p4suivi = function (box) {
    var s = scaffold(box, "L'algorithme de suivi de chemin : μ ← σμ, puis quelques pas de Newton amortis");
    var pl = p4plot(s.svg, "Itérés du suivi de chemin sur le polygone");
    var svg2 = addSvg(box, s.svg);
    var gp = new Plot(svg2, { x: [0, 10], y: [-8, 1], w: 680, h: 230, pad: { l: 48, r: 16, t: 14, b: 34 }, label: "Ecart n mu et vraie erreur, échelle logarithmique" });
    var c = [-1, -2], val = -8;
    var sigSel = select(s.controls, "σ =", [["0.5", "0,5"], ["0.3", "0,3"], ["0.1", "0,1"], ["0.01", "0,01"]], "0.3", restart);
    var kSel = select(s.controls, "pas de Newton par valeur de μ", [["1", "1"], ["2", "2"], ["c", "jusqu'au centre"]], "2", restart);
    button(s.controls, "Étape suivante", function () { advance(1); });
    button(s.controls, "Tout dérouler", function () { advance(200); });
    button(s.controls, "Recommencer", restart);
    var ro = readout(s.controls);
    legend(s.legend, [["--text", "trajectoire centrale ; nμ (en bas)"], ["--s4", "itérés ; vraie erreur c·x − min"], ["--s5", "écart c·x − b·p certifié"]]);
    var hist, newt;
    function restart() {
      var mu0 = 1, u0 = p4center(mu0, c, p4path(c)[100][1]);
      hist = [{ mu: mu0, u: u0, its: [u0], newt: 0, D: p4dual(u0, mu0, c) }]; newt = 0; draw();
    }
    function done() { return 5 * hist[hist.length - 1].mu <= 1e-6; }
    function advance(n) {
      var sig = parseFloat(sigSel.value), kk = kSel.value;
      for (var i = 0; i < n && !done(); i++) {
        var last = hist[hist.length - 1], mu = last.mu * sig, u = last.u, its = [];
        var steps = kk === "c" ? 60 : parseInt(kk, 10);
        for (var j = 0; j < steps; j++) {
          var r = p4step(u, mu, c); u = r.u; its.push(u); newt++;
          if (kk === "c" && r.lam2 < 1e-8) break;
        }
        hist.push({ mu: mu, u: u, its: its, newt: newt, D: p4dual(u, mu, c) });
      }
      draw();
    }
    function draw() {
      var sig = parseFloat(sigSel.value);
      pl.clear(); p4axes(pl); p4polygon(pl);
      pl.poly(p4path(c).map(function (q) { return q[1]; }).concat([[2, 3]]), "ln ck thin");
      pl.dot(2, 3, 6, "f3");
      var mk = arrowMarker(s.svg, "f4"), prev = hist[0].u;
      hist.slice(1).forEach(function (h) {
        h.its.forEach(function (q) {
          if (Math.hypot(pl.tx(q[0]) - pl.tx(prev[0]), pl.ty(q[1]) - pl.ty(prev[1])) > 9) pl.seg(prev[0], prev[1], q[0], q[1], "ln c4 thin", { "marker-end": mk });
          prev = q;
        });
      });
      hist.forEach(function (h) { pl.dot(h.u[0], h.u[1], 3.5, "f4"); });
      var last = hist[hist.length - 1];
      pl.dot(last.u[0], last.u[1], 6, "f4");
      // bottom: log10 of n mu, of the true error, and of the certified gap
      var K = Math.max(4, Math.ceil(Math.log(1e-6 / 5) / Math.log(sig)));
      gp.o.x = [0, K]; gp.clear();
      var xt = []; for (var t = 0; t <= K; t += K > 12 ? 2 : 1) xt.push(t);
      gp.axes({ xticks: xt, yticks: [-8, -6, -4, -2, 0], yfmt: function (v) { return "10" + p4sup(v); }, xlabel: "k (valeurs de μ)" });
      var gN = hist.map(function (h, k) { return [k, Math.log10(5 * h.mu)]; });
      var gE = hist.map(function (h, k) { return [k, Math.log10(Math.max(c[0] * h.u[0] + c[1] * h.u[1] - val, 1e-12))]; });
      var gC = hist.map(function (h, k) { return h.D.feasible ? [k, Math.log10(Math.max(h.D.cx - h.D.bp, 1e-12))] : null; });
      gp.poly(gN, "ln ck thin"); gN.forEach(function (q) { gp.dot(q[0], q[1], 3, "fk"); });
      gp.poly(gE, "ln c4"); gE.forEach(function (q) { gp.dot(q[0], q[1], 3.5, "f4"); });
      gp.poly(gC, "ln c5 thin dash"); gC.forEach(function (q) { if (q) gp.dot(q[0], q[1], 2.5, "f5"); });
      var err = c[0] * last.u[0] + c[1] * last.u[1] - val, k = hist.length - 1;
      var lines = ["k = " + k + "   μ = " + p4e(last.mu, 3) + "   x = " + p4pt(last.u, 6) + "   pas de Newton cumulés : " + last.newt,
        "vraie erreur c·x − min = " + p4e(err, 3) + "   nμ = 5μ = " + p4e(5 * last.mu, 3) +
        (last.D.feasible ? "   certificat : p admissible, c·x − b·p = " + p4e(last.D.cx - last.D.bp, 3) : "   certificat : p non admissible (s n'est pas ≥ 0), pas de garantie")];
      if (done()) {
        lines.push(err <= 5 * last.mu * 1.05 && last.D.feasible ? "Terminé : nμ ≤ 10⁻⁶ et l'itéré est assez centré, l'erreur est bien sous nμ." :
          "Terminé en apparence (nμ ≤ 10⁻⁶), mais l'erreur vraie vaut " + p4e(err, 2) + " : l'itéré a décroché de la trajectoire, nμ ne garantit plus rien.");
      }
      ro.textContent = lines.join("\n");
    }
    restart(); redrawers.push(draw);
  };
