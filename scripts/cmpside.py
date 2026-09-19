import os
from PIL import Image, ImageDraw

# 工作目录：优先环境变量 IPCHECK_DIR，否则用当前工作目录（在案例目录里直接跑即可）
os.chdir(os.environ.get("IPCHECK_DIR") or os.getcwd())

items = []

# 1. our product bottle crop (from img1.jpg)
im = Image.open('img1.jpg').convert('RGB')
W, H = im.size
crop = im.crop((int(W * 0.15), int(H * 0.02), int(W * 0.62), int(H * 1.0)))
items.append(('OURS  B0XXXXXX04', crop))

# 2. D675100 sheet
for p, lab in [('figsD675100/D675100_p03.png', 'D675100 (capsule shaped container)'),
               ('figsD675100/D675100_p04.png', 'D675100 p4')]:
    if os.path.exists(p):
        items.append((lab, Image.open(p).convert('RGB')))

# 3. D813673 sheet 3 (FIG3/4) - the capsule spray container
for p, lab in [('figsD813673/D813673_p04.png', 'D813673 (spray container, capsule)'),
               ('figsD813673/D813673_p03.png', 'D813673 FIG.2 w/ handle')]:
    if os.path.exists(p):
        items.append((lab, Image.open(p).convert('RGB')))

cellw, cellh = 380, 560
sheet = Image.new('RGB', (cellw * len(items), cellh + 26), 'white')
d = ImageDraw.Draw(sheet)
for k, (lab, im) in enumerate(items):
    im = im.copy()
    im.thumbnail((cellw - 16, cellh - 16))
    x = k * cellw + (cellw - im.width) // 2
    y = 26 + (cellh - im.height) // 2
    sheet.paste(im, (x, y))
    d.text((k * cellw + 6, 8), lab, fill='black')
sheet.save('compare_capsule.png')
print('saved', sheet.size, [i[0] for i in items])
