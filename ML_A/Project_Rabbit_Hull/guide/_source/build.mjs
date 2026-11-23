// build.mjs — assembles the pages of the study guide for "Into the Rabbit Hull" (ML_A/Project_Rabbit_Hull/guide).
//
// A page is a folder pages/<Name>/ whose *.html parts are concatenated in file-name order (or a single
// file pages/<Name>.html). The first part starts with a header comment:
//   title, short, description, subtitle, kicker, footer, widgets (comma-separated names of widgets/*.js files;
//   default: the page name, e.g. 05_minkowski -> widgets/05_minkowski.js if it exists).
// Formulas are written $...$ (inline) and $$...$$ (display); they are rendered here with KaTeX, so the produced
// pages are self-contained: CSS, fonts and scripts are inlined, no connection is needed to read them.
//
// Images written <img data-src="paper_figures/x.jpg" alt="..."> are inlined as data URIs.
//
// Usage: npm install && node build.mjs            (writes ../*.html for every page that exists)
//        node build.mjs 05_minkowski.html         (one page only: fast, and only its errors are reported)

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import katex from "katex";

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.resolve(here, "..");
const katexDir = path.join(here, "node_modules", "katex", "dist");

// Reading order of the pages: navigation bar and previous/next links.
const PAGES = [
  { file: "index.html", nav: "Start here" },
  { file: "01_background.html", nav: "1 · Background" },
  { file: "02_toolbox.html", nav: "2 · Math toolbox" },
  { file: "03_concepts_tasks.html", nav: "3 · Part I: tasks" },
  { file: "04_statistics_geometry.html", nav: "4 · Part II: geometry" },
  { file: "05_minkowski.html", nav: "5 · Part III: Minkowski" },
  { file: "06_critical_reading.html", nav: "6 · Critical reading" },
  { file: "07_selftest.html", nav: "7 · Self-test" },
];
// Other documents of the project, shown after the pages in the navigation bar when they exist.
const EXTRA_LINKS = [
  { href: "../report/report.pdf", nav: "Report (PDF)" },
  { href: "../slides/slides.pdf", nav: "Slides (PDF)" },
];

const DEFAULT_FOOTER = "Study guide for <em>Into the Rabbit Hull: From Task-Relevant Concepts in DINO to Minkowski Geometry</em> " +
  "(Fel, Wang et al., arXiv:2510.08638, ICLR 2026). Figures marked “from the paper” are reproduced from the paper under its CC BY 4.0 licence.";

