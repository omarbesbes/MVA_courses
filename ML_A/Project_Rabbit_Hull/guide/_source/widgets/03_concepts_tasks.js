// widgets/03_concepts_tasks.js — interactive figures of page 3 (concepts and tasks). Own helpers are prefixed "p3".

  /* --- 1. importance: contributions E[Z_i] W'_ij add up to the mean output --- */
  WIDGETS.p3importance = function (box) {
    var s = scaffold(box, "Importance of three concepts for two outputs: bars E[Zᵢ]·W′ᵢⱼ, marker = their sum (the mean output)");
    var P = new Plot(s.svg, { x: [0, 8], y: [-4, 4], w: 680, h: 330, pad: { l: 46, r: 16, t: 20, b: 40 }, label: "Bars of the contributions of three concepts to two outputs" });
    var ez = [0.5, 0.2, 0.05], W = [[2, -1], [0.5, 1], [-3, 4]];
    var sl = [];
    for (var i = 0; i < 3; i++) (function (i) {
      sl.push(slider(s.controls, "E[Z<sub>" + (i + 1) + "</sub>]", 0, 1, 0.05, ez[i], draw));
    })(i);
    var wl = [];
    for (var i = 0; i < 3; i++) for (var j = 0; j < 2; j++) (function (i, j) {
      wl.push(slider(s.controls, "W′<sub>" + (i + 1) + (j + 1) + "</sub>", -4, 4, 0.5, W[i][j], draw));
    })(i, j);
    button(s.controls, "Reset", function () {
      sl.forEach(function (x, i) { x.set(ez[i]); });
      wl.forEach(function (x, k) { x.set(W[Math.floor(k / 2)][k % 2]); });
      draw();
    });
    var ro = readout(s.controls);
    legend(s.legend, [["--s1", "concept 1"], ["--s2", "concept 2"], ["--s3", "concept 3"], ["--text", "sum = mean output"]]);
    function draw() {
      P.clear();
      for (var v = -4; v <= 4; v += 2) { P.seg(0, v, 8, v, v === 0 ? "ax" : "gr"); P.text(0, v, String(v), "tx-s", "end", -6, 4); }
      var sums = [0, 0], cls = ["f1", "f2", "f3"], txt = [];
      for (var j = 0; j < 2; j++) {
        var x0 = 1 + j * 4, pos = 0, neg = 0;
        for (var i = 0; i < 3; i++) {
          var c = sl[i].get() * wl[i * 2 + j].get();
          sums[j] += c;
          var y0 = c >= 0 ? pos : neg, y1 = y0 + c;
          if (c >= 0) pos = y1; else neg = y1;
          var xa = P.tx(x0 + i * 0.7 - 0.2), xb = P.tx(x0 + i * 0.7 + 0.4);
          var ya = P.ty(Math.max(y0, y1)), yb = P.ty(Math.min(y0, y1));
          el("rect", { x: xa, y: ya, width: xb - xa, height: Math.max(yb - ya, 0.5), "class": cls[i] }, P.g);
          txt.push(c);
        }
        P.dot(x0 + 0.7, sums[j], 6, "fk");
        P.text(x0 + 0.7, -3.7, "output " + (j + 1), "tx-b", "middle");
      }
      for (var j2 = 0; j2 < 2; j2++) {
        var parts = [0, 1, 2].map(function (i) { return fmt(sl[i].get() * wl[i * 2 + j2].get(), 2); });
        ro.textContent += "";
      }
      sl.forEach(function (x) { x.out.textContent = fmt(x.get(), 2); });
      wl.forEach(function (x) { x.out.textContent = fmt(x.get(), 1); });
      var lines = [0, 1].map(function (j) {
        return "output " + (j + 1) + ": " + [0, 1, 2].map(function (i) { return fmt(sl[i].get() * wl[i * 2 + j].get(), 2); }).join(" + ").replace(/\+ -/g, "− ") + " = " + fmt(sums[j], 2);
      });
      ro.textContent = lines.join("\n");
    }
    draw(); redrawers.push(draw);
  };

  /* --- 2. entropy of a footprint on 16x16 patches + 5 special tokens --- */
  WIDGETS.p3entropy = function (box) {
    var s = scaffold(box, "Entropy of a footprint: choose which of the 261 tokens fire (uniformly)");
    var W = 16, sel = new Array(261).fill(false); // 0 cls, 1-4 registers, 5.. patches (row-major)
    var P = new Plot(s.svg, { x: [0, 680], y: [380, 0], w: 680, h: 380, pad: { l: 0, r: 0, t: 0, b: 0 }, label: "Grid of tokens, selected tokens are filled" });
    var presets = {
      one: function (i) { return i === 0 || false; },
      reg: function (i) { return i >= 1 && i <= 4; },
      cls5: function (i) { return i < 5; },
      left: function (i) { return i >= 5 && ((i - 5) % 16) < 5; },
      border: function (i) { if (i < 5) return false; var r = Math.floor((i - 5) / 16), c = (i - 5) % 16; return r === 0 || c === 0 || r === 15 || c === 15; },
      patches: function (i) { return i >= 5; },
      all: function () { return true; },
      none: function () { return false; }
    };
    var sel2 = select(s.controls, "preset", [["one", "one token (cls)"], ["reg", "four registers"], ["cls5", "five special tokens"], ["left", "left third of the grid (5 columns)"], ["border", "border of the grid"], ["patches", "the 256 patches"], ["all", "all 261 tokens"], ["none", "empty (click tokens)"]], "left", function () { apply(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "token with activation (uniform)"], ["--muted", "token silent"], ["--s2", "special token outline"]]);
    function apply() { var f = presets[sel2.value]; for (var i = 0; i < 261; i++) sel[i] = f(i); draw(); }
    var CS = 20, GX = 180, GY = 8, SY = 8 + 16 * 20 + 22;
    function rc(i) { // top-left pixel of token i
      if (i < 5) return [GX + i * (CS + 6), SY];
      return [GX + ((i - 5) % 16) * CS, GY + Math.floor((i - 5) / 16) * CS];
    }
    s.svg.addEventListener("click", function (e) {
      var q = svgPoint(s.svg, e);
      for (var i = 0; i < 261; i++) { var p = rc(i); if (q.x >= p[0] && q.x < p[0] + CS && q.y >= p[1] && q.y < p[1] + CS) { sel[i] = !sel[i]; sel2.value = "none"; draw(); return; } }
    });
    function draw() {
      P.clear();
      var m = 0, i;
      for (i = 0; i < 261; i++) {
        var p = rc(i);
        el("rect", { x: p[0] + 1, y: p[1] + 1, width: CS - 2, height: CS - 2, "class": (sel[i] ? "f3" : "am") + (i < 5 ? " ln c2" : ""), style: i < 5 ? "stroke-width:1.5px" : "" }, P.g);
        if (sel[i]) m++;
      }
      P.text(0, 0, "", "tx-s");
      var t1 = el("text", { x: GX - 8, y: SY + 14, "class": "tx-s", "text-anchor": "end" }, P.g); t1.textContent = "cls, reg 1–4";
      var t2 = el("text", { x: GX - 8, y: GY + 14, "class": "tx-s", "text-anchor": "end" }, P.g); t2.textContent = "16 × 16 patches";
      var H = m > 0 ? Math.log(m) : NaN;
      ro.textContent = "tokens on: m = " + m + "     entropy H = ln m = " + fmt(H, 3) + " nats     (maximum ln 261 = 5.565, ln 256 = 5.545)     effective tokens e^H = " + (m > 0 ? m : "—");
    }
    apply(); redrawers.push(draw);
  };

  /* --- 3. Elsewhere: toy grid, toggle the object --- */
  WIDGETS.p3elsewhere = function (box) {
    var s = scaffold(box, "Toy image of 8 × 8 tokens: where three concepts fire, and what they depend on");
    var N = 8, P = new Plot(s.svg, { x: [0, 31], y: [0, 10.5], w: 680, h: 240, pad: { l: 8, r: 8, t: 22, b: 4 }, label: "Three token maps of the same toy image for an object concept, a background concept and an Elsewhere concept" });
    var on = true, obj = function (r, c) { return r >= 3 && r <= 5 && c >= 1 && c <= 2; };
    var cb = checkbox(s.controls, "object present", true, function () { on = cb.checked; draw(); });
    var ro = readout(s.controls);
    legend(s.legend, [["--s3", "object tokens"], ["--s2", "concept fires"], ["--s4", "fires (background concept)"]]);
    var panels = [
      ["object concept", function (r, c) { return on && obj(r, c); }, "f2"],
      ["background concept (wall)", function (r, c) { return c >= 5; }, "f4"],
      ["Elsewhere concept", function (r, c) { return on && !obj(r, c) && c >= 3; }, "f2"]
    ];
    function draw() {
      P.clear();
      panels.forEach(function (pn, k) {
        var ox = k * 10.5 + 0.3;
        P.text(ox + 4, 10.3, pn[0], "tx-b", "middle");
        for (var r = 0; r < N; r++) for (var c = 0; c < N; c++) {
          var x = P.tx(ox + c), y = P.ty(9.4 - r), w = P.tx(1) - P.tx(0);
          var isObj = on && obj(r, c), fire = pn[1](r, c);
          el("rect", { x: x, y: y, width: w * 0.94, height: w * 0.94, "class": fire ? pn[2] : (isObj ? "f3" : "am"), "fill-opacity": fire && isObj ? 0.6 : (isObj ? 0.45 : 1) }, P.g);
        }
      });
      var cnt = panels.map(function (pn) { var n = 0; for (var r = 0; r < N; r++) for (var c = 0; c < N; c++) if (pn[1](r, c)) n++; return n; });
      ro.textContent = "tokens firing — object concept: " + cnt[0] + ", background concept: " + cnt[1] + ", Elsewhere concept: " + cnt[2] +
        (on ? "\nElsewhere fires only away from the object, yet disappears when the object is removed" : "\nobject removed: the object concept and the Elsewhere concept vanish, the background concept stays");
    }
    draw(); redrawers.push(draw);
  };
