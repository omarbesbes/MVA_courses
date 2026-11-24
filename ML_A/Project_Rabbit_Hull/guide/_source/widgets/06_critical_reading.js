/* widgets/06_critical_reading.js — interactive figures of page 6 (critical reading). Inserted inside the scope of app.js. */

/* Gamma(shape) sampler (Marsaglia-Tsang, with the boost for shape < 1) and derived samplers */
function p6gamma(rng, a) {
  if (a < 1) return p6gamma(rng, a + 1) * Math.pow(rng(), 1 / a);
  var d = a - 1 / 3, c = 1 / Math.sqrt(9 * d);
  for (;;) {
    var x = gaussRand(rng), v = 1 + c * x;
    if (v <= 0) continue;
    v = v * v * v;
    var u = rng();
    if (Math.log(u) < 0.5 * x * x + d - d * v + d * Math.log(v)) return d * v;
  }
}
function p6beta(rng, a) { var g1 = p6gamma(rng, a), g2 = p6gamma(rng, a); return g1 / (g1 + g2); }
function p6dirichlet3(rng, a) {
  var g = [p6gamma(rng, a), p6gamma(rng, a), p6gamma(rng, a)], s = g[0] + g[1] + g[2];
  return [g[0] / s, g[1] / s, g[2] / s];
}
function p6close(P) { return P.concat([P[0]]); }

/* ---------------- a budget inside a tile: box or simplex ---------------- */
WIDGETS.p6budget = function (box) {
  var ui = scaffold(box, "Two features of one group: free codes (a square) or a shared unit budget (a triangle)");
  var pc = new Plot(ui.svg, { w: 420, h: 420, x: [-0.15, 1.15], y: [-0.15, 1.15], label: "Feasible set of the codes (z1, z2) with sample points" });
  var svg2 = addSvg(box, ui.svg);
  var pa = new Plot(svg2, { w: 560, h: 420, x: [-2, 3.6], y: [-0.9, 3.13], label: "The resulting cloud of activations x = z1 g1 + z2 g2" });
  var wrap = document.createElement("div");
  wrap.style.cssText = "display:flex;flex-wrap:wrap;gap:0.6rem;align-items:center;justify-content:center";
  ui.svg.parentNode.insertBefore(wrap, ui.svg); wrap.appendChild(ui.svg); wrap.appendChild(svg2);
  [ui.svg, svg2].forEach(function (sv) { sv.style.cssText = "flex:1 1 270px;min-width:0;max-width:400px;width:auto;height:auto"; });
  var modeSel, aS, phiS, nS, seedBtn, showOther, out, seed = 1;
  var L = 1.6;
  function gens() {
    var phi = phiS.get() * Math.PI / 180;
    return [[L, 0], [L * Math.cos(phi), L * Math.sin(phi)]];
  }
  function sample(mode, a, n, sd) {
    var rng = mulberry32(sd * 7919 + (mode === "box" ? 1 : 2)), Z = [];
    for (var i = 0; i < n; i++) {
      if (mode === "box") Z.push([p6beta(rng, a), p6beta(rng, a)]);
      else { var w = p6dirichlet3(rng, a); Z.push([w[1], w[2]]); }
    }
    return Z;
  }
  function feas(mode, G) {   // feasible polygon in code space and in activation space
    var C = mode === "box" ? [[0, 0], [1, 0], [1, 1], [0, 1]] : [[0, 0], [1, 0], [0, 1]];
    var X = C.map(function (z) { return [z[0] * G[0][0] + z[1] * G[1][0], z[0] * G[0][1] + z[1] * G[1][1]]; });
    return [C, X];
  }
  function draw() {
    var mode = modeSel.value, other = mode === "box" ? "simplex" : "box", a = aS.get(), n = Math.round(nS.get()), G = gens();
    var f = feas(mode, G), fo = feas(mode === "box" ? "simplex" : "box", G);
    var Z = sample(mode, a, n, seed);
    var cls = mode === "box" ? "2" : "1";
    pc.clear(); pc.axes({ xticks: [0, 0.5, 1], yticks: [0, 0.5, 1], xd: 1, yd: 1, xlabel: "z₁", ylabel: "z₂" });
    pa.clear(); pa.axes({ xticks: [0, 1, 2, 3], yticks: [0, 1, 2, 3], nogrid: false });
    if (showOther.checked) {
      pc.poly(p6close(fo[0]), "ln cm dash thin"); pa.poly(p6close(fo[1]), "ln cm dash thin");
    }
    pc.poly(p6close(f[0]), "a" + cls); pc.poly(p6close(f[0]), "ln c" + cls);
    pa.poly(p6close(f[1]), "a" + cls); pa.poly(p6close(f[1]), "ln c" + cls);
    // the line z1 + z2 = 1
    pc.seg(0, 1, 1, 0, "ln cm thin dash");
    var over = 0, sum = 0;
    Z.forEach(function (z) {
      var x = z[0] * G[0][0] + z[1] * G[1][0], y = z[0] * G[0][1] + z[1] * G[1][1];
      if (z[0] + z[1] > 1 + 1e-9) over++;
      sum += z[0] + z[1];
      pc.dot(z[0], z[1], 2.4, "f3"); pa.dot(x, y, 2.4, "f3");
    });
    pa.seg(0, 0, G[0][0], G[0][1], "ln c5"); pa.seg(0, 0, G[1][0], G[1][1], "ln c5");
    pa.text(G[0][0], G[0][1], "g₁", "tx-b", "start", 6, 14); pa.text(G[1][0], G[1][1], "g₂", "tx-b", "start", 6, -6);
    pc.text(1, 0, "(1, 0)", "tx", "end", -4, -6); pc.text(0, 1, "(0, 1)", "tx", "start", 6, 14);
    var det = Math.abs(G[0][0] * G[1][1] - G[0][1] * G[1][0]);
    out.textContent = (mode === "box" ? "box: z₁, z₂ independent, Beta(α, α)" : "simplex: (1−z₁−z₂, z₁, z₂) ~ Dirichlet(α, α, α)") +
      ",  α = " + fmt(a, 2) + ",  N = " + n +
      "\nsample with z₁ + z₂ > 1: " + fmt(100 * over / n, 1) + " %   (a unit budget forbids them: 0 % for the triangle)" +
      "\nmean z₁ + z₂ = " + fmt(sum / n, 3) +
      "\narea of the set of activations = |det(g₁, g₂)| × " + (mode === "box" ? "1" : "½") + " = " + fmt(det * (mode === "box" ? 1 : 0.5), 3);
  }
  modeSel = select(ui.controls, "codes of the group", [["box", "box (free)"], ["simplex", "triangle (unit budget)"]], "box", draw);
  aS = slider(ui.controls, "concentration α (small = near the corners)", 0.2, 3, 0.1, 0.5, function () { aS.out.textContent = fmt(aS.get(), 1); draw(); });
  aS.out.textContent = "0.5";
  phiS = slider(ui.controls, "angle between g₁ and g₂", 30, 150, 5, 70, function () { phiS.out.textContent = Math.round(phiS.get()) + "°"; draw(); });
  phiS.out.textContent = "70°";
  nS = slider(ui.controls, "points", 100, 1000, 50, 400, function () { nS.out.textContent = Math.round(nS.get()); draw(); });
  nS.out.textContent = "400";
  seedBtn = button(ui.controls, "new sample", function () { seed++; draw(); });
  showOther = checkbox(ui.controls, "outline the other set", true, draw);
  out = readout(ui.controls);
  legend(ui.legend, [["--s2", "box (linear code, bounded)"], ["--s1", "triangle (one tile of three archetypes)"], ["--s3", "sampled codes and activations"], ["--s5", "generators g₁, g₂"]]);
  draw(); redrawers.push(draw);
};