const MACROS = {
  "\\R": "\\mathbb{R}",
  "\\E": "\\mathbb{E}",
  "\\N": "\\mathcal{N}",
  "\\X": "\\mathcal{X}",
  "\\Y": "\\mathcal{Y}",
  "\\Pc": "\\mathcal{P}",
  "\\Qc": "\\mathcal{Q}",
  "\\Tc": "\\mathcal{T}",
  "\\Ac": "\\mathcal{A}",
  "\\Sc": "\\mathcal{S}",
  "\\Cc": "\\mathcal{C}",
  // vectors (bold lower case) and matrices (bold upper case), as in the paper
  "\\va": "\\boldsymbol{a}", "\\vb": "\\boldsymbol{b}", "\\vd": "\\boldsymbol{d}", "\\ve": "\\boldsymbol{e}",
  "\\vp": "\\boldsymbol{p}", "\\vq": "\\boldsymbol{q}", "\\vu": "\\boldsymbol{u}", "\\vv": "\\boldsymbol{v}",
  "\\vw": "\\boldsymbol{w}", "\\vx": "\\boldsymbol{x}", "\\vy": "\\boldsymbol{y}", "\\vz": "\\boldsymbol{z}",
  "\\vk": "\\boldsymbol{k}", "\\vg": "\\boldsymbol{g}", "\\vt": "\\boldsymbol{t}", "\\vm": "\\boldsymbol{m}",
  "\\val": "\\boldsymbol{\\alpha}", "\\vbe": "\\boldsymbol{\\beta}", "\\vga": "\\boldsymbol{\\gamma}", "\\vom": "\\boldsymbol{\\omega}",
  "\\vphi": "\\boldsymbol{\\phi}", "\\vsig": "\\boldsymbol{\\sigma}",
  "\\mA": "\\boldsymbol{A}", "\\mB": "\\boldsymbol{B}", "\\mC": "\\boldsymbol{C}", "\\mD": "\\boldsymbol{D}",
  "\\mG": "\\boldsymbol{G}", "\\mK": "\\boldsymbol{K}", "\\mP": "\\boldsymbol{P}", "\\mQ": "\\boldsymbol{Q}",
  "\\mS": "\\boldsymbol{S}", "\\mV": "\\boldsymbol{V}", "\\mW": "\\boldsymbol{W}", "\\mX": "\\boldsymbol{X}",
  "\\mY": "\\boldsymbol{Y}", "\\mZ": "\\boldsymbol{Z}", "\\mI": "\\boldsymbol{I}", "\\mU": "\\boldsymbol{U}",
  "\\mL": "\\boldsymbol{L}", "\\mH": "\\boldsymbol{H}", "\\mR": "\\boldsymbol{R}",
  "\\conv": "\\operatorname{conv}",
  "\\relint": "\\operatorname{relint}",
  "\\supp": "\\operatorname{supp}",
  "\\diam": "\\operatorname{diam}",
  "\\tr": "\\operatorname{tr}",
  "\\rank": "\\operatorname{rank}",
  "\\Ima": "\\operatorname{Im}",
  "\\spn": "\\operatorname{span}",
  "\\softmax": "\\operatorname{softmax}",
  "\\diag": "\\operatorname{diag}",
  "\\cov": "\\operatorname{cov}",
  "\\Var": "\\operatorname{Var}",
  "\\LN": "\\operatorname{LN}",
  "\\argmin": "\\operatorname*{arg\\,min}",
  "\\argmax": "\\operatorname*{arg\\,max}",
  "\\msum": "\\oplus",
  "\\bigmsum": "\\bigoplus",
  "\\simplex": "\\Delta",
  "\\eps": "\\varepsilon",
  "\\T": "^{\\top}",
  "\\ind": "\\mathbf{1}",
  "\\dd": "\\mathrm{d}",
  "\\norm": "\\left\\lVert #1 \\right\\rVert",
  "\\abs": "\\left\\lvert #1 \\right\\rvert",
  "\\ps": "\\langle #1,\\, #2 \\rangle",
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

// Renders $$...$$ then $...$, leaving <script>, <style>, <svg> and comments untouched.
function processMath(src, file) {
  const protectedRe = /<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>|<svg[\s\S]*?<\/svg>|<!--[\s\S]*?-->/g;
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
  // \$ = literal dollar
  const DOLLAR = "\u0000DOLLAR\u0000";
  chunk = chunk.replace(/\\\$/g, DOLLAR);
  chunk = chunk.replace(/\$\$([\s\S]+?)\$\$/g, (m, tex, i) =>
    `<div class="math-display">${renderMath(tex.trim(), true, file, src, offset + i)}</div>`);
  chunk = chunk.replace(/\$((?:[^$\\]|\\[\s\S])+?)\$([.,;:!?)\]%]+)?/g, (m, tex, punct, i) => {
    if (/\n\s*\n/.test(tex)) {
      errors.push(`${file}:${lineOf(src, offset + i)}  unclosed $ (inline formula across an empty line)`);
      return m;
    }
    const html = renderMath(tex, false, file, src, offset + i);
    if (!punct) return html;
    // Punctuation right after a formula must not start a new line. A browser may break after the last
    // block of a KaTeX formula (an inline-block), even before a word joiner or a no-break space, so the
    // sign goes INSIDE that last block, just before its three closing tags (block, katex-html, katex).
    const tail = "</span></span></span>";
    return html.endsWith(tail) ? html.slice(0, -tail.length) + `<span class="kp">${punct}</span>` + tail : html + punct;
  });
  return chunk.replace(new RegExp(DOLLAR, "g"), "$");
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

// Tab title: strip the TeX syntax of formulas.
function plainTitle(s) {
  return s.replace(/\$([^$]*)\$/g, (m, t) => t.replace(/\\[a-zA-Z]+/g, "").replace(/[{}^_\\]/g, ""));
}

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// Every h2 and h3 must carry an explicit, stable id (other pages link to them).
// Builds the table of contents and checks the internal anchors.
function buildToc(html, file) {
  const used = new Set();
  const items = [];
  html = html.replace(/<h([23])((?:\s[^>]*)?)>([\s\S]*?)<\/h\1>/g, (m, lvl, attrs, inner) => {
    const id = (attrs.match(/\sid="([^"]+)"/) || [])[1];
    if (!id) { errors.push(`${file}: <h${lvl}> without an explicit id: ${inner.replace(/<[^>]+>/g, "").slice(0, 60)}`); return m; }
    if (used.has(id)) errors.push(`${file}: duplicate id "${id}"`);
    used.add(id);
    // The table of contents does not show references ("notes p. 2").
    const tocInner = inner.replace(/<(a|span) class="ref"[^>]*>[\s\S]*?<\/\1>/g, "").trim();
    if (!/\bdata-notoc\b/.test(attrs)) items.push({ lvl: Number(lvl), id, inner: tocInner });
    return `<h${lvl}${attrs}>${inner}<a class="anchor" href="#${id}" aria-label="Link to this section">#</a></h${lvl}>`;
  });
  const all = [...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]);
  const seen = new Set();
  for (const id of all) {
    if (seen.has(id) && !used.has(id)) errors.push(`${file}: duplicate id "${id}"`);
    seen.add(id);
  }
  const ids = new Set(all);
  for (const m of html.matchAll(/href="#([^"]+)"/g)) {
    if (!ids.has(m[1])) errors.push(`${file}: internal link #${m[1]} has no target`);
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

