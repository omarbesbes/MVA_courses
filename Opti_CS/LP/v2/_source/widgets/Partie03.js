// widgets/Partie03.js — interactive figures of Partie 3 (l'algorithme du simplexe).
// Inserted by build.mjs inside the scope of app.js: uses el, Plot, scaffold, slider, select, button, readout, legend,
// fmt, Fr, frVec, basicSolution, simplex, halfPlanePolygon, lineInBox, arrowMarker, combinations, redrawers.
// Every number quoted in the "À observer" paragraphs of the page was recomputed by verify_P03/v13_widgets.py.

  /* ---------------- helpers of this page (prefixed p3) ---------------- */
  var P3_SUB = "₀₁₂₃₄₅₆₇₈₉";
  function p3sub(n) { return String(n).split("").map(function (d) { return P3_SUB[+d]; }).join(""); }
  function p3name(j, nx, art) { return j < nx ? "x" + p3sub(j + 1) : (art || "y") + p3sub(j - nx + 1); }
  function p3set(cols, nx) {
    return "{" + cols.slice().sort(function (a, b) { return a - b; }).map(function (j) { return p3name(j, nx); }).join(", ") + "}";
  }
  function p3pt(x) { return "(" + x[0].str() + " ; " + x[1].str() + ")"; }
  function p3vec(v) { return "(" + v.map(function (q) { return q === null ? "—" : q.str(); }).join(", ") + ")"; }
  function p3f(x, d) { return fmt(x, d).replace(".", ",").replace("-", "−"); }
  function p3par(q) { var t = q.str(); return t.indexOf("/") >= 0 ? "(" + t + ")" : t; }
  // The polygon {a·x ≤ r for the rows of A restricted to the first two columns} ∩ {x ≥ 0} ∩ box.
  function p3polygon(A, b, box) {
    var cons = A.map(function (row, i) { return [row[0], row[1], Fr.of(b[i]).val()]; });
    cons.push([-1, 0, 0], [0, -1, 0]);
    return halfPlanePolygon(cons, box);
  }
  // An SVG text with subscripts: parts = [[text, isSub], …] (no Unicode subscript exists for B).
  function p3subText(g, x, y, parts, cls, anchor) {
    var t = el("text", { x: x, y: y, "class": cls || "tx-s", "text-anchor": anchor || "start" }, g);
    parts.forEach(function (pp) {
      var sp = el("tspan", pp[1] ? { "baseline-shift": "sub", "font-size": "75%" } : {}, t); sp.textContent = pp[0];
    });
    return t;
  }
  function p3closed(P) { return P.length ? P.concat([P[0]]) : P; }
  // Draws the constraint lines a x1 + b x2 = r (grey) with the label "x_k = 0" of their slack variable.
  function p3lines(plot, A, b, box, slackOf) {
    A.forEach(function (row, i) {
      var r = Fr.of(b[i]).val(), seg = lineInBox(row[0], row[1], r, box);
      if (!seg) return;
      plot.seg(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln cm hair");
      var lab = slackOf ? slackOf(i) : null;
      if (!lab) return;
      var p;
      if (row[0] > 0 && row[1] > 0) { var yl = box[2] + 0.45; p = [(r - row[1] * yl) / row[0], yl]; plot.text(p[0], p[1], lab, "tx-s", "start", 6, 0); }
      else { var yt = box[3] - 0.2; p = [(r - row[1] * yt) / row[0], yt]; if (!isFinite(p[0])) p = [box[1] - 0.6, r / row[1]]; plot.text(p[0], p[1], lab, "tx-s", "start", 6, 4); }
    });
  }
  // An arrow between two data points of a Plot.
  function p3arrow(plot, p, q, cls, marker, shorten) {
    var x1 = plot.tx(p[0]), y1 = plot.ty(p[1]), x2 = plot.tx(q[0]), y2 = plot.ty(q[1]);
    var L = Math.hypot(x2 - x1, y2 - y1);
    if (L < 1e-6) return null;
    var sh = shorten === undefined ? 6 : shorten;
    return el("line", { x1: x1 + (x2 - x1) / L * 3, y1: y1 + (y2 - y1) / L * 3, x2: x2 - (x2 - x1) / L * sh, y2: y2 - (y2 - y1) / L * sh, "class": cls, "marker-end": marker }, plot.g);
  }
  // Edge direction, in the plane (x1, x2), when the non-basic variable j enters: d = (−B⁻¹a_j on the basis, e_j).
  function p3edge(step, j) {
    var d = [0, 0];
    [0, 1].forEach(function (k) {
      if (j === k) d[k] = 1;
      else { var r = step.basis.indexOf(k); if (r >= 0) d[k] = -step.T[r][j].val(); }
    });
    return d;
  }
  var P3_TINT = { enter: "background: color-mix(in srgb, var(--s2) 16%, transparent)", leave: "background: color-mix(in srgb, var(--s6) 16%, transparent)",
    piv: "background: color-mix(in srgb, var(--s3) 28%, transparent); font-weight: 700; outline: 2px solid var(--s3); outline-offset: -2px" };
  // The simplex tableau of a step as an HTML table: B⁻¹A | B⁻¹b, the reduced-cost row and −c·x, the ratios.
  function p3tableau(div, step, names) {
    var e = step.entering, lr = step.leaving, n = step.reduced.length;
    var h = "<table style='font-family: var(--font-mono); font-size: 0.82rem; text-align: right; width: auto; min-width: 100%'><thead><tr><th>base</th>";
    for (var j = 0; j < n; j++) h += "<th style='text-align:right" + (j === e ? "; " + P3_TINT.enter : "") + "'>" + names[j] + "</th>";
    h += "<th style='text-align:right'>x<sub>B</sub></th><th style='text-align:right'>rapport</th></tr></thead><tbody>";
    step.basis.forEach(function (col, r) {
      h += "<tr" + (r === lr ? " style='" + P3_TINT.leave + "'" : "") + "><th>" + names[col] + "</th>";
      for (var j = 0; j < n; j++) {
        var st = r === lr && j === e ? P3_TINT.piv : j === e ? P3_TINT.enter : "";
        h += "<td" + (st ? " style='" + st + "'" : "") + ">" + step.T[r][j].str() + "</td>";
      }
      var q = step.ratios ? step.ratios[r] : null;
      h += "<td>" + step.xB[r].str() + "</td><td>" + (step.ratios ? (q === null ? "—" : q.str()) : "") + "</td></tr>";
    });
    h += "<tr><th>c̃</th>";
    for (j = 0; j < n; j++) h += "<td style='color: var(--s2)" + (j === e ? "; " + P3_TINT.enter : "") + "'>" + step.reduced[j].str() + "</td>";
    h += "<td>" + step.cost.neg().str() + "</td><td></td></tr></tbody></table>";
    div.innerHTML = h;
  }

  /* --- 1. The simplex step by step on the polygon of Ex. 4.2.1 (§3) --- */
  WIDGETS.p3simplexe = function (box) {
    var s = scaffold(box, "Le simplexe pas à pas sur l'exercice 4.2.1 (forme standard, x₃, x₄, x₅ = variables d'écart)");
    var BOX = [-0.5, 7.5, -0.4, 3.73];
    var plot = new Plot(s.svg, { x: [BOX[0], BOX[1]], y: [BOX[2], BOX[3]], w: 680, h: 380, pad: { l: 40, r: 22, t: 24, b: 38 }, label: "Le polygone de l'exercice 4.2.1, le chemin du simplexe et les arêtes du sommet courant" });
    var COSTS = { a: [-1, -2], b: [-1, -1], c: [0, -1], d: [1, -1], e: [1, 2] };
    var cSel = select(s.controls, "Coût", [["a", "c = (−1, −2) : max x₁ + 2x₂ (ex. 4.2.1)"], ["b", "c = (−1, −1)"], ["c", "c = (0, −1)"], ["d", "c = (1, −1)"], ["e", "c = (1, 2) : ex. 4.2.3 tel qu'imprimé"]], "a", reset);
    var rSel = select(s.controls, "Règle", [["dantzig", "plus négatif (Dantzig)"], ["bland", "plus petit indice (Bland)"]], "dantzig", reset);
    var bSel = select(s.controls, "b₃", [["5", "5"], ["3.5", "7/2 (sommet dégénéré)"]], "5", reset);
    button(s.controls, "Itération suivante", function () { if (k < run.steps.length - 1) { k++; draw(); } });
    button(s.controls, "Tout dérouler", function () { k = run.steps.length - 1; draw(); });
    button(s.controls, "Recommencer", function () { k = 0; draw(); });
    var ro = readout(s.controls);
    var tw = document.createElement("div"); tw.className = "table-wrap"; box.appendChild(tw);
    legend(s.legend, [["--s1", "ensemble admissible"], ["--s3", "chemin du simplexe"], ["--s2", "arête qui descend (c̃ < 0) ; ligne de niveau"], ["--muted", "arête qui monte"]]);
    var A = [[-3, 2, 1, 0, 0], [-1, 2, 0, 1, 0], [1, 1, 0, 0, 1]], NAMES = ["x₁", "x₂", "x₃", "x₄", "x₅"];
    var run, k = 0, b, c;
    function reset() {
      b = [2, 4, Fr.of(parseFloat(bSel.value))];
      c = COSTS[cSel.value].concat([0, 0, 0]);
      run = simplex(A, b, c, [2, 3, 4], { rule: rSel.value });
      k = 0; draw();
    }
    function draw() {
      plot.clear();
      var mk3 = arrowMarker(s.svg, "f3"), mk2 = arrowMarker(s.svg, "f2"), mkm = arrowMarker(s.svg, "fm");
      plot.axes({ xticks: [0, 1, 2, 3, 4, 5], yticks: [0, 1, 2, 3], nogrid: true, xlabel: "x₁", ylabel: "x₂" });
      var P = p3polygon(A, b, BOX);
      plot.poly(p3closed(P), "a1"); plot.poly(p3closed(P), "ln c1 thin");
      p3lines(plot, A, b, BOX, function (i) { return "x" + p3sub(i + 3) + " = 0"; });
      var st = run.steps[k], x = st.x, xp = [x[0].val(), x[1].val()];
      // level line of the cost through the current vertex
      var lv = lineInBox(c[0], c[1], st.cost.val(), BOX);
      if (lv) plot.seg(lv[0][0], lv[0][1], lv[1][0], lv[1][1], "ln c2 hair dash");
      // path
      for (var i = 0; i < k; i++) {
        var p = run.steps[i].x, q = run.steps[i + 1].x;
        p3arrow(plot, [p[0].val(), p[1].val()], [q[0].val(), q[1].val()], "ln c3", mk3, 8);
      }
      for (i = 0; i <= k; i++) plot.dot(run.steps[i].x[0].val(), run.steps[i].x[1].val(), 4.5, "f3");
      // edges leaving the current vertex, one per non-basic variable
      for (var j = 0; j < 5; j++) {
        if (st.basis.indexOf(j) >= 0) continue;
        var d = p3edge(st, j), L = Math.hypot(d[0], d[1]);
        if (L < 1e-12) continue;
        var tip = [xp[0] + 0.75 * d[0] / L, xp[1] + 0.75 * d[1] / L], neg = st.reduced[j].sign() < 0;
        var a = p3arrow(plot, xp, tip, "ln " + (neg ? "c2" : "cm") + (j === st.entering ? "" : " thin"), neg ? mk2 : mkm, 4);
        plot.text(tip[0], tip[1], "c̃" + p3sub(j + 1) + " = " + st.reduced[j].str(), "tx-s " + (neg ? "t2" : ""), d[0] >= -0.2 ? "start" : "end", d[0] >= -0.2 ? 5 : -5, d[1] > 0.3 ? -4 : 12);
      }
      // preview of the next vertex
      if (st.entering >= 0 && k + 1 < run.steps.length) {
        var nx = run.steps[k + 1].x;
        plot.seg(xp[0], xp[1], nx[0].val(), nx[1].val(), "ln c3 dash thin");
        plot.dot(nx[0].val(), nx[1].val(), 6, "ln c3 thin nofill");
      }
      plot.dot(xp[0], xp[1], 7, "f3");
      plot.text(5.7, 3.35, "itération " + k, "tx-b");
      plot.text(5.7, 3.0, "x = " + p3pt(x), "tx-s");
      plot.text(5.7, 2.7, "coût c·x = " + st.cost.str(), "tx-s t2");
      plot.text(5.7, 2.4, "base " + p3set(st.basis, 5), "tx-s");
      p3tableau(tw, st, NAMES);
      // the text
      var txt = "Itération " + k + " : sommet (x₁ ; x₂) = " + p3pt(x) + ", base " + p3set(st.basis, 5) + ", coût c·x = " + st.cost.str() + ".\n";
      var red = []; for (j = 0; j < 5; j++) if (st.basis.indexOf(j) < 0) red.push("c̃" + p3sub(j + 1) + " = " + st.reduced[j].str());
      txt += "Coûts réduits hors base : " + red.join(", ") + ".\n";
      if (st.entering < 0) {
        txt += run.status === "optimal" ? "Tous les coûts réduits sont ≥ 0 : ce sommet est optimal (valeur " + st.cost.str() + ")." : "Arrêt.";
        var zero = []; for (j = 0; j < 5; j++) if (st.basis.indexOf(j) < 0 && st.reduced[j].isZero()) zero.push(NAMES[j]);
        if (zero.length) txt += "\nc̃ = 0 pour " + zero.join(", ") + " : le long de cette arête le coût ne change pas ; si l'arête n'est pas réduite à un point, l'optimum n'est pas unique.";
      } else {
        var e = st.entering, nm = NAMES[e];
        txt += nm + " entre (" + (rSel.value === "bland" ? "plus petit indice de coût réduit < 0" : "coût réduit le plus négatif") + "). Direction d = B⁻¹a" + p3sub(e + 1) + " = " + p3vec(st.dir) + ".\n";
        if (st.leaving < 0) txt += "Aucun dᵣ > 0 : on peut avancer indéfiniment, le minimum vaut −∞.";
        else {
          var rr = st.basis.map(function (col, r) { return NAMES[col] + " : " + (st.ratios[r] === null ? "—" : p3par(st.xB[r]) + "/" + p3par(st.dir[r]) + " = " + st.ratios[r].str()); });
          txt += "Rapports x_B/d sur d > 0 : " + rr.join(" ; ") + " → ε = " + st.eps.str() + ", " + NAMES[st.basis[st.leaving]] + " sort.\n";
          txt += st.eps.isZero() ? "Pas nul (ε = 0) : la base change mais le point ne bouge pas — pivot dégénéré." : "Le coût va baisser de ε·|c̃| = " + st.eps.mul(st.reduced[e].neg()).str() + ".";
        }
      }
      ro.textContent = txt;
    }
    reset(); redrawers.push(draw);
  };

  /* --- 2. The ratio test: walk along an edge and see which basic variable stops you (§3) --- */
  WIDGETS.p3rapport = function (box) {
    var s = scaffold(box, "Le test du rapport : on avance x(ε) le long d'une arête jusqu'à ce qu'une variable de base s'annule");
    var BOX = [-0.5, 5.6, -0.4, 4.28];
    var plot = new Plot(s.svg, { x: [BOX[0], BOX[1]], y: [BOX[2], BOX[3]], w: 680, h: 330, pad: { l: 40, r: 282, t: 20, b: 34 }, label: "À gauche le polygone et le point x(epsilon), à droite les valeurs des variables de base" });
    var VARS = { a: { A: [[-3, 2, 1, 0, 0], [-1, 2, 0, 1, 0], [1, 1, 0, 0, 1]], b: [2, 4, 5] }, u: { A: [[-3, 2, 1, 0], [-1, 2, 0, 1]], b: [2, 4] } };
    var vSel = select(s.controls, "Polygone", [["a", "ex. 4.2.1"], ["u", "sans x₁ + x₂ ≤ 5 (non borné)"]], "a", function () { setVariant(); });
    var vxSel = select(s.controls, "Sommet de départ", [["0", "—"]], "0", function () { setVertex(); });
    var eSel = select(s.controls, "Variable entrante", [["0", "—"]], "0", function () { setEntering(); });
    var eps = slider(s.controls, "ε", 0, 1, 0.005, 0, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "ensemble admissible"], ["--s3", "x(ε) admissible"], ["--s6", "x(ε) hors de l'ensemble admissible"], ["--s2", "arête suivie"]]);
    var V, verts, cur, st, ent, dir, ratios, epsK, epsMax;
    function setVariant() {
      V = VARS[vSel.value];
      var m = V.A.length, n = V.A[0].length;
      verts = combinations(n, m).map(function (cols) { return { cols: cols, sol: basicSolution(V.A, V.b, cols) }; })
        .filter(function (v) { return v.sol.x && (v.sol.status === "admissible" || v.sol.status === "dégénérée"); });
      verts.sort(function (u, v) { return u.sol.x[0].cmp(v.sol.x[0]) || u.sol.x[1].cmp(v.sol.x[1]); });
      vxSel.innerHTML = "";
      verts.forEach(function (v, i) { var o = document.createElement("option"); o.value = i; o.textContent = p3pt(v.sol.x) + " — base " + p3set(v.cols, n); vxSel.appendChild(o); });
      vxSel.value = verts.length > 1 ? "1" : "0";
      setVertex();
    }
    function setVertex() {
      cur = verts[parseInt(vxSel.value, 10)];
      var n = V.A[0].length, c = [-1, -2]; while (c.length < n) c.push(0);
      st = simplex(V.A, V.b, c, cur.cols, { maxIter: 0 }).steps[0];
      eSel.innerHTML = "";
      for (var j = 0; j < n; j++) if (st.basis.indexOf(j) < 0) {
        var o = document.createElement("option"); o.value = j; o.textContent = "x" + p3sub(j + 1) + " (c̃" + p3sub(j + 1) + " = " + st.reduced[j].str() + ")"; eSel.appendChild(o);
      }
      setEntering();
    }
    function setEntering() {
      ent = parseInt(eSel.value, 10);
      dir = st.T.map(function (r) { return r[ent]; });
      ratios = dir.map(function (d, r) { return d.sign() > 0 ? st.xB[r].div(d) : null; });
      epsK = null; ratios.forEach(function (q) { if (q !== null && (epsK === null || q.cmp(epsK) < 0)) epsK = q; });
      epsMax = epsK === null ? 4 : Math.max(0.5, 1.6 * epsK.val());
      eps.input.max = epsMax; eps.input.step = epsMax / 400; eps.set(epsK === null ? 1 : epsK.val() / 2);
      draw();
    }
    function draw() {
      var e = eps.get(), n = V.A[0].length, m = V.A.length;
      eps.out.textContent = p3f(e, 3);
      plot.clear();
      var mk2 = arrowMarker(s.svg, "f2");
      plot.axes({ xticks: [0, 1, 2, 3, 4, 5], yticks: [0, 1, 2, 3, 4], nogrid: true, xlabel: "x₁", ylabel: "x₂" });
      var P = p3polygon(V.A, V.b, BOX);
      plot.poly(p3closed(P), "a1"); plot.poly(p3closed(P), "ln c1 thin");
      p3lines(plot, V.A, V.b, BOX, function (i) { return "x" + p3sub(i + 3) + " = 0"; });
      verts.forEach(function (v) { plot.dot(v.sol.x[0].val(), v.sol.x[1].val(), 3.5, "fm"); });
      var x0 = [cur.sol.x[0].val(), cur.sol.x[1].val()], d = p3edge(st, ent);
      // the edge line (to the end of the box), the blocking point
      var far = 30, end = [x0[0] + far * d[0], x0[1] + far * d[1]];
      plot.clip(); plot.seg(x0[0], x0[1], end[0], end[1], "ln c2 hair dash"); plot.unclip();
      if (epsK !== null) {
        var pk = [x0[0] + epsK.val() * d[0], x0[1] + epsK.val() * d[1]];
        p3arrow(plot, x0, pk, "ln c2", mk2, 7);
        plot.dot(pk[0], pk[1], 6, "ln c3 thin nofill");
      } else {
        p3arrow(plot, x0, [x0[0] + 1.2 * d[0] / Math.hypot(d[0], d[1]), x0[1] + 1.2 * d[1] / Math.hypot(d[0], d[1])], "ln c2", mk2, 4);
      }
      var xe = [x0[0] + e * d[0], x0[1] + e * d[1]];
      var vals = st.xB.map(function (v, r) { return v.val() - e * dir[r].val(); });
      var ok = vals.every(function (v) { return v >= -1e-9; });
      plot.dot(x0[0], x0[1], 5, "f3");
      plot.clip(); plot.dot(xe[0], xe[1], 7, ok ? "f3" : "f6"); plot.unclip();
      // bars of the basic variables
      var g = el("g", {}, s.svg), X0 = 430, W = 230, Y0 = 158, H = 100;
      var vmax = 0.5; st.xB.forEach(function (v, r) { vmax = Math.max(vmax, Math.abs(v.val()), Math.abs(v.val() - epsMax * dir[r].val())); });
      p3subText(g, X0 + W / 2, 28, [["variables de base x", 0], ["B", 1], ["(ε) = x", 0], ["B", 1], [" − ε d", 0]], "tx-b", "middle");
      el("line", { x1: X0, x2: X0 + W, y1: Y0, y2: Y0, "class": "ax" }, g);
      var bw = W / m;
      vals.forEach(function (v, r) {
        var h = v / vmax * H, cx = X0 + bw * (r + 0.5);
        el("rect", { x: cx - bw * 0.28, y: h >= 0 ? Y0 - h : Y0, width: bw * 0.56, height: Math.max(Math.abs(h), 0.5), "class": v >= -1e-9 ? "f1" : "f6", "fill-opacity": 0.8 }, g);
        var blocking = epsK !== null && ratios[r] !== null && ratios[r].cmp(epsK) === 0;
        if (blocking) el("rect", { x: cx - bw * 0.4, y: Y0 - H - 22, width: bw * 0.8, height: 2 * H + 84, rx: 6, "class": "ln c3 thin nofill" }, g);
        var lab = el("text", { x: cx, y: Y0 + H + 26, "class": "tx-b", "text-anchor": "middle" }, g); lab.textContent = "x" + p3sub(st.basis[r] + 1);
        var val = el("text", { x: cx, y: h >= 0 ? Y0 - h - 6 : Y0 - h + 14, "class": "tx-s", "text-anchor": "middle" }, g); val.textContent = p3f(v, 2);
        var dd = el("text", { x: cx, y: Y0 + H + 42, "class": "tx-s", "text-anchor": "middle" }, g); dd.textContent = "d = " + dir[r].str();
        var rq = el("text", { x: cx, y: Y0 + H + 56, "class": "tx-s", "text-anchor": "middle" }, g); rq.textContent = ratios[r] !== null ? "rapport " + ratios[r].str() : "pas de rapport";
      });
      // text
      var cost = st.cost.val() + e * st.reduced[ent].val();
      var txt = "Départ " + p3pt(cur.sol.x) + ", base " + p3set(st.basis, n) + " ; x" + p3sub(ent + 1) + " entre, c̃" + p3sub(ent + 1) + " = " + st.reduced[ent].str() + " (coût −x₁ − 2x₂).\n";
      txt += "d = B⁻¹a" + p3sub(ent + 1) + " = " + p3vec(dir) + " ; x_B(ε) = x_B − ε d = " + p3vec(st.xB) + " − ε " + p3vec(dir) + ".\n";
      if (epsK === null) txt += "Aucune composante de d n'est > 0 : aucune variable de base ne s'annule, on avance indéfiniment ; le coût c·x(ε) = " + st.cost.str() + " + ε·(" + st.reduced[ent].str() + ") tend vers " + (st.reduced[ent].sign() < 0 ? "−∞." : "+∞ (cette arête monte).");
      else {
        var who = []; ratios.forEach(function (q, r) { if (q !== null && q.cmp(epsK) === 0) who.push("x" + p3sub(st.basis[r] + 1)); });
        txt += "Rapports sur d > 0 : " + st.basis.map(function (col, r) { return "x" + p3sub(col + 1) + " " + (ratios[r] === null ? "—" : ratios[r].str()); }).join(", ") + " → ε_max = " + epsK.str() + " (" + who.join(" et ") + " s'annule" + (who.length > 1 ? "nt" : "") + ").";
      }
      txt += "\nε = " + p3f(e, 3) + " : x(ε) = (" + p3f(xe[0], 2) + " ; " + p3f(xe[1], 2) + "), " + (ok ? "admissible" : "NON admissible") + ", coût " + p3f(cost, 2) + ".";
      ro.textContent = txt;
    }
    setVariant(); redrawers.push(draw);
  };

  /* --- 3. Phase I on a small example, then phase II (§5) --- */
  WIDGETS.p3phase1 = function (box) {
    var s = scaffold(box, "Phase I puis phase II : d'abord annuler les variables artificielles, ensuite optimiser");
    var BOX = [-0.5, 5.2, -0.4, 3.8];
    var plot = new Plot(s.svg, { x: [BOX[0], BOX[1]], y: [BOX[2], BOX[3]], w: 680, h: 330, pad: { l: 40, r: 200, t: 20, b: 34 }, label: "Le plan (x1, x2), l'ensemble admissible et les itérés des phases I et II" });
    // constraints written a·x ≤ r for the drawing; standard form rows (with slacks) for the simplex
    var EX = {
      ok: { draw: [[-1, -1, -2], [1, -1, 1], [0, 1, 3]], A: [[-1, -1, 1, 0, 0], [1, -1, 0, 1, 0], [0, 1, 0, 0, 1]], b: [-2, 1, 3], c: [2, 1, 0, 0, 0],
        txt: "x₁ + x₂ ≥ 2, x₁ − x₂ ≤ 1, x₂ ≤ 3 ; min 2x₁ + x₂" },
      vide: { draw: [[-1, -1, -2], [1, 1, 1]], A: [[-1, -1, 1, 0], [1, 1, 0, 1]], b: [-2, 1], c: [2, 1, 0, 0], txt: "x₁ + x₂ ≥ 2, x₁ + x₂ ≤ 1 ; min 2x₁ + x₂" }
    };
    var exSel = select(s.controls, "Exemple", [["ok", "réalisable"], ["vide", "X_ad vide"]], "ok", reset);
    button(s.controls, "Pas suivant", function () { if (k < all.length - 1) { k++; draw(); } });
    button(s.controls, "Recommencer", function () { k = 0; draw(); });
    var ro = readout(s.controls);
    var tw = document.createElement("div"); tw.className = "table-wrap"; box.appendChild(tw);
    legend(s.legend, [["--s1", "ensemble admissible du vrai problème"], ["--s6", "phase I : y ≠ 0"], ["--s3", "y = 0 : point admissible, puis phase II"]]);
    var E, all, k, nx, m, flipped;
    function reset() {
      E = EX[exSel.value]; m = E.A.length; nx = E.A[0].length;
      // rows with b_i < 0 are multiplied by −1, then one artificial variable per row
      flipped = [];
      var At = E.A.map(function (row, i) { var f = E.b[i] < 0; flipped.push(f); return row.map(function (v) { return f ? -v : v; }); });
      var bt = E.b.map(function (v) { return Math.abs(v); });
      var Ab = At.map(function (row, i) { return row.concat(At.map(function (r2, k2) { return k2 === i ? 1 : 0; })); });
      var cI = []; for (var j = 0; j < nx; j++) cI.push(0); for (j = 0; j < m; j++) cI.push(1);
      var bas = []; for (j = 0; j < m; j++) bas.push(nx + j);
      var r1 = simplex(Ab, bt, cI, bas);
      all = r1.steps.map(function (st) { return { phase: "I", st: st }; });
      var last = r1.steps[r1.steps.length - 1];
      E.status1 = r1.status; E.value1 = last.cost;
      if (last.cost.isZero() && last.basis.every(function (col) { return col < nx; })) {
        var r2 = simplex(At, bt, E.c, last.basis);
        r2.steps.forEach(function (st) { all.push({ phase: "II", st: st }); });
        E.status2 = r2.status;
      }
      k = 0; draw();
    }
    function draw() {
      plot.clear();
      var mk = arrowMarker(s.svg, "fm");
      plot.axes({ xticks: [0, 1, 2, 3, 4, 5], yticks: [0, 1, 2, 3], nogrid: true, xlabel: "x₁", ylabel: "x₂" });
      var cons = E.draw.map(function (r) { return r.slice(); }); cons.push([-1, 0, 0], [0, -1, 0]);
      var P = halfPlanePolygon(cons, BOX);
      if (P.length) { plot.poly(p3closed(P), "a1"); plot.poly(p3closed(P), "ln c1 thin"); }
      E.draw.forEach(function (r) { var seg = lineInBox(r[0], r[1], r[2], BOX); if (seg) plot.seg(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln cm hair"); });
      if (!P.length) {
        plot.text(2.6, 2.6, "x₁ + x₂ ≥ 2", "tx-s", "start"); plot.text(0.05, 0.35, "x₁ + x₂ ≤ 1", "tx-s", "start");
        plot.text(2.2, 3.4, "aucun point commun : X_ad = ∅", "tx-s t6", "middle");
      }
      for (var i = 0; i < k; i++) {
        var p = all[i].st.x, q = all[i + 1].st.x;
        p3arrow(plot, [p[0].val(), p[1].val()], [q[0].val(), q[1].val()], "ln cm thin", mk, 7);
      }
      function yOf(st) { return st.x.slice(nx); }
      for (i = 0; i <= k; i++) {
        var st = all[i].st, yz = all[i].phase === "II" || yOf(st).every(function (v) { return v.isZero(); });
        plot.dot(st.x[0].val(), st.x[1].val(), i === k ? 7 : 4.5, yz ? "f3" : "f6");
      }
      // side panel
      var cur = all[k], stc = cur.st;
      var g = el("g", {}, s.svg), X0 = 498;
      function t(y, str, cls) { var tx = el("text", { x: X0, y: y, "class": cls || "tx-s" }, g); tx.textContent = str; }
      t(34, "phase " + cur.phase + ", pas " + k, "tx-b");
      t(56, "x = " + p3pt(stc.x));
      if (cur.phase === "I") {
        t(74, "y = " + p3vec(yOf(stc)));
        t(92, "Σ yᵢ = " + stc.cost.str(), "tx-s t6");
      } else t(74, "coût 2x₁ + x₂ = " + stc.cost.str(), "tx-s t2");
      var names = []; for (var j = 0; j < nx + (cur.phase === "I" ? m : 0); j++) names.push(p3name(j, nx));
      var bnames = "{" + stc.basis.slice().sort(function (a, b) { return a - b; }).map(function (j2) { return p3name(j2, nx); }).join(", ") + "}";
      t(120, "base " + bnames);
      p3tableau(tw, stc, names);
      // text
      var txt = E.txt + (flipped.some(Boolean) ? " — en forme standard, les lignes où bᵢ < 0 ont été multipliées par −1 ; une variable artificielle yᵢ par ligne.\n" : "\n");
      if (cur.phase === "I") {
        txt += "Phase I : min Σ yᵢ. ";
        if (stc.entering >= 0) txt += p3name(stc.entering, nx) + " entre (c̃ = " + stc.reduced[stc.entering].str() + "), rapports " + p3vec(stc.ratios) + " → " + p3name(stc.basis[stc.leaving], nx) + " sort, ε = " + stc.eps.str() + ".";
        else if (stc.cost.isZero()) txt += "Optimum de la phase I de valeur 0 : y = 0, la base " + bnames + " est une base admissible du vrai problème. Pas suivant : phase II avec le vrai coût.";
        else txt += "Optimum de la phase I de valeur Σ yᵢ = " + stc.cost.str() + " > 0 : aucun point ne vérifie Ax = b, x ≥ 0. X_ad est vide, on s'arrête.";
      } else {
        txt += "Phase II : min 2x₁ + x₂ depuis la base trouvée. ";
        if (stc.entering >= 0) txt += p3name(stc.entering, nx) + " entre (c̃ = " + stc.reduced[stc.entering].str() + "), rapports " + p3vec(stc.ratios) + " → " + p3name(stc.basis[stc.leaving], nx) + " sort, ε = " + stc.eps.str() + ".";
        else txt += "Coûts réduits ≥ 0 : optimum " + p3pt(stc.x) + ", valeur " + stc.cost.str() + ".";
      }
      ro.textContent = txt;
    }
    reset(); redrawers.push(draw);
  };

  /* --- 4. Degenerate pivots and cycling: Beale's example (§4) --- */
  WIDGETS.p3cyclage = function (box) {
    var s = scaffold(box, "L'exemple de Beale : des pivots dégénérés qui tournent en rond (et la règle de Bland qui en sort)");
    s.svg.setAttribute("viewBox", "0 0 680 330"); s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Le graphe des bases visitées par le simplexe sur l'exemple de Beale");
    var A = [[1, 0, 0, Fr(1, 4), -8, -1, 9], [0, 1, 0, Fr(1, 2), -12, Fr(-1, 2), 3], [0, 0, 1, 0, 0, 1, 0]], b = [0, 0, 1];
    var c = [0, 0, 0, Fr(-3, 4), 20, Fr(-1, 2), 6], NAMES = ["x₁", "x₂", "x₃", "x₄", "x₅", "x₆", "x₇"];
    var rSel = select(s.controls, "Règle", [["dantzig", "plus négatif (Dantzig)"], ["bland", "plus petit indice (Bland)"]], "dantzig", reset);
    button(s.controls, "Pivot suivant", function () { if (k < run.steps.length - 1) { k++; draw(); } });
    button(s.controls, "Recommencer", function () { k = 0; draw(); });
    var ro = readout(s.controls);
    var tw = document.createElement("div"); tw.className = "table-wrap"; box.appendChild(tw);
    legend(s.legend, [["--s3", "pivots déjà faits"], ["--muted", "autres pivots possibles des deux règles"], ["--s2", "base courante"]]);
    // the bases met by the two rules, and where to draw them
    var cx = 190, cy = 168, R = 118, POS = {}, KEYS = ["1,2,3", "2,3,4", "3,4,5", "3,5,6", "3,6,7", "1,3,7"];
    KEYS.forEach(function (key, i) { var a = (-150 + 60 * i) * Math.PI / 180; POS[key] = [cx + R * Math.cos(a), cy + R * Math.sin(a)]; });
    POS["1,3,6"] = [420, POS["3,5,6"][1]]; POS["1,2,6"] = [530, POS["3,5,6"][1] - 70]; POS["1,4,6"] = [610, POS["3,5,6"][1]];
    function keyOf(basis) { return basis.map(function (j) { return j + 1; }).sort(function (u, v) { return u - v; }).join(","); }
    var EDGES = [["1,2,3", "2,3,4"], ["2,3,4", "3,4,5"], ["3,4,5", "3,5,6"], ["3,5,6", "3,6,7"], ["3,6,7", "1,3,7"], ["1,3,7", "1,2,3"], ["3,5,6", "1,3,6"], ["1,3,6", "1,2,6"], ["1,2,6", "1,4,6"]];
    var run, k;
    function reset() { run = simplex(A, b, c, [0, 1, 2], { rule: rSel.value, maxIter: 18 }); k = 0; draw(); }
    function draw() {
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var mkm = arrowMarker(s.svg, "fm"), mk3 = arrowMarker(s.svg, "f3");
      var g = el("g", {}, s.svg), done = {};
      for (var i = 0; i < k; i++) done[keyOf(run.steps[i].basis) + ">" + keyOf(run.steps[i + 1].basis)] = run.steps[i].eps;
      EDGES.forEach(function (ed) {
        var p = POS[ed[0]], q = POS[ed[1]], dx = q[0] - p[0], dy = q[1] - p[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L;
        var on = done[ed[0] + ">" + ed[1]] !== undefined;
        el("line", { x1: p[0] + ux * 40, y1: p[1] + uy * 17, x2: q[0] - ux * 42, y2: q[1] - uy * 19, "class": on ? "ln c3" : "ln cm thin", "marker-end": on ? mk3 : mkm }, g);
      });
      var stc = run.steps[k], curKey = keyOf(stc.basis);
      Object.keys(POS).forEach(function (key) {
        var p = POS[key], isCur = key === curKey;
        el("rect", { x: p[0] - 40, y: p[1] - 15, width: 80, height: 30, rx: 9, "class": isCur ? "a2" : "am" }, g);
        el("rect", { x: p[0] - 40, y: p[1] - 15, width: 80, height: 30, rx: 9, "class": isCur ? "ln c2" : "ln cm hair", fill: "none" }, g);
        var tx = el("text", { x: p[0], y: p[1] + 4.5, "class": isCur ? "tx-b" : "tx-s", "text-anchor": "middle" }, g);
        tx.textContent = "{" + key.split(",").map(function (j) { return "x" + p3sub(j); }).join(", ") + "}";
      });
      function lab(x, y, str, cls, anc) { var t = el("text", { x: x, y: y, "class": cls || "tx-s", "text-anchor": anc || "middle" }, g); t.textContent = str; }
      lab(cx, cy - 6, "6 bases, un seul point", "tx-s");
      lab(cx, cy + 10, "x = (0, 0, 1, 0, 0, 0, 0)", "tx-s");
      lab(cx, cy + 26, "coût 0, tous les pas ε = 0", "tx-s t6");
      lab(POS["1,2,6"][0], POS["1,2,6"][1] - 22, "coût −1/2", "tx-s t3");
      lab(POS["1,4,6"][0], POS["1,4,6"][1] + 30, "coût −5/4 : optimal", "tx-s t3");
      lab(POS["1,3,6"][0] + 45, POS["1,3,6"][1] + 30, "ε = 0", "tx-s");
      lab((POS["1,3,6"][0] + POS["1,2,6"][0]) / 2 - 18, (POS["1,3,6"][1] + POS["1,2,6"][1]) / 2 - 6, "ε = 1/2", "tx-s");
      lab((POS["1,2,6"][0] + POS["1,4,6"][0]) / 2 + 22, (POS["1,2,6"][1] + POS["1,4,6"][1]) / 2 - 6, "ε = 1", "tx-s");
      lab(470, 300, "Bland quitte le cycle au 4ᵉ pivot (x₁ entre au lieu de x₇).", "tx-s");
      p3tableau(tw, stc, NAMES);
      var red = []; for (var j = 0; j < 7; j++) if (stc.basis.indexOf(j) < 0) red.push("c̃" + p3sub(j + 1) + " = " + stc.reduced[j].str());
      var txt = "Après " + k + " pivot" + (k > 1 ? "s" : "") + " : base " + p3set(stc.basis, 7) + ", x = " + p3vec(stc.x) + ", coût " + stc.cost.str() + ".\nCoûts réduits : " + red.join(", ") + ".\n";
      if (stc.entering < 0) txt += "Tous ≥ 0 : optimum atteint en " + k + " pivots.";
      else {
        txt += NAMES[stc.entering] + " entre ; rapports " + p3vec(stc.ratios) + " → " + NAMES[stc.basis[stc.leaving]] + " sort, ε = " + stc.eps.str() + (stc.eps.isZero() ? " : pivot dégénéré, le point ne bouge pas." : " : le point bouge, le coût baisse de " + stc.eps.mul(stc.reduced[stc.entering].neg()).str() + ".");
      }
      if (rSel.value === "dantzig" && k > 0 && k % 6 === 0) txt += "\nRetour à la base de départ après " + k + " pivots : le simplexe cycle et ne s'arrêtera jamais.";
      ro.textContent = txt;
    }
    reset(); redrawers.push(draw);
  };
