#!/usr/bin/env python3
"""Dump a compact Markdown outline of the study-guide pages (sections, cards, statements, memo lines,
tricks, widgets). Used by the pages that must summarize the others (index, toolbox, memorize) and by reviewers.

Usage (from the study_guide folder):
    python3 tools/extract_outline.py [page.html …] > outline.md
    python3 tools/extract_outline.py --full 04_fixed_point_forward_backward.html   # also print 'idea' and 'why' text
"""
import os
import re
import sys

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGES = ["index.html", "01_convex_analysis.html", "02_subdifferential_conjugate.html", "03_proximity_operator.html",
         "04_fixed_point_forward_backward.html", "05_douglas_rachford_ppxa.html", "06_duality_admm_primal_dual.html",
         "07_majorization_minimization.html", "08_labs.html", "09_toolbox.html", "10_memorize.html"]


def txt(node, limit=None):
    if node is None:
        return ""
    s = node.get_text(" ", strip=True)
    s = re.sub(r"\s+", " ", s)
    if limit and len(s) > limit:
        s = s[:limit].rstrip() + " …"
    return s


def main():
    full = "--full" in sys.argv
    pages = [a for a in sys.argv[1:] if not a.startswith("--")] or PAGES
    for page in pages:
        path = os.path.join(ROOT, page)
        if not os.path.exists(path):
            print(f"\n# {page}\n\n(not written yet)")
            continue
        soup = BeautifulSoup(open(path, encoding="utf-8").read(), "lxml")
        title = txt(soup.find("title"))
        print(f"\n# {page} — {title}\n")
        nw = len(soup.select(".widget"))
        print(f"cards: {len(soup.select('article.card[id]'))} · widgets: {nw} · size: {os.path.getsize(path)//1024} KB\n")
        for sec in soup.select("section.chapter"):
            h2 = sec.find("h2")
            print(f"## [{sec.get('id')}] {txt(h2)}")
            lead = sec.select_one("header .lead")
            if lead:
                print(f"> {txt(lead, 300)}")
            for card in sec.select("article.card[id]"):
                kinds = [c for c in card.get("class", []) if c != "card"]
                h3 = card.select_one(".card-head h3")
                src = card.select_one(".card-head .src")
                print(f"- **{card.get('id')}** ({'/'.join(kinds)}) {txt(h3)} — {txt(src)}")
                st = card.select_one(".statement, .ex-statement")
                if st:
                    print(f"  - statement: {txt(st, 700)}")
                idea = card.select_one("p.idea")
                if idea:
                    print(f"  - idea: {txt(idea, 300)}")
                if full:
                    why = card.select_one(".why")
                    if why:
                        print(f"  - why: {txt(why, 900)}")
                memo = card.select_one(".callout.memo")
                if memo:
                    print(f"  - memo: {txt(memo, 300)}")
                tricks = sorted({a.get_text(strip=True)[:3] for a in card.select("a.chip.t b")})
                if tricks:
                    print(f"  - tricks: {', '.join(tricks)}")
                uses = [a.get("data-id") or a.get("href") for a in card.select(".chips a")]
                if uses:
                    print(f"  - links: {', '.join(u for u in uses if u)}")
                for w in card.select(".widget"):
                    print(f"  - widget #{w.get('id')}: {txt(w.select_one('.w-title'), 160)}")
            # widgets outside cards
            for w in sec.select(".widget"):
                if not w.find_parent("article"):
                    print(f"- widget #{w.get('id')}: {txt(w.select_one('.w-title'), 160)}")
        retain = soup.select_one("#retain .box")
        if retain:
            print("\n### What to retain")
            for li in retain.select("li"):
                print(f"- {txt(li, 220)}")


if __name__ == "__main__":
    main()
