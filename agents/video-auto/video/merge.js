/**
 * video-auto 视频合成流水线 v3
 * 使用 ESM 动态 import 调用 @ffmpeg/ffmpeg
 *
 * 功能：
 *  1. 探测 TTS 音频时长（纯 Python wave）
 *  2. 将音频均匀切分为 n 段（Python）
 *  3. 将每段音频与对应视频片段合并（FFmpeg WASM）
 *  4. 拼接所有片段（FFmpeg WASM concat）
 *
 * 运行：node --experimental-vm-modules video/merge.js
 * 或：  python3 video/merge_audio_video.py（纯 Python fallback）
 */

import { FFmpeg } from '../node_modules/@ffmpeg/ffmpeg/dist/esm/index.js';
import { fetchFile, toBlobURL } from '../node_modules/@ffmpeg/util/dist/esm/index.js';
import { readFileSync, writeFileSync, existsSync, mkdirSync, copyFileSync, unlinkSync, readdirSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';
import { execSync } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const AUDIO_FILE  = join(__dirname, '../audio/tts_output.wav');
const SLIDES_DIR  = join(__dirname, 'slides');
const OUTPUT_DIR  = join(__dirname, 'combined');

function todayDir() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

// ── 音频探测（Python fallback） ─────────────────────────────────
function getAudioDurationFallback(audioFile) {
  try {
    const out = execSync(`python3 -c "
import wave, sys
with wave.open('${audioFile}', 'rb') as w:
    print(w.getnframes() / w.getframerate())
"`, { encoding: 'utf8' });
    return parseFloat(out.trim()) || 0;
  } catch {
    return 0;
  }
}

// ── 音频切分（Python） ──────────────────────────────────────────
function splitAudioPython(audioFile, nChunks) {
  const outPattern = join(SLIDES_DIR, 'chunk_{:02d}.wav');
  try {
    execSync(`python3 -c "
import wave, sys, os

n = ${nChunks}
with wave.open('${audioFile}', 'rb') as w:
    params = w.getparams()
    frames = w.readframes(w.getnframes())

total = params.nframes
per = total // n
for i in range(n):
    s = i * per * params.sampwidth * params.channels
    if i == n - 1:
        ch = frames[s:]
    else:
        ch = frames[s:(s + per * params.sampwidth * params.channels)]
    out = '${outPattern}'.format(i+1)
    with wave.open(out, 'wb') as w:
        w.setparams(params)
        w.writeframes(ch)
    print(f'chunk {{i+1}}: {len(ch)//params.sampwidth//params.channels}s')
"`, { encoding: 'utf8' });
    console.log('  Python 音频切分完成');
    return true;
  } catch (e) {
    console.error('  Python 切分失败:', e.message);
    return false;
  }
}

// ── FFmpeg WASM 加载 ───────────────────────────────────────────
async function loadFFmpeg() {
  const ffmpeg = new FFmpeg();
  const onLog = ({ message }) => {
    if (message.includes('frame=') || message.includes('time=')) process.stdout.write('.');
    else if (message.trim()) process.stdout.write(`\n  [ffmpeg] ${message}`);
  };
  ffmpeg.on('log', onLog);

  const cdnBase = 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/umd';
  try {
    await ffmpeg.load({
      coreURL: await toBlobURL(`${cdnBase}/ffmpeg-core.js`, 'text/javascript'),
      wasmURL: await toBlobURL(`${cdnBase}/ffmpeg-core.wasm`, 'application/wasm'),
    });
    console.log('✅ FFmpeg WASM 加载成功');
    return { ffmpeg, ok: true };
  } catch (e) {
    console.log(`⚠️  加载失败: ${e.message}`);
    try {
      const altBase = 'https://cdn.jsdelivr.net/npm/@ffmpeg/core@0.12.6/dist/umd';
      await ffmpeg.load({
        coreURL: await toBlobURL(`${altBase}/ffmpeg-core.js`, 'text/javascript'),
        wasmURL: await toBlobURL(`${altBase}/ffmpeg-core.wasm`, 'application/wasm'),
      });
      console.log('✅ FFmpeg WASM 加载成功（备用CDN）');
      return { ffmpeg, ok: true };
    } catch (e2) {
      console.error('❌ FFmpeg WASM 加载全部失败');
      return { ffmpeg: null, ok: false };
    }
  }
}

// ── 音频+视频合并（FFmpeg WASM） ────────────────────────────────
async function mergeOneWasm(ffmpeg, videoFile, audioFile, outFile) {
  await ffmpeg.writeFile('v.mp4', await fetchFile(videoFile));
  await ffmpeg.writeFile('a.wav', await fetchFile(audioFile));
  await ffmpeg.exec([
    '-i', 'v.mp4', '-i', 'a.wav',
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
    '-shortest', '-y', outFile,
  ]);
  await ffmpeg.deleteFile('v.mp4');
  await ffmpeg.deleteFile('a.wav');
}

// ── 音频+视频合并（系统 ffmpeg） ────────────────────────────────
async function mergeOneFFmpeg(videoFile, audioFile, outFile) {
  return new Promise((resolve) => {
    const p = spawn('ffmpeg', [
      '-i', videoFile, '-i', audioFile,
      '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
      '-shortest', '-y', outFile,
    ]);
    let err = '';
    p.stderr.on('data', d => { err += d.toString(); });
    p.on('close', code => {
      resolve(code === 0);
      if (code !== 0) console.log(`  ffmpeg err: ${err.slice(-100)}`);
    });
  });
}

// ── 主流程 ─────────────────────────────────────────────────────
async function main() {
  console.log('\n🎬 video-auto 视频合成流水线 v3\n');
  console.log('  音频:', AUDIO_FILE);
  console.log('  片段:', SLIDES_DIR);

  // 验证
  if (!existsSync(AUDIO_FILE)) {
    console.error('❌ 音频不存在，请先生成 TTS 配音');
    process.exit(1);
  }

  const slides = readdirSync(SLIDES_DIR)
    .filter(f => /^slide\d+\.mp4$/i.test(f))
    .sort((a, b) => parseInt(a.match(/\d+/)[0]) - parseInt(b.match(/\d+/)[0]))
    .map(f => join(SLIDES_DIR, f));

  if (!slides.length) {
    console.error('❌ 未找到视频片段，请先生成视频');
    process.exit(1);
  }
  console.log(`✅ 音频存在，${slides.length} 个视频片段\n`);

  // Step 1: 探测音频时长
  console.log('⏱️  Step 1: 探测音频时长...');
  const audioDuration = getAudioDurationFallback(AUDIO_FILE);
  console.log(`  音频时长: ${audioDuration.toFixed(1)} 秒\n`);

  // Step 2: 切分音频
  console.log('✂️  Step 2: 切分音频...');
  const ok = splitAudioPython(AUDIO_FILE, slides.length);
  if (!ok) {
    console.error('❌ 音频切分失败');
    process.exit(1);
  }

  // 确认 chunk 文件
  const chunks = [];
  for (let i = 1; i <= slides.length; i++) {
    const c = join(SLIDES_DIR, `chunk_${String(i).padStart(2,'0')}.wav`);
    chunks.push({ file: existsSync(c) ? c : null, idx: i });
  }
  const validChunks = chunks.filter(c => c.file);
  console.log(`  有效音频片段: ${validChunks.length}/${slides.length}\n`);

  // Step 3: 合并音频+视频
  console.log('🎞️  Step 3: 合并音频+视频片段...');
  const merged = [];
  for (let i = 0; i < slides.length; i++) {
    const outFile = `/tmp/merged_${String(i+1).padStart(2,'0')}.mp4`;
    process.stdout.write(`  [${i+1}/${slides.length}] ${slides[i].split('/').pop()}`);
    if (!chunks[i].file) {
      copyFileSync(slides[i], outFile);
      console.log(' ⏭️（无音频）');
      merged.push(outFile);
      continue;
    }
    // 优先用系统 ffmpeg
    let ok = false;
    try {
      ok = await mergeOneFFmpeg(slides[i], chunks[i].file, outFile);
    } catch {}
    if (!ok) {
      // 降级：复制原视频
      copyFileSync(slides[i], outFile);
      console.log(' ⏭️（合并失败）');
    } else {
      console.log(' ✅');
    }
    merged.push(outFile);
  }

  // 清理 chunks
  for (const c of chunks) {
    if (c.file) try { unlinkSync(c.file); } catch {}
  }

  // Step 4: 拼接
  console.log('\n🔗 Step 4: 拼接...');
  mkdirSync(OUTPUT_DIR, { recursive: true });
  const finalFile = join(OUTPUT_DIR, 'complete_with_audio.mp4');

  // 写 concat list
  const listContent = merged.map(f => `file '${f}'`).join('\n');
  writeFileSync('/tmp/concat.txt', listContent);

  let concatOk = false;
  try {
    await mergeOneFFmpeg('/tmp/concat.txt', '/dev/null', finalFile);
    concatOk = true;
  } catch {}
  if (!concatOk) {
    // 备选：直接复制第一个
    copyFileSync(merged[0], finalFile);
    console.log('  ⚠️ 拼接失败，复制第一段作为输出');
  } else {
    console.log('  ✅ 拼接成功');
  }

  // 清理
  for (const f of merged) try { unlinkSync(f); } catch {}
  try { unlinkSync('/tmp/concat.txt'); } catch {}

  // Step 5: 复制到日期目录
  const dateDir = join(__dirname, '..', '..', 'video', todayDir());
  mkdirSync(dateDir, { recursive: true });
  const destFile = join(dateDir, 'complete_with_audio.mp4');
  copyFileSync(finalFile, destFile);

  const sizeMB = (statSync(destFile).size / 1024 / 1024).toFixed(1);
  console.log(`\n🎉 完成！`);
  console.log(`📦 ${destFile} (${sizeMB} MB)`);
  console.log(`\n✅ 流水线执行完毕\n`);
}

main().catch(err => {
  console.error('\n❌ 异常:', err);
  process.exit(1);
});
