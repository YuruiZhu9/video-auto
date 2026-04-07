#!/bin/bash
# Install basic_pitch then run full pipeline test
echo "安装basic_pitch..."
uv pip install --python /workspace/venv-uv/bin/python3 "basic-pitch>=2024.2.2" 2>&1 | tail -3

echo "运行测试..."
/workspace/venv-uv/bin/python3 /workspace/gt_pipeline_test.py > /workspace/gt_test_result.txt 2>&1
echo "结果:"
cat /workspace/gt_test_result.txt
