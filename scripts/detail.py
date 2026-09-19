# -*- coding: utf-8 -*-
"""抽取 Amazon 详情表 / BSR / 品牌 / 卖家 等字段（通用版，兼容新旧版式）。"""
import html
import re
import sys

src = sys.argv[1]
raw = open(src, encoding="utf-8", errors="ignore").read()


def clean(s):
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


log = []

# 详情表：抓取所有 detailBullets / prodDet 行
for pat in [
    r'<li[^>]*>\s*<span[^>]*class="a-text-bold"[^>]*>([\s\S]{0,80}?)</span>[\s\S]{0,200}?<span[^>]*>([\s\S]{0,200}?)</span>',
    r'<tr[^>]*>\s*<td[^>]*>([\s\S]{0,80}?)</td>\s*<td[^>]*>([\s\S]{0,200}?)</td>',
]:
    for m in re.finditer(pat, raw, re.I):
        k, v = clean(m.group(1)), clean(m.group(2))
        if k and v and len(k) < 60 and len(v) < 200:
            log.append("详情: %s = %s" % (k, v))

# 排名
for m in re.finditer(r'(?:Best Sellers Rank|畅销商品排名)([\s\S]{0,600}?)(?:</ul>|</div></div>)', raw, re.I):
    log.append("BSR: " + clean(m.group(1))[:500])
    break

# 卖家 / 店铺
for pat in [r'id="sellerProfileTriggerId"[^>]*>([\s\S]{0,120}?)</a>',
            r'id="bylineInfo"[^>]*>([\s\S]{0,200}?)</a>',
            r'Sold by[\s\S]{0,200}?<span[^>]*>([\s\S]{0,120}?)</span>']:
    m = re.search(pat, raw, re.I)
    log.append("主体: " + (clean(m.group(1)) if m else "<未找到>"))

# 价格
m = re.search(r'class="a-offscreen">(\$[\d.,]+)</span>', raw)
log.append("价格: " + (m.group(1) if m else "<未找到>"))

# 变体（颜色）
cols = re.findall(r'data-defaultasin="([A-Z0-9]{10})"', raw)
log.append("变体 ASIN: " + (", ".join(dict.fromkeys(cols)) if cols else "<未找到>"))

# 所有出现的 patent 相关词（含上下文短语）
pats = re.findall(r"[^<>]{0,120}(?:patent|Patented|Patent Pending)[^<>]{0,120}", raw, re.I)
log.append("patent 字样: " + (" | ".join(dict.fromkeys(clean(p) for p in pats))[:2000] or "无"))

# 上架日期关键词
for kw in ["Date First Available", "首度推出日", "Item model number", "型号"]:
    m = re.search(re.escape(kw) + r"[\s\S]{0,160}", raw, re.I)
    if m:
        log.append("★ " + clean(m.group(0))[:200])

open("_detail.txt", "w", encoding="utf-8").write("\n".join(dict.fromkeys(log)))
print("ok", len(log))
