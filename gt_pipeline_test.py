#!/workspace/venv-uv/bin/python3
import sys, os, json, soundfile as sf

# 音频信息
audio_file = '/workspace/AI-music-score-featch/test_audio/fb89949e-2e61-464b-bfac-22e7750db3fa.wav'
data, sr = sf.read(audio_file)
duration = len(data) / sr

print(f"=== AI Guitar Tab 扒谱测试 ===")
print(f"音频: {audio_file}")
print(f"采样率: {sr}Hz | 时长: {duration:.2f}秒 | 形状: {data.shape}")
print()

# 设置Python路径
sys.path.insert(0, '/workspace/AI-music-score-featch/backend')

# 导入pipeline
try:
    from core.pipeline import transcribe_audio
    print("Pipeline模块导入: ✅")
except Exception as e:
    print(f"Pipeline模块导入: ❌ {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# 创建输出目录
os.makedirs('/workspace/AI-music-score-featch/backend/test_out', exist_ok=True)

# 执行转录
print("开始转录...")
try:
    result = transcribe_audio('/workspace/AI-music-score-featch/backend/test_out', {}, 'test-001')
    print("Pipeline执行: ✅")
    print(f"结果keys: {list(result.keys())}")
    for k, v in result.items():
        print(f"  {k}: {str(v)[:200]}")
except Exception as e:
    print(f"Pipeline执行: ❌ {e}")
    import traceback; traceback.print_exc()

print()
print("=== 完成 ===")
