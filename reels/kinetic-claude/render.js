// Покадровый рендер index.html (GSAP-таймлайн) в silent.mp4.
// node render.js            — полный рендер по timing.json
// node render.js --snap 1,5 — снимки кадров snap_<t>.jpg (время ролика) для проверки
const path = require('path');
const { spawn } = require('child_process');
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const cfg = require('./timing.json');
const A = cfg.anchors;
const fps = cfg.fps || 30;
// время ролика -> время исходной анимации (кусочно-линейно по якорям)
const map = t => {
  for (let i = 1; i < A.length; i++)
    if (t <= A[i][0]) { const [a, b] = A[i - 1], [c, d] = A[i]; return b + (t - a) * (d - b) / (c - a); }
  return A.at(-1)[1];
};

(async () => {
  const b = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(__dirname, 'index.html'));
  await p.waitForFunction('window.READY');
  const snap = process.argv.indexOf('--snap');
  if (snap > 0) {
    for (const t of process.argv[snap + 1].split(',')) {
      await p.evaluate(`seek(${map(+t)})`);
      await p.screenshot({ path: path.join(__dirname, `snap_${t}.jpg`), type: 'jpeg', quality: 70 });
    }
    return b.close();
  }
  const out = path.join(__dirname, 'silent.mp4');
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round(A.at(-1)[0] * fps);
  for (let i = 0; i < n; i++) {
    await p.evaluate(`seek(${map(i / fps)})`);
    ff.stdin.write(await p.screenshot({ type: 'jpeg', quality: 92 }));
    if (i % 60 === 0) process.stdout.write(`${i}/${n} `);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
  console.log('\nsilent.mp4 готов');
})();
