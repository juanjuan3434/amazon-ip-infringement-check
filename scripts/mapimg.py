import re, io, html

s = io.open('amz.html', encoding='utf-8', errors='ignore').read()

# In Amazon search-result/carousel JSON, each item has asin + image url close together.
out = []
# pattern: "asin":"B0...","...url":"...images/I/xxx..."
for m in re.finditer(r'"(B0[A-Z0-9]{8})"(.{0,1500}?)(https://m\.media-amazon\.com/images/I/([A-Za-z0-9\-_\.\+]+)\._[^"]{0,60}?\.jpg)', s, re.S):
    out.append((m.group(1), m.group(4)))

# also reverse order (image then asin)
for m in re.finditer(r'(https://m\.media-amazon\.com/images/I/([A-Za-z0-9\-_\.\+]+)\._[^"]{0,60}?\.jpg)(.{0,1500}?)"(B0[A-Z0-9]{8})"', s, re.S):
    out.append((m.group(4), m.group(2)))

seen = set()
lines = []
for a, img in out:
    k = (a, img)
    if k in seen:
        continue
    seen.add(k)
    lines.append('%s -> %s' % (a, img))

io.open('_map.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('WROTE', len(lines))
