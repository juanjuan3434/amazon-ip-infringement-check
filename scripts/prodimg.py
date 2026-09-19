import io, os, urllib.request
from PIL import Image, ImageDraw

keys = [
 ('MAIN0','51CDblE638L'), ('MAIN1','51vO01BuIBL'), ('MAIN2','51282tA19pL'),
 ('MAIN3','51vYdK3TZfL'), ('MAIN4','51zp0wI2UbL'), ('MAIN5','51X1DP10G5L'),
 ('IMG0','81g41G1LUvL'), ('IMG1','81BroEZ+y3L'), ('IMG2','81+Zr4yocJL'),
 ('IMG3','81yZ25hRH-L'), ('IMG4','817hBiOqO5L'), ('IMG5','81jmJEOY8OL'),
 ('IMG6','81gI09tyjEL'),
]
hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'image/*,*/*'}
ims = []
for i, (tag, k) in enumerate(keys):
    fn = 'pimg%02d.jpg' % i
    if not (os.path.exists(fn) and os.path.getsize(fn) > 3000):
        u = 'https://m.media-amazon.com/images/I/%s._AC_SL1200_.jpg' % k
        try:
            r = urllib.request.Request(u, headers=hdr)
            b = urllib.request.urlopen(r, timeout=40).read()
            io.open(fn, 'wb').write(b)
        except Exception as e:
            print(i, k, 'ERR', e)
            continue
    try:
        im = Image.open(fn).convert('RGB')
        im.thumbnail((420, 420))
        ims.append((i, tag, im))
    except Exception as e:
        print(i, k, 'OPEN ERR', e)

cell = 430
cols = 3
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cell, rows * (cell + 24)), 'white')
d = ImageDraw.Draw(sheet)
for n, (i, tag, im) in enumerate(ims):
    cx = (n % cols) * cell
    cy = (n // cols) * (cell + 24)
    sheet.paste(im, (cx + (cell - im.width) // 2, cy + 24 + (cell - im.height) // 2))
    d.text((cx + 6, cy + 6), '%s' % tag, fill='black')
sheet.save('prod_montage.png')
print('saved', sheet.size, len(ims))
