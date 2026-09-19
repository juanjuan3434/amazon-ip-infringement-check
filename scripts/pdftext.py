# -*- coding: utf-8 -*-
"""抽取任意专利 PDF 的文本 + 单独抽出权利要求（EP / WIPO / 公开申请 均适用）。

用法:
    python pdftext.py EP4342332B1.pdf _ep.txt [_ep_claims.txt]

依赖:
    pypdf —— 本机通常未预装，缺则先跑:  python -m pip install pypdf

★ 适用边界（务必分清两条流水线）:
    - EP / WIPO / 部分公开申请 = 【文字流 PDF】 -> 用本脚本抽文本、抽权项
    - USPTO 授权文本的【附图】 = CCITT Group 4 传真位图 -> 用 decode.py / sheets.py 解码成 PNG 目视
    两者不可互换：EP 的 PDF 里没有传真位图，USPTO 的附图页里也没有可抽的文字权项。
"""
import io, re, sys

src = sys.argv[1] if len(sys.argv) > 1 else 'EP4342332B1.pdf'
out = sys.argv[2] if len(sys.argv) > 2 else '_pdf.txt'
clm = sys.argv[3] if len(sys.argv) > 3 else None

try:
    from pypdf import PdfReader
except ImportError:
    print('!! 缺少 pypdf，请先执行: python -m pip install pypdf')
    raise SystemExit(2)

r = PdfReader(src)
n = len(r.pages)
txt = []
for i, p in enumerate(r.pages):
    try:
        txt.append('==== PAGE %d ====\n' % (i + 1) + (p.extract_text() or ''))
    except Exception as e:
        txt.append('==== PAGE %d ERR %s ====' % (i + 1, e))
all_ = '\n'.join(txt)
io.open(out, 'w', encoding='utf-8').write(all_)
print('pages', n, 'chars', len(all_), '->', out)

# 扉页关键字段抽查（指定国清单 / 期限 / 权利人），命中就打印，省一次 Read
for pat, label in [
    (r'(Designated Contracting States:[\s\S]{0,400})', '指定国'),
    (r'(Term:\s*\d+\s*Years)', '期限'),
    (r'(71\)[\s\S]{0,120})', '申请人/权利人'),
    (r'(72\)[\s\S]{0,120})', '发明人'),
]:
    m = re.search(pat, all_, re.I)
    if m:
        print('--', label, ':', ' '.join(m.group(1).split())[:220])

if clm:
    m = re.search(r'(Claims?\s*\n)([\s\S]{0,20000})', all_, re.I)
    if m:
        io.open(clm, 'w', encoding='utf-8').write(m.group(0))
        print('claims', len(m.group(0)), '->', clm)
    else:
        print('claims marker not found (再试搜 "We claim" / "What is claimed" / "Patentanspr"）')
