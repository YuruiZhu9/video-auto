#!/bin/bash
openclaw cron run 29c8ba5c-0d8e-464e-bd27-e4aa89012b73 --timeout 90000 2>&1
echo "---T2---"
openclaw cron run 49eab175-9b4f-45d9-bd80-36c954f99ef7 --timeout 90000 2>&1
echo "---T3---"
openclaw cron run f5afdfd6-068f-4518-80f8-fdf5f8741c1b --timeout 90000 2>&1
echo "=== DONE ==="
