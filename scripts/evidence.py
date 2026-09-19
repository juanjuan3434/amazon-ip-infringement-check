import io
from PIL import Image, ImageDraw

def load(fn, w):
    im = Image.open(fn).convert('RGB')
    r = w / im.width
    return im.resize((w, int(im.height * r)))

W = 420
items = [
    ('本产品主图(Amazon UK B0HD6MFQ7X)', 'pimg00.jpg'),
    ('包装特写 POPCORN PENS / 6 Pack', 'pk_zoom.png'),
    ('效果图（吹风机发泡成 3D）', 'art_zoom.png'),
    ('USD1049230S FIG.3（钻石画点钻笔，不命中）', 'D1049230_p04.png'),
]
ims = []
for tag, fn in items:
    try:
        ims.append((tag, load(fn, W)))
    except Exception as e:
        print(tag, 'ERR', e)

h = max(im.height for _, im in ims) + 30
sheet = Image.new('RGB', (W * 2, h * 2), 'white')
d = ImageDraw.Draw(sheet)
for k, (tag, im) in enumerate(ims):
    cx = (k % 2) * W
    cy = (k // 2) * h
    d.text((cx + 6, cy + 6), tag, fill='black')
    sheet.paste(im, (cx + (W - im.width) // 2, cy + 26))
sheet.save('pen_evidence.png')
print('saved', sheet.size)
