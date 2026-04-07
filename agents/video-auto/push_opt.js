#!/usr/bin/env node
const https = require('https');
const fs = require('fs');

const TOKEN = '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';
const REPO = 'YuruiZhu9/video-auto';

function httpReq(method, urlPath, data) {
  return new Promise((resolve, reject) => {
    const body = data ? JSON.stringify(data) : undefined;
    const options = {
      hostname: 'api.github.com',
      path: urlPath,
      method: method,
      headers: {
        'Authorization': 'token ' + TOKEN,
        'User-Agent': 'video-auto-agent',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
      }
    };
    if (body) options.headers['Content-Length'] = Buffer.byteLength(body);
    const req = https.request(options, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(d) }); }
        catch(e) { resolve({ status: res.statusCode, data: d }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function getSha(path) {
  try {
    const r = await httpReq('GET', `/repos/${REPO}/contents/${path}?ref=main`);
    return r.status === 200 ? r.data.sha : null;
  } catch(e) { return null; }
}

async function uploadFile(repoPath, localPath, msg) {
  const content = fs.readFileSync(localPath).toString('base64');
  const sha = await getSha(repoPath);
  const payload = { message: msg, content, branch: 'main' };
  if (sha) payload.sha = sha;
  const res = await httpReq('PUT', `/repos/${REPO}/contents/${repoPath}`, payload);
  console.log(`  ${repoPath}: ${res.status} ${res.status === 200 || res.status === 201 ? 'OK' : JSON.stringify(res.data).slice(0,200)}`);
  return res.status === 200 || res.status === 201;
}

(async () => {
  await uploadFile('OPTIMIZATION.md', '/workspace/agents/video-auto/OPTIMIZATION.md', 'Add OPTIMIZATION.md pipeline improvement plan');
})().catch(e => { console.error(e.message); process.exit(1); });
