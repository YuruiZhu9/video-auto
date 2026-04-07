#!/usr/bin/env python3
"""
CosyVoice2 推理脚本
功能：阿里开源零样本语音克隆 / 多语言合成 / 流式输出
参考：https://github.com/FunAudioLLM/CosyVoice
"""

import sys
import os
import argparse
import datetime

def cosyvoice_tts(text, ref_audio=None, preset=None, output=None):
    """使用 CosyVoice2 生成语音"""
    try:
        from cosyvoice import CosyVoice
        import soundfile as sf
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请先安装：pip install cosyvoice soundfile")
        sys.exit(1)

    print("加载 CosyVoice2-0.5B 模型...")
    cosyvoice = CosyVoice("CosyVoice2-0.5B")

    if ref_audio and os.path.exists(ref_audio):
        print(f"使用零样本克隆模式，参考音频: {ref_audio}")
        result = cosyvoice.inference_zero_shot(
            text,
            ref_audio,
            "对应的参考音频文字（可选，自动识别）"
        )
    elif preset:
        print(f"使用预设音色: {preset}")
        result = cosyvoice.inference_sft(text, preset)
    else:
        print("使用默认音色 (female_zh)")
        result = cosyvoice.inference_sft(text, "female_zh")

    if output is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"/workspace/voice-cloning/results/cosyvoice_{timestamp}.wav"

    os.makedirs(os.path.dirname(output), exist_ok=True)
    sf.write(output, result["speech"], result["sample_rate"])
    print(f"✅ 音频已生成: {output}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CosyVoice2 语音克隆/合成")
    parser.add_argument("text", help="要转换的文字")
    parser.add_argument("--ref", "-r", default=None, help="参考音频路径（用于克隆）")
    parser.add_argument(
        "--preset", "-p",
        choices=["female_zh", "male_zh", "female_en", "male_en", "female_ja", "male_ja", "female_ko", "male_ko"],
        default=None,
        help="预设音色（无克隆时使用）"
    )
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    args = parser.parse_args()

    cosyvoice_tts(text=args.text, ref_audio=args.ref, preset=args.preset, output=args.output)
