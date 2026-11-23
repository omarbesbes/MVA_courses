  // widgets/03_relaxed.js — interactive figures of page 3 (inserted in the scope of app.js).

  /* ---------------------------------------------------------------------------------------------
     p3front — relaxed rules in the plane (bias, acceptance), with the front A = 1 - TV(p,q) + bias.
     --------------------------------------------------------------------------------------------- */
  WIDGETS.p3front = function (box) {
    var s = scaffold(box, "Relaxed rules: acceptance gained against bias paid");
    var svg2 = addSvg(box, s.svg);
    var PRE = {
      a: { n: ["“Paris”", "“the”", "“a”"], p: [0.6, 0.3, 0.1], q: [0.3, 0.5, 0.2] },
      four: { n: ["A", "B", "C", "D"], p: [0.4, 0.3, 0.2, 0.1], q: [0.1, 0.2, 0.3, 0.4] },
      zero: { n: ["A", "B", "C", "D"], p: [0.6, 0.4, 0, 0], q: [0.3, 0.3, 0.3, 0.1] },
      close: { n: ["A", "B", "C", "D", "E"], p: [0.42, 0.25, 0.15, 0.10, 0.08], q: [0.36, 0.30, 0.16, 0.09, 0.09] }
    };
    var FAM = [["len", "lenience (λ)"], ["mix", "mixture target (w)"], ["tok", "token rule (q on the top set of p)"],
      ["thr", "threshold on p(x), fresh sample of p"]];
    var names, p, q, targets = [];
    var sel = select(s.controls, "Example", [["a", "worked example A"], ["four", "four tokens (§7)"], ["zero", "a drafter that proposes forbidden tokens"],
      ["close", "a drafter close to the target"], ["custom", "your own (drag the bars)"]], "a", function () { if (PRE[sel.value]) load(sel.value); });
    var fam = select(s.controls, "Rule", FAM, "len", draw);
    var knob = slider(s.controls, "relaxation", 0, 1, 0.01, 0.25, draw);
    var out = readout(s.controls);
    var table = tableView(box, "Show the numbers (all four rules at this relaxation)");
    legend(s.legend, [["--s2", "draft q", "bar"], ["--s1", "target p", "bar"], ["--text", "output of the selected rule", "dot"],
      ["--s4", "selected rule, as the knob moves"], ["--muted", "the other rules"], ["--text", "front: nothing above"]]);
    var bars = new Plot(s.svg, { w: 600, h: 240, x: [0, 3], y: [0, 1], pad: { l: 44, r: 14, t: 24, b: 30 },
      label: "Target and draft distributions with the output distribution of the selected relaxed rule" });
    var plane = new Plot(svg2, { w: 600, h: 300, x: [0, 0.6], y: [0, 1], pad: { l: 48, r: 18, t: 22, b: 40 },
      label: "Acceptance against bias for four families of relaxed rules, with the front that no rule can exceed" });

    function load(k) { names = PRE[k].n.slice(); p = PRE[k].p.slice(); q = PRE[k].q.slice(); draw(); }
    // acceptance A and output distribution of rule kind at relaxation t in [0, 1] (0 = strictest)
    function rule(kind, t) {
      var n = p.length, i, A = 0, o = [], b = [], mx = Math.max.apply(null, p), res = residual(p, q) || p, par;
      if (kind === "len") {
        par = 1 - 0.97 * t;
        for (i = 0; i < n; i++) { b[i] = q[i] > 0 ? Math.min(1, p[i] / (par * q[i])) : 0; A += q[i] * b[i]; }
        for (i = 0; i < n; i++) o[i] = q[i] * b[i] + (1 - A) * res[i];
        return { A: A, out: o, par: "λ = " + fmt(par, 2) };
      }
      if (kind === "mix") {
        par = 1 - t;
        for (i = 0; i < n; i++) o[i] = par * p[i] + (1 - par) * q[i];
        return { A: overlap(o, q), out: o, par: "w = " + fmt(par, 2) };
      }
      par = 1 - t; // top set { v : p(v) >= par * max p }
      var top = p.map(function (v) { return v >= par * mx - 1e-12; }), eta = 0;
      for (i = 0; i < n; i++) if (!top[i]) eta += q[i];
      if (kind === "tok") {
        for (i = 0; i < n; i++) o[i] = (top[i] ? q[i] : 0) + p[i] * eta;
        return { A: overlap(o, q), out: o, par: "top set: p(x) ≥ " + fmt(par, 2) + " × max p" };
      }
      for (i = 0; i < n; i++) { A += top[i] ? q[i] : 0; }
      for (i = 0; i < n; i++) o[i] = (top[i] ? q[i] : 0) + (1 - A) * p[i];
      return { A: A, out: o, par: "accept iff p(x) ≥ " + fmt(par * mx, 3) };
    }
    function draw() {
      var n = p.length, i, t = knob.get(), cur = rule(fam.value, t), tv = tvDist(p, q);
      knob.out.textContent = cur.par;
      // ---- bars
      bars.o.x = [0, n]; bars.clear(); targets = [];
      var centers = []; for (i = 0; i < n; i++) centers.push(i + 0.5);
      bars.axes({ yticks: [0, 0.25, 0.5, 0.75, 1], yd: 2, xticks: centers, xnames: names, noxgrid: true, noyaxis: true, ylabel: "probability" });
      var top = bars.pad.t, hgt = bars.H - bars.pad.b - bars.pad.t;
      for (i = 0; i < n; i++) (function (i) {
        var X = bars.tx(i + 0.5);
        var bq = bars.bar(i + 0.5, -13, 22, q[i], "f2"), bp = bars.bar(i + 0.5, 13, 22, p[i], "f1");
        el("circle", { cx: X, cy: bars.ty(cur.out[i]), r: 4.5, "class": "fk ring" }, bars.g);
        var info = function () {
          return { title: "token " + names[i], rows: [["--s1", "target p", fmt(p[i], 3)], ["--s2", "draft q", fmt(q[i], 3)],
            ["--text", "output of the rule", fmt(cur.out[i], 3)], [null, "output ÷ target", p[i] > 0 ? fmt(cur.out[i] / p[i], 2) : (cur.out[i] > 1e-9 ? "∞ (forbidden token written)" : "—")]] };
        };
        hoverable(el("rect", { x: X - 36, y: top, width: 72, height: hgt, "class": "hit" }, bars.svg), info, [bq, bp]);
        hoverable(el("rect", { x: X - 25, y: top, width: 24, height: hgt, "class": "hit drag" }, bars.svg), info, [bq], true);
        hoverable(el("rect", { x: X + 1, y: top, width: 24, height: hgt, "class": "hit drag" }, bars.svg), info, [bp], true);
        targets.push({ x: X - 13, w: 22, s: 0, i: i }, { x: X + 13, w: 22, s: 1, i: i });
      })(i);
      // ---- plane
      var xmax = Math.max(0.3, Math.ceil((tv + 0.12) * 10) / 10);
      plane.o.x = [0, xmax]; plane.clear();
      var xt = []; for (var x = 0; x <= xmax + 1e-9; x += 0.1) xt.push(x);
      plane.axes({ xticks: xt, xd: 1, yticks: [0, 0.2, 0.4, 0.6, 0.8, 1], yd: 1, xlabel: "bias: TV(output, target)", ylabel: "acceptance" });
      plane.clip();
      plane.poly([[0, 1 - tv], [tv, 1], [0, 1], [0, 1 - tv]], "am");
      plane.poly([[0, 1 - tv], [tv, 1], [xmax, 1]], "ln ck thin");
      var rows = [];
      FAM.forEach(function (f) {
        var pts = [];
        for (var k = 0; k <= 100; k++) { var r = rule(f[0], k / 100); pts.push([tvDist(r.out, p), r.A]); }
        if (f[0] !== fam.value) plane.poly(pts, "ln cm thin");
        var r0 = rule(f[0], t);
        rows.push([f[1], r0.par, fmt(r0.A, 3), fmt(tvDist(r0.out, p), 3), fmt(1 - tv + tvDist(r0.out, p) - r0.A, 3)]);
      });
      var sp = [];
      for (var k2 = 0; k2 <= 100; k2++) { var r2 = rule(fam.value, k2 / 100); sp.push([tvDist(r2.out, p), r2.A]); }
      plane.poly(sp, "ln c4");
      plane.unclip();
      var bias = tvDist(cur.out, p);
      plane.dot(0, 1 - tv, 4, "fk"); plane.text(0, 1 - tv, "exact rule", "tx-s", "start", 8, 14);
      plane.dot(tv, 1, 4, "fk"); plane.text(tv, 1, "accept everything", "tx-s", tv > xmax * 0.6 ? "end" : "start", tv > xmax * 0.6 ? -8 : 8, 14);
      plane.text(0, 1, "impossible", "tx-s", "start", 8, 14);
      plane.dot(bias, cur.A, 6, "f4");
      var worst = 0, forb = false;
      for (i = 0; i < n; i++) { if (p[i] > 0) worst = Math.max(worst, cur.out[i] / p[i]); else if (cur.out[i] > 1e-9) forb = true; }
      var gap = 1 - tv + bias - cur.A;
      out.textContent = "exact rule: acceptance " + fmt(1 - tv, 3) + ", bias 0        selected rule: acceptance " + fmt(cur.A, 3) + ", bias " + fmt(bias, 3) +
        "\nacceptance gained " + fmt(cur.A - (1 - tv), 3) + " for a bias of " + fmt(bias, 3) + "   →   " + (gap < 5e-4 ? "on the front (nothing wasted)" : "below the front by " + fmt(gap, 3)) +
        "\nlargest output ÷ target over the tokens: " + (forb ? "∞ (a token with p = 0 can be written)" : fmt(worst, 2));
      table(["rule", "setting", "acceptance", "bias", "distance below the front"], rows);
    }
    dragBars(s.svg, bars, function () { return targets; }, function (si, i, v) {
      if (si === 0) q = setBar(q, i, v); else p = setBar(p, i, v);
      sel.value = "custom"; draw();
    });
    load("a");
  };

  /* ---------------------------------------------------------------------------------------------
     p3sets — accept sets of the deterministic rules (greedy decoding) on one toy target distribution.
     --------------------------------------------------------------------------------------------- */
  WIDGETS.p3sets = function (box) {
    var s = scaffold(box, "Which tokens does each rule accept? (greedy decoding)");
    var LOG = [3.0, 2.4, 1.6, 1.1, 0.6, 0.2, -0.3, -0.9];      // toy logits of the target, most likely first
    var Q = normalize([0.26, 0.30, 0.08, 0.14, 0.05, 0.09, 0.03, 0.05]); // a toy drafter: it prefers the target's second choice
    var NAMES = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"];
    var KN = {
      exact: null,
      topk: { lab: "k", min: 1, max: 5, step: 1, val: 2 },
      margin: { lab: "κ", min: 0.05, max: 1, step: 0.01, val: 0.4 },
      specdec: null,
      bild: { lab: "α<sub>RB</sub>", min: 0.5, max: 6, step: 0.1, val: 2 },
      typical: { lab: "ε (with δ = √ε)", min: 0.01, max: 0.25, step: 0.01, val: 0.09 }
    };
    var st = slider(s.controls, "how flat the target is (temperature)", 0.4, 2.5, 0.05, 1, draw);
    var sel = select(s.controls, "Rule", [["exact", "exact match"], ["topk", "top-k (Stern et al.)"], ["margin", "margin: p(x) ≥ κ · max p"],
      ["specdec", "SpecDec: top 3 and within e⁻¹ of the best"], ["bild", "BiLD rollback: p(x) ≥ exp(−α)"], ["typical", "typical acceptance (Medusa)"]], "typical", setRule);
    var kn = slider(s.controls, "knob", 0, 1, 0.01, 0.5, draw);
    var out = readout(s.controls);
    var table = tableView(box);
    legend(s.legend, [["--s3", "target's first choice (the exact rule accepts it)", "bar"], ["--s4", "accepted by the relaxed rule only", "bar"],
      ["--muted", "rejected if drafted", "bar"], ["--s2", "toy drafter q", "dot"], ["--text", "threshold of the rule", "dash"]]);
    var plot = new Plot(s.svg, { w: 600, h: 300, x: [0, 8], y: [0, 1], pad: { l: 44, r: 14, t: 24, b: 34 },
      label: "A toy target distribution with the set of tokens accepted by the selected relaxed rule" });

    function setRule() {
      var k = KN[sel.value], lab = kn.input.parentNode;
      lab.style.display = k ? "" : "none";
      if (k) { kn.input.min = k.min; kn.input.max = k.max; kn.input.step = k.step; kn.input.value = k.val; lab.firstChild.innerHTML = k.lab; }
      draw();
    }
    function draw() {
      var T = st.get(), i, n = LOG.length, rule = sel.value, v = kn.get();
      st.out.textContent = fmt(T, 2);
      var p = normalize(LOG.map(function (z) { return Math.exp(z / T); })), H = entropy(p), mx = p[0], thr = null, S = [], txt = "";
      if (rule === "exact") { S = p.map(function (x, k) { return k === 0; }); txt = "accept only the first choice"; }
      if (rule === "topk") { S = p.map(function (x, k) { return k < v; }); kn.out.textContent = String(v); txt = "accept the " + v + " most likely tokens"; }
      if (rule === "margin") { thr = v * mx; kn.out.textContent = fmt(v, 2); txt = "threshold κ · max p = " + fmt(thr, 3); }
      if (rule === "specdec") { thr = Math.exp(-1) * mx; txt = "top 3, and p(x) ≥ e⁻¹ · max p = " + fmt(thr, 3); }
      if (rule === "bild") { thr = Math.exp(-v); kn.out.textContent = fmt(v, 1); txt = "floor exp(−α) = " + fmt(thr, 3); }
      if (rule === "typical") { var d = Math.sqrt(v); thr = Math.min(v, d * Math.exp(-H)); kn.out.textContent = fmt(v, 2) + ", δ = " + fmt(d, 2);
        txt = "threshold min(ε, δ·e^(−H)) = min(" + fmt(v, 3) + ", " + fmt(d * Math.exp(-H), 3) + ") = " + fmt(thr, 3); }
      if (thr !== null) S = p.map(function (x, k) { return k === 0 || (x >= thr - 1e-12 && (rule !== "specdec" || k < 3)); });
      var ymax = mx > 0.6 ? 1 : mx > 0.4 ? 0.6 : 0.4;
      plot.o.y = [0, ymax]; plot.clear();
      var centers = [], yt = []; for (i = 0; i < n; i++) centers.push(i + 0.5);
      for (var y = 0; y <= ymax + 1e-9; y += ymax / 4) yt.push(y);
      plot.axes({ yticks: yt, yd: 2, xticks: centers, xnames: NAMES, noxgrid: true, noyaxis: true, ylabel: "target probability p(x)", xlabel: "tokens, by rank under the target" });
      if (thr !== null && thr <= ymax) plot.seg(0, thr, n, thr, "ln ck thin dash");
      var rows = [], mass = 0, acc = 0, top = plot.pad.t, hgt = plot.H - plot.pad.b - plot.pad.t, cnt = 0;
      for (i = 0; i < n; i++) (function (i) {
        var cls = i === 0 ? "f3" : S[i] ? "f4" : "fm", status = i === 0 ? "first choice" : S[i] ? "accepted (relaxed)" : "rejected";
        var b = plot.bar(i + 0.5, 0, 24, p[i], cls);
        el("circle", { cx: plot.tx(i + 0.5), cy: plot.ty(Math.min(Q[i], ymax)), r: 4, "class": "f2 ring" }, plot.g);
        if (S[i]) { mass += p[i]; acc += Q[i]; cnt++; }
        hoverable(el("rect", { x: plot.tx(i + 0.5) - 30, y: top, width: 60, height: hgt, "class": "hit" }, plot.svg), function () {
          return { title: NAMES[i] + " token: " + status, rows: [["--s1", "target probability p", fmt(p[i], 3)], ["--s2", "drafter probability q", fmt(Q[i], 3)]] };
        }, [b]);
        rows.push([NAMES[i], fmt(p[i], 3), fmt(Q[i], 3), status]);
      })(i);
      out.textContent = "entropy of the target: " + fmt(H, 2) + " nats        " + txt +
        "\naccept set: " + cnt + " token" + (cnt > 1 ? "s" : "") + ", carrying " + fmt(100 * mass, 0) + "% of the target's probability" +
        "\nwith the toy drafter: draft accepted with probability " + fmt(acc, 2) + " (exact rule: " + fmt(Q[0], 2) + ");  output ≠ target's choice with probability " + fmt(acc - Q[0], 2);
      table(["token (rank under the target)", "target p", "drafter q", "status"], rows);
    }
    setRule();
  };
