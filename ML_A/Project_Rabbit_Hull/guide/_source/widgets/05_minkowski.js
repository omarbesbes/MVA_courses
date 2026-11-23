/* widgets/05_minkowski.js — interactive figures of page 5 (MRH). Inserted inside the scope of app.js. */

/* nearest point of a convex polygon (given by its vertices, 1 to n points) to q; q itself if it is inside */
function p5nearest(P, q) {
  if (P.length === 1) return [P[0][0], P[0][1]];
  var H = P.length >= 3 ? convexHull(P) : P;
  if (H.length >= 3 && pointInConvex(H, q)) return [q[0], q[1]];
  var best = null, bd = Infinity;
  for (var i = 0; i < H.length; i++) {
    if (H.length === 2 && i === 1) break;
    var a = H[i], b = H[(i + 1) % H.length], dx = b[0] - a[0], dy = b[1] - a[1];
    var L = dx * dx + dy * dy, t = L > 0 ? ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / L : 0;
    t = Math.min(Math.max(t, 0), 1);
    var c = [a[0] + t * dx, a[1] + t * dy], d = Math.hypot(c[0] - q[0], c[1] - q[1]);
    if (d < bd) { bd = d; best = c; }
  }
  return best;
}
function p5closed(P) { return P.concat([P[0]]); }

/* ---------------- one attention head ---------------- */
WIDGETS.p5head = function (box) {
  var ui = scaffold(box, "One attention head: the output y = Σ αⱼ vⱼ stays in the hull of the values");
  var plot = new Plot(ui.svg, { w: 560, h: 420, x: [-1, 7], y: [-1, 5.5], label: "Four value vectors, their convex hull and the output of a softmax attention head" });
  var V = [[0.4, 0.3], [5.6, 0.7], [4.3, 4.4], [0.9, 3.6]];
  var X = [1.2, 0.4, -0.6, 0.2], sl = [], tauS, supSel;
  var supports = { all: [0, 1, 2, 3], s123: [0, 1, 2], s12: [0, 1] };
  function alphaOf(tau) {
    var S = supports[supSel.value], x = X.map(function (v, j) { return S.indexOf(j) >= 0 ? v : -Infinity; });
    return softmaxT(x, tau);
  }
  var out;
  function draw() {
    var tau = tauS.get(), a = alphaOf(tau), y = combo(V, a), S = supports[supSel.value];
    plot.clear();
    plot.axes({ xticks: [0, 2, 4, 6], yticks: [0, 2, 4], cross: false });
    var H = convexHull(V);
    plot.poly(p5closed(H), "a1"); plot.poly(p5closed(H), "ln c1 thin");
    if (S.length < 4) {
      var sub = S.map(function (j) { return V[j]; });
      var Hs = convexHull(sub);
      plot.poly(Hs.length > 2 ? p5closed(Hs) : sub, "ln c5");
      if (Hs.length > 2) plot.poly(p5closed(Hs), "a5");
    }
    var path = [];
    for (var i = 0; i <= 60; i++) { var t = 3 * Math.pow(0.05 / 3, i / 60); path.push(combo(V, alphaOf(t))); }
    plot.poly(path, "ln c3 dash thin");
    V.forEach(function (v, j) {
      plot.dot(v[0], v[1], 7, "f1 drag");
      plot.text(v[0], v[1], "v" + (j + 1) + "  α=" + fmt(a[j], 2), "tx", "middle", 0, v[1] > 2 ? -13 : 22);
    });
    plot.dot(y[0], y[1], 7, "f3");
    plot.text(y[0], y[1], "y", "tx-b", "start", 10, -8);
    var inside = pointInConvex(H, y);
    out.textContent = "logits x = (" + X.map(function (v) { return fmt(v, 1); }).join(", ") + "),  τ = " + fmt(tau, 2) +
      "\nα = (" + a.map(function (v) { return fmt(v, 3); }).join(", ") + ")  sum = " + fmt(a.reduce(function (s, v) { return s + v; }, 0), 3) +
      "\ny = (" + fmt(y[0], 3) + ", " + fmt(y[1], 3) + ")   inside conv(V): " + (inside ? "yes" : "no") +
      "\nsmallest weight: " + fmt(Math.min.apply(null, S.map(function (j) { return a[j]; })), 4) + "  (never 0 for a finite τ: y is in the relative interior of the hull of S)";
  }
  for (var j = 0; j < 4; j++) (function (j) {
    var s = slider(ui.controls, "logit x" + (j + 1), -4, 4, 0.1, X[j], function () { X[j] = s.get(); s.out.textContent = fmt(X[j], 1); draw(); });
    s.out.textContent = fmt(X[j], 1); sl.push(s);
  })(j);
  tauS = slider(ui.controls, "temperature τ", 0.05, 3, 0.05, 1, function () { tauS.out.textContent = fmt(tauS.get(), 2); draw(); });
  tauS.out.textContent = "1.00";
  supSel = select(ui.controls, "support", [["all", "all four values"], ["s123", "S = {1, 2, 3}"], ["s12", "S = {1, 2}"]], "all", draw);
  out = readout(ui.controls);
  legend(ui.legend, [["--s1", "values vⱼ (drag them)"], ["--s3", "output y; dashed: y as τ goes from 3 to 0.05"], ["--s5", "hull of the active support S"]]);
  draggable(plot, V, draw, { radius: 24, clamp: function (i, x, y) { return [Math.min(Math.max(x, -0.5), 6.5), Math.min(Math.max(y, -0.5), 5)]; } });
  draw(); redrawers.push(draw);
};

