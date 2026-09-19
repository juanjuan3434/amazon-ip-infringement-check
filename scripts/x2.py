import re, sys, html, io

p = sys.argv[1] if len(sys.argv) > 1 else 'amz.html'
s = io.open(p, encoding='utf-8', errors='ignore').read()

out = []

def grab(label, pat, flags=re.S):
    m = re.search(pat, s, flags)
    if m:
        v = re.sub(r'<[^>]+>', ' ', m.group(1))
        v = html.unescape(v)
        v = re.sub(r'\s+', ' ', v).strip()
        out.append('%s = %s' % (label, v[:400]))
    else:
        out.append('%s = <未找到>' % label)

def grab_all(label, pat, flags=re.S, limit=12):
    ms = re.findall(pat, s, flags)
    if ms:
        for i, m in enumerate(ms[:limit]):
            v = re.sub(r'<[^>]+>', ' ', m)
            v = html.unescape(v)
            v = re.sub(r'\s+', ' ', v).strip()
            if v:
                out.append('%s[%d] = %s' % (label, i, v[:300]))
    else:
        out.append('%s = <未找到>' % label)

grab('TITLE', r'id="productTitle"[^>]*>(.*?)</span>')
grab_all('BULLET', r'<span class="a-list-item">\s*(.*?)\s*</span>')

for key in ['Date First Available', 'Item model number', 'Best Sellers Rank',
            'ASIN', 'Manufacturer', 'Item Weight', 'Package Dimensions',
            'Product Dimensions', 'Unit Count', 'Item Volume', 'UPC', 'Is Discontinued']:
    m = re.search(re.escape(key) + r'[^<]*</span>\s*<span[^>]*>\s*(?:<span[^>]*>)?([^<]{1,200})', s, re.S)
    if m:
        out.append('FIELD %s = %s' % (key, html.unescape(m.group(1)).strip()))
    else:
        m2 = re.search(r'>\s*' + re.escape(key) + r'\s*:?\s*<[^>]*>\s*([^<]{1,200})', s, re.S)
        out.append('FIELD %s = %s' % (key, html.unescape(m2.group(1)).strip() if m2 else '<未找到>'))

grab('STORE', r'<a[^>]*id="bylineInfo"[^>]*>(.*?)</a>')
grab('RATING', r'id="acrCustomerReviewText"[^>]*>(.*?)</span>')
grab('STARS', r'([\d.]+) out of 5 stars')

# patent / design patent mentions
for kw in ['patent', 'Patent', 'PATENT', 'design patent', 'Patent Pending', '专利']:
    n = len(re.findall(re.escape(kw), s))
    out.append('KW_COUNT %s = %d' % (kw, n))

# variants
grab_all('VARIANT', r'"asin"\s*:\s*"(B0[A-Z0-9]{8})"', limit=20)

# images
grab_all('IMGKEY', r'"hiRes":"(https://m\.media-amazon\.com/images/[^"]+)"', limit=10)
grab_all('MAINIMG', r'"large":"(https://m\.media-amazon\.com/images/I/[^"]+)"', limit=6)

io.open('_x2.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('WROTE', len(out))
