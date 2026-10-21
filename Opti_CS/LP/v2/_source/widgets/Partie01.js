// widgets/Partie01.js — figures interactives de la partie 1 (modéliser, forme standard, géométrie, existence).
// Inséré par build.mjs dans la portée de app.js : utilise el, fmt, frac, Plot, scaffold, slider, select, button,
// checkbox, readout, legend, svgPoint, arrowMarker, halfPlanePolygon, lineInBox, et enregistre ses widgets dans WIDGETS.

  /* --- petits outils de la partie 1 --- */
  // Nombre en français (virgule décimale) ; entiers et fractions simples écrits exactement.
  function p1num(x, d) {
    if (!isFinite(x)) return fmt(x, d);
    var f = frac(x);
    if (f.indexOf("/") >= 0 && f.length <= 5) return f;
    if (Math.abs(x - Math.round(x)) < 1e-9) return String(Math.round(x)).replace("-", "−");
    return fmt(x, d === undefined ? 2 : d).replace(".", ",").replace("-", "−");
  }
  function p1pt(p, d) {
    var a = p1num(p[0], d), b = p1num(p[1], d);
    return (a.indexOf(",") >= 0 || b.indexOf(",") >= 0) ? "(" + a + " ; " + b + ")" : "(" + a + ", " + b + ")";
  }
  function p1dot(u, v) { var s = 0; for (var i = 0; i < u.length; i++) s += u[i] * v[i]; return s; }

  // Le polygone de l'Exercice 4.2.1 : contraintes a·x ≤ r, sommets dans l'ordre trigonométrique.
  var P1_CONS = [[-3, 2, 2, "(1)"], [-1, 2, 4, "(2)"], [1, 1, 5, "(3)"]];
  var P1_V5 = [[0, 0], [5, 0], [2, 3], [1, 2.5], [0, 1]];
  var P1_E5 = [[0, 1, [0, -1], "x₂ = 0"], [1, 2, [1, 1], "(3)"], [2, 3, [-1, 2], "(2)"], [3, 4, [-3, 2], "(1)"], [4, 0, [-1, 0], "x₁ = 0"]];
  var P1_V3 = [[0, 0], [1, 2.5], [0, 1]];
  var P1_E3 = [[1, 2, [-3, 2], "(1)"], [2, 0, [-1, 0], "x₁ = 0"]];
  var P1_R3 = [{ from: 0, dir: [1, 0], normal: [0, -1], name: "x₂ = 0" }, { from: 1, dir: [2, 1], normal: [-1, 2], name: "(2)" }];
  // Position des étiquettes de sommets (décalages en pixels).
  var P1_LAB = { "0,0": [6, 16, "start"], "5,0": [8, -8, "start"], "2,3": [24, 4, "start"], "1,2.5": [-10, -6, "end"], "0,1": [9, 4, "start"] };

  function p1drawConstraints(pl, box, withThird) {
    P1_CONS.forEach(function (h, k) {
      if (k === 2 && !withThird) return;
      var seg = lineInBox(h[0], h[1], h[2], box);
      if (!seg) return;
      pl.seg(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln cm thin");
      var top = seg[0][1] > seg[1][1] ? seg[0] : seg[1];
      if (k === 2) top = seg[0][1] < seg[1][1] ? seg[0] : seg[1];
      pl.text(top[0], top[1], h[3], "tx-s", k === 2 ? "start" : "end", k === 2 ? 6 : -6, k === 2 ? -6 : 14);
    });
  }

  /* --- 1. Faire tourner la direction de coût (méthode graphique, §3) --- */
  WIDGETS.p1direction = function (box) {
    var s = scaffold(box, "Faire tourner la direction de coût c : où la ligne de niveau quitte-t-elle le polygone ?");
    var BOX = [-0.6, 6.6, -0.6, 4.8];
    var pl = new Plot(s.svg, { x: [BOX[0], BOX[1]], y: [BOX[2], BOX[3]], w: 640, h: 500, pad: { l: 40, r: 16, t: 20, b: 42 }, label: "Polygone de l'exercice 4.2.1, lignes de niveau de c·x et optimum" });
    var PRESETS = [["12", "(1, 2) : Ex. 4.2.1", [1, 2]], ["11", "(1, 1) : ⟂ à l'arête (3)", [1, 1]], ["m12", "(−1, 2) : ⟂ à l'arête (2)", [-1, 2]],
      ["m32", "(−3, 2) : ⟂ à l'arête (1)", [-3, 2]], ["2m1", "(2, −1)", [2, -1]], ["m1m1", "(−1, −1)", [-1, -1]], ["free", "libre (curseur)", null]];
    var preset = select(s.controls, "c =", PRESETS.map(function (p) { return [p[0], p[1]]; }), "12", function () { fromPreset(); draw(); });
    var th = slider(s.controls, "angle de c (°)", 0, 360, 0.5, 63.5, function () { preset.value = "free"; fromSlider(); draw(); });
    var third = checkbox(s.controls, "contrainte (3) x₁ + x₂ ≤ 5", true, function () { fromSlider(true); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "Xad"], ["--s2", "lignes de niveau c·x = constante, et c"], ["--s3", "ensemble des solutions optimales"]]);
    var c = [1, 2], snapName = "";

    function snaps() {
      var list = third.checked ? P1_E5.map(function (e) { return [e[2], e[3]]; }) : P1_E3.map(function (e) { return [e[2], e[3]]; }).concat(P1_R3.map(function (r) { return [r.normal, r.name]; }));
      return list;
    }
    function fromPreset() {
      var p = PRESETS.filter(function (q) { return q[0] === preset.value; })[0];
      if (!p || !p[2]) { fromSlider(); return; }
      c = p[2].slice(); snapName = "";
      var a = Math.atan2(c[1], c[0]) * 180 / Math.PI; if (a < 0) a += 360;
      th.set(a);
    }
    function fromSlider(keepPreset) {
      if (keepPreset && preset.value !== "free") { fromPreset(); return; }
      var a = th.get(), best = null;
      snapName = "";
      snaps().forEach(function (sn) {
        var b = Math.atan2(sn[0][1], sn[0][0]) * 180 / Math.PI; if (b < 0) b += 360;
        var d = Math.abs(((a - b + 540) % 360) - 180);
        if (d < 0.8 && (!best || d < best.d)) best = { d: d, n: sn[0], name: sn[1] };
      });
      if (best) { var L = Math.hypot(best.n[0], best.n[1]); c = [best.n[0] / L, best.n[1] / L]; snapName = best.name; }
      else c = [Math.cos(a * Math.PI / 180), Math.sin(a * Math.PI / 180)];
    }

    function draw() {
      var withThird = third.checked;
      var V = withThird ? P1_V5 : P1_V3;
      var vals = V.map(function (v) { return p1dot(c, v); });
      var M = Math.max.apply(null, vals), tol = 1e-9 * (1 + Math.abs(M));
      var opt = []; vals.forEach(function (v, i) { if (v >= M - tol) opt.push(i); });
      var unb = null, optRays = [];
      if (!withThird) {
        var best = 1e-9;
        P1_R3.forEach(function (r) {
          var d = p1dot(c, r.dir), dn = d / Math.hypot(r.dir[0], r.dir[1]);
          if (dn > best) { best = dn; unb = r; }   // la demi-droite où c·x monte le plus vite
          else if (Math.abs(d) <= 1e-9 && opt.indexOf(r.from) >= 0) optRays.push(r);
        });
        if (unb) optRays = [];
      }
      pl.clear();
      pl.axes({ xticks: [0, 1, 2, 3, 4, 5, 6], yticks: [0, 1, 2, 3, 4], cross: true, xlabel: "x₁", ylabel: "x₂" });
      var cons = P1_CONS.filter(function (h, k) { return withThird || k !== 2; }).map(function (h) { return [h[0], h[1], h[2]]; }).concat([[-1, 0, 0], [0, -1, 0]]);
      var P = halfPlanePolygon(cons, BOX);
      pl.poly(P.concat([P[0]]), "a1");
      p1drawConstraints(pl, BOX, withThird);
      // bord de Xad
      pl.clip();
      if (withThird) pl.poly(P1_V5.concat([P1_V5[0]]), "ln c1");
      else {
        pl.poly([[0, 0]].concat([[0, 1], [1, 2.5]]), "ln c1");
        P1_R3.forEach(function (r) { var o = P1_V3[r.from]; pl.seg(o[0], o[1], o[0] + 9 * r.dir[0], o[1] + 9 * r.dir[1], "ln c1"); });
      }
      // lignes de niveau
      var corners = [[BOX[0], BOX[2]], [BOX[1], BOX[2]], [BOX[1], BOX[3]], [BOX[0], BOX[3]]].map(function (p) { return p1dot(c, p); });
      var kmin = Math.min.apply(null, corners), kmax = Math.max.apply(null, corners), D = (kmax - kmin) / 9;
      for (var j = 1; j < 9; j++) {
        var seg = lineInBox(c[0], c[1], kmin + j * D, BOX);
        if (seg) pl.seg(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln c2 thin dash", { "stroke-opacity": 0.55 });
      }
      if (!unb) {
        var so = lineInBox(c[0], c[1], M, BOX);
        if (so) pl.seg(so[0][0], so[0][1], so[1][0], so[1][1], "ln c2");
      }
      // ensemble optimal
      if (!unb) {
        if (opt.length === 2) pl.seg(V[opt[0]][0], V[opt[0]][1], V[opt[1]][0], V[opt[1]][1], "ln c3", { style: "stroke-width:7px", "stroke-opacity": 0.75 });
        optRays.forEach(function (r) { var o = V[r.from]; pl.seg(o[0], o[1], o[0] + 9 * r.dir[0], o[1] + 9 * r.dir[1], "ln c3", { style: "stroke-width:7px", "stroke-opacity": 0.75 }); });
      }
      pl.unclip();
      // flèche c
      var mk = arrowMarker(s.svg, "f2");
      var base;
      if (unb) base = [2.2, 1.2];
      else if (opt.length === 2) base = [(V[opt[0]][0] + V[opt[1]][0]) / 2, (V[opt[0]][1] + V[opt[1]][1]) / 2];
      else base = V[opt[0]];
      var cu = Math.hypot(c[0], c[1]), tip = [base[0] + 0.85 * c[0] / cu, base[1] + 0.85 * c[1] / cu];
      pl.seg(base[0], base[1], tip[0], tip[1], "ln c2", { "marker-end": mk });
      pl.text(tip[0], tip[1], "c", "tx-b t2", "start", 6, -4);
      if (unb) {
        // flèche le long de la demi-droite qui fait monter c·x, décalée vers l'intérieur de Xad
        var o = V[unb.from], kEnd = unb.dir[1] === 0 ? 5.6 : 2.0, off = unb.dir[1] === 0 ? 0.3 : -0.3;
        var a0 = [o[0] + 0.5 * unb.dir[0], o[1] + 0.5 * unb.dir[1] + off], a1 = [o[0] + kEnd * unb.dir[0], o[1] + kEnd * unb.dir[1] + off];
        var mk6 = arrowMarker(s.svg, "f6");
        pl.seg(a0[0], a0[1], a1[0], a1[1], "ln c6", { "marker-end": mk6 });
        pl.text(a1[0], a1[1], "c·x → +∞", "tx-b t6", "start", 10, 5);
      }
      // sommets
      V.forEach(function (v, i) {
        var isOpt = !unb && opt.indexOf(i) >= 0;
        pl.dot(v[0], v[1], isOpt ? 7 : 4.5, isOpt ? "f3" : "f1");
        var L = P1_LAB[v[0] + "," + v[1]] || [6, -6, "start"];
        pl.text(v[0], v[1], p1pt(v) + " → " + p1num(vals[i]), isOpt ? "tx-b t3" : "tx-s", L[2], L[0], L[1]);
      });
      // texte
      var ang = Math.atan2(c[1], c[0]) * 180 / Math.PI; if (ang < 0) ang += 360;
      var txt = "On maximise c·x avec c = " + p1pt(c, 3) + " (angle " + fmt(ang, 1).replace(".", ",") + "°)" + (snapName ? ", c perpendiculaire à l'arête " + snapName : "") + ".";
      txt += "\nValeurs de c·x aux sommets : " + V.map(function (v, i) { return p1pt(v) + " → " + p1num(vals[i]); }).join(" ; ");
      if (unb) txt += "\nNON BORNÉ : le long de la demi-droite issue de " + p1pt(V[unb.from]) + " dans la direction " + p1pt(unb.dir) + ", c·x augmente sans fin (c·" + p1pt(unb.dir) + " = " + p1num(p1dot(c, unb.dir)) + " > 0). Valeur +∞, aucune solution optimale.";
      else if (optRays.length) txt += "\nOptimum " + p1num(M) + " atteint sur toute une demi-droite issue de " + p1pt(V[optRays[0].from]) + " (c est perpendiculaire à sa direction " + p1pt(optRays[0].dir) + ") : une infinité de solutions optimales, dont un sommet.";
      else if (opt.length === 2) txt += "\nOptimum " + p1num(M) + " atteint sur toute l'arête " + p1pt(V[opt[0]]) + " — " + p1pt(V[opt[1]]) + " : une infinité de solutions optimales, dont deux sommets.";
      else txt += "\nOptimum " + p1num(M) + " atteint en un seul point, le sommet " + p1pt(V[opt[0]]) + ".";
      ro.textContent = txt;
    }
    fromPreset(); draw(); redrawers.push(draw);
  };

  /* --- 2. Les variables d'écart d'un point qu'on déplace (§3) --- */
  WIDGETS.p1ecarts = function (box) {
    var s = scaffold(box, "Déplacez le point x : ses variables d'écart sont ≥ 0 exactement dans le polygone");
    var BOX = [-0.6, 6.6, -0.6, 4.8];
    var pl = new Plot(s.svg, { x: [BOX[0], BOX[1]], y: [BOX[2], BOX[3]], w: 640, h: 500, pad: { l: 40, r: 16, t: 20, b: 42 }, label: "Un point x, ses distances signées aux droites des contraintes et ses variables d'écart" });
    var x = [1.5, 1], dragging = false;
    button(s.controls, "sommet (2, 3)", function () { x = [2, 3]; draw(); });
    button(s.controls, "sommet (1, 5/2)", function () { x = [1, 2.5]; draw(); });
    button(s.controls, "point (4, 3)", function () { x = [4, 3]; draw(); });
    button(s.controls, "point (2, 1)", function () { x = [2, 1]; draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "Xad"], ["--s3", "écart ≥ 0 (bon côté)"], ["--s6", "écart < 0 (contrainte violée)"]]);

    function setFromEvent(e) {
      var p = svgPoint(s.svg, e), u = pl.ix(p.x), v = pl.iy(p.y);
      u = Math.min(Math.max(u, BOX[0] + 0.05), BOX[1] - 0.05); v = Math.min(Math.max(v, BOX[2] + 0.05), BOX[3] - 0.05);
      var near = null;
      P1_V5.concat([[2, 1], [4, 3]]).forEach(function (q) { if (Math.hypot(q[0] - u, q[1] - v) < 0.14) near = q; });
      x = near ? near.slice() : [Math.round(u * 20) / 20, Math.round(v * 20) / 20];
      draw();
    }
    s.svg.addEventListener("pointerdown", function (e) { dragging = true; try { s.svg.setPointerCapture(e.pointerId); } catch (err) {} setFromEvent(e); });
    s.svg.addEventListener("pointermove", function (e) { if (dragging) setFromEvent(e); });
    s.svg.addEventListener("pointerup", function () { dragging = false; });
    s.svg.addEventListener("pointercancel", function () { dragging = false; });

    function draw() {
      pl.clear();
      pl.axes({ xticks: [0, 1, 2, 3, 4, 5, 6], yticks: [0, 1, 2, 3, 4], cross: true, xlabel: "x₁", ylabel: "x₂" });
      var P = halfPlanePolygon(P1_CONS.map(function (h) { return [h[0], h[1], h[2]]; }).concat([[-1, 0, 0], [0, -1, 0]]), BOX);
      pl.poly(P.concat([P[0]]), "a1");
      pl.poly(P1_V5.concat([P1_V5[0]]), "ln c1 thin");
      p1drawConstraints(pl, BOX, true);
      var sl = P1_CONS.map(function (h) { return h[2] - h[0] * x[0] - h[1] * x[1]; });
      var z = [x[0], x[1]].concat(sl);
      var names = ["x₁", "x₂", "s₁", "s₂", "s₃"];
      // directions (degrés) des cinq segments issus de x : vers les trois droites, puis vers les deux axes
      var dirs = P1_CONS.map(function (h, k) { var d = Math.atan2(h[1], h[0]) * 180 / Math.PI; return sl[k] >= 0 ? d : d + 180; })
        .concat([x[0] >= 0 ? 180 : 0, x[1] >= 0 ? 270 : 90]).map(function (d) { return ((d % 360) + 360) % 360; });
      // segments vers les droites : pied de la perpendiculaire x + s a / |a|²
      P1_CONS.forEach(function (h, k) {
        var a2 = h[0] * h[0] + h[1] * h[1], f = [x[0] + sl[k] * h[0] / a2, x[1] + sl[k] * h[1] / a2];
        var cls = sl[k] >= -1e-12 ? "ln c3" : "ln c6";
        pl.seg(x[0], x[1], f[0], f[1], cls, { style: "stroke-width:2.6px" });
        pl.dot(f[0], f[1], 3, sl[k] >= -1e-12 ? "f3" : "f6");
        // étiquette au milieu du segment, décalée du côté où l'angle libre jusqu'au segment voisin est le plus grand
        var ccw = 360, cw = 360;
        dirs.forEach(function (d, j) { if (j === k) return; ccw = Math.min(ccw, (d - dirs[k] + 360) % 360); cw = Math.min(cw, (dirs[k] - d + 360) % 360); });
        var phi = (dirs[k] + (ccw > cw ? 90 : -90)) * Math.PI / 180, ox = Math.cos(phi), oy = Math.sin(phi);
        var m = [(x[0] + f[0]) / 2, (x[1] + f[1]) / 2];
        var Lpx = Math.hypot(pl.tx(f[0]) - pl.tx(x[0]), pl.ty(f[1]) - pl.ty(x[1]));
        if (Lpx > 1 && Lpx < 70) {   // segment court (x près d'un sommet) : étiquette au-delà du pied, dans le prolongement
          var th = dirs[k] * Math.PI / 180; ox = Math.cos(th); oy = Math.sin(th); m = f;
        }
        var anchor = ox > 0.3 ? "start" : ox < -0.3 ? "end" : "middle";
        var off = Lpx <= 1 ? 17 : 9;   // x sur la droite : on s'écarte du disque du point
        pl.text(m[0], m[1], names[2 + k] + " = " + p1num(sl[k]), "tx-s " + (sl[k] >= -1e-12 ? "t3" : "t6"), anchor, off * ox, -off * oy + 4 + (oy < -0.3 ? 4 : 0));
      });
      pl.seg(x[0], x[1], 0, x[1], x[0] >= 0 ? "ln c3 thin dash" : "ln c6 thin dash");
      pl.seg(x[0], x[1], x[0], 0, x[1] >= 0 ? "ln c3 thin dash" : "ln c6 thin dash");
      var ok = z.every(function (v) { return v >= -1e-12; });
      pl.dot(x[0], x[1], 13, ok ? "a1" : "a5");
      pl.dot(x[0], x[1], 9, (ok ? "f1" : "f6") + " drag");
      pl.text(x[0], x[1], "x", "on-fill", "middle", 0, 4);   // le nom du point, dans le disque (aucune collision avec les étiquettes)
      var zeros = z.filter(function (v) { return Math.abs(v) < 1e-12; }).length;
      var txt = "x = " + p1pt(x) + "      coût x₁ + 2x₂ = " + p1num(x[0] + 2 * x[1]);
      txt += "\ns₁ = 2 + 3x₁ − 2x₂ = " + p1num(sl[0]) + "    s₂ = 4 + x₁ − 2x₂ = " + p1num(sl[1]) + "    s₃ = 5 − x₁ − x₂ = " + p1num(sl[2]);
      txt += "\nz = (x₁, x₂, s₁, s₂, s₃) = (" + z.map(function (v) { return p1num(v); }).join(" ; ") + ") vérifie toujours Az = b.";
      if (ok) txt += "\nz ≥ 0 : x est ADMISSIBLE.";
      else txt += "\nz n'est pas ≥ 0 (" + z.map(function (v, i) { return v < -1e-12 ? names[i] + " < 0" : null; }).filter(Boolean).join(", ") + ") : x n'est PAS admissible, il est du mauvais côté de " + (z.filter(function (v) { return v < -1e-12; }).length > 1 ? "ces droites." : "cette droite.");
      txt += "\nCoordonnées nulles de z : " + zeros + (zeros >= 2 ? (ok ? " → x est sur deux droites à la fois : c'est un SOMMET (partie 2)." : " → intersection de deux droites, mais hors de Xad : pas un sommet.") : zeros === 1 ? " → x est sur une droite de contrainte (le bord)." : " → x n'est sur aucune droite de contrainte.");
      txt += "\n(Distance euclidienne à la droite (i) : |sᵢ| / ‖aᵢ‖, avec ‖a₁‖ = √13, ‖a₂‖ = √5, ‖a₃‖ = √2.)";
      ro.textContent = txt;
    }
    draw(); redrawers.push(draw);
  };

  /* --- 3. Le plan c·x = γ qui balaie le triangle T de l'exemple (4.5) (§3) --- */
  function p1P3(p) { return [190 - 38 * p[0] + 62 * p[1], 236 + 31 * p[0] - 70 * p[2]]; }
  WIDGETS.p1triangle = function (box) {
    var s = scaffold(box, "Le plan c·x = γ monte et balaie le triangle T de l'exemple (4.5)");
    s.svg.setAttribute("viewBox", "0 0 640 360");
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Le triangle T en perspective et le plan de niveau du coût");
    var CS = [["142", "c = (1, 4, 2) : exemple (4.5)", [1, 4, 2]], ["243", "c = (2, 4, 3) : une arête optimale", [2, 4, 3]],
      ["311", "c = (3, 1, 1)", [3, 1, 1]], ["213", "c = (2, 1, 3) : coût constant sur T", [2, 1, 3]]];
    var csel = select(s.controls, "Coût", CS.map(function (q) { return [q[0], q[1]]; }), "142", draw);
    var gS = slider(s.controls, "niveau γ", 0, 26, 0.1, 1, draw);
    button(s.controls, "premier contact", function () { var c = cur(); gS.set(Math.min.apply(null, VERT.map(function (v) { return p1dot(c, v); }))); draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "le triangle T"], ["--s2", "le plan c·x = γ et sa trace sur T"], ["--s3", "solutions optimales"]]);
    var VERT = [[3, 0, 0], [0, 6, 0], [0, 0, 2]], N = [2, 1, 3];
    var BX = [3.7, 6.8, 2.7];
    function cur() { var id = csel.value; return CS.filter(function (q) { return q[0] === id; })[0][2]; }
    function path(pts, cls, extra) {
      var d = pts.map(function (p, i) { var q = p1P3(p); return (i ? "L" : "M") + q[0].toFixed(1) + " " + q[1].toFixed(1); }).join("") + "Z";
      var a = { d: d, "class": cls }; for (var k in extra || {}) a[k] = extra[k];
      return el("path", a, s.svg);
    }
    function seg3(p, q, cls, extra) {
      var a = p1P3(p), b = p1P3(q), at = { x1: a[0], y1: a[1], x2: b[0], y2: b[1], "class": cls };
      for (var k in extra || {}) at[k] = extra[k];
      return el("line", at, s.svg);
    }
    function txt3(p, str, cls, dx, dy, anchor) {
      var a = p1P3(p), t = el("text", { x: a[0] + (dx || 0), y: a[1] + (dy || 0), "class": cls, "text-anchor": anchor || "start" }, s.svg);
      t.textContent = str; return t;
    }
    function planeBox(c, g) {
      var pts = [], i, j, k, corners = [];
      for (i = 0; i < 2; i++) for (j = 0; j < 2; j++) for (k = 0; k < 2; k++) corners.push([i * BX[0], j * BX[1], k * BX[2]]);
      for (var a = 0; a < 8; a++) for (var b = a + 1; b < 8; b++) {
        var diff = 0; for (var t = 0; t < 3; t++) if (corners[a][t] !== corners[b][t]) diff++;
        if (diff !== 1) continue;
        var fa = p1dot(c, corners[a]) - g, fb = p1dot(c, corners[b]) - g;
        if ((fa <= 0 && fb >= 0) || (fa >= 0 && fb <= 0)) {
          if (fa === fb) continue;
          var u = fa / (fa - fb), p = [0, 1, 2].map(function (m) { return corners[a][m] + u * (corners[b][m] - corners[a][m]); });
          if (!pts.some(function (q) { return Math.hypot(q[0] - p[0], q[1] - p[1], q[2] - p[2]) < 1e-9; })) pts.push(p);
        }
      }
      if (pts.length < 3) return pts;
      var gc = [0, 1, 2].map(function (m) { return pts.reduce(function (acc, q) { return acc + q[m]; }, 0) / pts.length; });
      var e = Math.abs(c[0]) < 0.9 * Math.hypot(c[0], c[1], c[2]) ? [1, 0, 0] : [0, 1, 0];
      var u1 = [c[1] * e[2] - c[2] * e[1], c[2] * e[0] - c[0] * e[2], c[0] * e[1] - c[1] * e[0]];
      var u2 = [c[1] * u1[2] - c[2] * u1[1], c[2] * u1[0] - c[0] * u1[2], c[0] * u1[1] - c[1] * u1[0]];
      pts.sort(function (p, q) {
        var dp = [p[0] - gc[0], p[1] - gc[1], p[2] - gc[2]], dq = [q[0] - gc[0], q[1] - gc[1], q[2] - gc[2]];
        return Math.atan2(p1dot(dp, u2), p1dot(dp, u1)) - Math.atan2(p1dot(dq, u2), p1dot(dq, u1));
      });
      return pts;
    }
    function draw() {
      var c = cur(), g = Math.round(gS.get() * 10) / 10;
      gS.out.textContent = p1num(g, 1);
      var vals = VERT.map(function (v) { return p1dot(c, v); });
      var M = Math.min.apply(null, vals), Mx = Math.max.apply(null, vals);
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var mk = arrowMarker(s.svg, "fk");
      [[[BX[0], 0, 0], "x₁", -22, 4], [[0, BX[1], 0], "x₂", 8, 4], [[0, 0, BX[2]], "x₃", 6, -2]].forEach(function (a) {
        seg3([0, 0, 0], a[0], "ax", { "marker-end": mk });
        txt3(a[0], a[1], "tx-i", a[2], a[3]);
      });
      var constant = Math.abs(Mx - M) < 1e-9;
      var touching = Math.abs(g - M) < 1e-9, after = g > M + 1e-9 && g < Mx - 1e-9, last = Math.abs(g - Mx) < 1e-9;
      // le plan (dans une boîte) derrière T
      var pb = planeBox(c, g);
      if (pb.length >= 3) { path(pb, "a2"); path(pb, "ln c2 thin", { "stroke-opacity": 0.6, fill: "none" }); }
      path(VERT, "a1"); path(VERT, "ln c1", { fill: "none" });
      // trace sur T
      var tr = [];
      [[0, 1], [1, 2], [0, 2]].forEach(function (e) {
        var fa = vals[e[0]] - g, fb = vals[e[1]] - g;
        if (fa === 0 && fb === 0) return;
        if ((fa <= 0 && fb >= 0) || (fa >= 0 && fb <= 0)) {
          var u = fa / (fa - fb), p = [0, 1, 2].map(function (m) { return VERT[e[0]][m] + u * (VERT[e[1]][m] - VERT[e[0]][m]); });
          if (!tr.some(function (q) { return Math.hypot(q[0] - p[0], q[1] - p[1], q[2] - p[2]) < 1e-9; })) tr.push(p);
        }
      });
      if (constant && touching) path(VERT, "a3");
      else if (tr.length === 2) seg3(tr[0], tr[1], touching ? "ln c3" : "ln c2", { style: "stroke-width:" + (touching ? 7 : 4) + "px" });
      // sommets
      var lab = [[4, 22, "start"], [-26, 24, "start"], [10, -8, "start"]];
      VERT.forEach(function (v, i) {
        var isMin = Math.abs(vals[i] - M) < 1e-9 && g >= M - 1e-9;
        var q = p1P3(v);
        el("circle", { cx: q[0], cy: q[1], r: isMin ? 7 : 4.5, "class": isMin ? "f3" : "f1" }, s.svg);
        txt3(v, "(" + v.join(", ") + ") : coût " + p1num(vals[i]), isMin ? "tx-b t3" : "tx-s", lab[i][0], lab[i][1], lab[i][2]);
      });
      var t0 = el("text", { x: 430, y: 40, "class": "tx-b t1" }, s.svg); t0.textContent = "T : x ≥ 0, 2x₁ + x₂ + 3x₃ = 6";
      var t1 = el("text", { x: 430, y: 60, "class": "tx-s t2" }, s.svg); t1.textContent = "plan : " + c.map(function (v, i) { return (v === 1 ? "" : v) + "x" + "₁₂₃"[i]; }).join(" + ") + " = " + p1num(g, 1);
      var msg = "Coûts aux sommets : " + VERT.map(function (v, i) { return "(" + v.join(", ") + ") → " + p1num(vals[i]); }).join(" ; ") + ".  Minimum M = " + p1num(M) + ".";
      if (constant) {
        msg += "\nc = (2, 1, 3) est la normale du plan de T : le coût vaut " + p1num(M) + " en tout point de T (projection de c sur le plan de T nulle).";
        msg += touching ? "\nγ = " + p1num(M) + " : le plan CONTIENT T. Tout point de T, intérieur compris, est optimal." : g < M ? "\nγ < " + p1num(M) + " : le plan est parallèle à T et ne l'a pas atteint." : "\nγ > " + p1num(M) + " : le plan est parallèle à T et l'a dépassé.";
      } else if (g < M - 1e-9) msg += "\nγ = " + p1num(g, 1) + " < M : le plan n'a pas encore touché T (tout point de T coûte plus que γ).";
      else if (touching) {
        var mins = VERT.filter(function (v, i) { return Math.abs(vals[i] - M) < 1e-9; });
        msg += "\nγ = M : PREMIER CONTACT, " + (mins.length === 1 ? "au seul sommet (" + mins[0].join(", ") + ") : c'est l'unique solution optimale." : "le long de toute l'arête (" + mins[0].join(", ") + ") — (" + mins[1].join(", ") + ") : une infinité de solutions optimales, dont deux sommets.");
      } else if (after) msg += "\nγ = " + p1num(g, 1) + " : la trace du plan sur T est un segment (les points de T de coût γ). Ils ne sont pas optimaux : on a déjà touché T à γ = " + p1num(M) + ".";
      else if (last) msg += "\nγ = " + p1num(Mx) + " : dernier contact (le maximum du coût sur T).";
      else msg += "\nγ > " + p1num(Mx) + " : le plan a dépassé T.";
      ro.textContent = msg;
    }
    draw(); redrawers.push(draw);
  };

  /* --- 4. Le cône des colonnes pour une seule contrainte (existence, §5) --- */
  // min et max de c·x sur {x ≥ 0 : a·x = b} (une seule contrainte) : bornes, colonnes qui les atteignent.
  function p1oneRow(a, c, b) {
    var n = a.length, i, j;
    if (b < 0) { a = a.map(function (v) { return -v; }); b = -b; }
    var feas = b === 0 || a.some(function (v) { return v > 0; });
    if (!feas) return { feasible: false };
    var lo = null, hi = null, loCols = [], hiCols = [], unbLo = false, unbHi = false;
    for (i = 0; i < n; i++) {
      if (a[i] === 0 && c[i] < 0) unbLo = true;
      if (a[i] === 0 && c[i] > 0) unbHi = true;
      for (j = 0; j < n; j++) if (a[i] > 0 && a[j] < 0) {
        var r = c[i] / a[i] - c[j] / a[j];
        if (r < -1e-12) unbLo = true;
        if (r > 1e-12) unbHi = true;
      }
    }
    if (b === 0) { lo = 0; hi = 0; }
    else {
      for (i = 0; i < n; i++) if (a[i] > 0) {
        var v = b * c[i] / a[i];
        if (lo === null || v < lo - 1e-12) { lo = v; loCols = [i]; } else if (Math.abs(v - lo) <= 1e-12) loCols.push(i);
        if (hi === null || v > hi + 1e-12) { hi = v; hiCols = [i]; } else if (Math.abs(v - hi) <= 1e-12) hiCols.push(i);
      }
    }
    return { feasible: true, lo: unbLo ? -Infinity : lo, hi: unbHi ? Infinity : hi, loCols: unbLo ? [] : loCols, hiCols: unbHi ? [] : hiCols, a: a, b: b };
  }
  // Le cône engendré par des vecteurs du plan, sous forme de demi-plans {u x + v y ≤ 0} (null : tout le plan).
  function p1coneCons(vs) {
    var ang = [];
    vs.forEach(function (v) { if (Math.hypot(v[0], v[1]) > 1e-12) { var t = Math.atan2(v[1], v[0]); if (t < 0) t += 2 * Math.PI; ang.push(t); } });
    ang.sort(function (p, q) { return p - q; });
    var uniq = []; ang.forEach(function (t) { if (!uniq.length || t - uniq[uniq.length - 1] > 1e-9) uniq.push(t); });
    if (uniq.length > 1 && 2 * Math.PI - uniq[uniq.length - 1] + uniq[0] < 1e-9) uniq.pop();
    if (!uniq.length) return { type: "zéro" };
    if (uniq.length === 1) return { type: "demi-droite", u: [Math.cos(uniq[0]), Math.sin(uniq[0])] };
    var G = -1, k = 0;
    for (var i = 0; i < uniq.length; i++) {
      var gap = (i + 1 < uniq.length ? uniq[i + 1] : uniq[0] + 2 * Math.PI) - uniq[i];
      if (gap > G) { G = gap; k = i; }
    }
    var start = uniq[(k + 1) % uniq.length], end = uniq[k];
    var u = [Math.cos(start), Math.sin(start)], w = [Math.cos(end), Math.sin(end)];
    if (G > Math.PI + 1e-9) return { type: "secteur", cons: [[u[1], -u[0], 0], [-w[1], w[0], 0]], u: u, w: w };
    if (Math.abs(G - Math.PI) <= 1e-9) return uniq.length === 2 ? { type: "droite", u: u } : { type: "demi-plan", cons: [[u[1], -u[0], 0]], u: u };
    return { type: "plan", cons: [] };
  }
  WIDGETS.p1cone = function (box) {
    var s = scaffold(box, "Le cône des colonnes : pourquoi l'infimum d'un PL est atteint (une contrainte, trois variables)");
    var BOX = [-3, 6, -6, 10];
    var pl = new Plot(s.svg, { x: [BOX[0], BOX[1]], y: [BOX[2], BOX[3]], w: 640, h: 440, pad: { l: 40, r: 16, t: 20, b: 40 }, label: "Le cône engendré par les colonnes (a_i, c_i), la verticale t = b et l'intervalle des coûts réalisables" });
    var PRE = {
      atteint: { cols: [[1, 2], [2, 1], [1, -1]], b: 4 },
      moinsinf: { cols: [[1, 2], [2, 1], [-1, -3]], b: 4 },
      vide: { cols: [[1, 2], [2, 1], [1, -1]], b: -2 },
      arete: { cols: [[1, -1], [2, -2], [1, 2]], b: 4 }
    };
    var cols = PRE.atteint.cols.map(function (v) { return v.slice(); }), drag = -1;
    var pre = select(s.controls, "Exemple", [["atteint", "minimum atteint"], ["moinsinf", "valeur −∞"], ["vide", "Xad vide"], ["arete", "deux colonnes optimales"]], "atteint", function () {
      var P = PRE[pre.value]; cols = P.cols.map(function (v) { return v.slice(); }); bS.set(P.b); draw();
    });
    var bS = slider(s.controls, "second membre b", -3, 6, 0.5, 4, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--muted", "cône C = {Σ xᵢ 𝒜ᵢ, x ≥ 0}"], ["--s1", "coûts réalisables (C sur la verticale t = b)"], ["--s3", "minimum"]]);
    function pick(e) {
      var p = svgPoint(s.svg, e), best = -1, bd = 22;
      cols.forEach(function (v, i) { var d = Math.hypot(pl.tx(v[0]) - p.x, pl.ty(v[1]) - p.y); if (d < bd) { bd = d; best = i; } });
      return best;
    }
    s.svg.addEventListener("pointerdown", function (e) { drag = pick(e); if (drag >= 0) { try { s.svg.setPointerCapture(e.pointerId); } catch (err) {} } });
    s.svg.addEventListener("pointermove", function (e) {
      if (drag < 0) return;
      var p = svgPoint(s.svg, e), u = Math.round(pl.ix(p.x) * 2) / 2, v = Math.round(pl.iy(p.y) * 2) / 2;
      u = Math.min(Math.max(u, -2.5), 5.5); v = Math.min(Math.max(v, -5.5), 9.5);
      if (u === 0 && v === 0) return;
      cols[drag] = [u, v]; draw();
    });
    s.svg.addEventListener("pointerup", function () { drag = -1; });
    s.svg.addEventListener("pointercancel", function () { drag = -1; });
    function ray(v, cls) {
      var L = 40 / Math.hypot(v[0], v[1]);
      pl.seg(0, 0, v[0] * L, v[1] * L, cls);
    }
    function draw() {
      var b = Math.round(bS.get() * 2) / 2; bS.out.textContent = p1num(b);
      var a = cols.map(function (v) { return v[0]; }), c = cols.map(function (v) { return v[1]; });
      var R = p1oneRow(a, c, b), K = p1coneCons(cols);
      pl.clear();
      pl.axes({ xticks: [-2, 0, 2, 4, 6], yticks: [-6, -4, -2, 0, 2, 4, 6, 8, 10], cross: true, xlabel: "t = a·x", ylabel: "y = c·x" });
      pl.clip();
      if (K.cons) { var P = halfPlanePolygon(K.cons, BOX); if (P.length) pl.poly(P.concat([P[0]]), "am"); }
      if (K.type === "demi-droite") ray(K.u, "ln cm");
      if (K.type === "droite") { ray(K.u, "ln cm"); ray([-K.u[0], -K.u[1]], "ln cm"); }
      cols.forEach(function (v) { ray(v, "ln cm thin"); });
      pl.seg(b, BOX[2], b, BOX[3], "ln cm thin dash");
      if (R.feasible) {
        var y0 = Math.max(R.lo, BOX[2] - 1), y1 = Math.min(R.hi, BOX[3] + 1);
        pl.seg(b, y0, b, y1, "ln c1", { style: "stroke-width:5px" });
      }
      pl.unclip();
      var mk2 = arrowMarker(s.svg, "f2");
      if (R.feasible && R.lo === -Infinity) { pl.seg(b + 0.25, -2, b + 0.25, BOX[2] + 0.3, "ln c2", { "marker-end": mk2 }); pl.text(b + 0.25, -3.5, "c·x → −∞", "tx-b t2", "start", 8, 0); }
      if (R.feasible && R.hi === Infinity) { pl.seg(b + 0.25, 6, b + 0.25, BOX[3] - 0.3, "ln c2", { "marker-end": mk2 }); }
      if (R.feasible && isFinite(R.lo)) { pl.dot(b, R.lo, 7, "f3"); pl.text(b, R.lo, "min " + p1num(R.lo), "tx-b t3", "start", 10, 4); }
      cols.forEach(function (v, i) {
        pl.dot(v[0], v[1], 7, "fk drag");
        // étiquette du côté où la demi-droite de la colonne ne passe pas : dessous si elle monte, dessus sinon
        pl.text(v[0], v[1], "𝒜" + "₁₂₃"[i] + " = " + p1pt(v), "tx-s", v[0] < 0 ? "end" : "start", v[0] < 0 ? -9 : 9, v[1] > 0 ? 17 : -9);
      });
      var t = "a = (" + a.map(p1num).join(", ") + "), c = (" + c.map(p1num).join(", ") + "), b = " + p1num(b) + " : on minimise c·x sur Xad = {x ≥ 0 : a·x = b}.";
      t += "\nLe cône C est " + { "zéro": "réduit à {0}", "demi-droite": "une demi-droite", "secteur": "un secteur d'angle < 180° (fermé)", "demi-plan": "un demi-plan (fermé)", "droite": "une droite", "plan": "tout le plan" }[K.type] + ".";
      if (!R.feasible) t += "\nLa verticale t = " + p1num(b) + " ne rencontre pas C : Xad est VIDE (aucun x ≥ 0 n'a a·x = b), valeur +∞.";
      else {
        t += "\nCoûts réalisables {c·x : x ∈ Xad} = " + (R.lo === -Infinity ? "]−∞" : "[" + p1num(R.lo)) + ", " + (R.hi === Infinity ? "+∞[" : p1num(R.hi) + "]") + " : un intervalle fermé (C est fermé).";
        if (R.lo === -Infinity) t += "\nValeur −∞ : C contient la direction (0, −1) — on garde a·x = b en faisant baisser le coût sans fin. Pas de solution optimale.";
        else if (b === 0) t += "\nb = 0 : x = 0 est admissible et optimal (valeur 0).";
        else {
          t += "\nMinimum " + p1num(R.lo) + " ATTEINT en x = (b/aᵢ) eᵢ pour i = " + R.loCols.map(function (i) { return i + 1; }).join(" ou ") + " : une seule composante non nulle (une solution basique, m = 1).";
          if (R.loCols.length > 1) t += " Deux colonnes sur la même demi-droite du bord : toutes leurs combinaisons sont optimales (une arête optimale).";
        }
      }
      ro.textContent = t;
    }
    draw(); redrawers.push(draw);
  };
