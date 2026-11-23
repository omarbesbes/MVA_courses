// widgets/01_background.js — interactive figures of page 1 (background). Own helpers are prefixed "p1".

  /* --- 1. attention: scores -> softmax weights -> weighted average of values --- */
  WIDGETS.p1attention = function (box) {
    var s = scaffold(box, "One attention head, five tokens: the output is a weighted average of the value vectors");
    var P = new Plot(s.svg, { x: [-4, 4], y: [-4, 4], w: 680, h: 360, pad: { l: 40, r: 290, t: 20, b: 30 }, label: "Value vectors in the plane, weights and their weighted average" });
    var V = [[3, 1], [-2, 2.5], [-3, -2], [1, -3], [2.5, -1]];
    var sc0 = [2, 1, 0, -1, 0.5], sl = [];
    for (var i = 0; i < 5; i++) (function (i) { sl.push(slider(s.controls, "score q·k<sub>" + (i + 1) + "</sub>", -4, 4, 0.1, sc0[i], draw)); })(i);
    var tau = slider(s.controls, "temperature τ", 0.2, 3, 0.1, 1, draw);
    button(s.controls, "Reset", function () { sl.forEach(function (x, i) { x.set(sc0[i]); }); tau.set(1); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "value v_j (size = weight)"], ["--text", "output = Σ α_j v_j"]]);
    function draw() {
      P.clear();
      P.seg(-4, 0, 4, 0, "ax"); P.seg(0, -4, 0, 4, "ax");
      var sc = sl.map(function (x) { return x.get(); }), t = tau.get();
      var w = softmaxT(sc, t), out = [0, 0];
      for (var j = 0; j < 5; j++) { out[0] += w[j] * V[j][0]; out[1] += w[j] * V[j][1]; }
      var hull = convexHull(V); P.poly(hull, "ln c1 thin dash");
      for (var j = 0; j < 5; j++) {
        P.dot(V[j][0], V[j][1], 4 + 22 * w[j], "f3");
        P.text(V[j][0], V[j][1], "v" + (j + 1), "tx-s", "middle", 0, -10 - 22 * w[j] * 0.5);
      }
      P.dot(out[0], out[1], 6, "fk");
      // bar chart of weights at the right
      var bx = 490;
      for (var j = 0; j < 5; j++) {
        var y = 40 + j * 40;
        el("rect", { x: bx, y: y, width: Math.max(1, 170 * w[j]), height: 22, "class": "f3" }, P.g);
        P.g.appendChild(el("text", { x: bx - 6, y: y + 16, "class": "tx-s", "text-anchor": "end" })).textContent = "α" + (j + 1) + " = " + fmt(w[j], 2);
      }
      P.g.appendChild(el("text", { x: bx, y: 24, "class": "tx-b" })).textContent = "softmax weights (sum 1)";
      ro.textContent = "α = softmax(scores / τ) = (" + w.map(function (x) { return fmt(x, 2); }).join(", ") + ")\noutput = (" + fmt(out[0], 2) + ", " + fmt(out[1], 2) + ") — always inside the dashed polygon conv(v₁…v₅)";
    }
    draw(); redrawers.push(draw);
  };

  /* --- 2. top-k: ReLU vs TopK vs BatchTopK on pre-activations --- */
  WIDGETS.p1topk = function (box) {
    var s = scaffold(box, "Which codes survive? Pre-activations of 3 tokens × 5 concepts");
    var svg = s.svg; svg.setAttribute("viewBox", "0 0 680 260"); svg.setAttribute("role", "img"); svg.setAttribute("aria-label", "Matrix of pre-activations and the codes kept by the chosen rule");
    var M0 = [[2.0, -0.5, 1.0, 0.3, 0.9], [0.2, 0.1, -0.3, 0.4, 0.0], [3.0, 1.5, 0.8, 2.2, 1.9]];
    var M = M0.map(function (r) { return r.slice(); });
    var mode = select(s.controls, "rule", [["relu", "ReLU (no sparsity)"], ["topk", "TopK (k per token)"], ["batch", "BatchTopK (k·tokens in total)"]], "topk", draw);
    var ks = slider(s.controls, "k", 1, 4, 1, 2, draw);
    button(s.controls, "Reset", function () { M = M0.map(function (r) { return r.slice(); }); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "kept code zᵢ"], ["--border", "set to 0"]]);
    function codes() {
      var k = ks.get(), m = mode.value, Z = M.map(function (r) { return r.map(function (v) { return Math.max(v, 0); }); });
      if (m === "relu") return Z;
      if (m === "topk") return Z.map(function (r) { var idx = r.map(function (v, i) { return i; }).sort(function (a, b) { return r[b] - r[a]; }).slice(0, k); return r.map(function (v, i) { return idx.indexOf(i) >= 0 ? v : 0; }); });
      var all = []; Z.forEach(function (r) { r.forEach(function (v) { all.push(v); }); });
      all.sort(function (a, b) { return b - a; });
      var thr = all[Math.min(k * Z.length, all.length) - 1];
      return Z.map(function (r) { return r.map(function (v) { return v >= thr && v > 0 ? v : 0; }); });
    }
    function draw() {
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      var Z = codes(), cw = 52, ch = 54, x0 = 60, x1 = 400, y0 = 40;
      function txt(x, y, t, c, a) { var n = el("text", { x: x, y: y, "class": c, "text-anchor": a || "middle" }, svg); n.textContent = t; }
      txt(x0 + 2.5 * cw, 20, "pre-activations", "tx-b"); txt(x1 + 2.5 * cw - 40, 20, "codes z kept", "tx-b");
      for (var i = 0; i < 3; i++) {
        txt(30, y0 + i * ch + 30, "token " + (i + 1), "tx-s", "middle");
        for (var j = 0; j < 5; j++) {
          el("rect", { x: x0 + j * cw, y: y0 + i * ch, width: cw - 4, height: ch - 4, "class": M[i][j] > 0 ? "a3 ln c3" : "gr", rx: 4, "stroke-width": 1 }, svg);
          txt(x0 + j * cw + cw / 2 - 2, y0 + i * ch + 30, fmt(M[i][j], 1), "tx");
          var on = Z[i][j] > 0;
          el("rect", { x: x1 - 40 + j * cw, y: y0 + i * ch, width: cw - 4, height: ch - 4, "class": on ? "a2 ln c2" : "gr", rx: 4, "stroke-width": 1 }, svg);
          txt(x1 - 40 + j * cw + cw / 2 - 2, y0 + i * ch + 30, on ? fmt(Z[i][j], 1) : "0", on ? "tx-b" : "tx-s");
        }
      }
      var cnt = Z.map(function (r) { return r.filter(function (v) { return v > 0; }).length; });
      ro.textContent = "non-zero codes per token: " + cnt.join(", ") + " (total " + cnt.reduce(function (a, b) { return a + b; }, 0) + ")";
    }
    draw(); redrawers.push(draw);
  };

  /* --- 3. superposition: c directions in the plane, sparse activations, read-out --- */
  WIDGETS.p1superposition = function (box) {
    var s = scaffold(box, "Several feature directions in the plane: write a = Σ zᵢ dᵢ, read rᵢ = dᵢ·a");
    var svg = s.svg, W = 680, H = 300; svg.setAttribute("viewBox", "0 0 " + W + " " + H); svg.setAttribute("role", "img"); svg.setAttribute("aria-label", "Feature directions in the plane and the read-out of their coefficients");
    var cs = slider(s.controls, "features c", 2, 6, 1, 3, build);
    var zs = [];
    for (var i = 0; i < 6; i++) (function (i) { zs.push(slider(s.controls, "z<sub>" + (i + 1) + "</sub>", 0, 2, 0.25, i === 0 ? 1 : 0, draw)); })(i);
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "direction dᵢ"], ["--s3", "true code zᵢ"], ["--s1", "read-out rᵢ"]]);
    function build() { draw(); }
    function draw() {
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      var c = cs.get(), cx = 170, cy = 150, R = 110, D = [], z = [];
      for (var i = 0; i < c; i++) { var th = 2 * Math.PI * i / c; D.push([Math.cos(th), Math.sin(th)]); z.push(zs[i].get()); }
      zs.forEach(function (q, i) { q.out.textContent = i < c ? fmt(q.get(), 2) : "(unused)"; });
      var a = [0, 0]; for (var i = 0; i < c; i++) { a[0] += z[i] * D[i][0]; a[1] += z[i] * D[i][1]; }
      el("circle", { cx: cx, cy: cy, r: R, "class": "gr", fill: "none" }, svg);
      for (var i = 0; i < c; i++) {
        el("line", { x1: cx, y1: cy, x2: cx + R * D[i][0], y2: cy - R * D[i][1], "class": "ln c2" }, svg);
        var t = el("text", { x: cx + (R + 14) * D[i][0], y: cy - (R + 14) * D[i][1] + 4, "class": "tx-b", "text-anchor": "middle" }, svg); t.textContent = "d" + (i + 1);
      }
      el("circle", { cx: cx + R * a[0] / 1.0 * 0.5, cy: cy - R * a[1] * 0.5, r: 6, "class": "fk" }, svg);
      var t2 = el("text", { x: cx, y: 290, "class": "tx-s", "text-anchor": "middle" }, svg); t2.textContent = "dot = a (drawn at half scale)";
      var r = []; for (var i = 0; i < c; i++) r.push(D[i][0] * a[0] + D[i][1] * a[1]);
      var bx = 400, bw = 36, mid = 150, sc = 70;
      el("line", { x1: bx - 10, y1: mid, x2: bx + c * 44 + 10, y2: mid, "class": "ax" }, svg);
      for (var i = 0; i < c; i++) {
        var x = bx + i * 44;
        function bar(v, dx, cl) { el("rect", { x: x + dx, y: v >= 0 ? mid - v * sc : mid, width: 16, height: Math.max(Math.abs(v) * sc, 0.5), "class": cl }, svg); }
        bar(z[i], 0, "f3"); bar(r[i], 18, "f1");
        var tl = el("text", { x: x + 17, y: mid + 70 + 0, "class": "tx-s", "text-anchor": "middle" }, svg); tl.textContent = "i=" + (i + 1);
      }
      var mu = 0; for (var i = 0; i < c; i++) for (var j = 0; j < i; j++) mu = Math.max(mu, Math.abs(D[i][0] * D[j][0] + D[i][1] * D[j][1]));
      ro.textContent = "coherence μ = max|dᵢ·dⱼ| = " + fmt(mu, 3) + "   read-outs r = (" + r.map(function (x) { return fmt(x, 2); }).join(", ") + ")";
    }
    draw(); redrawers.push(draw);
  };
