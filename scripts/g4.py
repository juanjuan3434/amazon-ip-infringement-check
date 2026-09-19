# -*- coding: utf-8 -*-
"""Minimal ITU-T T.6 (CCITT Group 4) decoder -> 8-bit grayscale PNG (stdlib only)."""
import struct, zlib, os, json

# ---------- code tables ----------
WHITE_TERM = {
 0:"00110101",1:"000111",2:"0111",3:"1000",4:"1011",5:"1100",6:"1110",7:"1111",
 8:"10011",9:"10100",10:"00111",11:"01000",12:"001000",13:"000011",14:"110100",
 15:"110101",16:"101010",17:"101011",18:"0100111",19:"0001100",20:"0001000",
 21:"0010111",22:"0000011",23:"0000100",24:"0101000",25:"0101011",26:"0010011",
 27:"0100100",28:"0011000",29:"00000010",30:"00000011",31:"00011010",32:"00011011",
 33:"00010010",34:"00010011",35:"00010100",36:"00010101",37:"00010110",38:"00010111",
 39:"00101000",40:"00101001",41:"00101010",42:"00101011",43:"00101100",44:"00101101",
 45:"00000100",46:"00000101",47:"00001010",48:"00001011",49:"01010010",50:"01010011",
 51:"01010100",52:"01010101",53:"00100100",54:"00100101",55:"01011000",56:"01011001",
 57:"01011010",58:"01011011",59:"01001010",60:"01001011",61:"00110010",62:"00110011",
 63:"00110100",
 64:"11011",128:"10010",192:"010111",256:"0110111",320:"00110110",384:"00110111",
 448:"01100100",512:"01100101",576:"01101000",640:"01100111",704:"011001100",
 768:"011001101",832:"011010010",896:"011010011",960:"011010100",1024:"011010101",
 1088:"011010110",1152:"011010111",1216:"011011000",1280:"011011001",1344:"011011010",
 1408:"011011011",1472:"010011000",1536:"010011001",1600:"010011010",1664:"011000",
 1728:"010011011"}
BLACK_TERM = {
 0:"0000110111",1:"010",2:"11",3:"10",4:"011",5:"0011",6:"0010",7:"00011",
 8:"000101",9:"000100",10:"0000100",11:"0000101",12:"0000111",13:"00000100",
 14:"00000111",15:"000011000",16:"0000010111",17:"0000011000",18:"0000001000",
 19:"00001100111",20:"00001101000",21:"00001101100",22:"00000110111",23:"00000101000",
 24:"00000010111",25:"00000011000",26:"000011001010",27:"000011001011",28:"000011001100",
 29:"000011001101",30:"000001101000",31:"000001101001",32:"000001101010",33:"000001101011",
 34:"000011010010",35:"000011010011",36:"000011010100",37:"000011010101",38:"000011010110",
 39:"000011010111",40:"000001101100",41:"000001101101",42:"000011011010",43:"000011011011",
 44:"000001010100",45:"000001010101",46:"000001010110",47:"000001010111",48:"000001100100",
 49:"000001100101",50:"000001010010",51:"000001010011",52:"000000100100",53:"000000110111",
 54:"000000111000",55:"000000100111",56:"000000101000",57:"000001011000",58:"000001011001",
 59:"000000101011",60:"000000101100",61:"000001011010",62:"000001100110",63:"000001100111",
 64:"0000001111",128:"000011001000",192:"000011001001",256:"000001011011",
 320:"000000110011",384:"000000110100",448:"000000110101",512:"0000001101100",
 576:"0000001101101",640:"0000001001010",704:"0000001001011",768:"0000001001100",
 832:"0000001001101",896:"0000001110010",960:"0000001110011",1024:"0000001110100",
 1088:"0000001110101",1152:"0000001110110",1216:"0000001110111",1280:"0000001010010",
 1344:"0000001010011",1408:"0000001010100",1472:"0000001010101",1536:"0000001011010",
 1600:"0000001011011",1664:"0000001100100",1728:"0000001100101"}
