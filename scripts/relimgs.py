import io, os, re, urllib.request
from PIL import Image, ImageDraw

urls = [
 'https://m.media-amazon.com/images/I/41ydBB+ri9L._AC_QL10_SX980_SY55_FMwebp_.jpg',
 'https://m.media-amazon.com/images/I/61+uVqOvbnL._AC_QL10_SX980_SY55_FMwebp_.jpg',
 'https://m.media-amazon.com/images/I/71Dmj7sBdjL._AC_QL10_SX980_SY55_FMwebp_.jpg',
 'https://m.media-amazon.com/images/I/71BkXEwLqTL._AC_UF480,480_SR480,480_.jpg',
 'https://m.media-amazon.com/images/I/61NCzK7sWvL._AC_UF480,480_SR480,480_.jpg',
 'https://m.media-amazon.com/images/I/71TwU4JCjeL._AC_UF480,480_SR480,480_.jpg',
 'https://m.media-amazon.com/images/I/61Ap6IgJJdL._AC_UF480,480_SR480,480_.jpg',
 'https://m.media-amazon.com/images/I/314kYyBCm0L._AC_UF480,480_SR480,480_.jpg',
 'https://m.media-amazon.com/images/I/71PY9UHNPLL._AC_UF480,480_SR480,480_.jpg',
 'https://m.media-amazon.com/images/I/71cyDyIXAJL._AC_UF480,480_SR480,480_.jpg',
 'https://m.media-amazon.com/images/I/51nIF+D-RML._AC_QL_SX300_SY250_FMwebp_.jpg',
]

hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'image/*,*/*'}
ims = []
for i, u in enumerate(urls):
    fn = 'rel%02d.jpg' % i
    if not (os.path.exists(fn) and os.path.getsize(fn) > 3000):
        try:
            r = urllib.request.Request(u, headers=hdr)
            b = urllib.request.urlopen(r, timeout=40).read()
            io.open(fn, 'wb').write(b)
        except Exception as e:
            print(i, 'ERR', e)
            continue
    try:
        im = Image.open(fn).convert('RGB')
        im.thumbnail((300, 300))
        ims.append((i, im))
    except Exception as e:
        print(i, 'OPEN ERR', e)

cell = 300
cols = 4
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cell, rows * (cell + 22)), 'white')
d = ImageDraw.Draw(sheet)
for k, (i, im) in enumerate(ims):
    cx = (k % cols) * cell
    cy = (k // cols) * (cell + 22)
    sheet.paste(im, (cx + (cell - im.width) // 2, cy + 22 + (cell - im.height) // 2))
    d.text((cx + 6, cy + 6), 'rel%02d' % i, fill='black')
sheet.save('rel_montage.png')
print('saved', sheet.size, len(ims))
