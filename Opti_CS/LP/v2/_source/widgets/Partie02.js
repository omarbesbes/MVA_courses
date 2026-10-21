// widgets/Partie02.js — interactive figures of Partie 2 (sommets et solutions basiques).
// Inserted by build.mjs inside the scope of app.js: uses el, Plot, scaffold, select, button, checkbox, readout,
// legend, fmt, svgPoint, combinations, Fr, frDet, basicSolution, halfPlanePolygon, lineInBox, arrowMarker and
// registers its widgets in WIDGETS. Every helper of this file is prefixed by p2.

  /* ---------------- shared helpers of the page ---------------- */
  var P2_SUBS = "₀₁₂₃₄₅₆₇₈₉";
  function p2sub(k) { return String(k).split("").map(function (ch) { return P2_SUBS[+ch]; }).join(""); }
  function p2set(cols) { return "{" + cols.map(function (j) { return j + 1; }).join(", ") + "}"; }
  function p2vec(x) { return "(" + x.map(function (v) { return v.str(); }).join(", ") + ")"; }
  function p2pt(x) { return "(" + x[0].str() + " ; " + x[1].str() + ")"; }
  function p2int(v) { return String(v).replace("-", "−"); }
  // The running example: Allaire, Exercice 4.2.1 in standard form (m = 3, n = 5); b3 = 5, or 7/2 (degenerate variant).
  var P2_A = [[-3, 2, 1, 0, 0], [-1, 2, 0, 1, 0], [1, 1, 0, 0, 1]];
  // y = P2_M d: the vector of the kernel of A that moves the point (x1, x2) of the plane by d = (d1, d2).
  var P2_M = [[1, 0], [0, 1], [3, -2], [1, -2], [-1, -1]];
  function p2lines(b3) { return [[1, 0, 0], [0, 1, 0], [-3, 2, 2], [-1, 2, 4], [1, 1, b3]]; }
  function p2polygon(b3, box) { return halfPlanePolygon([[-1, 0, 0], [0, -1, 0], [-3, 2, 2], [-1, 2, 4], [1, 1, b3]], box); }
  function p2full(x1, x2, b3) {
    return [x1, x2, Fr(2).add(x1.mul(3)).sub(x2.mul(2)), Fr(4).add(x1).sub(x2.mul(2)), Fr.of(b3).sub(x1).sub(x2)];
  }
  // Draws the polygon, the five lines x_i = 0 (labels at lab[i] = [x, y, anchor, dx, dy]) and returns nothing.
  function p2drawPolygon(plot, b3, box, lab, hl) {
    var P = p2polygon(b3, box);
    if (P.length) { plot.poly(P.concat([P[0]]), "a1"); }
    p2lines(b3).forEach(function (L, i) {
      var seg = lineInBox(L[0], L[1], L[2], box);
      if (!seg) return;
      var on = hl && hl.indexOf(i) >= 0;
      plot.seg(seg[0][0], seg[0][1], seg[1][0], seg[1][1], on ? "ln c3" : "ln cm thin", on ? { style: "stroke-width:3px" } : {});
      if (lab[i]) plot.text(lab[i][0], lab[i][1], "x" + p2sub(i + 1) + " = 0", on ? "tx-s t3" : "tx-s", lab[i][2], lab[i][3], lab[i][4]);
    });
    if (P.length) plot.poly(P.concat([P[0]]), "ln c1");
  }

  /* --- 1. The ten choices of three columns of Exercise 4.2.1 (§2) --- */
  WIDGETS.p2bases = function (box) {
    var s = scaffold(box, "Les dix choix de trois colonnes de l'Exercice 4.2.1 : une base = deux droites xᵢ = 0");
    var BOX = [-4.7, 6.3, -0.9, 5.8];
    var plot = new Plot(s.svg, { x: [BOX[0], BOX[1]], y: [BOX[2], BOX[3]], w: 680, h: 420, pad: { l: 30, r: 10, t: 10, b: 26 },
      label: "Le polygone de l'Exercice 4.2.1, les cinq droites x_i = 0 et les dix points de base" });
    var LAB = [[0, 5.8, "start", 5, 12], [6.3, 0, "end", -2, -6], [3.2, 5.8, "start", 6, 12], [-4.7, -0.35, "start", 4, 16], [5.85, -0.9, "end", -8, -4]];
    var vSel = select(s.controls, "Variante", [["5", "x₁ + x₂ ≤ 5 (Ex. 4.2.1)"], ["3.5", "x₁ + x₂ ≤ 7/2 (dégénérée)"]], "5", function () {
      compute(); if (sel.kind === "point" && !basesOf(sel.key).length) sel = { kind: "base", k: 0 }; draw();
    });
    var nbBox = checkbox(s.controls, "bases voisines", false, draw);
    var lab = document.createElement("span"); lab.textContent = "Base B :"; s.controls.appendChild(lab);
    var all = combinations(5, 3), data = [], sel = { kind: "base", k: 0 };
    var btns = all.map(function (cols, k) {
      return button(s.controls, p2set(cols).replace(/ /g, ""), function () { sel = { kind: "base", k: k }; draw(); });
    });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "point de base admissible (sommet)"], ["--s6", "point de base non admissible"], ["--s3", "base choisie : ses deux droites hors base"]]);
    function keyOf(x) { return x[0].str() + "|" + x[1].str(); }
    function compute() {
      var b3 = Fr.of(parseFloat(vSel.value));
      data = all.map(function (cols) {
        var r = basicSolution(P2_A, [2, 4, b3], cols);
        return { cols: cols, x: r.x, status: r.status, key: r.x ? keyOf(r.x) : null,
          N: [0, 1, 2, 3, 4].filter(function (j) { return cols.indexOf(j) < 0; }) };
      });
    }
    function basesOf(key) { return data.filter(function (d) { return d.key === key; }); }
    function admissible(d) { return d.status === "admissible" || d.status === "dégénérée"; }
    function neighbours(d) {
      return data.filter(function (e) {
        if (e === d) return false;
        var common = e.cols.filter(function (j) { return d.cols.indexOf(j) >= 0; }).length;
        return common === 2;
      });
    }
    function bMatrix(cols) {
      return "[" + P2_A.map(function (row) { return "[" + cols.map(function (j) { return p2int(row[j]); }).join(", ") + "]"; }).join(", ") + "]";
    }
    s.svg.addEventListener("click", function (e) {
      var pt = svgPoint(s.svg, e), best = null, bd = 16;
      data.forEach(function (d) {
        if (!d.x) return;
        var dd = Math.hypot(plot.tx(d.x[0].val()) - pt.x, plot.ty(d.x[1].val()) - pt.y);
        if (dd < bd) { bd = dd; best = d.key; }
      });
      if (best) { sel = { kind: "point", key: best }; draw(); }
    });
    function draw() {
      var b3 = parseFloat(vSel.value);
      var cur = sel.kind === "base" ? data[sel.k] : null;
      var key = cur ? cur.key : sel.key;
      plot.clear();
      plot.axes({ xticks: [-4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6], yticks: [1, 2, 3, 4, 5], cross: true });
      p2drawPolygon(plot, b3, BOX, LAB, cur ? cur.N : null);
      if (cur && nbBox.checked && cur.x) {
        neighbours(cur).forEach(function (e) {
          if (!e.x || e.key === cur.key) return;
          plot.seg(cur.x[0].val(), cur.x[1].val(), e.x[0].val(), e.x[1].val(), admissible(e) ? "ln c3 dash" : "ln c6 dot", { style: "stroke-width:2.6px" });
        });
      }
      var seen = {};
      data.forEach(function (d) {
        if (!d.x || seen[d.key]) return;
        seen[d.key] = true;
        plot.dot(d.x[0].val(), d.x[1].val(), 5.5, admissible(d) ? "f1" : "f6");
      });
      if (cur && nbBox.checked && cur.x) { // admissible neighbours: a thin green ring (their segments lie on the green lines)
        neighbours(cur).forEach(function (e) {
          if (e.x && e.key !== cur.key && admissible(e)) plot.dot(e.x[0].val(), e.x[1].val(), 8.5, "ln c3 nofill dash");
        });
      }
      if (key) {
        var d0 = basesOf(key)[0];
        plot.dot(d0.x[0].val(), d0.x[1].val(), 10, "ln c3 nofill");
      }
      btns.forEach(function (b, k) {
        b.style.outline = cur && k === sel.k ? "2px solid var(--s3)" : "";
        b.style.fontWeight = cur && k === sel.k ? "700" : "";
      });
      // readout
      var t = "";
      if (cur) {
        var Ns = cur.N.map(function (j) { return "x" + p2sub(j + 1); });
        t += "Base B = " + p2set(cur.cols) + " : hors base " + Ns.join(" = ") + " = 0 (les droites " + Ns[0] + " = 0 et " + Ns[1] + " = 0).\n";
        t += "B = (" + cur.cols.map(function (j) { return "a" + p2sub(j + 1); }).join(" ") + ") = " + bMatrix(cur.cols) + ",  det B = " + frDet(P2_A.map(function (row) { return cur.cols.map(function (j) { return row[j]; }); })).str();
        if (!cur.x) { t += " : singulière, pas de point de base."; }
        else {
          t += " ≠ 0 : inversible.\n";
          t += "variables de base B⁻¹b :  " + cur.cols.map(function (j) { return "x" + p2sub(j + 1) + " = " + cur.x[j].str(); }).join(",  ") + "   →   x = " + p2vec(cur.x) + "\n";
          if (cur.status === "non admissible") {
            var neg = cur.cols.filter(function (j) { return cur.x[j].sign() < 0; });
            t += neg.map(function (j) { return "x" + p2sub(j + 1) + " = " + cur.x[j].str(); }).join(", ") + " < 0 : non admissible ; le point " + p2pt(cur.x) + " est hors du polygone.";
          } else {
            var same = basesOf(cur.key);
            t += (cur.status === "dégénérée" ? "Solution basique dégénérée (une variable de base nulle)" : "Toutes ≥ 0 : solution basique") +
              ", le sommet " + p2pt(cur.x) + " ; x₁ + 2x₂ = " + cur.x[0].add(cur.x[1].mul(2)).str() + ".";
            if (same.length > 1) t += "\nLe même point est donné par " + same.length + " bases : " + same.map(function (d) { return p2set(d.cols); }).join(", ") + ".";
          }
          if (nbBox.checked) {
            t += "\nBases voisines (une colonne échangée) : " + neighbours(cur).map(function (e) {
              var st = !e.x ? "singulière" : admissible(e) ? (e.key === cur.key ? "même point" : "sommet " + p2pt(e.x)) : "non admissible";
              return p2set(e.cols) + " " + st;
            }).join(" ; ") + ".";
          }
        }
      } else {
        var bs = basesOf(sel.key), d1 = bs[0];
        var zeros = [0, 1, 2, 3, 4].filter(function (j) { return d1.x[j].isZero(); });
        t += "Le point " + p2pt(d1.x) + ", x = " + p2vec(d1.x) + ", est donné par " + (bs.length > 1 ? bs.length + " bases : " : "la base ") +
          bs.map(function (d) { return p2set(d.cols); }).join(", ") + ".\n";
        t += zeros.length + " droites xᵢ = 0 y passent (" + zeros.map(function (j) { return "x" + p2sub(j + 1); }).join(", ") + ")";
        if (!admissible(d1)) t += " ; point non admissible (" + d1.cols.filter(function (j) { return d1.x[j].sign() < 0; }).map(function (j) { return "x" + p2sub(j + 1) + " = " + d1.x[j].str(); }).join(", ") + ").";
        else t += zeros.length > 2 ? " : plus que n − m = 2, le sommet est dégénéré." : " : sommet non dégénéré, une seule base.";
      }
      var inv = data.filter(function (d) { return d.x; }).length, adm = data.filter(admissible).length;
      var verts = {}; data.filter(admissible).forEach(function (d) { verts[d.key] = 1; });
      t += "\nBilan : 10 choix, " + inv + " inversibles, " + adm + " bases admissibles pour " + Object.keys(verts).length + " sommets, " + (inv - adm) + " non admissibles. Cliquez un point pour voir ses bases.";
      ro.textContent = t;
    }
    compute(); draw(); redrawers.push(draw);
  };

  /* --- 2. Sliding to a vertex: the proof of Proposition 4.2.6 (§4) --- */
  WIDGETS.p2glisser = function (box) {
    var s = scaffold(box, "Glisser jusqu'au sommet : réduire le support le long d'une direction du noyau");
    var BOX = [-0.5, 6.1, -0.5, 4.2];
    var plot = new Plot(s.svg, { x: [BOX[0], BOX[1]], y: [BOX[2], BOX[3]], w: 680, h: 440, pad: { l: 30, r: 10, t: 10, b: 26 },
      label: "Le polygone de l'Exercice 4.2.1 et le chemin qui réduit le support d'un point jusqu'à un sommet" });
    var LAB = [[0, 4.2, "start", 5, 12], [6.1, 0, "end", -2, -6], [1.45, 4.2, "end", -4, 12], [4.4, 4.2, "start", 6, 12], [5.6, -0.5, "end", -6, -4]];
    var COSTS = { "0": [0, 0, 0, 0, 0], "11": [-1, -1, 0, 0, 0], "12": [-1, -2, 0, 0, 0] };
    var OPT = { "0": Fr(0), "11": Fr(-5), "12": Fr(-8) };
    var cSel = select(s.controls, "Coût", [["0", "c = 0 : tout point est optimal"], ["11", "max x₁ + x₂ : une arête optimale"], ["12", "max x₁ + 2x₂ (Ex. 4.2.1)"]], "0", restart);
    var pSel = select(s.controls, "Départ", [["2,2", "(1 ; 1), intérieur"], ["6,4", "(3 ; 2), sur l'arête x₅ = 0"], ["0,1", "(0 ; 1/2), sur l'arête x₁ = 0"], ["click", "point cliqué"]], "2,2", function () { if (pSel.value !== "click") { start = pSel.value.split(",").map(function (v) { return Fr(+v, 2); }); } restart(); });
    var dSel = select(s.controls, "Direction (intérieur)", [["1,0", "→ (1, 0)"], ["1,1", "↗ (1, 1)"], ["0,1", "↑ (0, 1)"], ["-1,1", "↖ (−1, 1)"], ["-1,0", "← (−1, 0)"], ["-1,-1", "↙ (−1, −1)"], ["0,-1", "↓ (0, −1)"], ["1,-1", "↘ (1, −1)"]], "1,0", draw);
    button(s.controls, "Un pas", function () { var st = plan(path[path.length - 1]); if (st.move) { path.push(st.next); steps.push(st); } draw(); });
    button(s.controls, "Jusqu'au sommet", function () {
      for (var it = 0; it < 6; it++) { var st = plan(path[path.length - 1]); if (!st.move) break; path.push(st.next); steps.push(st); }
      draw();
    });
    button(s.controls, "Recommencer", restart);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "Xad"], ["--s2", "lignes de niveau du coût"], ["--s3", "solutions optimales, chemin"], ["--muted", "x ± εy : x est un milieu"]]);
    var start = [Fr(1), Fr(1)], path = [], steps = [];
    function restart() { path = [p2full(start[0], start[1], 5)]; steps = []; draw(); }
    function dot(c, y) { var r = Fr(0); for (var j = 0; j < 5; j++) r = r.add(y[j].mul(c[j])); return r; }
    // One step of the proof from x: the direction y, its sign, the step eps0, the next point.
    function plan(x) {
      var c = COSTS[cSel.value];
      var Z = [0, 1, 2, 3, 4].filter(function (j) { return x[j].isZero(); });
      var rows = Z.map(function (j) { return P2_M[j]; }), rk = 0, r0 = null;
      rows.forEach(function (r) {
        if (!r0) { r0 = r; rk = 1; } else if (r0[0] * r[1] - r0[1] * r[0] !== 0) rk = 2;
      });
      var supp = [0, 1, 2, 3, 4].filter(function (j) { return !x[j].isZero(); });
      if (rk === 2) return { move: false, supp: supp, Z: Z };
      var u = dSel.value.split(",").map(Number), d;
      if (rk === 0) d = u;
      else { d = [-r0[1], r0[0]]; if (d[0] * u[0] + d[1] * u[1] < 0) d = [-d[0], -d[1]]; }
      var y = P2_M.map(function (row) { return Fr(row[0] * d[0] + row[1] * d[1]); });
      var cy = dot(c, y), flipped = false;
      var hasNeg = y.some(function (v) { return v.sign() < 0; });
      if (cy.sign() > 0 || (cy.isZero() && !hasNeg)) { y = y.map(function (v) { return v.neg(); }); cy = cy.neg(); flipped = true; }
      var eps0 = null, jst = [];
      y.forEach(function (v, j) {
        if (v.sign() >= 0) return;
        var q = x[j].div(v.neg());
        if (eps0 === null || q.cmp(eps0) < 0) { eps0 = q; jst = [j]; } else if (q.cmp(eps0) === 0) jst.push(j);
      });
      if (eps0 === null) return { move: false, unbounded: true, supp: supp, Z: Z, y: y, cy: cy };
      var epsSym = null;
      y.forEach(function (v, j) { if (v.isZero()) return; var q = x[j].div(v.sign() > 0 ? v : v.neg()); if (epsSym === null || q.cmp(epsSym) < 0) epsSym = q; });
      var next = x.map(function (v, j) { return v.add(eps0.mul(y[j])); });
      return { move: true, supp: supp, Z: Z, rank: rk, y: y, cy: cy, flipped: flipped, eps0: eps0, jst: jst, epsSym: epsSym, next: next, free: rk === 0 };
    }
    s.svg.addEventListener("click", function (e) {
      var pt = svgPoint(s.svg, e);
      var x1 = Math.round(plot.ix(pt.x) * 2), x2 = Math.round(plot.iy(pt.y) * 2);
      var cand = p2full(Fr(x1, 2), Fr(x2, 2), 5);
      if (cand.some(function (v) { return v.sign() < 0; })) { ro.textContent = "Ce point (" + Fr(x1, 2).str() + " ; " + Fr(x2, 2).str() + ") est hors du polygone : choisissez un point de Xad."; return; }
      start = [Fr(x1, 2), Fr(x2, 2)]; pSel.value = "click"; restart();
    });
    function draw() {
      var cv = cSel.value, c = COSTS[cv];
      plot.clear();
      var mk = arrowMarker(s.svg, "f3"); // Plot.clear() empties the svg, defs included
      plot.axes({ xticks: [0, 1, 2, 3, 4, 5, 6], yticks: [1, 2, 3, 4], cross: true });
      plot.clip();
      if (cv === "11") [1, 2, 3, 4, 5].forEach(function (g) { var L = lineInBox(1, 1, g, BOX); if (L) plot.seg(L[0][0], L[0][1], L[1][0], L[1][1], "ln c2 thin dash"); });
      if (cv === "12") [2, 4, 6, 8].forEach(function (g) { var L = lineInBox(1, 2, g, BOX); if (L) plot.seg(L[0][0], L[0][1], L[1][0], L[1][1], "ln c2 thin dash"); });
      plot.unclip();
      p2drawPolygon(plot, 5, BOX, LAB, null);
      if (cv === "11") plot.seg(2, 3, 5, 0, "ln c3", { style: "stroke-width:6px", "stroke-opacity": 0.45 });
      if (cv === "12") plot.dot(2, 3, 11, "ln c3 nofill");
      if (cv === "11") plot.text(4, 1, "x₁ + x₂ = 5 (optimum)", "tx-s t2", "start", 14, 4);
      if (cv === "12") plot.text(3.6, 2.2, "x₁ + 2x₂ = 8 (optimum)", "tx-s t2", "start", 0, -6);
      var x = path[path.length - 1], st = plan(x);
      if (st.move) {
        var a = [x[0].sub(st.epsSym.mul(st.y[0])).val(), x[1].sub(st.epsSym.mul(st.y[1])).val()];
        var b = [x[0].add(st.epsSym.mul(st.y[0])).val(), x[1].add(st.epsSym.mul(st.y[1])).val()];
        plot.seg(a[0], a[1], b[0], b[1], "ln cm", { style: "stroke-width:5px", "stroke-opacity": 0.5 });
        plot.seg(x[0].val(), x[1].val(), st.next[0].val(), st.next[1].val(), "ln c3 dash", { "marker-end": mk });
      }
      for (var i = 1; i < path.length; i++) plot.seg(path[i - 1][0].val(), path[i - 1][1].val(), path[i][0].val(), path[i][1].val(), "ln c3");
      path.forEach(function (p, i) {
        var last = i === path.length - 1;
        plot.dot(p[0].val(), p[1].val(), last ? 6.5 : 4.5, last && !st.move ? "f3" : "fk");
        plot.text(p[0].val(), p[1].val(), "x" + ["⁰", "¹", "²", "³", "⁴", "⁵", "⁶"][Math.min(i, 6)], "tx-i", "start", 8, i % 2 ? 16 : -8);
      });
      // readout
      var cost = dot(c, x), t = "";
      t += "x = " + p2vec(x) + "   coût c·x = " + cost.str() + (cost.cmp(OPT[cv]) === 0 ? " (optimal)" : " (optimum : " + OPT[cv].str() + ")") + "\n";
      t += "support " + p2set(st.supp) + " : k = " + st.supp.length;
      if (!st.move && !st.unbounded) {
        var B = st.supp.length === 3 ? st.supp : null;
        t += ", colonnes " + st.supp.map(function (j) { return "a" + p2sub(j + 1); }).join(", ") + " libres" + (B ? " (det = " + frDet(P2_A.map(function (row) { return B.map(function (j) { return row[j]; }); })).str() + ")" : "") +
          " → sommet, solution basique de la base " + p2set(st.supp) + ".";
        if (cost.cmp(OPT[cv]) !== 0) t += "\nCe sommet n'est pas optimal : pour aller plus loin, il faut passer à un sommet voisin meilleur (le simplexe, partie 3).";
      } else if (st.move) {
        t += (st.supp.length > 3 ? " > m = 3 : colonnes liées" : " : colonnes liées") + " → pas un sommet.\n";
        t += "y = " + p2vec(st.y) + " : Ay = 0, y nul hors du support" + (st.free ? " (direction choisie)" : " (direction imposée : garder " + st.Z.map(function (j) { return "x" + p2sub(j + 1); }).join(", ") + " = 0)") + ".\n";
        t += "c·y = " + st.cy.str() + (st.cy.isZero() ? " : direction plate, le coût ne change pas." : " < 0 : x n'est pas optimal ; on prend le sens qui fait baisser le coût (version constructive).") + "\n";
        t += "x ± εy ∈ Xad pour ε ≤ " + st.epsSym.str() + " (segment gris : x en est le milieu).\n";
        t += "Pas maximal ε₀ = min{ xⱼ/(−yⱼ) : yⱼ < 0 } = " + st.eps0.str() + " : " + st.jst.map(function (j) { return "x" + p2sub(j + 1); }).join(" et ") + " s'annule" + (st.jst.length > 1 ? "nt" : "") + " → « Un pas » mène à " + p2vec(st.next) + ".";
      }
      if (steps.length) t += "\nChemin : " + path.map(p2pt).join(" → ") + "  (supports de taille " + path.map(function (p) { return p.filter(function (v) { return !v.isZero(); }).length; }).join(", ") + ").";
      ro.textContent = t;
    }
    restart(); redrawers.push(draw);
  };

  /* --- 3. How many vertices: the cube of Exercise 4.2.2 (§5) --- */
  WIDGETS.p2compteur = function (box) {
    var s = scaffold(box, "Combien de sommets ? Le cube de l'Exercice 4.2.2 avec n = 2m");
    var plot = new Plot(s.svg, { x: [1, 50], y: [1, 1e30], ylog: true, w: 680, h: 360, pad: { l: 46, r: 14, t: 14, b: 34 },
      label: "Nombre de choix de colonnes, de sommets du cube et m au cube, en échelle logarithmique, en fonction de m" });
    var mS = slider(s.controls, "m =", 1, 50, 1, 30, draw);
    var vSel = select(s.controls, "Vitesse", [["1e6", "10⁶ choix par seconde"], ["1e9", "10⁹ choix par seconde"], ["1e12", "10¹² choix par seconde"]], "1e9", draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "choix de colonnes C(2m, m)"], ["--s3", "sommets du cube 2ᵐ"], ["--muted", "m³ (un pivot de Gauss)"]]);
    function lbinom(m) { var l = 0; for (var i = 1; i <= m; i++) l += Math.log10((m + i) / i); return l; }
    function binomExact(m) { var c = BigInt(1); for (var i = 1; i <= m; i++) c = c * BigInt(m + i) / BigInt(i); return c.toString(); }
    var SUP = { "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "-": "⁻" };
    function sup(e) { return String(e).split("").map(function (ch) { return SUP[ch]; }).join(""); }
    function sci(l10) { // a number given by its log10, "≈ 1,18·10¹⁷"
      var e = Math.floor(l10 + 1e-12), mant = Math.pow(10, l10 - e);
      if (mant >= 9.995) { mant /= 10; e += 1; }
      return fmt(mant, 2).replace(".", ",") + "·10" + sup(e);
    }
    function group(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, " "); }
    function count(l10, exact) { return l10 < 15 ? "= " + group(exact) : "≈ " + sci(l10); }
    function duration(sec) {
      var y = sec / (365.25 * 24 * 3600);
      if (sec < 1e-6) return fmt(sec * 1e9, 1).replace(".", ",") + " ns";
      if (sec < 1e-3) return fmt(sec * 1e6, 1).replace(".", ",") + " µs";
      if (sec < 1) return fmt(sec * 1e3, 1).replace(".", ",") + " ms";
      if (sec < 120) return fmt(sec, 1).replace(".", ",") + " s";
      if (sec < 7200) return fmt(sec / 60, 1).replace(".", ",") + " min";
      if (sec < 2 * 86400) return fmt(sec / 3600, 1).replace(".", ",") + " h";
      if (y < 1) return fmt(sec / 86400, 1).replace(".", ",") + " jours";
      if (y < 1e4) return fmt(y, 1).replace(".", ",") + " ans";
      var t = "≈ " + sci(Math.log10(y)) + " ans";
      if (y > 1.38e10) { var r = y / 1.38e10; t += " (≈ " + (r < 1e4 ? String(Math.round(r)) : sci(Math.log10(r))) + " fois l'âge de l'Univers)"; }
      return t;
    }
    function draw() {
      var m = mS.get(), speed = parseFloat(vSel.value), i;
      mS.out.textContent = m + "  (n = " + 2 * m + ")";
      plot.clear();
      plot.axes({ xticks: [1, 10, 20, 30, 40, 50], yticks: [1, 1e6, 1e12, 1e18, 1e24, 1e30], yfmt: function (v) { var e = Math.round(Math.log10(v)); return e === 0 ? "1" : "10" + sup(e); } });
      var cb = [], cv = [], cp = [];
      for (i = 1; i <= 50; i++) { cb.push([i, Math.pow(10, lbinom(i))]); cv.push([i, Math.pow(2, i)]); cp.push([i, i * i * i]); }
      plot.poly(cp, "ln cm dash");
      plot.poly(cb, "ln c1");
      plot.poly(cv, "ln c3");
      plot.seg(m, 1, m, 1e30, "ln ck thin dot");
      plot.dot(m, Math.pow(10, lbinom(m)), 5, "f1");
      plot.dot(m, Math.pow(2, m), 5, "f3");
      plot.dot(m, m * m * m, 4, "fm");
      plot.text(50, Math.pow(10, lbinom(50)), "C(2m, m)", "tx-s t1", "end", -4, -8);
      plot.text(50, Math.pow(2, 50), "2ᵐ", "tx-s t3", "end", -4, -8);
      plot.text(50, 125000, "m³", "tx-s", "end", -4, -8);
      var lb = lbinom(m), sec = Math.pow(10, lb) / speed;
      var t = "m = " + m + ", n = 2m = " + 2 * m + " :\n";
      t += "  choix de m colonnes parmi n : C(" + 2 * m + ", " + m + ") " + count(lb, binomExact(m)) + "\n";
      t += "  bases inversibles = sommets du cube : 2" + sup(m) + " " + count(m * Math.log10(2), Math.pow(2, m)) + "\n";
      t += "  pour comparer, m³ = " + group(m * m * m) + "\n";
      t += "Examiner tous les choix à " + vSel.options[vSel.selectedIndex].text + " : " + duration(sec) + ".";
      ro.textContent = t;
    }
    draw(); redrawers.push(draw);
  };
