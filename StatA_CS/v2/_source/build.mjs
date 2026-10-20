// build.mjs — assemble les pages de StatA_CS/v2.
//
// Chaque fichier de pages/ est un fragment HTML qui commence par un commentaire
// d'en-tête (title, short, description). Les formules s'écrivent $...$ (en ligne)
// et $$...$$ (centrées) ; elles sont rendues ici avec KaTeX, si bien que les pages
// produites sont autonomes : CSS, polices et scripts sont inclus, aucune connexion
// n'est nécessaire pour les lire.
//
// Usage : npm install && node build.mjs        (écrit ../*.html)

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import katex from "katex";

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.resolve(here, "..");
const katexDir = path.join(here, "node_modules", "katex", "dist");

// Ordre de lecture : sert à la barre de navigation et aux liens précédent/suivant.
const PAGES = [
  { file: "index.html", nav: "Accueil" },
  { file: "00_rappels.html", nav: "Rappels" },
  { file: "01_seance1.html", nav: "S1" },
  { file: "02_seance2.html", nav: "S2" },
  { file: "03_seance3.html", nav: "S3" },
  { file: "04_seance4.html", nav: "S4" },
  { file: "05_seance5.html", nav: "S5" },
  { file: "06_seance6.html", nav: "S6" },
  { file: "08_td1.html", nav: "TD1" },
  { file: "09_td2.html", nav: "TD2" },
  { file: "10_td3.html", nav: "TD3" },
  { file: "07_fiche.html", nav: "Fiche réflexes" },
];

const MACROS = {
  "\\R": "\\mathbb{R}",
  "\\N": "\\mathcal{N}",
  "\\E": "\\mathbb{E}",
  "\\P": "\\mathbb{P}",
  "\\Var": "\\operatorname{Var}",
  "\\Cov": "\\operatorname{Cov}",
  "\\tr": "\\operatorname{tr}",
  "\\rg": "\\operatorname{rg}",
  "\\sgn": "\\operatorname{sgn}",
  "\\diag": "\\operatorname{diag}",
  "\\Ker": "\\operatorname{Ker}",
  "\\Ima": "\\operatorname{Im}",
  "\\supp": "\\operatorname{supp}",
  "\\argmin": "\\operatorname*{arg\\,min}",
  "\\argmax": "\\operatorname*{arg\\,max}",
  "\\T": "^{\\top}",
  "\\bstar": "\\beta^{*}",
  "\\hb": "\\hat\\beta",
  "\\Astar": "\\mathcal{A}^{*}",
  "\\hA": "\\hat{\\mathcal{A}}",
  "\\eps": "\\varepsilon",
  "\\ind": "\\mathbf{1}",
  "\\dd": "\\mathrm{d}",
  "\\norm": "\\left\\lVert #1 \\right\\rVert",
  "\\abs": "\\left\\lvert #1 \\right\\rvert",
  "\\ps": "\\langle #1,\\, #2 \\rangle",
  "\\MC": "^{\\mathrm{MC}}",
  "\\cF": "\\mathcal{F}",
  "\\cA": "\\mathcal{A}",
};

const errors = [];
const warnings = [];

function lineOf(text, index) {
  return text.slice(0, index).split("\n").length;
}

function renderMath(tex, display, file, src, index) {
  try {
    return katex.renderToString(tex, {
      displayMode: display,
      throwOnError: true,
      output: "html",
      macros: { ...MACROS },
      trust: false,
      strict: (code, msg) => {
        if (code === "unicodeTextInMathMode") return "ignore";
        warnings.push(`${file}:${lineOf(src, index)}  ${code}: ${msg}`);
        return "ignore";
      },
    });
  } catch (e) {
    errors.push(`${file}:${lineOf(src, index)}  ${e.message}\n      ${tex.slice(0, 160).replace(/\s+/g, " ")}`);
    return `<span class="math-error">${tex.replace(/</g, "&lt;")}</span>`;
  }
}

// Rend $$...$$ puis $...$, en laissant intacts <script>, <style> et les commentaires.
function processMath(src, file) {
  const protectedRe = /<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>|<!--[\s\S]*?-->/g;
  let out = "";
  let last = 0;
  for (const m of src.matchAll(protectedRe)) {
    out += processChunk(src.slice(last, m.index), file, src, last);
    out += m[0];
    last = m.index + m[0].length;
  }
  out += processChunk(src.slice(last), file, src, last);
  return out;
}

