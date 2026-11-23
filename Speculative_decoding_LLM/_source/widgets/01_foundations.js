  // widgets/01_foundations.js — interactive figures of page 1 (inserted in the scope of app.js).

  /* ---------------------------------------------------------------------------------------------
     p1step — one drafted token: accepted mass min(p, q), residual, and the distribution of the output.
     --------------------------------------------------------------------------------------------- */
  WIDGETS.p1step = function (box) {
    var s = scaffold(box, "One drafted token: what is kept, what is rejected, what comes out");
    var PRE = {
      a: { n: ["“Paris”", "“the”", "“a”"], p: [0.6, 0.3, 0.1], q: [0.3, 0.5, 0.2] },
      close: { n: ["A", "B", "C", "D", "E"], p: [0.42, 0.25, 0.15, 0.10, 0.08], q: [0.38, 0.28, 0.16, 0.09, 0.09] },
      sure: { n: ["A", "B", "C", "D", "E"], p: [0.35, 0.25, 0.20, 0.12, 0.08], q: [0.85, 0.06, 0.04, 0.03, 0.02] },
      wrong: { n: ["A", "B", "C", "D", "E"], p: [0.50, 0.20, 0.15, 0.10, 0.05], q: [0.10, 0.60, 0.15, 0.10, 0.05] },
      greedy: { n: ["A", "B", "C", "D", "E"], p: [0, 1, 0, 0, 0], q: [0.25, 0.45, 0.15, 0.10, 0.05] }
    };
    var names, p, q, emp = null, empAcc = 0, seed = 7;
    var sel = select(s.controls, "Example", [["a", "worked example A"], ["close", "a drafter close to the target"], ["sure", "an over-confident drafter"],
      ["wrong", "a drafter with the wrong favourite"], ["greedy", "a greedy target (p on one token)"], ["custom", "your own (drag the bars)"]], "a",
      function () { if (PRE[sel.value]) load(sel.value); });
    var mode = select(s.controls, "After a rejection, draw from", [["res", "the residual (the exact rule)"], ["p", "a fresh sample from p (wrong)"]], "res",
      function () { emp = null; draw(); });
    button(s.controls, "Draw 20 000 tokens", function () { simulate(20000); draw(); });
    var out = readout(s.controls);
    var table = tableView(box);
    legend(s.legend, [["--s2", "draft q", "bar"], ["--s1", "target p", "bar"], ["--s3", "accepted: min(p, q)", "bar"],
      ["--text", "output of the rule (computed)", "dot"], ["--text", "observed in the draws"]]);
    var plot = new Plot(s.svg, { w: 600, h: 330, x: [0, 3], y: [0, 1], pad: { l: 44, r: 14, t: 24, b: 34 },
      label: "Bars of the target and draft distributions on a small vocabulary, with the accepted mass and the distribution of the output" });
    var targets = [];

    function load(k) { names = PRE[k].n.slice(); p = PRE[k].p.slice(); q = PRE[k].q.slice(); emp = null; draw(); }
    function replacement() { return mode.value === "res" ? residual(p, q) : p; }
    function outDist() {
      var b = overlap(p, q), r = replacement();
      return p.map(function (pv, i) { return Math.min(pv, q[i]) + (r ? (1 - b) * r[i] : 0); });
    }
    function simulate(n) {
      var rng = mulberry32(seed++), cnt = p.map(function () { return 0; }), acc = 0, r = replacement();
      for (var k = 0; k < n; k++) {
        var x = sampleIndex(q, rng);
        if (rng() < Math.min(1, p[x] / q[x])) { acc++; cnt[x]++; } else cnt[r ? sampleIndex(r, rng) : x]++;
      }
      emp = cnt.map(function (c) { return c / n; }); empAcc = acc / n;
    }
    function draw() {
      var n = p.length, i;
      plot.o.x = [0, n]; plot.clear(); targets = [];
      var centers = []; for (i = 0; i < n; i++) centers.push(i + 0.5);
      plot.axes({ yticks: [0, 0.2, 0.4, 0.6, 0.8, 1], yd: 1, xticks: centers, xnames: names, noxgrid: true, noyaxis: true, ylabel: "probability" });
      var o = outDist(), r = residual(p, q), b = overlap(p, q), top = plot.pad.t, hgt = plot.H - plot.pad.b - plot.pad.t;
      var rows = [];
      for (i = 0; i < n; i++) (function (i) {
        var X = plot.tx(i + 0.5), m = Math.min(p[i], q[i]);
        el("rect", { x: X - 30, y: plot.ty(m), width: 60, height: Math.max(0, plot.ty(0) - plot.ty(m)), "class": "a3" }, plot.g);
        el("line", { x1: X - 30, x2: X + 30, y1: plot.ty(m), y2: plot.ty(m), "class": "ln c3 thin" }, plot.g);
        var bq = plot.bar(i + 0.5, -13, 22, q[i], "f2"), bp = plot.bar(i + 0.5, 13, 22, p[i], "f1");
        if (emp) el("line", { x1: X + 1, x2: X + 25, y1: plot.ty(emp[i]), y2: plot.ty(emp[i]), "class": "ln ck thin" }, plot.g);
        el("circle", { cx: X + 13, cy: plot.ty(o[i]), r: 4.5, "class": "fk ring" }, plot.g);
        var info = function () {
          var rr = [["--s1", "target p", fmt(p[i], 3)], ["--s2", "draft q", fmt(q[i], 3)], ["--s3", "kept: min(p, q)", fmt(m, 3)],
            [null, "accepted with probability", fmt(q[i] > 0 ? Math.min(1, p[i] / q[i]) : NaN, 3)], ["--text", "output of the rule", fmt(o[i], 3)]];
          if (emp) rr.push([null, "observed in the draws", fmt(emp[i], 3)]);
          return { title: "token " + names[i], rows: rr };
        };
        hoverable(el("rect", { x: X - 36, y: top, width: 72, height: hgt, "class": "hit" }, plot.svg), info, [bq, bp]);
        hoverable(el("rect", { x: X - 25, y: top, width: 24, height: hgt, "class": "hit drag" }, plot.svg), info, [bq], true);
        hoverable(el("rect", { x: X + 1, y: top, width: 24, height: hgt, "class": "hit drag" }, plot.svg), info, [bp], true);
        targets.push({ x: X - 13, w: 22, s: 0, i: i }, { x: X + 13, w: 22, s: 1, i: i });
        rows.push([names[i], fmt(p[i], 3), fmt(q[i], 3), fmt(m, 3), fmt(q[i] > 0 ? Math.min(1, p[i] / q[i]) : NaN, 3), r ? fmt(r[i], 3) : "—", fmt(o[i], 3)]);
      })(i);
      var bias = tvDist(o, p);
      out.textContent = "acceptance probability  β = Σ min(p, q) = " + fmt(b, 3) + "      total variation  TV(p, q) = " + fmt(1 - b, 3) +
        "\ndistance between the output of the rule and the target:  TV = " + fmt(bias, 3) + (bias < 5e-4 ? "  (exact)" : "  (biased: the output is not p)") +
        (emp ? "\nobserved over 20 000 draws: " + fmt(100 * empAcc, 1) + "% of the drafts accepted" : "");
      table(["token", "target p", "draft q", "kept min(p, q)", "accepted with prob.", "residual", "output"], rows);
    }
    dragBars(s.svg, plot, function () { return targets; }, function (si, i, v) {
      if (si === 0) q = setBar(q, i, v); else p = setBar(p, i, v);
      emp = null; sel.value = "custom"; draw();
    });
    load("a");
  };

  /* ---------------------------------------------------------------------------------------------
     p1rounds — simulate rounds with i.i.d. acceptances: tokens per round against the formula.
     --------------------------------------------------------------------------------------------- */
  WIDGETS.p1rounds = function (box) {
    var s = scaffold(box, "Rounds: how many tokens does one call of the target produce?");
    var strip = document.createElement("div"); strip.className = "toks w-html"; box.insertBefore(strip, s.svg);
    var rng = mulberry32(20221130), counts = [], rounds = 0, sumTok = 0, last = -1;
    var sa = slider(s.controls, "acceptance rate α", 0.3, 0.95, 0.05, 0.8, reset);
    var sg = slider(s.controls, "draft length γ", 1, 12, 1, 5, reset);
    button(s.controls, "One round", function () { play(1); });
    button(s.controls, "1000 rounds", function () { play(1000); });
    button(s.controls, "Reset", reset);
    var out = readout(s.controls);
    var table = tableView(box);
    legend(s.legend, [["--s1", "observed share of the rounds", "bar"], ["--text", "probability given by the formula", "dot"]]);
    var plot = new Plot(s.svg, { w: 600, h: 280, x: [0.4, 6.6], y: [0, 0.4], pad: { l: 44, r: 14, t: 24, b: 40 },
      label: "Histogram of the number of tokens produced by a round, with the probabilities of the formula" });

    function theory(a, g) { var t = []; for (var k = 1; k <= g; k++) t.push(Math.pow(a, k - 1) * (1 - a)); t.push(Math.pow(a, g)); return t; }
    function tok(cls, txt) { var e = document.createElement("span"); e.className = "tok " + cls; e.textContent = txt; e.style.textDecoration = "none"; return e; }
    function reset() {
      var g = sg.get(); counts = []; for (var k = 0; k <= g; k++) counts.push(0);
      rounds = 0; sumTok = 0; last = -1; draw();
    }
    function play(n) {
      var a = sa.get(), g = sg.get();
      for (var r = 0; r < n; r++) { var acc = 0; while (acc < g && rng() < a) acc++; counts[acc]++; rounds++; sumTok += acc + 1; last = acc; }
      draw();
    }
    function draw() {
      var a = sa.get(), g = sg.get(), th = theory(a, g), k;
      sa.out.textContent = fmt(a, 2); sg.out.textContent = String(g);
      // the last round, token by token
      strip.textContent = "";
      var lab = document.createElement("span"); lab.className = "lab"; lab.textContent = last < 0 ? "no round yet" : "last round"; strip.appendChild(lab);
      if (last >= 0) {
        for (k = 0; k < last; k++) strip.appendChild(tok("ok", "✓"));
        if (last < g) strip.appendChild(tok("no", "✗"));
        strip.appendChild(tok("fix", "p"));
        for (k = last + 1; k < g; k++) strip.appendChild(tok("dim", "·"));
        var end = document.createElement("span"); end.className = "lab"; end.style.marginLeft = "0.5rem";
        end.textContent = "→ " + (last + 1) + " token" + (last ? "s" : "") + "  (✓ accepted draft, ✗ rejected draft, p token written by the target, · discarded)";
        end.style.minWidth = "0"; strip.appendChild(end);
      }
      // histogram
      var ymax = Math.max(0.2, Math.ceil(Math.max.apply(null, th) * 10 + 0.5) / 10);
      plot.o.x = [0.4, g + 1.6]; plot.o.y = [0, ymax]; plot.clear();
      var xt = [], yt = []; for (k = 1; k <= g + 1; k++) xt.push(k);
      for (var y = 0; y <= ymax + 1e-9; y += ymax > 0.6 ? 0.2 : 0.1) yt.push(y);
      plot.axes({ xticks: xt, yticks: yt, yd: 1, noxgrid: true, noyaxis: true, xlabel: "tokens produced by the round", ylabel: "share of the rounds" });
      var rows = [], bw = Math.min(24, (plot.W - plot.pad.l - plot.pad.r) / (g + 1.2) - 6), top = plot.pad.t, hgt = plot.H - plot.pad.b - plot.pad.t;
      var colW = (plot.W - plot.pad.l - plot.pad.r) / (g + 1.2);
      for (k = 1; k <= g + 1; k++) (function (k) {
        var f = rounds ? counts[k - 1] / rounds : 0;
        var bar = plot.bar(k, 0, bw, f, "f1");
        plot.dot(k, th[k - 1], 4.5, "fk");
        hoverable(el("rect", { x: plot.tx(k) - colW / 2, y: top, width: colW, height: hgt, "class": "hit" }, plot.svg), function () {
          return { title: k + " token" + (k > 1 ? "s" : "") + (k === g + 1 ? " (all drafts accepted)" : ""),
            rows: [["--s1", "observed share", rounds ? fmt(f, 3) : "—"], ["--text", "formula", fmt(th[k - 1], 3)]] };
        }, [bar]);
        rows.push([String(k), String(counts[k - 1]), rounds ? fmt(f, 3) : "—", fmt(th[k - 1], 4)]);
      })(k);
      var mean = (1 - Math.pow(a, g + 1)) / (1 - a);
      out.textContent = "rounds played: " + rounds + "      tokens per round: observed " + (rounds ? fmt(sumTok / rounds, 3) : "—") + ", formula " + fmt(mean, 3) +
        "\naccepted drafts per round (formula): " + fmt(mean - 1, 3) + "      drafts discarded per round: " + fmt(g - (mean - 1), 3) +
        "  (" + fmt(100 * (g - (mean - 1)) / g, 0) + "% of the drafter's work)";
      table(["tokens in the round", "rounds", "observed share", "formula"], rows);
    }
    reset();
    play(200); // a first batch, so that the page does not open on an empty histogram
  };

  /* ---------------------------------------------------------------------------------------------
     p1speed — the speed-up law as a function of the draft length.
     --------------------------------------------------------------------------------------------- */
  WIDGETS.p1speed = function (box) {
    var s = scaffold(box, "The speed-up law: speed-up against the draft length γ");
    var GMAX = 30;
    var sa = slider(s.controls, "acceptance rate α", 0.3, 0.95, 0.01, 0.8, draw);
    var sc = slider(s.controls, "cost of the drafter c", 0, 0.5, 0.01, 0.05, draw);
    var out = readout(s.controls);
    var table = tableView(box);
    legend(s.legend, [["--s1", "your acceptance rate α"], ["--muted", "α − 0.1 and α + 0.1"], ["--muted", "no gain (speed-up 1)", "dash"]]);
    var plot = new Plot(s.svg, { w: 600, h: 330, x: [0, GMAX + 1], y: [0, 4], pad: { l: 44, r: 62, t: 24, b: 40 },
      label: "Speed-up of speculative decoding as a function of the draft length, for three acceptance rates" });

    function tokens(a, g) { return (1 - Math.pow(a, g + 1)) / (1 - a); }
    function speed(a, g, c) { return tokens(a, g) / (g * c + 1); }
    function draw() {
      var a = sa.get(), c = sc.get(), lo = Math.max(0.01, a - 0.1), hi = Math.min(0.99, a + 0.1), g;
      sa.out.textContent = fmt(a, 2); sc.out.textContent = fmt(c, 2);
      var best = 1, m = 0;
      for (g = 1; g <= GMAX; g++) { if (speed(a, g, c) > speed(a, best, c)) best = g; m = Math.max(m, speed(a, g, c), speed(hi, g, c)); }
      var steps = [2, 3, 4, 6, 8, 12, 16, 24], ymax = 24;
      for (var k = 0; k < steps.length; k++) if (m <= steps[k] * 0.96) { ymax = steps[k]; break; }
      plot.o.y = [0, ymax]; plot.clear();
      var yt = [], st = ymax <= 4 ? 1 : ymax <= 8 ? 2 : 4;
      for (var y = 0; y <= ymax; y += st) yt.push(y);
      plot.axes({ xticks: [1, 5, 10, 15, 20, 25, 30], yticks: yt, noxgrid: true, xlabel: "draft length γ", ylabel: "speed-up (×)" });
      plot.seg(0, 1, GMAX + 1, 1, "ln cm thin dash");
      var xs = [], P = [], L = [], Hh = [], rows = [];
      for (g = 1; g <= GMAX; g++) {
        xs.push(g); P.push([g, speed(a, g, c)]); L.push([g, speed(lo, g, c)]); Hh.push([g, speed(hi, g, c)]);
        rows.push([String(g), fmt(tokens(a, g), 3), fmt(g * c + 1, 2), fmt(speed(a, g, c), 3), fmt(speed(lo, g, c), 3), fmt(speed(hi, g, c), 3)]);
      }
      plot.poly(L, "ln cm thin"); plot.poly(Hh, "ln cm thin"); plot.poly(P, "ln c1");
      plot.text(GMAX, speed(lo, GMAX, c), "α = " + fmt(lo, 2), "tx-s", "start", 6, 4);
      plot.text(GMAX, speed(hi, GMAX, c), "α = " + fmt(hi, 2), "tx-s", "start", 6, 4);
      var sb = speed(a, best, c);
      plot.dot(best, sb, 5, "f1");
      plot.text(best, sb, "best: γ = " + best + ", ×" + fmt(sb, 2), "tx-b", best > 20 ? "end" : "start", best > 20 ? -9 : 9, -9);
      plot.crosshair(xs, function (i) {
        var gg = xs[i];
        return { title: "draft length γ = " + gg, rows: [["--s1", "speed-up, α = " + fmt(a, 2), "×" + fmt(speed(a, gg, c), 2)],
          ["--muted", "speed-up, α = " + fmt(hi, 2), "×" + fmt(speed(hi, gg, c), 2)], ["--muted", "speed-up, α = " + fmt(lo, 2), "×" + fmt(speed(lo, gg, c), 2)],
          [null, "tokens per round", fmt(tokens(a, gg), 2)], [null, "time of a round (target calls)", fmt(gg * c + 1, 2)]] };
      });
      out.textContent = (a > c ? "α > c: a gain exists.  " : "α ≤ c: no draft length gives a gain.  ") + "Best draft length γ = " + best + ":  speed-up ×" + fmt(sb, 2) +
        ",  " + fmt(tokens(a, best), 2) + " tokens per round,  a round lasts " + fmt(best * c + 1, 2) + " target calls." +
        "\nWith α = " + fmt(hi, 2) + " the best speed-up would be ×" + fmt(bestOf(hi, c), 2) + ";  with α = " + fmt(lo, 2) + ", ×" + fmt(bestOf(lo, c), 2) + ".";
      table(["γ", "tokens per round", "time of a round", "speed-up (your α)", "speed-up (α − 0.1)", "speed-up (α + 0.1)"], rows);
    }
    function bestOf(a, c) { var b = 0; for (var g = 1; g <= 60; g++) b = Math.max(b, speed(a, g, c)); return b; }
    draw();
  };
