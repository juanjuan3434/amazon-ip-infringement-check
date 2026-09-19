// dl_ep.js — 欧洲专利局（EPO）公开出版服务 PDF 下载模板
//
// URL 规律:
//   https://data.epo.org/publication-server/rest/v1.2/publication-dates/{公告日YYYY-MM-DD}/patents/EP{号}{国别码}{B1|A1}/document.pdf
//   例:                                    .../publication-dates/2025-12-24/patents/EP4342332NWB1/document.pdf
//
// ⚠️ 两个坑:
//   1. EP 号后面必须带【国别码】（常见 NW = 无国别指定/EP 通用），写成 EP4342332B1 会 404；
//   2. 路径里的日期是【授权/公开公告日】，不是申请日（授权日读扉页 Bulletin 或 EPO Register）。
//
// 用法: 改 list 后  node dl_ep.js      （Node 22 managed runtime 即可，无需装包）
const fs = require('fs');
const list = [
  ['EP4342332B1.pdf', 'https://data.epo.org/publication-server/rest/v1.2/publication-dates/2025-12-24/patents/EP4342332NWB1/document.pdf'],
];
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  for (const [f, url] of list) {
    if (fs.existsSync(f) && fs.statSync(f).size > 20000) { console.log(f, 'cached'); continue; }
    for (let i = 1; i <= 4; i++) {
      try {
        const ctl = new AbortController();
        const t = setTimeout(() => ctl.abort(), 110000);
        const r = await fetch(url, {
          headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'application/pdf,*/*' },
          signal: ctl.signal,
        });
        clearTimeout(t);
        if (r.ok) { const b = Buffer.from(await r.arrayBuffer()); fs.writeFileSync(f, b); console.log(f, 'OK', r.status, b.length); break; }
        console.log(f, 'HTTP', r.status, 'try', i);
      } catch (e) { console.log(f, 'ERR', e.name, e.message, 'try', i); }
      await sleep(3000);
    }
  }
})();
// 下完接着跑:  python pdftext.py EP4342332B1.pdf _ep.txt _ep_claims.txt
