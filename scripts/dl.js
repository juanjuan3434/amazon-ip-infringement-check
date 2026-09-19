const fs = require('fs');
// list: [输出文件名, 专利号]
const list = [
  ['D874826.pdf', 'D874826'],
  ['D968078.pdf', 'D968078'],
  ['D1014960.pdf', 'D1014960'],
];
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const log = [];
  for (const [f, id] of list) {
    if (fs.existsSync(f) && fs.statSync(f).size > 20000) { log.push(`${f} cached`); continue; }
    for (let i = 1; i <= 4; i++) {
      try {
        const ctl = new AbortController();
        const t = setTimeout(() => ctl.abort(), 110000);
        const r = await fetch('https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/' + id, {
          headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'application/pdf,*/*', 'Referer': 'https://ppubs.uspto.gov/' },
          signal: ctl.signal,
        });
        clearTimeout(t);
        if (r.ok) {
          const b = Buffer.from(await r.arrayBuffer());
          fs.writeFileSync(f, b);
          log.push(`${f} OK ${b.length} try${i}`);
          break;
        }
        log.push(`${f} HTTP ${r.status} try${i}`);
      } catch (e) {
        log.push(`${f} ERR ${e.name}:${e.message} try${i}`);
      }
      await sleep(3000);
    }
    await sleep(1500);
  }
  fs.writeFileSync('_dl.txt', log.join('\n'));
  console.log(log.join('\n'));
})();
