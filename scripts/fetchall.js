// fetchall.js — 带重试的批量抓取（部分站点会间歇性 reset）
// 用法: node fetchall.js urls.txt [delayMs]
const fs = require('fs');
const path = require('path');

const listFile = process.argv[2];
const delay = parseInt(process.argv[3] || '1500', 10);
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';

const lines = fs.readFileSync(listFile, 'utf8').split(/\r?\n/).map(s => s.trim()).filter(s => s && !s.startsWith('#'));
const log = [];

const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  for (const line of lines) {
    const [out, url] = line.split('|').map(s => s.trim());
    if (!out || !url) { log.push('SKIP bad line: ' + line); continue; }
    let ok = false;
    for (let i = 1; i <= 3 && !ok; i++) {
      try {
        const r = await fetch(url, {
          headers: { 'User-Agent': UA, 'Accept': 'text/html,application/pdf,*/*', 'Accept-Language': 'en-US,en;q=0.9' },
          redirect: 'follow',
        });
        const buf = Buffer.from(await r.arrayBuffer());
        fs.writeFileSync(path.resolve(out), buf);
        log.push(`${out} OK status=${r.status} ct=${r.headers.get('content-type')} bytes=${buf.length} try${i}`);
        ok = true;
      } catch (e) {
        log.push(`${out} try${i} ERR ${e.message}`);
        await sleep(2500);
      }
    }
    await sleep(delay);
  }
  fs.writeFileSync('_fetchlog.txt', log.join('\n'));
  console.log(log.join('\n'));
})();
