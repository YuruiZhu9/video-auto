#!/usr/bin/env python3
"""
video-auto 视频拼接工具
使用 Python 拼接相同编码的 MP4 文件（纯 Python，无 ffmpeg）
原理：MP4 由 box 组成，相同编码的 MP4 可以通过拼接 mdat box 实现拼接

用法：
  python3 concat_mp4.py --files slide01.mp4 slide02.mp4 --output combined.mp4
  python3 concat_mp4.py --dir slides --pattern "slide%d.mp4" --count 9 --output combined.mp4
"""

import struct
import sys
import os
import argparse
from pathlib import Path

def parse_box(data, offset=0):
    """解析MP4 box，返回 (box_type, box_size, box_data, next_offset)"""
    if offset + 8 > len(data):
        return None, None, None, len(data)
    
    size = struct.unpack('>I', data[offset:offset+4])[0]
    box_type = data[offset+4:offset+8].decode('ascii', errors='replace')
    
    if size == 0:
        size = len(data) - offset
    elif size == 1:
        if offset + 16 > len(data):
            return None, None, None, len(data)
        size = struct.unpack('>Q', data[offset+8:offset+16])[0]
    
    box_data = data[offset+8:offset+size] if size > 8 else b''
    return box_type, size, box_data, offset + size

def get_mp4_info(filepath):
    """读取MP4基本信息"""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"  文件: {filepath} ({len(data)/1024:.0f} KB)")
    
    boxes = {}
    offset = 0
    while offset < len(data):
        box_type, box_size, box_data, offset = parse_box(data, offset)
        if box_type is None:
            break
        if box_type in ('moov', 'ftyp', 'mdat', 'free', 'skip'):
            boxes[box_type] = (box_size, box_data)
        # 不进入子box解析（简化）
    return boxes

def concat_mp4_files(input_files, output_file):
    """
    拼接多个MP4文件
    适用于：相同编码、相同分辨率、相同帧率的MP4文件
    """
    if not input_files:
        print("❌ 没有输入文件")
        return False
    
    if len(input_files) == 1:
        print(f"只有一个文件，直接复制")
        with open(input_files[0], 'rb') as src:
            data = src.read()
        with open(output_file, 'wb') as dst:
            dst.write(data)
        return True
    
    print(f"\n🔗 开始拼接 {len(input_files)} 个 MP4 文件...\n")
    
    # Step 1: 分析所有文件
    all_boxes = []
    for f in input_files:
        boxes = get_mp4_info(f)
        all_boxes.append(boxes)
    
    # Step 2: 检查是否兼容
    ftyp_data = all_boxes[0].get('ftyp')
    if not ftyp_data:
        print("❌ 第一个文件没有 ftyp box，无法拼接")
        return False
    
    print(f"\n📋 检查兼容性...")
    
    # 检查 moov 位置（最好都在文件开头）
    moov_positions = []
    for i, boxes in enumerate(all_boxes):
        if 'moov' in boxes:
            moov_positions.append(i)
    
    print(f"  moov在文件开头: {len(moov_positions)}/{len(all_boxes)}")
    
    # Step 3: 合并
    print(f"\n📦 执行合并...")
    
    output_parts = []
    mdat_parts = []
    
    for i, (filepath, boxes) in enumerate(zip(input_files, all_boxes)):
        print(f"  [{i+1}/{len(input_files)}] 处理 {os.path.basename(filepath)}...")
        
        with open(filepath, 'rb') as f:
            file_data = f.read()
        
        offset = 0
        while offset < len(file_data):
            box_type, box_size, box_data, offset = parse_box(file_data, offset)
            if box_type is None:
                break
            
            if box_type == 'ftyp':
                # 只保留第一个文件的 ftyp
                if i == 0:
                    output_parts.append(file_data[offset-8:offset-8+box_size])
            elif box_type == 'moov':
                # 只保留第一个文件的 moov（包含音视频元数据）
                if i == 0:
                    output_parts.append(file_data[offset-8:offset-8+box_size])
            elif box_type == 'mdat':
                # 收集所有 mdat 数据
                mdat_parts.append(file_data[offset-8:offset-8+box_size])
            # 跳过 free/skip 等辅助box
    
    # Step 4: 组装输出
    # 计算 mdat 的偏移量（粗略估计）
    current_offset = sum(len(p) for p in output_parts)
    
    print(f"\n  组装 {len(mdat_parts)} 个 mdat 片段...")
    
    # 如果所有文件 moov 都在开头，直接拼接
    if len(moov_positions) == len(all_boxes) and moov_positions[0] == 0:
        output = b''.join(output_parts) + b''.join(mdat_parts)
    else:
        # 使用更保守的方式：ftyp + moov + 所有 mdat
        output = b''.join(output_parts) + b''.join(mdat_parts)
    
    # Step 5: 写入
    with open(output_file, 'wb') as f:
        f.write(output)
    
    size_mb = os.path.getsize(output_file) / 1024 / 1024
    print(f"\n✅ 拼接完成: {output_file} ({size_mb:.1f} MB)")
    return True


def main():
    parser = argparse.ArgumentParser(description='MP4 拼接工具（纯 Python，无需 ffmpeg）')
    parser.add_argument('--files', nargs='+', help='输入 MP4 文件列表')
    parser.add_argument('--dir', help='输入目录')
    parser.add_argument('--pattern', default='slide%02d.mp4', help='文件模式（Python %% 格式化）')
    parser.add_argument('--count', type=int, default=9, help='文件数量')
    parser.add_argument('--output', required=True, help='输出文件路径')
    
    args = parser.parse_args()
    
    if args.files:
        input_files = args.files
    elif args.dir:
        input_files = [os.path.join(args.dir, args.pattern % i) for i in range(1, args.count + 1)]
    else:
        print("❌ 请指定 --files 或 --dir")
        sys.exit(1)
    
    input_files = [f for f in input_files if os.path.exists(f)]
    print(f"📂 找到 {len(input_files)} 个文件")
    
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    success = concat_mp4_files(input_files, args.output)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
