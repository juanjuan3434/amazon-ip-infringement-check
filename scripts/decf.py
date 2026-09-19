import os, subprocess, sys
from PIL import Image, ImageDraw

P = sys.executable                      # 用当前解释器，换机器/换 Python 版本都不会失效
HERE = os.path.dirname(os.path.abspath(__file__))
# 工作目录：优先环境变量 IPCHECK_DIR，否则用当前工作目录（在案例目录里直接跑即可）
os.chdir(os.environ.get("IPCHECK_DIR") or os.getcwd())

pdfs = ['D1108260', 'D1014284', 'D1002381', 'D888570', 'D887842', 'D813673',
        'D700521', 'D709381', 'D1084872', 'D1145154', 'D1125697', 'D1114352',
        'D1093159', 'D1088892', 'D1021262']

have = []
for n in pdfs:
    fn = n + '.pdf'
    outdir = 'figs' + n
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    # decode cover (idx0) and first sheet (idx4)
    for idx in (0, 4):
        target = os.path.join(outdir, '%s_p%02d.png' % (n, idx))
        if os.path.exists(target):
            continue
        try:
            subprocess.run([P, os.path.join(HERE, 'decode.py'), fn, outdir, str(idx), '2'],
                           capture_output=True, timeout=110)
        except Exception as e:
            print(n, idx, 'ERR', e)
    # find produced png
    cands = sorted([f for f in os.listdir(outdir) if f.endswith('.png')])
    pick = None
    for c in cands:
        if '_p04' in c:
            pick = os.path.join(outdir, c)
    if pick is None and cands:
        pick = os.path.join(outdir, cands[0])
    if pick and os.path.exists(pick):
        have.append((n, pick))
    else:
        print(n, 'NO PNG', cands)

cell = 300
cols = 5
rows = (len(have) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cell, rows * (cell + 20)), 'white')
d = ImageDraw.Draw(sheet)
for k, (n, p) in enumerate(have):
    try:
        im = Image.open(p).convert('RGB')
    except Exception as e:
        print(n, 'OPENERR', e); continue
    im.thumbnail((cell, cell))
    cx = (k % cols) * cell
    cy = (k // cols) * (cell + 20)
    sheet.paste(im, (cx + (cell - im.width) // 2, cy + 20 + (cell - im.height) // 2))
    d.text((cx + 5, cy + 4), n, fill='black')
sheet.save('pat_montage.png')
print('DONE', sheet.size, len(have))
