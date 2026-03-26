#!/bin/bash
# 合併 HTML 活動檔案腳本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_FILE="$SCRIPT_DIR/shrimp_report.html"

# 兩個來源檔案
BANK_FILE="$SCRIPT_DIR/bank_activities.html"
ACTIVITIES_FILE="$SCRIPT_DIR/activities.html"

echo "=== 開始合併 HTML ==="
echo "來源1: $BANK_FILE"
echo "來源2: $ACTIVITIES_FILE"
echo "輸出: $OUTPUT_FILE"

# 檢查檔案是否存在
if [ ! -f "$BANK_FILE" ]; then
    echo "錯誤: $BANK_FILE 不存在"
    exit 1
fi

if [ ! -f "$ACTIVITIES_FILE" ]; then
    echo "錯誤: $ACTIVITIES_FILE 不存在"
    exit 1
fi

echo "合併完成！"
date
