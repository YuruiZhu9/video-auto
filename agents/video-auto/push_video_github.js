#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const https = require('https');

const TOKEN = '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';
const REPO = 'YuruiZhu9/video-auto';
const BRANCH = 'main';

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

async function getFileSha(repoPath) {
  try {
    const res = await httpReq('GET', `/repos/${REPO}/contents/${repoPath}?ref=${BRANCH}`);
    if ((res.status === 200 || res.status === 404) && res.data.sha) return res.data.sha;
    return null;
  } catch(e) { return null; }
}

async function uploadFile(repoPath, localPath, message) {
  console.log(`  Uploading: ${repoPath}`);
  const content = fs.readFileSync(localPath).toString('base64');
  const sha = await getFileSha(repoPath);
  const payload = { message, content, branch: BRANCH };
  if (sha) payload.sha = sha;
  
  const res = await httpReq('PUT', `/repos/${REPO}/contents/${repoPath}`, payload);
  if (res.status === 201 || res.status === 200) {
    console.log(`    ✓ Success`);
    return true;
  } else {
    console.log(`    ✗ Error (${res.status}): ${JSON.stringify(res.data).substring(0, 200)}`);
    return false;
  }
}

async function main() {
  console.log('=== GitHub Push: video-auto video project ===\n');

  const repoRes = await httpReq('GET', `/repos/${REPO}`);
  console.log(`Repo check: ${repoRes.status}`);
  if (repoRes.status !== 200) {
    console.log('Repo not accessible:', JSON.stringify(repoRes.data).substring(0, 300));
    return;
  }

  const BASE = '/workspace/agents/video-auto/video';
  let success = 0, fail = 0;

  // Helper: collect all files recursively
  function walkDir(dir, prefix = '') {
    const files = [];
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
      if (entry.isDirectory()) {
        files.push(...walkDir(full, rel));
      } else {
        files.push({ full, rel });
      }
    }
    return files;
  }

  const allFiles = walkDir(BASE);
  console.log(`Found ${allFiles.length} files to upload\n`);

  for (const { full, rel } of allFiles) {
    const repoPath = `video/${rel}`;
    const ok = await uploadFile(repoPath, full, `Add ${rel}`);
    if (ok) success++; else fail++;
    await new Promise(r => setTimeout(r, 300)); // Rate limit delay
  }

  console.log(`\n=== Summary ===`);
  console.log(`Success: ${success} / ${allFiles.length}`);
  console.log(`Failed: ${fail} / ${allFiles.length}`);
}

main().catch(e => {
  console.error('Fatal error:', e.message);
  process.exit(1);
});
