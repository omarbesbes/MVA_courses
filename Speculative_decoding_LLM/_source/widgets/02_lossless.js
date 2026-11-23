  // widgets/02_lossless.js — interactive figures of page 2 (inserted in the scope of app.js).

  /* ---------------------------------------------------------------------------------------------
     p2tree — a toy drafter whose j-th candidate is the target's choice with probability a(1-a)^(j-1).
     Upper panel: the best tree for a node budget N (the N nodes of highest path probability).
     Lower panel: expected tokens per call of the target against the budget, chain versus best tree.
     --------------------------------------------------------------------------------------------- */
  WIDGETS.p2tree = function (box) {
    var s = scaffold(box, "The best tree for a node budget, and what it yields");
    var svg2 = addSvg(box, s.svg);
    var NMAX = 256, K = 48;
    var sa = slider(s.controls, "first-choice agreement <i>a</i>", 0.3, 0.9, 0.01, 0.7, draw);
    var sn = slider(s.controls, "node budget <i>N</i>", 1, 32, 1, 16, draw);
    var out = readout(s.controls);
    var table = tableView(box);
    legend(s.legend, [["--s2", "candidate token (larger = more likely to be kept)", "dot"], ["--s3", "best tree with N nodes"],
      ["--s5", "one chain of N tokens"], ["--muted", "limit of a chain", "dash"]]);

    // Best-first expansion: nodes come out by decreasing value, so the first N are the best tree of N nodes.
    function bestTree(a, N) {
      var r = [], j;
      for (j = 0; j < K; j++) r.push(a * Math.pow(1 - a, j));
      var cand = [{ v: r[0], d: 1, j: 0, par: -1 }], nodes = [];
      while (nodes.length < N && cand.length) {
        var b = 0;
        for (j = 1; j < cand.length; j++) if (cand[j].v > cand[b].v * (1 + 1e-12)) b = j;
        var c = cand.splice(b, 1)[0];
        c.id = nodes.length; c.kids = []; nodes.push(c);
        if (c.par >= 0) nodes[c.par].kids.push(c.id);
        cand.push({ v: c.v * r[0], d: c.d + 1, j: 0, par: c.id });
        if (c.j + 1 < K) cand.push({ v: c.v / r[c.j] * r[c.j + 1], d: c.d, j: c.j + 1, par: c.par });
      }
      return nodes;
    }
    function ranks(nodes, n) { var p = []; while (n) { p.unshift(n.j + 1); n = n.par >= 0 ? nodes[n.par] : null; } return p; }

    function draw() {
      var a = sa.get(), N = sn.get(), i;
      sa.out.textContent = fmt(a, 2); sn.out.textContent = String(N);
      var all = bestTree(a, NMAX), cumT = [], cumC = [], t = 0, c = 0;
      for (i = 0; i < NMAX; i++) { t += all[i].v; c += Math.pow(a, i + 1); cumT.push(1 + t); cumC.push(1 + c); }

      /* ---- upper panel: the tree ---- */
      var nodes = bestTree(a, N), roots = [], slot = 0, depth = 0, leaves = 0;
      nodes.forEach(function (n) { if (n.par < 0) roots.push(n.id); if (n.d > depth) depth = n.d; });
      function place(id) {
        var n = nodes[id];
        if (!n.kids.length) { n.y = slot++; leaves++; return; }
        n.kids.forEach(place);
        n.y = nodes[n.kids[0]].y;
      }
      roots.forEach(place);
      var gap = 17, H = Math.max(130, 26 + 34 + (slot - 1) * gap + 16);
      var top = new Plot(s.svg, { w: 600, h: H, x: [-0.6, Math.max(depth, 6) + 0.6], y: [slot - 0.5, -0.9], pad: { l: 14, r: 14, t: 26, b: 34 },
        label: "The best tree of " + N + " candidate tokens for a drafter whose first choice is right with probability " + fmt(a, 2) });
      var xt = []; for (i = 1; i <= Math.max(depth, 6); i++) xt.push(i);
      top.axes({ xticks: xt, nogrid: true, noyaxis: true, xlabel: "position in the draft", ylabel: "context → candidates (first choice on the top row, alternatives below)" });
      var rootY = nodes[roots[0]].y;
      nodes.forEach(function (n) {
        var px = n.par >= 0 ? nodes[n.par].d : 0, py = n.par >= 0 ? nodes[n.par].y : rootY;
        top.seg(px, py, n.d, n.y, "ln cm hair");
      });
      el("rect", { x: top.tx(0) - 9, y: top.ty(rootY) - 9, width: 18, height: 18, rx: 4, "class": "am ln cm thin" }, top.g);
      nodes.forEach(function (n) {
        var dot = top.dot(n.d, n.y, 2.2 + 8 * Math.sqrt(n.v), "f2");
        hoverable(dot, function () {
          return { title: "position " + n.d + ", candidate ranks " + ranks(nodes, n).join(" → "),
            rows: [["--s2", "probability that this token is kept", pct(n.v, 1)]] };
        }, [dot]);
      });

      /* ---- lower panel: tokens per call against the budget ---- */
      var ymax = Math.ceil(Math.max(cumT[NMAX - 1], 1 / (1 - a)) + 0.6);
      var bot = new Plot(svg2, { w: 600, h: 250, x: [1, NMAX], y: [1, ymax], xlog: true, pad: { l: 44, r: 18, t: 26, b: 40 },
        label: "Expected tokens per call of the target as a function of the node budget, for one chain and for the best tree" });
      var yt = []; for (i = 1; i <= ymax; i += (ymax > 8 ? 2 : 1)) yt.push(i);
      bot.axes({ xticks: [1, 2, 4, 8, 16, 32, 64, 128, 256], yticks: yt, noxgrid: true,
        xlabel: "node budget N (logarithmic scale)", ylabel: "expected tokens per call of the target" });
      var lim = 1 / (1 - a);
      bot.seg(1, lim, NMAX, lim, "ln cm thin dash");
      var T = [], C = [], xs = [];
      for (i = 0; i < NMAX; i++) { xs.push(i + 1); T.push([i + 1, cumT[i]]); C.push([i + 1, cumC[i]]); }
      bot.poly(C, "ln c5"); bot.poly(T, "ln c3");
      bot.seg(N, 1, N, ymax, "cross");
      bot.dot(N, cumC[N - 1], 4.5, "f5"); bot.dot(N, cumT[N - 1], 4.5, "f3");
      bot.crosshair(xs, function (k) {
        return { title: "budget of " + xs[k] + (xs[k] > 1 ? " nodes" : " node"), rows: [["--s3", "best tree", fmt(cumT[k], 2)], ["--s5", "one chain", fmt(cumC[k], 2)], ["--muted", "limit of a chain", fmt(lim, 2)]] };
      });

      out.textContent = "best tree with " + N + (N > 1 ? " nodes: " : " node: ") + fmt(cumT[N - 1], 2) + " tokens per call of the target (" + depth + (depth > 1 ? " positions deep, " : " position deep, ") + leaves + (leaves > 1 ? " branches)" : " branch)") +
        "\none chain of " + N + (N > 1 ? " tokens: " : " token: ") + fmt(cumC[N - 1], 2) + "   (a chain never exceeds " + fmt(lim, 2) + ")" +
        "\nfrom 128 to 256 nodes the best tree gains " + fmt(cumT[255] - cumT[127], 2) + " token" + (cumT[255] - cumT[127] >= 1.995 ? "s" : "") + "; from 16 to 32 nodes, " + fmt(cumT[31] - cumT[15], 2);
      var rows = [];
      [1, 2, 4, 8, 16, 32, 64, 128, 256].forEach(function (n) { rows.push([String(n), fmt(cumC[n - 1], 2), fmt(cumT[n - 1], 2)]); });
      table(["node budget N", "one chain: tokens per call", "best tree: tokens per call"], rows);
    }
    draw();
  };

  /* ---------------------------------------------------------------------------------------------
     p2load — a toy model of load. A pass that scores n positions costs 1 + κ n. With B sequences in the
     batch, plain decoding advances one token in 1 + κB; a speculative round costs γc(1 + κB) for the
     draft and 1 + κB(γ + 1) for the verification, and yields τ = (1 − α^(γ+1)) / (1 − α) tokens.
     --------------------------------------------------------------------------------------------- */
  WIDGETS.p2load = function (box) {
    var s = scaffold(box, "A toy model of load: the same method at different batch sizes");
    var sa = slider(s.controls, "acceptance rate α", 0.4, 0.95, 0.01, 0.7, draw);
    var sg = slider(s.controls, "draft length γ", 1, 16, 1, 5, draw);
    var sc = slider(s.controls, "drafter cost <i>c</i>", 0, 0.3, 0.01, 0.05, draw);
    var sk = slider(s.controls, "cost of one more position κ", 0.001, 0.03, 0.001, 0.005, draw);
    var out = readout(s.controls);
    var table = tableView(box);
    legend(s.legend, [["--s3", "speed-up with the draft length γ chosen above"], ["--s5", "speed-up with the best draft length for each batch size", "dash"], ["--muted", "no gain", "dash"]]);
    var BS = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256];

    function tau(al, g) { return (1 - Math.pow(al, g + 1)) / (1 - al); }
    function sp(al, g, c, k, B) { var x = k * B; return tau(al, g) * (1 + x) / (g * c * (1 + x) + 1 + (g + 1) * x); }
    function best(al, c, k, B) { var bg = 0, bv = 1; for (var g = 1; g <= 32; g++) { var v = sp(al, g, c, k, B); if (v > bv + 1e-12) { bv = v; bg = g; } } return { g: bg, v: bv }; }

    function draw() {
      var al = sa.get(), g = sg.get(), c = sc.get(), k = sk.get(), i;
      sa.out.textContent = fmt(al, 2); sg.out.textContent = String(g); sc.out.textContent = fmt(c, 2); sk.out.textContent = fmt(k, 3);
      var cur = [], env = [], top = 1.2;
      for (i = 0; i <= 160; i++) {
        var B = Math.pow(256, i / 160), v = sp(al, g, c, k, B), b = best(al, c, k, B);
        cur.push([B, v]); env.push([B, b.v]); top = Math.max(top, v, b.v);
      }
      var ymax = Math.ceil(top * 2 + 0.4) / 2;
      var plot = new Plot(s.svg, { w: 600, h: 290, x: [1, 256], y: [0, ymax], xlog: true, pad: { l: 44, r: 18, t: 26, b: 40 },
        label: "Speed-up of speculative decoding over plain decoding as a function of the batch size, in a toy cost model" });
      var yt = []; for (i = 0; i <= ymax + 1e-9; i += (ymax > 5 ? 1 : 0.5)) yt.push(i);
      plot.axes({ xticks: [1, 2, 4, 8, 16, 32, 64, 128, 256], yticks: yt, yd: ymax > 5 ? 0 : 1, noxgrid: true,
        xlabel: "sequences decoded together (batch size, logarithmic scale)", ylabel: "speed-up over plain decoding at the same batch size" });
      plot.seg(1, 1, 256, 1, "ln cm thin dash");
      plot.poly(env, "ln c5 dash"); plot.poly(cur, "ln c3");
      // break-even batch size: tau(1 + x) = γc(1 + x) + 1 + (γ + 1)x
      var t = tau(al, g), num = t - 1 - g * c, den = g + 1 + g * c - t, bstar = num > 0 && den > 0 ? num / den / k : (num > 0 ? Infinity : 0);
      if (bstar >= 1 && bstar <= 256) { plot.dot(bstar, 1, 5, "f6"); plot.text(bstar, 1, "break-even: " + fmt(bstar, 0) + " sequences", "tx-s", bstar > 40 ? "end" : "start", bstar > 40 ? -8 : 8, 16); }
      plot.crosshair(BS, function (j) {
        var b = best(al, c, k, BS[j]);
        return { title: "batch of " + BS[j] + (BS[j] > 1 ? " sequences" : " sequence"), rows: [["--s3", "speed-up with γ = " + g, "×" + fmt(sp(al, g, c, k, BS[j]), 2)],
          ["--s5", b.g ? "best draft length: γ = " + b.g : "best choice: no speculation", "×" + fmt(b.v, 2)]] };
      });
      var b1 = best(al, c, k, 1), b32 = best(al, c, k, 32), b128 = best(al, c, k, 128);
      function bl(b) { return b.g ? String(b.g) : "none (speculation off)"; }
      out.textContent = "draft length γ = " + g + ":  ×" + fmt(sp(al, g, c, k, 1), 2) + " at batch 1,  ×" + fmt(sp(al, g, c, k, 32), 2) + " at batch 32,  ×" + fmt(sp(al, g, c, k, 128), 2) + " at batch 128" +
        (bstar === 0 ? "\nno gain at any batch size" : bstar === Infinity ? "\nstill a gain at any batch size" : "\nno gain beyond about " + fmt(bstar, 0) + " sequences") +
        "\nbest draft length:  " + bl(b1) + " at batch 1,  " + bl(b32) + " at batch 32,  " + bl(b128) + " at batch 128" +
        "\n(toy model: a pass over n positions costs 1 + κn; real engines add memory limits and scheduling)";
      var rows = [];
      BS.forEach(function (B) { var b = best(al, c, k, B); rows.push([String(B), "×" + fmt(sp(al, g, c, k, B), 2), b.g ? String(b.g) : "no speculation", "×" + fmt(b.v, 2)]); });
      table(["batch size", "speed-up with γ = " + g, "best draft length", "speed-up with the best length"], rows);
    }
    draw();
  };