// <!-- include figures/L05/x.svg --> is replaced by the file (generated by figures_LNN.py), on one line
// so that the line numbers of the error messages stay exact.
function withIncludes(src, name) {
  return src.replace(/<!--\s*include\s+(\S+)\s*-->/g, (m, f) => {
    const p = path.join(here, f);
    if (!fs.existsSync(p)) { errors.push(`${name}: include of missing file ${f}`); return ""; }
    return fs.readFileSync(p, "utf8").replace(/\s*\n\s*/g, " ").trim();
  });
}

// <img data-src="paper_figures/x.jpg" ...> is inlined as a data URI, so that the page stays self-contained.
const MIME = { ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".svg": "image/svg+xml" };
function inlineImages(html, name) {
  return html.replace(/<img([^>]*?)\sdata-src="([^"]+)"([^>]*)>/g, (m, a, f, b) => {
    const p = path.join(here, f);
    if (!fs.existsSync(p)) { errors.push(`${name}: image ${f} not found`); return m; }
    if (!/\salt="/.test(a + b)) errors.push(`${name}: image ${f} has no alt text`);
    const mime = MIME[path.extname(f).toLowerCase()];
    if (!mime) { errors.push(`${name}: image ${f} has an unsupported type`); return m; }
    return `<img${a} src="data:${mime};base64,${fs.readFileSync(p).toString("base64")}"${b} loading="lazy">`;
  });
}

// The parts of a page, in order.
function partsOf(p) {
  const dir = path.join(here, "pages", p.file.replace(/\.html$/, ""));
  if (fs.existsSync(dir) && fs.statSync(dir).isDirectory()) {
    return fs.readdirSync(dir).filter((f) => f.endsWith(".html")).sort().map((f) => {
      const name = `${path.basename(dir)}/${f}`;
      return { name, src: withIncludes(fs.readFileSync(path.join(dir, f), "utf8"), name) };
    });
  }
  const single = path.join(here, "pages", p.file);
  return fs.existsSync(single) ? [{ name: p.file, src: withIncludes(fs.readFileSync(single, "utf8"), p.file) }] : [];
}

// The script of a page: app.js with the page's widget files inserted at its placeholder.
function pageScript(page, meta, appJs) {
  const base = page.file.replace(/\.html$/, "");
  const names = (meta.widgets ? meta.widgets.split(",").map((s) => s.trim()).filter(Boolean) : [base]);
  let code = "";
  for (const n of names) {
    const f = path.join(here, "widgets", `${n}.js`);
    if (fs.existsSync(f)) code += `\n  /* ---- widgets/${n}.js ---- */\n` + fs.readFileSync(f, "utf8") + "\n";
    else if (meta.widgets) errors.push(`${page.file}: widget file widgets/${n}.js not found`);
  }
  const js = appJs.replace("/* @@PAGE_WIDGETS@@ */", () => code);
  try { new Function(js); } catch (e) { errors.push(`${page.file}: JavaScript syntax error in app.js + widgets (${names.join(", ")}): ${e.message}`); }
  return js;
}

