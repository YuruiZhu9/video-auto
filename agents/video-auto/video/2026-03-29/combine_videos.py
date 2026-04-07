#!/usr/bin/env python3
"""
视频拼接脚本 - 使用 PyAV 库合并多个 MP4 片段
依赖: pip install av
用法: python3 combine_videos.py
"""
import os
import sys

try:
    import av
except ImportError:
    print("❌ PyAV 未安装。请先运行: pip install av")
    print("安装后重试: python3 combine_videos.py")
    sys.exit(1)

INPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SLIDES_DIR = os.path.join(INPUT_DIR, "slides")
OUTPUT_FILE = os.path.join(INPUT_DIR, "combined", "complete.mp4")

# 按顺序排列的视频文件
VIDEO_FILES = [f"slide{i:02d}.mp4" for i in range(1, 10)]

def combine_videos(input_files, output_path):
    """使用 PyAV 合并多个视频文件"""
    print(f"📹 开始合并 {len(input_files)} 个视频片段...")
    print(f"📁 输出路径: {output_path}")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 打开输出容器
    out_container = av.open(output_path, 'w')
    out_stream = None
    
    for idx, filename in enumerate(input_files):
        filepath = os.path.join(SLIDES_DIR, filename)
        if not os.path.exists(filepath):
            print(f"⚠️  文件不存在，跳过: {filepath}")
            continue
        
        print(f"  [{idx+1}/{len(input_files)}] 处理: {filename}")
        
        inp_container = av.open(filepath)
        in_stream = inp_container.streams.video[0]
        
        # 设置输出流（如果还没设置）
        if out_stream is None:
            out_stream = out_container.add_stream(
                'h264',
                rate=in_stream.guessed_rate,
                options={'preset': 'fast'}
            )
            out_stream.width = in_stream.width
            out_stream.height = in_stream.height
            out_stream.pix_fmt = 'yuv420p'
        
        for packet in inp_container.demux(in_stream):
            for frame in packet.decode():
                frame = frame.reformat(width=out_stream.width, height=out_stream.height, pix_fmt='yuv420p')
                for pkt in out_stream.encode(frame):
                    out_container.mux(pkt)
        
        inp_container.close()
    
    # 刷新编码器
    for pkt in out_stream.encode():
        out_container.mux(pkt)
    out_stream.close()
    out_container.close()
    
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✅ 合并完成！输出文件: {output_path} ({size_mb:.1f} MB)")

if __name__ == '__main__':
    # 过滤存在的文件
    existing_files = [f for f in VIDEO_FILES 
                     if os.path.exists(os.path.join(SLIDES_DIR, f))]
    
    if not existing_files:
        print("❌ 未找到任何视频文件，请确保 slide01.mp4 ~ slide09.mp4 在 slides/ 目录")
        sys.exit(1)
    
    print(f"发现 {len(existing_files)} 个视频文件")
    combine_videos(existing_files, OUTPUT_FILE)