function processChunk(chunk, file, src, offset) {
  // \$ = dollar littéral
  const DOLLAR = "\u0000DOLLAR\u0000";
  chunk = chunk.replace(/\\\$/g, DOLLAR);
  chunk = chunk.replace(/\$\$([\s\S]+?)\$\$/g, (m, tex, i) =>
    `<div class="math-display">${renderMath(tex.trim(), true, file, src, offset + i)}</div>`);
  chunk = chunk.replace(/\$((?:[^$\\]|\\[\s\S])+?)\$/g, (m, tex, i, whole) => {
    if (/\n\s*\n/.test(tex)) {
      errors.push(`${file}:${lineOf(src, offset + i)}  $ non fermé (formule en ligne sur un paragraphe vide)`);
      return m;
    }
    // Une ponctuation collée à la formule ne doit pas passer seule à la ligne : on insère un
    // « word joiner » (U+2060), qui interdit la coupure entre la formule et le signe qui suit.
    const next = whole[i + m.length] || "";
    return renderMath(tex, false, file, src, offset + i) + (/[.,;:!?)\]»%]/.test(next) ? "\u2060" : "");
  });
  return chunk.replace(new RegExp(DOLLAR, "g"), "$");
}

// Typographie française : espace fine insécable avant ; : ! ? » et insécable après «, pour qu'aucun
// signe ne commence une ligne. Seul le texte est touché : balises, <pre>, <code>, <script>, <style> exclus.
function frenchSpacing(html) {
  const parts = html.split(/(<pre[\s\S]*?<\/pre>|<code[\s\S]*?<\/code>|<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>|<[^>]+>)/);
  return parts
    .map((part, k) => (k % 2 === 1 ? part : part.replace(/ ([;:!?»])/g, "\u202F$1").replace(/« /g, "«\u00A0")))
    .join("");
}

function parseFront(src) {
  const m = src.match(/^\s*<!--([\s\S]*?)-->/);
  const meta = {};
  if (!m) return { meta, body: src };
  for (const line of m[1].split("\n")) {
    const kv = line.match(/^\s*([a-z]+)\s*:\s*(.*)$/);
    if (kv) meta[kv[1]] = kv[2].trim();
  }
  return { meta, body: src.slice(m[0].length) };
}

function slugify(s) {
  return s
    .normalize("NFD").replace(/[̀-ͯ]/g, "")
    .toLowerCase().replace(/<[^>]+>/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")
    .slice(0, 60) || "section";
}

// Titre d'onglet : on retire la syntaxe TeX des formules éventuelles.
function plainTitle(s) {
  return s.replace(/\$([^$]*)\$/g, (m, t) => t.replace(/\\[a-zA-Z]+/g, "").replace(/[{}^_\\]/g, ""));
}

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// Ajoute un id aux h2/h3 qui n'en ont pas et construit le sommaire de la page.
function buildToc(html, file) {
  const used = new Set();
  const items = [];
  html = html.replace(/<h([23])((?:\s[^>]*)?)>([\s\S]*?)<\/h\1>/g, (m, lvl, attrs, inner) => {
    let id = (attrs.match(/\sid="([^"]+)"/) || [])[1];
    const text = inner.replace(/<[^>]+>/g, "");
    if (!id) {
      id = slugify(text);
      let k = 2;
      while (used.has(id)) id = `${slugify(text)}-${k++}`;
      attrs = `${attrs} id="${id}"`;
    }
    if (used.has(id)) errors.push(`${file}: id en double « ${id} »`);
    used.add(id);
    // Le sommaire n'affiche pas les références (« Cours1 · diapo 7 », « → page »).
    const tocInner = inner.replace(/<(a|span) class="ref"[^>]*>[\s\S]*?<\/\1>/g, "").trim();
    if (!/\bdata-notoc\b/.test(attrs)) items.push({ lvl: Number(lvl), id, inner: tocInner });
    return `<h${lvl}${attrs}>${inner}<a class="anchor" href="#${id}" aria-label="Lien vers cette section">#</a></h${lvl}>`;
  });
  // Vérifie que les ancres internes pointent vers un id existant.
  const ids = new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]));
  for (const m of html.matchAll(/href="#([^"]+)"/g)) {
    if (!ids.has(m[1])) errors.push(`${file}: lien interne #${m[1]} sans cible`);
  }
  let toc = "";
  let open = false;
  for (const it of items) {
    if (it.lvl === 2) {
      if (open) toc += "</ol></li>";
      toc += `<li><a href="#${it.id}">${it.inner}</a><ol>`;
      open = true;
    } else {
      if (!open) { toc += "<li><ol>"; open = true; }
      toc += `<li><a href="#${it.id}">${it.inner}</a></li>`;
    }
  }
  if (open) toc += "</ol></li>";
  toc = toc.replace(/<ol><\/ol>/g, "");
  return { html, toc: `<ol>${toc}</ol>`, ids };
}

