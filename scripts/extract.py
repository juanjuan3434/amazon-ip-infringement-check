import re, os, struct, json

# 工作目录：优先环境变量 IPCHECK_DIR，否则用当前工作目录
base = os.environ.get("IPCHECK_DIR") or os.getcwd()
path = os.path.join(base, "D1000009.pdf")     # ← 改成你要解析的 PDF 文件名
data = open(path, "rb").read()

log = []

# --- locate all indirect objects with their offsets ---
objpos = []
for m in re.finditer(rb"(\d+)\s+(\d+)\s+obj", data):
    objpos.append((int(m.group(1)), m.start(), m.end()))

def get_body(num):
    """return bytes from after 'N 0 obj' to before matching endobj"""
    for (n, s, e) in objpos:
        if n == num:
            end = data.find(b"endobj", e)
            return data[e:end if end > 0 else len(data)]
    return None

# --- build a name -> object number map from the trailer/xref is hard; instead scan all objects for image dicts ---
images = []
for (n, s, e) in objpos:
    body = get_body(n)
    if body is None:
        continue
    if b"/Image" not in body:
        continue
    head = body.split(b"stream", 1)[0]
    # raw stream bytes
    si = body.find(b"stream")
    if si < 0:
        continue
    # skip EOL after 'stream'
    p = si + len(b"stream")
    if body[p:p+2] == b"\r\n":
        p += 2
    elif body[p:p+1] in (b"\n", b"\r"):
        p += 1
    raw = body[p:]
    # strip trailing EOL before endstream
    ei = raw.rfind(b"endstream")
    if ei > 0:
        raw = raw[:ei]
    raw = raw.rstrip(b"\r\n")

    def gv(key, default=None, txt=head):
        m = re.search(rb"/" + key + rb"\s+(-?\d+)", txt)
        return int(m.group(1)) if m else default

    W = gv(b"Width"); H = gv(b"Height"); BPC = gv(b"BitsPerComponent", 1)
    K = gv(b"K")
    BlackIs1 = re.search(rb"/BlackIs1\s+(true|false)", head)
    log.append(dict(obj=n, Width=W, Height=H, BPC=BPC, K=K,
                    BlackIs1=(BlackIs1.group(1).decode() if BlackIs1 else None),
                    rawlen=len(raw),
                    filters=[f.decode() for f in re.findall(rb"/Filter\s*/?(\w+)", head)]))
    images.append((n, W, H, raw))

# --- write raw streams out & build TIFF wrappers ---
def build_tiff(w, h, ccitt, blackis1=True):
    # photometric 0 = WhiteIsZero (min value is white). For CCITT G4 with BlackIs1 true,
    # decoded 0 = black -> use photometric 1 (BlackIsZero) when BlackIs1 true.
    photometric = 1 if blackis1 else 0
    entries = []
    def E(tag, typ, count, val):
        entries.append((tag, typ, count, val))
    # offsets computed after we know data offset
    header = b"II" + struct.pack("<H", 42)
    # IFD offset after header
    ifd_off = 8
    n_entries = 13
    data_off = ifd_off + 2 + n_entries * 12 + 4
    E(256, 3, 1, w)                 # ImageWidth SHORT
    E(257, 3, 1, h)                 # ImageLength
    E(258, 3, 1, 1)                 # BitsPerSample
    E(259, 3, 1, 4)                 # Compression = CCITT G4
    E(262, 3, 1, photometric)       # PhotometricInterpretation
    E(266, 3, 1, 1)                 # FillOrder = 1
    E(273, 4, 1, data_off)          # StripOffsets
    E(277, 3, 1, 1)                 # SamplesPerPixel
    E(278, 3, 1, h)                 # RowsPerStrip
    E(279, 4, 1, len(ccitt))        # StripByteCounts
    E(282, 5, 1, 0)                 # XResolution (dummy, patch)
    E(283, 5, 1, 0)                 # YResolution
    E(296, 3, 1, 2)                 # ResolutionUnit inch
    entries.sort(key=lambda x: x[0])
    ifd = struct.pack("<H", len(entries))
    for (tag, typ, count, val) in entries:
        ifd += struct.pack("<HHII", tag, typ, count, val)
    ifd += struct.pack("<I", 0)
    blob = header + struct.pack("<I", ifd_off) + ifd + ccitt
    return blob

out = []
for i, (n, W, H, raw) in enumerate(images):
    fn = os.path.join(base, "d1000009_img%d.tif" % i)
    open(fn, "wb").write(build_tiff(W, H, raw, True))
    out.append(dict(idx=i, obj=n, W=W, H=H, tif=fn, rawlen=len(raw)))

log.append(out)
open(os.path.join(base, "_figs.json"), "w", encoding="utf-8").write(json.dumps(out, indent=1, ensure_ascii=False))
open(os.path.join(base, "_probe2.json"), "w", encoding="utf-8").write(json.dumps(log, indent=1, ensure_ascii=False))
print("done", len(images))