/* ---------------- Minkowski sum of two tiles ---------------- */
WIDGETS.p5sum = function (box) {
  var ui = scaffold(box, "Two tiles: x = p₁ + p₂ lies in P₁ ⊕ P₂");
  var plot = new Plot(ui.svg, { w: 560, h: 440, x: [-6.5, 6.5], y: [-5, 5], label: "Two polygons P1 and P2, one point in each and their Minkowski sum" });
  // points: 0-2 vertices of P1, 3-5 vertices of P2, 6 = p1, 7 = p2
  var pts = [[-2, -1.5], [1.5, -1.2], [-0.5, 1.8], [-1.5, -0.5], [1.5, 1.5], [-0.6, 2], [-0.2, -0.3], [0.5, 0.6]];
  var nSel, out;
  function nb() { return parseInt(nSel.value, 10); }
  function tileA() { return pts.slice(0, 3); }
  function tileB() { return pts.slice(3, 3 + nb()); }
  function fixIn() { var a = p5nearest(tileA(), pts[6]); pts[6] = a; var b = p5nearest(tileB(), pts[7]); pts[7] = b; }
  function draw() {
    fixIn();
    var A = tileA(), B = tileB(), HA = convexHull(A), HB = B.length > 2 ? convexHull(B) : B;
    var Sm = minkowskiSum(HA, HB), p1 = pts[6], p2 = pts[7], x = [p1[0] + p2[0], p1[1] + p2[1]];
    plot.clear();
    plot.axes({ xticks: [-4, -2, 0, 2, 4], yticks: [-4, -2, 0, 2, 4], cross: true });
    plot.poly(p5closed(Sm), "am"); plot.poly(p5closed(Sm), "ln cm");
    Sm.forEach(function (v) { plot.dot(v[0], v[1], 3.5, "fm"); });
    // P2 translated by p1: it lies inside the sum and touches it
    var T2 = HB.map(function (b) { return [b[0] + p1[0], b[1] + p1[1]]; });
    plot.poly(HB.length > 2 ? p5closed(T2) : T2, "ln c5 dash thin");
    plot.poly(p5closed(HA), "a1"); plot.poly(p5closed(HA), "ln c1");
    plot.poly(HB.length > 2 ? p5closed(HB) : HB, "ln c5");
    if (HB.length > 2) plot.poly(p5closed(HB), "a5");
    plot.text(HA[0][0], HA[0][1], "P₁", "tx-b", "end", -8, 14);
    plot.text(HB[0][0], HB[0][1], "P₂", "tx-b", "end", -8, -8);
    plot.text(Sm[0][0], Sm[0][1], "P₁ ⊕ P₂", "tx-b", "middle", 0, 20);
    A.forEach(function (v) { plot.dot(v[0], v[1], 6, "f1 drag"); });
    B.forEach(function (v) { plot.dot(v[0], v[1], 6, "f5 drag"); });
    plot.dot(p1[0], p1[1], 6, "f1"); plot.dot(p2[0], p2[1], 6, "f5");
    plot.text(p1[0], p1[1], "p₁", "tx", "start", 8, -8); plot.text(p2[0], p2[1], "p₂", "tx", "start", 8, -8);
    plot.seg(0, 0, p1[0], p1[1], "ln c1 thin"); plot.seg(p1[0], p1[1], x[0], x[1], "ln c5 thin");
    plot.dot(x[0], x[1], 8, "f3"); plot.text(x[0], x[1], "x = p₁ + p₂", "tx-b", "start", 10, -10);
    out.textContent = "p₁ = (" + fmt(p1[0], 2) + ", " + fmt(p1[1], 2) + "),  p₂ = (" + fmt(p2[0], 2) + ", " + fmt(p2[1], 2) + "),  x = (" + fmt(x[0], 2) + ", " + fmt(x[1], 2) + ")" +
      "\nvertices: P₁ " + HA.length + ", P₂ " + HB.length + ", P₁ ⊕ P₂ " + Sm.length + "  (at most " + (HA.length + HB.length) + ": the edges of the sum are the edges of the summands, merged by direction)" +
      "\nsupport in direction (1, 1): h₁ = " + fmt(supportFn(HA, [1, 1]), 2) + "  +  h₂ = " + fmt(supportFn(HB, [1, 1]), 2) + "  =  h₁₊₂ = " + fmt(supportFn(Sm, [1, 1]), 2);
  }
  nSel = select(ui.controls, "tile P₂ has", [["2", "2 vertices (a segment)"], ["3", "3 vertices (a triangle)"]], "2", draw);
  out = readout(ui.controls);
  legend(ui.legend, [["--s1", "tile P₁ and p₁"], ["--s5", "tile P₂ (dashed: P₂ + p₁) and p₂"], ["--s3", "x = p₁ + p₂"], ["--muted", "P₁ ⊕ P₂"]]);
  draggable(plot, pts, draw, {
    radius: 24,
    fixed: function (i) { return i === 5 && nb() < 3; },
    clamp: function (i, x, y) {
      if (i < 6) return [Math.min(Math.max(x, -2.5), 2.5), Math.min(Math.max(y, -2.5), 2.5)];
      return i === 6 ? p5nearest(tileA(), [x, y]) : p5nearest(tileB(), [x, y]);
    }
  });
  draw(); redrawers.push(draw);
};

