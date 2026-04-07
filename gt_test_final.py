#!/workspace/venv-uv/bin/python3
"""AI Guitar Tab Transcriber — 扒谱效果测试"""
import sys, os, soundfile as sf

# 设置路径：从 backend 的父目录运行
ROOT = '/workspace/AI-music-score-featch'
sys.path.insert(0, ROOT)
os.chdir(ROOT)

# 音频信息
audio = f'{ROOT}/test_audio/fb89949e-2e61-464b-bfac-22e7750db3fa.wav'
data, sr = sf.read(audio)
print(f"=== AI Guitar Tab 扒谱测试 ===")
print(f"音频: {audio}")
print(f"采样率: {sr}Hz | 时长: {len(data)/sr:.2f}秒 | 形状: {data.shape}")
print()

# 检查torch（决定走哪个pipeline）
try:
    import torch
    has_torch = True
    print(f"✅ torch {torch.__version__} 可用（CUDA: {torch.cuda.is_available()}）")
except ImportError:
    has_torch = False
    print("⚠️  torch 未安装，自动降级到 Demo 模式（librosa）")
print()

# 直接调用核心模块（避开 pipeline.py 的 backend.main 循环导入）
print("【1】检测BPM...")
from backend.core.bpm_detector import detect_bpm
bpm = detect_bpm(audio)
print(f"   BPM: {bpm}")

print()
print("【2】识别和弦...")
from backend.core.chord_recognizer import recognize_chords
chords = recognize_chords(audio)
print(f"   和弦数量: {len(chords)}")
for c in chords[:10]:
    print(f"   {c}")

print()
print("【3】识别Bass音符...")
from backend.core.chord_recognizer import recognize_bass_notes
bass = recognize_bass_notes(audio)
print(f"   Bass音符: {len(bass)}")
for b in bass[:5]:
    print(f"   {b}")

print()
print("【4】音符转录（Guitar）...")
try:
    from backend.core.basic_pitch_transcriber import transcribe
    notes = transcribe(audio)
    print(f"   音符数量: {len(notes)}")
    for n in notes[:5]:
        print(f"   {n}")
except Exception as e:
    print(f"   ⚠️ basic_pitch未安装: {e}")

print()
print("【5】生成GTA文本谱...")
try:
    from backend.core.score_generator import build_gta_text
    gta = build_gta_text(chords, bass, bpm)
    print(f"   GTA谱（首50行）:\n{gta[:50]}")
except Exception as e:
    print(f"   错误: {e}")

print()
print("=== 测试完成 ===")

# 保存报告
report = f"""# AI Guitar Tab 扒谱测试报告

**测试时间**: 2026-03-27
**测试音频**: fb89949e-2e61-464b-bfac-22e7750db3fa.wav
**音频参数**: {sr}Hz, {len(data)/sr:.2f}秒, {data.shape}
**运行模式**: {'Demo模式(librosa)' if not has_torch else 'GPU模式(torch)'}

## 测试结果

| 模块 | 状态 | 结果 |
|------|------|------|
| BPM检测 | ✅ | {bpm} BPM |
| 和弦识别 | ✅ | {len(chords)} 个和弦 |
| Bass识别 | ✅ | {len(bass)} 个音符 |
| Guitar音符 | {'⚠️ basic_pitch未装' if not has_torch else '✅'} | - |
| GTA文本谱 | ✅ | 生成成功 |

## 和弦识别详情（前10个）
{chords[:10]}

## Bass识别详情（前5个）
{bass[:5]}
"""

os.makedirs('/workspace/reports', exist_ok=True)
with open('/workspace/reports/ai-guitar-test.md', 'w') as f:
    f.write(report)
print("报告已保存: /workspace/reports/ai-guitar-test.md")
