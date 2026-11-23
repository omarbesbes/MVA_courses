  // widgets/04_judges.js — interactive figures of page 4 (inserted in the scope of app.js).

  /* ---------------------------------------------------------------------------------------------
     p4fly — the FLy rule (entropy gate + deferred window) on a toy draft. Toy tokens, toy entropies.
     --------------------------------------------------------------------------------------------- */
  WIDGETS.p4fly = function (box) {
    var s = scaffold(box, "FLy on a toy draft: entropy gate, then deferred window");
    s.svg.remove();
    // [drafted token, target's own choice if different, normalised entropy of the target at a mismatch]
    var D = [["So", "Thus", 0.46], [" she"], [" has"], [" 3"], [" ×"], [" 4"], [" ="], [" 12"], [" apples"],
      [" and", ",", 0.38], [" gives"], [" away", " 5", 0.33], [" 5"], [","], [" leaving"], [" 8", " 7", 0.04], [" for"], [" her"]];
    var grid = document.createElement("div"); grid.className = "w-html";
    grid.style.cssText = "display:flex;flex-wrap:wrap;gap:0.35rem 0.3rem;margin:0.4rem 0 0.6rem;font-size:0.84rem";
    box.insertBefore(grid, s.legend);
    var st = slider(s.controls, "entropy gate θ", 0, 1, 0.01, 0.3, draw);
    var sw = slider(s.controls, "window W", 0, 8, 1, 6, draw);
    var out = readout(s.controls);
    legend(s.legend, [["--s3", "matches the target's choice: accepted", "bar"], ["--s4", "mismatch accepted by FLy", "bar"],
      ["--s6", "rejected", "bar"], ["--muted", "discarded", "bar"]]);

    function run(theta, W) { // returns { n: number of accepted drafted tokens, why, lax: accepted mismatches }
      var lax = [], i, k;
      for (i = 0; i < D.length; i++) {
        if (!D[i][1]) continue;                          // the draft equals the target's choice
        if (D[i][2] < theta) return { n: i, why: "position " + (i + 1) + ": the target is confident there (entropy " + fmt(D[i][2], 2) + " < θ) → strict → rejected", lax: lax };
        if (i + W > D.length - 1 && W > 0) return { n: i, why: "position " + (i + 1) + ": deferred, but the window runs past the end of the draft → rejected (convention of this toy)", lax: lax };
        for (k = i + 1; k <= i + W; k++) if (D[k][1]) return { n: i, why: "position " + (i + 1) + ": deferred, but the target departs from the draft again at position " + (k + 1) + ", inside the window → rejected", lax: lax };
        lax.push(i);
      }
      return { n: D.length, why: "the whole draft is accepted", lax: lax };
    }
    function cell(tok, cls, sub1, sub2) {
      var c = document.createElement("div"); c.style.cssText = "display:flex;flex-direction:column;align-items:center;min-width:2.1rem";
      var t = document.createElement("span"); t.className = "tok " + cls; t.textContent = tok; t.style.fontFamily = "var(--font-mono)"; c.appendChild(t);
      [sub1, sub2].forEach(function (x) { var e = document.createElement("span"); e.style.cssText = "font-size:0.72rem;color:var(--text-2);line-height:1.25;white-space:pre"; e.textContent = x || " "; c.appendChild(e); });
      return c;
    }
    function draw() {
      var theta = st.get(), W = sw.get(), r = run(theta, W), exact = 0, i;
      st.out.textContent = fmt(theta, 2); sw.out.textContent = String(W);
      while (exact < D.length && !D[exact][1]) exact++;
      grid.textContent = "";
      for (i = 0; i < D.length; i++) {
        var mm = !!D[i][1], cls = i < r.n ? (mm ? "lax" : "ok") : i === r.n ? "no" : "dim";
        grid.appendChild(cell(D[i][0], cls, mm ? "target:" + D[i][1] : "", mm ? "entropy " + fmt(D[i][2], 2) : ""));
      }
      out.textContent = "exact rule: " + exact + " drafted token" + (exact === 1 ? "" : "s") + " accepted        FLy (θ = " + fmt(theta, 2) + ", W = " + W + "): " + r.n + " accepted" +
        (r.lax.length ? ", including " + r.lax.length + " mismatch" + (r.lax.length > 1 ? "es" : "") : "") + "\n" + r.why +
        (r.lax.indexOf(15) >= 0 ? "\n⚠ the wrong number (“ 8” for “ 7”) was accepted" : "");
    }
    draw();
  };

  /* ---------------------------------------------------------------------------------------------
     p4judge — a toy judge: threshold against tokens per target call and against spoiled answers.
     --------------------------------------------------------------------------------------------- */
  WIDGETS.p4judge = function (box) {
    var s = scaffold(box, "A toy judge: what the threshold buys, and what it costs");
    var svg2 = addSvg(box, s.svg);
    var MU = 0.15, G = 25, N = 200;
    var st = slider(s.controls, "threshold of the judge", -3, 3, 0.05, 0.6, draw);
    var sd = slider(s.controls, "separation of the judge", 0.5, 4, 0.1, 3, draw);
    var sh = slider(s.controls, "share of harmful mismatches", 0.05, 0.7, 0.01, 0.15, draw);
    var out = readout(s.controls);
    var table = tableView(box);
    legend(s.legend, [["--s4", "tokens per target call, with the judge"], ["--muted", "exact rule", "dash"], ["--s6", "answers with a harmful token accepted"]]);
    var top = new Plot(s.svg, { w: 600, h: 230, x: [-3, 3], y: [0, 26], pad: { l: 48, r: 16, t: 24, b: 30 },
      label: "Tokens per target call as a function of the judge's threshold" });
    var bot = new Plot(svg2, { w: 600, h: 230, x: [-3, 3], y: [0, 1], pad: { l: 48, r: 16, t: 24, b: 40 },
      label: "Share of answers in which a harmful token was accepted, as a function of the judge's threshold" });

    function erf(x) { var t = 1 / (1 + 0.3275911 * Math.abs(x)), y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x); return x >= 0 ? y : -y; }
    function Phi(x) { return 0.5 * (1 + erf(x / Math.SQRT2)); }
    function at(t, d, h) {
      var a = 1 - Phi(t - d / 2), f = 1 - Phi(t + d / 2), al = 1 - MU * (1 - a * (1 - h) - f * h);
      return { a: a, f: f, tok: al > 1 - 1e-9 ? G + 1 : (1 - Math.pow(al, G + 1)) / (1 - al), bad: 1 - Math.pow(1 - MU * h * f, N) };
    }
    function draw() {
      var t = st.get(), d = sd.get(), h = sh.get(), cur = at(t, d, h), exact = (1 - Math.pow(1 - MU, G + 1)) / MU, k;
      st.out.textContent = fmt(t, 2); sd.out.textContent = fmt(d, 1); sh.out.textContent = fmt(h, 2);
      var xs = [], T = [], B = [], rows = [];
      for (k = 0; k <= 120; k++) { var x = -3 + k * 0.05, r = at(x, d, h); xs.push(x); T.push([x, r.tok]); B.push([x, r.bad]);
        if (k % 10 === 0) rows.push([fmt(x, 1), pct(r.a, 0), pct(r.f, 1), fmt(r.tok, 1), pct(r.bad, 1)]); }
      top.clear();
      top.axes({ xticks: [-3, -2, -1, 0, 1, 2, 3], yticks: [0, 5, 10, 15, 20, 25], ylabel: "tokens per target call", noxgrid: true });
      top.seg(-3, exact, 3, exact, "ln cm thin dash");
      top.text(-3, exact, "exact rule: " + fmt(exact, 1), "tx-s", "start", 6, -6);
      top.poly(T, "ln c4"); top.seg(t, 0, t, 26, "cross"); top.dot(t, cur.tok, 5, "f4");
      bot.clear();
      bot.axes({ xticks: [-3, -2, -1, 0, 1, 2, 3], yticks: [0, 0.25, 0.5, 0.75, 1], yfmt: function (v) { return pct(v, 0); }, noxgrid: true,
        ylabel: "answers of " + N + " tokens with a harmful token accepted", xlabel: "← lenient      threshold of the judge      strict →" });
      bot.poly(B, "ln c6"); bot.seg(t, 0, t, 1, "cross"); bot.dot(t, cur.bad, 5, "f6");
      var info = function (i) {
        var r = at(xs[i], d, h);
        return { title: "threshold " + fmt(xs[i], 2), rows: [["--s4", "tokens per target call", fmt(r.tok, 1)], ["--s6", "answers with a harmful token accepted", pct(r.bad, 1)],
          [null, "harmless mismatches accepted", pct(r.a, 0)], [null, "harmful mismatches accepted", pct(r.f, 1)]] };
      };
      top.crosshair(xs, info); bot.crosshair(xs, info);
      out.textContent = "at this threshold the judge accepts " + pct(cur.a, 0) + " of the harmless mismatches and " + pct(cur.f, 1) + " of the harmful ones" +
        "\ntokens per target call: " + fmt(cur.tok, 1) + "  (exact rule: " + fmt(exact, 1) + ")        answers with a harmful token accepted: " + pct(cur.bad, 1) +
        "\n(toy model: a drafted token is a mismatch with probability " + MU + ", drafts of " + G + " tokens, answers of " + N + " tokens)";
      table(["threshold", "harmless accepted", "harmful accepted", "tokens per target call", "answers spoiled"], rows);
    }
    draw();
  };