function main() {
  const template = fs.readFileSync(path.join(here, "template.html"), "utf8");
  const css = katexCss() + "\n" + fs.readFileSync(path.join(here, "style.css"), "utf8");
  const appJs = fs.readFileSync(path.join(here, "app.js"), "utf8");
  const only = process.argv.slice(2);

  const present = PAGES.filter((p) => partsOf(p).length);
  const allIds = {};
  const built = [];

  for (const [i, page] of present.entries()) {
    const parts = partsOf(page);
    const { meta, body } = parseFront(parts[0].src);
    if (only.length && !only.includes(page.file)) {
      // Not built this time: only collect its ids, for the links between pages.
      allIds[page.file] = new Set(parts.flatMap((pt) => [...pt.src.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
      built.push({ page, meta, i, skip: true });
      continue;
    }
    if (!meta.title) errors.push(`${parts[0].name}: no "title" in the header`);
    // Formulas are rendered part by part, so that errors point to the right file and line
    // (the header comment is replaced by blank lines so that line numbers stay exact).
    const headerLines = parts[0].src.length - body.length ? parts[0].src.slice(0, parts[0].src.length - body.length).split("\n").length - 1 : 0;
    const html = [processMath("\n".repeat(headerLines) + body, parts[0].name), ...parts.slice(1).map((pt) => processMath(pt.src, pt.name))].join("\n");
    const t = buildToc(html, page.file);
    allIds[page.file] = t.ids;
    built.push({ page, meta, html: t.html, toc: t.toc, i });
  }

  // Links between v2 pages: file and anchor must exist.
  for (const b of built) {
    if (b.skip) continue;
    for (const m of b.html.matchAll(/href="((?:index|0\d_[a-z_]+)\.html)(?:#([^"]+))?"/g)) {
      const ids = allIds[m[1]];
      if (!ids) { warnings.push(`${b.page.file}: link to ${m[1]} (page not written yet)`); continue; }
      if (m[2] && !ids.has(m[2])) errors.push(`${b.page.file}: link ${m[1]}#${m[2]} has no target`);
    }
    // Links to the other documents of the project (report, slides, code) must point to existing files.
    for (const m of b.html.matchAll(/href="(\.\.\/[^"#]+)(?:#[^"]*)?"/g)) {
      const target = path.resolve(outDir, decodeURIComponent(m[1]));
      if (!fs.existsSync(target)) errors.push(`${b.page.file}: link to missing file ${m[1]}`);
    }
  }

  for (const b of built) {
    if (b.skip) continue;
    const prev = present[b.i - 1];
    const next = present[b.i + 1];
    const nav = present
      .map((p) => `<a href="${p.file}"${p.file === b.page.file ? ' aria-current="page"' : ""}>${p.nav}</a>`)
      .concat(EXTRA_LINKS.filter((l) => fs.existsSync(path.resolve(outDir, l.href))).map((l) => `<a class="v1" href="${l.href}">${l.nav}</a>`))
      .join("");
    const pager =
      (prev ? `<a class="prev" href="${prev.file}"><span>← Previous</span>${escapeHtml(titleOf(prev))}</a>` : "<span></span>") +
      (next ? `<a class="next" href="${next.file}"><span>Next →</span>${escapeHtml(titleOf(next))}</a>` : "<span></span>");
    const out = template
      .replace("{{TITLE}}", escapeHtml(plainTitle(b.meta.title || "")))
      .replace("{{DESCRIPTION}}", escapeHtml(b.meta.description || ""))
      .replace("{{KICKER}}", escapeHtml(b.meta.kicker || "Into the Rabbit Hull · study guide"))
      .replace("{{H1}}", () => processMath(b.meta.title || "", b.page.file))
      .replace("{{SUBTITLE}}", () => (b.meta.subtitle ? `<p class="subtitle">${processMath(b.meta.subtitle, b.page.file)}</p>` : ""))
      .replace("{{NAV}}", nav)
      .replace("{{TOC}}", b.toc)
      .replace("{{PAGER}}", pager)
      .replace("{{FOOTER}}", () => b.meta.footer || DEFAULT_FOOTER)
      .replace("{{CSS}}", () => css)
      .replace("{{CONTENT}}", () => inlineImages(b.html, b.page.file))
      .replace("{{JS}}", () => pageScript(b.page, b.meta, appJs));
    fs.writeFileSync(path.join(outDir, b.page.file), out);
    console.log(`wrote ${b.page.file}  (${(out.length / 1024).toFixed(0)} KB)`);
  }

  function titleOf(p) {
    const b = built.find((x) => x.page.file === p.file);
    return (b && (b.meta.short || b.meta.title)) || p.nav;
  }

  // With page names as arguments, only their errors are reported.
  const mine = (msg) => !only.length || only.some((f) => msg.startsWith(f) || msg.startsWith(f.replace(/\.html$/, "/")));
  for (const w of warnings.filter(mine)) console.warn("warning  " + w);
  errors.splice(0, errors.length, ...errors.filter(mine));
  if (errors.length) {
    console.error(`\n${errors.length} error(s):`);
    for (const e of errors) console.error("  " + e);
    process.exit(1);
  }
}

main();
