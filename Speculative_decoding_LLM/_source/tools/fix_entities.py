"""tools/fix_entities.py — inside formulas, replace &lt; / &gt; by < / > (KaTeX needs the raw characters).

    python3 tools/fix_entities.py pages/03_relaxed/*.html
"""
import re
import sys


def fix(src):
    def clean(m):
        return m.group(0).replace("&lt;", "<").replace("&gt;", ">")

    out = []
    # display formulas first, then inline formulas in what is left (same order as build.mjs)
    for k, part in enumerate(re.split(r"(\$\$[\s\S]+?\$\$)", src)):
        if k % 2:
            out.append(clean(re.match(r"[\s\S]*", part)))
        else:
            out.append(re.sub(r"(?<!\\)\$(?:[^$\\]|\\[\s\S])+?\$", clean, part))
    return "".join(out)


for f in sys.argv[1:]:
    s = open(f).read()
    t = fix(s)
    if s != t:
        open(f, "w").write(t)
        print("fixed", f)
