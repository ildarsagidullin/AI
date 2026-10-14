// Покадровый рендер index.html в silent.mp4.
// Тайминги сцен: timing.json -> cues (старт каждой сцены, сек) и end (конец ролика).
// Без cues — черновые тайминги из index.html.
// node render.js            — полный рендер
// node render.js --snap 1,5 — снимки кадров snap_<t>.jpg для проверки
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const cfgPath = path.join(__dirname, 'timing.json');
const cfg = fs.existsSync(cfgPath) ? JSON.parse(fs.readFileSync(cfgPath, 'utf8')) : {};
const fps = cfg.fps || 30;

(async () => {
  const b = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  if (cfg.cues) await p.addInitScript(`window.CUES=${JSON.stringify(cfg.cues)};window.END=${cfg.end};`);
  await p.goto('file://' + path.resolve(__dirname, 'index.html'));
  await p.waitForFunction('window.READY');
  const dur = await p.evaluate('window.DURATION');
  const snap = process.argv.indexOf('--snap');
  if (snap > 0) {
    for (const t of process.argv[snap + 1].split(',')) {
      await p.evaluate(`seek(${+t})`);
      await p.screenshot({ path: path.join(__dirname, `snap_${t}.jpg`), type: 'jpeg', quality: 70 });
    }
    return b.close();
  }
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', path.join(__dirname, 'silent.mp4')],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round(dur * fps);
  for (let i = 0; i < n; i++) {
    await p.evaluate(`seek(${i / fps})`);
    ff.stdin.write(await p.screenshot({ type: 'jpeg', quality: 92 }));
    if (i % 150 === 0) process.stdout.write(`${i}/${n} `);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
  console.log(`\nsilent.mp4 готов (${dur.toFixed(2)} c)`);
})();
