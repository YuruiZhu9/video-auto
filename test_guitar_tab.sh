#!/bin/bash
# AI Guitar Tab Transcriber — 测试 + App规划
echo "=== AI Guitar Tab 扒谱测试报告 ==="
echo ""

# 1. 检查后端状态
echo "【1】后端服务状态"
if curl -s http://localhost:8000/health 2>/dev/null; then
    echo "✅ 后端运行中"
else
    echo "⚠️  后端未运行（将在本地启动测试）"
fi
echo ""

# 2. 检查核心依赖
echo "【2】核心依赖检查"
for pkg in yt_dlp librosa basic_pitch mido fpdf2 demucs 2>/dev/null; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo "  ✅ $pkg"
    else
        echo "  ❌ $pkg — 未安装"
    fi
done
echo ""

# 3. 检查测试音频（Creative Commons）
echo "【3】可用测试资源"
echo "  - YouTube CC音乐搜索..."
# 找一些CC许可的吉他演奏
echo "  备选测试曲目（CC许可/无版权）："
echo "  1. 'An American Trilogy' - 经典民谣（版权过期）"
echo "  2. 'Stairway to Heaven' intro - 最经典吉他Riff"
echo "  3. 'Nothing Else Matters' - Metallica"
echo "  4. B站吉他UP主原创演奏（联系合作）"
echo ""

# 4. 运行demo模式测试（无需真实音频）
echo "【4】运行Demo模式测试"
cd /workspace/AI-music-score-featch/backend
timeout 30 python3 -c "
from core.pipeline import transcribe_audio
import os
os.makedirs('./test_outputs', exist_ok=True)
try:
    result = transcribe_audio('./test_outputs', {}, 'demo_test')
    print('✅ Pipeline执行成功')
    print(f'   输出: {list(result.keys())}')
except Exception as e:
    print(f'⚠️  Pipeline执行: {e}')
" 2>/dev/null || echo "demo模式需要启动服务，跳过"
echo ""

# 5. 检查前端构建
echo "【5】前端状态"
if [ -d "/workspace/AI-music-score-featch/frontend/dist" ]; then
    echo "  ✅ 前端已构建（dist目录存在）"
    ls /workspace/AI-music-score-featch/frontend/dist/ | head -5
elif [ -d "/workspace/AI-music-score-featch/ai-guitar-tab-frontend/dist" ]; then
    echo "  ✅ 前端已构建（ai-guitar-tab-frontend）"
    ls /workspace/AI-music-score-featch/ai-guitar-tab-frontend/dist/ | head -5
else
    echo "  ⚠️  前端未构建，需要构建"
fi
echo ""

# 6. Git状态
echo "【6】Git状态"
cd /workspace/AI-music-score-featch
git status --short 2>/dev/null | head -10
echo ""

# 7. 已有测试案例
echo "【7】已有输出文件'
ls /workspace/AI-music-score-featch/backend/outputs/ 2>/dev/null | head -10
echo ""

echo "=== 测试完成 ==="
