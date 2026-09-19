# -*- coding: utf-8 -*-
"""解析 FPO 检索结果页，输出「专利号 | 名称 | 日期 | 权利人」清单。"""
import html
import re
import sys

src = sys.argv[1]
raw = open(src, encoding="utf-8", errors="ignore").read()

# FPO 结果条目：<a href="/xxxxxxx.html">Title</a> 附近含日期
out = []
for m in re.finditer(r'<a[^>]+href="/([A-Z0-9]{6,12})\.html"[^>]*>([\s\S]{0,300}?)</a>', raw, re.I):
    num, title = m.group(1), html.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))
    title = re.sub(r"\s+", " ", title).strip()
    if not title or len(title) < 4:
        continue
    tail = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw[m.end():m.end() + 700])))
    out.append("%-12s | %s | %s" % (num, title[:110], tail[:220]))

seen, res = set(), []
for line in out:
    k = line.split("|")[0].strip()
    if k in seen:
        continue
    seen.add(k)
    res.append(line)

# 结果总数
m = re.search(r'([\d,]+)\s*(?:results|matches)', raw, re.I)
head = ("总数: " + m.group(1)) if m else "总数: ?"
open(sys.argv[2], "w", encoding="utf-8").write(head + "\n" + "\n".join(res))
print(head, "条目:", len(res))