/* ---------------- directional versus archetypal steering ---------------- */
WIDGETS.p5steer = function (box) {
  var ui = scaffold(box, "Steering: along a direction, or towards an archetype");
  var plot = new Plot(ui.svg, { w: 560, h: 340, x: [-1.5, 8], y: [-1.5, 5.5], label: "A polytope, a start point, a steering direction and an archetype" });
  var svg2 = addSvg(box, ui.svg);
  var plot2 = new Plot(svg2, { w: 560, h: 250, x: [0, 2.5], y: [0, 1.05], label: "Proximity to the archetype as a function of the steering strength" });
  var P = [[0.5, 0.2], [5.5, 0.8], [4.6, 4.2], [0.2, 3.2]], a = P[1];
  var pts = [[1.2, 1.4]], angS, sS, out;
  function draw() {
    var x = pts[0], L = Math.hypot(a[0] - x[0], a[1] - x[1]), th = angS.get() * Math.PI / 180, u = [Math.cos(th), Math.sin(th)], s = sS.get();
    var dirAt = function (t) { return [x[0] + t * L * u[0], x[1] + t * L * u[1]]; };
    var arcAt = function (t) { t = Math.min(t, 1); return [x[0] + t * (a[0] - x[0]), x[1] + t * (a[1] - x[1])]; };
    var prox = function (p) { return Math.exp(-Math.hypot(p[0] - a[0], p[1] - a[1])); };
    plot.clear();
    plot.axes({ xticks: [0, 2, 4, 6], yticks: [0, 2, 4] });
    plot.clip();
    plot.poly(p5closed(P), "a1"); plot.poly(p5closed(P), "ln c1 thin");
    plot.seg(x[0], x[1], dirAt(2.5)[0], dirAt(2.5)[1], "ln c2 dash thin");
    plot.seg(x[0], x[1], a[0], a[1], "ln c1 dash thin");
    var d = dirAt(s), r = arcAt(s);
    plot.seg(x[0], x[1], d[0], d[1], "ln c2"); plot.seg(x[0], x[1], r[0], r[1], "ln c1");
    plot.dot(a[0], a[1], 7, "f1"); plot.text(a[0], a[1], "archetype a", "tx-b", "end", -10, 4);
    plot.dot(x[0], x[1], 7, "f3 drag"); plot.text(x[0], x[1], "x (drag)", "tx", "start", 10, 16);
    plot.dot(d[0], d[1], 6, "f2"); plot.dot(r[0], r[1], 6, "f1");
    // curves
    plot2.clear();
    plot2.axes({ xticks: [0, 0.5, 1, 1.5, 2, 2.5], yticks: [0, 0.5, 1], xd: 1, yd: 1, xlabel: "steering strength s (in units of ‖a − x‖)", ylabel: "proximity exp(−‖xₛ − a‖)" });
    plot2.fn(function (t) { return prox(dirAt(t)); }, "ln c2", 200);
    plot2.fn(function (t) { return prox(arcAt(t)); }, "ln c1", 200, 0, 1);
    plot2.seg(1, prox(a), 2.5, prox(a), "ln c1 dash thin");
    plot2.dot(s, prox(d), 6, "f2"); plot2.dot(Math.min(s, 2.5), prox(r), 6, "f1");
    var sStar = Math.max(0, ((a[0] - x[0]) * u[0] + (a[1] - x[1]) * u[1]) / L);
    var dperp = Math.abs((a[0] - x[0]) * u[1] - (a[1] - x[1]) * u[0]);
    out.textContent = "‖a − x‖ = " + fmt(L, 2) + ",  s = " + fmt(s, 2) +
      "\ndirectional: x + s‖a−x‖u is " + (pointInConvex(P, d) ? "inside" : "OUTSIDE") + " the polytope; proximity " + fmt(prox(d), 3) + "; best at s* = " + fmt(sStar, 2) + " with proximity exp(−" + fmt(dperp, 2) + ") = " + fmt(Math.exp(-dperp), 3) +
      "\narchetypal: x + min(s,1)(a−x) is " + (pointInConvex(P, r) ? "inside" : "OUTSIDE") + " the polytope; proximity " + fmt(prox(r), 3) + "; reaches 1 at s = 1";
  }
  angS = slider(ui.controls, "direction u (degrees)", -180, 180, 1, 20, function () { angS.out.textContent = fmt(angS.get(), 0) + "°"; draw(); });
  angS.out.textContent = "20°";
  sS = slider(ui.controls, "strength s", 0, 2.5, 0.02, 0.8, function () { sS.out.textContent = fmt(sS.get(), 2); draw(); });
  sS.out.textContent = "0.80";
  out = readout(ui.controls);
  legend(ui.legend, [["--s2", "directional: x + s‖a−x‖u"], ["--s1", "archetypal: x + s(a − x), s ≤ 1"], ["--s3", "start x"]]);
  draggable(plot, pts, draw, { radius: 26, clamp: function (i, x, y) { return p5nearest(P, [x, y]); } });
  draw(); redrawers.push(draw);
};

