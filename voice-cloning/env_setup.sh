#!/bin/bash
# ============================================================
# 语音克隆环境一键安装脚本
# 支持：Qwen3-TTS / CosyVoice2 / ChatTTS v2 / F5-TTS
# ============================================================

set -e

echo "=========================================="
echo "  语音克隆环境安装脚本"
echo "=========================================="

# 检测 conda
if ! command -v conda &>/dev/null; then
    echo "❌ 未找到 conda，请先安装 Miniconda/Anaconda"
    exit 1
fi

ENV_NAME="voice-cloning"
PYTHON_VERSION="3.10"

# 创建环境
echo ">>> 创建 conda 环境: ${ENV_NAME}"
conda create -n ${ENV_NAME} python=${PYTHON_VERSION} -y

# 激活环境（兼容不同shell）
if [[ -f ~/miniconda3/etc/profile.d/conda.sh ]]; then
    source ~/miniconda3/etc/profile.d/conda.sh
elif [[ -f ~/anaconda3/etc/profile.d/conda.sh ]]; then
    source ~/anaconda3/etc/profile.d/conda.sh
fi
conda activate ${ENV_NAME}

echo ">>> 安装 PyTorch (CUDA 12.4)"
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

echo ">>> 安装语音克隆依赖"
pip install \
    qwen3-tts \
    ChatTTS \
    cosyvoice \
    soundfile \
    numpy \
    scipy \
    fastapi \
    uvicorn

# 设置模型下载镜像（国内加速）
export HF_ENDPOINT=${HF_ENDPOINT:-https://hf-mirror.com}

echo ""
echo "=========================================="
echo "  ✅ 安装完成！"
echo "=========================================="
echo ""
echo "激活环境：conda activate ${ENV_NAME}"
echo "运行示例："
echo "  python /workspace/voice-cloning/scripts/qwen3_tts_infer.py \\"
echo "    '今天天气真好' \\"
echo "    --ref /workspace/voice-cloning/ref-audio/my-voice.wav"
echo ""
echo "详细文档：/workspace/reports/voice-cloning/README.md"
