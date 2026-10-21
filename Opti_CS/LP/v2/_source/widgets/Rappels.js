// widgets/Rappels.js — interactive figures of the page Rappels.html.
// Inserted by build.mjs inside the scope of app.js: uses el, fmt, Plot, scaffold, slider, select, button, checkbox,
// readout, legend, addSvg, svgPoint, Fr, frMat, arrowMarker, drawArc, drawNode, and registers its widgets in WIDGETS.
// Own helpers are prefixed "rap".

  /* ---------------- small helpers ---------------- */
  function rapDec(x, d) { return fmt(x, d === undefined ? 2 : d).replace("-", "−").replace(".", ","); }
  var RAP_SUP = { "-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹" };
  function rapPow10(k) { return "10" + String(k).split("").map(function (ch) { return RAP_SUP[ch]; }).join(""); }
  // 1234567 -> "1,23·10⁶" ; small numbers written in full with thin spaces.
  function rapSci(x) {
    if (!isFinite(x)) return "∞";
    if (x < 1e7) return String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    var e = Math.floor(Math.log10(x)), m = x / Math.pow(10, e);
    if (m >= 9.995) { m /= 10; e += 1; }
    return rapDec(m, 2) + "·" + rapPow10(e);
  }
  function rapTime(sec) {
    if (sec < 1e-6) return rapDec(sec * 1e9, sec * 1e9 < 10 ? 1 : 0) + " ns";
    if (sec < 1e-3) return rapDec(sec * 1e6, sec * 1e6 < 10 ? 1 : 0) + " µs";
    if (sec < 1) return rapDec(sec * 1e3, sec * 1e3 < 10 ? 1 : 0) + " ms";
    if (sec < 60) return rapDec(sec, sec < 10 ? 1 : 0) + " s";
    if (sec < 3600) return rapDec(sec / 60, 0) + " min";
    if (sec < 86400) return rapDec(sec / 3600, 1) + " h";
    var year = 3.15576e7;
    if (sec < year) return rapDec(sec / 86400, 1) + " jours";
    var y = sec / year;
    return (y < 1e5 ? rapDec(y, y < 10 ? 1 : 0) : rapSci(y)) + " ans";
  }
  function rapText(g, x, y, s, cls, anchor) {
    var t = el("text", { x: x, y: y, "class": cls || "tx", "text-anchor": anchor || "start" }, g);
    t.textContent = s; return t;
  }

  /* =====================================================================================================
     1. Gauss–Jordan pivots, step by step (§1, systèmes)
     ===================================================================================================== */
  var RAP_GJ = {
    sys: { label: "système 3×3", M: [[1, 1, 1, 6], [2, 1, -1, 1], [1, -1, 2, 5]], names: ["x", "y", "z"], basis: [-1, -1, -1] },
    rang2: { label: "système de rang 2", M: [[1, 2, 1, 4], [2, 4, 0, 2], [3, 6, 1, 6]], names: ["x", "y", "z"], basis: [-1, -1, -1] },
    ex421: { label: "exercice 4.2.1 (forme standard)", M: [[-3, 2, 1, 0, 0, 2], [-1, 2, 0, 1, 0, 4], [1, 1, 0, 0, 1, 5]],
      names: ["x₁", "x₂", "x₃", "x₄", "x₅"], basis: [2, 3, 4], c: [-1, -2, 0, 0, 0] }
  };

  WIDGETS.rapGaussJordan = function (box) {
    var s = scaffold(box, "Élimination de Gauss–Jordan : un pivot à la fois (cliquez sur un coefficient)");
    var svg = s.svg;
    var sel = select(s.controls, "Matrice", [["sys", RAP_GJ.sys.label], ["rang2", RAP_GJ.rang2.label], ["ex421", RAP_GJ.ex421.label]], "sys", reset);
    button(s.controls, "Pivot suivant", autoPivot);
    button(s.controls, "Annuler", function () { if (hist.length) { var h = hist.pop(); T = h.T; basis = h.basis; pivots = h.pivots; last = h.last; msg = h.msg; draw(); } });
    button(s.controls, "Recommencer", reset);
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "colonnes de la base (identité)"], ["--s2", "dernier pivot"], ["--muted", "cliquez sur un coefficient non nul"]]);
    var D, T, basis, pivots, last, msg, hist;

    function copyT(A) { return A.map(function (r) { return r.slice(); }); }
    function reset() {
      D = RAP_GJ[sel.value];
      T = frMat(D.M); basis = D.basis.slice(); pivots = []; last = null; hist = [];
      msg = D.c ? "Base de départ évidente {x₃, x₄, x₅} : les colonnes des variables d'écart forment l'identité."
                : "Aucun pivot encore. Cliquez sur un coefficient non nul, ou sur « Pivot suivant ».";
      draw();
    }
    function nVar() { return T[0].length - 1; }
    function pivot(r, k) {
      var m = T.length, n1 = T[0].length, p = T[r][k], i, j, ops = [];
      if (p.isZero()) { msg = "Pivot nul en (L" + (r + 1) + ", " + D.names[k] + ") : impossible, on ne divise pas par 0."; draw(); return; }
      hist.push({ T: copyT(T), basis: basis.slice(), pivots: pivots.slice(), last: last, msg: msg });
      for (j = 0; j < n1; j++) T[r][j] = T[r][j].div(p);
      ops.push("L" + (r + 1) + " ← L" + (r + 1) + " / (" + p.str() + ")");
      for (i = 0; i < m; i++) if (i !== r && !T[i][k].isZero()) {
        var f = T[i][k];
        for (j = 0; j < n1; j++) T[i][j] = T[i][j].sub(f.mul(T[r][j]));
        ops.push("L" + (i + 1) + " ← L" + (i + 1) + " − (" + f.str() + ")·L" + (r + 1));
      }
      var out = basis[r];
      basis[r] = k; pivots.push(p); last = [r, k];
      msg = "Pivot " + p.str() + " en (L" + (r + 1) + ", " + D.names[k] + ") : " + ops.join(" ; ") + "." +
        (out >= 0 && out !== k ? "\n" + D.names[k] + " entre dans la base, " + D.names[out] + " en sort (c'est un pas du simplexe)." : "");
      draw();
    }
    function reduced() { // reduced costs and cost, when the basis is complete and the matrix has a cost vector
      if (!D.c || basis.indexOf(-1) >= 0) return null;
      var n = nVar(), red = [], j, i;
      for (j = 0; j < n; j++) {
        var z = Fr(0);
        for (i = 0; i < T.length; i++) z = z.add(Fr.of(D.c[basis[i]]).mul(T[i][j]));
        red.push(basis.indexOf(j) >= 0 ? Fr(0) : Fr.of(D.c[j]).sub(z));
      }
      var cost = Fr(0);
      for (i = 0; i < T.length; i++) cost = cost.add(Fr.of(D.c[basis[i]]).mul(T[i][n]));
      return { red: red, cost: cost };
    }
    function autoPivot() {
      var m = T.length, n = nVar(), r, k;
      var rc = reduced();
      if (rc) { // simplex rule: most negative reduced cost, then the ratio test
        var e = -1;
        for (k = 0; k < n; k++) if (rc.red[k].sign() < 0 && (e < 0 || rc.red[k].cmp(rc.red[e]) < 0)) e = k;
        if (e < 0) { msg = "Tous les coûts réduits sont ≥ 0 : la solution basique est optimale (partie 3). Plus de pivot à faire."; draw(); return; }
        var best = -1;
        for (r = 0; r < m; r++) if (T[r][e].sign() > 0) {
          var q = T[r][n].div(T[r][e]);
          if (best < 0 || q.cmp(T[best][n].div(T[best][e])) < 0) best = r;
        }
        if (best < 0) { msg = "Aucun coefficient positif dans la colonne " + D.names[e] + " : le problème est non borné."; draw(); return; }
        pivot(best, e);
        msg += "\nRègle du simplexe : " + D.names[e] + " a le coût réduit le plus négatif ; la ligne L" + (best + 1) + " a le plus petit rapport xB/colonne.";
        draw(); return;
      }
      for (r = 0; r < m; r++) if (basis[r] < 0) {
        for (k = 0; k < n; k++) if (basis.indexOf(k) < 0 && !T[r][k].isZero()) { pivot(r, k); return; }
      }
      msg = "Plus de pivot possible : chaque ligne a sa variable de base, ou les lignes restantes sont nulles à gauche.";
      draw();
    }
    function draw() {
      var m = T.length, n = nVar(), rc = reduced();
      var W = 600, cw = Math.min(78, (W - 110) / (n + 1)), rh = 40, x0 = (W - (90 + cw * (n + 1))) / 2 + 90, y0 = 34;
      var H = y0 + rh * m + (D.c ? rh + 10 : 0) + 12;
      svg.setAttribute("viewBox", "0 0 " + W + " " + H);
      svg.setAttribute("role", "img");
      svg.setAttribute("aria-label", "Tableau de la matrice augmentée");
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      var g = el("g", {}, svg), i, j;
      for (j = 0; j <= n; j++) rapText(g, x0 + cw * j + cw / 2, y0 - 12, j < n ? D.names[j] : "b", "tx-b", "middle");
      for (i = 0; i < m; i++) {
        var y = y0 + rh * i;
        rapText(g, x0 - 14, y + rh / 2 + 5, "L" + (i + 1) + (basis[i] >= 0 ? " : " + D.names[basis[i]] : ""), basis[i] >= 0 ? "tx-b t3" : "tx", "end");
        for (j = 0; j <= n; j++) {
          var isBasicCol = j < n && basis.indexOf(j) >= 0, isLast = last && last[0] === i && last[1] === j;
          var rect = el("rect", { x: x0 + cw * j + 2, y: y + 3, width: cw - 4, height: rh - 6, rx: 6,
            "class": isLast ? "f2" : (isBasicCol ? "a3" : "fs"), "fill-opacity": isLast ? 0.25 : null,
            style: j < n && !T[i][j].isZero() ? "cursor:pointer;stroke:var(--border)" : "stroke:var(--border)" }, g);
          var t = rapText(g, x0 + cw * j + cw / 2, y + rh / 2 + 5, T[i][j].str(), j === n ? "tx-b" : "tx", "middle");
          if (j < n) {
            (function (ii, jj) {
              var h = function () { pivot(ii, jj); };
              rect.addEventListener("click", h); t.addEventListener("click", h); t.style.cursor = "pointer";
            })(i, j);
          }
          if (j === n) {
            var neg = T[i][n].sign() < 0 && basis[i] >= 0 && basis.indexOf(-1) < 0;
            if (neg) t.setAttribute("class", "tx-b t6");
          }
        }
      }
      el("line", { x1: x0 + cw * n, x2: x0 + cw * n, y1: y0, y2: y0 + rh * m, "class": "ax" }, g);
      el("line", { x1: x0, x2: x0 + cw * (n + 1), y1: y0, y2: y0, "class": "ax" }, g);
      if (D.c) {
        var yc = y0 + rh * m + 10;
        rapText(g, x0 - 14, yc + rh / 2 + 5, "c̃", "tx-b t2", "end");
        for (j = 0; j < n; j++) {
          rapText(g, x0 + cw * j + cw / 2, yc + rh / 2 + 5, rc ? rc.red[j].str() : "—", rc && rc.red[j].sign() < 0 ? "tx-b t2" : "tx", "middle");
        }
        rapText(g, x0 + cw * n + cw / 2, yc + rh / 2 + 5, rc ? "c·x = " + rc.cost.str() : "", "tx-s t2", "middle");
        el("line", { x1: x0, x2: x0 + cw * (n + 1), y1: yc, y2: yc, "class": "gr" }, g);
      }
      // readout
      var lines = [msg];
      if (basis.indexOf(-1) < 0) {
        var x = [], prod = Fr(1);
        for (j = 0; j < n; j++) x.push(Fr(0));
        basis.forEach(function (col, r) { x[col] = T[r][n]; });
        pivots.forEach(function (p) { prod = prod.mul(p); });
        var negs = x.filter(function (v) { return v.sign() < 0; }).length;
        var zero = basis.some(function (col, r) { return T[r][n].isZero(); });
        lines.push((D.c ? "Solution basique : (" : "Solution : (" + D.names.join(", ") + ") = (") + x.map(function (v) { return v.str(); }).join(", ") + ")" +
          (D.c ? (negs ? " — non admissible (composante négative, en rose)" : (zero ? " — admissible, dégénérée" : " — admissible")) : ""));
        if (pivots.length) {
          var cols = basis.map(function (c) { return D.names[c]; }).join(", ");
          lines.push("Produit des pivots = " + prod.str() + " = déterminant des colonnes (" + cols + "), dans l'ordre des lignes" +
            (D.c && D.basis.indexOf(-1) < 0 ? " (la base de départ est l'identité, de déterminant 1)." : "."));
        }
        if (rc) {
          var neg = rc.red.filter(function (v) { return v.sign() < 0; }).length;
          lines.push("Coût c·x = " + rc.cost.str() + (neg ? " ; un coût réduit est négatif : on peut encore descendre." : " ; tous les coûts réduits sont ≥ 0 : optimum."));
        }
      } else {
        var zeroRows = [];
        for (i = 0; i < m; i++) if (basis[i] < 0 && T[i].slice(0, n).every(function (v) { return v.isZero(); }))
          zeroRows.push("L" + (i + 1) + (T[i][n].isZero() ? " : 0 = 0, équation redondante" : " : 0 = " + T[i][n].str() + ", système incompatible"));
        if (zeroRows.length) lines.push("Ligne nulle à gauche — " + zeroRows.join(" ; ") + ".");
      }
      ro.textContent = lines.join("\n");
    }
    reset();
  };

  /* =====================================================================================================
     2. A convex combination in the pentagon of Ex. 4.2.1 (§2, enveloppe convexe)
     ===================================================================================================== */
  var RAP_PENTA = [[0, 0], [5, 0], [2, 3], [1, 2.5], [0, 1]];

  WIDGETS.rapConvexe = function (box) {
    var s = scaffold(box, "Combinaison convexe de sommets : déplacez le point P");
    var p = new Plot(s.svg, { x: [-0.8, 6], y: [-0.8, 3.95], w: 560, h: 400, pad: { l: 36, r: 16, t: 16, b: 30 }, label: "Pentagone de l'exercice 4.2.1 et un point P" });
    var fanSel = select(s.controls, "Triangulation depuis", RAP_PENTA.map(function (v, i) { return [String(i), "V" + "₁₂₃₄₅"[i]]; }), "0", draw);
    var showC = checkbox(s.controls, "coût c", true, draw);
    var ang = slider(s.controls, "direction de c", 0, 355, 5, 245, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "pentagone"], ["--s3", "poids de P (épaisseur ∝ poids), meilleur sommet"], ["--s2", "coût c et ligne de niveau par P"], ["--s6", "poids négatif"]]);
    var P = [2, 2], dragging = false;
    var SUBS = "₁₂₃₄₅";

    function bary(Q, A, B, C) {
      var det = (B[0] - A[0]) * (C[1] - A[1]) - (C[0] - A[0]) * (B[1] - A[1]);
      var l2 = ((Q[0] - A[0]) * (C[1] - A[1]) - (C[0] - A[0]) * (Q[1] - A[1])) / det;
      var l3 = ((B[0] - A[0]) * (Q[1] - A[1]) - (Q[0] - A[0]) * (B[1] - A[1])) / det;
      return [1 - l2 - l3, l2, l3];
    }
    function setP(evt) {
      var pt = svgPoint(s.svg, evt);
      P = [Math.min(5.9, Math.max(-0.7, p.ix(pt.x))), Math.min(3.85, Math.max(-0.7, p.iy(pt.y)))];
      P = [Math.round(P[0] * 20) / 20, Math.round(P[1] * 20) / 20];
      draw();
    }
    s.svg.addEventListener("pointerdown", function (e) { dragging = true; s.svg.setPointerCapture(e.pointerId); setP(e); });
    s.svg.addEventListener("pointermove", function (e) { if (dragging) setP(e); });
    s.svg.addEventListener("pointerup", function () { dragging = false; });
    s.svg.addEventListener("pointercancel", function () { dragging = false; });

    function draw() {
      var st = parseInt(fanSel.value, 10), th = ang.get() * Math.PI / 180, c = [Math.cos(th), Math.sin(th)], i;
      ang.out.textContent = ang.get() + "°";
      p.clear();
      p.axes({ xticks: [0, 1, 2, 3, 4, 5], yticks: [0, 1, 2, 3], cross: true });
      p.poly(RAP_PENTA.concat([RAP_PENTA[0]]), "a1");
      p.poly(RAP_PENTA.concat([RAP_PENTA[0]]), "ln c1 thin");
      // triangles of the fan
      var tris = [];
      for (i = 1; i <= 3; i++) tris.push([st, (st + i) % 5, (st + i + 1) % 5]);
      tris.forEach(function (t) { p.seg(RAP_PENTA[t[0]][0], RAP_PENTA[t[0]][1], RAP_PENTA[t[2]][0], RAP_PENTA[t[2]][1], "ln cm hair dash"); });
      var bestT = 0, bestMin = -Infinity, W;
      tris.forEach(function (t, k) {
        var w = bary(P, RAP_PENTA[t[0]], RAP_PENTA[t[1]], RAP_PENTA[t[2]]), mn = Math.min(w[0], w[1], w[2]);
        if (mn > bestMin + 1e-12) { bestMin = mn; bestT = k; W = w; }
      });
      var T3 = tris[bestT], inside = bestMin >= -1e-9;
      p.poly([RAP_PENTA[T3[0]], RAP_PENTA[T3[1]], RAP_PENTA[T3[2]], RAP_PENTA[T3[0]]], inside ? "a3" : "am");
      // cost
      var vals = RAP_PENTA.map(function (v) { return c[0] * v[0] + c[1] * v[1]; });
      var imin = 0; vals.forEach(function (v, k) { if (v < vals[imin] - 1e-12) imin = k; });
      var cP = c[0] * P[0] + c[1] * P[1];
      if (showC.checked) {
        p.clip();
        var dir = [-c[1], c[0]];
        p.seg(P[0] - 9 * dir[0], P[1] - 9 * dir[1], P[0] + 9 * dir[0], P[1] + 9 * dir[1], "ln c2 thin dash");
        var V = RAP_PENTA[imin];
        p.seg(V[0] - 9 * dir[0], V[1] - 9 * dir[1], V[0] + 9 * dir[0], V[1] + 9 * dir[1], "ln c3 thin dash");
        p.unclip();
        var o = [5.3, 3.3], mk = arrowMarker(s.svg, "f2");
        p.seg(o[0], o[1], o[0] + 0.55 * c[0], o[1] + 0.55 * c[1], "ln c2", { "marker-end": mk });
        p.text(o[0], o[1], "c", "tx-b t2", "middle", 0, 18);
      }
      // weights: segments from P to the three vertices, width proportional to the weight
      T3.forEach(function (vi, k) {
        var w = W[k], V = RAP_PENTA[vi];
        p.seg(P[0], P[1], V[0], V[1], w >= -1e-9 ? "ln c3" : "ln c6", { style: "stroke-width:" + (1 + 7 * Math.min(1, Math.abs(w))).toFixed(1) + "px;stroke-opacity:0.75" });
      });
      RAP_PENTA.forEach(function (V, k) {
        var inT = T3.indexOf(k), w = inT >= 0 ? W[inT] : 0;
        p.dot(V[0], V[1], 5, k === imin && showC.checked ? "f3" : "fk");
        var dx = V[0] < 0.5 ? -8 : 8, an = V[0] < 0.5 ? "end" : "start";
        p.text(V[0], V[1], "V" + SUBS[k] + "  " + rapDec(w, 2), inT >= 0 ? (w < -1e-9 ? "tx-b t6" : "tx-b t3") : "tx-s", an, dx, V[1] < 0.5 ? 16 : -8);
      });
      p.dot(P[0], P[1], 7, inside ? "f2" : "f6").setAttribute("class", (inside ? "f2" : "f6") + " drag");
      p.text(P[0], P[1], "P", "tx-b", "start", 9, -9);
      var parts = T3.map(function (vi, k) { return rapDec(W[k], 2) + "·V" + SUBS[vi]; });
      var lines = ["P = (" + rapDec(P[0], 2) + " ; " + rapDec(P[1], 2) + ") = " + parts.join(" + ") + "   (somme des poids : " + rapDec(W[0] + W[1] + W[2], 2) + ")",
        inside ? "Les trois poids sont ≥ 0 : P est une combinaison convexe de trois sommets (Carathéodory, d + 1 = 3)."
               : "Un poids est négatif : P est hors du pentagone, ce n'est pas une combinaison convexe des sommets."];
      if (showC.checked) {
        lines.push("c = (" + rapDec(c[0], 2) + " ; " + rapDec(c[1], 2) + ") ;  c·V₁…c·V₅ = " + vals.map(function (v) { return rapDec(v, 2); }).join(" ; "));
        lines.push("c·P = " + rapDec(cP, 2) + " = Σ poids × c·Vᵢ" + (inside ? " ≥ min c·Vᵢ = " + rapDec(vals[imin], 2) + ", atteint en V" + SUBS[imin] + " (vert) : le minimum est en un sommet."
                                                                       : " ; P hors du pentagone, l'inégalité n'est plus garantie."));
      }
      ro.textContent = lines.join("\n");
    }
    draw();
  };

  /* =====================================================================================================
     3. Growth of n³, 2ⁿ, C(n, n/2), n! (§6)
     ===================================================================================================== */
  function rapBinom(n, k) { var r = 1; for (var i = 1; i <= k; i++) r = r * (n - k + i) / i; return Math.round(r); }
  function rapFact(n) { var r = 1; for (var i = 2; i <= n; i++) r *= i; return r; }
  var RAP_GROW = [
    { name: "n³", f: function (n) { return n * n * n; }, cls: "c3", t: "t3" },
    { name: "2ⁿ", f: function (n) { return Math.pow(2, n); }, cls: "c2", t: "t2" },
    { name: "C(n, n/2)", f: function (n) { return rapBinom(n, Math.floor(n / 2)); }, cls: "c5", t: "t5" },
    { name: "n!", f: rapFact, cls: "c6", t: "t6" }
  ];

  WIDGETS.rapCroissance = function (box) {
    var s = scaffold(box, "Croissance comparée : nombre d'opérations et temps de calcul");
    var p = new Plot(s.svg, { x: [1, 60], y: [1, 1e80], ylog: true, w: 600, h: 380, pad: { l: 52, r: 120, t: 16, b: 32 }, label: "Croissance de n³, 2ⁿ, C(n, n/2) et n!" });
    var nS = slider(s.controls, "n", 1, 60, 1, 30, draw);
    var fast = checkbox(s.controls, "machine 1000 fois plus rapide", false, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "n³"], ["--s2", "2ⁿ"], ["--s5", "C(n, n/2)"], ["--s6", "n!"], ["--muted", "opérations possibles en 1 s, 1 h, 1 an, l'âge de l'Univers"]]);
    var REFS = [["1 s", 1], ["1 h", 3600], ["1 an", 3.15576e7], ["âge de l'Univers", 4.355e17]];

    function nmax(f, budget) { var n = 1; while (n < 100000 && f(n + 1) <= budget) n++; return n; }
    function nmaxCube(budget) { var n = Math.floor(Math.cbrt(budget)); while ((n + 1) * (n + 1) * (n + 1) <= budget) n++; while (n * n * n > budget) n--; return n; }

    function draw() {
      var n = nS.get(), speed = fast.checked ? 1e12 : 1e9;
      nS.out.textContent = String(n);
      p.clear();
      p.axes({ xticks: [1, 10, 20, 30, 40, 50, 60], yticks: [1, 1e10, 1e20, 1e30, 1e40, 1e50, 1e60, 1e70, 1e80],
        yfmt: function (v) { return rapPow10(Math.round(Math.log10(v))); }, xlabel: "n" });
      REFS.forEach(function (r) {
        var y = r[1] * speed;
        p.seg(1, y, 60, y, "ln cm thin dash");
        p.text(60, y, r[0], "tx-s", "start", 6, 4);
      });
      p.clip();
      RAP_GROW.forEach(function (G) {
        var pts = [];
        for (var k = 1; k <= 60; k++) pts.push([k, G.f(k)]);
        p.poly(pts, "ln " + G.cls);
      });
      p.seg(n, 1, n, 1e80, "ln ck hair");
      RAP_GROW.forEach(function (G) { var v = G.f(n); if (v <= 1e80) p.dot(n, Math.max(1, v), 4.5, "f" + G.cls.slice(1)); });
      p.unclip();
      var hour = 3600 * speed;
      var lines = RAP_GROW.map(function (G) {
        var v = G.f(n);
        return G.name + " = " + rapSci(v) + " opérations : " + rapTime(v / speed);
      });
      lines.unshift("n = " + n + ", à " + (fast.checked ? "10¹²" : "10⁹") + " opérations par seconde :");
      lines.push("En une heure : n³ jusqu'à n = " + rapSci(nmaxCube(hour)) + " ; 2ⁿ jusqu'à " + nmax(RAP_GROW[1].f, hour) +
        " ; C(n, n/2) jusqu'à " + nmax(RAP_GROW[2].f, hour) + " ; n! jusqu'à " + nmax(rapFact, hour) + ".");
      ro.textContent = lines.join("\n");
    }
    draw();
  };

  /* =====================================================================================================
     4. Dijkstra, step by step (§5)
     ===================================================================================================== */
  var RAP_DIJ = {
    ex: { label: "exemple de la figure", nodes: ["s", "a", "b", "c", "d", "p"],
      pos: { s: [60, 150], a: [210, 60], b: [210, 240], c: [370, 60], d: [370, 240], p: [520, 150] },
      arcs: [["s", "a", 4, -12], ["s", "b", 1, 12], ["b", "a", 2, 12], ["a", "c", 1, -12], ["b", "c", 5, -12], ["b", "d", 8, 12], ["c", "d", 3, -12], ["c", "p", 6, -12], ["d", "p", 1, 12]],
      target: "p" },
    neg: { label: "un coût négatif", nodes: ["s", "a", "b"],
      pos: { s: [90, 150], a: [330, 60], b: [330, 240] },
      arcs: [["s", "a", 2, -12], ["s", "b", 3, 12], ["b", "a", -2, 12]], target: "a", truth: { s: 0, a: 1, b: 3 } }
  };

  WIDGETS.rapDijkstra = function (box) {
    var s = scaffold(box, "L'algorithme de Dijkstra, étape par étape");
    var svg = s.svg;
    svg.setAttribute("viewBox", "0 0 600 300");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Graphe orienté et étiquettes de Dijkstra");
    var sel = select(s.controls, "Graphe", [["ex", RAP_DIJ.ex.label], ["neg", RAP_DIJ.neg.label]], "ex", reset);
    button(s.controls, "Étape suivante", step);
    button(s.controls, "Recommencer", reset);
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "nœuds fixés, arcs des prédécesseurs"], ["--s2", "arcs relâchés à cette étape"], ["--s1", "nœuds non fixés"]]);
    var G, d, pred, fixed, lastNode, relaxed, msg, k;

    function reset() {
      G = RAP_DIJ[sel.value];
      d = {}; pred = {}; fixed = []; lastNode = null; relaxed = []; k = 0;
      G.nodes.forEach(function (v) { d[v] = Infinity; pred[v] = null; });
      d.s = 0;
      msg = "Initialisation : d(s) = 0, toutes les autres étiquettes valent ∞. Aucun nœud n'est fixé.";
      draw();
    }
    function lab(x) { return isFinite(x) ? String(x).replace("-", "−") : "∞"; }
    function step() {
      var cand = G.nodes.filter(function (v) { return fixed.indexOf(v) < 0 && isFinite(d[v]); });
      if (!cand.length) { msg = "Terminé : tous les nœuds accessibles sont fixés."; finish(); return; }
      var i = cand.reduce(function (a, b) { return d[b] < d[a] ? b : a; });
      fixed.push(i); lastNode = i; relaxed = []; k++;
      var upd = [];
      G.arcs.forEach(function (a) {
        if (a[0] !== i || fixed.indexOf(a[1]) >= 0) return;
        relaxed.push(a);
        var nd = d[i] + a[2];
        if (nd < d[a[1]]) { upd.push(a[1] + " : " + lab(d[a[1]]) + " → " + lab(nd)); d[a[1]] = nd; pred[a[1]] = i; }
      });
      msg = "Étape " + k + " : on fixe " + i + " (plus petite étiquette, d = " + lab(d[i]) + ")." +
        (relaxed.length ? " Arcs relâchés : " + relaxed.map(function (a) { return a[0] + "→" + a[1]; }).join(", ") + "." : " Aucun arc sortant vers un nœud non fixé.") +
        (upd.length ? "\nMises à jour : " + upd.join(" ; ") + "." : (relaxed.length ? "\nAucune étiquette ne baisse." : ""));
      if (fixed.length === G.nodes.length) finish(); else draw();
    }
    function finish() {
      var path = [G.target], v = G.target;
      while (pred[v]) { v = pred[v]; path.unshift(v); }
      msg += "\nTous les nœuds sont fixés. Chemin trouvé vers " + G.target + " : " + path.join(" → ") + ", coût " + lab(d[G.target]) + ".";
      if (G.truth) msg += "\nMais le chemin s → b → a coûte 3 + (−2) = 1 < 2 : Dijkstra se trompe, car un coût est négatif (la vraie distance de a est " + G.truth.a + ").";
      draw();
    }
    function draw() {
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      var g = el("g", {}, svg);
      var mk = { m: arrowMarker(svg, "fm"), g: arrowMarker(svg, "f3"), o: arrowMarker(svg, "f2") };
      G.arcs.forEach(function (a) {
        var isTree = pred[a[1]] === a[0] && fixed.indexOf(a[1]) >= 0, isRel = relaxed.indexOf(a) >= 0;
        var cls = isRel ? "ln c2" : (isTree ? "ln c3" : "ln cm thin");
        drawArc(g, G.pos[a[0]], G.pos[a[1]], { r: 18, cls: cls, marker: isRel ? mk.o : (isTree ? mk.g : mk.m),
          label: lab(a[2]), labelOffset: a[3], labelCls: isRel ? "tx-b t2" : "tx-b" });
      });
      G.nodes.forEach(function (v) {
        var P = G.pos[v], isFixed = fixed.indexOf(v) >= 0;
        drawNode(g, P, v, { r: 17, cls: isFixed ? "f3" : "f1" });
        if (v === lastNode) el("circle", { cx: P[0], cy: P[1], r: 22, "class": "ln c3 thin nofill" }, g);
        var dy = P[1] < 150 ? -28 : (P[1] > 150 ? 38 : -28);
        rapText(g, P[0], P[1] + dy, "d = " + lab(d[v]), isFixed ? "tx-b t3" : "tx-b", "middle");
      });
      ro.textContent = msg;
    }
    reset();
  };
