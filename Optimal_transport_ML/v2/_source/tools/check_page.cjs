// tools/check_page.cjs — checks a built page of Optimal_transport_ML/v2 in headless Chromium.
//
//   node tools/check_page.cjs Lesson05.html                 report (exit code 1 if a problem is found)
//   node tools/check_page.cjs Lesson05.html --shots DIR     also save screenshots of every figure and widget
//
// Checks: console and page errors; every widget drawn; KaTeX errors; internal anchors; display formulas wider
// than the column at desktop width (with every fold opened); no horizontal page scroll at phone width.
const path = require("path");
let pw;
try { pw = require("playwright"); } catch (e) { pw = require("/opt/node22/lib/node_modules/playwright"); }
const page = process.argv[2];
const shotsIdx = process.argv.indexOf("--shots");
const shots = shotsIdx > 0 ? process.argv[shotsIdx + 1] : null;
if (!page) { console.error("usage: node tools/check_page.cjs Page.html [--shots DIR]"); process.exit(2); }
const url = "file://" + path.resolve(__dirname, "..", "..", page);
(async () => {
  const browser = await pw.chromium.launch();
  let problems = 0;
  for (const [w, scheme] of [[1280, "light"], [1280, "dark"], [390, "light"]]) {
    const p = await browser.newPage({ viewport: { width: w, height: 900 }, colorScheme: scheme });
    const errs = [];
    p.on("pageerror", (e) => errs.push("pageerror: " + e.message));
    p.on("console", (m) => { if (m.type() === "error") errs.push("console: " + m.text()); });
    await p.goto(url); await p.waitForTimeout(700);
    await p.click("[data-action=expand]"); await p.waitForTimeout(300);
    const r = await p.evaluate(() => {
      const d = [...document.querySelectorAll(".math-display")];
      const over = d.filter((x) => x.scrollWidth > x.clientWidth + 2).map((x) => x.textContent.slice(0, 60));
      const widgets = [...document.querySelectorAll(".widget")];
      return {
        displays: d.length, overflowing: over.length, overflowSamples: over.slice(0, 5),
        widgets: widgets.length,
        widgetsBroken: widgets.filter((x) => !x.querySelector("svg *") || x.textContent.includes("Figure unavailable")).map((x) => x.getAttribute("data-widget")),
        figures: document.querySelectorAll("figure.fig").length,
        mathErrors: document.querySelectorAll(".math-error").length,
        brokenAnchors: [...document.querySelectorAll('a[href^="#"]')].map((a) => a.getAttribute("href")).filter((h) => !document.getElementById(decodeURIComponent(h.slice(1)))),
        docW: document.documentElement.scrollWidth, winW: window.innerWidth,
        boxes: document.querySelectorAll(".box").length, exos: document.querySelectorAll(".exo").length, quizzes: document.querySelectorAll(".quiz").length,
      };
    });
    const bad = errs.length + r.widgetsBroken.length + r.mathErrors + r.brokenAnchors.length + (r.docW > r.winW ? 1 : 0) + (w > 1000 ? r.overflowing : 0);
    problems += bad;
    console.log(`${w}px ${scheme}: ${bad ? "PROBLEMS" : "ok"}  displays=${r.displays} overflowing=${r.overflowing}${w > 1000 && r.overflowing ? " " + JSON.stringify(r.overflowSamples) : ""} widgets=${r.widgets} broken=${JSON.stringify(r.widgetsBroken)} figures=${r.figures} mathErrors=${r.mathErrors} brokenAnchors=${JSON.stringify(r.brokenAnchors)} pageWidth=${r.docW}/${r.winW} boxes=${r.boxes} exercises=${r.exos} quizzes=${r.quizzes}`);
    for (const e of errs) console.log("   " + e);
    if (shots && w > 1000) {
      require("fs").mkdirSync(shots, { recursive: true });
      const base = page.replace(/\.html$/, "");
      await p.click("[data-action=collapse]");
      if (scheme === "light") {
        const figs = await p.$$("figure.fig");
        for (const [i, f] of figs.entries()) { await f.scrollIntoViewIfNeeded(); await f.screenshot({ path: `${shots}/${base}_fig${String(i).padStart(2, "0")}.png` }); }
      }
      const ws = await p.$$(".widget");
      for (const [i, x] of ws.entries()) {
        const name = await x.getAttribute("data-widget");
        await x.scrollIntoViewIfNeeded(); await x.screenshot({ path: `${shots}/${base}_${scheme}_w${String(i).padStart(2, "0")}_${name}.png` });
      }
    }
    await p.close();
  }
  await browser.close();
  console.log(problems ? `${problems} problem(s)` : "all checks passed");
  process.exit(problems ? 1 : 0);
})();
