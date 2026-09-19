import os, subprocess
from PIL import Image, ImageDraw

P = r'C:\Users\34347\.workbuddy\binaries\python\versions\3.13.12\python.exe'
D = r'C:\Users\34347\WorkBuddy\2026-08-21-09-54-29\ip_check\spray'
os.chdir(D)

pdfs = ['D1006632', 'D1012718', 'D1114621', 'D1090262', 'D1023770',
        'D899943', 'D904895', 'D660704', 'D660705', 'D658998']

have = []
for n in pdfs:
    fn = n + '.pdf'
    outdir = 'figs' + n
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    for idx in (0, 4):
        try:
            subprocess.run([P, 'decode.py', fn, outdir, str(idx), '2'],
                           capture_output=True, timeout=115)
        except Exception as e:
            print(n, idx, 'ERR', e)
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

cell = 320
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
sheet.save('pat_montage2.png')
print('DONE', sheet.size, len(have))
