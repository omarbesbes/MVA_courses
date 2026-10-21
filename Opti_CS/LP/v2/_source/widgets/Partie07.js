// widgets/Partie07.js — figures interactives de la partie 7 (flots, transport, affectation).
// Inséré par build.mjs dans la portée de app.js : utilise el, fmt, frac, scaffold, select, button, checkbox, slider,
// readout, legend, drawArc, drawNode, simplex, hungarian, mulberry32, et enregistre ses widgets dans WIDGETS.
// Toutes les données (graphe de la diapo 26, capacités, coûts, constructeur automobile, matrice 4 x 4) sont celles
// des scripts de vérification de la page.

  /* ---------------- données communes : le graphe de la diapo 26 ---------------- */
  var P7G = {
    nodes: ["s", "1", "2", "3", "4", "p"],
    arcs: [["s", "1"], ["s", "3"], ["1", "2"], ["1", "3"], ["2", "1"], ["2", "3"],
           ["2", "4"], ["2", "p"], ["3", "2"], ["3", "4"], ["4", "2"], ["4", "p"]],
    pos: { s: [70, 170], "1": [215, 70], "3": [215, 270], "2": [445, 70], "4": [445, 270], p: [590, 170] },
    bend: [-0.12, 0.12, -0.09, 0.0, -0.09, 0.07, -0.12, -0.1, 0.07, -0.05, -0.12, 0.1],
    U: [5, 4, 2, 3, 1, 1, 3, 4, 2, 3, 1, 5],
    C: [2, 5, 6, 2, 1, 1, 3, 7, 2, 6, 1, 2],
    flow5: [3, 2, 2, 1, 0, 0, 0, 3, 1, 2, 0, 2]
  };
  var P7OFF = [11, 11, 11, 13, 11, 12, 13, 11, 12, 11, 13, 11];   // décalage des étiquettes (comme figures_P07.py)
  function p7num(x, d) { return fmt(x, d === undefined ? 2 : d).replace(".", ","); }
  function p7sign(v) { return (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v); }
  function p7arcName(a) { return "(" + a[0] + "," + a[1] + ")"; }
  // Pointe de flèche de taille fixe (indépendante de l'épaisseur du trait).
  function p7marker(svg, cls) {
    var defs = svg.querySelector("defs") || el("defs", {}, svg);
    var id = "p7mk-" + cls + "-" + Math.random().toString(36).slice(2, 8);
    var mk = el("marker", { id: id, viewBox: "0 0 10 10", refX: 9, refY: 5, markerUnits: "userSpaceOnUse", markerWidth: 11, markerHeight: 11, orient: "auto-start-reverse" }, defs);
    el("path", { d: "M0,0 L10,5 L0,10 z", "class": cls }, mk);
    return "url(#" + id + ")";
  }
  function p7clear(svg) { while (svg.firstChild) svg.removeChild(svg.firstChild); }
  // Une zone cliquable large le long d'un arc.
  function p7hit(g, l, P, onClick) {
    var a = P7G.arcs[l];
    var h = drawArc(g, P[a[0]], P[a[1]], { bend: P7G.bend[l], cls: "p7hit", r: 18, style: "stroke:transparent;stroke-width:16px;pointer-events:stroke;cursor:pointer" });
    h.path.addEventListener("click", function (e) { onClick(l, e); });
    return h;
  }

  /* --- 1. La loi de Kirchhoff, nœud par nœud (§2) --- */
  WIDGETS.p7kirchhoff = function (box) {
    var s = scaffold(box, "Loi de Kirchhoff : cliquez (ou touchez) un arc pour y ajouter une unité de flot");
    var W = 680, H = 340, G = P7G;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Le graphe de la diapo 26 avec un flot réglable sur chaque arc et le bilan de chaque nœud");
    var PRE = {
      sp5: { b: [5, 0, 0, 0, 0, -5], x: G.flow5 },
      mix: { b: [4, 0, 0, 1, 0, -5], x: [3, 1, 2, 1, 0, 0, 0, 3, 1, 2, 0, 2] },
      bad: { b: [5, 0, 0, 0, 0, -4], x: null }
    };
    var x = G.flow5.slice(), msg = "";
    var bSel = select(s.controls, "Flots extérieurs", [["sp5", "bₛ = +5, bₚ = −5"], ["mix", "bₛ = +4, b₃ = +1, bₚ = −5"], ["bad", "bₛ = +5, bₚ = −4 (somme ≠ 0)"]], "sp5", function () { x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; msg = ""; draw(); });
    button(s.controls, "Un flot qui convient", function () {
      var pr = PRE[bSel.value];
      if (pr.x) { x = pr.x.slice(); msg = ""; } else { msg = "Aucun flot ne convient : la somme des bᵢ n'est pas nulle (voir la dernière ligne)."; }
      draw();
    });
    button(s.controls, "Tout à zéro", function () { x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; msg = ""; draw(); });
    var minus = checkbox(s.controls, "retirer une unité (−1)", false, function () {});
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "arc portant du flot"], ["--muted", "arc vide"], ["--s6", "nœud où Kirchhoff est violée"]]);

    function draw() {
      var b = PRE[bSel.value].b, P = G.pos, i, l;
      var inn = [0, 0, 0, 0, 0, 0], out = [0, 0, 0, 0, 0, 0];
      G.arcs.forEach(function (a, k) { out[G.nodes.indexOf(a[0])] += x[k]; inn[G.nodes.indexOf(a[1])] += x[k]; });
      p7clear(s.svg);
      var g = el("g", {}, s.svg);
      var m3 = p7marker(s.svg, "f3"), mm = p7marker(s.svg, "fm"), m2 = p7marker(s.svg, "f2");
      for (l = 0; l < G.arcs.length; l++) {
        var a = G.arcs[l], v = x[l];
        if (v > 0) drawArc(g, P[a[0]], P[a[1]], { bend: G.bend[l], cls: "ln c3", r: 18, marker: m3, label: String(v), labelCls: "tx-b t3", labelOffset: P7OFF[l] + 1, style: "stroke-width:" + (1.4 + 0.7 * Math.min(v, 6)).toFixed(1) + "px" });
        else drawArc(g, P[a[0]], P[a[1]], { bend: G.bend[l], cls: "ln cm thin dash", r: 18, marker: mm, label: "0", labelCls: "tx-s", labelOffset: P7OFF[l] });
      }
      for (l = 0; l < G.arcs.length; l++) p7hit(g, l, P, function (k, e) {
        var d = (minus.checked || e.shiftKey) ? -1 : 1;
        x[k] = Math.max(0, Math.min(9, x[k] + d)); msg = ""; draw();
      });
      // flots extérieurs
      var dirs = { s: [-46, -40], p: [46, -40], "3": [-50, 26], "1": [-46, -30], "2": [46, -30], "4": [50, 26] };
      G.nodes.forEach(function (v, k) {
        if (!b[k]) return;
        var q = P[v], d = dirs[v], L = Math.hypot(d[0], d[1]);
        var far = [q[0] + d[0], q[1] + d[1]], near = [q[0] + d[0] / L * 19, q[1] + d[1] / L * 19];
        var ln = b[k] > 0 ? { x1: far[0], y1: far[1], x2: near[0], y2: near[1] } : { x1: near[0], y1: near[1], x2: far[0], y2: far[1] };
        ln["class"] = "ln c2 thin"; ln["marker-end"] = m2;
        el("line", ln, g);
        var t = el("text", { x: far[0] + (d[0] < 0 ? -4 : 4), y: far[1] - 5, "class": "tx-b t2", "text-anchor": d[0] < 0 ? "end" : "start" }, g);
        t.textContent = "b" + ({ s: "ₛ", p: "ₚ", "1": "₁", "2": "₂", "3": "₃", "4": "₄" })[v] + " = " + p7sign(b[k]);
      });
      // nœuds et bilans
      var lines = [], allOk = true, sumD = 0;
      G.nodes.forEach(function (v, k) {
        var dlt = b[k] + inn[k] - out[k];
        sumD += dlt;
        if (dlt !== 0) allOk = false;
        drawNode(g, P[v], v, { cls: dlt === 0 ? "f3" : "f6", r: 18 });
        var up = (v === "1" || v === "2");
        var t = el("text", { x: P[v][0], y: P[v][1] + (up ? -27 : 36), "class": dlt === 0 ? "tx-s" : "tx-b t6", "text-anchor": "middle" }, g);
        t.textContent = p7sign(b[k] || 0).replace(/^$/, "0") + " + " + inn[k] + " − " + out[k] + " = " + p7sign(dlt).replace(/^$/, "0");
        lines.push("Nœud " + v + " : b = " + (p7sign(b[k]) || "0") + ", entre " + inn[k] + ", sort " + out[k] + "  →  b + entre − sort = " + (p7sign(dlt) || "0") + (dlt === 0 ? "  ✓" : "  ✗"));
      });
      var sumB = b.reduce(function (u, v) { return u + v; }, 0);
      var Ax = G.nodes.map(function (v, k) { return out[k] - inn[k]; });
      var txt = (msg ? msg + "\n" : "") + lines.join("\n");
      txt += "\nAx = (" + Ax.map(function (v) { return p7sign(v) || "0"; }).join(", ") + ")   b = (" + b.map(function (v) { return p7sign(v) || "0"; }).join(", ") + ")";
      txt += "\nSomme des six bilans = " + (p7sign(sumD) || "0") + " = Σ bᵢ, quel que soit le flot (chaque arc compte une fois en « entre » et une fois en « sort »).";
      if (sumB !== 0) txt += "\nΣ bᵢ = " + p7sign(sumB) + " ≠ 0 : au moins un nœud reste toujours déséquilibré, aucun flot n'existe.";
      else txt += allOk ? "\nKirchhoff est vérifiée partout (et x ≥ 0) : c'est un flot. Ax = b." : "\nKirchhoff n'est pas vérifiée partout : ce n'est pas (encore) un flot.";
      ro.textContent = txt;
    }
    draw(); redrawers.push(draw);
  };

  /* --- 2. Le constructeur automobile par le simplexe (§4) --- */
  WIDGETS.p7transport = function (box) {
    var s = scaffold(box, "Le constructeur automobile résolu par le simplexe du cours, une itération à la fois");
    var W = 680, H = 350;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Graphe biparti usines vers concessionnaires avec la base courante du simplexe");
    var NAMES = ["U1C1", "U1C2", "U1C3", "U2C1", "U2C2", "U2C3"];
    var ARC = [["U1", "C1"], ["U1", "C2"], ["U1", "C3"], ["U2", "C1"], ["U2", "C2"], ["U2", "C3"]];
    var cost = [8, 15, 0, 10, 4, 0];
    var A = [[1, 1, 1, 0, 0, 0], [0, 0, 0, 1, 1, 1], [-1, 0, 0, -1, 0, 0], [0, -1, 0, 0, -1, 0]]; // ligne de C3 supprimée
    var bv = [100, 80, -80, -75];
    var BASES = [
      ["nw", "nord-ouest : U1C1, U1C2, U2C2, U2C3", [0, 1, 4, 5]],
      ["b2", "U1C1, U1C2, U2C1, U2C3", [0, 1, 3, 5]],
      ["b3", "U1C1, U1C2, U1C3, U2C1 (dégénérée)", [0, 1, 2, 3]],
      ["b4", "U1C1, U1C3, U2C1, U2C2", [0, 2, 3, 4]],
      ["b5", "U1C2, U1C3, U2C1, U2C3 (dégénérée)", [1, 2, 3, 5]],
      ["b6", "U1C2, U1C3, U2C1, U2C2 (dégénérée)", [1, 2, 3, 4]],
      ["b7", "U1C1, U1C3, U2C2, U2C3", [0, 2, 4, 5]]
    ];
    var P = { U1: [130, 110], U2: [130, 260], C1: [450, 70], C2: [450, 185], C3: [450, 300] };
    var bNode = { U1: 100, U2: 80, C1: -80, C2: -75, C3: -25 };
    var res = null, k = 0;
    var bSel = select(s.controls, "Base de départ", BASES.map(function (t) { return [t[0], t[1]]; }), "nw", restart);
    bSel.style.maxWidth = "16rem";
    button(s.controls, "Itération suivante", function () { if (res && k < res.steps.length - 1) { k++; draw(); } });
    button(s.controls, "Recommencer", restart);
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "arc de base (flot)"], ["--muted", "arc hors base (coût réduit)"], ["--s2", "arc entrant"]]);
    function restart() {
      var B = BASES.filter(function (t) { return t[0] === bSel.value; })[0][2];
      res = simplex(A, bv, cost, B, { rule: "dantzig" }); k = 0; draw();
    }
    function potentials(basis) {
      var p = { C3: Fr(0) }, changed = true;
      while (changed) {
        changed = false;
        basis.forEach(function (j) {
          var i0 = ARC[j][0], j0 = ARC[j][1];
          if (p[i0] && !p[j0]) { p[j0] = p[i0].sub(cost[j]); changed = true; }
          else if (p[j0] && !p[i0]) { p[i0] = p[j0].add(cost[j]); changed = true; }
        });
      }
      return p;
    }
    function draw() {
      var st = res.steps[k], j;
      var inB = function (jj) { return st.basis.indexOf(jj) >= 0; };
      var pot = potentials(st.basis);
      var delta = {};
      if (st.entering >= 0) {
        delta[st.entering] = "+ε";
        st.basis.forEach(function (jj, r) { var d = st.dir[r].sign(); if (d > 0) delta[jj] = "−ε"; else if (d < 0) delta[jj] = "+ε"; });
      }
      p7clear(s.svg);
      var g = el("g", {}, s.svg);
      var m3 = p7marker(s.svg, "f3"), mm = p7marker(s.svg, "fm"), m2 = p7marker(s.svg, "f2");
      var labels = [];
      for (j = 0; j < 6; j++) {
        var a = ARC[j], xv = st.x[j].val(), cls, mk, lab, lcls;
        if (j === st.entering) { cls = "ln c2"; mk = m2; lab = "entre : c̃ = " + st.reduced[j].str(); lcls = "tx-b t2"; }
        else if (inB(j)) { cls = "ln c3"; mk = m3; lab = "x = " + st.x[j].str(); lcls = "tx-b t3"; }
        else { cls = "ln cm thin dash"; mk = mm; lab = "c̃ = " + st.reduced[j].str(); lcls = st.reduced[j].sign() < 0 ? "tx-b t2" : "tx-s"; }
        var sty = inB(j) ? "stroke-width:" + (1.6 + xv / 25).toFixed(1) + "px" : (j === st.entering ? "stroke-width:3px;stroke-dasharray:7 5" : "");
        drawArc(g, P[a[0]], P[a[1]], { cls: cls, r: 20, marker: mk, style: sty });
        if (delta[j]) lab += "  (" + delta[j] + ")";
        if (st.leaving >= 0 && st.basis[st.leaving] === j) lab += " sort";
        var t = 0.68;
        labels.push([P[a[0]][0] + t * (P[a[1]][0] - P[a[0]][0]), P[a[0]][1] + t * (P[a[1]][1] - P[a[0]][1]), lab, lcls]);
      }
      labels.forEach(function (L) {
        var w = 7 + 6.1 * L[2].length;
        el("rect", { x: L[0] - w / 2, y: L[1] - 10, width: w, height: 16, rx: 3, "class": "lbl-bg" }, g);
        var tt = el("text", { x: L[0], y: L[1] + 3, "class": L[3], "text-anchor": "middle" }, g); tt.textContent = L[2];
      });
      Object.keys(P).forEach(function (v) {
        drawNode(g, P[v], v, { cls: v[0] === "U" ? "f1" : (v === "C3" ? "fm" : "f5"), r: 20 });
        var left = v[0] === "U";
        var t1 = el("text", { x: P[v][0] + (left ? -28 : 28), y: P[v][1] - 2, "class": left ? "tx-b t1" : "tx-b t5", "text-anchor": left ? "end" : "start" }, g);
        t1.textContent = "b = " + p7sign(bNode[v]);
        var t2 = el("text", { x: P[v][0] + (left ? -28 : 28), y: P[v][1] + 14, "class": "tx-s", "text-anchor": left ? "end" : "start" }, g);
        t2.textContent = "p = " + pot[v].str() + (v === "C3" ? " (fixé)" : "");
      });
      var tt2 = el("text", { x: W / 2 - 50, y: H - 6, "class": "tx-s", "text-anchor": "middle" }, g);
      tt2.textContent = "itération " + k + " sur " + (res.steps.length - 1) + " ; coût " + st.cost.str() + " (centaines d'euros)";
      // texte
      var txt = "Itération " + k + " — base : " + st.basis.map(function (jj) { return NAMES[jj]; }).join(", ") +
        " ; x = (" + st.x.map(function (v) { return v.str(); }).join(", ") + ") ; coût " + st.cost.str() + ".";
      txt += "\nPotentiels (pᵢ − pⱼ = cᵢⱼ sur les arcs de base, p = 0 en C3) : " + Object.keys(P).map(function (v) { return v + " = " + pot[v].str(); }).join(", ") + ".";
      var hb = [];
      for (j = 0; j < 6; j++) if (!inB(j)) hb.push(NAMES[j] + " : " + st.reduced[j].str());
      if (st.entering < 0) {
        txt += "\nCoûts réduits hors base : " + hb.join(", ") + ". Tous ≥ 0 : la base est optimale.";
        txt += "\nOptimum : coût " + st.cost.str() + " centaines d'euros, soit " + (st.cost.val() * 100).toLocaleString("fr-FR") + " €. Solution entière, comme promis par le Th. 4.3.7.";
      } else {
        txt += "\nCoûts réduits hors base : " + hb.join(", ") + " → entre " + NAMES[st.entering] + " (le plus négatif).";
        var cyc = [];
        Object.keys(delta).forEach(function (jj) { cyc.push(NAMES[jj] + " " + delta[jj]); });
        txt += "\nCycle créé par l'arc entrant : " + cyc.join(", ") + ".";
        var rat = [];
        st.basis.forEach(function (jj, r) { if (st.ratios[r]) rat.push(NAMES[jj] + " : " + st.ratios[r].str()); });
        txt += "\nRapports xᵢ / dᵢ : " + rat.join(", ") + " → sort " + NAMES[st.basis[st.leaving]] + ", ε = " + st.eps.str() +
          (st.eps.isZero() ? " (pas dégénéré : le flot ne bouge pas, seule la base change)." : " ; le coût baisse de " + st.reduced[st.entering].neg().str() + " × " + st.eps.str() + " = " + st.reduced[st.entering].neg().mul(st.eps).str() + ".");
      }
      ro.textContent = txt;
    }
    restart(); redrawers.push(draw);
  };

  /* --- 3. Le flot maximal par chemins augmentants, et la coupe minimale (§5) --- */
  function p7augment(U, x, mode) {
    var G = P7G, nodes = G.nodes, s = "s", p = "p", out = {};
    nodes.forEach(function (v) { out[v] = []; });
    G.arcs.forEach(function (a, l) { out[a[0]].push([a[1], l, 1]); });
    G.arcs.forEach(function (a, l) { out[a[1]].push([a[0], l, -1]); });
    function cap(l, d) { return d > 0 ? U[l] - x[l] : x[l]; }
    var prev = {}; prev[s] = null;
    if (mode === "bfs") {
      var q = [s];
      while (q.length) {
        var v = q.shift();
        if (v === p) break;
        out[v].forEach(function (e) { if (!(e[0] in prev) && cap(e[1], e[2]) > 0) { prev[e[0]] = [v, e[1], e[2]]; q.push(e[0]); } });
      }
    } else {
      (function dfs(v) {
        if (v === p) return true;
        for (var i = 0; i < out[v].length; i++) {
          var e = out[v][i];
          if (!(e[0] in prev) && cap(e[1], e[2]) > 0) { prev[e[0]] = [v, e[1], e[2]]; if (dfs(e[0])) return true; }
        }
        return false;
      })(s);
    }
    if (!(p in prev)) return { path: null, reach: Object.keys(prev) };
    var path = [], w = p;
    while (prev[w] !== null) { path.push([prev[w][1], prev[w][2], prev[w][0], w]); w = prev[w][0]; }
    path.reverse();
    return { path: path, reach: Object.keys(prev) };
  }
  function p7fordFulkerson(U, mode) {
    var x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], steps = [];
    for (var it = 0; it < 200; it++) {
      var r = p7augment(U, x, mode);
      if (!r.path) return { steps: steps, x: x, S: r.reach };
      var th = Infinity;
      r.path.forEach(function (e) { th = Math.min(th, e[1] > 0 ? U[e[0]] - x[e[0]] : x[e[0]]); });
      var caps = r.path.map(function (e) { return e[1] > 0 ? U[e[0]] - x[e[0]] : x[e[0]]; });
      r.path.forEach(function (e) { x[e[0]] += th * e[1]; });
      steps.push({ path: r.path, theta: th, caps: caps, x: x.slice() });
    }
    return { steps: steps, x: x, S: [] };
  }
  WIDGETS.p7flotmax = function (box) {
    var s = scaffold(box, "Flot maximal de s à p par chemins augmentants, puis la coupe minimale qui le certifie");
    var W = 680, H = 350, G = P7G;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Le graphe de la diapo 26 avec capacités, flot courant et chemin augmentant");
    var U = G.U.slice(), res = null, k = 0;
    var mSel = select(s.controls, "Chemin choisi", [["bfs", "le plus court (Edmonds–Karp)"], ["dfs", "le premier trouvé en profondeur"]], "bfs", restart);
    button(s.controls, "Chemin augmentant suivant", function () { if (k <= res.steps.length) { k++; draw(); } });
    button(s.controls, "Recommencer", restart);
    button(s.controls, "Capacités de la page", function () { U = G.U.slice(); restart(); });
    var minus = checkbox(s.controls, "clic sur un arc : capacité −1", false, function () {});
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "chemin augmentant de l'étape"], ["--s1", "arc portant du flot"], ["--s2", "arc saturé"], ["--muted", "arc vide"]]);
    function restart() { res = p7fordFulkerson(U, mSel.value); k = 0; draw(); }
    function value(x) { return x[0] + x[1]; }
    function draw() {
      var K = res.steps.length, x = k === 0 ? [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] : res.steps[Math.min(k, K) - 1].x;
      var showCut = k > K, P = G.pos, l;
      var S = showCut ? res.S : [];
      var path = (k >= 1 && k <= K) ? res.steps[k - 1].path : [];
      var onPath = {};
      path.forEach(function (e) { onPath[e[0]] = e[1]; });
      p7clear(s.svg);
      var g = el("g", {}, s.svg);
      var m1 = p7marker(s.svg, "f1"), m2 = p7marker(s.svg, "f2"), mm = p7marker(s.svg, "fm");
      if (showCut) {
        el("rect", { x: 22, y: 34, width: 268, height: 278, rx: 16, "class": "a3" }, g);
        var tS = el("text", { x: 34, y: 54, "class": "tx-b t3" }, g); tS.textContent = "S = {" + S.join(", ") + "}";
      }
      for (l = 0; l < 12; l++) if (l in onPath) {
        var a0 = G.arcs[l];
        drawArc(g, P[a0[0]], P[a0[1]], { bend: G.bend[l], cls: "ln c3", r: 18, style: "stroke-width:11px;stroke-opacity:0.3" });
      }
      for (l = 0; l < 12; l++) {
        var a = G.arcs[l], lab = x[l] + "/" + U[l];
        if (U[l] > 0 && x[l] === U[l]) drawArc(g, P[a[0]], P[a[1]], { bend: G.bend[l], cls: "ln c2", r: 18, marker: m2, label: lab, labelCls: "tx-b t2", labelOffset: P7OFF[l] + 2, style: "stroke-width:3px" });
        else if (x[l] > 0) drawArc(g, P[a[0]], P[a[1]], { bend: G.bend[l], cls: "ln c1", r: 18, marker: m1, label: lab, labelCls: "tx-b t1", labelOffset: P7OFF[l] + 2, style: "stroke-width:" + (1.4 + 0.5 * x[l]).toFixed(1) + "px" });
        else drawArc(g, P[a[0]], P[a[1]], { bend: G.bend[l], cls: "ln cm thin dash", r: 18, marker: mm, label: lab, labelCls: "tx-s", labelOffset: P7OFF[l] + 1 });
      }
      for (l = 0; l < 12; l++) p7hit(g, l, P, function (j, e) {
        U[j] = Math.max(0, Math.min(9, U[j] + ((minus.checked || e.shiftKey) ? -1 : 1))); restart();
      });
      G.nodes.forEach(function (v) { drawNode(g, P[v], v, { cls: S.indexOf(v) >= 0 ? "f3" : "f1", r: 18 }); });
      var tv = el("text", { x: W / 2, y: H - 8, "class": "tx-b", "text-anchor": "middle" }, g);
      tv.textContent = "valeur du flot : " + value(x) + (showCut ? " = capacité de la coupe" : "");
      // texte
      var txt;
      if (k === 0) {
        txt = "Flot nul. Capacités : " + G.arcs.map(function (a, j) { return a[0] + a[1] + " " + U[j]; }).join(", ") + ".\nCliquez « Chemin augmentant suivant ». (Un clic sur un arc change sa capacité et relance l'algorithme.)";
      } else if (!showCut) {
        var st = res.steps[k - 1], nodesTxt = ["s"], parts = [];
        st.path.forEach(function (e, i) {
          nodesTxt.push(e[3]);
          parts.push(e[1] > 0 ? e[2] + "→" + e[3] + " : u − x = " + st.caps[i] : e[2] + "→" + e[3] + " : arc " + p7arcName(G.arcs[e[0]]) + " à l'envers, on peut retirer " + st.caps[i]);
        });
        txt = "Étape " + k + " : chemin " + nodesTxt.join(" → ") + ".\nCapacités résiduelles : " + parts.join(" ; ") + ".\nGoulot θ = " + st.theta + " ; valeur du flot : " + (value(st.x) - st.theta) + " → " + value(st.x) + ".";
        if (k === K) txt += "\nCliquez encore : on cherche un nouveau chemin.";
      } else {
        var cutArcs = [], back = [], capS = 0;
        G.arcs.forEach(function (a, j) {
          var i0 = S.indexOf(a[0]) >= 0, j0 = S.indexOf(a[1]) >= 0;
          if (i0 && !j0) { cutArcs.push(p7arcName(a) + " " + x[j] + "/" + U[j]); capS += U[j]; }
          if (!i0 && j0) back.push(p7arcName(a) + " " + x[j]);
        });
        txt = "Plus aucun chemin augmentant. Les nœuds atteignables depuis s dans le graphe résiduel forment S = {" + S.join(", ") + "}.";
        txt += "\nArcs de S vers T, tous saturés : " + (cutArcs.join(", ") || "aucun") + " ; capacité de la coupe = " + capS + ".";
        txt += "\nArcs de T vers S, tous vides : " + (back.join(", ") || "aucun") + ".";
        txt += "\nValeur du flot = " + value(x) + " = capacité de la coupe : le flot est maximal et la coupe minimale (" + K + " chemins augmentants).";
      }
      ro.textContent = txt;
    }
    restart(); redrawers.push(draw);
  };

  /* --- 4. Dijkstra pas à pas (§6) --- */
  WIDGETS.p7dijkstra = function (box) {
    var s = scaffold(box, "L'algorithme de Dijkstra pas à pas : à chaque étape, on fixe le nœud d'étiquette provisoire la plus petite");
    var W = 680, H = 350, G = P7G;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Le graphe de la diapo 26 avec les coûts, les étiquettes de Dijkstra et l'arbre des plus courts chemins");
    var cSel = select(s.controls, "Coûts", [["page", "ceux de la section 6 (tous ≥ 0)"], ["neg", "avec un coût négatif : c₁₃ = −2, cₛ₃ = 1"]], "page", restart);
    button(s.controls, "Étape suivante", function () { if (k < steps.length) { k++; draw(); } });
    button(s.controls, "Tout dérouler", function () { k = steps.length; draw(); });
    button(s.controls, "Recommencer", function () { k = 0; draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "nœud fixé, arc de l'arbre"], ["--s2", "arcs examinés à l'étape"], ["--muted", "autres arcs"]]);
    var C, steps, k = 0, truth;
    function costs() {
      var c = G.C.slice();
      if (cSel.value === "neg") { c[1] = 1; c[3] = -2; }
      return c;
    }
    function run(c) {
      var d = {}, pred = {}, done = [], out = [];
      G.nodes.forEach(function (v) { d[v] = Infinity; pred[v] = null; });
      d.s = 0;
      while (done.length < G.nodes.length) {
        var best = null;
        G.nodes.forEach(function (v) { if (done.indexOf(v) < 0 && d[v] < Infinity && (best === null || d[v] < d[best])) best = v; });
        if (best === null) break;
        done.push(best);
        var exam = [];
        G.arcs.forEach(function (a, l) {
          if (a[0] !== best || done.indexOf(a[1]) >= 0) return;
          var cand = d[best] + c[l], old = d[a[1]], better = cand < old;
          if (better) { d[a[1]] = cand; pred[a[1]] = best; }
          exam.push({ l: l, to: a[1], cand: cand, old: old, better: better });
        });
        var ignored = [];
        G.arcs.forEach(function (a, l) { if (a[0] === best && done.indexOf(a[1]) >= 0 && a[1] !== best && d[best] + c[l] < d[a[1]]) ignored.push({ l: l, to: a[1], cand: d[best] + c[l], old: d[a[1]] }); });
        out.push({ v: best, d: Object.assign({}, d), pred: Object.assign({}, pred), exam: exam, ignored: ignored, done: done.slice() });
      }
      return out;
    }
    function bellman(c) {
      var d = {}, pred = {};
      G.nodes.forEach(function (v) { d[v] = Infinity; pred[v] = null; });
      d.s = 0;
      for (var it = 0; it < G.nodes.length; it++) G.arcs.forEach(function (a, l) { if (d[a[0]] + c[l] < d[a[1]]) { d[a[1]] = d[a[0]] + c[l]; pred[a[1]] = a[0]; } });
      return { d: d, pred: pred };
    }
    function pathTo(pred, v) { var out = [v]; while (pred[out[0]] !== null && out.length < 10) out.unshift(pred[out[0]]); return out; }
    function restart() { C = costs(); steps = run(C); truth = bellman(C); k = 0; draw(); }
    function dstr(v) { return v === Infinity ? "∞" : String(v).replace("-", "−"); }
    function draw() {
      var P = G.pos, l;
      var st = k > 0 ? steps[k - 1] : null;
      var d = st ? st.d : { s: 0, "1": Infinity, "2": Infinity, "3": Infinity, "4": Infinity, p: Infinity };
      var pred = st ? st.pred : {};
      var done = st ? st.done : [];
      var examL = {};
      if (st) st.exam.forEach(function (e) { examL[e.l] = e.better; });
      var tree = {};
      G.nodes.forEach(function (v) { if (pred[v]) tree[pred[v] + ">" + v] = true; });
      p7clear(s.svg);
      var g = el("g", {}, s.svg);
      var m3 = p7marker(s.svg, "f3"), m2 = p7marker(s.svg, "f2"), mm = p7marker(s.svg, "fm");
      for (l = 0; l < 12; l++) {
        var a = G.arcs[l], lab = String(C[l]).replace("-", "−");
        var isTree = tree[a[0] + ">" + a[1]] && done.indexOf(a[1]) >= 0;
        if (l in examL) drawArc(g, P[a[0]], P[a[1]], { bend: G.bend[l], cls: "ln c2", r: 18, marker: m2, label: lab, labelCls: "tx-b t2", labelOffset: P7OFF[l] + 1, style: "stroke-width:3px" });
        else if (isTree) drawArc(g, P[a[0]], P[a[1]], { bend: G.bend[l], cls: "ln c3", r: 18, marker: m3, label: lab, labelCls: "tx-b t3", labelOffset: P7OFF[l] + 1, style: "stroke-width:3px" });
        else drawArc(g, P[a[0]], P[a[1]], { bend: G.bend[l], cls: "ln cm thin", r: 18, marker: mm, label: lab, labelCls: C[l] < 0 ? "tx-b t6" : "tx-s", labelOffset: P7OFF[l] });
      }
      G.nodes.forEach(function (v) {
        var fixed = done.indexOf(v) >= 0, cur = st && st.v === v;
        drawNode(g, P[v], v, { cls: fixed ? "f3" : "fm", r: 18 });
        if (cur) el("circle", { cx: P[v][0], cy: P[v][1], r: 23, "class": "ln c3 thin nofill" }, g);
        var up = (v === "1" || v === "2");
        var t = el("text", { x: P[v][0], y: P[v][1] + (up ? -28 : 37), "class": fixed ? "tx-b t3" : "tx-s", "text-anchor": "middle" }, g);
        t.textContent = "d = " + dstr(d[v]) + (fixed ? "" : " (provisoire)");
      });
      var lines = [];
      for (var i = 0; i < k; i++) {
        var S = steps[i], parts = S.exam.map(function (e) {
          return S.v + "→" + e.to + " : " + dstr(S.d[S.v]) + " + " + dstr(C[e.l]) + " = " + dstr(e.cand) + (e.better ? " < " + dstr(e.old) + " ⇒ d(" + e.to + ") = " + dstr(e.cand) : " ≥ " + dstr(e.old) + ", rien");
        });
        S.ignored.forEach(function (e) { parts.push(S.v + "→" + e.to + " : " + dstr(e.cand) + " < " + dstr(e.old) + " mais " + e.to + " est déjà fixé : ignoré !"); });
        lines.push("Étape " + (i + 1) + " : on fixe " + S.v + " (d = " + dstr(S.d[S.v]) + ")" + (parts.length ? " ; " + parts.join(" ; ") : " ; aucun arc vers un nœud non fixé"));
      }
      var txt = k === 0 ? "Départ : d(s) = 0, toutes les autres étiquettes valent ∞. Cliquez « Étape suivante »." : lines.join("\n");
      if (k === steps.length) {
        var pd = pathTo(steps[k - 1].pred, "p");
        txt += "\nRésultat de Dijkstra : chemin " + pd.join(" → ") + ", coût " + dstr(steps[k - 1].d.p) + ".";
        var tp = pathTo(truth.pred, "p");
        if (truth.d.p !== steps[k - 1].d.p) txt += "\nFAUX : le vrai plus court chemin (Bellman–Ford) est " + tp.join(" → ") + ", de coût " + dstr(truth.d.p) + ". Avec un coût négatif, un nœud fixé peut encore être amélioré.";
        else txt += "\nC'est bien le plus court chemin (vérifié par Bellman–Ford) ; les arcs verts forment l'arbre des plus courts chemins depuis s.";
      }
      ro.textContent = txt;
    }
    restart(); redrawers.push(draw);
  };

  /* --- 5. L'affectation : matrices doublement stochastiques et permutations (§7) --- */
  WIDGETS.p7affectation = function (box) {
    var s = scaffold(box, "Affectation : une matrice doublement stochastique qu'on déforme vers une permutation, et le coût linéaire");
    var W = 680, H = 300, N = 4;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Matrice de coûts 4 x 4, matrice doublement stochastique D(t) et coûts des 24 permutations");
    var PAGE = [[5, 6, 1, 15], [10, 2, 12, 7], [14, 4, 9, 8], [13, 16, 3, 11]];
    var Cm = PAGE.map(function (r) { return r.slice(); }), seed = 1;
    var perms = [];
    (function rec(cur, used) {
      if (cur.length === N) { perms.push(cur.slice()); return; }
      for (var j = 0; j < N; j++) if (!used[j]) { used[j] = true; cur.push(j); rec(cur, used); cur.pop(); used[j] = false; }
    })([], []);
    var MIX = [[[0, 1, 2, 3], 1 / 2], [[1, 0, 3, 2], 1 / 3], [[3, 2, 1, 0], 1 / 6]];
    var cSel = select(s.controls, "Coûts", [["page", "exemple : 4 tâches, 4 machines"], ["rand", "tirage au hasard"]], "page", function () { if (cSel.value === "page") Cm = PAGE.map(function (r) { return r.slice(); }); else newDraw(); draw(); });
    button(s.controls, "Nouveau tirage", function () { cSel.value = "rand"; newDraw(); draw(); });
    var d0Sel = select(s.controls, "Départ D₀", [["J", "matrice uniforme J/4"], ["mix", "mélange de 3 permutations (1/2, 1/3, 1/6)"]], "J", draw);
    var tgSel = select(s.controls, "Vers", [["opt", "la permutation optimale (hongrois)"], ["greedy", "la permutation gloutonne"], ["id", "l'identité"]], "opt", draw);
    var tS = slider(s.controls, "t", 0, 1, 0.01, 0.4, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "coefficient Dᵢⱼ (opacité)"], ["--s3", "permutation optimale"], ["--s2", "coût de D(t)"]]);
    function newDraw() {
      var rng = mulberry32(4242 + 97 * seed++);
      Cm = []; for (var i = 0; i < N; i++) { Cm.push([]); for (var j = 0; j < N; j++) Cm[i].push(1 + Math.floor(rng() * 16)); }
    }
    function pcost(sg) { var t = 0; for (var i = 0; i < N; i++) t += Cm[i][sg[i]]; return t; }
    function greedy() {
      var cells = [], ur = {}, uc = {}, sg = [];
      for (var i = 0; i < N; i++) for (var j = 0; j < N; j++) cells.push([Cm[i][j], i, j]);
      cells.sort(function (a, b) { return a[0] - b[0] || a[1] - b[1] || a[2] - b[2]; });
      cells.forEach(function (c) { if (!ur[c[1]] && !uc[c[2]]) { ur[c[1]] = 1; uc[c[2]] = 1; sg[c[1]] = c[2]; } });
      return sg;
    }
    function draw() {
      var t = tS.get(); tS.out.textContent = p7num(t, 2);
      var opt = Array.prototype.slice.call(hungarian(Cm)), gr = greedy(), id = [0, 1, 2, 3];
      var target = tgSel.value === "opt" ? opt : tgSel.value === "greedy" ? gr : id;
      var D0 = [], D = [], i, j;
      for (i = 0; i < N; i++) { D0.push([]); for (j = 0; j < N; j++) D0[i].push(0); }
      if (d0Sel.value === "J") { for (i = 0; i < N; i++) for (j = 0; j < N; j++) D0[i][j] = 1 / N; }
      else MIX.forEach(function (m) { for (i = 0; i < N; i++) D0[i][m[0][i]] += m[1]; });
      for (i = 0; i < N; i++) { D.push([]); for (j = 0; j < N; j++) D[i].push((1 - t) * D0[i][j] + t * (target[i] === j ? 1 : 0)); }
      var c0 = 0, cD = 0;
      for (i = 0; i < N; i++) for (j = 0; j < N; j++) { c0 += Cm[i][j] * D0[i][j]; cD += Cm[i][j] * D[i][j]; }
      var allc = perms.map(pcost), cmin = Math.min.apply(null, allc), cmax = Math.max.apply(null, allc);
      var mean = allc.reduce(function (a, b) { return a + b; }, 0) / allc.length;
      p7clear(s.svg);
      var g = el("g", {}, s.svg);
      // matrice
      var x0 = 70, y0 = 48, cw = 58, ch = 50;
      var tt = el("text", { x: x0 + 2 * cw, y: 22, "class": "tx-b", "text-anchor": "middle" }, g); tt.textContent = "coûts cᵢⱼ et D(t) (case bleue = Dᵢⱼ)";
      for (j = 0; j < N; j++) { var tc = el("text", { x: x0 + j * cw + cw / 2, y: y0 - 6, "class": "tx-s", "text-anchor": "middle" }, g); tc.textContent = "M" + (j + 1); }
      for (i = 0; i < N; i++) {
        var tr = el("text", { x: x0 - 8, y: y0 + i * ch + ch / 2 + 4, "class": "tx-s", "text-anchor": "end" }, g); tr.textContent = "T" + (i + 1);
        for (j = 0; j < N; j++) {
          var X = x0 + j * cw, Y = y0 + i * ch;
          el("rect", { x: X + 2, y: Y + 2, width: cw - 4, height: ch - 4, rx: 5, "class": "f1", "fill-opacity": (0.06 + 0.8 * D[i][j]).toFixed(3) }, g);
          if (opt[i] === j) el("rect", { x: X + 1, y: Y + 1, width: cw - 2, height: ch - 2, rx: 6, "class": "ln c3 nofill", style: "stroke-width:2.6px" }, g);
          var strong = D[i][j] > 0.55;
          var t1 = el("text", { x: X + cw / 2, y: Y + 22, "class": strong ? "tx-b on-fill" : "tx-b", "text-anchor": "middle" }, g); t1.textContent = Cm[i][j];
          var t2 = el("text", { x: X + cw / 2, y: Y + 38, "class": strong ? "tx-s on-fill" : "tx-s", "text-anchor": "middle" }, g); t2.textContent = p7num(D[i][j], 2);
        }
      }
      var tb = el("text", { x: x0 + 2 * cw, y: y0 + N * ch + 22, "class": "tx-s", "text-anchor": "middle" }, g);
      tb.textContent = "chaque ligne et chaque colonne de D(t) somme à 1";
      // axe des coûts des 24 permutations
      var ax0 = 370, ax1 = 650, ay = 190;
      function X2(v) { return ax0 + (v - cmin) / Math.max(1, cmax - cmin) * (ax1 - ax0); }
      var tt3 = el("text", { x: (ax0 + ax1) / 2, y: 22, "class": "tx-b", "text-anchor": "middle" }, g); tt3.textContent = "coûts des 24 permutations";
      el("line", { x1: ax0 - 6, y1: ay, x2: ax1 + 6, y2: ay, "class": "ax" }, g);
      var stack = {};
      perms.forEach(function (sg, q) {
        var v = allc[q], h = stack[v] = (stack[v] || 0) + 1;
        var isOpt = v === cmin;
        el("circle", { cx: X2(v), cy: ay - 9 - (h - 1) * 12, r: isOpt ? 6 : 4.5, "class": isOpt ? "f3" : "fk", "fill-opacity": isOpt ? 1 : 0.7 }, g);
      });
      [cmin, Math.round(mean * 100) / 100, cmax].forEach(function (v) {
        el("line", { x1: X2(v), y1: ay, x2: X2(v), y2: ay + 5, "class": "ax" }, g);
        var tx = el("text", { x: X2(v), y: ay + 18, "class": "tx-s", "text-anchor": "middle" }, g); tx.textContent = p7num(v, v === Math.round(v) ? 0 : 2);
      });
      var tm = el("text", { x: X2(mean), y: ay + 32, "class": "tx-s", "text-anchor": "middle" }, g); tm.textContent = "moyenne";
      var to = el("text", { x: X2(cmin), y: ay - 30 - 12 * ((stack[cmin] || 1) - 1), "class": "tx-b t3", "text-anchor": "start" }, g); to.textContent = "optimum " + cmin;
      // coût de D(t)
      var yD = 262;
      el("line", { x1: X2(c0), y1: yD, x2: X2(pcost(target)), y2: yD, "class": "ln c2 thin dash" }, g);
      el("path", { d: "M" + X2(cD) + " " + (yD - 8) + " l7 8 l-7 8 l-7 -8 z", "class": "f2" }, g);
      var tDv = el("text", { x: X2(cD), y: yD - 13, "class": "tx-b t2", "text-anchor": "middle" }, g); tDv.textContent = "D(t) : " + p7num(cD, 2);
      el("line", { x1: X2(cD), y1: ay + 36, x2: X2(cD), y2: yD - 26, "class": "ln c2 hair dash" }, g);
      // texte
      var sgStr = function (sg) { return "(" + sg.map(function (v) { return v + 1; }).join(", ") + ")"; };
      var rows = D.map(function (r) { return r.reduce(function (a, b) { return a + b; }, 0); });
      var cols = [0, 1, 2, 3].map(function (jj) { return D.reduce(function (a, r) { return a + r[jj]; }, 0); });
      var ok = rows.concat(cols).every(function (v) { return Math.abs(v - 1) < 1e-9; });
      var txt = "D(t) = (1 − t)·D₀ + t·P avec t = " + p7num(t, 2) + " : coefficients ≥ 0, sommes des lignes et des colonnes = 1 " + (ok ? "✓" : "✗") + " → doublement stochastique.";
      txt += "\nCoût Σ cᵢⱼ Dᵢⱼ(t) = (1 − t)·" + p7num(c0, 2) + " + t·" + pcost(target) + " = " + p7num(cD, 2) + " : affine en t, donc jamais meilleur qu'en une extrémité.";
      txt += "\nHongrois : σ = " + sgStr(opt) + ", coût " + pcost(opt) + " = le plus petit des 24 coûts (" + cmin + ") ; glouton : σ = " + sgStr(gr) + ", coût " + pcost(gr) + " ; identité : " + pcost(id) + ".";
      txt += "\nMoyenne des 24 permutations = " + p7num(mean, 2) + (d0Sel.value === "J" ? " = coût de J/4 (= somme des cᵢⱼ / 4)." : " ; D₀ coûte la moyenne pondérée de ses 3 permutations : " + MIX.map(function (m) { return pcost(m[0]); }).join(", ") + ".");
      ro.textContent = txt;
    }
    draw(); redrawers.push(draw);
  };
