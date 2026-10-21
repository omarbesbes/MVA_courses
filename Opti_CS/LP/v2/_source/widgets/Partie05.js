// widgets/Partie05.js — interactive figures of Partie 5 (la dualité).
// Inserted by build.mjs inside the scope of app.js: uses el, fmt, frac, scaffold, slider, select, button, checkbox,
// readout, legend, svgPoint, Fr, frSolve, halfPlanePolygon, lineInBox, combinations, simplex, redrawers, WIDGETS.
// All the private helpers of this file are prefixed p5.

  /* ---------------- helpers ---------------- */
  // A rectangular panel inside an SVG: data coordinates xr × yr mapped into the pixel box bx = [x0, y0, w, h].
  function p5panel(svg, bx, xr, yr) {
    var P = { bx: bx, box: [xr[0], xr[1], yr[0], yr[1]] };
    P.X = function (x) { return bx[0] + (x - xr[0]) / (xr[1] - xr[0]) * bx[2]; };
    P.Y = function (y) { return bx[1] + bx[3] - (y - yr[0]) / (yr[1] - yr[0]) * bx[3]; };
    P.ix = function (px) { return xr[0] + (px - bx[0]) / bx[2] * (xr[1] - xr[0]); };
    P.iy = function (py) { return yr[0] + (bx[1] + bx[3] - py) / bx[3] * (yr[1] - yr[0]); };
    P.inside = function (pt) { return pt.x >= bx[0] - 8 && pt.x <= bx[0] + bx[2] + 8 && pt.y >= bx[1] - 8 && pt.y <= bx[1] + bx[3] + 8; };
    P.g = el("g", {}, svg);
    var id = "p5clip" + Math.random().toString(36).slice(2);
    var cp = el("clipPath", { id: id }, svg);
    el("rect", { x: bx[0], y: bx[1], width: bx[2], height: bx[3] }, cp);
    P.gc = el("g", { "clip-path": "url(#" + id + ")" }, svg);
    P.top = el("g", {}, svg);
    P.poly = function (pts, cls, g, close) {
      if (!pts.length) return null;
      var d = pts.map(function (p, i) { return (i ? "L" : "M") + P.X(p[0]).toFixed(1) + " " + P.Y(p[1]).toFixed(1); }).join("") + (close === false ? "" : "Z");
      return el("path", { d: d, "class": cls }, g || P.gc);
    };
    P.line = function (x1, y1, x2, y2, cls, g, extra) {
      var a = { x1: P.X(x1), y1: P.Y(y1), x2: P.X(x2), y2: P.Y(y2), "class": cls };
      for (var k in extra || {}) a[k] = extra[k];
      return el("line", a, g || P.gc);
    };
    P.cline = function (a, b, r, cls, extra) {
      var s = lineInBox(a, b, r, P.box);
      if (s) P.line(s[0][0], s[0][1], s[1][0], s[1][1], cls, P.gc, extra);
      return s;
    };
    P.dot = function (x, y, r, cls, g) { return el("circle", { cx: P.X(x), cy: P.Y(y), r: r, "class": cls }, g || P.top); };
    P.text = function (x, y, s, cls, anchor, dx, dy, g) {
      var t = el("text", { x: P.X(x) + (dx || 0), y: P.Y(y) + (dy || 0), "class": cls || "tx-s", "text-anchor": anchor || "start" }, g || P.top);
      t.textContent = s; return t;
    };
    P.axes = function (xt, yt, xlabel, ylabel) {
      var g = P.g;
      xt.forEach(function (v) {
        el("line", { x1: P.X(v), x2: P.X(v), y1: bx[1], y2: bx[1] + bx[3], "class": "gr" }, g);
        var t = el("text", { x: P.X(v), y: bx[1] + bx[3] + 14, "class": "tx-s", "text-anchor": "middle" }, g); t.textContent = frac(v);
      });
      yt.forEach(function (v) {
        el("line", { x1: bx[0], x2: bx[0] + bx[2], y1: P.Y(v), y2: P.Y(v), "class": "gr" }, g);
        var t = el("text", { x: bx[0] - 5, y: P.Y(v) + 4, "class": "tx-s", "text-anchor": "end" }, g); t.textContent = frac(v);
      });
      var x0 = Math.min(Math.max(0, xr[0]), xr[1]), y0 = Math.min(Math.max(0, yr[0]), yr[1]);
      el("line", { x1: bx[0], x2: bx[0] + bx[2], y1: P.Y(y0), y2: P.Y(y0), "class": "ax" }, g);
      el("line", { x1: P.X(x0), x2: P.X(x0), y1: bx[1], y2: bx[1] + bx[3], "class": "ax" }, g);
      if (xlabel) { var a = el("text", { x: bx[0] + bx[2], y: bx[1] + bx[3] + 28, "class": "tx-s", "text-anchor": "end" }, g); a.textContent = xlabel; }
      if (ylabel) { var b = el("text", { x: P.X(x0) + 5, y: bx[1] - 6, "class": "tx-s" }, g); b.textContent = ylabel; }
    };
    return P;
  }
  function p5clear(svg) { while (svg.firstChild) svg.removeChild(svg.firstChild); }
  function p5vec(v) { return "(" + v.map(function (z) { return z instanceof Fr ? z.str() : frac(z); }).join(", ") + ")"; }
  function p5snap(v, step) { return Math.round(v / step) * step; }
  // A light outline behind a label, so that it stays legible where it crosses a line.
  function p5halo(t) { t.setAttribute("style", "paint-order:stroke;stroke:var(--surface);stroke-width:3px;stroke-linejoin:round"); return t; }
  // Two panels side by side are too small on a phone: below this width (in CSS pixels) they are stacked.
  function p5narrow(box) { var w = box.clientWidth || 680; return w < 560; }
  function p5onWidth(box, draw) {
    var last = p5narrow(box);
    window.addEventListener("resize", function () { var n = p5narrow(box); if (n !== last) { last = n; draw(); } });
  }
  function p5dotF(u, v) { var s = Fr(0); for (var i = 0; i < u.length; i++) s = s.add(Fr.of(u[i]).mul(Fr.of(v[i]))); return s; }

  /* ======================================================================
     1. Primal and dual side by side (§3, weak duality) — example (R)
     ====================================================================== */
  WIDGETS.p5paire = function (box) {
    var s = scaffold(box, "Le primal (R) et son dual : déplacez x et p, regardez b·p ≤ c·x");
    var svg = s.svg;
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Deux plans : à gauche la région admissible du primal et le point x, à droite celle du dual et le point p ; en bas une règle avec b·p et c·x");
    var A = [[2, 1], [1, 3]], b = [8, 9];
    var c1S = slider(s.controls, "prix de l’aliment 1, c₁ =", 1, 6, 0.5, 3, function () { draw(); });
    button(s.controls, "x optimal", function () { var o = optX(); x = o.slice(); draw(); });
    button(s.controls, "p optimal", function () { var o = optP(); p = o.slice(); draw(); });
    button(s.controls, "les deux", function () { x = optX().slice(); p = optP().slice(); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "région primale, x"], ["--s5", "région duale, p"], ["--s2", "lignes de niveau"], ["--s3", "optimum"]]);
    var x = [6, 4], p = [0.5, 0.2], drag = null, PX, PP;
    function cvec() { return [c1S.get(), 2]; }
    function optX() {
      var c = cvec(), V = [[0, 8], [3, 2], [9, 0]], best = V[0];
      V.forEach(function (v) { if (c[0] * v[0] + c[1] * v[1] < c[0] * best[0] + c[1] * best[1] - 1e-12) best = v; });
      return best;
    }
    function dualPoly() { var c = cvec(); return halfPlanePolygon([[2, 1, c[0]], [1, 3, c[1]], [-1, 0, 0], [0, -1, 0]], [-0.3, 3.3, -0.3, 1.3]); }
    function optP() {
      var best = null;
      dualPoly().forEach(function (v) { if (!best || 8 * v[0] + 9 * v[1] > 8 * best[0] + 9 * best[1] + 1e-12) best = v; });
      return [best[0], best[1]];
    }
    function where(e) {
      var pt = svgPoint(svg, e);
      if (PX && PX.inside(pt)) return { w: "x", v: [Math.max(0, Math.min(10, p5snap(PX.ix(pt.x), 0.25))), Math.max(0, Math.min(10, p5snap(PX.iy(pt.y), 0.25)))] };
      if (PP && PP.inside(pt)) return { w: "p", v: [Math.max(-0.3, Math.min(3.3, p5snap(PP.ix(pt.x), 0.05))), Math.max(-0.3, Math.min(1.3, p5snap(PP.iy(pt.y), 0.05)))] };
      return null;
    }
    svg.addEventListener("pointerdown", function (e) {
      var h = where(e); if (!h) return;
      drag = h.w; if (drag === "x") x = h.v; else p = h.v;
      try { svg.setPointerCapture(e.pointerId); } catch (err) {}
      e.preventDefault(); draw();
    });
    svg.addEventListener("pointermove", function (e) {
      if (!drag) return;
      var h = where(e); if (!h || h.w !== drag) return;
      if (drag === "x") x = h.v; else p = h.v;
      draw();
    });
    svg.addEventListener("pointerup", function () { drag = null; });
    svg.addEventListener("pointercancel", function () { drag = null; });

    function draw() {
      var c = cvec(); c1S.out.textContent = frac(c[0]);
      p5clear(svg);
      // wide: the two planes side by side; narrow (phone): stacked, with the ruler below
      var L = p5narrow(box) ?
        { W: 360, H: 660, px: [44, 34, 290, 220], pp: [44, 318, 290, 200], t1: [189, 16], t2: [189, 300], lab: [[16, 572, "la règle : b·p (violet) et c·x (bleu) ;"], [16, 586, "l’intervalle entre les deux est l’écart c·x − b·p"]], ru: [24, 612, 312, 30] } :
        { W: 680, H: 396, px: [44, 40, 270, 238], pp: [392, 40, 270, 238], t1: [179, 14], t2: [527, 14], lab: [[44, 322, "la règle : b·p (violet) et c·x (bleu) ; l’intervalle entre les deux est l’écart c·x − b·p"]], ru: [44, 346, 618, 30] };
      svg.setAttribute("viewBox", "0 0 " + L.W + " " + L.H);
      PX = p5panel(svg, L.px, [0, 10], [0, 10]);
      PP = p5panel(svg, L.pp, [-0.3, 3.3], [-0.3, 1.3]);
      PX.axes([0, 2, 4, 6, 8, 10], [0, 2, 4, 6, 8, 10], "x₁", "x₂");
      PP.axes([0, 1, 2, 3], [0, 0.5, 1], "p₁", "p₂");
      var t1 = el("text", { x: L.t1[0], y: L.t1[1], "class": "tx-b", "text-anchor": "middle" }, svg); t1.textContent = "primal : min c·x, Ax ≥ b, x ≥ 0";
      var t2 = el("text", { x: L.t2[0], y: L.t2[1], "class": "tx-b", "text-anchor": "middle" }, svg); t2.textContent = "dual : max b·p, Aᵀp ≤ c, p ≥ 0";
      // primal region
      var reg = halfPlanePolygon([[-2, -1, -8], [-1, -3, -9], [-1, 0, 0], [0, -1, 0]], PX.box);
      PX.poly(reg, "a1"); PX.poly(reg, "ln c1 thin");
      var e = [A[0][0] * x[0] + A[0][1] * x[1] - b[0], A[1][0] * x[0] + A[1][1] * x[1] - b[1]];
      var sl = [c[0] - (A[0][0] * p[0] + A[1][0] * p[1]), c[1] - (A[0][1] * p[0] + A[1][1] * p[1])];
      PX.cline(2, 1, 8, "ln cm " + (Math.abs(e[0]) < 1e-9 ? "" : "thin"));
      PX.cline(1, 3, 9, "ln cm " + (Math.abs(e[1]) < 1e-9 ? "" : "thin"));
      p5halo(PX.text(4.2, 0, "2x₁ + x₂ = 8", "tx-s", "start", 0, -6, PX.gc));
      p5halo(PX.text(5.0, 4 / 3, "x₁ + 3x₂ = 9", "tx-s", "start", 0, -6, PX.gc));
      var ox = optX(), copt = c[0] * ox[0] + c[1] * ox[1], cx = c[0] * x[0] + c[1] * x[1];
      PX.cline(c[0], c[1], copt, "ln c2 thin");
      PX.cline(c[0], c[1], cx, "ln c2 thin dash");
      PX.dot(ox[0], ox[1], 5, "f3");
      var xadm = x[0] >= -1e-9 && x[1] >= -1e-9 && e[0] >= -1e-9 && e[1] >= -1e-9;
      PX.dot(x[0], x[1], 7, xadm ? "f1 drag" : "f6 drag");
      PX.text(x[0], x[1], "x", "tx-b", "start", 9, -8);
      // dual region
      var dreg = dualPoly();
      PP.poly(dreg, "a5"); PP.poly(dreg, "ln c5 thin");
      PP.cline(2, 1, c[0], "ln cm " + (Math.abs(sl[0]) < 1e-9 ? "" : "thin"));
      PP.cline(1, 3, 2, "ln cm " + (Math.abs(sl[1]) < 1e-9 ? "" : "thin"));
      var op = optP(), bopt = 8 * op[0] + 9 * op[1], bp = 8 * p[0] + 9 * p[1];
      PP.cline(8, 9, bopt, "ln c2 thin");
      PP.cline(8, 9, bp, "ln c2 thin dash");
      // label at the foot of the line 2p₁ + p₂ = c₁: on its right while there is room, else on its left
      var foot = c[0] / 2, right = foot + 1.15 <= 3.3;
      p5halo(PP.text(right ? foot + 0.05 : foot - 0.05, 0, "2p₁ + p₂ = c₁", "tx-s", right ? "start" : "end", 0, -6, PP.gc));
      p5halo(PP.text(-0.27, 0.76, "p₁ + 3p₂ = 2", "tx-s", "start", 0, -6, PP.gc));
      PP.dot(op[0], op[1], 5, "f3");
      var padm = p[0] >= -1e-9 && p[1] >= -1e-9 && sl[0] >= -1e-9 && sl[1] >= -1e-9;
      PP.dot(p[0], p[1], 7, padm ? "f5 drag" : "f6 drag");
      PP.text(p[0], p[1], "p", "tx-b", "start", 9, -8);
      // ruler
      var R = p5panel(svg, L.ru, [0, 30], [0, 1]);
      el("line", { x1: R.X(0), x2: R.X(30), y1: R.Y(0.5), y2: R.Y(0.5), "class": "ax" }, svg);
      for (var t = 0; t <= 30; t += 5) {
        el("line", { x1: R.X(t), x2: R.X(t), y1: R.Y(0.5) - 4, y2: R.Y(0.5) + 4, "class": "ax" }, svg);
        var tt = el("text", { x: R.X(t), y: R.Y(0.5) + 18, "class": "tx-s", "text-anchor": "middle" }, svg); tt.textContent = t;
      }
      var lo = Math.max(0, Math.min(30, Math.min(bp, cx))), hi = Math.max(0, Math.min(30, Math.max(bp, cx)));
      var ok = bp <= cx + 1e-9;
      el("rect", { x: R.X(lo), y: R.Y(0.5) - 6, width: Math.max(0, R.X(hi) - R.X(lo)), height: 12, "class": ok ? "a4" : "a2" }, svg);
      [[bp, "b·p", "f5", -12], [cx, "c·x", "f1", -12]].forEach(function (m, k) {
        var X = R.X(Math.max(0, Math.min(30, m[0])));
        el("circle", { cx: X, cy: R.Y(0.5), r: 6, "class": m[2] }, svg);
        var tx = el("text", { x: X, y: R.Y(0.5) - 12 - (k === 1 && Math.abs(R.X(bp) - R.X(cx)) < 46 ? 14 : 0), "class": "tx-b", "text-anchor": "middle" }, svg);
        tx.textContent = m[1] + " = " + frac(m[0]);
      });
      L.lab.forEach(function (q) { var lab = el("text", { x: q[0], y: q[1], "class": "tx-s" }, svg); lab.textContent = q[2]; });
      // readout
      var gap = cx - bp;
      var txt = "x = " + p5vec(x) + (xadm ? " admissible" : " NON admissible") + " ; c·x = " + frac(cx) +
        "\np = " + p5vec(p) + (padm ? " admissible" : " NON admissible") + " ; b·p = " + frac(bp) +
        "\nécart c·x − b·p = x₁s₁ + x₂s₂ + p₁e₁ + p₂e₂ = " + [x[0] * sl[0], x[1] * sl[1], p[0] * e[0], p[1] * e[1]].map(function (v) { return v < -1e-12 ? "(" + frac(v) + ")" : frac(v); }).join(" + ") + " = " + frac(gap) +
        "\n   où s = c − Aᵀp = " + p5vec(sl) + " (jeu des contraintes duales) et e = Ax − b = " + p5vec(e) + " (surplus primal)";
      if (xadm && padm) txt += "\nLes deux sont admissibles : les quatre produits sont ≥ 0, donc b·p ≤ c·x (dualité faible)." + (Math.abs(gap) < 1e-9 ? "  Écart nul : x et p sont optimaux." : "");
      else txt += "\nHors des régions admissibles, un produit peut être négatif : l’inégalité b·p ≤ c·x n’est plus garantie.";
      ro.textContent = txt;
    }
    draw(); redrawers.push(draw); p5onWidth(box, draw);
  };

  /* ======================================================================
     2. Complementary slackness as a method (§5) — production example
     ====================================================================== */
  WIDGETS.p5ecarts = function (box) {
    var s = scaffold(box, "La méthode des écarts complémentaires : choisissez un sommet, le widget en déduit les prix y et les teste");
    var svg = s.svg, W = 680, H = 330;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Le polygone de production, ses sommets cliquables, et pour le sommet choisi les écarts primaux et les prix duaux");
    var M = [[2, 1], [1, 1], [1, 3]], r = [10, 6, 15], names = ["bois", "machine", "main-d’œuvre"];
    var V = [[0, 0], [5, 0], [4, 2], [1.5, 4.5], [0, 5]];
    var Vn = ["(0, 0)", "(5, 0)", "(4, 2)", "(3/2, 9/2)", "(0, 5)"];
    var cur = 1, P;
    var vSel = select(s.controls, "Sommet candidat", V.map(function (v, i) { return [String(i), "x = " + Vn[i]]; }), "1", function () { cur = parseInt(vSel.value, 10); draw(); });
    var gS = slider(s.controls, "profit unitaire du produit 2, g₂ =", 5, 130, 5, 30, function () { draw(); });
    button(s.controls, "Sommet optimal", function () { cur = optIdx(); vSel.value = String(cur); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "région admissible"], ["--s2", "ligne de niveau du profit"], ["--s3", "sommet optimal"], ["--s5", "prix duaux y"], ["--s6", "valeur interdite (y < 0 ou contrainte violée)"]]);
    function g() { return [40, gS.get()]; }
    function optIdx() { var gg = g(), best = 0; V.forEach(function (v, i) { if (gg[0] * v[0] + gg[1] * v[1] > gg[0] * V[best][0] + gg[1] * V[best][1] + 1e-9) best = i; }); return best; }
    svg.addEventListener("pointerdown", function (e) {
      if (!P) return;
      var pt = svgPoint(svg, e), best = -1, bd = 22;
      V.forEach(function (v, i) { var d = Math.hypot(pt.x - P.X(v[0]), pt.y - P.Y(v[1])); if (d < bd) { bd = d; best = i; } });
      if (best >= 0) { cur = best; vSel.value = String(cur); draw(); }
    });
    // The method: from x, deduce y (exactly), then test it.
    function method(xv) {
      var gg = g().map(Fr.of), xF = xv.map(Fr.of);
      var slack = M.map(function (row, i) { return Fr.of(r[i]).sub(p5dotF(row, xF)); });
      var free = [0, 1, 2].filter(function (i) { return slack[i].isZero(); });        // y_i may be > 0
      var eqs = [0, 1].filter(function (j) { return xF[j].sign() > 0; });             // dual constraint j tight
      var y = [Fr(0), Fr(0), Fr(0)], solved = true;
      if (eqs.length !== free.length) solved = false;
      else if (eqs.length) {
        var B = eqs.map(function (j) { return free.map(function (i) { return M[i][j]; }); });
        var sol = frSolve(B, eqs.map(function (j) { return gg[j]; }));
        if (!sol) solved = false; else free.forEach(function (i, k) { y[i] = sol[k]; });
      }
      var red = [0, 1].map(function (j) { return p5dotF(M.map(function (row) { return row[j]; }), y).sub(gg[j]); }); // (M^T y − g)_j
      var yok = y.every(function (z) { return z.sign() >= 0; }), rok = red.every(function (z) { return z.sign() >= 0; });
      return { slack: slack, free: free, eqs: eqs, y: y, red: red, solved: solved, ok: solved && yok && rok, yok: yok, rok: rok };
    }
    function draw() {
      var gg = g(); gS.out.textContent = String(gg[1]);
      p5clear(svg);
      P = p5panel(svg, [40, 20, 270, 260], [0, 7], [0, 6.5]);
      P.axes([0, 1, 2, 3, 4, 5, 6, 7], [0, 1, 2, 3, 4, 5, 6], "x₁ (produit 1)", "x₂ (produit 2)");
      var reg = halfPlanePolygon([[2, 1, 10], [1, 1, 6], [1, 3, 15], [-1, 0, 0], [0, -1, 0]], P.box);
      P.poly(reg, "a1"); P.poly(reg, "ln c1 thin");
      var xv = V[cur], m = method(xv);
      M.forEach(function (row, i) { P.cline(row[0], row[1], r[i], "ln cm " + (m.slack[i].isZero() ? "" : "thin dash")); });
      P.text(4.6, 1.15, "bois", "tx-s", "start", 4, 0, P.gc);
      P.text(2.7, 3.45, "machine", "tx-s", "start", 0, 0, P.gc);
      P.text(0.15, 5.25, "main-d’œuvre", "tx-s", "start", 0, -2, P.gc);
      var oi = optIdx(), prof = gg[0] * V[oi][0] + gg[1] * V[oi][1];
      P.cline(gg[0], gg[1], prof, "ln c2 thin");
      V.forEach(function (v, i) { P.dot(v[0], v[1], i === cur ? 8 : 5, i === oi ? "f3" : "f1"); });
      P.dot(xv[0], xv[1], 12, "ln ck thin nofill");
      // right: the table of products, drawn as bars
      var x0 = 350, rowH = 44, top = 34;
      var t0 = el("text", { x: x0, y: 18, "class": "tx-b" }, svg); t0.textContent = "côté primal";
      var t0b = el("text", { x: x0 + 160, y: 18, "class": "tx-b" }, svg); t0b.textContent = "côté dual";
      var rows = [];
      M.forEach(function (row, i) { rows.push({ lab: names[i], a: "écart s" + "₁₂₃"[i], av: m.slack[i], b: "y" + "₁₂₃"[i], bv: m.y[i] }); });
      [0, 1].forEach(function (j) { rows.push({ lab: "produit " + (j + 1), a: "x" + "₁₂"[j], av: Fr.of(xv[j]), b: "(Mᵀy − g)" + "₁₂"[j], bv: m.red[j] }); });
      rows.forEach(function (rw, k) {
        var y0 = top + k * rowH;
        var t = el("text", { x: x0, y: y0 + 12, "class": "tx-s" }, svg); t.textContent = rw.lab;
        var scaleA = 5, scaleB = 1.5;   // bars ≤ 75 px (primal) and ≤ 60 px (dual): their labels stay inside the figure
        var wa = Math.min(75, Math.abs(rw.av.val()) * scaleA), wb = Math.min(60, Math.abs(rw.bv.val()) * scaleB);
        el("rect", { x: x0, y: y0 + 17, width: Math.max(1.5, wa), height: 10, "class": rw.av.sign() < 0 ? "f6" : "f1" }, svg);
        var ta = el("text", { x: x0 + Math.max(1.5, wa) + 4, y: y0 + 26, "class": "tx-s" }, svg); ta.textContent = rw.a + " = " + rw.av.str();
        el("rect", { x: x0 + 160, y: y0 + 17, width: Math.max(1.5, wb), height: 10, "class": rw.bv.sign() < 0 ? "f6" : "f5" }, svg);
        var tb = el("text", { x: x0 + 160 + Math.max(1.5, wb) + 4, y: y0 + 26, "class": "tx-s" }, svg); tb.textContent = rw.b + " = " + (m.solved ? rw.bv.str() : "?");
        var prod = rw.av.mul(rw.bv);
        var tp = el("text", { x: x0 + 160, y: y0 + 12, "class": prod.isZero() ? "tx-s t3" : "tx-s t6" }, svg);
        tp.textContent = m.solved ? (prod.isZero() ? "produit = 0 ✓" : "produit = " + prod.str()) : "";
      });
      var tl = el("text", { x: x0, y: top + 5 * rowH + 12, "class": m.ok ? "tx-b t3" : "tx-b t6" }, svg);
      tl.textContent = m.ok ? "certificat : profit = r·y, sommet optimal" : "pas de y admissible : sommet non optimal";
      // readout: the method, step by step
      var st = "x = " + Vn[cur] + ", profit g·x = " + Fr.of(gg[0]).mul(Fr.of(xv[0])).add(Fr.of(gg[1]).mul(Fr.of(xv[1]))).str();
      st += "\n1. Écarts primaux s = r − Mx = " + p5vec(m.slack) + " : " + ([0, 1, 2].filter(function (i) { return !m.slack[i].isZero(); }).map(function (i) { return "s" + "₁₂₃"[i] + " > 0 ⇒ y" + "₁₂₃"[i] + " = 0"; }).join(", ") || "toutes les contraintes sont actives");
      st += "\n2. " + (m.eqs.length ? m.eqs.map(function (j) { return "x" + "₁₂"[j] + " > 0 ⇒ " + ["2y₁ + y₂ + y₃", "y₁ + y₂ + 3y₃"][j] + " = " + gg[j]; }).join(" ; ") : "aucune variable > 0 : aucune équation");
      if (!m.solved) st += "\n3. Système sans solution unique : ce point n’est pas un sommet utilisable.";
      else {
        st += "\n3. Solution : y = " + p5vec(m.y) + ", et Mᵀy − g = " + p5vec(m.red);
        if (m.ok) st += "\n4. y ≥ 0 et Mᵀy ≥ g : y est admissible pour le dual, et r·y = " + p5dotF(r, m.y).str() + " = g·x. Optimal (Rem. 4.2.14).";
        else st += "\n4. " + (!m.yok ? "un yᵢ < 0" : "") + (!m.yok && !m.rok ? " et " : "") + (!m.rok ? "une contrainte duale violée (Mᵀy − g a une composante < 0)" : "") + " : aucun prix compatible avec ce sommet, il n’est pas optimal.";
      }
      ro.textContent = st;
    }
    draw(); redrawers.push(draw);
  };

  /* ======================================================================
     3. The six bases of (R): primal point, dual point, same value (§6)
     ====================================================================== */
  WIDGETS.p5bases = function (box) {
    var s = scaffold(box, "Chaque base donne un couple (x, p) avec c·x = b·p : l’optimum, c’est la base où les deux sont admissibles");
    var svg = s.svg;
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Les six bases du problème (R) en forme standard : solution basique primale à gauche, solution basique duale à droite, et leurs valeurs sur une règle");
    var A = [[2, 1, -1, 0], [1, 3, 0, -1]], b = [8, 9], c = [3, 2, 0, 0];
    var all = combinations(4, 2).map(function (cols) { return p5base(cols); }).filter(function (B) { return B; });
    var cur = 1, PX, PP;
    var bSel = select(s.controls, "Base", all.map(function (B, i) { return [String(i), "{" + B.cols.map(function (j) { return "x" + "₁₂₃₄"[j]; }).join(", ") + "}"]; }), "1", function () { cur = parseInt(bSel.value, 10); draw(); });
    var bPrim = button(s.controls, "Pas du simplexe (primal)", function () { stepPrimal(); });
    var bDual = button(s.controls, "Pas du simplexe dual (hors cours)", function () { stepDual(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "x admissible"], ["--s5", "p admissible"], ["--s6", "non admissible"], ["--s3", "base optimale"]]);
    function p5base(cols) {
      var B = A.map(function (row) { return cols.map(function (j) { return row[j]; }); });
      var xb = frSolve(B, b); if (!xb) return null;
      var x = [Fr(0), Fr(0), Fr(0), Fr(0)]; cols.forEach(function (j, k) { x[j] = xb[k]; });
      var Bt = cols.map(function (j) { return A.map(function (row) { return row[j]; }); });
      var p = frSolve(Bt, cols.map(function (j) { return c[j]; }));
      var red = [0, 1, 2, 3].map(function (j) { return Fr.of(c[j]).sub(p5dotF([A[0][j], A[1][j]], p)); });
      return { cols: cols, x: x, p: p, red: red, prim: xb.every(function (v) { return v.sign() >= 0; }), dual: red.every(function (v) { return v.sign() >= 0; }),
        val: p5dotF(c, x), bp: p5dotF(b, p), xb: xb };
    }
    function idxOf(cols) { for (var i = 0; i < all.length; i++) if (all[i].cols[0] === Math.min(cols[0], cols[1]) && all[i].cols[1] === Math.max(cols[0], cols[1])) return i; return -1; }
    function stepPrimal() {
      var B = all[cur]; if (!B.prim || B.dual) return;
      var res = simplex(A, b, c, B.cols.slice(), { rule: "dantzig" });
      if (res.steps.length > 1) { cur = idxOf(res.steps[1].basis); bSel.value = String(cur); draw(); }
    }
    function stepDual() {
      var B = all[cur]; if (!B.dual || B.prim) return;
      // leaving row: most negative x_B ; entering: min ratio red_j / |(B^-1 A)_rj| over (B^-1 A)_rj < 0
      var r = 0; B.xb.forEach(function (v, k) { if (v.cmp(B.xb[r]) < 0) r = k; });
      var Bt = B.cols.map(function (j) { return A.map(function (row) { return row[j]; }); });
      var er = [Fr(0), Fr(0)]; er[r] = Fr(1);
      var u = frSolve(Bt, er); // row r of B^-1
      var best = -1, bestQ = null;
      [0, 1, 2, 3].forEach(function (j) {
        if (B.cols.indexOf(j) >= 0) return;
        var t = p5dotF(u, [A[0][j], A[1][j]]);
        if (t.sign() < 0) { var q = B.red[j].div(t.neg()); if (best < 0 || q.cmp(bestQ) < 0) { best = j; bestQ = q; } }
      });
      if (best < 0) return;
      var nc = B.cols.slice(); nc[r] = best; cur = idxOf(nc); bSel.value = String(cur); draw();
    }
    function draw() {
      p5clear(svg);
      // wide: the two planes side by side; narrow (phone): stacked, with the ruler below
      var L = p5narrow(box) ?
        { W: 360, H: 660, px: [44, 34, 290, 220], pp: [44, 318, 290, 200], t1: [189, 16], t2: [189, 300], lab: [[16, 572, "valeur commune c·x = b·p de chaque base :"], [16, 586, "bleu = x admissible (≥ 13), violet = p admissible (≤ 13)"]], ru: [24, 612, 312, 30] } :
        { W: 680, H: 398, px: [44, 40, 270, 238], pp: [392, 40, 270, 238], t1: [179, 14], t2: [527, 14], lab: [[44, 326, "valeur commune c·x = b·p de chaque base : bleu = x admissible (≥ 13), violet = p admissible (≤ 13)"]], ru: [44, 352, 618, 30] };
      svg.setAttribute("viewBox", "0 0 " + L.W + " " + L.H);
      PX = p5panel(svg, L.px, [-0.5, 10], [-0.5, 9]);
      PP = p5panel(svg, L.pp, [-0.3, 3.3], [-0.3, 3.3]);
      PX.axes([0, 2, 4, 6, 8, 10], [0, 2, 4, 6, 8], "x₁", "x₂");
      PP.axes([0, 1, 2, 3], [0, 1, 2, 3], "p₁", "p₂");
      var t1 = el("text", { x: L.t1[0], y: L.t1[1], "class": "tx-b", "text-anchor": "middle" }, svg); t1.textContent = "primal : x de la base (x₁, x₂)";
      var t2 = el("text", { x: L.t2[0], y: L.t2[1], "class": "tx-b", "text-anchor": "middle" }, svg); t2.textContent = "dual : p tel que Bᵀp = coûts de la base";
      var reg = halfPlanePolygon([[-2, -1, -8], [-1, -3, -9], [-1, 0, 0], [0, -1, 0]], PX.box);
      PX.poly(reg, "a1"); PX.poly(reg, "ln c1 thin");
      PX.cline(2, 1, 8, "ln cm thin"); PX.cline(1, 3, 9, "ln cm thin");
      var dreg = halfPlanePolygon([[2, 1, 3], [1, 3, 2], [-1, 0, 0], [0, -1, 0]], PP.box);
      PP.poly(dreg, "a5"); PP.poly(dreg, "ln c5 thin");
      PP.cline(2, 1, 3, "ln cm thin"); PP.cline(1, 3, 2, "ln cm thin");
      var Bc = all[cur];
      // the two dual lines of the basis, thick: (A^T p)_j = c_j for j in the basis
      Bc.cols.forEach(function (j) { PP.cline(A[0][j], A[1][j], c[j], "ln c5"); });
      // the two primal lines of the basis: x_j = 0 for j out of the basis
      [0, 1, 2, 3].forEach(function (j) {
        if (Bc.cols.indexOf(j) >= 0) return;
        if (j === 0) PX.cline(1, 0, 0, "ln c1"); else if (j === 1) PX.cline(0, 1, 0, "ln c1");
        else if (j === 2) PX.cline(2, 1, 8, "ln c1"); else PX.cline(1, 3, 9, "ln c1");
      });
      all.forEach(function (B, i) {
        var xv = [B.x[0].val(), B.x[1].val()], pv = [B.p[0].val(), B.p[1].val()];
        var sel = i === cur, opt = B.prim && B.dual;
        PX.dot(xv[0], xv[1], sel ? 8 : 5, opt ? "f3" : B.prim ? "f1" : "f6");
        PP.dot(pv[0], pv[1], sel ? 8 : 5, opt ? "f3" : B.dual ? "f5" : "f6");
        var lab = "{" + B.cols.map(function (j) { return j + 1; }).join(",") + "}";
        PX.text(xv[0], xv[1], lab, sel ? "tx-b" : "tx-s", "start", 7, -7);
        PP.text(pv[0], pv[1], lab, sel ? "tx-b" : "tx-s", "start", 7, pv[1] > 2.5 ? 14 : -7);
        if (sel) { PX.dot(xv[0], xv[1], 13, "ln ck thin nofill"); PP.dot(pv[0], pv[1], 13, "ln ck thin nofill"); }
      });
      // ruler with the six values
      var R = p5panel(svg, L.ru, [0, 30], [0, 1]);
      el("line", { x1: R.X(0), x2: R.X(30), y1: R.Y(0.5), y2: R.Y(0.5), "class": "ax" }, svg);
      for (var t = 0; t <= 30; t += 5) {
        el("line", { x1: R.X(t), x2: R.X(t), y1: R.Y(0.5) - 4, y2: R.Y(0.5) + 4, "class": "ax" }, svg);
        var tt = el("text", { x: R.X(t), y: R.Y(0.5) + 18, "class": "tx-s", "text-anchor": "middle" }, svg); tt.textContent = t;
      }
      all.forEach(function (B, i) {
        var v = B.val.val(), X = R.X(v), cls = B.prim && B.dual ? "f3" : B.prim ? "f1" : B.dual ? "f5" : "f6";
        el("circle", { cx: X, cy: R.Y(0.5), r: i === cur ? 7 : 5, "class": cls }, svg);
        var tx = el("text", { x: X, y: R.Y(0.5) - 11 - (B.prim ? 0 : 12), "class": i === cur ? "tx-b" : "tx-s", "text-anchor": "middle" }, svg); tx.textContent = B.val.str();
      });
      L.lab.forEach(function (q) { var lab2 = el("text", { x: q[0], y: q[1], "class": "tx-s" }, svg); lab2.textContent = q[2]; });
      bPrim.disabled = !(Bc.prim && !Bc.dual); bDual.disabled = !(Bc.dual && !Bc.prim);
      var st = "Base {" + Bc.cols.map(function (j) { return "x" + "₁₂₃₄"[j]; }).join(", ") + "} : x = " + p5vec(Bc.x) + (Bc.prim ? " (admissible)" : " (NON admissible : une composante < 0)");
      st += "\np = B⁻ᵀc_B = " + p5vec(Bc.p) + " ; coûts réduits c − Aᵀp = " + p5vec(Bc.red) + (Bc.dual ? " ≥ 0 : p admissible pour le dual" : " : une composante < 0, p NON admissible");
      st += "\nc·x = " + Bc.val.str() + " et b·p = " + Bc.bp.str() + " : égaux, car x·(c − Aᵀp) = 0 (x est nul hors base, les coûts réduits sont nuls dans la base).";
      if (Bc.prim && Bc.dual) st += "\nLes deux sont admissibles : c·x = b·p certifie que x et p sont optimaux.";
      else if (Bc.prim) st += "\nLe simplexe (primal) garde x admissible et cherche à rendre p admissible : bouton « Pas du simplexe (primal) ».";
      else if (Bc.dual) st += "\nLe simplexe dual (hors cours) garde p admissible et cherche à rendre x admissible : bouton « Pas du simplexe dual ».";
      else st += "\nNi x ni p n’est admissible : aucune des deux méthodes ne passe par cette base.";
      ro.textContent = st;
    }
    draw(); redrawers.push(draw); p5onWidth(box, draw);
  };

  /* ======================================================================
     4. Shadow prices (§7) — production example, V(b_i) and its slope
     ====================================================================== */
  WIDGETS.p5ombre = function (box) {
    var s = scaffold(box, "Le prix ombre : faites varier une ressource, la pente du profit optimal est le prix dual");
    var svg = s.svg, W = 680, H = 330;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "À gauche la région de production et son sommet optimal, à droite le profit optimal en fonction de la ressource choisie");
    var M = [[2, 1], [1, 1], [1, 3]], r0 = [10, 6, 15], g = [40, 30], names = ["bois", "machine", "main-d’œuvre"], tmax = [16, 10, 24];
    var res = 0, r = r0.slice();
    var rSel = select(s.controls, "Ressource", names.map(function (n, i) { return [String(i), n]; }), "0", function () { res = parseInt(rSel.value, 10); r = r0.slice(); setSlider(); draw(); });
    var bS = slider(s.controls, "quantité b =", 0, 16, 0.5, 10, function () { r[res] = bS.get(); draw(); });
    button(s.controls, "Valeur du cours", function () { r = r0.slice(); setSlider(); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "région admissible"], ["--s3", "sommet optimal, courbe V"], ["--s5", "tangente de pente yᵢ"], ["--s4", "domaine où le prix ne change pas"]]);
    function setSlider() { bS.input.max = tmax[res]; bS.set(r[res]); }
    // vertices of the dual region D = {M^T y >= g, y >= 0} (it does not depend on r): 3 tight constraints among 5
    var cons = [[[2, 1, 1], 40], [[1, 1, 3], 30], [[1, 0, 0], 0], [[0, 1, 0], 0], [[0, 0, 1], 0]];
    var DV = [];
    combinations(5, 3).forEach(function (tri) {
      var y = frSolve(tri.map(function (k) { return cons[k][0]; }), tri.map(function (k) { return cons[k][1]; }));
      if (!y) return;
      if (!cons.every(function (cn) { return p5dotF(cn[0], y).cmp(Fr.of(cn[1])) >= 0; })) return;
      if (!DV.some(function (z) { return z.every(function (v, i) { return v.cmp(y[i]) === 0; }); })) DV.push(y);
    });
    // V(r) = min over the dual vertices of r·y (strong duality; r >= 0 so the minimum is at a vertex)
    function Vof(rr) { var best = null; DV.forEach(function (y) { var v = p5dotF(rr, y); if (!best || v.cmp(best) < 0) best = v; }); return best; }
    function argmins(rr) { var v = Vof(rr); return DV.filter(function (y) { return p5dotF(rr, y).cmp(v) === 0; }); }
    // breakpoints in t = r_i of the lower envelope min_y (const_y + t y_i)
    function breakpoints(i) {
      var out = [];
      for (var a = 0; a < DV.length; a++) for (var b2 = a + 1; b2 < DV.length; b2++) {
        var ya = DV[a], yb = DV[b2];
        if (ya[i].cmp(yb[i]) === 0) continue;
        var ca = Fr(0), cb = Fr(0);
        for (var k = 0; k < 3; k++) if (k !== i) { ca = ca.add(Fr.of(r[k]).mul(ya[k])); cb = cb.add(Fr.of(r[k]).mul(yb[k])); }
        var t = cb.sub(ca).div(ya[i].sub(yb[i]));
        if (t.val() < 0 || t.val() > tmax[i]) continue;
        var rr = r.slice(); rr[i] = t;
        var V = Vof(rr.map(Fr.of));
        if (p5dotF(rr.map(Fr.of), ya).cmp(V) === 0 && p5dotF(rr.map(Fr.of), yb).cmp(V) === 0 && !out.some(function (z) { return z.cmp(t) === 0; })) out.push(t);
      }
      return out.sort(function (u, v) { return u.cmp(v); });
    }
    function draw() {
      var rF = r.map(Fr.of), t = Fr.of(r[res]);
      bS.out.textContent = t.str();
      p5clear(svg);
      var PL = p5panel(svg, [40, 24, 250, 250], [0, 8], [0, 8]);
      PL.axes([0, 2, 4, 6, 8], [0, 2, 4, 6, 8], "x₁", "x₂");
      var reg = halfPlanePolygon([[2, 1, r[0]], [1, 1, r[1]], [1, 3, r[2]], [-1, 0, 0], [0, -1, 0]], PL.box);
      PL.poly(reg, "a1"); PL.poly(reg, "ln c1 thin");
      M.forEach(function (row, i) { PL.cline(row[0], row[1], r[i], i === res ? "ln c4" : "ln cm thin"); });
      var best = null; reg.forEach(function (v) { var val = g[0] * v[0] + g[1] * v[1]; if (!best || val > best[2] + 1e-9) best = [v[0], v[1], val]; });
      if (best) { PL.cline(g[0], g[1], best[2], "ln c2 thin"); PL.dot(best[0], best[1], 6, "f3"); }
      var tl = el("text", { x: 165, y: 14, "class": "tx-b", "text-anchor": "middle" }, svg); tl.textContent = "production : " + names[res] + " = " + t.str();
      // right panel: V(t)
      var bps = breakpoints(res), ts = [Fr(0)].concat(bps, [Fr(tmax[res])]);
      var pts = ts.map(function (tt) { var rr = rF.slice(); rr[res] = tt; return [tt.val(), Vof(rr).val()]; });
      var vmax = Math.max.apply(null, pts.map(function (q) { return q[1]; }));
      var ymax = Math.ceil((vmax + 20) / 50) * 50;
      var PR = p5panel(svg, [372, 24, 290, 250], [0, tmax[res]], [0, ymax]);
      var xt = []; for (var k = 0; k <= tmax[res]; k += (tmax[res] > 12 ? 4 : 2)) xt.push(k);
      var yt = []; for (var q = 0; q <= ymax; q += 50) yt.push(q);
      PR.axes(xt, yt, "b (" + names[res] + ")", "V(b) = profit maximal");
      var mins = argmins(rF), left = null, right = null;
      mins.forEach(function (y) { if (!left || y[res].cmp(left) > 0) left = y[res]; if (!right || y[res].cmp(right) < 0) right = y[res]; });
      // validity interval of the current price (right slope): between the breakpoints around t
      var lo = Fr(0), hi = Fr(tmax[res]), prev = Fr(0);
      bps.forEach(function (bp) { if (bp.cmp(t) <= 0 && bp.cmp(lo) > 0) lo = bp; if (bp.cmp(t) > 0 && bp.cmp(hi) < 0) hi = bp; if (bp.cmp(t) < 0 && bp.cmp(prev) > 0) prev = bp; });
      var isBp = bps.some(function (bp) { return bp.cmp(t) === 0; });
      el("rect", { x: PR.X(lo.val()), y: PR.Y(0) - 5, width: Math.max(2, PR.X(hi.val()) - PR.X(lo.val())), height: 10, "class": "a4" }, svg);
      PR.poly(pts, "ln c3", PR.gc, false);
      pts.forEach(function (q, k) { if (k > 0 && k < pts.length - 1) PR.dot(q[0], q[1], 3.5, "f3"); });
      var Vt = Vof(rF).val();
      var sl = right.val();
      PR.line(t.val() - 3, Vt - 3 * sl, t.val() + 3, Vt + 3 * sl, "ln c5 thin dash", PR.gc);
      PR.dot(t.val(), Vt, 6, "f5");
      PR.line(t.val(), 0, t.val(), Vt, "ln cm thin dot", PR.gc);
      var ys = mins[0];
      var st = "b = " + p5vec(rF) + " : profit maximal V = " + Vof(rF).str() + (best ? ", atteint en x = (" + frac(best[0]) + ", " + frac(best[1]) + ")" : "");
      st += "\nprix duaux (solution du dual min b·y, Mᵀy ≥ g, y ≥ 0) : y = " + p5vec(ys) + (mins.length > 1 ? " — non unique, autres : " + mins.slice(1).map(p5vec).join(", ") : "");
      // a final slope 0 lasts for ever: V is non-decreasing (more resource never hurts) and concave
      var hiStr = hi.cmp(Fr(tmax[res])) === 0 && right.isZero() ? "+∞[" : hi.str() + "]";
      if (isBp && left.cmp(right) !== 0) {
        st += "\nb est un point anguleux de V : pente à gauche " + left.str() + " (sur [" + prev.str() + " ; " + t.str() + "]), pente à droite " + right.str() + " (sur [" + t.str() + " ; " + hiStr + ", bande dorée) : le dual a plusieurs solutions.";
      } else {
        st += "\npente de V en b = y" + "₁₂₃"[res] + " = " + right.str() + " : une unité de " + names[res] + " en plus rapporte " + right.str() + " (prix ombre).";
        st += "\nCe prix reste valable pour b dans [" + lo.str() + " ; " + hiStr + " (bande dorée) : la base optimale ne change pas.";
      }
      ro.textContent = st;
    }
    setSlider(); draw(); redrawers.push(draw);
  };

  /* ======================================================================
     5. The call centre (§8)
     ====================================================================== */
  WIDGETS.p5centre = function (box) {
    var s = scaffold(box, "Le centre d’appels : planifiez vous-même, ou changez la demande et lisez les prix duaux");
    var svg = s.svg, W = 680, H = 330;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Trois tranches horaires sur la journée, et pour chacun des cinq intervalles la demande, l’effectif et le prix dual");
    var U = [[1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1]], S = [4, 5, 6], c0 = [5, 10, 6, 12, 4];
    var c = c0.slice(), x = [6, 9, 5];
    var mode = select(s.controls, "Mode", [["plan", "planifier soi-même (x)"], ["dem", "changer la demande (c)"]], "plan", function () { vis(); draw(); });
    var xs = [0, 1, 2].map(function (i) { return slider(s.controls, "x" + "₁₂₃"[i] + " =", 0, 20, 1, x[i], function () { x[i] = xs[i].get(); draw(); }); });
    var cs = [0, 1, 2, 3, 4].map(function (j) { return slider(s.controls, "c" + "₁₂₃₄₅"[j] + " =", 0, 20, 1, c[j], function () { c[j] = cs[j].get(); draw(); }); });
    var bOpt = button(s.controls, "Planning optimal", function () { x = solveP(c).x.map(function (v) { return v.val(); }); x.forEach(function (v, i) { xs[i].set(v); }); draw(); });
    button(s.controls, "Données du cours", function () { c = c0.slice(); cs.forEach(function (sl, j) { sl.set(c[j]); }); x = [6, 9, 5]; xs.forEach(function (sl, i) { sl.set(x[i]); }); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s2", "clients cⱼ"], ["--s1", "effectif (Ux)ⱼ"], ["--s5", "prix dual pⱼ"], ["--s6", "intervalle non couvert"]]);
    function vis() {
      var m = mode.value;
      xs.forEach(function (sl) { sl.input.parentNode.style.display = m === "plan" ? "" : "none"; });
      cs.forEach(function (sl) { sl.input.parentNode.style.display = m === "dem" ? "" : "none"; });
      bOpt.style.display = m === "plan" ? "" : "none";
    }
    // exact primal optimum: 3 tight constraints among U x >= c (5) and x >= 0 (3)
    function solveP(cc) {
      var rows = U.map(function (row, j) { return [row, cc[j]]; }).concat([[[1, 0, 0], 0], [[0, 1, 0], 0], [[0, 0, 1], 0]]);
      var best = null;
      combinations(8, 3).forEach(function (tri) {
        var z = frSolve(tri.map(function (k) { return rows[k][0]; }), tri.map(function (k) { return rows[k][1]; }));
        if (!z || !rows.every(function (rw) { return p5dotF(rw[0], z).cmp(Fr.of(rw[1])) >= 0; })) return;
        var v = p5dotF(S, z);
        if (!best || v.cmp(best.v) < 0) best = { v: v, x: z };
      });
      return best;
    }
    // exact dual optima: 5 tight constraints among U^T p <= S (3) and p >= 0 (5)
    var UT = [0, 1, 2].map(function (i) { return U.map(function (row) { return row[i]; }); });
    function solveD(cc) {
      var rows = UT.map(function (col, i) { return [col, S[i]]; });
      for (var j = 0; j < 5; j++) { var e = [0, 0, 0, 0, 0]; e[j] = -1; rows.push([e, 0]); }
      var best = null, arg = [];
      combinations(8, 5).forEach(function (five) {
        var z = frSolve(five.map(function (k) { return rows[k][0]; }), five.map(function (k) { return rows[k][1]; }));
        if (!z || !rows.every(function (rw) { return p5dotF(rw[0], z).cmp(Fr.of(rw[1])) <= 0; })) return;
        var v = p5dotF(cc, z);
        if (!best || v.cmp(best) > 0) { best = v; arg = [z]; }
        else if (v.cmp(best) === 0 && !arg.some(function (a) { return a.every(function (q, i) { return q.cmp(z[i]) === 0; }); })) arg.push(z);
      });
      return { v: best, p: arg };
    }
    function draw() {
      xs.forEach(function (sl, i) { sl.out.textContent = String(x[i]); });
      cs.forEach(function (sl, j) { sl.out.textContent = String(c[j]); });
      var P = solveP(c), D = solveD(c), pd = D.p[0];
      var xx = mode.value === "plan" ? x : P.x.map(function (v) { return v.val(); });
      p5clear(svg);
      var L = 70, R = 640, X = function (t) { return L + (R - L) * t / 5; };
      var names = ["α₁ = 0", "α₂", "β₁", "α₃", "β₂", "β₃ = 24"];
      [[0, 2], [1, 4], [3, 5]].forEach(function (ab, k) {
        var y = 10 + k * 24;
        el("rect", { x: X(ab[0]), y: y, width: X(ab[1]) - X(ab[0]), height: 17, rx: 4, "class": "a1" }, svg);
        el("rect", { x: X(ab[0]), y: y, width: X(ab[1]) - X(ab[0]), height: 17, rx: 4, "class": "ln c1 thin" }, svg);
        var t = el("text", { x: (X(ab[0]) + X(ab[1])) / 2, y: y + 13, "class": "tx-s", "text-anchor": "middle" }, svg);
        t.textContent = "tranche " + (k + 1) + " : S" + "₁₂₃"[k] + " = " + S[k] + " ; x" + "₁₂₃"[k] + " = " + frac(xx[k]);
      });
      var ya = 96;
      el("line", { x1: L, y1: ya, x2: R, y2: ya, "class": "ax" }, svg);
      names.forEach(function (nm, k) {
        el("line", { x1: X(k), y1: 8, x2: X(k), y2: ya, "class": "gr" }, svg);
        var t = el("text", { x: X(k), y: ya + 15, "class": "tx-s", "text-anchor": "middle" }, svg); t.textContent = nm;
      });
      var staff = U.map(function (row) { return row[0] * xx[0] + row[1] * xx[1] + row[2] * xx[2]; });
      var base = 276, mx = Math.max(14, Math.max.apply(null, c.concat(staff))), sc = 140 / mx;
      for (var j = 0; j < 5; j++) {
        var x1 = X(j) + 8, w = (X(j + 1) - X(j) - 16) / 2 - 2;
        var bad = staff[j] < c[j] - 1e-9;
        el("rect", { x: x1, y: base - c[j] * sc, width: w, height: c[j] * sc, "class": "f2", "fill-opacity": 0.75 }, svg);
        el("rect", { x: x1 + w + 4, y: base - staff[j] * sc, width: w, height: staff[j] * sc, "class": bad ? "f6" : "f1", "fill-opacity": 0.75 }, svg);
        var a = el("text", { x: x1 + w / 2, y: base - c[j] * sc - 4, "class": "tx-s t2", "text-anchor": "middle" }, svg); a.textContent = c[j];
        var b2 = el("text", { x: x1 + w * 1.5 + 4, y: base - staff[j] * sc - 4, "class": bad ? "tx-s t6" : "tx-s t1", "text-anchor": "middle" }, svg); b2.textContent = frac(staff[j]);
        var pl = el("text", { x: (X(j) + X(j + 1)) / 2, y: base + 15, "class": "tx-s t5", "text-anchor": "middle" }, svg);
        pl.textContent = "I" + "₁₂₃₄₅"[j] + " : p" + "₁₂₃₄₅"[j] + " = " + pd[j].str();
      }
      el("line", { x1: L, y1: base, x2: R, y2: base, "class": "ax" }, svg);
      var tt = el("text", { x: L - 6, y: base - 120, "class": "tx-s t2", "text-anchor": "end" }, svg); tt.textContent = "clients";
      var tu = el("text", { x: L - 6, y: base - 106, "class": "tx-s t1", "text-anchor": "end" }, svg); tu.textContent = "effectif";
      var tv = el("text", { x: L - 6, y: base + 15, "class": "tx-s t5", "text-anchor": "end" }, svg); tv.textContent = "prix";
      var st;
      if (mode.value === "plan") {
        var cost = S[0] * x[0] + S[1] * x[1] + S[2] * x[2];
        var unc = [0, 1, 2, 3, 4].filter(function (j) { return staff[j] < c[j]; });
        st = "Votre planning x = (" + x.join(", ") + ") coûte S·x = " + cost + ".";
        if (unc.length) st += "\nNon admissible : intervalle(s) " + unc.map(function (j) { return "I" + "₁₂₃₄₅"[j]; }).join(", ") + " non couvert(s).";
        else {
          var sur = staff.map(function (v, j) { return v - c[j]; });
          var red = [0, 1, 2].map(function (i) { return S[i] - (UT[i][0] * pd[0].val() + UT[i][1] * pd[1].val() + UT[i][2] * pd[2].val() + UT[i][3] * pd[3].val() + UT[i][4] * pd[4].val()); });
          st += "\nAdmissible. Le dual donne une borne : tout planning coûte au moins c·p̄ = " + D.v.str() + ".";
          st += "\nÉcart S·x − c·p̄ = Σ p̄ⱼ × surplusⱼ + Σ xᵢ (S − Uᵀp̄)ᵢ = " + sur.map(function (v, j) { return pd[j].str() + "×" + v; }).join(" + ") +
            " + " + red.map(function (v, i) { return x[i] + "×" + frac(v); }).join(" + ") + " = " + frac(cost - D.v.val()) + ".";
          st += cost - D.v.val() < 1e-9 ? "\nÉcart nul : votre planning est optimal." : "\nChaque opérateur en surplus sur un intervalle de prix p̄ⱼ > 0 coûte p̄ⱼ de trop.";
        }
      } else {
        st = "Demande c = (" + c.join(", ") + ") : planning optimal x* = " + p5vec(P.x) + ", coût " + P.v.str() + " = c·p (dual) avec p = " + p5vec(pd) + ".";
        if (D.p.length > 1) st += "\nPrix duaux non uniques : les sommets optimaux du dual sont " + D.p.map(p5vec).join(" et ") + " (et toutes leurs combinaisons convexes) ; c’est un point anguleux du coût optimal.";
        var deltas = [0, 1, 2, 3, 4].map(function (j) { var cc = c.slice(); cc[j] += 1; return solveP(cc).v.sub(P.v).str(); });
        st += "\nUn client de plus sur I₁…I₅ coûte réellement : " + deltas.join(", ") + "   (prix duaux : " + pd.map(function (q) { return q.str(); }).join(", ") + ").";
        st += "\nQuand les deux listes diffèrent, la base optimale change avant une unité : le prix n’est valable que localement.";
        st += P.x.every(function (v) { return v.d === 1; }) ? "\nLe planning optimal est entier sans qu’on l’ait demandé (matrice totalement unimodulaire, partie 6)." : "";
      }
      ro.textContent = st;
    }
    vis(); draw(); redrawers.push(draw);
  };
