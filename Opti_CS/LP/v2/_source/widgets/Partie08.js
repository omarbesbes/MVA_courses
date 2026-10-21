// widgets/Partie08.js — figures interactives de la partie 8 (problèmes entiers célèbres).
// Inséré par build.mjs dans la portée de app.js : utilise el, scaffold, slider, select, button, checkbox, readout,
// legend, Fr, svgPoint, redrawers. Toutes les fonctions propres sont préfixées p8.

  /* ---------------- outils communs de la page ---------------- */
  var P8_P = [4, 4, 8, 2, 8], P8_U = [16, 15, 22, 4, 12], P8_NAMES = ["A", "B", "C", "D", "E"];
  // Une fraction exacte en typographie française : 47,5 ; 3/4 ; 151/3.
  function p8num(q) {
    q = Fr.of(q);
    if (q.d === 1) return String(q.n).replace("-", "−");
    if ([2, 4, 5, 8, 10, 20, 25].indexOf(q.d) >= 0) return String(+(q.n / q.d).toFixed(4)).replace(".", ",").replace("-", "−");
    return q.str();
  }
  function p8short(q) { // a fraction in a vector: 1/2, 3/4 … as compact as possible
    q = Fr.of(q);
    var sp = { "1/2": "½", "1/4": "¼", "3/4": "¾", "1/3": "⅓", "2/3": "⅔" }[q.n + "/" + q.d];
    return sp || q.str();
  }
  // Relaxation continue (borne de Dantzig) avec des variables fixées : fixed[j] = 0, 1 ou undefined.
  // Renvoie null si les objets fixés à 1 dépassent la capacité, sinon {bound (Fr), x (Fr[]), k (indice fractionnaire ou −1)}.
  function p8relax(p, u, L, fixed) {
    var n = p.length, x = [], cap = Fr(L), val = Fr(0), j, k = -1;
    for (j = 0; j < n; j++) x.push(Fr(0));
    for (j = 0; j < n; j++) if (fixed[j] === 1) { x[j] = Fr(1); cap = cap.sub(p[j]); val = val.add(u[j]); }
    if (cap.sign() < 0) return null;
    var free = [];
    for (j = 0; j < n; j++) if (fixed[j] === undefined) free.push(j);
    free.sort(function (a, b) { return Fr(u[b], p[b]).cmp(Fr(u[a], p[a])) || a - b; });
    for (var t = 0; t < free.length; t++) {
      j = free[t];
      if (Fr(p[j]).cmp(cap) <= 0) { x[j] = Fr(1); cap = cap.sub(p[j]); val = val.add(u[j]); }
      else { x[j] = cap.div(p[j]); val = val.add(x[j].mul(u[j])); if (!x[j].isZero()) k = j; break; }
    }
    return { bound: val, x: x, k: k };
  }
  function p8greedy(p, u, L) {
    var n = p.length, order = [], j, x = [], cap = L, val = 0;
    for (j = 0; j < n; j++) { order.push(j); x.push(0); }
    order.sort(function (a, b) { return Fr(u[b], p[b]).cmp(Fr(u[a], p[a])) || a - b; });
    order.forEach(function (j) { if (p[j] <= cap) { x[j] = 1; cap -= p[j]; val += u[j]; } });
    return { val: val, x: x };
  }
  function p8best(p, u, L) { // énumération des 2^n sous-ensembles
    var n = p.length, best = { val: -1, x: null }, nf = 0;
    for (var m = 0; m < (1 << n); m++) {
      var w = 0, v = 0, x = [];
      for (var j = 0; j < n; j++) { var b = (m >> j) & 1; x.push(b); w += b * p[j]; v += b * u[j]; }
      if (w <= L) { nf++; if (v > best.val) best = { val: v, x: x }; }
    }
    best.nfeas = nf;
    return best;
  }
  function p8list(x) { var s = []; x.forEach(function (b, j) { if (b) s.push(P8_NAMES[j]); }); return s.length ? s.join(", ") : "rien"; }

  /* --- 1. Le sac-à-dos : votre choix, le glouton, la relaxation, l'optimum (§2) --- */
  WIDGETS.p8sac = function (box) {
    var s = scaffold(box, "Remplissez le sac : cliquez sur les objets, comparez avec le glouton, la relaxation et l'optimum");
    var W = 680, H = 316, x0 = 120, scale = 540 / 26;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Cinq objets à cliquer et quatre sacs dessinés à l'échelle de leur poids");
    var sel = [0, 0, 0, 0, 0];
    var Ls = slider(s.controls, "Capacité L", 4, 26, 1, 14, draw);
    button(s.controls, "Prendre le glouton", function () { sel = p8greedy(P8_P, P8_U, Ls.get()).x.slice(); draw(); });
    button(s.controls, "Vider le sac", function () { sel = [0, 0, 0, 0, 0]; draw(); });
    var showOpt = checkbox(s.controls, "afficher l'optimum", false, draw);
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "votre choix (admissible)"], ["--s6", "votre choix (trop lourd)"], ["--s4", "glouton"], ["--s5", "relaxation continue"], ["--s3", "optimum"]]);

    s.svg.addEventListener("click", function (e) {
      var pt = svgPoint(s.svg, e);
      for (var j = 0; j < 5; j++) {
        var cx = 20 + j * 132;
        if (pt.x >= cx && pt.x <= cx + 120 && pt.y >= 10 && pt.y <= 78) { sel[j] = 1 - sel[j]; draw(); return; }
      }
    });

    function bar(g, y, xs, k, label, sub) {
      var L = Ls.get();
      var t1 = el("text", { x: 12, y: y + 15, "class": "tx-b" }, g); t1.textContent = label;
      var t2 = el("text", { x: 12, y: y + 29, "class": "tx-s" }, g); t2.textContent = sub;
      el("rect", { x: x0, y: y, width: L * scale, height: 30, rx: 4, "class": "ln cm thin dash nofill" }, g);
      if (!xs) return;
      var xx = x0;
      xs.forEach(function (q, j) {
        q = Fr.of(q); if (q.isZero()) return;
        var w = q.val() * P8_P[j] * scale;
        var over = xx + w > x0 + L * scale + 0.5;
        var kk = k === "sel" ? (over ? 6 : 1) : k;
        el("rect", { x: xx + 1, y: y + 2, width: Math.max(w - 2, 1), height: 26, rx: 3, "class": "a" + Math.min(kk, 5) + " ln c" + kk + " thin" + (kk === 6 ? " dash" : "") }, g);
        var tt = el("text", { x: xx + w / 2, y: y + 19, "class": "tx-b", "text-anchor": "middle" }, g);
        tt.textContent = (q.cmp(1) === 0 ? "" : p8short(q) + " ") + P8_NAMES[j];
        xx += w;
      });
    }

    function draw() {
      var L = Ls.get();
      Ls.out.textContent = L;
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg);
      var w = 0, v = 0;
      sel.forEach(function (b, j) { w += b * P8_P[j]; v += b * P8_U[j]; });
      var ok = w <= L;
      for (var j = 0; j < 5; j++) {
        var cx = 20 + j * 132;
        var cls = sel[j] ? (ok ? "a1 ln c1" : "a1 ln c6") : "am ln cm thin";
        el("rect", { x: cx, y: 10, width: 120, height: 68, rx: 7, "class": cls + " drag" }, g);
        var a = el("text", { x: cx + 60, y: 30, "class": "tx-b", "text-anchor": "middle" }, g); a.textContent = P8_NAMES[j] + (sel[j] ? "  (dans le sac)" : "");
        var b2 = el("text", { x: cx + 60, y: 49, "class": "tx-s", "text-anchor": "middle" }, g); b2.textContent = "poids " + P8_P[j] + " · utilité " + P8_U[j];
        var c2 = el("text", { x: cx + 60, y: 66, "class": "tx-s", "text-anchor": "middle" }, g); c2.textContent = "u/p = " + p8num(Fr(P8_U[j], P8_P[j]));
      }
      var gr = p8greedy(P8_P, P8_U, L), rl = p8relax(P8_P, P8_U, L, {}), op = p8best(P8_P, P8_U, L);
      bar(g, 100, sel, "sel", "votre sac", "utilité " + v + ", poids " + w);
      bar(g, 150, gr.x, 4, "glouton", "utilité " + gr.val);
      bar(g, 200, rl.x, 5, "relaxation", "borne " + p8num(rl.bound));
      bar(g, 250, showOpt.checked ? op.x : null, 3, "optimum", showOpt.checked ? "utilité " + op.val : "caché");
      if (!showOpt.checked) { var q = el("text", { x: x0 + L * scale / 2, y: 270, "class": "tx-b", "text-anchor": "middle" }, g); q.textContent = "?"; }
      // ruler
      var yy = 296;
      el("line", { x1: x0, y1: yy, x2: x0 + 26 * scale, y2: yy, "class": "ax" }, g);
      for (var t = 0; t <= 26; t += 2) {
        el("line", { x1: x0 + t * scale, y1: yy - 3, x2: x0 + t * scale, y2: yy + 3, "class": "ax" }, g);
        var tt = el("text", { x: x0 + t * scale, y: yy + 15, "class": "tx-s", "text-anchor": "middle" }, g); tt.textContent = t;
      }
      el("line", { x1: x0 + L * scale, y1: 94, x2: x0 + L * scale, y2: yy, "class": "ln c2 thin" }, g);
      var lt = el("text", { x: x0 + L * scale + 4, y: 96, "class": "tx-s t2" }, g); lt.textContent = "L = " + L;
      var txt = "Votre sac : " + p8list(sel) + " — poids " + w + " / " + L + (ok ? " (admissible)" : " : TROP LOURD") + " — utilité " + v + ".";
      txt += "\nGlouton (par u/p décroissant, on prend chaque objet qui tient encore) : " + p8list(gr.x) + " → " + gr.val + ".";
      txt += "\nRelaxation continue (0 ≤ xⱼ ≤ 1) : borne " + p8num(rl.bound) + (rl.k >= 0 ? " (objet " + P8_NAMES[rl.k] + " coupé : " + p8short(rl.x[rl.k]) + ")" : " (solution entière)") + ".";
      txt += "\nOptimum entier : " + (showOpt.checked ? op.val + " (" + p8list(op.x) + "), par énumération des 32 sous-ensembles dont " + op.nfeas + " admissibles" : "?  (cochez « afficher l'optimum »)") + ".";
      txt += "\nEncadrement : " + gr.val + " ≤ optimum ≤ " + p8num(rl.bound) + (ok && v > gr.val ? "   — votre sac fait mieux que le glouton : nouvelle borne inférieure " + v + "." : "");
      ro.textContent = txt;
    }
    draw(); redrawers.push(draw);
  };

  /* --- 2. L'arbre de séparation-évaluation pas à pas (§3) --- */
  // Le parcours complet, calculé d'avance : nœuds dans l'ordre de visite.
  function p8bnb(p, u, L, oneFirst, startGreedy) {
    var nodes = [], g = p8greedy(p, u, L);
    var best = startGreedy ? { val: g.val, x: g.x.slice(), from: "glouton" } : null;
    function visit(fixed, parent, depth, label) {
      var r = p8relax(p, u, L, fixed);
      var nd = { id: nodes.length, parent: parent, fixed: fixed, depth: depth, label: label, r: r, kids: [], bestBefore: best ? best.val : null };
      nodes.push(nd);
      if (parent !== null) nodes[parent].kids.push(nd.id);
      if (!r) { nd.dec = "infeasible"; nd.bestAfter = nd.bestBefore; return; }
      if (best && r.bound.cmp(best.val) <= 0) { nd.dec = "pruned"; nd.bestAfter = nd.bestBefore; return; }
      if (r.k < 0) {
        nd.dec = "integer";
        best = { val: r.bound.val(), x: r.x.map(function (q) { return q.val(); }), from: "nœud " + nd.id };
        nd.bestAfter = best.val; nd.bestX = best.x; return;
      }
      nd.dec = "branch"; nd.branch = r.k; nd.bestAfter = nd.bestBefore;
      (oneFirst ? [1, 0] : [0, 1]).forEach(function (v) {
        var f2 = {}; for (var key in fixed) f2[key] = fixed[key]; f2[r.k] = v;
        visit(f2, nd.id, depth + 1, P8_NAMES[r.k] + "=" + v);
      });
    }
    visit({}, null, 0, "");
    return { nodes: nodes, best: best, greedy: g };
  }

  WIDGETS.p8arbre = function (box) {
    var s = scaffold(box, "Séparation-évaluation sur le sac-à-dos : un nœud à chaque clic");
    var W = 680, H = 372;
    s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Arbre de séparation-évaluation construit pas à pas");
    var Ls = slider(s.controls, "Capacité L", 4, 26, 1, 14, reset);
    var ord = select(s.controls, "Ordre", [["1", "branche x = 1 d'abord"], ["0", "branche x = 0 d'abord"]], "1", reset);
    var st = select(s.controls, "Départ", [["g", "solution du glouton"], ["n", "aucune solution connue"]], "g", reset);
    button(s.controls, "Étape", function () { if (shown < run.nodes.length) shown++; draw(); });
    button(s.controls, "Tout", function () { shown = run.nodes.length; draw(); });
    button(s.controls, "Recommencer", function () { shown = 0; draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "séparé (relaxation fractionnaire)"], ["--s3", "solution entière"], ["--s6", "élagué (borne ≤ meilleure connue)"], ["--muted", "irréalisable"]]);
    var run, shown, pos;

    // A new setting shows the whole tree at once; « Recommencer » then « Étape » replays it node by node.
    function reset() { Ls.out.textContent = Ls.get(); run = p8bnb(P8_P, P8_U, Ls.get(), ord.value === "1", st.value === "g"); layout(); shown = run.nodes.length; draw(); }
    function layout() {
      var slot = 0; pos = {};
      (function place(i) {
        var nd = run.nodes[i];
        if (!nd.kids.length) { pos[i] = slot++; return; }
        nd.kids.forEach(place);
        pos[i] = nd.kids.reduce(function (a, k) { return a + pos[k]; }, 0) / nd.kids.length;
      })(0);
      run.nslots = slot;
      run.depth = run.nodes.reduce(function (a, nd) { return Math.max(a, nd.depth); }, 0);
      H = Math.max(150, Y(run.depth) + 46);
      s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    }
    function X(sl) { return run.nslots <= 1 ? W / 2 : 40 + sl * (W - 80) / (run.nslots - 1); }
    function Y(d) { return 34 + d * 62; }
    function fixedStr(f) { var a = []; for (var k in f) a.push(P8_NAMES[k] + " = " + f[k]); return a.length ? a.join(", ") : "aucune variable fixée"; }
    function bestStr(v) { return v === null ? "aucune" : String(v); }

    function draw() {
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg), i, nd;
      for (i = 1; i < shown; i++) {
        nd = run.nodes[i];
        var pa = run.nodes[nd.parent];
        el("line", { x1: X(pos[pa.id]), y1: Y(pa.depth) + 15, x2: X(pos[i]), y2: Y(nd.depth) - 15, "class": "ln cm thin" }, g);
        var mx = (X(pos[pa.id]) + X(pos[i])) / 2, my = (Y(pa.depth) + Y(nd.depth)) / 2;
        var lt = el("text", { x: mx + (X(pos[i]) < X(pos[pa.id]) ? -5 : 5), y: my + 2, "class": "tx-s", "text-anchor": X(pos[i]) < X(pos[pa.id]) ? "end" : "start" }, g);
        lt.textContent = nd.label;
      }
      for (i = 0; i < shown; i++) {
        nd = run.nodes[i];
        var cls = { branch: "f1", integer: "f3", pruned: "f6", infeasible: "fm" }[nd.dec];
        var c = el("circle", { cx: X(pos[i]), cy: Y(nd.depth), r: 14, "class": cls }, g);
        if (i === shown - 1) el("circle", { cx: X(pos[i]), cy: Y(nd.depth), r: 18, "class": "ln ck thin nofill" }, g);
        var t = el("text", { x: X(pos[i]), y: Y(nd.depth) + 4.5, "class": "on-fill", "text-anchor": "middle" }, g); t.textContent = i;
        var b = el("text", { x: X(pos[i]), y: Y(nd.depth) + 28, "class": "tx-s", "text-anchor": "middle" }, g);
        b.textContent = nd.r ? p8num(nd.r.bound) : "×";
        void c;
      }
      if (!shown) { var h = el("text", { x: W / 2, y: H / 2, "class": "tx", "text-anchor": "middle" }, g); h.textContent = "Cliquez sur « Étape » pour évaluer la racine."; }
      var txt = "Glouton : " + run.greedy.val + "   ·   ";
      txt += "Nœuds évalués : " + shown + " / " + run.nodes.length + " (l'arbre complet aurait 63 nœuds, dont 32 feuilles).";
      if (shown) {
        nd = run.nodes[shown - 1];
        txt += "\nNœud " + nd.id + " (" + fixedStr(nd.fixed) + ") : ";
        if (nd.dec === "infeasible") txt += "les objets fixés à 1 pèsent plus que L = " + Ls.get() + " → irréalisable, on abandonne la branche.";
        else {
          txt += "relaxation x = (" + nd.r.x.map(p8short).join(", ") + "), borne " + p8num(nd.r.bound) + ". ";
          if (nd.dec === "pruned") txt += "Borne " + p8num(nd.r.bound) + " ≤ meilleure connue " + nd.bestBefore + " → élagué : rien de mieux dans cette branche.";
          else if (nd.dec === "integer") txt += "Solution entière : nouvelle meilleure connue " + nd.bestAfter + " (" + p8list(nd.bestX) + ").";
          else txt += "Fractionnaire en " + P8_NAMES[nd.branch] + " et borne > meilleure connue (" + bestStr(nd.bestBefore) + ") → on sépare : " + P8_NAMES[nd.branch] + " = 1 / " + P8_NAMES[nd.branch] + " = 0.";
        }
        var cur = nd.bestAfter;
        txt += "\nMeilleure connue après ce nœud : " + bestStr(cur) + ".";
        if (shown === run.nodes.length) txt += "  Terminé : toutes les branches sont fermées, l'optimum " + run.best.val + " (" + p8list(run.best.x) + ") est prouvé.";
      }
      ro.textContent = txt;
    }
    reset(); redrawers.push(draw);
  };

  /* --- 3. Le voyageur de commerce : degrés seuls, optimum, plus proche voisin, coupes (§4) --- */
  function p8dist(P) {
    return P.map(function (a) { return P.map(function (b) { return Math.floor(Math.hypot(a[0] - b[0], a[1] - b[1]) + 0.5); }); });
  }
  function p8tourLen(D, t) { var s = 0; for (var k = 0; k < t.length; k++) s += D[t[k]][t[(k + 1) % t.length]]; return s; }
  function p8perms(a) {
    if (a.length <= 1) return [a.slice()];
    var out = [];
    a.forEach(function (v, i) { var rest = a.slice(0, i).concat(a.slice(i + 1)); p8perms(rest).forEach(function (q) { out.push([v].concat(q)); }); });
    return out;
  }
  // Toutes les réunions de cycles disjoints de longueur ≥ 3 couvrant `nodes` (les solutions binaires des contraintes de degré).
  function p8covers(nodes) {
    if (!nodes.length) return [[]];
    var first = nodes[0], rest = nodes.slice(1), out = [];
    for (var k = 2; k <= rest.length; k++) {
      combinations(rest.length, k).forEach(function (idx) {
        var others = idx.map(function (i) { return rest[i]; });
        var remaining = rest.filter(function (v) { return others.indexOf(v) < 0; });
        if (remaining.length > 0 && remaining.length < 3) return;
        var subs = p8covers(remaining);
        p8perms(others).forEach(function (perm) {
          if (perm[0] > perm[perm.length - 1]) return;
          subs.forEach(function (sc) { out.push([[first].concat(perm)].concat(sc)); });
        });
      });
    }
    return out;
  }
  function p8nn(D) {
    var t = [0], left = []; for (var v = 1; v < D.length; v++) left.push(v);
    while (left.length) {
      var cur = t[t.length - 1], bi = 0;
      for (var i = 1; i < left.length; i++) if (D[cur][left[i]] < D[cur][left[bi]]) bi = i;
      t.push(left[bi]); left.splice(bi, 1);
    }
    return t;
  }
  function p8inside(cover, S) { // nombre d'arêtes de la solution à l'intérieur de S
    var c = 0;
    cover.forEach(function (cy) { for (var k = 0; k < cy.length; k++) { var a = cy[k], b = cy[(k + 1) % cy.length]; if (S.indexOf(a) >= 0 && S.indexOf(b) >= 0) c++; } });
    return c;
  }

  WIDGETS.p8tsp = function (box) {
    var s = scaffold(box, "Voyageur de commerce : faites glisser les villes, comparez trois tracés, ajoutez des coupes");
    var plot = new Plot(s.svg, { x: [0, 100], y: [-6, 62], w: 680, h: 330, pad: { l: 14, r: 14, t: 14, b: 14 }, label: "Villes déplaçables et tournées" });
    var PRESETS = {
      cours: [[20, 20], [35, 30], [25, 0], [65, 10], [65, 30], [75, 50]],
      grappes: [[8, 40], [22, 52], [26, 30], [70, 12], [88, 20], [80, 40], [62, 30]],
      cercle: [0, 1, 2, 3, 4, 5, 6].map(function (k) { return [Math.round(50 + 40 * Math.cos(2 * Math.PI * k / 7)), Math.round(28 + 28 * Math.sin(2 * Math.PI * k / 7))]; })
    };
    var pre = select(s.controls, "Villes", [["cours", "exemple de la page (6 villes)"], ["grappes", "deux grappes (7 villes)"], ["cercle", "cercle (7 villes)"], ["alea", "au hasard (7 villes)"]], "cours", function () { load(pre.value); });
    var cDeg = checkbox(s.controls, "degrés seuls", true, draw);
    var cOpt = checkbox(s.controls, "tournée optimale", true, draw);
    var cNN = checkbox(s.controls, "plus proche voisin depuis 1", false, draw);
    button(s.controls, "Ajouter la coupe violée", function () { if (state.viol) { cuts.push(state.viol); draw(); } });
    button(s.controls, "Effacer les coupes", function () { cuts = []; draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s6", "contraintes de degré (et coupes) seules"], ["--s3", "tournée optimale"], ["--s4", "plus proche voisin"]]);
    var P = [], cuts = [], drag = -1, seed = 11, state = {};

    function load(name) {
      if (name === "alea") {
        var rng = mulberry32(seed++ * 7919);
        P = []; for (var i = 0; i < 7; i++) P.push([Math.round(5 + 90 * rng()), Math.round(56 * rng())]);
      } else P = PRESETS[name].map(function (q) { return q.slice(); });
      cuts = []; draw();
    }
    s.svg.addEventListener("pointerdown", function (e) {
      var pt = svgPoint(s.svg, e), bi = -1, bd = 22;
      P.forEach(function (q, i) { var d = Math.hypot(plot.tx(q[0]) - pt.x, plot.ty(q[1]) - pt.y); if (d < bd) { bd = d; bi = i; } });
      if (bi >= 0) { drag = bi; s.svg.setPointerCapture(e.pointerId); }
    });
    s.svg.addEventListener("pointermove", function (e) {
      if (drag < 0) return;
      var pt = svgPoint(s.svg, e);
      P[drag] = [Math.round(Math.min(100, Math.max(0, plot.ix(pt.x)))), Math.round(Math.min(60, Math.max(-4, plot.iy(pt.y))))];
      draw();
    });
    s.svg.addEventListener("pointerup", function () { drag = -1; });

    function edges(cycle, cls, off, g) {
      for (var k = 0; k < cycle.length; k++) {
        var a = P[cycle[k]], b = P[cycle[(k + 1) % cycle.length]];
        var dx = plot.tx(b[0]) - plot.tx(a[0]), dy = plot.ty(b[1]) - plot.ty(a[1]), L = Math.hypot(dx, dy) || 1;
        var ox = -dy / L * off, oy = dx / L * off;
        el("line", { x1: plot.tx(a[0]) + ox, y1: plot.ty(a[1]) + oy, x2: plot.tx(b[0]) + ox, y2: plot.ty(b[1]) + oy, "class": cls }, g);
      }
    }
    function draw() {
      plot.clear();
      var n = P.length, D = p8dist(P), idx = [], i;
      for (i = 0; i < n; i++) idx.push(i);
      var tours = p8perms(idx.slice(1)).filter(function (q) { return q[0] < q[q.length - 1]; }).map(function (q) { return [0].concat(q); });
      var best = tours[0], bl = p8tourLen(D, best);
      tours.forEach(function (t) { var l = p8tourLen(D, t); if (l < bl) { bl = l; best = t; } });
      var covers = p8covers(idx).filter(function (cv) { return cuts.every(function (S) { return p8inside(cv, S) <= S.length - 1; }); });
      var cv = covers[0], cl = Infinity;
      covers.forEach(function (c) { var l = c.reduce(function (a, cy) { return a + p8tourLen(D, cy); }, 0); if (l < cl) { cl = l; cv = c; } });
      var nn = p8nn(D), nl = p8tourLen(D, nn);
      var g = plot.g;
      if (cNN.checked) edges(nn, "ln c4 thin", cDeg.checked || cOpt.checked ? 4 : 0, g);
      if (cOpt.checked) edges(best, "ln c3", 0, g);
      if (cDeg.checked) cv.forEach(function (cy) { edges(cy, "ln c6 dash", cOpt.checked ? -4 : 0, g); });
      P.forEach(function (q, i) { drawNode(g, [plot.tx(q[0]), plot.ty(q[1])], String(i + 1), { r: 11, cls: "f1 drag" }); });
      // violated cut, if the best solution of the degree constraints has several cycles
      state.viol = null;
      if (cv.length > 1) {
        var small = cv.slice().sort(function (a, b) { return a.length - b.length; })[0];
        state.viol = small.slice().sort(function (a, b) { return a - b; });
      }
      function nm(S) { return "{" + S.map(function (v) { return v + 1; }).join(", ") + "}"; }
      var txt = n + " villes : " + tours.length + " tournées, " + p8covers(idx).length + " solutions binaires des contraintes de degré (distances euclidiennes arrondies à l'entier).";
      txt += "\nDegrés seuls" + (cuts.length ? " + " + cuts.length + " coupe(s) " + cuts.map(nm).join(" ") : "") + " : " + cl + "  =  " + cv.map(function (cy) { return cy.map(function (v) { return v + 1; }).join("-") + " (" + p8tourLen(D, cy) + ")"; }).join(" + ");
      txt += "\nTournée optimale : " + bl + " (" + best.map(function (v) { return v + 1; }).join("-") + ")   ·   plus proche voisin depuis 1 : " + nl + " (" + nn.map(function (v) { return v + 1; }).join("-") + ")";
      txt += "\nEncadrement : " + cl + " ≤ " + bl + " ≤ " + nl + ".";
      if (state.viol) {
        var S = state.viol;
        txt += "\nSous-tour sur S = " + nm(S) + " : " + S.length + " arêtes à l'intérieur de S, plus que card(S) − 1 = " + (S.length - 1) + " : la contrainte de sous-tour de S (somme des xᵢⱼ, i et j dans S, ≤ " + (S.length - 1) + ") est violée.";
      } else txt += "\nLa solution des degrés (et des coupes) est une tournée : elle est optimale.";
      ro.textContent = txt;
    }
    load("cours"); redrawers.push(draw);
  };

  /* --- 4. Table de vérité des contraintes logiques (§5) --- */
  WIDGETS.p8logique = function (box) {
    var s = scaffold(box, "Une règle logique, une inégalité candidate : la table de vérité dit si la traduction est juste");
    s.svg.setAttribute("role", "img");
    s.svg.setAttribute("aria-label", "Table de vérité : combinaisons permises et inégalité vérifiée");
    // [libellé, nombre de variables, règle logique, candidats [texte, test]]
    var RULES = [
      ["pas a et b ensemble (diapo 59)", 2, function (a, b) { return !(a && b); },
        [["xa + xb ≤ 1", function (a, b) { return a + b <= 1; }], ["xa + xb = 1", function (a, b) { return a + b === 1; }], ["xa + xb ≥ 1", function (a, b) { return a + b >= 1; }]]],
      ["au moins un de a, b (diapo 60)", 2, function (a, b) { return a || b; },
        [["xa + xb ≥ 1", function (a, b) { return a + b >= 1; }], ["xa + xb ≤ 1", function (a, b) { return a + b <= 1; }], ["xa · xb = 1 (non linéaire)", function (a, b) { return a * b === 1; }]]],
      ["si a alors b (diapo 61)", 2, function (a, b) { return !a || b; },
        [["xa ≤ xb", function (a, b) { return a <= b; }], ["xa ≥ xb", function (a, b) { return a >= b; }], ["xa + xb ≥ 1", function (a, b) { return a + b >= 1; }]]],
      ["si non b alors non a (diapo 62)", 2, function (a, b) { return b || !a; },
        [["(1 − xb) ≤ (1 − xa)", function (a, b) { return 1 - b <= 1 - a; }], ["xa ≤ xb", function (a, b) { return a <= b; }], ["xb ≤ xa", function (a, b) { return b <= a; }]]],
      ["si a alors b et/ou c (diapo 63)", 3, function (a, b, c) { return !a || b || c; },
        [["xa ≤ xb + xc", function (a, b, c) { return a <= b + c; }], ["2 xa ≤ xb + xc", function (a, b, c) { return 2 * a <= b + c; }], ["xa + xb + xc ≥ 1", function (a, b, c) { return a + b + c >= 1; }]]],
      ["si a alors b et c (ajout)", 3, function (a, b, c) { return !a || (b && c); },
        [["xa ≤ xb et xa ≤ xc", function (a, b, c) { return a <= b && a <= c; }], ["2 xa ≤ xb + xc", function (a, b, c) { return 2 * a <= b + c; }], ["xa ≤ xb + xc", function (a, b, c) { return a <= b + c; }]]],
      ["si a et b alors c (ajout)", 3, function (a, b, c) { return !(a && b) || c; },
        [["xa + xb − 1 ≤ xc", function (a, b, c) { return a + b - 1 <= c; }], ["xa + xb ≤ xc", function (a, b, c) { return a + b <= c; }], ["xa ≤ xc", function (a, b, c) { return a <= c; }]]],
      ["exactement un de a, b, c (ajout)", 3, function (a, b, c) { return a + b + c === 1; },
        [["xa + xb + xc = 1", function (a, b, c) { return a + b + c === 1; }], ["xa + xb + xc ≤ 1", function (a, b, c) { return a + b + c <= 1; }], ["xa + xb + xc ≥ 1", function (a, b, c) { return a + b + c >= 1; }]]],
      ["au plus deux de a, b, c (ajout)", 3, function (a, b, c) { return a + b + c <= 2; },
        [["xa + xb + xc ≤ 2", function (a, b, c) { return a + b + c <= 2; }], ["xa + xb + xc ≤ 1", function (a, b, c) { return a + b + c <= 1; }], ["xa + xb ≤ 1", function (a, b) { return a + b <= 1; }]]]
    ];
    var ruleSel = select(s.controls, "Règle", RULES.map(function (r, i) { return [String(i), r[0]]; }), "2", function () { fillCands(); draw(); });
    ruleSel.style.maxWidth = "15rem";
    var candLab = document.createElement("label");
    var candSpan = document.createElement("span"); candSpan.textContent = "Inégalité";
    var cand = document.createElement("select");
    candLab.appendChild(candSpan); candLab.appendChild(cand); s.controls.appendChild(candLab);
    cand.addEventListener("change", draw);
    cand.style.maxWidth = "15rem";
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "la ligne est traitée correctement"], ["--s6", "désaccord"]]);
    function fillCands() {
      cand.innerHTML = "";
      RULES[+ruleSel.value][3].forEach(function (c, i) { var o = document.createElement("option"); o.value = String(i); o.textContent = c[0]; cand.appendChild(o); });
      cand.value = "0";
    }
    function draw() {
      var R = RULES[+ruleSel.value], k = R[1], C = R[3][+cand.value];
      var rows = [], m;
      for (m = 0; m < (1 << k); m++) { var v = []; for (var j = k - 1; j >= 0; j--) v.push((m >> j) & 1); rows.push(v); }
      var W = 680, rh = 26, H = 40 + rh * rows.length + 8;
      s.svg.setAttribute("viewBox", "0 0 " + W + " " + H);
      while (s.svg.firstChild) s.svg.removeChild(s.svg.firstChild);
      var g = el("g", {}, s.svg);
      var names = ["xa", "xb", "xc"].slice(0, k);
      var cols = names.map(function (nm, i) { return 40 + i * 60; });
      var cRule = 40 + k * 60 + 30, cIneq = cRule + 190, cOk = cIneq + 200;
      function T(x, y, str, cls, anchor) { var t = el("text", { x: x, y: y, "class": cls || "tx", "text-anchor": anchor || "middle" }, g); t.textContent = str; return t; }
      names.forEach(function (nm, i) { T(cols[i], 24, nm, "tx-b"); });
      T(cRule, 24, "permis par la règle ?", "tx-b");
      T(cIneq, 24, C[0], "tx-b");
      T(cOk, 24, "accord", "tx-b");
      el("line", { x1: 10, y1: 32, x2: W - 10, y2: 32, "class": "ax" }, g);
      var bad = [];
      rows.forEach(function (v, r) {
        var y = 40 + r * rh;
        var allowed = !!R[2].apply(null, v), sat = !!C[1].apply(null, v), agree = allowed === sat;
        if (!agree) bad.push({ v: v, allowed: allowed });
        el("rect", { x: 10, y: y, width: W - 20, height: rh - 3, rx: 4, "class": agree ? "a3" : "a5" }, g);
        if (!agree) el("rect", { x: 10, y: y, width: W - 20, height: rh - 3, rx: 4, "class": "ln c6 thin nofill" }, g);
        v.forEach(function (b, i) { T(cols[i], y + 17, String(b), "tx"); });
        T(cRule, y + 17, allowed ? "oui" : "non (interdit)", allowed ? "tx" : "tx-b");
        T(cIneq, y + 17, sat ? "vérifiée" : "violée", sat ? "tx" : "tx-b");
        T(cOk, y + 17, agree ? "✓" : "✗", agree ? "tx-b t3" : "tx-b t6");
      });
      var txt;
      if (!bad.length) txt = "Traduction correcte : l'inégalité rejette exactement les combinaisons interdites par la règle.";
      else txt = "Traduction fausse sur " + bad.length + " ligne(s) : " + bad.map(function (b) { return "(" + b.v.join(", ") + ") " + (b.allowed ? "est permise mais rejetée" : "est interdite mais acceptée"); }).join(" ; ") + ".";
      if (+ruleSel.value === 5 && +cand.value === 1) txt += "\nMême table que la paire xa ≤ xb, xa ≤ xc, mais relaxation plus faible : (xa, xb, xc) = (1/2, 1, 0) vérifie 2xa ≤ xb + xc et viole xa ≤ xc.";
      if (+ruleSel.value === 3) txt += "\nLa contraposée a la même table que « si a alors b » : la même inégalité xa ≤ xb la traduit (diapo 62).";
      ro.textContent = txt;
    }
    fillCands(); draw(); redrawers.push(draw);
  };