function katexCss() {
  let css = fs.readFileSync(path.join(katexDir, "katex.min.css"), "utf8");
  css = css.replace(/src:url\(fonts\/([^)]+)\.woff2\) format\("woff2"\)[^;}]*/g, (m, name) => {
    const b64 = fs.readFileSync(path.join(katexDir, "fonts", `${name}.woff2`)).toString("base64");
    return `src:url(data:font/woff2;base64,${b64}) format("woff2")`;
  });
  return css;
}

function main() {
  const template = fs.readFileSync(path.join(here, "template.html"), "utf8");
  const css = katexCss() + "\n" + fs.readFileSync(path.join(here, "style.css"), "utf8");
  const js = fs.readFileSync(path.join(here, "app.js"), "utf8");
  const only = process.argv.slice(2);

  const present = PAGES.filter((p) => fs.existsSync(path.join(here, "pages", p.file)));
  const allIds = {};
  const built = [];

  for (const [i, page] of present.entries()) {
    const src = fs.readFileSync(path.join(here, "pages", page.file), "utf8");
    const { meta, body } = parseFront(src);
    if (!meta.title) errors.push(`${page.file}: pas de « title » dans l'en-tête`);
    let html = frenchSpacing(processMath(body, page.file));
    const t = buildToc(html, page.file);
    allIds[page.file] = t.ids;
    built.push({ page, meta, html: t.html, toc: t.toc, i });
  }

  // Liens entre pages : fichier et ancre doivent exister.
  for (const b of built) {
    for (const m of b.html.matchAll(/href="(\d\d_[a-z0-9_]+\.html|index\.html)(?:#([^"]+))?"/g)) {
      const ids = allIds[m[1]];
      if (!ids) { warnings.push(`${b.page.file}: lien vers ${m[1]} (page absente pour l'instant)`); continue; }
      if (m[2] && !ids.has(m[2])) errors.push(`${b.page.file}: lien ${m[1]}#${m[2]} sans cible`);
    }
  }

  for (const b of built) {
    if (only.length && !only.includes(b.page.file)) continue;
    const prev = present[b.i - 1];
    const next = present[b.i + 1];
    const nav = present
      .map((p) => `<a href="${p.file}"${p.file === b.page.file ? ' aria-current="page"' : ""}>${p.nav}</a>`)
      .join("");
    const pager =
      (prev ? `<a class="prev" href="${prev.file}"><span>← Précédent</span>${escapeHtml(builtTitle(prev))}</a>` : "<span></span>") +
      (next ? `<a class="next" href="${next.file}"><span>Suivant →</span>${escapeHtml(builtTitle(next))}</a>` : "<span></span>");
    const out = template
      .replace("{{TITLE}}", escapeHtml(plainTitle(b.meta.title || "")))
      .replace("{{DESCRIPTION}}", escapeHtml(b.meta.description || ""))
      .replace("{{KICKER}}", escapeHtml(b.meta.kicker || "Statistiques avancées 3A · version pédagogique"))
      .replace("{{H1}}", () => processMath(b.meta.title || "", b.page.file))
      .replace("{{SUBTITLE}}", () => (b.meta.subtitle ? `<p class="subtitle">${processMath(b.meta.subtitle, b.page.file)}</p>` : ""))
      .replace("{{NAV}}", nav)
      .replace("{{TOC}}", b.toc)
      .replace("{{PAGER}}", pager)
      .replace("{{CSS}}", () => css)
      .replace("{{CONTENT}}", () => b.html)
      .replace("{{JS}}", () => js);
    fs.writeFileSync(path.join(outDir, b.page.file), out);
    console.log(`écrit ${b.page.file}  (${(out.length / 1024).toFixed(0)} Ko)`);
  }

  function builtTitle(p) {
    const b = built.find((x) => x.page.file === p.file);
    return (b && (b.meta.short || b.meta.title)) || p.nav;
  }

  // Avec des noms de pages en argument, on ne signale que leurs erreurs.
  const mine = (msg) => !only.length || only.some((f) => msg.startsWith(f));
  for (const w of warnings.filter(mine)) console.warn("avertissement  " + w);
  errors.splice(0, errors.length, ...errors.filter(mine));
  if (errors.length) {
    console.error(`\n${errors.length} erreur(s) :`);
    for (const e of errors) console.error("  " + e);
    process.exit(1);
  }
}

main();
