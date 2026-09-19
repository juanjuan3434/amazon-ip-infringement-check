const fs = require('fs');
const list = [
  ['D1108260.pdf', 'D1108260'],
  ['D1014284.pdf', 'D1014284'],
  ['D1002381.pdf', 'D1002381'],
  ['D888570.pdf', 'D888570'],
  ['D887842.pdf', 'D887842'],
  ['D813673.pdf', 'D813673'],
  ['D700521.pdf', 'D700521'],
  ['D709381.pdf', 'D709381'],
  ['D1084872.pdf', 'D1084872'],
  ['D1145154.pdf', 'D1145154'],
  ['D1125697.pdf', 'D1125697'],
  ['D1114352.pdf', 'D1114352'],
  ['D1093159.pdf', 'D1093159'],
  ['D1088892.pdf', 'D1088892'],
  ['D1021262.pdf', 'D1021262'],
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
