# macOS 截圖喚醒螢幕教學

## 問題
當顯示器進入睡眠或未喚醒時，截圖只會抓到桌面牆紙，看不到應用程式視窗。

## 解決方案
每次截圖前先喚醒螢幕。

## 步驟

### 1. 喚醒螢幕 + 截圖（推薦）
```bash
# 喚醒螢幕
caffeinate -u -t 1

# 移動滑鼠並點擊
peekaboo move 500,500
peekaboo click --coords 500,500

# 截圖（使用 Mac 內建指令）
/usr/sbin/screencapture -x /tmp/screenshot.png

# 複製到允許的目錄
cp /tmp/screenshot.png ~/.openclaw/media/outbound/screenshot.png
```

### 2. 發送到 Discord
```bash
openclaw message send --channel discord --target 頻道ID --media ~/.openclaw/media/outbound/screenshot.png
```

## 關鍵點
- 必須先執行 `caffeinate -u -t 1` 喚醒螢幕
- 必須移動滑鼠 + 點擊讓畫面完全喚醒
- 等待 1-2 秒後再截圖
- 使用 `/usr/sbin/screencapture` 而非 peekaboo 截圖

---
*Last updated: 2026-03-16*
