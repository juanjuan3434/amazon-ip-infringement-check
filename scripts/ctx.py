# -*- coding: utf-8 -*-
"""从 Amazon HTML 中抽取指定关键词周围的上下文（用于定位关联商品、专利声明等）。"""
import html
import re
import sys

src = sys.argv[1]
kw = sys.argv[2]
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 1200

raw = open(src, encoding="utf-8", errors="ignore").read()


def clean(s):
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


out = []
for m in re.finditer(re.escape(kw), raw, re.I):
    a = max(0, m.start() - ctx)
    b = min(len(raw), m.end() + ctx)
    seg = raw[a:b]
    out.append("=" * 80)
    asins = sorted(set(re.findall(r"/dp/([A-Z0-9]{10})", seg)))
    out.append("邻近 ASIN: " + (", ".join(asins) or "-"))
    out.append(clean(seg))

open("_ctx.txt", "w", encoding="utf-8").write("\n".join(out))
print("matches:", len(out) // 3)
