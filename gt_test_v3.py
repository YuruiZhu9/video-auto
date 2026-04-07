#!/workspace/venv-uv/bin/python3
"""AI Guitar Tab 扒谱效果测试"""
import sys, os, soundfile as sf

ROOT = '/workspace/AI-music-score-featch'
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.environ['PYTHONPATH'] = ROOT

TASK_ID = 'test-001'
audio = f'{ROOT}/test_audio/fb89949e-2e61-464b-bfac-22e7750db3fa.wav'

data, sr = sf.read(audio)
print(f"=== AI Guitar Tab 扒谱测试 ===")
print(f"音频: {sr}Hz | {len(data)/sr:.2f}秒 | {data.shape}")

# torch检查
try:
    import torch
    print(f"✅ torch {torch.__version__} 可用，CUDA={torch.cuda.is_available()}")
except ImportError:
    print("⚠️  torch 未装，走 Demo/librosa 模式")

print()

# ── 1. BPM ──────────────────────────────────────────────────────
from backend.core.bpm_detector import detect_bpm
print("【1】BPM 检测...")
r = detect_bpm(audio, TASK_ID)
print(f"   结果: {r}")
print()

# ── 2. 和弦识别 ─────────────────────────────────────────────────
from backend.core.chord_recognizer import recognize_chords
print("【2】和弦识别...")
chords = recognize_chords(audio, TASK_ID)
print(f"   识别到 {len(chords)} 个和弦")
for c in chords[:8]:
    print(f"   {c.get('start',0):.2f}s | {c.get('chord','?')} | 置信度 {c.get('confidence',0):.2f}")
print()

# ── 3. Bass 音符 ─────────────────────────────────────────────────
from backend.core.chord_recognizer import recognize_bass_notes
print("【3】Bass 音符识别...")
bass = recognize_bass_notes(audio, TASK_ID)
print(f"   识别到 {len(bass)} 个音符")
for b in bass[:8]:
    print(f"   {b.get('start',0):.2f}s | {b.get('note','?')} | 弦{b.get('string','?')} 品{b.get('fret','?')} | conf {b.get('confidence',0):.2f}")
print()

# ── 4. Guitar 音符转录 ─────────────────────────────────────────
from backend.core.basic_pitch_transcriber import is_available, transcribe
print(f"【4】Basic Pitch 可用: {is_available()}")
if is_available():
    notes = transcribe(audio, TASK_ID)
    print(f"   识别到 {len(notes)} 个音符")
    for n in notes[:5]:
        print(f"   {n}")
else:
    print("   ⚠️ basic_pitch 未安装，跳过")
    notes = []

# ── 5. GTA 文本谱生成 ───────────────────────────────────────────
print()
print("【5】GTA 文本谱生成...")
try:
    from backend.core.score_generator import build_gta_text
    bpm_val = r.get('bpm', 120) if isinstance(r, dict) else 120
    gta = build_gta_text(chords, bass, bpm_val)
    lines = gta.split('\n')
    print(f"   共 {len(lines)} 行")
    print("   前15行:")
    for l in lines[:15]:
        print(f"   | {l}")
except Exception as e:
    print(f"   ❌ 错误: {e}")
    import traceback; traceback.print_exc()

# ── 6. MIDI 生成 ───────────────────────────────────────────────
print()
print("【6】MIDI 文件生成...")
try:
    from backend.core.score_generator import build_midi_file
    out_dir = f'{ROOT}/backend/test_out'
    os.makedirs(out_dir, exist_ok=True)
    midi_path = build_midi_file(chords, bass, bpm_val if 'bpm_val' in dir() else 120, out_dir, TASK_ID)
    import os
    size = os.path.getsize(midi_path) if os.path.exists(midi_path) else 0
    print(f"   ✅ MIDI 生成成功: {midi_path} ({size} bytes)")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# ── 保存报告 ────────────────────────────────────────────────────
print()
print("=== 测试完成 ===")
report = f"""# AI Guitar Tab 扒谱测试报告

**日期**: 2026-03-27
**音频**: fb89949e-2e61-464b-bfac-22e7750db3fa.wav
**参数**: {sr}Hz / {len(data)/sr:.2f}秒
**模式**: {'GPU(torch)' if 'torch' in dir() else 'Demo(librosa)'}

## 模块测试结果

| 模块 | 状态 | 详情 |
|------|------|------|
| BPM检测 | ✅ | {r} |
| 和弦识别 | ✅ | {len(chords)} 个和弦 |
| Bass识别 | ✅ | {len(bass)} 个音符 |
| Guitar音符 | {'✅ '+str(len(notes))+'个音符' if notes else '⚠️ basic_pitch未装'} | - |
| GTA文本谱 | ✅ | {len(gta.split(chr(10)))}行 |
| MIDI | {'✅ 成功' if midi_path else '❌ 失败'} | - |

## 和弦详情
{chr(10).join(f"- {c.get('start',0):.2f}s | {c.get('chord','?')} | {c.get('confidence',0):.2f}" for c in chords[:15])}

## Bass音符详情
{chr(10).join(f"- {b.get('start',0):.2f}s | {b.get('note','?')} | 弦{b.get('string','?')}/品{b.get('fret','?')}" for b in bass[:15])}
"""
with open('/workspace/reports/ai-guitar-test.md', 'w', encoding='utf-8') as f:
    f.write(report)
print("报告已保存: /workspace/reports/ai-guitar-test.md")
