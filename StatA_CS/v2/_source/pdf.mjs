// pdf.mjs — exporte la page « Révision pour l'examen » en PDF A4 (après `node build.mjs`).
//   node pdf.mjs   →  ../Revision_examen_StatA.pdf   (toute la page, preuves et réponses dépliées)
//                     ../Revision_essentiel_StatA.pdf (les synthèses seulement, pour la dernière relecture)
// Demande Playwright (`npm install playwright` ou une installation globale) et un Chromium ;
// CHROME_PATH=/chemin/vers/chrome pour utiliser un navigateur précis.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
let chromium;
for (const mod of ["playwright", "playwright-core"]) {
  try { ({ chromium } = require(mod)); break; } catch {}
}
if (!chromium) { console.error("Playwright introuvable : npm install playwright"); process.exit(1); }

const here = path.dirname(fileURLToPath(import.meta.url));
const page = path.join(here, "..", "11_revision.html");
const exe = process.env.CHROME_PATH || (fs.existsSync("/opt/pw-browsers/chromium-1194/chrome-linux/chrome") ? "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" : undefined);

// Sections gardées dans la version « essentiel ».
const ESSENTIEL = ["carte", "conventions", "theoremes", "preuves", "pieges", "jour-j"];
const SCALE = 0.9;                                         // texte un peu plus petit qu'à l'écran
const PRINTABLE_W = Math.floor(((210 - 24) / 25.4) * 96 / SCALE); // largeur utile A4 (marges 12 mm), en px CSS

async function exportPdf(browser, out, essentiel) {
  const p = await browser.newPage({ viewport: { width: PRINTABLE_W, height: 1400 }, colorScheme: "light" });
  await p.goto("file://" + page);
  await p.evaluate(({ essentiel, keep }) => {
    document.documentElement.setAttribute("data-theme", "light");
    document.querySelectorAll("main details").forEach((d) => { d.open = true; });
    if (!essentiel) return;
    const kept = new Set(keep);
    let cur = null;
    for (const el of [...document.querySelector("main").children]) {
      if (el.tagName === "H2") cur = el.id;
      if (!kept.has(cur)) el.style.display = "none";
    }
    document.querySelector(".top h1").textContent = "Révision pour l'examen — l'essentiel";
    const sub = document.querySelector(".top .subtitle");
    if (sub) sub.textContent = "Les synthèses à relire en dernier : le cours en une page, les conventions, les théorèmes et leurs hypothèses, les preuves à savoir refaire, les pièges, le jour J.";
  }, { essentiel, keep: ESSENTIEL });
  await p.addStyleTag({ content: `@media print {
    body { font-size: 10.5pt; line-height: 1.5; }
    main { max-width: none; }
    .box { break-inside: auto; }
    h2, h3, h4, .box-h, .exo-h { break-after: avoid; }
    .memo, ol.steps > li, tr, .quiz, .math-display, .chain > li, details.fold > summary { break-inside: avoid; }
    h2 { margin-top: 1.6rem; }
    a { color: inherit; text-decoration: none; }
    .anchor { display: none; }
  }` });
  await p.emulateMedia({ media: "print" });
  await p.waitForTimeout(200);
  // Sur papier rien ne défile : on réduit (zoom CSS) toute formule ou tout tableau plus large que la colonne.
  const shrunk = await p.evaluate(() => {
    let n = 0;
    document.querySelectorAll("main .math-display, main .table-wrap").forEach((el) => {
      if (!el.offsetParent) return;
      const sw = el.scrollWidth, cw = el.clientWidth;
      if (sw > cw + 1) { el.style.zoom = (cw / sw - 0.005).toFixed(3); n++; }
    });
    return n;
  });
  await p.pdf({
    path: out, format: "A4", printBackground: true, scale: SCALE,
    margin: { top: "13mm", bottom: "15mm", left: "12mm", right: "12mm" },
    displayHeaderFooter: true, headerTemplate: "<span></span>",
    footerTemplate: '<div style="font-size:8px;color:#888;width:100%;text-align:center;font-family:sans-serif">Statistiques avancées 3A — Révision pour l\'examen — <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
  });
  await p.close();
  console.log(`écrit ${path.basename(out)}  (${(fs.statSync(out).size / 1024 / 1024).toFixed(1)} Mo, ${shrunk} bloc(s) réduit(s))`);
}

const browser = await chromium.launch(exe ? { executablePath: exe } : {});
await exportPdf(browser, path.join(here, "..", "Revision_examen_StatA.pdf"), false);
await exportPdf(browser, path.join(here, "..", "Revision_essentiel_StatA.pdf"), true);
await browser.close();
