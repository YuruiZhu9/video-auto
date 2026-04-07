#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
video-auto 文件命名规范工具

功能：
  1. 统一输出文件命名格式：{prefix}_{topic_slug}_{seq:02d}_{date}_{suffix}.{ext}
  2. 主题转 slug（中文→拼音/英文）
  3. 自动生成带时间戳的文件清单
  4. 多视频拼接时的过渡文件名规范

命名规范：
  - 前缀：slide / video / audio / content / subtitle / grid
  - 主题：去除空格、特殊字符，转为小写slug（中文保留拼音）
  - 日期：{YYYY-MM-DD} 格式
  - 序号：{seq:02d} 自动递增
  - 片段类型后缀：_intro / _main / _outro / _transition / _final

示例：
  slide_ai_recommend_sys_01_2026-04-06_intro.mp4
  video_ai_recommend_sys_01_2026-04-06_seg02_main.mp4
  audio_script_ai_recommend_sys_01_2026-04-06.wav
  grid_topic_preview_2026-04-06.png

Author: video-auto optimizer
Version: 1.0.0
"""

import re
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# ====== 依赖处理 ======

def _safe_import_transliterate():
    """安全导入 transliterate 库（可选依赖）"""
    try:
        from transliterate import translit
        return translit
    except ImportError:
        return None


def _simple_slug(text: str) -> str:
    """无依赖的中文/英文 slug 生成"""
    # 去除标点和多余空格
    text = re.sub(r'[，。！？、：；""''【】（）\(\)\[\]\{\}<>《》/\\|`~!@#$%^&*+=]', ' ', text)
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 逐字符处理
    result = []
    for ch in text:
        code = ord(ch)
        if 0x4E00 <= code <= 0x9FFF:
            # CJK统一汉字 → 用拼音首字母近似
            result.append(_char_to_pinyin(ch))
        elif code <= 127:
            # ASCII 字符
            if ch.isalnum():
                result.append(ch.lower())
            else:
                result.append('_')
        # 空格等跳过
    return re.sub(r'_+', '_', ''.join(result).strip('_')).lower()


def _char_to_pinyin(ch: str) -> str:
    """简单汉字→拼音映射（常用500字，覆盖大部分场景）"""
    # 常用汉字拼音映射（简化版，覆盖90%常见字）
    _pinyin_map = {
        # 常用单字
        'AI': 'ai', '爱': 'ai', '的': 'de', '是': 'shi', '在': 'zai',
        '我': 'wo', '你': 'ni', '他': 'ta', '们': 'men', '有': 'you',
        '了': 'le', '不': 'bu', '这': 'zhe', '个': 'ge', '人': 'ren',
        '们': 'men', '来': 'lai', '到': 'dao', '们': 'men', '说': 'shuo',
        '为': 'wei', '学': 'xue', '可': 'ke', '以': 'yi', '会': 'hui',
        '就': 'jiu', '要': 'yao', '去': 'qu', '看': 'kan', '好': 'hao',
        '得': 'de', '地': 'di', '能': 'neng', '而': 'er', '着': 'zhe',
        '过': 'guo', '发': 'fa', '展': 'zhan', '更': 'geng', '新': 'xin',
        '技': 'ji', '术': 'shu', '视': 'shi', '频': 'pin', '频': 'pin',
        '系': 'xi', '统': 'tong', '推': 'tui', '荐': 'jian', '算': 'suan',
        '法': 'fa', '学': 'xue', '习': 'xi', '模': 'mo', '型': 'xing',
        '大': 'da', '语': 'yu', '言': 'yan', '数': 'shu', '据': 'ju',
        '据': 'ju', '图': 'tu', '片': 'pian', '音': 'yin', '乐': 'le',
        '视': 'shi', '觉': 'jue', '智': 'zhi', '能': 'neng', '应': 'ying',
        '用': 'yong', '互': 'hu', '联': 'lian', '网': 'wang', '云': 'yun',
        '计': 'ji', '算': 'suan', '机': 'ji', '数': 'shu', '据': 'ju',
        '处': 'chu', '理': 'li', '研': 'yan', '究': 'jiu', '开': 'kai',
        '发': 'fa', '工': 'gong', '具': 'ju', '平': 'ping', '台': 'tai',
        '视': 'shi', '频': 'pin', '工': 'gong', '具': 'ju', '最': 'zui',
        '新': 'xin', '进': 'jin', '展': 'zhan', '盘': 'pan', '点': 'dian',
               '最': 'zui', '新': 'xin', '前': 'qian', '沿': 'yan',
        '年': 'nian', '月': 'yue', '日': 'ri', '周': 'zhou', '报': 'bao',
        '告': 'gao', '工': 'gong', '作': 'zuo', '流': 'liu', '程': 'cheng',
        '效': 'xiao', '率': 'lv', '提': 'ti', '升': 'sheng', '视': 'shi',
        '频': 'pin', '剪': 'jian', '转': 'zhuan', '换': 'huan', '音': 'yin',
        '频': 'pin', '合': 'he', '并': 'bing', '片': 'pian', '成': 'cheng',
        '品': 'pin', '出': 'chu', '口': 'kou', '输': 'shu', '入': 'ru',
        '源': 'yuan', '码': 'ma', '格': 'ge', '式': 'shi', '分': 'fen',
        '辨': 'bian', '率': 'lv', '时': 'shi', '长': 'chang', '片': 'pian',
        '断': 'duan', '间': 'jian', '时': 'shi', '间': 'jian', '戳': 'chuo',
        '场': 'chang', '景': 'jing', '切': 'qie', '换': 'huan', '识': 'shi',
        '别': 'bie', '语': 'yu', '音': 'yin', '识': 'shi', '别': 'bie',
        '字': 'zi', '幕': 'mu', '字': 'zi', '母': 'mu', '合': 'he',
        '配': 'pei', '置': 'zhi', '参': 'can', '数': 'shu', '环': 'huan',
        '境': 'jing', '文': 'wen', '档': 'dang', '文': 'wen', '件': 'jian',
        '目': 'mu', '录': 'lu', '执': 'zhi', '行': 'xing', '错': 'cuo',
        '误': 'wu', '问': 'wen', '题': 'ti', '解': 'jie', '决': 'jue',
        '方': 'fang', '案': 'an', '介': 'jie', '绍': 'shao', '教': 'jiao',
        '程': 'cheng', '案': 'an', '例': 'li', '业': 'ye', '务': 'wu',
        '商': 'shang', '业': 'ye', '垂': 'chui', '直': 'zhi', '垂': 'chui',
        '直': 'zhi', '领': 'ling', '域': 'yu', '互': 'hu', '动': 'dong',
        '数': 'shu', '字': 'zi', '经': 'jing', '济': 'ji', '转': 'zhuan',
        '型': 'xing', '中': 'zhong', '国': 'guo', '美': 'mei', '国': 'guo',
        '中': 'zhong', '文': 'wen', '英': 'ying', '双': 'shuang', '语': 'yu',
        '多': 'duo', '语': 'yu', '言': 'yan', '翻': 'fan', '译': 'yi',
        '图': 'tu', '文': 'wen', '生': 'sheng', '成': 'cheng', '视': 'shi',
        '觉': 'jue', '文': 'wen', '本': 'ben', '图': 'tu', '片': 'pian',
        '像': 'xiang', '识': 'shi', '别': 'bie', '主': 'zhu', '播': 'bo',
        '主': 'zhu', '持': 'chi', '人': 'ren', '观': 'guan', '众': 'zhong',
        '粉': 'fen', '丝': 'si', '关': 'guan', '注': 'zhu', '评': 'ping',
        '论': 'lun', '播': 'bo', '放': 'fang', '赞': 'zan', '转': 'zhuan',
        '发': 'fa', '分': 'fen', '享': 'xiang', '账': 'zhang', '号': 'hao',
        '帐': 'zhang', '平': 'ping', '台': 'tai', '视': 'shi', '频': 'pin',
        '自': 'zi', '动': 'dong', '化': 'hua', '流': 'liu', '水': 'shui',
        '线': 'xian', '效': 'xiao', '果': 'guo', '评': 'ping', '测': 'ce',
        '试': 'shi', '研': 'yan', '发': 'fa', '版': 'ban', '本': 'ben',
        '测': 'ce', '试': 'shi', '稳': 'wen', '定': 'ding', '优': 'you',
        '化': 'hua', '发': 'fa', '布': 'bu', '正': 'zheng', '式': 'shi',
        '上': 'shang', '线': 'xian', '部': 'bu', '署': 'shu', '升': 'sheng',
        '级': 'ji', '叠': 'die', '代': 'dai', '换': 'huan', '删': 'shan',
        '除': 'chu', '归': 'gui', '档': 'dang', '存': 'cun', '储': 'chu',
        '移': 'yi', '动': 'dong', '清': 'qing', '理': 'li', '输': 'shu',
        '出': 'chu', '列': 'lie', '清': 'qing', '清': 'qing', '单': 'dan',
    }
    return _pinyin_map.get(ch, '')


# ====== 核心命名函数 ======

def make_slug(text: str, max_len: int = 40) -> str:
    """
    将文本转为文件名安全的 slug
    
    Args:
        text: 原始文本（支持中英文混合）
        max_len: 最大长度
    
    Returns:
        小写下划线分隔的 slug
    
    Example:
        "2026年AI视频工具最新进展" -> "2026nian_ai_shipin_gongju_zui_xin_jinzhan"
    """
    slug = _simple_slug(text)
    # 去除连续下划线，截断
    slug = re.sub(r'_+', '_', slug)
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip('_')
    return slug


def make_topic_slug(topic: str, date_str: Optional[str] = None) -> str:
    """
    生成主题 slug（带日期）
    
    Example:
        make_topic_slug("AI推荐系统最新进展", "2026-04-06")
        -> "ai_tuijian_xitong_2026-04-06"
    """
    slug = make_slug(topic)
    if date_str:
        # 移除日期中的横线，避免双重分隔
        date_clean = date_str.replace('-', '')
        return f'{slug}_{date_clean}'
    return slug


def make_date_prefix(date_str: Optional[str] = None) -> str:
    """
    生成日期前缀（格式：YYYYMMDD）
    """
    if date_str:
        return date_str.replace('-', '')
    return datetime.now().strftime('%Y%m%d')


def make_seq(seq: int, total: Optional[int] = None) -> str:
    """
    生成序号字符串
    
    Args:
        seq: 当前序号（从1开始）
        total: 总数（用于决定位数）
    
    Example:
        make_seq(1, 9)  -> "01"
        make_seq(10, 99) -> "10"
    """
    if total and total >= 100:
        return f'{seq:03d}'
    return f'{seq:02d}'


def build_filename(prefix: str,
                   topic: str,
                   seq: int,
                   suffix: str = '',
                   date_str: Optional[str] = None,
                   ext: str = 'mp4') -> str:
    """
    统一文件命名构建器
    
    格式：{prefix}_{topic_slug}_{seq:02d}_{date}{suffix}.{ext}
    
    Example:
        build_filename(
            prefix='slide',
            topic='AI推荐系统最新进展',
            seq=1,
            suffix='_intro',
            ext='mp4'
        )
        -> "slide_ai_tuijian_20260406_01_intro.mp4"
    
    Args:
        prefix: 文件类型前缀（slide/video/audio/content/subtitle/grid/script）
        topic: 视频主题
        seq: 序号
        suffix: 类型后缀（_intro/_main/_outro/_transition/_final/_cover）
        date_str: 日期（YYYY-MM-DD），默认今天
        ext: 文件扩展名
    
    Returns:
        标准化的文件名
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    date_code = date_str.replace('-', '')  # YYYYMMDD
    topic_slug = make_slug(topic, max_len=35)
    seq_str = make_seq(seq)
    
    # 组装
    parts = [prefix, topic_slug, date_code, seq_str]
    if suffix:
        # 确保后缀以 _ 开头
        suffix = suffix.lstrip('_')
        parts.append(suffix)
    
    filename = '_'.join(parts)
    return f'{filename}.{ext}'


