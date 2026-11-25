// Render a scene's static markup (no scripts) at 1080x1920 and print element centres in frame px.
// Usage: node tools/measure.cjs compositions/s4-page.html id1 id2 ...
const fs = require("fs"), path = require("path");
const { chromium } = require("playwright");
(async () => {
  const [file, ...ids] = process.argv.slice(2);
  const root = path.resolve(__dirname, "..");
  let tpl = fs.readFileSync(path.join(root, file), "utf8");
  tpl = tpl.replace(/^[\s\S]*?<template>/, "").replace(/<\/template>[\s\S]*$/, "").replace(/<script[\s\S]*?<\/script>/g, "");
  const html = `<!doctype html><html><head><meta charset="utf-8"><base href="file://${root}/">
<link rel="stylesheet" href="assets/css/common.css"><style>html,body{margin:0;width:1080px;height:1920px;overflow:hidden}</style></head>
<body><div style="position:relative;width:1080px;height:1920px">${tpl}</div></body></html>`;
  const tmp = path.join(root, ".hyperframes", "measure.html");
  fs.writeFileSync(tmp, html);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto("file://" + tmp);
  await p.evaluate(() => document.fonts.ready);
  const out = await p.evaluate((ids) => Object.fromEntries(ids.map((id) => {
    const r = document.getElementById(id).getBoundingClientRect();
    return [id, { x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2), w: Math.round(r.width), h: Math.round(r.height) }];
  })), ids);
  console.log(JSON.stringify(out));
  await p.screenshot({ path: path.join(root, ".hyperframes", "measure.png") });
  await b.close();
})();
