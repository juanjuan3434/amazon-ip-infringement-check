# -*- coding: utf-8 -*-
"""Catalog image XObjects inside a USPTO PDF without decoding (fast)."""
import os, re, sys, json

path = sys.argv[1]
out = sys.argv[2]
data = open(path, "rb").read()
objpos = [(int(m.group(1)), m.end()) for m in re.finditer(rb"(\d+)\s+(\d+)\s+obj", data)]
rows = []
idx = 0
for (n, e) in objpos:
    end = data.find(b"endobj", e)
    body = data[e:end if end > 0 else len(data)]
    if b"/Image" not in body:
        continue
    head = body.split(b"stream", 1)[0]
    mw = re.search(rb"/Width\s+(\d+)", head)
    mh = re.search(rb"/Height\s+(\d+)", head)
    if not mw or not mh:
        rows.append("obj %d: no Width/Height  filters=%s" % (n, re.findall(rb"/(\w+Decode)", head)))
        continue
    W, H = int(mw.group(1)), int(mh.group(1))
    si = body.find(b"stream")
    p = si + 6
    if body[p:p+2] == b"\r\n":
        p += 2
    elif body[p:p+1] in (b"\n", b"\r"):
        p += 1
    raw = body[p:]
    ei = raw.rfind(b"endstream")
    if ei > 0:
        raw = raw[:ei]
    rows.append("idx=%d obj=%d  %dx%d  rawlen=%d  filters=%s"
                % (idx, n, W, H, len(raw.rstrip(b"\r\n")),
                   [f.decode() for f in re.findall(rb"/(\w+Decode)", head)]))
    idx += 1
open(out, "w", encoding="utf-8").write("\n".join(rows))
print("images:", idx)
