#!/bin/bash
exec > /tmp/gt_real_log.txt 2>&1
/workspace/venv-uv/bin/python3 /workspace/gt_real_test.py >> /tmp/gt_real_log.txt 2>&1
echo "DONE at $(date)" >> /tmp/gt_real_log.txt
