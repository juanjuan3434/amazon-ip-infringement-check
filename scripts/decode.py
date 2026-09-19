# -*- coding: utf-8 -*-
"""Decode selected pages of a USPTO PDF to PNG (cone collar case)."""
import os, re, sys, importlib.util

# 解码器从本脚本所在目录加载（与安装位置无关，换机器/换用户名都能跑）
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("g4", os.path.join(HERE, "g4.py"))
g4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g4)

pdf = sys.argv[1]
outdir = sys.argv[2]
want = [int(x) for x in sys.argv[3].split(",")]
scale = int(sys.argv[4]) if len(sys.argv) > 4 else 2
tag = os.path.splitext(os.path.basename(pdf))[0]

data = open(pdf, "rb").read()
objpos = [(int(m.group(1)), m.end()) for m in re.finditer(rb"(\d+)\s+(\d+)\s+obj", data)]
imgs = []
for (n, e) in objpos:
    end = data.find(b"endobj", e)
    body = data[e:end if end > 0 else len(data)]
    if b"/Image" not in body:
        continue
    head = body.split(b"stream", 1)[0]
    mw = re.search(rb"/Width\s+(\d+)", head)
    mh = re.search(rb"/Height\s+(\d+)", head)
    if not mw or not mh:
        continue
    W, H = int(mw.group(1)), int(mh.group(1))
    if W < 800:
        continue
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
    imgs.append((W, H, raw.rstrip(b"\r\n")))

log = ["%s: %d image pages found" % (tag, len(imgs))]
for i, (W, H, _) in enumerate(imgs):
    log.append("  idx %02d  %dx%d" % (i, W, H))

os.makedirs(outdir, exist_ok=True)
for i in want:
    if i >= len(imgs):
        log.append("  page %d missing" % i)
        continue
    W, H, raw = imgs[i]
    rows = g4.decode_g4(raw, W, H)
    hr = [bytearray(1 if any(r[j:j+scale]) else 0 for j in range(0, W, scale)) for r in rows]
    out_rows = []
    for y in range(0, H, scale):
        blk = hr[y:y+scale]
        base = blk[0]
        for extra in blk[1:]:
            base = bytearray(1 if (base[k] or extra[k]) else 0 for k in range(len(base)))
        out_rows.append(bytearray(0 if v else 255 for v in base))
    fn = os.path.join(outdir, "%s_p%02d.png" % (tag, i))
    g4.write_png_gray(fn, out_rows, W // scale, H // scale)
    log.append("  page %02d -> %s  %dx%d  %d bytes" % (i, os.path.basename(fn), W // scale, H // scale, os.path.getsize(fn)))

open(os.path.join(outdir, "_decoded.txt"), "w", encoding="utf-8").write("\n".join(log))
print("\n".join(log))