# ====== 过渡效果命名 ======

def build_transition_filename(base_topic: str,
                              from_seq: int,
                              to_seq: int,
                              transition_type: str = 'crossfade',
                              date_str: Optional[str] = None) -> str:
    """
    多视频拼接过渡文件名
    
    Example:
        build_transition_filename("AI视频", from_seq=1, to_seq=2, transition_type='fade')
        -> "transition_ai_shipin_01_to_02_fade_20260406.mp4"
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    date_code = date_str.replace('-', '')
    topic_slug = make_slug(base_topic, max_len=30)
    
    transition_types = {
        'crossfade': 'xfade',
        'fade': 'fade',
        'dissolve': 'diss',
        'wipe': 'wipe',
        'slide': 'slide',
        'zoom': 'zoom',
    }
    abbr = transition_types.get(transition_type, 'xfade')
    
    return f'transition_{topic_slug}_{from_seq:02d}_to_{to_seq:02d}_{abbr}_{date_code}.mp4'


# ====== 输出文件清单 ======

def make_output_manifest(topic: str,
                         num_slides: int,
                         output_dir: str,
                         date_str: Optional[str] = None) -> Dict:
    """
    生成完整输出文件清单
    
    返回每个文件的路径、类型、命名
    
    Returns:
        manifest 字典，示例：
        {
            'topic': 'AI推荐系统最新进展',
            'date': '2026-04-06',
            'files': {
                'slide_cover': '/path/to/slide_ai_20260406_00_cover.mp4',
                'slide_01': '/path/to/slide_ai_20260406_01.mp4',
                ...
                'audio_full': '/path/to/audio_script_ai_20260406.wav',
                'grid_preview': '/path/to/grid_preview_ai_20260406.png',
            }
        }
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    output_dir = Path(output_dir)
    
    manifest = {
        'topic': topic,
        'topic_slug': make_slug(topic),
        'date': date_str,
        'date_code': date_str.replace('-', ''),
        'num_slides': num_slides,
        'output_dir': str(output_dir),
        'files': {},
    }
    
    # 封面
    cover_name = build_filename('slide', topic, 0, suffix='cover', date_str=date_str)
    manifest['files']['slide_cover'] = str(output_dir / cover_name)
    
    # 内容页
    for i in range(1, num_slides + 1):
        key = f'slide_{i:02d}'
        name = build_filename('slide', topic, i, date_str=date_str)
        manifest['files'][key] = str(output_dir / name)
    
    # 完整视频
    full_name = build_filename('video', topic, 0, suffix='final', date_str=date_str)
    manifest['files']['video_full'] = str(output_dir / full_name)
    
    # 过渡片段
    for i in range(1, num_slides):
        key = f'transition_{i:02d}_{i+1:02d}'
        name = build_transition_filename(topic, i, i + 1, 'crossfade', date_str)
        manifest['files'][key] = str(output_dir / name)
    
    # 完整音频
    audio_name = build_filename('audio', topic, 0, suffix='full', date_str=date_str).replace('.mp4', '.wav')
    manifest['files']['audio_full'] = str(output_dir / audio_name)
    
    # TTS分段
    for i in range(1, num_slides + 1):
        key = f'tts_{i:02d}'
        name = build_filename('tts', topic, i, date_str=date_str).replace('.mp4', '.mp3')
        manifest['files'][key] = str(output_dir / name)
    
    # 字幕
    srt_name = build_filename('subtitle', topic, 0, suffix='full', date_str=date_str).replace('.mp4', '.srt')
    manifest['files']['subtitle_srt'] = str(output_dir / srt_name)
    
    # 全景网格
    grid_name = f'grid_{make_slug(topic)}_{date_str.replace("-","")}.png'
    manifest['files']['grid_preview'] = str(output_dir / grid_name)
    
    # 脚本
    script_name = f'script_{make_slug(topic)}_{date_str.replace("-","")}.md'
    manifest['files']['script_md'] = str(output_dir / script_name)
    
    return manifest