EXT_MAKEUP = {
 1792:"00000001000",1856:"00000001100",1920:"00000001101",1984:"000000010010",
 2048:"000000010011",2112:"000000010100",2176:"000000010101",2240:"000000010110",
 2304:"000000010111",2368:"000000011100",2432:"000000011101",2496:"000000011110",
 2560:"000000011111"}

W = {v: k for k, v in WHITE_TERM.items()}
W.update({v: k for k, v in EXT_MAKEUP.items()})
B = {v: k for k, v in BLACK_TERM.items()}
B.update({v: k for k, v in EXT_MAKEUP.items()})

MODE = {"1": ("V", 0), "011": ("V", 1), "000011": ("V", 2), "0000011": ("V", 3),
        "010": ("V", -1), "000010": ("V", -2), "0000010": ("V", -3),
        "001": ("H", 0), "0001": ("P", 0), "0000001": ("X", 0),
        "000000000001": ("EOL", 0)}


class BitReader:
    def __init__(self, data):
        self.d = data
        self.p = 0        # byte index
        self.b = 0        # bit index within byte (0 = MSB)

    def bit(self):
        if self.p >= len(self.d):
            return None
        byte = self.d[self.p]
        v = (byte >> (7 - self.b)) & 1
        self.b += 1
        if self.b == 8:
            self.b = 0
            self.p += 1
        return v

    def peek_str(self, n):
        save = (self.p, self.b)
        s = ""
        for _ in range(n):
            v = self.bit()
            if v is None:
                break
            s += str(v)
        self.p, self.b = save
        return s

    def consume(self, n):
        for _ in range(n):
            self.bit()


def read_run(br, table):
    """Decode one 1D run length (1 or 2 code words)."""
    total = 0
    for _ in range(12):          # makeup chain safety
        code = ""
        val = None
        for _ in range(14):
            v = br.bit()
            if v is None:
                return total
            code += str(v)
            if code in table:
                val = table[code]
                break
        if val is None:
            return total
        total += val
        if val < 64:
            return total
    return total


def changes_of(row, width):
    """Boundary indices of the colour changes on a line.

    The a0/a1/b1/b2 convention used by T.6 is 'last pixel index of the preceding
    run' (== first pixel index of the following run minus 1).  A boundary at c
    means pixels <= c have the old colour and pixels >= c+1 the new one.
    """
    out = []
    prev = 0
    for i in range(width):
        v = row[i]
        if v != prev:
            out.append(i - 1)
            prev = v
    return out


def decode_g4(data, width, height, max_rows=None):
    br = BitReader(data)
    rows = []
    ref = None  # virtual all-white line
    ref_changes = []
    for y in range(height):
        row = bytearray(width)          # 0 white, 1 black
        pos = 0
        cur = 0
        a0 = -1
        guard = 0
        while pos < width and guard < 200000:
            guard += 1
            # find b1 : first change on ref line > a0 with color != cur
            b1 = None
            b2 = None
            for j, cp in enumerate(ref_changes):
                if cp > a0:
                    col = 1 if (j % 2 == 0) else 0
                    if col != cur:
                        b1 = cp
                        b2 = ref_changes[j + 1] if j + 1 < len(ref_changes) else width
                        break
            if b1 is None:
                b1 = width
                b2 = width
            # read mode code
            code = ""
            mode = None
            for _ in range(13):
                v = br.bit()
                if v is None:
                    mode = ("EOF", 0)
                    break
                code += str(v)
                if code in MODE:
                    mode = MODE[code]
                    break
            if mode is None:
                mode = ("EOF", 0)
            kind, off = mode
            if kind == "EOF":
                # pad remaining rows white
                for yy in range(y, height):
                    rows.append(bytearray(width))
                return rows
            if kind == "EOL":
                continue
            if kind == "P":
                # a0 <-- b2 ; run of colour `cur` covers pos..b2 (b2 inclusive)
                end = min(b2 + 1, width)
                if end > pos:
                    if cur:
                        row[pos:end] = b"\x01" * (end - pos)
                    pos = end
                a0 = pos - 1
                continue
            if kind == "H":
                r1 = read_run(br, W if cur == 0 else B)
                e1 = min(pos + r1, width)
                if cur:
                    row[pos:e1] = b"\x01" * (e1 - pos)
                pos = e1
                cur ^= 1
                r2 = read_run(br, W if cur == 0 else B)
                e2 = min(pos + r2, width)
                if cur:
                    row[pos:e2] = b"\x01" * (e2 - pos)
                pos = e2
                cur ^= 1
                a0 = pos - 1
                continue
            if kind == "X":
                continue
            if kind == "V":
                a1 = b1 + off
                if a1 < pos:
                    a1 = pos
                e = min(a1 + 1, width)          # run covers pos..a1 inclusive
                if cur:
                    row[pos:e] = b"\x01" * (e - pos)
                pos = e
                cur ^= 1
                a0 = pos - 1
                continue
        rows.append(row)
        ref_changes = changes_of(row, width)
    return rows


