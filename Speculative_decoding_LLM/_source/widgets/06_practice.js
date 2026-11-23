  // widgets/06_practice.js — interactive figures of page 6 (inserted in the scope of app.js).

  /* ---------------------------------------------------------------------------------------------
     p6class — LANTERN on a toy codebook of 24 codes laid out on a line (neighbours on the axis are
     neighbours in latent space). The drafter proposes one code with certainty; the exact test accepts
     it with the target's probability of that code; the relaxed test with the mass of the set A(k, δ).
     --------------------------------------------------------------------------------------------- */
  WIDGETS.p6class = function (box) {
    var s = scaffold(box, "Accepting on the mass of the neighbours (toy codebook)");
    var P = [0.004, 0.006, 0.008, 0.010, 0.014, 0.022, 0.050, 0.085, 0.060, 0.110, 0.075, 0.130, 0.090, 0.065, 0.035, 0.020, 0.012, 0.016, 0.040, 0.058, 0.036, 0.022, 0.018, 0.014];
    var n = P.length;
    var sx = slider(s.controls, "drafted code", 1, n, 1, 11, draw);
    var sk = slider(s.controls, "neighbours considered <i>k</i>", 0, 12, 1, 8, draw);
    var sd = slider(s.controls, "budget δ", 0, 0.5, 0.01, 0.3, draw);
    var out = readout(s.controls);
    var table = tableView(box);
    legend(s.legend, [["--s1", "target probability of a code", "bar"], ["--s2", "the drafted code", "bar"], ["--s4", "neighbours counted with it (their mass moves onto the drafted code)", "bar"]]);

    // nearest codes first (distance on the line; the lower index first when two are at the same distance)
    function neighbours(x, k) {
      var ord = [];
      for (var d = 1; ord.length < k && d < n; d++) {
        if (x - d >= 0 && ord.length < k) ord.push(x - d);
        if (x + d < n && ord.length < k) ord.push(x + d);
      }
      return ord;
    }
    function draw() {
      var x = sx.get() - 1, k = sk.get(), delta = sd.get(), i;
      sx.out.textContent = String(x + 1); sk.out.textContent = String(k); sd.out.textContent = fmt(delta, 2);
      var cand = neighbours(x, k), inA = {}, tv = 0, cnt = 0;
      for (i = 0; i < cand.length; i++) { if (tv + P[cand[i]] >= delta) break; tv += P[cand[i]]; inA[cand[i]] = true; cnt++; }
      var agg = P[x] + tv;
      var ymax = Math.max(0.2, Math.ceil(agg * 1.12 * 20) / 20);
      var plot = new Plot(s.svg, { w: 600, h: 300, x: [0.3, n + 0.7], y: [0, ymax], pad: { l: 44, r: 14, t: 28, b: 40 },
        label: "Target probability of each code of a toy codebook; the drafted code and the neighbours whose probability is counted with it" });
      var yt = []; for (i = 0; i <= ymax + 1e-9; i += (ymax > 0.42 ? 0.1 : 0.05)) yt.push(i);
      var xt = []; for (i = 1; i <= n; i += 1) xt.push(i);
      plot.axes({ xticks: xt, yticks: yt, yd: 2, noxgrid: true, xlabel: "codes, ordered so that neighbours are similar", ylabel: "probability" });
      if (cand.length) {
        var lo = Math.min.apply(null, cand.concat([x])) + 1, hi = Math.max.apply(null, cand.concat([x])) + 1;
        plot.seg(lo - 0.4, ymax * 0.965, hi + 0.4, ymax * 0.965, "ln cm thin");
        plot.text((lo + hi) / 2, ymax * 0.965, "the " + k + " nearest codes", "tx-s", "middle", 0, -5);
      }
      var rows = [];
      for (i = 0; i < n; i++) (function (i) {
        var marks = [], state = i === x ? "drafted code" : inA[i] ? "counted with the drafted code" : "unchanged";
        if (i === x) {
          marks.push(plot.bar(i + 1, 0, 15, P[i], "f2"));
          if (agg > P[i] + 1e-9) marks.push(plot.bar(i + 1, 0, 15, agg, "f4", P[i]));
        } else if (inA[i]) marks.push(plot.bar(i + 1, 0, 15, P[i], "a4 ln c4 thin"));
        else marks.push(plot.bar(i + 1, 0, 15, P[i], "f1"));
        var after = i === x ? agg : inA[i] ? 0 : P[i];
        marks.forEach(function (m, j) {
          hoverable(m, function () {
            return { title: "code " + (i + 1) + " — " + state, rows: [["--s1", "target probability", fmt(P[i], 3)], [i === x ? "--s2" : inA[i] ? "--s4" : "--s1", "in the distorted target", fmt(after, 3)]] };
          }, marks, j > 0);
        });
        rows.push([String(i + 1), fmt(P[i], 3), state, fmt(after, 3)]);
      })(i);
      out.textContent = "exact test: the drafted code is accepted with probability " + pct(P[x], 1) + " (the target's probability of that single code)" +
        "\nrelaxed test, k = " + k + ", δ = " + fmt(delta, 2) + ": " + cnt + (cnt === 1 ? " neighbour" : " neighbours") + " counted, acceptance " + pct(Math.min(1, agg), 1) + (agg > P[x] + 1e-9 ? "  (×" + fmt(agg / P[x], 1) + ")" : "") +
        "\ntotal variation between the distorted target and the target: " + fmt(tv, 3) + "  (budget " + fmt(delta, 2) + ")" +
        (cnt < cand.length ? "\nthe next neighbour would exceed the budget" : (k > 0 ? "\nall " + k + " nearest codes fit in the budget: k is the limit here" : "\nk = 0: the exact test"));
      table(["code", "target probability", "status", "distorted target"], rows);
    }
    draw();
  };

  /* ---------------------------------------------------------------------------------------------
     p6time — from tokens per round to time per answer. Speed-up over the target alone:
     exact rule (l_e + 1) / (1 + γc); relaxed rule in tokens per second (l_r + 1) / (1 + γc);
     relaxed rule per answer: the same divided by the length inflation λ.
     --------------------------------------------------------------------------------------------- */
  WIDGETS.p6time = function (box) {
    var s = scaffold(box, "From tokens per round to time per answer");
    var se = slider(s.controls, "accepted drafts per round, exact rule", 0.5, 8, 0.1, 2, draw);
    var sr = slider(s.controls, "accepted drafts per round, relaxed rule", 0.5, 10, 0.1, 2.7, draw);
    var sl = slider(s.controls, "length of the relaxed answers ÷ exact answers", 0.8, 2, 0.01, 1.54, draw);
    var sg = slider(s.controls, "draft length γ", 1, 12, 1, 6, draw);
    var sc = slider(s.controls, "drafter cost <i>c</i>", 0, 0.3, 0.01, 0.05, draw);
    var out = readout(s.controls);
    var table = tableView(box);
    legend(s.legend, [["--muted", "exact rule", "bar"], ["--s4", "relaxed rule", "bar"], ["--muted", "the target alone (1×)", "dash"]]);

    function draw() {
      var le = se.get(), lr = sr.get(), lam = sl.get(), g = sg.get(), c = sc.get();
      se.out.textContent = fmt(le, 1); sr.out.textContent = fmt(lr, 1); sl.out.textContent = "×" + fmt(lam, 2); sg.out.textContent = String(g); sc.out.textContent = fmt(c, 2);
      var den = 1 + g * c, Se = (le + 1) / den, Sa = (lr + 1) / den, Sr = Sa / lam, star = (lr + 1) / (le + 1);
      var ymax = Math.ceil(Math.max(Se, Sa, Sr, 1.5) + 0.4);
      var plot = new Plot(s.svg, { w: 600, h: 280, x: [0.4, 3.6], y: [0, ymax], pad: { l: 44, r: 14, t: 28, b: 52 },
        label: "Speed-up over the target alone: exact rule, relaxed rule counted in tokens per second, relaxed rule counted per answer" });
      var yt = []; for (var i = 0; i <= ymax; i += (ymax > 6 ? 2 : 1)) yt.push(i);
      plot.axes({ xticks: [1, 2, 3], xnames: ["exact rule", "relaxed rule,", "relaxed rule,"], yticks: yt, noxgrid: true, ylabel: "speed-up over the target alone" });
      plot.text(2, 0, "tokens per second", "tx", "middle", 0, 31);
      plot.text(3, 0, "time per answer", "tx", "middle", 0, 31);
      plot.seg(0.4, 1, 3.6, 1, "ln cm thin dash");
      var bars = [[1, Se, "fm", "exact rule", "--muted"], [2, Sa, "a4 ln c4 thin", "relaxed rule, tokens per second", "--s4"], [3, Sr, "f4", "relaxed rule, time per answer", "--s4"]];
      bars.forEach(function (b) {
        var m = plot.bar(b[0], 0, 24, b[1], b[2]);
        plot.text(b[0], b[1], "×" + fmt(b[1], 2), "tx-b", "middle", 0, -7);
        hoverable(m, function () { return { title: b[3], rows: [[b[4], "speed-up over the target alone", "×" + fmt(b[1], 2)]] }; }, [m]);
      });
      function rel(a, b) { var d = (a / b - 1) * 100; return (d >= 0 ? "+" : "−") + fmt(Math.abs(d), 0) + "%"; }
      out.textContent = "exact rule: ×" + fmt(Se, 2) +
        "\nrelaxed rule, counted in tokens per second: ×" + fmt(Sa, 2) + "  (" + rel(Sa, Se) + " against the exact rule)" +
        "\nrelaxed rule, counted per answer: ×" + fmt(Sr, 2) + "  (" + rel(Sr, Se) + " against the exact rule)" +
        "\nthe relaxed rule finishes an answer sooner only if its answers are less than " + fmt(star, 2) + " times as long";
      table(["", "tokens per round", "speed-up over the target alone"], [["exact rule", fmt(le + 1, 1), "×" + fmt(Se, 2)],
        ["relaxed rule, tokens per second", fmt(lr + 1, 1), "×" + fmt(Sa, 2)], ["relaxed rule, time per answer", fmt(lr + 1, 1), "×" + fmt(Sr, 2)]]);
    }
    draw();
  };
