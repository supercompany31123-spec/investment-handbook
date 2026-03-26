# Stock Deep Research Skill

深度股票研究技能 - 每日 20:00 自動執行

## 功能
- 技術分析：K線 + MA5/10/20 + MACD + RSI 半年圖表
- 新聞摘要：從玩股網、FT中文網取得財經新聞
- 市場影響分析：判斷新聞對類股/大盤的影響
- Discord 自動發送

## 使用方式
```
python3 /Users/wuxiaoyin/.openclaw/workspace/skills/stock-deep-research/stock_deep.py
```

## 腳本位置
`/Users/wuxiaoyin/.openclaw/workspace/skills/stock-deep-research/stock_deep.py`

## 設定
- Discord Token: `MTQ4MTI3NTg2MjYxMDYwODI4NQ.GFMBXg.FbVHlCk4P-dpT_SMR6BUj2UzNN5Ahm_HjTpUVA`
- Channel ID: `1481483157575569409`
- 追蹤股票: 2330.TW (台積電), 6223.TWO (旺矽), 4772.TWO (台特化)

## 新聞來源
- 玩股網 API: `https://www.wantgoo.com/news/category/頭條/list`
- 文章內容: `https://www.wantgoo.com/news/{id}/detail`
- FT中文網 RSS: `https://www.ftchinese.com/rss/news`

## Cron Job ID
`290d9bcf-ae0a-4fb9-84f4-a1c28c61d79e`
