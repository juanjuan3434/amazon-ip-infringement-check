# -*- coding: utf-8 -*-
"""把 FPO 单篇专利页 HTML 的正文抽成文本（供 fmt.py 再断行）。"""
import html
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
raw = open(src, encoding="utf-8", errors="ignore").read()

# 去掉脚本/样式
t = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.I)
t = re.sub(r"<style[\s\S]*?</style>", " ", t, flags=re.I)
t = re.sub(r"<!--[\s\S]*?-->", " ", t)
t = re.sub(r"<[^>]+>", " ", t)
t = html.unescape(t)
t = re.sub(r"\s+", " ", t).strip()
open(dst, "w", encoding="utf-8").write(t)
print("written", dst, len(t))
