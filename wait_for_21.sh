#!/bin/bash
# 等待到 21:00

while true; do
    current_time=$(date +%H:%M)
    if [ "$current_time" = "21:00" ]; then
        break
    fi
    sleep 30
done

# 時間到了，發送訊息
echo "Time reached 21:00, sending message..."
