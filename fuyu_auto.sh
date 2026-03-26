#!/bin/bash

# 富宇活动週报 - 每周日 08:00 自动执行

WORKDIR="/Users/wuxiaoyin/.openclaw/workspace"
WEBHOOK_URL="https://discord.com/api/webhooks/1483111152182362272/pNUOad9ckhSdqdXMC2aXkfly42X_yageo2MHIrEvCMFmzxV4ZwXqIcFR1Qezr40Ng78C"
SCREENSHOT="$WORKDIR/fuyu_auto.png"
LOGFILE="$WORKDIR/fuyu_auto.log"

echo "$(date): 开始执行富宇活动週报" >> $LOGFILE

# 打开网页
open "https://www.fu-yu.com/event"

# 等待页面加载
sleep 6

# 截屏
/usr/sbin/screencapture -x $SCREENSHOT
echo "$(date): 截图完成" >> $LOGFILE

# 发送图片到 Discord
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$SCREENSHOT" \
  -F "content=🦞 富宇活动週报 - 报名的活动有哪些？"

echo "$(date): 已发送到 Discord" >> $LOGFILE