def write_png_gray(path, rows, width, height, scale=1):
    """rows: list of bytearray with 0/255 values already; write 8-bit grayscale PNG"""
    raw = bytearray()
    for y in range(height):
        raw.append(0)                      # filter: none
        raw.extend(bytes(rows[y]))
    comp = zlib.compress(bytes(raw), 6)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    open(path, "wb").write(png)


def downsample(rows, width, height, f):
    nw = width // f
    nh = height // f
    out = []
    for y in range(nh):
        line = bytearray(nw)
        for x in range(nw):
            x0 = x * f
            acc = 0
            y0 = y * f
            for dy in range(f):
                r = rows[y0 + dy]
                for dx in range(f):
                    if r[x0 + dx]:
                        acc = 1
                        break
                if acc:
                    break
            line[x] = 0 if acc else 255
        out.append(line)
    return out, nw, nh


if __name__ == "__main__":
    base = r"C:\Users\34347\WorkBuddy\2026-08-21-09-54-29\ip_check\bandana_figs"
    meta = json.load(open(os.path.join(base, "_figs.json"), encoding="utf-8"))
    report = []
    for item in meta:
        if not isinstance(item, dict) or "W" not in item:
            report.append("skip %r" % (item,))
            continue
        w, h = item["W"], item["H"]
        if not w or not h:
            report.append("skip %s (no size)" % item)
            continue
        raw = open(item["tif"], "rb").read()
        off = struct.unpack("<I", raw[4:8])[0]
        # read StripOffsets from our TIFF (tag 273)
        ifd_off = struct.unpack("<I", raw[4:8])[0]
        n = struct.unpack("<H", raw[ifd_off:ifd_off+2])[0]
        strip_off = None
        for k in range(n):
            e = ifd_off + 2 + k * 12
            tag, typ, cnt, val = struct.unpack("<HHII", raw[e:e+12])
            if tag == 273:
                strip_off = val
        ccitt = raw[strip_off:]
        try:
            rows = decode_g4(ccitt, w, h)
            rows = [bytearray(255 if v else 0 for v in r) for r in rows]
            # report black ratio to detect garbage
            black = sum(1 for r in rows for v in r if v)
            ratio = black / float(w * h)
            f = 1
            while (w // f) > 1400:
                f += 1
            ds, nw, nh = downsample(rows, w, h, f)
            out = os.path.join(base, "D1000009_fig%d.png" % item["idx"])
            write_png_gray(out, ds, nw, nh)
            report.append("img%d: %dx%d blackRatio=%.3f scale=1/%d -> %s (%dx%d) %d bytes"
                          % (item["idx"], w, h, ratio, f, out, nw, nh, os.path.getsize(out)))
        except Exception as ex:
            report.append("img%d: FAIL %r" % (item["idx"], ex))
    open(os.path.join(base, "_decode.txt"), "w", encoding="utf-8").write("\n".join(report))
    print("done")
