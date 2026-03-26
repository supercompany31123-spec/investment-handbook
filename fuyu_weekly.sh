#!/bin/bash

# 富宇活動週報腳本
# 每週日早上 08:00 執行

WORKDIR="/Users/wuxiaoyin/.openclaw/workspace"
LOGFILE="$WORKDIR/fuyu_weekly.log"
SCREENSHOT="$WORKDIR/fuyu_weekly.png"

echo "$(date): 開始執行富宇活動週報" >> $LOGFILE

# 打開網頁
open "https://www.fu-yu.com/event"

# 等待頁面載入
sleep 5

# 截圖
/usr/sbin/screencapture -x $SCREENSHOT

echo "$(date): 截圖完成" >> $LOGFILE

# 這裡會由 subagent 分析並發送結果到 Discord
echo "$(date): 等待分析..." >> $LOGFILE
