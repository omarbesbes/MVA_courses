  // widgets/index.js — interactive figure of the home page (inserted in the scope of app.js).

  /* ---------------------------------------------------------------------------------------------
     home — one position, three tokens (example A of page 1), one knob: the lenience λ of page 3.
     Accept the drafted token x with probability min(1, p(x) / (λ q(x))); after a rejection draw from
     the residual of the exact rule. Shows the output distribution, the acceptance and the bias.
     --------------------------------------------------------------------------------------------- */
  WIDGETS.home = function (box) {
    var s = scaffold(box, "One knob from exact to lossy");
    var NAMES = ["Paris", "the", "a"], P = [0.6, 0.3, 0.1], Q = [0.3, 0.5, 0.2], G = 5;
    var sl = slider(s.controls, "lenience λ  (1 = the exact rule)", 0.4, 1, 0.01, 1, draw);
    var out = readout(s.controls);
    var table = tableView(box);
    legend(s.legend, [["--s1", "target model p", "bar"], ["--s2", "drafter q", "bar"], ["--s4", "what comes out", "bar"]]);

    function rule(lam) {
      var tv = tvDist(P, Q), A = 0, o = [], i;
      for (i = 0; i < 3; i++) A += Math.min(Q[i], P[i] / lam);
      for (i = 0; i < 3; i++) o.push(Math.min(Q[i], P[i] / lam) + (1 - A) * Math.max(P[i] - Q[i], 0) / tv);
      return { A: A, out: o, bias: tvDist(o, P), tv: tv };
    }
    function draw() {
      var lam = sl.get(), r = rule(lam), i;
      sl.out.textContent = fmt(lam, 2);
      var plot = new Plot(s.svg, { w: 600, h: 260, x: [0.4, 3.6], y: [0, 0.7], pad: { l: 44, r: 14, t: 26, b: 36 },
        label: "Probability of three tokens under the target model, the drafter, and the output of the rule" });
      plot.axes({ xticks: [1, 2, 3], xnames: NAMES, yticks: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], yd: 1, noxgrid: true, ylabel: "probability of the next token" });
      var rows = [];
      for (i = 0; i < 3; i++) (function (i) {
        var b1 = plot.bar(i + 1, -28, 22, P[i], "f1"), b2 = plot.bar(i + 1, 0, 22, Q[i], "f2"), b3 = plot.bar(i + 1, 28, 22, r.out[i], "f4");
        var info = function () { return { title: "token “" + NAMES[i] + "”", rows: [["--s1", "target model", fmt(P[i], 3)], ["--s2", "drafter", fmt(Q[i], 3)], ["--s4", "output", fmt(r.out[i], 3)]] }; };
        hoverable(b1, info, [b1, b2, b3]); hoverable(b2, info, [b1, b2, b3], true); hoverable(b3, info, [b1, b2, b3], true);
        rows.push([NAMES[i], fmt(P[i], 2), fmt(Q[i], 2), fmt(r.out[i], 3)]);
      })(i);
      var tok = r.A > 1 - 1e-9 ? G + 1 : (1 - Math.pow(r.A, G + 1)) / (1 - r.A);
      out.textContent = "draft accepted with probability " + pct(r.A, 0) + "   →   " + fmt(tok, 2) + " tokens per call of the target with drafts of " + G +
        "\ndistance between the output and the target (total variation): " + fmt(r.bias, 2) +
        "\nrejection + distance = " + fmt(1 - r.A, 2) + " + " + fmt(r.bias, 2) + " = " + fmt(1 - r.A + r.bias, 2) + "   (the distance between the two models is " + fmt(r.tv, 2) + ")" +
        (lam > 0.995 ? "\nλ = 1: the exact rule; the output is the target's distribution" : r.A > 1 - 1e-9 ? "\nevery draft is accepted: the output is the drafter's distribution" : "");
      table(["token", "target model", "drafter", "output"], rows);
    }
    draw();
  };