/* ---------------- the hexagon: two decompositions ---------------- */
WIDGETS.p5hexagon = function (box) {
  var ui = scaffold(box, "The regular hexagon is a sum of three segments and also a triangle plus its reflection");
  var plot = new Plot(ui.svg, { w: 560, h: 420, x: [-1.81, 1.81], y: [-1.3, 1.3], label: "A regular hexagon, a point in it, and two decompositions of the point" });
  var R3 = Math.sqrt(3), H = [];
  for (var k = 0; k < 6; k++) H.push([Math.cos(k * Math.PI / 3), Math.sin(k * Math.PI / 3)]);
  var D = [[1, 0], [0.5, R3 / 2], [-0.5, R3 / 2]];               // directions of the three segments (0, 60, 120 degrees)
  var T = [[-0.5, -R3 / 6], [0.5, -R3 / 6], [0, R3 / 3]];         // centred equilateral triangle of side 1
  var pts = [[0.5, 0]], modeSel, sS, rS, out;
  function solve3(M, b) { // Cramer
    var det = function (m) { return m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]); };
    var d = det(M), r = [];
    for (var c = 0; c < 3; c++) { var Mc = M.map(function (row, i) { var q = row.slice(); q[c] = b[i]; return q; }); r.push(det(Mc) / d); }
    return r;
  }
  function draw() {
    var x = pts[0], mode = modeSel.value;
    plot.clear();
    plot.axes({ xticks: [-1, 0, 1], yticks: [-1, 0, 1], cross: true });
    plot.poly(p5closed(H), "am"); plot.poly(p5closed(H), "ln cm");
    var msg;
    if (mode === "seg") {
      var c = x[1] / (R3 / 2);
      // t = (x1 - c/2 + s, c - s, s) with |t_k| <= 1/2
      var lo2 = Math.max(-0.5, -0.5 - (x[0] - 0.5 * c), c - 0.5), hi2 = Math.min(0.5, 0.5 - (x[0] - 0.5 * c), c + 0.5);
      var s = Math.min(Math.max(sS.get(), lo2), hi2);
      var t = [x[0] - 0.5 * c + s, c - s, s];
      D.forEach(function (d, i) { plot.seg(-0.5 * d[0], -0.5 * d[1], 0.5 * d[0], 0.5 * d[1], "ln c2 thin"); });
      var cur = [0, 0], cols = ["c2", "c3", "c5"];
      t.forEach(function (ti, i) {
        var nx = [cur[0] + ti * D[i][0], cur[1] + ti * D[i][1]];
        plot.seg(cur[0], cur[1], nx[0], nx[1], "ln " + cols[i]);
        plot.dot(nx[0], nx[1], 4, "fk"); cur = nx;
      });
      msg = "three segments [−½, ½]·dₖ at 0°, 60°, 120°:  x = t₁d₁ + t₂d₂ + t₃d₃\nt = (" + t.map(function (v) { return fmt(v, 3); }).join(", ") + "),  each |tₖ| ≤ ½;  free parameter s = t₃ ∈ [" + fmt(lo2, 3) + ", " + fmt(hi2, 3) + "]  (null direction (1, −1, 1))";
    } else {
      var w = solve3([[T[0][0], T[1][0], T[2][0]], [T[0][1], T[1][1], T[2][1]], [1, 1, 1]], [x[0], x[1], 0]);
      var wp = w.map(function (v) { return Math.max(v, 0); }), wm = w.map(function (v) { return Math.max(-v, 0); });
      var r = wp.reduce(function (a, b) { return a + b; }, 0), rho = rS.get(), e = [(1 - rho) / 3 + rho, (1 - rho) / 3, (1 - rho) / 3];
      var lam = wp.map(function (v, i) { return v + (1 - r) * e[i]; }), mu = wm.map(function (v, i) { return v + (1 - r) * e[i]; });
      var p = combo(T, lam), q = combo(T, mu), mq = [-q[0], -q[1]];
      plot.poly(p5closed(T), "a1"); plot.poly(p5closed(T), "ln c1 thin");
      var mT = T.map(function (v) { return [-v[0], -v[1]]; });
      plot.poly(p5closed(mT), "a5"); plot.poly(p5closed(mT), "ln c5 thin");
      plot.seg(0, 0, p[0], p[1], "ln c1"); plot.seg(p[0], p[1], p[0] + mq[0], p[1] + mq[1], "ln c5");
      plot.dot(p[0], p[1], 5, "f1"); plot.dot(mq[0], mq[1], 5, "f5");
      plot.text(p[0], p[1], "p ∈ T", "tx", "start", 7, -7); plot.text(mq[0], mq[1], "−q ∈ −T", "tx", "start", 7, 14);
      msg = "T ⊕ (−T), T an equilateral triangle of side 1:  x = p − q\nλ = (" + lam.map(function (v) { return fmt(v, 3); }).join(", ") + ") for p,  μ = (" + mu.map(function (v) { return fmt(v, 3); }).join(", ") + ") for q;  both sum to 1";
    }
    plot.dot(x[0], x[1], 8, "f3 drag"); plot.text(x[0], x[1], "x", "tx-b", "start", 10, -10);
    out.textContent = msg + "\nx = (" + fmt(x[0], 3) + ", " + fmt(x[1], 3) + ")";
  }
  modeSel = select(ui.controls, "decomposition", [["seg", "three segments"], ["tri", "triangle + reflection"]], "seg", draw);
  sS = slider(ui.controls, "segments: free parameter s", -0.5, 0.5, 0.01, 0, function () { sS.out.textContent = fmt(sS.get(), 2); draw(); });
  sS.out.textContent = "0.00";
  rS = slider(ui.controls, "triangles: slack ρ", 0, 1, 0.01, 0, function () { rS.out.textContent = fmt(rS.get(), 2); draw(); });
  rS.out.textContent = "0.00";
  out = readout(ui.controls);
  legend(ui.legend, [["--s3", "the point x (drag it)"], ["--s2", "segments"], ["--s1", "T"], ["--s5", "−T"]]);
  draggable(plot, pts, draw, { radius: 30, clamp: function (i, x, y) { return p5nearest(H, [x, y]); } });
  draw(); redrawers.push(draw);
};
