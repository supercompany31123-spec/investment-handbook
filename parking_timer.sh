#!/bin/bash
# 等待到 2026-03-18 00:01:00

TARGET_DATE="2026-03-18 00:01:00"
TARGET_EPOCH=$(date -j -f "%Y-%m-%d %H:%M:%S" "$TARGET_DATE" +%s)
NOW_EPOCH=$(date +%s)

WAIT_SECONDS=$((TARGET_EPOCH - NOW_EPOCH))

if [ $WAIT_SECONDS -gt 0 ]; then
    echo "等待 $WAIT_SECONDS 秒 until $TARGET_DATE"
    sleep $WAIT_SECONDS
fi

# 运行脚本
cd /Users/wuxiaoyin/.openclaw/workspace
source venv/bin/activate
python3 parking_rush.py

# 截图
sleep 5
caffeinate -u -t 1
sleep 1
peekaboo move 500,400
peekaboo click --coords 500,400
sleep 3
/usr/sbin/screencapture -x ~/.openclaw/media/outbound/parking_result.png

# 发送截图
openclaw message send --channel discord --target 1481949086306406400 --media ~/.openclaw/media/outbound/parking_result.png

echo "完成！"
