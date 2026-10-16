#!/usr/bin/env python3
"""Build assets/registry.js from the study-guide pages and check the guide's integrity.

Usage (from the study_guide folder):
    python3 tools/build_registry.py            # rebuild registry only
    python3 tools/build_registry.py --check    # rebuild + report missing canonical ids, duplicate ids,
                                               # broken links, malformed HTML
    python3 tools/build_registry.py --check --ids /path/to/ids.json   # custom canonical id list

The registry maps every element that has an id and lives in an <article class="card …"> (or any element
with data-registry) to {p: page, k: kind, t: title, s: statement html}. The popovers of guide.js read it.
"""
import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGES = ["index.html", "01_convex_analysis.html", "02_subdifferential_conjugate.html", "03_proximity_operator.html",
         "04_fixed_point_forward_backward.html", "05_douglas_rachford_ppxa.html", "06_duality_admm_primal_dual.html",
         "07_majorization_minimization.html", "08_labs.html", "09_toolbox.html", "10_memorize.html"]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
KINDS = ["def", "thm", "prop", "lemma", "cor", "algo", "rem", "ex", "lab", "trick", "sec"]
DEFAULT_IDS = "/tmp/claude-0/-home-user-MVA-courses/f24c33d9-fb2f-5d73-b038-590fc5d05386/scratchpad/spec/ids.json"


class Scanner(HTMLParser):
    """Collect ids, links, cards (with title + statement html) and check tag balance."""

    def __init__(self, page):
        super().__init__(convert_charrefs=False)
        self.page = page
        self.ids = {}          # id -> line
        self.dups = []
        self.links = []        # (href, line)
        self.cards = {}        # id -> dict(k, t, s)
        self.stack = []        # open tags (name, line, attrs)
        self.errors = []
        self.sections = {}     # id -> title for section/div ids with h2/h3
        self._cur_card = None  # (id, depth)
        self._capture = None   # dict(kind='statement'|'h3', depth, buf)
        self._card_depth = None
        self.raw = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        line = self.getpos()[0]
        if tag not in VOID:
            self.stack.append((tag, line))
        if tag == "p":
            # p inside p is malformed
            for t, l in reversed(self.stack[:-1]):
                if t == "p":
                    self.errors.append(f"line {line}: <p> nested inside <p> opened at line {l}")
                    break
                if t in ("div", "section", "article", "details", "li", "td", "th", "body", "main", "blockquote", "figure", "header", "footer", "nav", "aside"):
                    break
        if "id" in a:
            i = a["id"]
            if i in self.ids:
                self.dups.append((i, line, self.ids[i]))
            else:
                self.ids[i] = line
        if tag == "a" and "href" in a:
            self.links.append((a["href"], line))
        cls = (a.get("class") or "").split()
        if tag == "article" and "card" in cls and "id" in a:
            kind = next((c for c in cls if c in KINDS), "card")
            self._cur_card = a["id"]
            self._card_depth = len(self.stack)
            self.cards[a["id"]] = {"k": kind, "t": "", "s": ""}
        if self._cur_card and self._capture is None:
            if tag == "h3" and not self.cards[self._cur_card]["t"]:
                self._capture = {"kind": "t", "depth": len(self.stack), "buf": []}
                return
            if tag == "div" and ("statement" in cls or "ex-statement" in cls) and not self.cards[self._cur_card]["s"]:
                self._capture = {"kind": "s", "depth": len(self.stack), "buf": []}
                return
        if self._capture is not None:
            self._capture["buf"].append(self.get_starttag_text())
        if tag in ("section", "div") and "id" in a:
            self.sections[a["id"]] = None

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            i = a["id"]
            line = self.getpos()[0]
            if i in self.ids:
                self.dups.append((i, line, self.ids[i]))
            else:
                self.ids[i] = line
        if self._capture is not None:
            self._capture["buf"].append(self.get_starttag_text())

    def handle_endtag(self, tag):
        line = self.getpos()[0]
        if tag in VOID:
            return
        # pop stack
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            # find matching tag in stack
            idx = None
            for k in range(len(self.stack) - 1, -1, -1):
                if self.stack[k][0] == tag:
                    idx = k
                    break
            if idx is None:
                self.errors.append(f"line {line}: stray closing tag </{tag}>")
            else:
                for t, l in self.stack[idx + 1:]:
                    self.errors.append(f"line {line}: </{tag}> closes <{t}> opened at line {l} (unclosed)")
                del self.stack[idx:]
        if self._capture is not None:
            if len(self.stack) < self._capture["depth"]:
                kind = self._capture["kind"]
                html = "".join(self._capture["buf"])
                if kind == "t":
                    self.cards[self._cur_card]["t"] = html
                else:
                    self.cards[self._cur_card]["s"] = html
                self._capture = None
            else:
                self._capture["buf"].append(f"</{tag}>")
        if self._cur_card and self._card_depth is not None and len(self.stack) < self._card_depth:
            self._cur_card = None
            self._card_depth = None

    def handle_data(self, data):
        if self._capture is not None:
            self._capture["buf"].append(data)

    def handle_entityref(self, name):
        if self._capture is not None:
            self._capture["buf"].append(f"&{name};")

    def handle_charref(self, name):
        if self._capture is not None:
            self._capture["buf"].append(f"&#{name};")

    def handle_comment(self, data):
        pass


