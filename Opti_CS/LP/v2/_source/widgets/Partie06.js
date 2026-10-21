// widgets/Partie06.js — figures interactives de la partie 6 (nombres entiers et totale unimodularité).
// Inséré par build.mjs dans la portée de app.js : utilise el, Plot, scaffold, slider, select, button, checkbox,
// readout, legend, fmt, Fr, frDet, frSolve, basicSolution, combinations, svgPoint, lineInBox.

  /* --- outils communs de la page (préfixés p6) --- */
  // Enveloppe convexe d'une liste de points entiers [[x, y], …] (chaîne monotone), sens trigonométrique.
  function p6hull(points) {
    var P = points.slice().sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
    if (P.length < 3) return P;
    function cr(o, a, b) { return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]); }
    var lo = [], up = [], i;
    for (i = 0; i < P.length; i++) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], P[i]) <= 0) lo.pop(); lo.push(P[i]); }
    for (i = P.length - 1; i >= 0; i--) { while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], P[i]) <= 0) up.pop(); up.push(P[i]); }
    return lo.slice(0, -1).concat(up.slice(0, -1));
  }
  // Sommets exacts (Fr) du polygone {a x + b y ≤ r} (contraintes entières), triés par angle.
  function p6vertices(cons) {
    var V = [], i, j;
    for (i = 0; i < cons.length; i++) for (j = i + 1; j < cons.length; j++) {
      var a1 = cons[i][0], b1 = cons[i][1], r1 = cons[i][2], a2 = cons[j][0], b2 = cons[j][1], r2 = cons[j][2];
      var d = a1 * b2 - a2 * b1;
      if (d === 0) continue;
      var x = Fr(r1 * b2 - b1 * r2, d), y = Fr(a1 * r2 - a2 * r1, d);
      var ok = cons.every(function (h) { return Fr(h[0]).mul(x).add(Fr(h[1]).mul(y)).cmp(Fr(h[2])) <= 0; });
      if (ok && !V.some(function (v) { return v[0].cmp(x) === 0 && v[1].cmp(y) === 0; })) V.push([x, y]);
    }
    if (!V.length) return V;
    var cx = 0, cy = 0;
    V.forEach(function (v) { cx += v[0].val(); cy += v[1].val(); });
    cx /= V.length; cy /= V.length;
    V.sort(function (p, q) { return Math.atan2(p[1].val() - cy, p[0].val() - cx) - Math.atan2(q[1].val() - cy, q[0].val() - cx); });
    return V;
  }
  function p6pt(p) { return "(" + (p[0].str ? p[0].str() : String(p[0]).replace("-", "−")) + " ; " + (p[1].str ? p[1].str() : String(p[1]).replace("-", "−")) + ")"; }
  function p6ipt(p) { return "(" + String(p[0]).replace("-", "−") + ", " + String(p[1]).replace("-", "−") + ")"; }
  function p6cross(g, x, y, s, cls) {
    el("line", { x1: x - s, y1: y - s, x2: x + s, y2: y + s, "class": cls }, g);
    el("line", { x1: x - s, y1: y + s, x2: x + s, y2: y - s, "class": cls }, g);
  }

  /* --- 1. Le réseau des points entiers d'un polygone (§2) --- */
  WIDGETS.p6reseau = function (box) {
    var s = scaffold(box, "Points entiers d'un polygone : optimum continu, arrondis, optimum entier, enveloppe convexe");
    var W = 680, H = 430;
    var plot = new Plot(s.svg, { x: [0, 1], y: [0, 1], w: W, h: H, pad: { l: 36, r: 14, t: 14, b: 30 }, label: "Polygone, points entiers et optima" });
    var ex = select(s.controls, "Exemple", [["d18", "diapo 18 (sac-à-dos)"], ["fin", "triangle fin"], ["ent", "sommets entiers"]], "d18", function () { setDefaults(); draw(); });
    var sL = slider(s.controls, "capacité L", 20, 80, 1, 59, draw);
    var sA = slider(s.controls, "c₁", -3, 3, 1, 1, draw);
    var sB = slider(s.controls, "c₂", 0, 20, 1, 11, draw);
    var cbH = checkbox(s.controls, "enveloppe convexe des points entiers", false, draw);
    var cbN = checkbox(s.controls, "lignes de niveau", true, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "P (continu)"], ["--s4", "points entiers / enveloppe"], ["--s3", "optimum continu"], ["--s6", "arrondi hors de P"], ["--muted", "arrondi admissible"], ["--s2", "lignes de niveau du coût"]]);
    function setDefaults() {
      var e = ex.value;
      if (e === "ent") { sB.input.min = -3; sB.input.max = 3; sB.set(2); sA.set(1); }
      else { sB.input.min = 0; sB.input.max = 20; sB.set(11); }
      if (e === "d18") sL.set(59);
    }
    function data() {
      var e = ex.value, L = Math.round(sL.get());
      if (e === "d18") return { cons: [[10, 12, L], [-1, 0, 0], [0, -1, 0]], c: [10, Math.round(sB.get())], main: [0], lab: ["10x₁ + 12x₂ = " + L] };
      if (e === "fin") return { cons: [[-4, 2, -1], [4, 2, 11], [0, -1, 0]], c: [0, 1], main: [0, 1], lab: ["4x₁ − 2x₂ = 1", "4x₁ + 2x₂ = 11"] };
      return { cons: [[1, 0, 4], [0, 1, 3], [1, 1, 5], [-1, 0, 0], [0, -1, 0]], c: [Math.round(sA.get()), Math.round(sB.get())], main: [0, 1, 2], lab: ["x₁ = 4", "x₂ = 3", "x₁ + x₂ = 5"] };
    }
    function draw() {
      var e = ex.value, D = data(), cons = D.cons, c = D.c;
      sL.out.textContent = String(Math.round(sL.get()));
      sA.out.textContent = String(Math.round(sA.get())).replace("-", "−");
      sB.out.textContent = String(Math.round(sB.get())).replace("-", "−");
      sL.input.parentNode.style.display = e === "d18" ? "" : "none";
      sA.input.parentNode.style.display = e === "ent" ? "" : "none";
      sB.input.parentNode.style.display = e === "fin" ? "none" : "";
      var V = p6vertices(cons);
      // valeurs et optimum continu (maximisation)
      var best = null, nOpt = 0;
      V.forEach(function (v) {
        var val = Fr(c[0]).mul(v[0]).add(Fr(c[1]).mul(v[1]));
        if (!best || val.cmp(best.val) > 0) { best = { v: v, val: val }; nOpt = 1; }
        else if (val.cmp(best.val) === 0) nOpt++;
      });
      // points entiers
      var xmax = Math.max.apply(null, V.map(function (v) { return v[0].val(); })), ymax = Math.max.apply(null, V.map(function (v) { return v[1].val(); }));
      var xmin = Math.min.apply(null, V.map(function (v) { return v[0].val(); })), ymin = Math.min.apply(null, V.map(function (v) { return v[1].val(); }));
      function feas(p) { return cons.every(function (h) { return h[0] * p[0] + h[1] * p[1] <= h[2]; }); }
      var pts = [], i, j;
      for (i = Math.floor(xmin); i <= Math.ceil(xmax); i++) for (j = Math.floor(ymin); j <= Math.ceil(ymax); j++) if (feas([i, j])) pts.push([i, j]);
      var ibest = -Infinity, iopt = [];
      pts.forEach(function (p) {
        var v = c[0] * p[0] + c[1] * p[1];
        if (v > ibest) { ibest = v; iopt = [p]; } else if (v === ibest) iopt.push(p);
      });
      // cadre à l'échelle 1 : 1
      var x0 = Math.min(-0.5, xmin - 0.5), x1 = Math.max(xmax + 0.8, 3), y0 = Math.min(-0.5, ymin - 0.5), y1 = Math.max(ymax + 0.8, 3);
      var pw = W - 36 - 14, ph = H - 14 - 30, sc = Math.min(pw / (x1 - x0), ph / (y1 - y0));
      var cxm = (x0 + x1) / 2, cym = (y0 + y1) / 2;
      plot.o.x = [cxm - pw / sc / 2, cxm + pw / sc / 2]; plot.o.y = [cym - ph / sc / 2, cym + ph / sc / 2];
      plot.clear();
      var tx = [], ty = [];
      for (i = Math.ceil(plot.o.x[0]); i <= plot.o.x[1]; i++) tx.push(i);
      for (j = Math.ceil(plot.o.y[0]); j <= plot.o.y[1]; j++) ty.push(j);
      plot.axes({ xticks: tx, yticks: ty, cross: true });
      var poly = V.map(function (v) { return [v[0].val(), v[1].val()]; });
      plot.poly(poly.concat([poly[0]]), "a1");
      plot.poly(poly.concat([poly[0]]), "ln c1 thin");
      var bx = [plot.o.x[0], plot.o.x[1], plot.o.y[0], plot.o.y[1]];
      D.main.forEach(function (k, m) {
        var h = cons[k], seg = lineInBox(h[0], h[1], h[2], bx);
        if (!seg) return;
        plot.seg(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln cm thin");
        var q = seg[0][1] < seg[1][1] ? seg[0] : seg[1];
        if (e === "d18") q = [h[2] / 10 * 0.62, (h[2] - h[2] * 0.62) / 12];
        if (e === "ent" && k === 0) q = [4, plot.o.y[1] - 0.4];
        if (e === "ent" && k === 1) q = [plot.o.x[1] - 1.6, 3];
        if (e === "ent" && k === 2) q = [3.25, 2.25];
        var t = plot.text(q[0], q[1], D.lab[m], "tx-s", "start", e === "d18" ? 22 : 6, e === "d18" ? 4 : -6);
        if (e === "fin") { t.setAttribute("text-anchor", m === 0 ? "end" : "start"); t.setAttribute("x", plot.tx(m === 0 ? 0.75 : 2.25)); t.setAttribute("y", plot.ty(1.9)); }
      });
      var hull = p6hull(pts);
      if (cbH.checked && hull.length >= 3) {
        plot.poly(hull.concat([hull[0]]), "a4");
        plot.poly(hull.concat([hull[0]]), "ln c4 dash");
      } else if (cbH.checked && hull.length === 2) plot.seg(hull[0][0], hull[0][1], hull[1][0], hull[1][1], "ln c4 dash");
      // points entiers (admissibles en or, les autres en gris)
      for (i = Math.ceil(plot.o.x[0]); i <= plot.o.x[1]; i++) for (j = Math.ceil(plot.o.y[0]); j <= plot.o.y[1]; j++) {
        if (feas([i, j])) plot.dot(i, j, 4, "f4"); else plot.dot(i, j, 1.8, "fm");
      }
      // lignes de niveau
      var bv = best.val.val();
      if (cbN.checked && (c[0] !== 0 || c[1] !== 0)) {
        var l1 = lineInBox(c[0], c[1], bv, bx), l2 = lineInBox(c[0], c[1], ibest, bx);
        if (l1) plot.seg(l1[0][0], l1[0][1], l1[1][0], l1[1][1], "ln c2 dash");
        if (l2 && Math.abs(ibest - bv) > 1e-9) plot.seg(l2[0][0], l2[0][1], l2[1][0], l2[1][1], "ln c2 thin");
      }
      // optimum continu, puis ses arrondis par-dessus (l'arrondi (6, 0) est à 0,1 unité de (5,9 ; 0))
      var ov = best.v, fx = [Math.floor(ov[0].val() + 1e-12), Math.ceil(ov[0].val() - 1e-12)], fy = [Math.floor(ov[1].val() + 1e-12), Math.ceil(ov[1].val() - 1e-12)];
      var rounds = [];
      fx.forEach(function (a) { fy.forEach(function (b) { if (!rounds.some(function (r) { return r[0] === a && r[1] === b; })) rounds.push([a, b]); }); });
      var integral = rounds.length === 1;
      plot.dot(ov[0].val(), ov[1].val(), integral ? 5 : 5.5, "f3");
      if (!integral) rounds.forEach(function (r) {
        if (feas(r)) el("rect", { x: plot.tx(r[0]) - 6, y: plot.ty(r[1]) - 6, width: 12, height: 12, "class": "fm", "fill-opacity": 0.85 }, plot.g);
        else p6cross(plot.g, plot.tx(r[0]), plot.ty(r[1]), 6, "ln c6");
      });
      // optimum entier (si l'optimum continu est entier, il est redessiné par-dessus)
      iopt.forEach(function (p) { plot.dot(p[0], p[1], 7, "f4"); el("circle", { cx: plot.tx(p[0]), cy: plot.ty(p[1]), r: 10.5, "class": "ln ck thin nofill" }, plot.g); });
      if (integral) plot.dot(ov[0].val(), ov[1].val(), 5, "f3");
      // texte
      var cs = "(" + String(c[0]).replace("-", "−") + ", " + String(c[1]).replace("-", "−") + ")";
      var txt = "Coût à maximiser c·x avec c = " + cs + ".\n";
      var zeroC = c[0] === 0 && c[1] === 0;
      txt += "Optimum continu : " + p6pt(ov) + ", valeur " + best.val.str() + (zeroC ? "  (coût nul : tout P est optimal)" : nOpt > 1 ? "  (ex æquo avec un autre sommet : toute une arête est optimale)" : "") + ".\n";
      if (integral) txt += "Il est entier : c'est aussi l'optimum entier (§1), les deux valeurs sont égales.\n";
      else {
        txt += "Arrondis : " + rounds.map(function (r) {
          if (feas(r)) return p6ipt(r) + " admissible, valeur " + (c[0] * r[0] + c[1] * r[1]);
          var bad = cons.filter(function (h) { return h[0] * r[0] + h[1] * r[1] > h[2]; })[0];
          return p6ipt(r) + " hors de P";
        }).join(" ; ") + ".\n";
      }
      txt += "Optimum entier (énumération des " + pts.length + " points entiers de P) : " + (iopt.length > 4 ? iopt.length + " points ex æquo" : iopt.map(p6ipt).join(" et ")) + ", valeur " + String(ibest).replace("-", "−") + ".\n";
      var gap = best.val.sub(Fr(ibest));
      txt += "Écart de relaxation = " + gap.str() + (gap.isZero() ? " : égalité min entier = min continu." : ".");
      if (cbH.checked) txt += "\nEnveloppe convexe des points entiers : sommets " + hull.map(p6ipt).join(", ") + ".";
      ro.textContent = txt;
    }
    setDefaults(); draw(); redrawers.push(draw);
  };

  /* --- 2. Cramer et le réseau image A Z² (§4) --- */
  WIDGETS.p6cramer = function (box) {
    var s = scaffold(box, "Cramer et le réseau image A ℤ² : A⁻¹b est entier pour tout b entier ⟺ det A = ±1");
    var W = 680, H = 440, pad = { l: 30, r: 14, t: 14, b: 28 };
    var xr = 4.5, yr = xr * (H - pad.t - pad.b) / (W - pad.l - pad.r);
    var plot = new Plot(s.svg, { x: [-xr, xr], y: [-yr, yr], w: W, h: H, pad: pad, label: "Réseau image A Z2, parallélogramme des colonnes et second membre b" });
    var b = [1, 0];
    var sl = [["a₁₁", 1], ["a₁₂", 1], ["a₂₁", -1], ["a₂₂", 1]].map(function (d) { return slider(s.controls, d[0], -3, 3, 1, d[1], draw); });
    [["det 1", [2, 1, 1, 1]], ["det 2", [1, 1, -1, 1]], ["det 3", [2, 1, 1, 2]], ["det 0", [1, 2, 1, 2]]].forEach(function (p) {
      button(s.controls, p[0], function () { p[1].forEach(function (v, i) { sl[i].set(v); }); draw(); });
    });
    var ro = readout(s.controls);
    legend(s.legend, [["--s4", "A ℤ² (b atteints)"], ["--muted", "autres points de ℤ²"], ["--s3", "colonnes a₁, a₂ et parallélogramme"], ["--s2", "b = x₁a₁ + x₂a₂"]]);
    s.svg.addEventListener("click", function (e) {
      var p = svgPoint(s.svg, e), x = Math.round(plot.ix(p.x)), y = Math.round(plot.iy(p.y));
      if (Math.abs(x) <= Math.floor(xr) && Math.abs(y) <= Math.floor(yr)) { b = [x, y]; draw(); }
    });
    function draw() {
      var a = sl.map(function (t) { return Math.round(t.get()); });
      sl.forEach(function (t, i) { t.out.textContent = String(a[i]).replace("-", "−"); });
      var A = [[a[0], a[1]], [a[2], a[3]]], D = a[0] * a[3] - a[1] * a[2];
      plot.clear();
      var mk2 = arrowMarker(s.svg, "f3"), mk3 = arrowMarker(s.svg, "f2");
      var tx = [], ty = [], i, j;
      for (i = -Math.floor(xr); i <= Math.floor(xr); i++) tx.push(i);
      for (j = -Math.floor(yr); j <= Math.floor(yr); j++) ty.push(j);
      plot.axes({ xticks: tx, yticks: ty, cross: true });
      var a1 = [a[0], a[2]], a2 = [a[1], a[3]];
      plot.clip();
      var par = [[0, 0], a1, [a1[0] + a2[0], a1[1] + a2[1]], a2, [0, 0]];
      plot.poly(par, "a3"); plot.poly(par, "ln c3 thin");
      // points de Z² : dans A Z² ?
      function inImage(p) {
        if (D !== 0) return ((a[3] * p[0] - a[1] * p[1]) % D === 0) && ((-a[2] * p[0] + a[0] * p[1]) % D === 0);
        for (var u = -12; u <= 12; u++) for (var v = -12; v <= 12; v++) if (a[0] * u + a[1] * v === p[0] && a[2] * u + a[3] * v === p[1]) return true;
        return false;
      }
      var nIn = 0, nTot = 0;
      for (i = -Math.floor(xr); i <= Math.floor(xr); i++) for (j = -Math.floor(yr); j <= Math.floor(yr); j++) {
        var ok = inImage([i, j]); nTot++; if (ok) nIn++;
        plot.dot(i, j, ok ? 4.5 : 2, ok ? "f4" : "fm");
      }
      el("line", { x1: plot.tx(0), y1: plot.ty(0), x2: plot.tx(a1[0]), y2: plot.ty(a1[1]), "class": "ln c3", "marker-end": mk2 }, plot.g);
      el("line", { x1: plot.tx(0), y1: plot.ty(0), x2: plot.tx(a2[0]), y2: plot.ty(a2[1]), "class": "ln c3", "marker-end": mk2 }, plot.g);
      plot.unclip();
      plot.text(a1[0], a1[1], "a₁", "tx-b t3", "start", 7, 14);
      plot.text(a2[0], a2[1], "a₂", "tx-b t3", "end", -7, -6);
      function pn(v) { return v < 0 ? "(" + v + ")" : String(v); }
      var txt = "A = (" + a[0] + " " + a[1] + " ; " + a[2] + " " + a[3] + ")   det A = " + pn(a[0]) + "·" + pn(a[3]) + " − " + pn(a[1]) + "·" + pn(a[2]) + " = " + D;
      txt = txt.replace(/-/g, "−");
      var good;
      if (D !== 0) {
        var n1 = b[0] * a[3] - a[1] * b[1], n2 = a[0] * b[1] - b[0] * a[2];
        var x1 = Fr(n1, D), x2 = Fr(n2, D);
        good = x1.d === 1 && x2.d === 1;
        var p1 = [x1.val() * a1[0], x1.val() * a1[1]];
        plot.clip();
        el("line", { x1: plot.tx(0), y1: plot.ty(0), x2: plot.tx(p1[0]), y2: plot.ty(p1[1]), "class": "ln c2 dash" }, plot.g);
        el("line", { x1: plot.tx(p1[0]), y1: plot.ty(p1[1]), x2: plot.tx(b[0]), y2: plot.ty(b[1]), "class": "ln c2 dash", "marker-end": mk3 }, plot.g);
        plot.unclip();
        var inv = [Fr(a[3], D), Fr(-a[1], D), Fr(-a[2], D), Fr(a[0], D)];
        txt += "   A⁻¹ = (" + inv[0].str() + " " + inv[1].str() + " ; " + inv[2].str() + " " + inv[3].str() + ")" + (inv.every(function (q) { return q.d === 1; }) ? " : entière" : " : pas entière");
        function q(n) { var raw = String(n).replace("-", "−") + "/" + (D < 0 ? "(" + String(D).replace("-", "−") + ")" : String(D)); var f = Fr(n, D).str(); return raw === f ? raw : raw + " = " + f; }
        txt += "\nb = " + p6ipt(b) + "   Cramer : x₁ = det(b | a₂)/det A = " + q(n1) + ",  x₂ = det(a₁ | b)/det A = " + q(n2);
        txt += "\nA⁻¹b = (" + x1.str() + " ; " + x2.str() + ") : " + (good ? "entier, b ∈ A ℤ²." : "pas entier, b ∉ A ℤ².");
        txt += "\nPoints dorés dans le cadre : " + nIn + " sur " + nTot + " ; en moyenne, une proportion 1/|det A| = 1/" + Math.abs(D) + " des b entiers.";
      } else {
        good = inImage(b);
        txt += " : A n'est pas inversible.\nLes colonnes sont alignées : A ℤ² tient sur une droite, et Ax = b n'a de solution que pour b sur cette droite. b = " + p6ipt(b) + (good ? " est atteint (par une infinité de x)." : " n'est pas atteint.");
      }
      el("circle", { cx: plot.tx(b[0]), cy: plot.ty(b[1]), r: 9, "class": "ln nofill " + (good ? "c3" : "c6"), style: "stroke-width:2.6px" }, plot.g);
      plot.text(b[0], b[1], "b", "tx-b", "start", 10, -8);
      txt += "\n(Cliquez un point du quadrillage pour changer b.)";
      ro.textContent = txt;
    }
    draw(); redrawers.push(draw);
  };

  /* --- 3. Totalement unimodulaire ? (§5–§6) --- */
  WIDGETS.p6tu = function (box) {
    var s = scaffold(box, "Totalement unimodulaire ? Toutes les sous-matrices carrées et leurs déterminants");
    var W = 680, H = 330;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Matrice modifiable, critère de Poincaré par colonne et sous-matrice témoin");
    var PRE = {
      inc: { rows: ["n₁", "n₂", "n₃", "n₄"], M: [[1, 1, 0, 0, 0], [-1, 0, 1, 1, 0], [0, -1, -1, 0, 1], [0, 0, 0, -1, -1]] },
      centre: { rows: ["f₁", "f₂", "f₃", "f₄", "f₅"], M: [[1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1]] },
      haut: { rows: ["1", "2", "3", "4"], M: [[1, 1, 1, 1, 0], [1, 1, 0, 1, 0], [1, 0, 0, 1, 0], [0, 0, 0, 1, 0]] },
      unimod: { rows: ["1", "2", "3"], M: [[1, 1, 0], [-1, 1, 1], [0, 1, 1]] },
      triangle: { rows: ["1", "2", "3"], M: [[1, 1, 0], [0, 1, 1], [1, 0, 1]] },
      affect: { rows: ["p₁", "p₂", "t₁", "t₂"], M: [[1, 1, 0, 0], [0, 0, 1, 1], [1, 0, 1, 0], [0, 1, 0, 1]] },
      cyc: { rows: ["f₁", "f₂", "f₃", "f₄", "f₅"], M: [[1, 0, 0, 0, 1], [1, 1, 0, 0, 0], [0, 1, 1, 0, 0], [0, 0, 1, 1, 0], [0, 0, 0, 1, 1]] }
    };
    var M, rows;
    var pre = select(s.controls, "Matrice", [["inc", "incidence d'un graphe orienté"], ["centre", "centre d'appels ᵗU"], ["haut", "intervalles « du haut »"], ["unimod", "unimodulaire non TU"], ["triangle", "triangle non orienté"], ["affect", "affectation 2 × 2"], ["cyc", "planning cyclique"]], "inc", load);
    button(s.controls, "Recharger", load);
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "colonne qui vérifie Poincaré"], ["--s6", "colonne qui ne le vérifie pas"], ["--s2", "sous-matrice témoin (det ∉ {0, ±1})"]]);
    function load() { var p = PRE[pre.value]; M = p.M.map(function (r) { return r.slice(); }); rows = p.rows.slice(); draw(); }
    var cell = 40, X0 = 104, Y0 = 46;
    s.svg.addEventListener("click", function (e) {
      var p = svgPoint(s.svg, e), m = M.length, n = M[0].length;
      var j = Math.floor((p.x - X0) / cell), i = Math.floor((p.y - Y0) / cell);
      if (i >= 0 && i < m && j >= 0 && j < n) { var v = M[i][j]; M[i][j] = v === 0 ? 1 : v === 1 ? -1 : v === -1 ? 2 : 0; draw(); }
      else if (i >= 0 && i < m && p.x >= X0 - 48 && p.x < X0) { M[i] = M[i].map(function (v) { return -v; }); draw(); }
    });
    function draw() {
      var m = M.length, n = M[0].length, k, i, j;
      // toutes les sous-matrices carrées
      var stats = [], witness = null, total = 0;
      for (k = 1; k <= Math.min(m, n); k++) {
        var st = { k: k, n: 0, zero: 0, one: 0, other: 0 };
        var R = combinations(m, k), C = combinations(n, k);
        R.forEach(function (r) {
          C.forEach(function (c) {
            var sub = r.map(function (ii) { return c.map(function (jj) { return M[ii][jj]; }); });
            var d = frDet(sub), v = d.val();
            st.n++; total++;
            if (d.isZero()) st.zero++; else if (Math.abs(v) === 1) st.one++; else { st.other++; if (!witness) witness = { r: r, c: c, d: d, sub: sub }; }
          });
        });
        stats.push(st);
      }
      // critère de Poincaré et 1 consécutifs, colonne par colonne
      var poin = [], interval = [];
      for (j = 0; j < n; j++) {
        var plus = 0, minus = 0, bad = false, ones = [];
        for (i = 0; i < m; i++) { var v = M[i][j]; if (v === 1) { plus++; ones.push(i); } else if (v === -1) minus++; else if (v !== 0) bad = true; }
        poin.push(!bad && plus <= 1 && minus <= 1);
        interval.push(!bad && minus === 0 && (ones.length === 0 || ones[ones.length - 1] - ones[0] === ones.length - 1));
      }
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg);
      // matrice
      for (i = 0; i < m; i++) for (j = 0; j < n; j++) {
        var hl = witness && witness.r.indexOf(i) >= 0 && witness.c.indexOf(j) >= 0;
        el("rect", { x: X0 + j * cell + 1, y: Y0 + i * cell + 1, width: cell - 2, height: cell - 2, rx: 5, "class": hl ? "a2" : "am", style: "cursor:pointer" }, g);
        var t = el("text", { x: X0 + j * cell + cell / 2, y: Y0 + i * cell + cell / 2 + 5, "class": M[i][j] === 0 ? "tx" : "tx-b", "text-anchor": "middle", style: "pointer-events:none" }, g);
        t.textContent = String(M[i][j]).replace("-", "−");
      }
      for (i = 0; i < m; i++) {
        var rl = el("text", { x: X0 - 10, y: Y0 + i * cell + cell / 2 + 5, "class": "tx-s", "text-anchor": "end", style: "cursor:pointer" }, g);
        rl.textContent = rows[i] + "  ±";
      }
      for (j = 0; j < n; j++) {
        var cx = X0 + j * cell + cell / 2, yb = Y0 + m * cell;
        var t1 = el("text", { x: cx, y: yb + 18, "class": "tx-b " + (poin[j] ? "t3" : "t6"), "text-anchor": "middle" }, g); t1.textContent = poin[j] ? "✓" : "✗";
        var t2 = el("text", { x: cx, y: yb + 36, "class": "tx-b " + (interval[j] ? "t3" : "t6"), "text-anchor": "middle" }, g); t2.textContent = interval[j] ? "✓" : "✗";
        var t0 = el("text", { x: cx, y: Y0 - 10, "class": "tx-s", "text-anchor": "middle" }, g); t0.textContent = "c" + (j + 1);
      }
      var yb2 = Y0 + m * cell;
      [["Poincaré", 18], ["1 consécutifs", 36]].forEach(function (r) { var t = el("text", { x: X0 - 10, y: yb2 + r[1], "class": "tx-s", "text-anchor": "end" }, g); t.textContent = r[0]; });
      // tableau des déterminants
      var TX = X0 + n * cell + 40;
      [["taille", 0], ["nombre", 62], ["det 0", 132], ["det ±1", 186], ["autres", 248]].forEach(function (c) {
        var hd = el("text", { x: TX + c[1], y: 40, "class": "tx-b" }, g); hd.textContent = c[0];
      });
      stats.forEach(function (st, r) {
        var y = 64 + r * 22;
        [[st.k + " × " + st.k, 0], [String(st.n), 62], [String(st.zero), 132], [String(st.one), 186], [String(st.other), 248]].forEach(function (c) {
          var t = el("text", { x: TX + c[1], y: y, "class": c[1] === 248 && st.other ? "tx-b t6" : "tx" }, g); t.textContent = c[0];
        });
      });
      var yv = 64 + stats.length * 22 + 10;
      s.svg.setAttribute("viewBox", "0 0 " + W + " " + Math.max(Y0 + m * cell + 52, yv + 40));
      var verdict = el("text", { x: TX, y: yv, "class": "tx-b " + (witness ? "t6" : "t3") }, g);
      verdict.textContent = witness ? "pas totalement unimodulaire" : "totalement unimodulaire";
      if (witness) {
        var wt = el("text", { x: TX, y: yv + 22, "class": "tx-s" }, g);
        wt.textContent = "témoin : lignes " + witness.r.map(function (r) { return rows[r]; }).join(", ") + " ; colonnes " + witness.c.map(function (c) { return "c" + (c + 1); }).join(", ") + " ; det = " + witness.d.str();
      }
      // texte
      var allP = poin.every(Boolean), allI = interval.every(Boolean);
      var txt = "Matrice " + m + " × " + n + " : " + total + " sous-matrices carrées (= C(" + (m + n) + ", " + m + ") − 1), toutes calculées en fractions exactes.\n";
      txt += witness ? "Pas TU : la sous-matrice (" + witness.sub.map(function (r) { return r.join(" "); }).join(" ; ").replace(/-/g, "−") + ") a pour déterminant " + witness.d.str() + ".\n"
        : "Totalement unimodulaire : tous les déterminants valent 0, 1 ou −1.\n";
      txt += "Critère de Poincaré (des 0, ±1, au plus un +1 et au plus un −1 par colonne) : " + (allP ? "vérifié." : "non vérifié (colonnes " + poin.map(function (p, j) { return p ? null : "c" + (j + 1); }).filter(Boolean).join(", ") + ").");
      txt += "\nMatrice d'intervalles (des 1 consécutifs dans chaque colonne) : " + (allI ? "oui." : "non.");
      if (!witness && !allP && !allI) txt += "\nTU sans vérifier aucun des deux critères : ils sont suffisants, pas nécessaires.";
      txt += "\nCliquez un coefficient : 0 → 1 → −1 → 2 → 0. Cliquez une étiquette de ligne (±) : la ligne est multipliée par −1.";
      ro.textContent = txt;
    }
    load(); redrawers.push(draw);
  };

  /* --- 4. Le centre d'appels en nombres entiers (§7) --- */
  WIDGETS.p6centre = function (box) {
    var s = scaffold(box, "Centre d'appels : toutes les solutions basiques du relaxé, et l'optimum entier");
    var W = 680, H = 400;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Tranches horaires, effectifs optimaux et couverture de la demande");
    var mode = select(s.controls, "Tranches", [["diapo", "diapo 15 : 3 tranches (intervalles)"], ["cyc", "24 h/24 : 5 tranches, cyclique"]], "diapo", function () { defaults(); draw(); });
    var sc = [1, 2, 3, 4, 5].map(function (j) { return slider(s.controls, "c" + "₁₂₃₄₅"[j - 1], 0, 15, 1, 0, draw); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "tranches (effectif optimal du relaxé)"], ["--s3", "nombre d'opérateurs présents"], ["--s2", "demande c"]]);
    function defaults() {
      var d = mode.value === "diapo" ? [5, 10, 6, 12, 4] : [3, 3, 3, 3, 3];
      sc.forEach(function (t, i) { t.set(d[i]); });
    }
    function setup() {
      if (mode.value === "diapo") return { M: [[1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1]], S: [4, 5, 6] };
      var M = [];
      for (var i = 0; i < 5; i++) { M.push([]); for (var j = 0; j < 5; j++) M[i].push(i === j || i === (j + 1) % 5 ? 1 : 0); }
      return { M: M, S: [1, 1, 1, 1, 1] };
    }
    function draw() {
      var c = sc.map(function (t) { return Math.round(t.get()); });
      sc.forEach(function (t, i) { t.out.textContent = String(c[i]); });
      var U = setup(), M = U.M, S = U.S, k = S.length, i, j;
      // forme standard [M, −I] (x, s) = c
      var A = M.map(function (r, ii) { return r.concat([0, 1, 2, 3, 4].map(function (jj) { return ii === jj ? -1 : 0; })); });
      var combos = combinations(k + 5, 5), nSing = 0, nInt = 0, nAdm = 0, nFrac = 0, nFracAdm = 0, best = null;
      combos.forEach(function (cols) {
        var r = basicSolution(A, c, cols);
        if (!r.x) { nSing++; return; }
        var integ = r.x.every(function (v) { return v.d === 1; });
        if (integ) nInt++; else nFrac++;
        if (r.status === "admissible" || r.status === "dégénérée") {
          nAdm++; if (!integ) nFracAdm++;
          var cost = Fr(0); for (var q = 0; q < k; q++) cost = cost.add(r.x[q].mul(S[q]));
          if (!best || cost.cmp(best.cost) < 0) best = { x: r.x.slice(0, k), cost: cost };
        }
      });
      // optimum entier par énumération (la dernière variable prend sa plus petite valeur admissible)
      var cmax = Math.max.apply(null, c), ib = Infinity, ix = null, cur = [];
      (function rec(q) {
        if (q === k - 1) {
          var need = 0, ok = true;
          for (var r = 0; r < 5; r++) {
            var part = 0; for (var t = 0; t < k - 1; t++) part += M[r][t] * cur[t];
            if (M[r][k - 1]) need = Math.max(need, c[r] - part); else if (part < c[r]) { ok = false; break; }
          }
          if (!ok) return;
          var cost = need * S[k - 1]; for (var t2 = 0; t2 < k - 1; t2++) cost += S[t2] * cur[t2];
          if (cost < ib) { ib = cost; ix = cur.concat([need]); }
          return;
        }
        for (var v = 0; v <= cmax; v++) { cur[q] = v; rec(q + 1); }
      })(0);
      // dessin
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg);
      var L = 70, R = 640, fw = (R - L) / 5;
      var bounds = mode.value === "diapo" ? [0, 5, 9, 13, 18, 24] : [0, 4.8, 9.6, 14.4, 19.2, 24];
      function X(t) { return L + t / 24 * (R - L); }
      var ytl = 34 + k * 30 + 18;
      el("line", { x1: X(0), y1: ytl, x2: X(24), y2: ytl, "class": "ax" }, g);
      for (j = 0; j <= 5; j++) {
        el("line", { x1: X(bounds[j]), y1: 22, x2: X(bounds[j]), y2: H - 26, "class": "gr" }, g);
        if (j < 5) { var tl = el("text", { x: (X(bounds[j]) + X(bounds[j + 1])) / 2, y: ytl + 18, "class": "tx-b", "text-anchor": "middle" }, g); tl.textContent = "f" + "₁₂₃₄₅"[j]; }
      }
      var t0 = el("text", { x: X(0), y: ytl + 34, "class": "tx-s", "text-anchor": "middle" }, g); t0.textContent = "0 h";
      var t24 = el("text", { x: X(24), y: ytl + 34, "class": "tx-s", "text-anchor": "middle" }, g); t24.textContent = "24 h";
      for (i = 0; i < k; i++) {
        var fr = []; for (j = 0; j < 5; j++) if (M[j][i]) fr.push(j);
        var y = 26 + i * 30;
        var pieces = [];
        if (fr.length === 2 && fr[1] - fr[0] > 1) pieces = [[fr[1], fr[1]], [fr[0], fr[0]]]; else pieces = [[fr[0], fr[fr.length - 1]]];
        pieces.forEach(function (pc, pi) {
          var x1 = X(bounds[pc[0]]) + 2, x2 = X(bounds[pc[1] + 1]) - 2;
          el("rect", { x: x1, y: y, width: x2 - x1, height: 22, rx: 4, "class": "a1" }, g);
          el("rect", { x: x1, y: y, width: x2 - x1, height: 22, rx: 4, "class": "ln c1 thin nofill" }, g);
          var xv = best ? best.x[i] : null, xcls = "tx-b " + (xv && xv.d !== 1 ? "t6" : "t3");
          var xs = xv ? "x" + "₁₂₃₄₅"[i] + " = " + xv.str() : "";
          if (pieces.length > 1) {
            var tt = el("text", { x: x1 + 6, y: y + 15, "class": pi === 0 ? "tx-s" : xcls }, g);
            tt.textContent = pi === 0 ? "tranche " + (i + 1) + " · nuit" : "↻ " + xs;
          } else {
            var lab = el("text", { x: x1 + 6, y: y + 15, "class": "tx-s" }, g);
            lab.textContent = "tranche " + (i + 1) + (mode.value === "diapo" ? " · salaire " + S[i] : "");
            var vt = el("text", { x: x2 - 6, y: y + 15, "class": xcls, "text-anchor": "end" }, g);
            vt.textContent = xs;
          }
        });
      }
      // couverture et demande
      var y0 = H - 30, top = ytl + 66, cm = Math.max(cmax, 1) * 1.3, sy = (y0 - top) / cm;
      el("line", { x1: L, y1: y0, x2: R, y2: y0, "class": "ax" }, g);
      for (j = 0; j < 5; j++) {
        var cov = Fr(0); for (i = 0; i < k; i++) if (M[j][i] && best) cov = cov.add(best.x[i]);
        var xm = (X(bounds[j]) + X(bounds[j + 1])) / 2, bw = Math.min(46, (X(bounds[j + 1]) - X(bounds[j])) * 0.5);
        el("rect", { x: xm - bw / 2, y: y0 - cov.val() * sy, width: bw, height: cov.val() * sy, "class": "a3" }, g);
        el("rect", { x: xm - bw / 2, y: y0 - cov.val() * sy, width: bw, height: cov.val() * sy, "class": "ln c3 thin nofill" }, g);
        el("line", { x1: xm - bw / 2 - 8, y1: y0 - c[j] * sy, x2: xm + bw / 2 + 8, y2: y0 - c[j] * sy, "class": "ln c2" }, g);
        var ytop = y0 - Math.max(cov.val(), c[j]) * sy;
        var tc = el("text", { x: xm, y: ytop - 22, "class": "tx-s t3", "text-anchor": "middle" }, g);
        tc.textContent = "présents " + cov.str();
        var td = el("text", { x: xm, y: ytop - 8, "class": "tx-s t2", "text-anchor": "middle" }, g);
        td.textContent = "demande " + c[j];
      }
      // texte
      var txt = "Relaxé : min S·x sous ᵗU x ≥ c, x ≥ 0, mis sous forme standard [ᵗU, −I](x, s) = c : " + combos.length + " choix de 5 colonnes, tous examinés.\n";
      txt += "Solutions basiques (base inversible) : " + (combos.length - nSing) + " ; entières : " + nInt + " ; fractionnaires : " + nFrac + " ; admissibles : " + nAdm + (nFracAdm ? " (dont " + nFracAdm + " fractionnaire)" : "") + ".\n";
      txt += "Optimum du relaxé (le sommet que rend le simplexe) : x = (" + best.x.map(function (v) { return v.str(); }).join(", ") + "), coût " + best.cost.str() + ".\n";
      txt += "Optimum entier (énumération) : x = (" + ix.join(", ") + "), coût " + ib + (best.cost.cmp(Fr(ib)) === 0 ? " : égal au relaxé." : " > " + best.cost.str() + " : écart de relaxation " + Fr(ib).sub(best.cost).str() + ".");
      txt += mode.value === "diapo" ? "\nᵗU a des 1 consécutifs dans chaque colonne : elle est TU, et toutes les solutions basiques sont entières, quelle que soit la demande." :
        "\nSalaires tous égaux à 1. La tranche de nuit couvre f₅ et f₁ (à cheval sur minuit) : la matrice 5 × 5 a pour déterminant 2, elle n'est pas TU.";
      ro.textContent = txt;
    }
    defaults(); draw(); redrawers.push(draw);
  };
