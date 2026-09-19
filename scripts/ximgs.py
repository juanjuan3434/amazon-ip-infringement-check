import re, io, json, html

s = io.open('amz.html', encoding='utf-8', errors='ignore').read()

# all product image urls (large) with nearby ASIN and title
out = []
# find pairs: image url ... nearby asin
for m in re.finditer(r'https://m\.media-amazon\.com/images/I/([A-Za-z0-9\-_\.\+]+)\._AC_[^"\']*?\.jpg', s):
    out.append(m.group(0))
uniq = []
seen = set()
for u in out:
    k = re.sub(r'\._[^/]*$', '', u)
    if k not in seen:
        seen.add(k)
        uniq.append(u)

# ASINs with nearby title
asins = {}
for m in re.finditer(r'/dp/(B0[A-Z0-9]{8})', s):
    a = m.group(1)
    asins[a] = asins.get(a, 0) + 1

# asin -> title pairs
pairs = []
for m in re.finditer(r'"asin"\s*:\s*"(B0[A-Z0-9]{8})"[^{}]{0,900}?"(?:title|productTitle)"\s*:\s*"([^"]{5,200})"', s):
    pairs.append((m.group(1), html.unescape(m.group(2))))

lines = []
lines.append('IMG_COUNT=%d  UNIQ=%d' % (len(out), len(uniq)))
lines.append('--- UNIQ IMAGES (%d) ---' % len(uniq))
lines.extend(uniq)
lines.append('--- ASIN counts (top 40) ---')
for a, c in sorted(asins.items(), key=lambda x: -x[1])[:40]:
    lines.append('%s x%d' % (a, c))
lines.append('--- ASIN/TITLE pairs (%d) ---' % len(pairs))
for a, t in pairs[:60]:
    lines.append('%s | %s' % (a, t[:150]))

io.open('_imgs.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('WROTE', len(lines))