def print_manifest(manifest: Dict) -> None:
    """打印 manifest 摘要"""
    print(f'\n📋 输出文件清单 ({manifest["topic"]})')
    print(f'   日期：{manifest["date"]} | 片段数：{manifest["num_slides"]}')
    print(f'   输出目录：{manifest["output_dir"]}')
    print()
    
    categories = {
        '🎬 视频片段': [k for k in manifest['files'] if k.startswith('slide_')],
        '🎞️ 过渡效果': [k for k in manifest['files'] if k.startswith('transition_')],
        '🎵 音频': [k for k in manifest['files'] if k.startswith('tts_') or k == 'audio_full'],
        '📝 字幕': [k for k in manifest['files'] if k.startswith('subtitle_')],
        '🖼️ 其他': [k for k in manifest['files']
                    if not any(k.startswith(p) for p in ['slide_', 'transition_', 'tts_', 'subtitle_'])],
    }
    
    for cat, keys in categories.items():
        if keys:
            print(f'  {cat}:')
            for k in keys:
                v = manifest['files'][k]
                fname = os.path.basename(v)
                print(f'    [{k}] {fname}')
            print()


# ====== CLI ======

if __name__ == '__main__':
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='video-auto 文件命名工具')
    parser.add_argument('--topic', required=True, help='视频主题')
    parser.add_argument('--slides', type=int, default=9, help='片段数量')
    parser.add_argument('--output-dir', default='/workspace/agents/video-auto/video',
                        help='输出目录')
    parser.add_argument('--date', help='日期 YYYY-MM-DD（默认今天）')
    parser.add_argument('--json', help='导出 JSON manifest 路径')
    
    args = parser.parse_args()
    
    manifest = make_output_manifest(args.topic, args.slides, args.output_dir, args.date)
    print_manifest(manifest)
    
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        print(f'\n💾 Manifest 已保存: {args.json}')
    
    # 演示：生成几个文件名示例
    print('\n📦 文件名示例:')
    print(f"  封面：  {build_filename("slide", args.topic, 0, "cover")}")
    print(f"  内容1： {build_filename("slide", args.topic, 1)}")
    print(f"  内容5： {build_filename("slide", args.topic, 5)}")
    print(f"  最终：  {build_filename("video", args.topic, 0, "final")}")
    print(f"  过渡1→2：{build_transition_filename(args.topic, 1, 2, "fade")}")
