// fetch_site.js — 带浏览器 UA 的通用站点抓取模板（Amazon 之外的信息源）
//
// 用途（排查流程里的三个固定靶点）:
//   1. 权利人/原版品牌官网 —— 读它的 "original / patented / Strictly Enforced" 话术与权利号；
//   2. 第三方【分销商页】—— ★ 品牌官网常对 WebFetch 返回 403，而分销商页（如 rilaks.ch、
//      mandypitcher.com、各地 SPAs/沙龙电商）通常可抓，且同样列产品名、设计号、EUIPO 号；
//      本案 UK 4 件注册外观号 + EU RCD 号就是从这类页面拿到的；
//   3. 案件通报页（AMZ123 / 大数跨境 / 网易 / 律所官网）—— 拿案号、法院、律所、涉案权利。
//
// 用法: 改 sites 后  node fetch_site.js
const fs = require('fs');
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';
const sites = [
  ['site_home.html', 'https://example.com/'],
];
(async () => {
  for (const [out, url] of sites) {
    for (let i = 1; i <= 3; i++) {
      try {
        const r = await fetch(url, { headers: { 'User-Agent': UA, 'Accept': 'text/html,*/*' }, redirect: 'follow' });
        const b = Buffer.from(await r.arrayBuffer());
        fs.writeFileSync(out, b);
        console.log(out, r.status, b.length);
        if (b.length < 2000 && r.status !== 200) console.log('  ^ 疑似拦截页，换分销商页/镜像重试');
        break;
      } catch (e) { console.log(out, 'ERR', e.message, 'try', i); }
    }
  }
})();
// 抓到 HTML 后用 h2t.py 抽文本再 grep 权利号:
//   python h2t.py site_home.html site_home.txt
