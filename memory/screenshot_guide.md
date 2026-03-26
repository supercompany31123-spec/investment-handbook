# 截圖標準流程

## 問題
Mac 顯示器關閉或睡眠時，截圖只會顯示桌面牆紙，看不到實際畫面。

## 解決方案
每次截圖前必須先喚醒螢幕！

## 標準截圖流程（非常重要！）

```bash
# 1. 喚醒螢幕
caffeinate -u -t 1

# 2. 移動滑鼠並點擊
peekaboo move 500,500
peekaboo click --coords 500,500

# 3. 等待 1-2 秒
sleep 1

# 4. 截圖
/usr/sbin/screencapture -x /tmp/screenshot.png

# 5. 複製到允許的目錄
cp /tmp/screenshot.png ~/.openclaw/media/outbound/screenshot.png
```

## 簡化版（推薦）
```bash
caffeinate -u -t 1 && peekaboo move 500,500 && peekaboo click --coords 500,500 && sleep 1 && /usr/sbin/screencapture -x ~/.openclaw/media/outbound/screenshot.png
```

## 為什麼要這樣？
- macOS 顯示器進入節能模式後，截圖只會抓到桌面
- 需要先喚醒才能抓到應用程式視窗

---
*Last updated: 2026-03-19*
