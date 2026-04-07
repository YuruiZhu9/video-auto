#!/bin/bash
# Set PYTHONPATH to parent dir so "backend.main" import works
export PYTHONPATH=/workspace/AI-music-score-featch
cd /workspace/AI-music-score-featch

echo "=== AI Guitar Tab 扒谱测试 ==="
echo "Python: $(which python3)"

/workspace/venv-uv/bin/python3 -u /workspace/gt_test_final.py > /workspace/gt_result.txt 2>&1
echo "EXIT:$?"
echo ""
cat /workspace/gt_result.txt
