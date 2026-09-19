import io, os, urllib.request
from PIL import Image, ImageDraw

# related-items carousel thumbnails (upgrade to larger size)
imgkeys = [
 '51HuCxxNa2L', '51V1ObebPrL', '510idhveBhL', '61T6dOWN4CL',
 '51QJV37UQeL', '31E5BcswH8L', '41U6O2GAu7L', '51Ft4aB8ZCL',
 '51-POM5saCL', '51xS1cgVR3L', '71WM+ZlHDlL', '81mJ1PvKpJL',
]
hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'image/*,*/*'}
ims = []
for i, k in enumerate(imgkeys):
    fn = 'urel%02d.jpg' % i
    if not (os.path.exists(fn) and os.path.getsize(fn) > 3000):
        u = 'https://m.media-amazon.com/images/I/%s._AC_SL400_.jpg' % k
        try:
            r = urllib.request.Request(u, headers=hdr)
            b = urllib.request.urlopen(r, timeout=40).read()
            io.open(fn, 'wb').write(b)
        except Exception as e:
            print(i, k, 'ERR', e)
            continue
    try:
        im = Image.open(fn).convert('RGB')
        im.thumbnail((320, 320))
        ims.append((i, k, im))
    except Exception as e:
        print(i, k, 'OPEN ERR', e)

cell = 330
cols = 4
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cell, rows * (cell + 24)), 'white')
d = ImageDraw.Draw(sheet)
for n, (i, k, im) in enumerate(ims):
    cx = (n % cols) * cell
    cy = (n // cols) * (cell + 24)
    sheet.paste(im, (cx + (cell - im.width) // 2, cy + 24 + (cell - im.height) // 2))
    d.text((cx + 6, cy + 6), 'urel%02d %s' % (i, k), fill='black')
sheet.save('uk_rel_montage.png')
print('saved', sheet.size, len(ims))
