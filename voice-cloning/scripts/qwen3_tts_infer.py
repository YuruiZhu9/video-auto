#!/usr/bin/env python3
"""
Qwen3-TTS 推理脚本
功能：零样本语音克隆 / 自然语言声音设计
参考：https://github.com/QwenLM/Qwen3-TTS
"""

import sys
import os
import argparse
import datetime

def tts_clone(text, ref_audio=None, voice_desc=None, output=None):
    """使用 Qwen3-TTS 生成语音"""
    try:
        from qwen3_tts import Qwen3TTS
        import soundfile as sf
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请先安装：pip install qwen3-tts soundfile")
        sys.exit(1)

    # 模型选择：0.6B（轻量）或 1.7B（高质量）
    model_name = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
    print(f"加载模型: {model_name} ...")

    model = Qwen3TTS(model_name, quantize="int8")

    kwargs = {"text": text, "language": "auto"}

    if ref_audio and os.path.exists(ref_audio):
        kwargs["ref_audio"] = ref_audio
        print(f"使用克隆模式，参考音频: {ref_audio}")
    elif voice_desc:
        kwargs["voice"] = voice_desc
        print(f"使用声音设计模式: {voice_desc}")
    else:
        print("警告：未提供参考音频或音色描述，使用默认音色")

    print(f"正在生成语音（文本长度: {len(text)} 字）...")
    audio = model.generate(**kwargs)

    if output is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"/workspace/voice-cloning/results/qwen3_{timestamp}.wav"

    os.makedirs(os.path.dirname(output), exist_ok=True)

    # 转换为标准格式并保存
    if hasattr(audio, 'numpy'):
        audio_data = audio.numpy()
    else:
        audio_data = audio

    sf.write(output, audio_data, 24000)
    print(f"✅ 音频已生成: {output}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Qwen3-TTS 语音克隆/合成")
    parser.add_argument("text", help="要转换的文字")
    parser.add_argument("--ref", "-r", default=None, help="参考音频路径（用于克隆）")
    parser.add_argument("--voice", "-v", default=None, help="自然语言音色描述，如 'a warm elderly man'")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    args = parser.parse_args()

    tts_clone(args.text, ref_audio=args.ref, voice_desc=args.voice, output=args.output)
