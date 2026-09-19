const fs = require('fs');
const list = [
  ['D1006632.pdf', 'D1006632'],
  ['D1012718.pdf', 'D1012718'],
  ['D1114621.pdf', 'D1114621'],
  ['D1090262.pdf', 'D1090262'],
  ['D1023770.pdf', 'D1023770'],
  ['D899943.pdf', 'D899943'],
  ['D904895.pdf', 'D904895'],
  ['D660704.pdf', 'D660704'],
  ['D660705.pdf', 'D660705'],
  ['D658998.pdf', 'D658998'],
];
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  for (const [f, id] of list) {
    if (fs.existsSync(f) && fs.statSync(f).size > 20000) { console.log(f, 'cached'); continue; }
    for (let i = 1; i <= 4; i++) {
      try {
        const ctl = new AbortController();
        const t = setTimeout(() => ctl.abort(), 110000);
        const r = await fetch('https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/' + id, {
          headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'application/pdf,*/*', 'Referer': 'https://ppubs.uspto.gov/' },
          signal: ctl.signal,
        });
        clearTimeout(t);
        if (r.ok) { const b = Buffer.from(await r.arrayBuffer()); fs.writeFileSync(f, b); console.log(f, 'OK', b.length); break; }
        console.log(f, 'HTTP', r.status, 'try', i);
      } catch (e) { console.log(f, 'ERR', e.name, e.message, 'try', i); }
      await sleep(2500);
    }
  }
})();