def strip_tags(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s).strip()


def clean_statement(s, limit=1600):
    s = re.sub(r"<span class=\"lbl\">.*?</span>", "", s, count=1, flags=re.S)
    s = re.sub(r"<details.*?</details>", "", s, flags=re.S)
    s = re.sub(r"<a class=\"anchor\"[^>]*>#</a>", "", s)
    s = s.strip()
    if len(s) > limit:
        # cut at a paragraph boundary if possible
        cut = s.rfind("</p>", 0, limit)
        s = (s[:cut + 4] if cut > 200 else s[:limit]) + "<p class=\"mini\">…</p>"
    return s


def main():
    check = "--check" in sys.argv
    ids_path = DEFAULT_IDS
    if "--ids" in sys.argv:
        ids_path = sys.argv[sys.argv.index("--ids") + 1]
    canonical = {}
    if os.path.exists(ids_path):
        with open(ids_path, encoding="utf-8") as fh:
            canonical = json.load(fh)

    registry = {}
    all_ids = {}   # page -> set(ids)
    scans = {}
    problems = 0
    for page in PAGES:
        path = os.path.join(ROOT, page)
        if not os.path.exists(path):
            all_ids[page] = None
            continue
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        sc = Scanner(page)
        try:
            sc.feed(src)
            sc.close()
        except Exception as e:  # pragma: no cover
            sc.errors.append(f"parser exception: {e}")
        for t, l in sc.stack:
            if t not in ("html", "body"):
                sc.errors.append(f"EOF: <{t}> opened at line {l} never closed")
        scans[page] = sc
        all_ids[page] = set(sc.ids.keys())
        for cid, c in sc.cards.items():
            registry[cid] = {"p": page, "k": c["k"], "t": strip_tags(c["t"]), "s": clean_statement(c["s"])}
        # sections with canonical ids: register title from the heading that follows
        for cid, meta in ((m["id"], m) for m in canonical.get(page, []) if m["k"] in ("sec",)):
            if cid in sc.ids and cid not in registry:
                m = re.search(r'id="%s"[^>]*>.*?<h[23][^>]*>(.*?)</h[23]>' % re.escape(cid), src, flags=re.S)
                registry[cid] = {"p": page, "k": "sec", "t": strip_tags(m.group(1)) if m else meta["t"], "s": ""}

    out = os.path.join(ROOT, "assets", "registry.js")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("/* generated by tools/build_registry.py — do not edit */\n")
        fh.write("window.LSD_REGISTRY = ")
        json.dump(registry, fh, ensure_ascii=False, indent=0)
        fh.write(";\n")
    print(f"registry: {len(registry)} entries from {sum(1 for p in all_ids.values() if p is not None)} pages -> assets/registry.js")

    if not check:
        return 0

    # canonical ids
    for page, items in canonical.items():
        if all_ids.get(page) is None:
            print(f"[pending] {page}: page not written yet ({len(items)} canonical ids expected)")
            continue
        missing = [m["id"] for m in items if m["id"] not in all_ids[page]]
        if missing:
            problems += len(missing)
            print(f"[MISSING IDS] {page}: {', '.join(missing)}")
        # kind consistency
        sc = scans[page]
        for m in items:
            if m["id"] in sc.cards and m["k"] not in ("sec",) and sc.cards[m["id"]]["k"] != m["k"]:
                print(f"[kind] {page}#{m['id']}: card kind '{sc.cards[m['id']]['k']}' but canonical kind is '{m['k']}' (acceptable if intentional)")
    # duplicates, html errors, links
    canon_by_page = {p: {m["id"] for m in items} for p, items in canonical.items()}
    for page, sc in scans.items():
        for i, l, l0 in sc.dups:
            problems += 1
            print(f"[DUPLICATE ID] {page}: '{i}' at line {l} (first at line {l0})")
        for e in sc.errors:
            problems += 1
            print(f"[HTML] {page}: {e}")
        for href, line in sc.links:
            if href.startswith(("http://", "https://", "mailto:", "../")):
                continue
            if href.startswith("#"):
                tgt_page, frag = page, href[1:]
            else:
                parts = href.split("#", 1)
                tgt_page = parts[0]
                frag = parts[1] if len(parts) > 1 else ""
            if tgt_page not in PAGES:
                if tgt_page.startswith("assets/") or tgt_page.startswith("tools/") or tgt_page.startswith("../"):
                    continue
                problems += 1
                print(f"[BROKEN LINK] {page} line {line}: unknown page '{href}'")
                continue
            if not frag:
                continue
            if all_ids.get(tgt_page) is None:
                if frag in canon_by_page.get(tgt_page, set()):
                    continue  # pending page, canonical id: fine
                print(f"[pending link] {page} line {line}: '{href}' (page not written yet, id not canonical)")
                continue
            if frag not in all_ids[tgt_page]:
                problems += 1
                print(f"[BROKEN LINK] {page} line {line}: '{href}' (no element with that id)")
        # cards without required parts (theorem-like)
        src = open(os.path.join(ROOT, page), encoding="utf-8").read()
        for cid, c in sc.cards.items():
            if c["k"] in ("thm", "prop", "lemma", "cor"):
                m = re.search(r'<article class="card [^"]*" id="%s".*?</article>' % re.escape(cid), src, flags=re.S)
                body = m.group(0) if m else ""
                need = {"statement": 'class="statement"', "idea": 'class="idea"', "why": 'class="why"', "proof": "details class=\"pl proof\"", "memo": "callout memo", "chips": 'class="chips"'}
                lacking = [k for k, v in need.items() if v not in body]
                if lacking:
                    print(f"[incomplete card] {page}#{cid}: missing {', '.join(lacking)}")
            if c["k"] == "def":
                m = re.search(r'<article class="card [^"]*" id="%s".*?</article>' % re.escape(cid), src, flags=re.S)
                body = m.group(0) if m else ""
                lacking = [k for k, v in {"statement": 'class="statement"', "idea": 'class="idea"', "memo": "callout memo"}.items() if v not in body]
                if lacking:
                    print(f"[incomplete card] {page}#{cid}: missing {', '.join(lacking)}")
        # raw '$' inside svg text is a sign of maths in SVG
        for mm in re.finditer(r"<svg.*?</svg>", src, flags=re.S):
            if "$" in mm.group(0) and "<script" not in mm.group(0):
                print(f"[warn] {page}: '$' inside an <svg> block near line {src[:mm.start()].count(chr(10)) + 1} (KaTeX does not render inside SVG)")
        # widgets count
        nw = len(re.findall(r'class="widget"', src))
        print(f"[info] {page}: {len(sc.cards)} cards, {nw} widgets, {len(sc.ids)} ids, {len(sc.links)} links")
    print(f"check finished: {problems} blocking problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
