// widgets/02_toolbox.js — interactive figures of page 2 (toolbox). Own helpers are prefixed "p2".

  function p2fmtSci(v) { return v >= 1e4 ? v.toExponential(1).replace("e+", "×10^") : String(Math.round(v)); }
  function p2edges(P) { // edge vectors of a counter-clockwise polygon
    return P.map(function (a, i) { var b = P[(i + 1) % P.length]; return [b[0] - a[0], b[1] - a[1]]; });
  }
  function p2parallel(e, f) { var cr = e[0] * f[1] - e[1] * f[0], dt = e[0] * f[0] + e[1] * f[1]; return Math.abs(cr) < 1e-6 * (Math.hypot(e[0], e[1]) * Math.hypot(f[0], f[1]) + 1e-12) && dt > 0; }

  /* --- 1. Welch bound, random coherence, tight-frame singular value --- */
  WIDGETS.p2welch = function (box) {
    var s = scaffold(box, "Dictionary of c unit vectors in dimension d: coherence of an ideal frame and of random vectors");
    var P = new Plot(s.svg, { x: [100, 1e6], y: [0, 1], xlog: true, w: 680, h: 340, pad: { l: 46, r: 16, t: 20, b: 40 }, label: "Welch bound and random coherence against the number of vectors" });
    var sc = slider(s.controls, "log₁₀ c", 2.1, 6, 0.01, Math.log10(32000), draw);
    var sd = slider(s.controls, "d", 16, 2048, 1, 768, draw);
    button(s.controls, "Paper (c = 32 000, d = 768)", function () { sc.set(Math.log10(32000)); sd.set(768); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "Welch bound"], ["--s2", "random vectors (typical coherence)"], ["--muted", "1/√d"]]);
    function draw() {
      var d = sd.get(), c = Math.round(Math.pow(10, sc.get()));
      var welch = function (cc) { return cc <= d ? 0 : Math.sqrt((cc - d) / (d * (cc - 1))); };
      var rnd = function (cc) { return Math.min(1, Math.sqrt(2 * Math.log(cc * (cc - 1)) / d)); };
      P.clear();
      P.axes({ xticks: [100, 1000, 1e4, 1e5, 1e6], yticks: [0, 0.2, 0.4, 0.6, 0.8, 1], xfmt: function (v) { return p2fmtSci(v); }, yd: 1, xlabel: "number of vectors c", ylabel: "coherence μ" });
      P.fn(welch, "ln c1", 300, 100, 1e6); P.fn(rnd, "ln c2", 300, 100, 1e6);
      P.seg(100, 1 / Math.sqrt(d), 1e6, 1 / Math.sqrt(d), "ln cm dash thin");
      P.seg(c, 0, c, 1, "ln cm thin");
      P.dot(c, welch(c), 5, "f1"); P.dot(c, rnd(c), 5, "f2");
      sc.out.textContent = p2fmtSci(c); sd.out.textContent = d;
      var tight = Math.sqrt(c / d);
      ro.textContent = "c = " + c + ", d = " + d + "\nWelch bound = " + fmt(welch(c), 4) + (c <= d ? " (c ≤ d: an orthonormal system exists, μ = 0)" : "") +
        "\nstd of one random inner product 1/√d = " + fmt(1 / Math.sqrt(d), 4) + ";  typical coherence of c random vectors ≈ " + fmt(rnd(c), 3) +
        "\ntight frame: all singular values √(c/d) = " + fmt(tight, 3) + (c > d ? ";  random rows: band [" + fmt(tight - 1, 2) + ", " + fmt(tight + 1, 2) + "]" : "");
    }
    draw(); redrawers.push(draw);
  };

  /* --- 2. barycentric coordinates: triangle (unique) and square (not unique) --- */
  WIDGETS.p2bary = function (box) {
    var s = scaffold(box, "Barycentric weights of a point: unique in a triangle, a family in a square");
    var P = new Plot(s.svg, { x: [-0.2, 1.2], y: [-0.2, 1.2], w: 440, h: 440, label: "A point inside a triangle or a square and its weights on the vertices" });
    var shapes = { tri: [[0, 0], [1, 0], [0.35, 0.95]], sq: [[0, 0], [1, 0], [1, 1], [0, 1]] };
    var pt = [[0.4, 0.4]], mode = "tri";
    var sel = select(s.controls, "Shape", [["tri", "triangle (3 vertices)"], ["sq", "square (4 vertices)"]], "tri", function () { mode = sel.value; pt[0] = mode === "tri" ? [0.45, 0.35] : [0.4, 0.55]; draw(); });
    var sl = slider(s.controls, "position on the family λ + tμ", 0, 1, 0.01, 0.5, draw);
    var ro = readout(s.controls);
    var cols = ["f1", "f2", "f3", "f5"];
    legend(s.legend, [["--s1", "v₁"], ["--s2", "v₂"], ["--s3", "v₃"], ["--s5", "v₄"]]);
    function weights() {
      var V = shapes[mode], x = pt[0][0], y = pt[0][1];
      if (mode === "tri") {
        var a = V[0], b = V[1], c = V[2];
        var det = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]);
        var l2 = ((x - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (y - a[1])) / det;
        var l3 = ((b[0] - a[0]) * (y - a[1]) - (x - a[0]) * (b[1] - a[1])) / det;
        return { lam: [1 - l2 - l3, l2, l3], range: null };
      }
      var l0 = [(1 - x) * (1 - y), x * (1 - y), x * y, (1 - x) * y], mu = [1, -1, 1, -1], lo = -Infinity, hi = Infinity;
      for (var i = 0; i < 4; i++) { if (mu[i] > 0) lo = Math.max(lo, -l0[i] / mu[i]); else hi = Math.min(hi, l0[i] / -mu[i]); }
      var t = lo + sl.get() * (hi - lo);
      return { lam: l0.map(function (v, i) { return Math.max(0, v + t * mu[i]); }), range: [lo, hi], t: t };
    }
    function clampPt(i, x, y) {
      if (mode === "sq") return [Math.min(Math.max(x, 0), 1), Math.min(Math.max(y, 0), 1)];
      var V = shapes.tri; pt[0] = [x, y]; var w = weights().lam;
      if (w[0] >= 0 && w[1] >= 0 && w[2] >= 0) return [x, y];
      var l = w.map(function (v) { return Math.max(v, 0); }), sm = l[0] + l[1] + l[2];
      l = l.map(function (v) { return v / sm; });
      return [l[0] * V[0][0] + l[1] * V[1][0] + l[2] * V[2][0], l[0] * V[0][1] + l[1] * V[1][1] + l[2] * V[2][1]];
    }
    draggable(P, pt, function () { draw(); }, { clamp: clampPt, radius: 40 });
    function draw() {
      var V = shapes[mode], w = weights(), lam = w.lam;
      P.clear();
      P.axes({ xticks: [0, 0.5, 1], yticks: [0, 0.5, 1], xd: 1, yd: 1 });
      P.poly(V.concat([V[0]]), "am ln c1");
      V.forEach(function (v, k) {
        P.seg(v[0], v[1], pt[0][0], pt[0][1], "ln " + ["c1", "c2", "c3", "c5"][k], { style: "stroke-width:" + (0.6 + 9 * lam[k]) + ";opacity:0.75" });
        P.dot(v[0], v[1], 6, cols[k]);
        P.text(v[0], v[1], "v" + "₁₂₃₄"[k] + " " + fmt(lam[k], 2), "tx", "middle", 0, v[1] < 0.5 ? 22 : -12);
      });
      P.dot(pt[0][0], pt[0][1], 8, "fk drag");
      sl.input.disabled = mode === "tri"; sl.out.textContent = mode === "tri" ? "n/a" : fmt(sl.get(), 2);
      var line = "point p = (" + fmt(pt[0][0], 2) + ", " + fmt(pt[0][1], 2) + ")   weights λ = (" + lam.map(function (v) { return fmt(v, 2); }).join(", ") + ")   sum = " + fmt(lam.reduce(function (a, b) { return a + b; }, 0), 2);
      ro.textContent = line + (mode === "tri" ? "\nUnique: three affinely independent vertices." : "\nFamily λ + tμ with μ = (1, −1, 1, −1), t ∈ [" + fmt(w.range[0], 2) + ", " + fmt(w.range[1], 2) + "]: every member gives the same p.");
    }
    draw(); redrawers.push(draw);
  };

  /* --- 3. Minkowski sum of two polygons --- */
  WIDGETS.p2minkowski = function (box) {
    var s = scaffold(box, "Two polygons P and Q (drag the vertices) and their Minkowski sum P ⊕ Q");
    var P = new Plot(s.svg, { x: [-6, 6], y: [-5, 5], w: 680, h: 420, label: "Two convex polygons and their Minkowski sum" });
    var init = [[-2.5, -1], [-0.5, -1.8], [0.8, 0.4], [-1.8, 1.4], [-0.6, -0.1], [0.4, -0.6], [1.6, 0.9], [-0.5, 1.3]];
    var pts = init.map(function (p) { return p.slice(); });
    var showSum = true;
    button(s.controls, "Reset", function () { init.forEach(function (p, i) { pts[i] = p.slice(); }); draw(); });
    button(s.controls, "Make Q a copy of P rotated", function () { var th = 0.9; for (var i = 0; i < 4; i++) pts[4 + i] = [pts[i][0] * Math.cos(th) - pts[i][1] * Math.sin(th), pts[i][0] * Math.sin(th) + pts[i][1] * Math.cos(th)]; draw(); });
    checkbox(s.controls, "show the sum", true, function (e) { showSum = e.target.checked; draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "P (edges in blue)"], ["--s5", "Q (edges in purple)"], ["--text", "P ⊕ Q (edge from P, from Q, or both when parallel)"]]);
    draggable(P, pts, function () { draw(); }, { radius: 26 });
    function draw() {
      var HP = convexHull(pts.slice(0, 4)), HQ = convexHull(pts.slice(4)), S = minkowskiSum(HP, HQ);
      P.clear();
      P.axes({ xticks: [-4, -2, 0, 2, 4], yticks: [-4, -2, 0, 2, 4], cross: true });
      if (showSum) {
        P.poly(S.concat([S[0]]), "am", { stroke: "none" });
        var eP = p2edges(HP), eQ = p2edges(HQ), lines = [];
        S.forEach(function (a, i) {
          var b = S[(i + 1) % S.length], e = [b[0] - a[0], b[1] - a[1]];
          var inP = eP.some(function (f) { return p2parallel(e, f); }), inQ = eQ.some(function (f) { return p2parallel(e, f); });
          var cls = inP && inQ ? "ck" : inP ? "c1" : "c5";
          P.seg(a[0], a[1], b[0], b[1], "ln " + cls, { style: "stroke-width:3" });
          lines.push((Math.atan2(e[1], e[0]) * 180 / Math.PI).toFixed(0) + "° " + (inP && inQ ? "P+Q" : inP ? "P" : "Q"));
        });
        S.forEach(function (v) { P.dot(v[0], v[1], 3, "fk"); });
        ro.textContent = "vertices: P " + HP.length + ", Q " + HQ.length + ", P ⊕ Q " + S.length + " (≤ " + (HP.length + HQ.length) + ");   area P " + fmt(polyArea(HP), 2) + ", Q " + fmt(polyArea(HQ), 2) + ", sum " + fmt(polyArea(S), 2) +
          "\nedges of the sum by angle: " + lines.join(", ");
      } else {
        ro.textContent = "vertices: P " + HP.length + ", Q " + HQ.length;
      }
      P.poly(HP.concat([HP[0]]), "ln c1 thin", { fill: "none", style: "stroke-width:2" });
      P.poly(HQ.concat([HQ[0]]), "ln c5 thin", { fill: "none", style: "stroke-width:2" });
      pts.forEach(function (p, i) { P.dot(p[0], p[1], 6, i < 4 ? "f1 drag" : "f5 drag"); });
    }
    draw(); redrawers.push(draw);
  };

  /* --- 4. support function of a polygon, and additivity --- */
  WIDGETS.p2support = function (box) {
    var s = scaffold(box, "Support function h(u) = max over the polygon of ⟨x, u⟩, and h_{P⊕Q} = h_P + h_Q");
    var P = new Plot(s.svg, { x: [-6, 6], y: [-5, 5], w: 680, h: 420, label: "A polygon, a direction and its supporting line" });
    var init = [[-2.5, -1], [-0.5, -1.8], [0.8, 0.4], [-1.8, 1.4]];
    var pts = init.map(function (p) { return p.slice(); }), Qv = [[-0.6, -0.1], [1.6, 0.0], [0.4, 1.3]];
    var th = slider(s.controls, "direction θ (°)", 0, 360, 1, 40, draw);
    var showQ = false;
    checkbox(s.controls, "add the triangle Q and its sum", false, function (e) { showQ = e.target.checked; draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "P (draggable)"], ["--s5", "Q"], ["--s2", "direction u and supporting line"]]);
    draggable(P, pts, function () { draw(); }, { radius: 26 });
    function argmax(Pg, u) { var b = null, m = -Infinity; Pg.forEach(function (p) { var v = p[0] * u[0] + p[1] * u[1]; if (v > m) { m = v; b = p; } }); return b; }
    function draw() {
      var t = th.get() * Math.PI / 180, u = [Math.cos(t), Math.sin(t)];
      var HP = convexHull(pts), HQ = convexHull(Qv), S = minkowskiSum(HP, HQ);
      var target = showQ ? S : HP;
      P.clear();
      P.axes({ xticks: [-4, -2, 0, 2, 4], yticks: [-4, -2, 0, 2, 4], cross: true });
      if (showQ) { P.poly(S.concat([S[0]]), "am ln cm thin"); P.poly(HQ.concat([HQ[0]]), "ln c5", { fill: "none", style: "stroke-width:2" }); }
      P.poly(HP.concat([HP[0]]), "ln c1", { fill: showQ ? "none" : "", style: "stroke-width:2" });
      var h = supportFn(target, u), q = argmax(target, u), nrm = [-u[1], u[0]], L = 12;
      P.seg(u[0] * h - nrm[0] * L, u[1] * h - nrm[1] * L, u[0] * h + nrm[0] * L, u[1] * h + nrm[1] * L, "ln c2", { style: "stroke-width:2" });
      P.seg(0, 0, u[0] * h, u[1] * h, "ln ck thin dash");
      P.seg(0, 0, u[0] * 1.5, u[1] * 1.5, "ln c2", { style: "stroke-width:3" });
      P.text(u[0] * 1.6, u[1] * 1.6, "u", "tx-b", "middle", 0, -6);
      P.dot(q[0], q[1], 6, "fk");
      pts.forEach(function (p) { P.dot(p[0], p[1], 6, "f1 drag"); });
      if (showQ) HQ.forEach(function (p) { P.dot(p[0], p[1], 4, "f5"); });
      var hp = supportFn(HP, u), hq = supportFn(HQ, u);
      ro.textContent = "u = (" + fmt(u[0], 2) + ", " + fmt(u[1], 2) + ")   h_P(u) = " + fmt(hp, 3) + (showQ ? "   h_Q(u) = " + fmt(hq, 3) + "   h_P + h_Q = " + fmt(hp + hq, 3) + "   h_{P⊕Q}(u) = " + fmt(supportFn(S, u), 3) : "") +
        "\nthe line ⟨x, u⟩ = h(u) touches " + (showQ ? "P ⊕ Q" : "P") + " at (" + fmt(q[0], 2) + ", " + fmt(q[1], 2) + ")";
      th.out.textContent = th.get() + "°";
    }
    draw(); redrawers.push(draw);
  };

  /* --- 5. softmax and temperature on the simplex --- */
  WIDGETS.p2softmax = function (box) {
    var s = scaffold(box, "Softmax of three logits at temperature τ: a point of the open triangle");
    var W = 520, H = 400, svg = s.svg; svg.setAttribute("viewBox", "0 0 " + W + " " + H); svg.setAttribute("role", "img"); svg.setAttribute("aria-label", "A point of the probability simplex given by softmax of three logits");
    var V = [[70, 340], [450, 340], [260, 36]];
    var xs = [], names = ["x₁", "x₂", "x₃"], init = [2, 1, 0];
    for (var i = 0; i < 3; i++) xs.push(slider(s.controls, names[i], -5, 5, 0.1, init[i], draw));
    var st = slider(s.controls, "log₁₀ τ", -1.3, 1.3, 0.01, 0, draw);
    button(s.controls, "Add 3 to all logits", function () { xs.forEach(function (x) { x.set(Math.min(5, x.get() + 3)); }); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "vertices e₁, e₂, e₃"], ["--s3", "softmax(x/τ)"], ["--muted", "path when τ goes from 0.05 to 20"]]);
    function pos(p) { return [p[0] * V[0][0] + p[1] * V[1][0] + p[2] * V[2][0], p[0] * V[0][1] + p[1] * V[1][1] + p[2] * V[2][1]]; }
    function draw() {
      var x = xs.map(function (v) { return v.get(); }), tau = Math.pow(10, st.get()), p = softmaxT(x, tau);
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      var g = el("g", {}, svg);
      el("path", { d: "M" + V[0].join(" ") + "L" + V[1].join(" ") + "L" + V[2].join(" ") + "Z", "class": "am ln cm thin" }, g);
      var d = "";
      for (var k = 0; k <= 80; k++) { var tt = Math.pow(10, -1.3 + 2.6 * k / 80), q = pos(softmaxT(x, tt)); d += (k ? "L" : "M") + q[0].toFixed(1) + " " + q[1].toFixed(1); }
      el("path", { d: d, "class": "ln cm", fill: "none", style: "stroke-width:1.5;stroke-dasharray:4 3" }, g);
      V.forEach(function (v, j) {
        el("circle", { cx: v[0], cy: v[1], r: 6, "class": "f1" }, g);
        var t = el("text", { x: v[0], y: v[1] + (j === 2 ? -12 : 22), "class": "tx", "text-anchor": "middle" }, g); t.textContent = "e" + "₁₂₃"[j] + "   p" + "₁₂₃"[j] + " = " + fmt(p[j], 3);
      });
      var c = pos(p); el("circle", { cx: c[0], cy: c[1], r: 8, "class": "f3" }, g);
      xs.forEach(function (v) { v.out.textContent = fmt(v.get(), 1); }); st.out.textContent = "τ = " + fmt(tau, 2);
      ro.textContent = "x = (" + x.map(function (v) { return fmt(v, 1); }).join(", ") + "), τ = " + fmt(tau, 2) + "  →  p = (" + p.map(function (v) { return fmt(v, 3); }).join(", ") + ")   (all > 0, sum " + fmt(p[0] + p[1] + p[2], 3) + ")";
    }
    draw(); redrawers.push(draw);
  };
