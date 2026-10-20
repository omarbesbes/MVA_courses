// widgets/Lesson02.js — interactive figures of Lesson 2 (Kantorovich's relaxation, the discrete problem).
// Inserted by build.mjs inside the scope of app.js: it uses el, Plot, scaffold, slider, select, button, checkbox,
// readout, legend, fmt, frac, mulberry32, svgPoint and hungarian, and registers its widgets in WIDGETS.
// Own helpers are prefixed l2.

  /* ---------------- helpers of this page ---------------- */
  // Number with at most 3 decimals, without trailing zeros: 0.30 -> "0.3".
  function l2n(x, d) {
    if (d === undefined) d = 3;
    var s = fmt(x, d);
    if (s.indexOf(".") >= 0) s = s.replace(/0+$/, "").replace(/\.$/, "");
    return s === "-0" ? "0" : s;
  }
  function l2zeros(n, m) { var P = []; for (var i = 0; i < n; i++) { P.push([]); for (var j = 0; j < m; j++) P[i].push(0); } return P; }
  // North-west corner rule on integer masses (exact). Returns the list of steps {i, j, t, rowDone, colDone}.
  function l2northWest(ka, kb) {
    var r = ka.slice(), c = kb.slice(), i = 0, j = 0, steps = [];
    while (i < r.length && j < c.length) {
      var t = Math.min(r[i], c[j]);
      r[i] -= t; c[j] -= t;
      var rd = r[i] === 0, cd = c[j] === 0;
      steps.push({ i: i, j: j, t: t, rowDone: rd, colDone: cd, r: r.slice(), c: c.slice() });
      if (rd) i++;
      if (cd) j++;
    }
    return steps;
  }
  // Exact optimal plan between integer-weighted atoms (weights k/N): duplicate the atoms and solve an assignment
  // problem with the Hungarian method (rational weights = duplicated uniform matching, OT4ML Prop. 3.21).
  function l2exactPlan(ka, kb, cost) { // cost(i, j); returns {U: plan in units, total: sum of unit costs}
    var du = [], dv = [], i, j;
    for (i = 0; i < ka.length; i++) for (var k = 0; k < ka[i]; k++) du.push(i);
    for (j = 0; j < kb.length; j++) for (var l = 0; l < kb[j]; l++) dv.push(j);
    var Cm = du.map(function (ii) { return dv.map(function (jj) { return cost(ii, jj); }); });
    var asg = hungarian(Cm), U = l2zeros(ka.length, kb.length), total = 0;
    for (var u = 0; u < du.length; u++) { U[du[u]][dv[asg[u]]] += 1; total += Cm[u][asg[u]]; }
    return { U: U, total: total };
  }
  function l2line(g, x1, y1, x2, y2, cls, extra) {
    var a = { x1: x1, y1: y1, x2: x2, y2: y2, "class": cls };
    for (var k in extra || {}) a[k] = extra[k];
    return el("line", a, g);
  }
  function l2text(g, x, y, s, cls, anchor, extra) {
    var a = { x: x, y: y, "class": cls || "tx-s", "text-anchor": anchor || "start" };
    for (var k in extra || {}) a[k] = extra[k];
    var t = el("text", a, g); t.textContent = s; return t;
  }
  function l2clear(svg) { while (svg.firstChild) svg.removeChild(svg.firstChild); return el("g", {}, svg); }

  /* ======================================================================
     1. The transport polytope of a 2 x 3 problem (§5), with the network simplex (§7)
     ====================================================================== */
  WIDGETS.l2polytope = function (box) {
    var sc = scaffold(box, "The couplings of a 2 × 3 problem form a polygon: drag the orange point, watch the plan and its cost");
    var W = 680, H = 360;
    sc.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    sc.svg.setAttribute("role", "img");
    sc.svg.setAttribute("aria-label", "The transport polytope in the coordinates s = P11, t = P12, with cost level lines, and the corresponding plan");
    var WEIGHTS = {
      gen: { a: [0.6, 0.4], b: [0.3, 0.45, 0.25] },
      deg: { a: [0.5, 0.5], b: [0.25, 0.5, 0.25] }
    };
    var xs = [0, 1], ys = [0, 1, 2];
    var COSTS = {
      q: function (i, j) { var d = xs[i] - ys[j]; return d * d; },
      l1: function (i, j) { return Math.abs(xs[i] - ys[j]); },
      sq: function (i, j) { return Math.sqrt(Math.abs(xs[i] - ys[j])); },
      mat: function (i, j) { return [[3, 1, 2], [1, 2, 4]][i][j]; }
    };
    var wSel = select(sc.controls, "Weights", [["gen", "a = (0.6, 0.4), b = (0.3, 0.45, 0.25)"], ["deg", "a = (½, ½), b = (¼, ½, ¼)"]], "gen", function () { cur = productPoint(); basis = null; msg = ""; draw(); });
    var cSel = select(sc.controls, "Cost", [["q", "|x − y|² on the line"], ["l1", "|x − y| on the line"], ["sq", "√|x − y| (concave)"], ["mat", "the matrix C = (3 1 2 / 1 2 4)"]], "mat", function () { basis = null; msg = ""; draw(); });
    button(sc.controls, "Product a ⊗ b", function () { cur = productPoint(); basis = null; msg = "The product plan a ⊗ b: every entry positive, an interior point."; draw(); });
    button(sc.controls, "North-west corner", function () { var P = nwPlan(); cur = { s: P[0][0], t: P[0][1] }; basis = null; msg = "The north-west corner plan: a vertex, found without looking at the cost."; draw(); });
    button(sc.controls, "Simplex: one pivot", pivot);
    button(sc.controls, "Jump to the optimum", function () { var o = optimum(); cur = { s: o.v[0], t: o.v[1] }; basis = null; msg = "An optimal vertex (the minimum of a linear cost over a polygon is attained at a vertex)."; draw(); });
    var ro = readout(sc.controls);
    legend(sc.legend, [["--s2", "current coupling"], ["--s3", "optimal vertex, plan"], ["--text", "vertices"], ["--muted", "cost level lines"]]);
    var cur, basis = null, msg = "", dragging = false;
    var PX = { x0: 64, y0: 22, w: 270, h: 270, lo: -0.04, hi: 0.56 };
    function X(s) { return PX.x0 + (s - PX.lo) / (PX.hi - PX.lo) * PX.w; }
    function Y(t) { return PX.y0 + PX.h - (t - PX.lo) / (PX.hi - PX.lo) * PX.h; }
    function wts() { return WEIGHTS[wSel.value]; }
    function plan(s, t) { var a = wts().a, b = wts().b; return [[s, t, a[0] - s - t], [b[0] - s, b[1] - t, b[2] - a[0] + s + t]]; }
    function costOf(P) { var f = COSTS[cSel.value], c = 0; for (var i = 0; i < 2; i++) for (var j = 0; j < 3; j++) c += P[i][j] * f(i, j); return c; }
    function cons() { // alpha s + beta t + gamma >= 0 (one line per entry of P)
      var a = wts().a, b = wts().b;
      return [[1, 0, 0], [0, 1, 0], [-1, -1, a[0]], [-1, 0, b[0]], [0, -1, b[1]], [1, 1, b[2] - a[0]]];
    }
    function feasible(p, tol) { return cons().every(function (c) { return c[0] * p[0] + c[1] * p[1] + c[2] >= -(tol || 1e-12); }); }
    function vertices() {
      var C = cons(), V = [], k, l;
      for (k = 0; k < C.length; k++) for (l = k + 1; l < C.length; l++) {
        var det = C[k][0] * C[l][1] - C[k][1] * C[l][0];
        if (Math.abs(det) < 1e-12) continue;
        var p = [(-C[k][2] * C[l][1] + C[k][1] * C[l][2]) / det, (-C[k][0] * C[l][2] + C[k][2] * C[l][0]) / det];
        if (feasible(p, 1e-10) && !V.some(function (q) { return Math.hypot(q[0] - p[0], q[1] - p[1]) < 1e-9; })) V.push(p);
      }
      var cx = 0, cy = 0; V.forEach(function (p) { cx += p[0]; cy += p[1]; }); cx /= V.length; cy /= V.length;
      V.sort(function (p, q) { return Math.atan2(p[1] - cy, p[0] - cx) - Math.atan2(q[1] - cy, q[0] - cx); });
      return V;
    }
    function productPoint() { var a = wts().a, b = wts().b; return { s: a[0] * b[0], t: a[0] * b[1] }; }
    function nwPlan() { // north-west corner on the weights (floating point, tolerance)
      var a = wts().a.slice(), b = wts().b.slice(), P = l2zeros(2, 3), i = 0, j = 0;
      while (i < 2 && j < 3) { var t = Math.min(a[i], b[j]); P[i][j] = t; a[i] -= t; b[j] -= t; var rd = a[i] < 1e-12, cd = b[j] < 1e-12; if (rd) i++; if (cd) j++; }
      return P;
    }
    function optimum() {
      var V = vertices(), best = null;
      V.forEach(function (v) { var c = costOf(plan(v[0], v[1])); if (!best || c < best.c - 1e-12) best = { v: v, c: c }; });
      best.all = V.filter(function (v) { return Math.abs(costOf(plan(v[0], v[1])) - best.c) < 1e-9; });
      return best;
    }
    function project(p) {
      if (feasible(p)) return p;
      var V = vertices(), best = null;
      for (var k = 0; k < V.length; k++) {
        var A = V[k], B = V[(k + 1) % V.length], dx = B[0] - A[0], dy = B[1] - A[1];
        var u = Math.max(0, Math.min(1, ((p[0] - A[0]) * dx + (p[1] - A[1]) * dy) / (dx * dx + dy * dy)));
        var q = [A[0] + u * dx, A[1] + u * dy], d = Math.hypot(q[0] - p[0], q[1] - p[1]);
        if (!best || d < best.d) best = { q: q, d: d };
      }
      return best.q;
    }
    function snap(p) { // snap to a vertex when within 7 pixels
      var V = vertices();
      for (var k = 0; k < V.length; k++) if (Math.hypot(X(V[k][0]) - X(p[0]), Y(V[k][1]) - Y(p[1])) < 7) return V[k].slice();
      return p;
    }
    function where(P) {
      var nz = 0, i, j; for (i = 0; i < 2; i++) for (j = 0; j < 3; j++) if (P[i][j] > 1e-9) nz++;
      var V = vertices(), isV = V.some(function (v) { return Math.hypot(v[0] - cur.s, v[1] - cur.t) < 1e-9; });
      var onEdge = !isV && cons().some(function (c) { return Math.abs(c[0] * cur.s + c[1] * cur.t + c[2]) < 1e-9; });
      return { nz: nz, kind: isV ? "a vertex" : onEdge ? "on an edge" : "inside the polygon" };
    }
    /* ---- transportation simplex on the current vertex ---- */
    function treeBasis(P) {
      var n = 2, m = 3, parent = [0, 1, 2, 3, 4], cells = [], i, j;
      function find(x) { while (parent[x] !== x) x = parent[x] = parent[parent[x]]; return x; }
      for (i = 0; i < n; i++) for (j = 0; j < m; j++) if (P[i][j] > 1e-9) {
        var ri = find(i), rj = find(n + j);
        if (ri === rj) return null; // a cycle in the support: not a vertex
        parent[ri] = rj; cells.push([i, j]);
      }
      var f = COSTS[cSel.value], cand = [];
      for (i = 0; i < n; i++) for (j = 0; j < m; j++) if (P[i][j] <= 1e-9) cand.push([i, j, f(i, j)]);
      cand.sort(function (p, q) { return p[2] - q[2]; });
      cand.forEach(function (c) { var ri = find(c[0]), rj = find(n + c[1]); if (cells.length < n + m - 1 && ri !== rj) { parent[ri] = rj; cells.push([c[0], c[1]]); } });
      return cells;
    }
    function potentials(B) {
      var f = COSTS[cSel.value], u = [0, null], v = [null, null, null], changed = true;
      while (changed) {
        changed = false;
        B.forEach(function (c) {
          if (u[c[0]] !== null && v[c[1]] === null) { v[c[1]] = f(c[0], c[1]) - u[c[0]]; changed = true; }
          else if (v[c[1]] !== null && u[c[0]] === null) { u[c[0]] = f(c[0], c[1]) - v[c[1]]; changed = true; }
        });
      }
      return { u: u, v: v };
    }
    function pivot() {
      var P = plan(cur.s, cur.t), f = COSTS[cSel.value], i, j;
      var w = where(P);
      if (w.kind !== "a vertex") { msg = "The simplex walks from vertex to vertex: first put the point on a vertex (for instance with “North-west corner”)."; draw(); return; }
      if (!basis) basis = treeBasis(P);
      var pot = potentials(basis), u = pot.u, v = pot.v;
      var red = [[0, 0, 0], [0, 0, 0]], best = null;
      for (i = 0; i < 2; i++) for (j = 0; j < 3; j++) {
        red[i][j] = f(i, j) - u[i] - v[j];
        var inB = basis.some(function (c) { return c[0] === i && c[1] === j; });
        if (!inB && red[i][j] < -1e-12 && (!best || red[i][j] < best.r)) best = { i: i, j: j, r: red[i][j] };
      }
      var head = "potentials u = (" + u.map(function (z) { return l2n(z); }).join(", ") + "), v = (" + v.map(function (z) { return l2n(z); }).join(", ") +
        ");  reduced costs r = C − u − v = [[" + red[0].map(function (z) { return l2n(z); }).join(", ") + "], [" + red[1].map(function (z) { return l2n(z); }).join(", ") + "]]";
      if (!best) { msg = head + "\nAll reduced costs ≥ 0: the potentials certify that this vertex is optimal (complementary slackness, §7). Cost " + l2n(costOf(P), 4) + "."; draw(); return; }
      // the cycle closed by the entering cell: path in the tree from row best.i to column best.j
      var adj = {}, key = function (t, k) { return t + k; };
      basis.forEach(function (c) { (adj[key("r", c[0])] = adj[key("r", c[0])] || []).push(["c", c[1]]); (adj[key("c", c[1])] = adj[key("c", c[1])] || []).push(["r", c[0]]); });
      var par = {}; par[key("r", best.i)] = null; var stack = [["r", best.i]];
      while (stack.length) { var nd = stack.pop(); (adj[key(nd[0], nd[1])] || []).forEach(function (nb) { if (!(key(nb[0], nb[1]) in par)) { par[key(nb[0], nb[1])] = nd; stack.push(nb); } }); }
      var cyc = [], node = ["c", best.j];
      while (par[key(node[0], node[1])]) { var pv = par[key(node[0], node[1])]; cyc.push(pv[0] === "r" ? [pv[1], node[1]] : [node[1], pv[1]]); node = pv; }
      cyc.reverse();
      var minus = cyc.filter(function (c, k) { return k % 2 === 0; }), plus = cyc.filter(function (c, k) { return k % 2 === 1; });
      var theta = Math.min.apply(null, minus.map(function (c) { return P[c[0]][c[1]]; }));
      var leave = minus.filter(function (c) { return P[c[0]][c[1]] <= theta + 1e-12; })[0];
      var before = costOf(P);
      minus.forEach(function (c) { P[c[0]][c[1]] -= theta; });
      plus.forEach(function (c) { P[c[0]][c[1]] += theta; });
      P[best.i][best.j] += theta;
      basis = basis.filter(function (c) { return !(c[0] === leave[0] && c[1] === leave[1]); }).concat([[best.i, best.j]]);
      cur = { s: P[0][0], t: P[0][1] };
      msg = head + "\nEnter cell (" + (best.i + 1) + "," + (best.j + 1) + ") with r = " + l2n(best.r) + "; push θ = " + l2n(theta) + " around the cycle; cell (" + (leave[0] + 1) + "," + (leave[1] + 1) + ") leaves.  Cost " + l2n(before, 4) + " → " + l2n(costOf(P), 4) + " (change θ·r = " + l2n(theta * best.r, 4) + ")" + (theta < 1e-12 ? "  — a degenerate pivot: the basis changed, the plan did not." : "");
      draw(true);
    }
    /* ---- pointer ---- */
    function toST(e) { var p = svgPoint(sc.svg, e); return [PX.lo + (p.x - PX.x0) / PX.w * (PX.hi - PX.lo), PX.lo + (PX.y0 + PX.h - p.y) / PX.h * (PX.hi - PX.lo)]; }
    function inPanel(e) { var p = svgPoint(sc.svg, e); return p.x > PX.x0 - 10 && p.x < PX.x0 + PX.w + 10 && p.y > PX.y0 - 10 && p.y < PX.y0 + PX.h + 10; }
    sc.svg.addEventListener("pointerdown", function (e) {
      if (!inPanel(e)) return;
      dragging = true; e.preventDefault();
      try { sc.svg.setPointerCapture(e.pointerId); } catch (err) {}
      var q = snap(project(toST(e))); cur = { s: q[0], t: q[1] }; basis = null; msg = ""; draw();
    });
    sc.svg.addEventListener("pointermove", function (e) { if (!dragging) return; e.preventDefault(); var q = snap(project(toST(e))); cur = { s: q[0], t: q[1] }; basis = null; msg = ""; draw(); });
    sc.svg.addEventListener("pointerup", function () { dragging = false; });
    sc.svg.addEventListener("pointercancel", function () { dragging = false; });
    /* ---- drawing ---- */
    function draw(keepBasis) {
      if (!keepBasis && basis && !dragging) { /* keep the basis only along simplex pivots */ }
      var g = l2clear(sc.svg), V = vertices(), P = plan(cur.s, cur.t), opt = optimum(), f = COSTS[cSel.value], i, j, k;
      // panel frame, grid, ticks
      var clipId = "l2pclip" + Math.random().toString(36).slice(2);
      var cp = el("clipPath", { id: clipId }, sc.svg); el("rect", { x: PX.x0, y: PX.y0, width: PX.w, height: PX.h }, cp);
      [0, 0.1, 0.2, 0.3, 0.4, 0.5].forEach(function (v) {
        l2line(g, X(v), PX.y0, X(v), PX.y0 + PX.h, "gr"); l2line(g, PX.x0, Y(v), PX.x0 + PX.w, Y(v), "gr");
        l2text(g, X(v), PX.y0 + PX.h + 14, l2n(v), "tx-s", "middle"); l2text(g, PX.x0 - 5, Y(v) + 4, l2n(v), "tx-s", "end");
      });
      l2line(g, X(0), PX.y0, X(0), PX.y0 + PX.h, "ax"); l2line(g, PX.x0, Y(0), PX.x0 + PX.w, Y(0), "ax");
      l2text(g, PX.x0 + PX.w, PX.y0 + PX.h + 30, "s = P₁₁", "tx-s", "end");
      l2text(g, PX.x0 + 4, PX.y0 - 8, "t = P₁₂", "tx-s", "start");
      // level lines of the cost: c0 + gs s + gt t
      var c0 = costOf(plan(0, 0)), gs = costOf(plan(1, 0)) - c0, gt = costOf(plan(0, 1)) - c0;
      var gc = el("g", { "clip-path": "url(#" + clipId + ")" }, g);
      var cs = [PX.lo, PX.hi].map(function (s) { return [PX.lo, PX.hi].map(function (t) { return c0 + gs * s + gt * t; }); });
      var cmin = Math.min(cs[0][0], cs[0][1], cs[1][0], cs[1][1]), cmax = Math.max(cs[0][0], cs[0][1], cs[1][0], cs[1][1]);
      for (k = 1; k < 12; k++) {
        var L = cmin + (cmax - cmin) * k / 12, pts = [];
        if (Math.abs(gt) > 1e-12) { [PX.lo, PX.hi].forEach(function (s) { pts.push([s, (L - c0 - gs * s) / gt]); }); }
        else { [PX.lo, PX.hi].forEach(function (t) { pts.push([(L - c0 - gt * t) / gs, t]); }); }
        l2line(gc, X(pts[0][0]), Y(pts[0][1]), X(pts[1][0]), Y(pts[1][1]), "ln cm hair dash");
      }
      // the optimal level line
      var Lo = opt.c, q0, q1;
      if (Math.abs(gt) > 1e-12) { q0 = [PX.lo, (Lo - c0 - gs * PX.lo) / gt]; q1 = [PX.hi, (Lo - c0 - gs * PX.hi) / gt]; }
      else { q0 = [(Lo - c0 - gt * PX.lo) / gs, PX.lo]; q1 = [(Lo - c0 - gt * PX.hi) / gs, PX.hi]; }
      l2line(gc, X(q0[0]), Y(q0[1]), X(q1[0]), Y(q1[1]), "ln c3 thin dash");
      // polygon
      var d = V.map(function (v, k) { return (k ? "L" : "M") + X(v[0]).toFixed(1) + " " + Y(v[1]).toFixed(1); }).join("") + "Z";
      el("path", { d: d, "class": "a3 ln c3 thin" }, g);
      // vertices with their cost
      var cx = 0, cy = 0; V.forEach(function (v) { cx += v[0]; cy += v[1]; }); cx /= V.length; cy /= V.length;
      V.forEach(function (v) {
        var isOpt = opt.all.some(function (o) { return Math.hypot(o[0] - v[0], o[1] - v[1]) < 1e-9; });
        el("circle", { cx: X(v[0]), cy: Y(v[1]), r: isOpt ? 6 : 4.5, "class": isOpt ? "f3" : "fk" }, g);
        var dx = X(v[0]) - X(cx), dy = Y(v[1]) - Y(cy), L2 = Math.hypot(dx, dy) || 1;
        l2text(g, X(v[0]) + dx / L2 * 16, Y(v[1]) + dy / L2 * 16 + 4, l2n(costOf(plan(v[0], v[1])), 3), isOpt ? "tx-s t3" : "tx-s", "middle");
      });
      // product plan marker and current point
      var pp = productPoint();
      el("circle", { cx: X(pp.s), cy: Y(pp.t), r: 3.5, "class": "fm" }, g);
      l2text(g, X(pp.s) + 6, Y(pp.t) + 12, "a ⊗ b", "tx-s", "start");
      el("circle", { cx: X(cur.s), cy: Y(cur.t), r: 7.5, "class": "f2 drag" }, g);
      // right panel: the plan on the line
      var R0 = 400, R1 = 664, yS = 54, yT = 150;
      function RX(v) { return R0 + (v + 0.3) / 2.6 * (R1 - R0); }
      l2line(g, R0, yS, R1, yS, "gr"); l2line(g, R0, yT, R1, yT, "gr");
      for (i = 0; i < 2; i++) for (j = 0; j < 3; j++) if (P[i][j] > 1e-9)
        l2line(g, RX(xs[i]), yS + 6, RX(ys[j]), yT - 6, "ln c3", { "stroke-width": (1 + 22 * P[i][j]).toFixed(2), "stroke-opacity": 0.6 });
      var a = wts().a, b = wts().b;
      for (i = 0; i < 2; i++) { el("circle", { cx: RX(xs[i]), cy: yS, r: (3 + 12 * Math.sqrt(a[i])).toFixed(1), "class": "f2" }, g); l2text(g, RX(xs[i]), yS - 16, "x" + "₁₂"[i] + " (" + l2n(a[i]) + ")", "tx-s t2", "middle"); }
      for (j = 0; j < 3; j++) { el("circle", { cx: RX(ys[j]), cy: yT, r: (3 + 12 * Math.sqrt(b[j])).toFixed(1), "class": "f1" }, g); l2text(g, RX(ys[j]), yT + 26, "y" + "₁₂₃"[j] + " (" + l2n(b[j]) + ")", "tx-s t1", "middle"); }
      // the matrix with its marginals, and the cost matrix
      var w = where(P), mx = 410, my = 214;
      l2text(g, mx, my, "P", "tx-i", "start");
      for (i = 0; i < 2; i++) {
        for (j = 0; j < 3; j++) l2text(g, mx + 40 + j * 46, my + 18 * i, l2n(Math.max(0, P[i][j]), 3), P[i][j] > 1e-9 ? "tx-s t3" : "tx-s", "end");
        l2text(g, mx + 40 + 3 * 46 + 6, my + 18 * i, "| " + l2n(a[i]), "tx-s t2", "start");
      }
      for (j = 0; j < 3; j++) l2text(g, mx + 40 + j * 46, my + 38, l2n(b[j]), "tx-s t1", "end");
      l2text(g, mx + 40 + 3 * 46 + 6, my + 38, "← column sums", "tx-s", "start");
      l2text(g, mx, my + 64, "C", "tx-i", "start");
      for (i = 0; i < 2; i++) for (j = 0; j < 3; j++) l2text(g, mx + 40 + j * 46, my + 64 + 18 * i, l2n(f(i, j), 3), "tx-s", "end");
      l2text(g, mx, my + 112, "⟨C, P⟩ = " + l2n(costOf(P), 4) + "   (optimum " + l2n(opt.c, 4) + ")", "tx-b", "start");
      l2text(g, mx, my + 130, w.nz + " non-zero entries; the point is " + w.kind, "tx-s", "start");
      ro.textContent = (msg ? msg + "\n" : "") + "s = " + l2n(cur.s) + ", t = " + l2n(cur.t) + ": " + w.nz + " non-zero entries (n + m − 1 = 4, nm = 6); " +
        (opt.all.length > 1 ? "several optimal vertices: a whole edge of the polygon is optimal." : "the optimum is a single vertex.");
    }
    cur = productPoint();
    draw(); redrawers.push(function () { draw(true); });
  };

  /* ======================================================================
     2. The north-west corner rule, one step at a time (§4)
     ====================================================================== */
  WIDGETS.l2nw = function (box) {
    var sc = scaffold(box, "The north-west corner rule, one step at a time — and its cost against the exact optimum");
    var W = 680, H = 400;
    sc.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    sc.svg.setAttribute("role", "img");
    sc.svg.setAttribute("aria-label", "A transport matrix filled from its top-left corner, and the same plan drawn on the real line");
    var PRESETS = {
      book: { x: [0, 1, 2], y: [0.5, 1.5, 2.5], ka: [2, 5, 3], kb: [5, 1, 4], N: 10 },
      sheet: { x: [0, 1, 2], y: [0.5, 1.5, 2.5], ka: [11, 8, 11], kb: [10, 10, 10], N: 10 },
      five: { x: [0, 1, 2, 3, 4], y: [0.5, 1.2, 2, 2.6, 3.3, 4.2], ka: [2, 5, 6, 4, 3], kb: [4, 2, 3, 5, 4, 2], N: 20 }
    };
    var pSel = select(sc.controls, "Example", [["book", "a = (0.2, 0.5, 0.3), b = (0.5, 0.1, 0.4)"], ["sheet", "sheet, Ex. 1: a = (1.1, 0.8, 1.1), b = (1, 1, 1)"], ["five", "5 and 6 bins"], ["random", "random histograms"]], "book", function () { load(); });
    var eSel = select(sc.controls, "cost |x − y|^p, p =", [["2", "2"], ["1", "1"], ["0.5", "½ (concave)"]], "2", function () { draw(); });
    var shuf = checkbox(sc.controls, "targets in a shuffled order", false, function () { load(true); });
    button(sc.controls, "Step", function () { if (k < steps.length) k++; draw(); });
    button(sc.controls, "Run to the end", function () { k = steps.length; draw(); });
    button(sc.controls, "Reset", function () { k = 0; draw(); });
    var ro = readout(sc.controls);
    legend(sc.legend, [["--s2", "sources (rows), masses a"], ["--s1", "targets (columns), masses b"], ["--s3", "mass sent so far"]]);
    var D, order, steps, k = 0, seed = 5;
    function load(keepData) {
      if (!keepData || !D) {
        if (pSel.value === "random") {
          var rng = mulberry32(100 + 17 * seed++), n = 3 + Math.floor(rng() * 3), m = 3 + Math.floor(rng() * 4), N = 20;
          function units(cnt) { var u = []; for (var q = 0; q < cnt; q++) u.push(1); for (q = cnt; q < N; q++) u[Math.floor(rng() * cnt)]++; return u; }
          function pos(cnt) { var p = []; for (var q = 0; q < cnt; q++) p.push(Math.round(rng() * 50) / 10); return p.sort(function (u, v) { return u - v; }); }
          D = { x: pos(n), y: pos(m), ka: units(n), kb: units(m), N: N };
        } else D = PRESETS[pSel.value];
      }
      order = D.y.map(function (v, j) { return j; });
      if (shuf.checked) { var r2 = mulberry32(7); for (var q = order.length - 1; q > 0; q--) { var z = Math.floor(r2() * (q + 1)), tmp = order[q]; order[q] = order[z]; order[z] = tmp; } if (order.every(function (v, j) { return v === j; })) order.reverse(); }
      steps = l2northWest(D.ka, order.map(function (j) { return D.kb[j]; }));
      k = 0; draw();
    }
    function mass(u) { return l2n(u / D.N, 3); }
    function draw() {
      var g = l2clear(sc.svg), n = D.x.length, m = D.y.length, p = parseFloat(eSel.value), i, j, q;
      var cell = Math.min(46, 270 / m), x0 = 92, y0 = 82;
      // marginals: bars
      var amax = Math.max.apply(null, D.ka), bmax = Math.max.apply(null, D.kb);
      l2text(g, x0 + m * cell / 2, 16, "the transport table (columns in processing order)", "tx-b", "middle");
      // residuals after k steps
      var U = l2zeros(n, m), rr = D.ka.slice(), cc = order.map(function (jj) { return D.kb[jj]; });
      for (q = 0; q < k; q++) { var st = steps[q]; U[st.i][st.j] += st.t; rr = st.r; cc = st.c; }
      for (j = 0; j < m; j++) {
        var hb = 28 * D.kb[order[j]] / bmax;
        el("rect", { x: x0 + j * cell + cell * 0.25, y: y0 - 6 - hb, width: cell * 0.5, height: hb, "class": "a1 ln c1 thin" }, g);
        l2text(g, x0 + (j + 0.5) * cell, y0 - 10 - hb, mass(D.kb[order[j]]), "tx-s t1", "middle");
      }
      for (i = 0; i < n; i++) {
        var wa = 34 * D.ka[i] / amax;
        el("rect", { x: x0 - 8 - wa, y: y0 + i * cell + cell * 0.25, width: wa, height: cell * 0.5, "class": "a2 ln c2 thin" }, g);
        l2text(g, x0 - 12 - wa, y0 + (i + 0.5) * cell + 4, mass(D.ka[i]), "tx-s t2", "end");
      }
      for (i = 0; i <= n; i++) l2line(g, x0, y0 + i * cell, x0 + m * cell, y0 + i * cell, "gr");
      for (j = 0; j <= m; j++) l2line(g, x0 + j * cell, y0, x0 + j * cell, y0 + n * cell, "gr");
      // path so far
      for (q = 1; q < k; q++) {
        var s0 = steps[q - 1], s1 = steps[q];
        l2line(g, x0 + (s0.j + 0.5) * cell, y0 + (s0.i + 0.5) * cell, x0 + (s1.j + 0.5) * cell, y0 + (s1.i + 0.5) * cell, "ln c3 thin", { "stroke-opacity": 0.5 });
      }
      for (i = 0; i < n; i++) for (j = 0; j < m; j++) if (U[i][j] > 0) {
        el("circle", { cx: x0 + (j + 0.5) * cell, cy: y0 + (i + 0.5) * cell, r: Math.min(cell * 0.45, 3 + 0.42 * cell * Math.sqrt(U[i][j] / Math.max(amax, bmax))), "class": "f3", "fill-opacity": 0.35 }, g);
        l2text(g, x0 + (j + 0.5) * cell, y0 + (i + 0.5) * cell + 4, mass(U[i][j]), "tx-s", "middle");
      }
      if (k > 0) { var last = steps[k - 1]; el("rect", { x: x0 + last.j * cell + 1, y: y0 + last.i * cell + 1, width: cell - 2, height: cell - 2, "class": "ln c3 nofill" }, g); }
      if (k < steps.length) { var nx = steps[k]; el("rect", { x: x0 + nx.j * cell + 3, y: y0 + nx.i * cell + 3, width: cell - 6, height: cell - 6, "class": "ln c2 thin dash nofill" }, g); }
      // residuals
      l2text(g, x0 + m * cell + 8, y0 - 8, "left in row", "tx-s", "start");
      for (i = 0; i < n; i++) l2text(g, x0 + m * cell + 8, y0 + (i + 0.5) * cell + 4, mass(rr[i]), rr[i] === 0 ? "tx-s" : "tx-s t2", "start");
      l2text(g, x0 - 8, y0 + n * cell + 16, "left in column", "tx-s", "end");
      for (j = 0; j < m; j++) l2text(g, x0 + (j + 0.5) * cell, y0 + n * cell + 16, mass(cc[j]), cc[j] === 0 ? "tx-s" : "tx-s t1", "middle");
      // the line
      var all = D.x.concat(D.y), lo = Math.min.apply(null, all) - 0.4, hi = Math.max.apply(null, all) + 0.4;
      var L0 = 440, L1 = 668, yS = 92, yT = 300;
      function LX(v) { return L0 + (v - lo) / (hi - lo) * (L1 - L0); }
      l2text(g, (L0 + L1) / 2, 16, "on the line", "tx-b", "middle");
      l2line(g, L0, yS, L1, yS, "gr"); l2line(g, L0, yT, L1, yT, "gr");
      for (q = 0; q < k; q++) {
        var s = steps[q];
        l2line(g, LX(D.x[s.i]), yS + 6, LX(D.y[order[s.j]]), yT - 6, "ln c3", { "stroke-width": (1 + 16 * s.t / D.N / Math.max(1, (amax + bmax) / D.N)).toFixed(2), "stroke-opacity": 0.6 });
      }
      for (i = 0; i < n; i++) { el("circle", { cx: LX(D.x[i]), cy: yS, r: (3 + 9 * Math.sqrt(D.ka[i] / amax)).toFixed(1), "class": "f2" }, g); l2text(g, LX(D.x[i]), yS - 16, "x=" + l2n(D.x[i]), "tx-s t2", "middle"); }
      for (j = 0; j < m; j++) { el("circle", { cx: LX(D.y[j]), cy: yT, r: (3 + 9 * Math.sqrt(D.kb[j] / bmax)).toFixed(1), "class": "f1" }, g); l2text(g, LX(D.y[j]), yT + 22 + (j % 2) * 12, "y=" + l2n(D.y[j]), "tx-s t1", "middle"); }
      // text
      var txt;
      if (k === 0) txt = "Press Step: the dashed cell is filled with min(left in row, left in column).";
      else {
        var s2 = steps[k - 1];
        txt = "Step " + k + ": cell (" + (s2.i + 1) + ", " + (s2.j + 1) + ") receives min(" + mass(s2.t + s2.r[s2.i]) + ", " + mass(s2.t + s2.c[s2.j]) + ") = " + mass(s2.t) + ".  " +
          (s2.rowDone && s2.colDone ? "Row and column exhausted together: move diagonally (a degenerate step)." : s2.rowDone ? "Row " + (s2.i + 1) + " exhausted: move down." : "Column " + (s2.j + 1) + " exhausted: move right.");
      }
      if (k === steps.length) {
        var nz = steps.length, cost = function (ii, jj) { return Math.pow(Math.abs(D.x[ii] - D.y[jj]), p); };
        var nwc = 0; steps.forEach(function (s3) { nwc += s3.t * cost(s3.i, order[s3.j]); }); nwc /= D.N;
        var ex = l2exactPlan(D.ka, D.kb, cost), opt = ex.total / D.N;
        var rel = (nwc - opt) / Math.max(opt, 1e-12);
        txt += "\nDone: " + nz + " filled cells (n + m − 1 = " + (n + m - 1) + "). Cost: north-west " + l2n(nwc, 4) + ", exact optimum " + l2n(opt, 4) +
          (rel < 1e-9 ? "  ✓ the north-west plan is optimal." : "  ✗ north-west is " + fmt(100 * rel, 1) + " % above the optimum.") +
          (shuf.checked ? "  (Targets not sorted: the rule ignores the cost.)" : p < 1 ? "  (Concave cost: sorting is not enough.)" : "  (Sorted points, convex cost: Prop. 3.10.)");
      }
      ro.textContent = txt;
    }
    load(); redrawers.push(draw);
  };

  /* ======================================================================
     3. Birkhoff–von Neumann decomposition (§6)
     ====================================================================== */
  WIDGETS.l2bvn = function (box) {
    var sc = scaffold(box, "Birkhoff–von Neumann: peel a bistochastic matrix, one permutation at a time");
    var W = 680, H = 330;
    sc.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    sc.svg.setAttribute("role", "img");
    sc.svg.setAttribute("aria-label", "A residual bistochastic matrix and the permutation matrices extracted from it with their weights");
    var mSel = select(sc.controls, "Matrix", [["text", "the 3 × 3 example of §6"], ["ex", "the 4 × 4 matrix of Exercise 13.6"], ["dense4", "random dense 4 × 4"], ["dense5", "random dense 5 × 5"], ["mix", "mixture of 3 permutations, 5 × 5"]], "text", function () { load(); });
    var rSel = select(sc.controls, "Matching", [["big", "largest λ first"], ["any", "any perfect matching"]], "big", function () { reset(); });
    button(sc.controls, "Extract one permutation", step);
    button(sc.controls, "Run to the end", function () { var guard = 0; while (total() > 1e-9 && guard++ < 60) step(true); draw(); });
    button(sc.controls, "Reset", reset);
    button(sc.controls, "New random matrix", function () { seed++; load(); });
    var ro = readout(sc.controls);
    legend(sc.legend, [["--s3", "support of the residual; outlined: the permutation just extracted"]]);
    var P0, R, terms, lastSig = null, seed = 1, info = "";
    function total() { var s = 0; R[0].forEach(function (v) { s += v; }); return s; }
    function randPerm(n, rng) { var p = []; for (var i = 0; i < n; i++) p.push(i); for (i = n - 1; i > 0; i--) { var j = Math.floor(rng() * (i + 1)), t = p[i]; p[i] = p[j]; p[j] = t; } return p; }
    function load() {
      var v = mSel.value, rng = mulberry32(31 + 97 * seed), n, i, j;
      if (v === "text") P0 = [[0.6, 0.4, 0], [0.4, 0.3, 0.3], [0, 0.3, 0.7]];
      else if (v === "ex") P0 = [[0.5, 0.5, 0, 0], [0.25, 0.25, 0.5, 0], [0.25, 0, 0.25, 0.5], [0, 0.25, 0.25, 0.5]];
      else if (v === "mix") {
        n = 5; P0 = l2zeros(n, n); var w = [rng() + 0.2, rng() + 0.2, rng() + 0.2], sw = w[0] + w[1] + w[2];
        for (var k = 0; k < 3; k++) { var s = randPerm(n, rng); for (i = 0; i < n; i++) P0[i][s[i]] += w[k] / sw; }
      } else {
        n = v === "dense4" ? 4 : 5; P0 = l2zeros(n, n);
        for (i = 0; i < n; i++) for (j = 0; j < n; j++) P0[i][j] = 0.15 + rng();
        for (var it = 0; it < 3000; it++) {
          for (i = 0; i < n; i++) { var rs = 0; for (j = 0; j < n; j++) rs += P0[i][j]; for (j = 0; j < n; j++) P0[i][j] /= rs; }
          for (j = 0; j < n; j++) { var cs = 0; for (i = 0; i < n; i++) cs += P0[i][j]; for (i = 0; i < n; i++) P0[i][j] /= cs; }
        }
      }
      reset();
    }
    function reset() { R = P0.map(function (r) { return r.slice(); }); terms = []; lastSig = null; info = "Press “Extract one permutation”."; draw(); }
    function matching(minVal) { // a perfect matching inside {R >= minVal}, or null
      var n = R.length, C = R.map(function (r) { return r.map(function (v) { return v >= minVal ? 0 : 1; }); });
      var a = hungarian(C), ok = true;
      for (var i = 0; i < n; i++) if (C[i][a[i]] !== 0) ok = false;
      return ok ? a : null;
    }
    function step(silent) {
      var n = R.length, tol = 1e-9;
      if (total() <= tol) { info = "Nothing left: the residual is zero."; if (!silent) draw(); return; }
      var sig;
      if (rSel.value === "any") sig = matching(tol);
      else {
        var vals = []; R.forEach(function (r) { r.forEach(function (v) { if (v > tol) vals.push(v); }); });
        vals.sort(function (u, v) { return v - u; });
        for (var q = 0; q < vals.length && !sig; q++) sig = matching(vals[q] - 1e-12);
      }
      if (!sig) { info = "No perfect matching found (this cannot happen for a bistochastic residual: Hall's condition)."; if (!silent) draw(); return; }
      var lam = Infinity, i;
      for (i = 0; i < n; i++) lam = Math.min(lam, R[i][sig[i]]);
      for (i = 0; i < n; i++) { R[i][sig[i]] -= lam; if (R[i][sig[i]] < tol) R[i][sig[i]] = 0; }
      terms.push({ lam: lam, sig: Array.prototype.slice.call(sig) });
      lastSig = Array.prototype.slice.call(sig);
      info = "Extracted σ = [" + lastSig.map(function (v) { return v + 1; }).join(", ") + "] with λ = " + l2n(lam, 3) + " (the smallest entry of R on the matched cells); at least one entry of R became 0.";
      if (!silent) draw();
    }
    function draw() {
      var g = l2clear(sc.svg), n = R.length, cell = n <= 3 ? 50 : n === 4 ? 44 : 38, x0 = 30, y0 = 40, i, j;
      l2text(g, x0 + n * cell / 2, 22, "residual R (row sums " + l2n(total(), 3) + ")", "tx-b", "middle");
      for (i = 0; i < n; i++) for (j = 0; j < n; j++) {
        var v = R[i][j];
        el("rect", { x: x0 + j * cell, y: y0 + i * cell, width: cell, height: cell, "class": v > 1e-9 ? "a3 ln cm hair" : "nofill ln cm hair", "fill-opacity": v > 1e-9 ? (0.12 + 0.6 * Math.min(1, v)).toFixed(2) : null }, g);
        l2text(g, x0 + (j + 0.5) * cell, y0 + (i + 0.5) * cell + 4, v > 1e-9 ? l2n(v, 2) : "0", "tx-s", "middle");
      }
      if (lastSig) for (i = 0; i < n; i++) el("rect", { x: x0 + lastSig[i] * cell + 2, y: y0 + i * cell + 2, width: cell - 4, height: cell - 4, "class": "ln c3 nofill" }, g);
      // extracted terms
      var X0 = x0 + n * cell + 40, per = 6, gw = 60, gh = 76, mc = Math.min(9, 40 / n);
      l2text(g, X0, 22, "P = Σ λ · (permutation matrix)", "tx-b", "start");
      terms.forEach(function (tm, k) {
        var gx = X0 + (k % per) * gw, gy = 36 + Math.floor(k / per) * gh;
        for (var a = 0; a < n; a++) for (var b = 0; b < n; b++) el("rect", { x: gx + b * mc, y: gy + a * mc, width: mc, height: mc, "class": "nofill ln cm hair" }, g);
        for (a = 0; a < n; a++) el("circle", { cx: gx + (tm.sig[a] + 0.5) * mc, cy: gy + (a + 0.5) * mc, r: Math.max(1.8, mc * 0.32), "class": "f3" }, g);
        l2text(g, gx + n * mc / 2, gy + n * mc + 13, "λ=" + l2n(tm.lam, 2), "tx-s", "middle");
      });
      var lsum = 0; terms.forEach(function (tm) { lsum += tm.lam; });
      l2text(g, X0, H - 12, terms.length + " permutation(s), Σλ = " + l2n(lsum, 3) + ";  Carathéodory bound (n − 1)² + 1 = " + ((n - 1) * (n - 1) + 1), "tx-s", "start");
      ro.textContent = info;
    }
    load(); redrawers.push(draw);
  };

  /* ======================================================================
     4. Using a plan: displacement interpolation and barycentric projection (§11)
     ====================================================================== */
  WIDGETS.l2plan = function (box) {
    var sc = scaffold(box, "Moving along a plan: the interpolation α_t and the barycentric projection (drag the points)");
    var W = 680, H = 420;
    sc.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    sc.svg.setAttribute("role", "img");
    sc.svg.setAttribute("aria-label", "Weighted source and target points in the plane, the optimal plan, its interpolation at time t and its barycentric projection");
    var pSel = select(sc.controls, "Example", [["split", "one point to two points"], ["w", "3 weighted points to 4"], ["perm", "8 to 8, uniform weights"], ["rand", "random, 5 to 7"]], "split", function () { load(); });
    var plSel = select(sc.controls, "Plan", [["opt", "optimal for ‖x − y‖²"], ["prod", "product a ⊗ b"]], "opt", function () { compute(); draw(); });
    var tS = slider(sc.controls, "t", 0, 1, 0.01, 0.5, function () { draw(); });
    var bary = checkbox(sc.controls, "barycentric projection", false, function () { draw(); });
    var segs = checkbox(sc.controls, "segments of the plan", true, function () { draw(); });
    var ro = readout(sc.controls);
    legend(sc.legend, [["--s2", "sources x_i (mass a_i)"], ["--s1", "targets y_j (mass b_j)"], ["--s3", "atoms of α_t; crosses: barycentric projection"]]);
    var view = { x0: 12, y0: 12, w: 656, h: 396, xr: [-2.9, 2.9] };
    view.k = view.w / (view.xr[1] - view.xr[0]);
    function VX(x) { return view.x0 + (x - view.xr[0]) * view.k; }
    function VY(y) { return view.y0 + view.h / 2 - y * view.k; }
    var S, T, ka, kb, N, P, drag = null, seed = 3, raf = 0;
    function load() {
      var v = pSel.value, rng = mulberry32(11 + 7 * seed), i;
      if (v === "split") { S = [[0, -1.0]]; ka = [2]; T = [[-1.4, 1.1], [1.4, 1.1]]; kb = [1, 1]; }
      else if (v === "w") { S = [[-1.8, -0.9], [-0.2, -1.3], [1.6, -0.7]]; ka = [3, 2, 1]; T = [[-1.5, 1.0], [-0.2, 1.4], [1.0, 1.1], [2.1, 0.5]]; kb = [1, 2, 2, 1]; }
      else if (v === "perm") {
        S = []; T = []; ka = []; kb = [];
        for (i = 0; i < 8; i++) { var a = 2 * Math.PI * i / 8; S.push([-1.5 + 0.9 * Math.cos(a), 0.9 * Math.sin(a)]); ka.push(1); }
        for (i = 0; i < 8; i++) { T.push([1.0 + 1.2 * (rng() - 0.5) * 1.6, 1.4 * (rng() - 0.5) * 1.6]); kb.push(1); }
      } else {
        S = []; T = []; var n = 5, m = 7; N = 20;
        for (i = 0; i < n; i++) S.push([-2.2 + 1.8 * rng(), -1.4 + 2.8 * rng()]);
        for (i = 0; i < m; i++) T.push([0.4 + 2.0 * rng(), -1.4 + 2.8 * rng()]);
        ka = S.map(function () { return 1; }); kb = T.map(function () { return 1; });
        for (i = n; i < N; i++) ka[Math.floor(rng() * n)]++;
        for (i = m; i < N; i++) kb[Math.floor(rng() * m)]++;
        seed++;
      }
      N = ka.reduce(function (u, v) { return u + v; }, 0);
      compute(); draw();
    }
    function cost(i, j) { var dx = S[i][0] - T[j][0], dy = S[i][1] - T[j][1]; return dx * dx + dy * dy; }
    function compute() {
      var n = S.length, m = T.length, i, j;
      if (plSel.value === "prod") { P = l2zeros(n, m); for (i = 0; i < n; i++) for (j = 0; j < m; j++) P[i][j] = ka[i] * kb[j] / (N * N); }
      else { var ex = l2exactPlan(ka, kb, cost); P = ex.U.map(function (r) { return r.map(function (u) { return u / N; }); }); }
    }
    function draw() {
      var g = l2clear(sc.svg), t = tS.get(), n = S.length, m = T.length, i, j;
      tS.out.textContent = fmt(t, 2);
      el("rect", { x: view.x0, y: view.y0, width: view.w, height: view.h, "class": "ln cm hair nofill" }, g);
      if (segs.checked) for (i = 0; i < n; i++) for (j = 0; j < m; j++) if (P[i][j] > 1e-12)
        l2line(g, VX(S[i][0]), VY(S[i][1]), VX(T[j][0]), VY(T[j][1]), "ln c3", { "stroke-width": (0.6 + 9 * P[i][j]).toFixed(2), "stroke-opacity": 0.25 });
      var atoms = [], cst = 0, nz = 0;
      for (i = 0; i < n; i++) for (j = 0; j < m; j++) if (P[i][j] > 1e-12) {
        nz++; cst += P[i][j] * cost(i, j);
        atoms.push({ x: (1 - t) * S[i][0] + t * T[j][0], y: (1 - t) * S[i][1] + t * T[j][1], w: P[i][j] });
      }
      for (i = 0; i < n; i++) el("circle", { cx: VX(S[i][0]), cy: VY(S[i][1]), r: (3 + 12 * Math.sqrt(ka[i] / N)).toFixed(1), "class": "f2 drag", "fill-opacity": 0.85 }, g);
      for (j = 0; j < m; j++) el("circle", { cx: VX(T[j][0]), cy: VY(T[j][1]), r: (3 + 12 * Math.sqrt(kb[j] / N)).toFixed(1), "class": "f1 drag", "fill-opacity": 0.85 }, g);
      atoms.forEach(function (a) { el("circle", { cx: VX(a.x), cy: VY(a.y), r: (2.5 + 11 * Math.sqrt(a.w)).toFixed(1), "class": "f3", "fill-opacity": 0.8 }, g); });
      var bmsg = "";
      if (bary.checked) {
        var mx = 0, my = 0, tx = 0, ty = 0;
        for (i = 0; i < n; i++) {
          var bx = 0, by = 0;
          for (j = 0; j < m; j++) { bx += P[i][j] * T[j][0]; by += P[i][j] * T[j][1]; }
          var ai = ka[i] / N; bx /= ai; by /= ai; mx += ai * bx; my += ai * by;
          l2line(g, VX(S[i][0]), VY(S[i][1]), VX(bx), VY(by), "ln c3 thin dot");
          l2line(g, VX(bx) - 6, VY(by) - 6, VX(bx) + 6, VY(by) + 6, "ln c3"); l2line(g, VX(bx) - 6, VY(by) + 6, VX(bx) + 6, VY(by) - 6, "ln c3");
        }
        for (j = 0; j < m; j++) { tx += kb[j] / N * T[j][0]; ty += kb[j] / N * T[j][1]; }
        var splits = 0; for (i = 0; i < n; i++) { var c = 0; for (j = 0; j < m; j++) if (P[i][j] > 1e-12) c++; if (c > 1) splits++; }
        bmsg = "\nBarycentric projection T̄(xᵢ) = (1/aᵢ) Σⱼ Pᵢⱼ yⱼ: " + splits + " source(s) split their mass" + (splits ? ", so T̄♯α ≠ β" : ", so T̄ is a genuine map and T̄♯α = β") +
          ".  Mean of T̄♯α = (" + l2n(mx, 3) + ", " + l2n(my, 3) + ") = mean of β = (" + l2n(tx, 3) + ", " + l2n(ty, 3) + ").";
      }
      // count distinct atoms and their smallest distance
      var distinct = [];
      atoms.forEach(function (a) { if (!distinct.some(function (b) { return Math.hypot(a.x - b.x, a.y - b.y) < 1e-9; })) distinct.push(a); });
      var dmin = Infinity;
      for (i = 0; i < distinct.length; i++) for (j = i + 1; j < distinct.length; j++) dmin = Math.min(dmin, Math.hypot(distinct[i].x - distinct[j].x, distinct[i].y - distinct[j].y));
      ro.textContent = "Plan: " + nz + " non-zero entries (n + m − 1 = " + (n + m - 1) + ", nm = " + n * m + "); cost ⟨C, P⟩ = " + l2n(cst, 4) +
        ".  At t = " + fmt(t, 2) + ", α_t has " + distinct.length + " atom(s)" + (distinct.length > 1 ? ", smallest distance between two of them " + l2n(dmin, 3) : "") + "." + bmsg;
    }
    function pick(e) {
      var p = svgPoint(sc.svg, e), best = null, d;
      S.forEach(function (q, i) { d = Math.hypot(VX(q[0]) - p.x, VY(q[1]) - p.y); if (d < 14 && (!best || d < best.d)) best = { arr: S, i: i, d: d }; });
      T.forEach(function (q, i) { d = Math.hypot(VX(q[0]) - p.x, VY(q[1]) - p.y); if (d < 14 && (!best || d < best.d)) best = { arr: T, i: i, d: d }; });
      return best;
    }
    sc.svg.addEventListener("pointerdown", function (e) {
      drag = pick(e); if (!drag) return;
      e.preventDefault(); try { sc.svg.setPointerCapture(e.pointerId); } catch (err) {}
    });
    sc.svg.addEventListener("pointermove", function (e) {
      if (!drag) return; e.preventDefault();
      var p = svgPoint(sc.svg, e);
      drag.arr[drag.i] = [Math.max(view.xr[0], Math.min(view.xr[1], view.xr[0] + (p.x - view.x0) / view.k)), Math.max(-1.75, Math.min(1.75, (view.y0 + view.h / 2 - p.y) / view.k))];
      if (!raf) raf = requestAnimationFrame(function () { raf = 0; compute(); draw(); });
    });
    sc.svg.addEventListener("pointerup", function () { drag = null; });
    sc.svg.addEventListener("pointercancel", function () { drag = null; });
    load(); redrawers.push(draw);
  };
