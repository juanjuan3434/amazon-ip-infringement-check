// amz.js — 多次重试抓 Amazon 页面，直到字节数足够
const fs = require('fs');
const out = process.argv[2];
const url = process.argv[3];
const UAS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
];
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const log = [];
  for (let i = 0; i < 8; i++) {
    const ua = UAS[i % UAS.length];
    try {
      const ctl = new AbortController();
      const t = setTimeout(() => ctl.abort(), 60000);
      const r = await fetch(url, {
        headers: {
          'User-Agent': ua,
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.9',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
          'Upgrade-Insecure-Requests': '1',
          'Sec-Fetch-Dest': 'document',
          'Sec-Fetch-Mode': 'navigate',
          'Sec-Fetch-Site': 'none',
          'Sec-Fetch-User': '?1',
        },
        redirect: 'follow',
        signal: ctl.signal,
      });
      clearTimeout(t);
      const buf = Buffer.from(await r.arrayBuffer());
      log.push(`try${i} status=${r.status} bytes=${buf.length}`);
      if (buf.length > 200000) {
        fs.writeFileSync(out, buf);
        log.push('SAVED ' + buf.length);
        fs.writeFileSync('_amzlog.txt', log.join('\n'));
        console.log(log.join('\n'));
        return;
      }
    } catch (e) {
      log.push(`try${i} ERR ${e.name}:${e.message}`);
    }
    await sleep(2500);
  }
  fs.writeFileSync('_amzlog.txt', log.join('\n'));
  console.log(log.join('\n'));
})();
