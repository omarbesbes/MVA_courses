  // widgets/05_reasoning.js — interactive figure of page 5 (inserted in the scope of app.js).

  /* ---------------------------------------------------------------------------------------------
     p5rsd — a toy reasoning trace: steps kept from the small model above a reward threshold,
     and the compute relative to the large model alone (the accounting of the RSD paper).
     --------------------------------------------------------------------------------------------- */
  WIDGETS.p5rsd = function (box) {
    var s = scaffold(box, "A reward threshold on the steps of a toy trace");
    var R = [0.93, 0.88, 0.97, 0.61, 0.91, 0.84, 0.35, 0.95, 0.90, 0.76, 0.98, 0.52, 0.89, 0.94]; // toy rewards
    var L = 40;                                                                                   // tokens per step (toy)
    var SIZES = { big: [7, 72, 7, "7B draft, 72B target, 7B reward model"], small: [1.5, 7, 7, "1.5B draft, 7B target, 7B reward model"] };
    var strip = document.createElement("div"); strip.className = "w-html";
    strip.style.cssText = "display:flex;flex-wrap:wrap;gap:0.35rem;margin:0.4rem 0 0.5rem;font-size:0.8rem";
    box.insertBefore(strip, s.svg);
    var sd = slider(s.controls, "threshold δ", 0, 1, 0.01, 0.7, draw);
    var sel = select(s.controls, "Models", [["big", SIZES.big[3]], ["small", SIZES.small[3]]], "big", draw);
    var out = readout(s.controls);
    var table = tableView(box);
    legend(s.legend, [["--s2", "step kept from the small model", "bar"], ["--s1", "step rewritten by the large model", "bar"],
      ["--s4", "compute relative to the large model alone"], ["--muted", "large model alone", "dash"]]);
    var plot = new Plot(s.svg, { w: 600, h: 230, x: [0, 1], y: [0, 1.4], pad: { l: 48, r: 16, t: 24, b: 40 },
      label: "Compute of the cascade relative to the large model alone, as a function of the reward threshold" });

    function rel(delta, z) {
      var rej = 0; R.forEach(function (r) { if (r < delta) rej++; });
      return { rej: rej, c: (R.length * L * z[0] + R.length * z[2] + rej * L * z[1]) / (R.length * L * z[1]) };
    }
    function draw() {
      var d = sd.get(), z = SIZES[sel.value], cur = rel(d, z), i;
      sd.out.textContent = fmt(d, 2);
      strip.textContent = "";
      R.forEach(function (r, k) {
        var c = document.createElement("div"); c.style.cssText = "display:flex;flex-direction:column;align-items:center";
        var t = document.createElement("span"); t.className = "tok " + (r >= d ? "q" : "p"); t.textContent = "step " + (k + 1);
        var e = document.createElement("span"); e.style.cssText = "font-size:0.72rem;color:var(--text-2)"; e.textContent = "r = " + fmt(r, 2);
        c.appendChild(t); c.appendChild(e); strip.appendChild(c);
      });
      plot.clear();
      plot.axes({ xticks: [0, 0.2, 0.4, 0.6, 0.8, 1], xd: 1, yticks: [0, 0.25, 0.5, 0.75, 1, 1.25], yd: 2, noxgrid: true,
        xlabel: "threshold δ on the reward", ylabel: "compute ÷ compute of the large model alone" });
      plot.seg(0, 1, 1, 1, "ln cm thin dash");
      var pts = [], xs = [], rows = [];
      for (i = 0; i <= 100; i++) { var x = i / 100, v = rel(x, z); xs.push(x); pts.push([x, v.c]); if (i % 10 === 0) rows.push([fmt(x, 1), String(R.length - v.rej), String(v.rej), fmt(v.c, 2), v.c > 0 ? "×" + fmt(1 / v.c, 1) : "—"]); }
      // step curve: horizontal segments
      var st = []; for (i = 0; i < pts.length; i++) { if (i > 0) st.push([pts[i][0], pts[i - 1][1]]); st.push(pts[i]); }
      plot.poly(st, "ln c4");
      plot.dot(d, cur.c, 5, "f4");
      plot.crosshair(xs, function (k) { var v = rel(xs[k], z); return { title: "threshold δ = " + fmt(xs[k], 2), rows: [["--s4", "relative compute", fmt(v.c, 2)],
        ["--s2", "steps kept from the small model", String(R.length - v.rej)], ["--s1", "steps rewritten by the large model", String(v.rej)]] }; });
      out.textContent = (R.length - cur.rej) + " of " + R.length + " steps kept from the small model, " + cur.rej + " rewritten by the large model" +
        "\ncompute relative to the large model alone: " + fmt(cur.c, 2) + (cur.c < 1 ? "   →   ×" + fmt(1 / cur.c, 1) + " fewer operations" : "   →   more operations than the large model alone") +
        "\n(toy trace; operations counted as model size × generated tokens, one token per reward call; accuracy is not modelled)";
      table(["threshold δ", "steps kept", "steps rewritten", "relative compute", "saving"], rows);
    }
    draw();
  };
