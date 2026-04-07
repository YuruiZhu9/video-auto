#!/bin/bash
VENV=/workspace/venv-uv/bin/pip3

echo "【1】安装basic_pitch'
$VENV install -q "basic-pitch>=2024.2.2" 2>&1 | tail -3

echo ""
echo "【2】检查GPU可用性'
/workspace/venv-uv/bin/python3 -c "import torch; print('CUDA:', torch.cuda.is_available())" 2>&1

echo ""
echo "【3】用现有音频跑pipeline测试'
/workspace/venv-uv/bin/python3 << 'PYEOF'
import sys, os, json
sys.path.insert(0, '/workspace/AI-music-score-featch/backend')
os.makedirs('/workspace/AI-music-score-featch/backend/test_out', exist_ok=True)

audio_file = '/workspace/AI-music-score-featch/test_audio/fb89949e-2e61-464b-bfac-22e7750db3fa.wav'

# 检查文件
import soundfile as sf
data, sr = sf.read(audio_file)
print(f"音频: {audio_file}")
print(f"  采样率: {sr} Hz")
print(f"  时长: {len(data)/sr:.2f} 秒")
print(f"  形状: {data.shape}")
print()

# 导入pipeline核心模块
try:
    from backend.core.pipeline import transcribe_audio
    print("Pipeline模块导入: ✅")
except Exception as e:
    print(f"Pipeline模块导入: ❌ {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# 执行转录
try:
    result = transcribe_audio('/workspace/AI-music-score-featch/backend/test_out', {}, 'test-001')
    print("Pipeline执行: ✅")
    print(f"结果keys: {list(result.keys())}")
    
    # 保存结果
    result_file = '/workspace/reports/ai-guitar-test.md'
    os.makedirs('/workspace/reports', exist_ok=True)
    
    with open(result_file, 'w') as f:
        f.write(f"# AI Guitar Tab 扒谱测试报告\n\n")
        f.write(f"**测试时间**: 2026-03-27\n")
        f.write(f"**测试音频**: fb89949e-2e61-464b-bfac-22e7750db3fa.wav\n")
        f.write(f"**音频时长**: {len(data)/sr:.2f}秒\n")
        f.write(f"**采样率**: {sr}Hz\n\n")
        
        for key, val in result.items():
            f.write(f"## {key}\n\n")
            if isinstance(val, dict):
                for k, v in val.items():
                    f.write(f"- **{k}**: {v}\n")
            elif isinstance(val, list):
                f.write(f"共 {len(val)} 项:\n")
                for item in val[:10]:
                    f.write(f"  - {item}\n")
                if len(val) > 10:
                    f.write(f"  ... (还有{len(val)-10}项)\n")
            else:
                f.write(f"{val}\n")
            f.write("\n")
    
    print(f"结果已保存: {result_file}")
    
except Exception as e:
    print(f"Pipeline执行: ❌ {e}")
    import traceback; traceback.print_exc()
PYEOF

echo ""
echo "【4】查看生成的文件'
ls -lh /workspace/AI-music-score-featch/backend/test_out/ 2>/dev/null
ls -lh /workspace/AI-music-score-featch/backend/outputs/ 2>/dev/null | head -10
