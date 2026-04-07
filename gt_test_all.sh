#!/bin/bash
# Full test: install basic_pitch + run pipeline test + save report
exec > /workspace/gt_test_log.txt 2>&1

echo "Step 1: Install basic_pitch to venv"
uv pip install --python /workspace/venv-uv/bin/python3 "basic-pitch>=2024.2.2" 2>&1 | tail -5
echo "Exit: $?"

echo "Step 2: Verify basic_pitch"
/workspace/venv-uv/bin/python3 -c "import basic_pitch; print('OK basic_pitch')" 2>&1

echo "Step 3: Run pipeline test"
cd /workspace/AI-music-score-featch/backend
/workspace/venv-uv/bin/python3 -c "
import sys, os, soundfile as sf

audio = '/workspace/AI-music-score-featch/test_audio/fb89949e-2e61-464b-bfac-22e7750db3fa.wav'
data, sr = sf.read(audio)
print(f'Audio: {sr}Hz, {len(data)/sr:.2f}s')

# 正确导入方式：从backend根目录运行
import asyncio
sys.path.insert(0, '.')
os.chdir('/workspace/AI-music-score-featch/backend')

# 直接调用核心函数（不用pipeline的事务注册）
from core.chord_recognizer import recognize_chords
from core.bpm_detector import detect_bpm
from core.basic_pitch_transcriber import transcribe

print('识别chords...')
chords = recognize_chords(audio)
print(f'Chords: {len(chords)} found')
for c in chords[:5]:
    print(f'  {c}')

print('识别BPM...')
bpm = detect_bpm(audio)
print(f'BPM: {bpm}')

print('音符转录...')
notes = transcribe(audio)
print(f'Notes: {len(notes)} found')

print('ALL OK')
" 2>&1

echo "Done at $(date)"
