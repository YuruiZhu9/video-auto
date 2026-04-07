#!/usr/bin/env python3
"""
ChatTTS v2 推理脚本
功能：无需克隆的对话式语音合成
参考：https://github.com/2noise/ChatTTS
"""

import sys
import os
import argparse
import datetime

def chattts_tts(text, seed=42, speed=5, oral=2, laugh=0, breath=2, output=None):
    """使用 ChatTTS v2 生成自然对话语音"""
    try:
        import torch
        import ChatTTS
        import numpy as np
        import scipy.io.wavfile as wav
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请先安装：pip install ChatTTS soundfile scipy")
        sys.exit(1)

    print("加载 ChatTTS 模型...")
    chat = ChatTTS.Chat()
    chat.load(compile=True)  # compile=True 可加速推理

    # 情感参数（通过韵律代码控制）
    params_refine_text = ChatTTS.Chat.RefineText(
        Prompt=f"[oral_{oral}][laugh_{laugh}][breath_{breath}]",
        Seed=seed,
    )
    params_infer_code = ChatTTS.Chat.InferCode(
        Speed=speed,  # 1-9，5为标准语速
    )

    print(f"生成语音（文本长度: {len(text)} 字，seed={seed}）...")
    wavs = chat.generate(
        text,
        params_refine_text=params_refine_text,
        params_infer_code=params_infer_code,
    )

    if output is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"/workspace/voice-cloning/results/chattts_{timestamp}.wav"

    os.makedirs(os.path.dirname(output), exist_ok=True)

    audio_data = wavs[0].cpu().numpy() if hasattr(wavs[0], 'cpu') else wavs[0]
    # 归一化到 int16
    audio_data = (audio_data * 32767).astype(np.int16)
    wav.write(output, 24000, audio_data)

    print(f"✅ 音频已生成: {output}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChatTTS v2 对话语音合成")
    parser.add_argument("text", help="要转换的文字")
    parser.add_argument("--seed", "-s", type=int, default=42, help="随机种子（固定音色）")
    parser.add_argument("--speed", type=int, default=5, choices=range(1, 10), help="语速 1-9")
    parser.add_argument("--oral", type=int, default=2, choices=range(0, 6), help="口语化程度 0-5")
    parser.add_argument("--laugh", type=int, default=0, choices=range(0, 5), help="笑声概率 0-4")
    parser.add_argument("--breath", type=int, default=2, choices=range(0, 6), help="呼吸音 0-5")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    args = parser.parse_args()

    chattts_tts(
        text=args.text,
        seed=args.seed,
        speed=args.speed,
        oral=args.oral,
        laugh=args.laugh,
        breath=args.breath,
        output=args.output,
    )
