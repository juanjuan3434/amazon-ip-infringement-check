# -*- coding: utf-8 -*-
"""把 FPO 单行长文本按句子分段，输出可读 txt，并抽出 claims 段。"""
import re, sys, os

src = sys.argv[1]
dst = sys.argv[2]
t = open(src, encoding='utf-8', errors='ignore').read()
t = re.sub(r'\s+', ' ', t)
# 在每个编号权利要求前断行
t = re.sub(r'(?<=[.;])\s+(?=\d{1,2}\.\s+[A-Z])', '\n\n', t)
t = re.sub(r'(?<=[.;])\s+(?=(?:What is claimed|We claim|Claims?|ABSTRACT|DESCRIPTION|BACKGROUND|SUMMARY|BRIEF DESCRIPTION|DRAWINGS|CROSS-REFERENCE|TECHNICAL FIELD|FIELD OF))', '\n\n', t)
t = t.replace('; ', ';\n  ')
open(dst, 'w', encoding='utf-8').write(t)
print('written', dst, len(t))
