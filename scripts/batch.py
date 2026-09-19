# -*- coding: utf-8 -*-
"""Batch: download USPTO design-patent PDFs -> extract CCITT G4 image XObjects -> decode -> PNG.
Reuses the (verified) decoder in g4.py."""
import os, re, struct, json, ssl, urllib.request, importlib.util, sys

# 工作目录：优先环境变量 IPCHECK_DIR，否则用当前工作目录（在哪个案例目录里跑就处理哪的数据）
BASE = os.environ.get("IPCHECK_DIR") or os.getcwd()
# 解码器始终从本脚本所在目录加载 —— 避免误用案例目录里那份过期的 g4.py 拷贝
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location("g4", os.path.join(HERE, "g4.py"))
g4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g4)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HDRS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"}

TARGETS = ["D1019011", "D1070195"]
report = []


def fetch(url):
    r = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
        return resp.read()


def extract_images(data, out_prefix, min_w=800):
    objpos = [(int(m.group(1)), m.end()) for m in re.finditer(rb"(\d+)\s+(\d+)\s+obj", data)]
    imgs = []
    for (n, e) in objpos:
        end = data.find(b"endobj", e)
        body = data[e:end if end > 0 else len(data)]
        if b"/Image" not in body:
            continue
        head = body.split(b"stream", 1)[0]
        si = body.find(b"stream")
        if si < 0:
            continue
        p = si + 6
        if body[p:p+2] == b"\r\n":
            p += 2
        elif body[p:p+1] in (b"\n", b"\r"):
            p += 1
        raw = body[p:]
        ei = raw.rfind(b"endstream")
        if ei > 0:
            raw = raw[:ei]
        raw = raw.rstrip(b"\r\n")
        W = int(re.search(rb"/Width\s+(\d+)", head).group(1))
        H = int(re.search(rb"/Height\s+(\d+)", head).group(1))
        if W < min_w:
            continue
        imgs.append((W, H, raw))
    res = []
    for i, (W, H, raw) in enumerate(imgs):
        rows = g4.decode_g4(raw, W, H)
        rows = [bytearray(255 if v else 0 for v in r) for r in rows]
        black = sum(1 for r in rows for v in r if v)
        ratio = black / float(W * H)
        ds, nw, nh = g4.downsample(rows, W, H, 2)
        out = "%s_s%d.png" % (out_prefix, i)
        g4.write_png_gray(out, ds, nw, nh)
        res.append((out, W, H, ratio))
    return res


for t in TARGETS:
    try:
        pdf = fetch("https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/%s" % t)
        pdfp = os.path.join(BASE, "%s.pdf" % t)
        open(pdfp, "wb").write(pdf)
        got = extract_images(pdf, os.path.join(BASE, t))
        report.append("%s pdf=%d bytes  pages=%d" % (t, len(pdf), len(got)))
        for (out, W, H, ratio) in got:
            report.append("    %s %dx%d black=%.3f size=%d" % (os.path.basename(out), W, H, ratio, os.path.getsize(out)))
    except Exception as ex:
        report.append("%s FAIL %r" % (t, ex))

open(os.path.join(BASE, "_batch.txt"), "w", encoding="utf-8").write("\n".join(report))
print("done")
