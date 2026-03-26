#!/bin/bash
# Discord message sender for webhook reminder

CHANNEL_ID="1481480532347846778"
MESSAGE="🦞 記得去 Discord 伺服器設定取得 Webhook URL，這樣才能自動發送富宇活動週報喔！"
TOKEN="MTQ4MTI3NTg2MjYxMDYwODI4NQ.GFMBXg.FbVHlCk4P-dpT_SMR6BUj2UzNN5Ahm_HjTpUVA"

curl -s -X POST "https://discord.com/api/v10/channels/${CHANNEL_ID}/messages" \
    -H "Authorization: Bot ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"content\": \"${MESSAGE}\"}"

echo ""
echo "Message sent at $(date)"