/* ---------------- a chord of an ellipse leaves it ---------------- */
WIDGETS.p6chord = function (box) {
  var ui = scaffold(box, "Two points on the curve of normalised tokens: the chord, the depth of its midpoint, and a polygon");
  var plot = new Plot(ui.svg, { w: 560, h: 410, x: [-3.8, 3.8], y: [-2.73, 2.73], label: "An ellipse with a chord between two of its points and an inscribed polygon" });
  var rS, t1S, t2S, nS, polyCk, out;
  function ellipse(a, b, n) { var P = []; for (var i = 0; i <= n; i++) { var t = 2 * Math.PI * i / n; P.push([a * Math.cos(t), b * Math.sin(t)]); } return P; }
  function dist2(a, b, q, t) { var dx = a * Math.cos(t) - q[0], dy = b * Math.sin(t) - q[1]; return dx * dx + dy * dy; }
  function nearest(a, b, q) {    // exact distance from q to the ellipse and the nearest point (grid + golden section)
    var best = Infinity, bt = 0, N = 720, i, t;
    for (i = 0; i < N; i++) { t = 2 * Math.PI * i / N; var d = dist2(a, b, q, t); if (d < best) { best = d; bt = t; } }
    var lo = bt - 2 * Math.PI / N, hi = bt + 2 * Math.PI / N, g = 0.6180339887;
    for (i = 0; i < 60; i++) {
      var m1 = hi - g * (hi - lo), m2 = lo + g * (hi - lo);
      if (dist2(a, b, q, m1) < dist2(a, b, q, m2)) hi = m2; else lo = m1;
    }
    t = (lo + hi) / 2;
    return { d: Math.sqrt(dist2(a, b, q, t)), p: [a * Math.cos(t), b * Math.sin(t)] };
  }
  function draw() {
    var rho = rS.get(), a = 2.0 * Math.sqrt(rho), b = 2.0 / Math.sqrt(rho);
    var t1 = t1S.get() * Math.PI / 180, t2 = t2S.get() * Math.PI / 180, n = Math.round(nS.get());
    var P1 = [a * Math.cos(t1), b * Math.sin(t1)], P2 = [a * Math.cos(t2), b * Math.sin(t2)];
    var M = [(P1[0] + P2[0]) / 2, (P1[1] + P2[1]) / 2];
    plot.clear(); plot.axes({ xticks: [-3, 0, 3], yticks: [-2, 0, 2], cross: true });
    var E = ellipse(a, b, 240);
    plot.poly(E, "a1"); plot.poly(E, "ln c1");
    if (polyCk.checked) {
      var Q = [];
      for (var k = 0; k < n; k++) { var tk = t1 + 2 * Math.PI * k / n; Q.push([a * Math.cos(tk), b * Math.sin(tk)]); }
      plot.poly(p6close(Q), "a5"); plot.poly(p6close(Q), "ln c5");
      Q.forEach(function (q) { plot.dot(q[0], q[1], 4, "f5"); });
    }
    var rad = Math.sqrt(M[0] * M[0] / (a * a) + M[1] * M[1] / (b * b)), R = [M[0] / rad, M[1] / rad];
    var nn = nearest(a, b, M);
    plot.seg(P1[0], P1[1], P2[0], P2[1], "ln c2");
    plot.seg(M[0], M[1], nn.p[0], nn.p[1], "ln c3");
    plot.dot(P1[0], P1[1], 6, "f1"); plot.dot(P2[0], P2[1], 6, "f1");
    plot.dot(M[0], M[1], 5, "f2"); plot.dot(nn.p[0], nn.p[1], 4, "f3");
    plot.text(P1[0], P1[1], "y", "tx-b", "start", 8, -8); plot.text(P2[0], P2[1], "y′", "tx-b", "start", 8, -8);
    plot.text(M[0], M[1], "midpoint", "tx", "start", 8, 14);
    var chord = Math.hypot(P1[0] - P2[0], P1[1] - P2[1]);
    var dth = Math.abs(t1S.get() - t2S.get()); if (dth > 180) dth = 360 - dth;
    var th = dth * Math.PI / 180;
    var msg = "chord ‖y − y′‖ = " + fmt(chord, 3) + ",  half-chord = " + fmt(chord / 2, 3) +
      "\nangle θ between the two points in the circle space (u) = " + fmt(dth, 1) + "°" +
      "\nexact distance from the midpoint to the curve = " + fmt(nn.d, 3) + "  = " + fmt(100 * nn.d / (chord / 2 + 1e-12), 1) + " % of the half-chord" +
      "\ndistance along the ray from the centre = " + fmt(Math.hypot(M[0] - R[0], M[1] - R[1]), 3) +
      "\ncircle formula: depth/half-chord = tan(θ/4) = " + fmt(Math.tan(th / 4), 3) + "  (exact when the axis ratio is 1; ‖midpoint‖ = √d·cos(θ/2) there)";
    if (polyCk.checked) msg += "\npolygon with " + n + " vertices: only its vertices lie on the curve; each edge leaves it, with depth tan(π/2n) = " + fmt(Math.tan(Math.PI / (2 * n)), 3) + " of its half-edge on a circle";
    out.textContent = msg;
  }
  rS = slider(ui.controls, "axis ratio γ<sub>max</sub>/γ<sub>min</sub> (shape of the ellipse)", 1, 3, 0.1, 1.5, function () { rS.out.textContent = fmt(rS.get(), 1); draw(); });
  rS.out.textContent = "1.5";
  t1S = slider(ui.controls, "point y: angle", 0, 360, 1, 70, function () { t1S.out.textContent = Math.round(t1S.get()) + "°"; draw(); });
  t1S.out.textContent = "70°";
  t2S = slider(ui.controls, "point y′: angle", 0, 360, 1, 130, function () { t2S.out.textContent = Math.round(t2S.get()) + "°"; draw(); });
  t2S.out.textContent = "130°";
  polyCk = checkbox(ui.controls, "inscribed polygon (a would-be summand)", false, draw);
  nS = slider(ui.controls, "polygon vertices", 3, 8, 1, 4, function () { nS.out.textContent = Math.round(nS.get()); draw(); });
  nS.out.textContent = "4";
  out = readout(ui.controls);
  legend(ui.legend, [["--s1", "the curve of normalised tokens"], ["--s2", "chord and its midpoint"], ["--s3", "nearest point of the curve"], ["--s5", "inscribed polygon"]]);
  draw(); redrawers.push(draw);
};
