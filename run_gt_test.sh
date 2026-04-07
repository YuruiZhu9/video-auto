#!/bin/bash
echo "=== AI Guitar Tab 扒谱测试 ==="
VENV=/workspace/venv-uv/bin/python3

echo "【1】依赖检查"
$VENV -c "import librosa, numpy, scipy, mido, soundfile, yt_dlp; print('✅ 核心库OK')" 2>&1
$VENV -c "from basic_pitch import BasicPitch; print('✅ basic_pitch OK')" 2>&1

echo ""
echo "【2】已有测试音频"
ls -lh /workspace/AI-music-score-featch/test_audio/ 2>/dev/null | head -10

echo ""
echo "【3】yt-dlp下载的YouTube测试音频'
ls -lh /workspace/AI-music-score-featch/test_audio/youtube_test/ 2>/dev/null | head -10

echo ""
echo "【4】运行demo测试'
cd /workspace/AI-music-score-featch/backend
$VENV -c "
import sys, os
sys.path.insert(0, '.')
os.makedirs('./test_out', exist_ok=True)
try:
    from core.pipeline import transcribe_audio
    result = transcribe_audio('./test_out', {}, 'demo_test')
    print('✅ Pipeline执行成功!')
    print('Keys:', list(result.keys()))
except Exception as e:
    print('❌ Pipeline错误:', e)
    import traceback; traceback.print_exc()
" 2>&1

echo ""
echo "【5】查找所有输出文件'
find /workspace/AI-music-score-featch -name "*.mid" -o -name "*.gta" -o -name "*.txt" 2>/dev/null | grep -v __pycache__ | head -10

echo "=== 完成 ==="
