# -*- coding: utf-8 -*-
"""Decode selected sheets from a downloaded USPTO design-patent PDF (fast path)."""
import os, re, sys, importlib.util

BASE = r"C:\Users\34347\WorkBuddy\2026-08-21-09-54-29\ip_check\bandana_figs"
spec = importlib.util.spec_from_file_location("g4", os.path.join(BASE, "g4.py"))
g4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g4)

pat = sys.argv[1]                       # e.g. D1019011
want = [int(x) for x in sys.argv[2].split(",")]

data = open(os.path.join(BASE, "%s.pdf" % pat), "rb").read()
objpos = [(int(m.group(1)), m.end()) for m in re.finditer(rb"(\d+)\s+(\d+)\s+obj", data)]
imgs = []
for (n, e) in objpos:
    end = data.find(b"endobj", e)
    body = data[e:end if end > 0 else len(data)]
    if b"/Image" not in body:
        continue
    head = body.split(b"stream", 1)[0]
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
    mw = re.search(rb"/Width\s+(\d+)", head)
    mh = re.search(rb"/Height\s+(\d+)", head)
    if not mw or not mh:
        continue
    W = int(mw.group(1))
    H = int(mh.group(1))
    if W < 800:
        continue
    imgs.append((W, H, raw.rstrip(b"\r\n")))

log = ["%s: %d image xobjects" % (pat, len(imgs))]
for i in want:
    if i >= len(imgs):
        log.append("  sheet %d: missing" % i)
        continue
    W, H, raw = imgs[i]
    rows = g4.decode_g4(raw, W, H)
    # fast downsample by 2 using C-level any() on slices
    hr = [bytearray(1 if any(r[j:j+2]) else 0 for j in range(0, W, 2)) for r in rows]
    out_rows = []
    for y in range(0, H, 2):
        blk = hr[y:y+2]
        base = blk[0]
        if len(blk) > 1:
            b2 = blk[1]
            base = bytearray(1 if (base[k] or b2[k]) else 0 for k in range(len(base)))
        out_rows.append(bytearray(0 if v else 255 for v in base))
    fn = os.path.join(BASE, "%s_sheet%d.png" % (pat, i))
    g4.write_png_gray(fn, out_rows, W // 2, H // 2)
    log.append("  sheet %d -> %s  %dx%d  %d bytes" % (i, os.path.basename(fn), W // 2, H // 2, os.path.getsize(fn)))

open(os.path.join(BASE, "_sheets.txt"), "w", encoding="utf-8").write("\n".join(log))
print("done")
