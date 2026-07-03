#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const inputPath = process.argv[2] ?? 'output/earthquakes.json';
const outputPath = process.argv[3] ?? 'output/index.html';
const document = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
const embedded = JSON.stringify(document).replaceAll('<', '\\u003c');

const html = `<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Japan Earthquake Monitor - HW25A064</title>
<style>
:root { color-scheme: light; --ink:#17212b; --muted:#657383; --line:#d8dee6; --paper:#f5f7fa; --accent:#b64232; }
* { box-sizing:border-box; }
body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif; color:var(--ink); background:var(--paper); }
header { background:white; border-bottom:1px solid var(--line); padding:24px clamp(20px,5vw,72px); }
header h1 { margin:0 0 6px; font-size:clamp(24px,4vw,38px); }
header p { margin:0; color:var(--muted); }
main { width:min(1120px,92vw); margin:28px auto 60px; }
.cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; }
.card { background:white; border:1px solid var(--line); border-radius:10px; padding:18px; }
.card strong { display:block; font-size:28px; margin-top:6px; }
.panel { margin-top:20px; background:white; border:1px solid var(--line); border-radius:10px; padding:20px; }
.controls { display:flex; flex-wrap:wrap; gap:12px; align-items:end; }
label { font-size:13px; color:var(--muted); }
input, select { display:block; margin-top:5px; padding:8px 10px; border:1px solid #aeb7c2; border-radius:6px; background:white; }
.chart { display:flex; align-items:end; gap:8px; min-height:170px; padding-top:20px; border-bottom:1px solid var(--line); }
.bar-wrap { flex:1; min-width:24px; text-align:center; font-size:11px; color:var(--muted); }
.bar { width:100%; max-width:46px; margin:0 auto 6px; background:var(--accent); border-radius:5px 5px 0 0; min-height:3px; }
table { width:100%; border-collapse:collapse; margin-top:16px; font-size:14px; }
th, td { padding:10px 8px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
th { color:#43505e; background:#fafbfc; position:sticky; top:0; }
.mag { font-weight:700; }
.mag-high { color:#a22f24; }
.small { color:var(--muted); font-size:12px; }
.table-wrap { overflow:auto; max-height:580px; }
footer { text-align:center; color:var(--muted); padding:24px; }
@media (max-width:680px) { th:nth-child(5),td:nth-child(5),th:nth-child(6),td:nth-child(6){display:none;} }
</style>
</head>
<body>
<header>
  <h1>Japan Earthquake Monitor</h1>
  <p>日本周辺の地震情報を取得し、Jenkinsで自動生成したダッシュボード / HW25A064 實光駿斗</p>
</header>
<main>
  <section class="cards" id="summary"></section>
  <section class="panel">
    <h2>日別件数</h2>
    <div id="chart" class="chart" aria-label="日別地震件数の棒グラフ"></div>
  </section>
  <section class="panel">
    <div class="controls">
      <label>地名検索<input id="search" type="search" placeholder="例: Honshu"></label>
      <label>最低マグニチュード<select id="minMag"><option value="0">すべて</option><option value="3">3.0以上</option><option value="4">4.0以上</option><option value="5">5.0以上</option></select></label>
      <span class="small" id="resultCount"></span>
    </div>
    <div class="table-wrap"><table>
      <thead><tr><th>発生時刻(JST)</th><th>規模</th><th>場所</th><th>深さ</th><th>緯度</th><th>経度</th></tr></thead>
      <tbody id="rows"></tbody>
    </table></div>
  </section>
  <section class="panel small" id="meta"></section>
</main>
<footer>Generated automatically by Python, JavaScript and Jenkins.</footer>
<script id="earthquake-data" type="application/json">${embedded}</script>
<script>
const doc = JSON.parse(document.getElementById('earthquake-data').textContent);
const summaryItems = [
  ['取得件数', doc.summary.count + '件'],
  ['最大M', doc.summary.max_magnitude.toFixed(1)],
  ['平均M', doc.summary.average_magnitude.toFixed(2)],
  ['平均深さ', doc.summary.average_depth_km.toFixed(1) + 'km'],
  ['M5以上', doc.summary.magnitude_5_or_more + '件']
];
document.getElementById('summary').innerHTML = summaryItems.map(([label,value]) => '<article class="card"><span class="small">'+label+'</span><strong>'+value+'</strong></article>').join('');

const daily = new Map();
for (const item of doc.events) {
  const day = item.time_jst.slice(5,10);
  daily.set(day, (daily.get(day) ?? 0) + 1);
}
const entries = [...daily.entries()].sort((a,b) => a[0].localeCompare(b[0]));
const maxCount = Math.max(...entries.map(([,v]) => v), 1);
document.getElementById('chart').innerHTML = entries.map(([day,count]) => '<div class="bar-wrap"><div class="bar" style="height:'+Math.max(3, count/maxCount*135)+'px" title="'+count+'件"></div><b>'+count+'</b><br>'+day+'</div>').join('');

function renderRows() {
  const query = document.getElementById('search').value.trim().toLowerCase();
  const minMag = Number(document.getElementById('minMag').value);
  const filtered = doc.events.filter(item => item.magnitude >= minMag && item.place.toLowerCase().includes(query));
  document.getElementById('rows').innerHTML = filtered.map(item => {
    const magClass = item.magnitude >= 5 ? 'mag mag-high' : 'mag';
    return '<tr><td>'+item.time_jst.replace('T',' ')+'</td><td class="'+magClass+'">M'+item.magnitude.toFixed(1)+'</td><td>'+
      (item.detail_url ? '<a href="'+item.detail_url+'" target="_blank" rel="noreferrer">'+item.place+'</a>' : item.place) +
      '</td><td>'+item.depth_km.toFixed(1)+' km</td><td>'+item.latitude.toFixed(4)+'</td><td>'+item.longitude.toFixed(4)+'</td></tr>';
  }).join('');
  document.getElementById('resultCount').textContent = filtered.length + '件を表示';
}
document.getElementById('search').addEventListener('input', renderRows);
document.getElementById('minMag').addEventListener('change', renderRows);
renderRows();
document.getElementById('meta').textContent = '生成日時: '+doc.generated_at_jst+' / データソース: '+doc.source+' / 期間: 過去'+doc.query.days+'日 / 最低M: '+doc.query.minimum_magnitude;
</script>
</body>
</html>`;

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, html, 'utf8');
console.log(`[dashboard] generated ${outputPath} (${document.events.length} events)`);
