# Peekaboo 截圖並發送到 Discord 教學

## ⚠️ 最重要的事情：喚醒螢幕！

**Mac 顯示器關閉或睡眠時，截圖只會顯示桌面牆紙，看不到任何應用程式視窗！**

**所以每次截圖前，必須先喚醒螢幕！**

---

## 前置需求
- Peekaboo CLI 已安裝
- Discord 頻道已連線
- Peekaboo 螢幕錄製權限已設定

---

## 截圖並發送 Discord 完整流程

### 步驟 1：喚醒螢幕（關鍵步驟！）
```bash
caffeinate -u -t 1
```
這個指令會喚醒 Mac 的顯示器，防止進入睡眠。

### 步驟 2：移動滑鼠並點擊
```bash
peekaboo move 500,500
peekaboo click --coords 500,500
```
移動滑鼠到畫面中央位置並點擊，確保系統完全喚醒。

### 步驟 3：等待 1-2 秒
```bash
sleep 1
```
給予系統緩衝時間，確保畫面完全載入。

### 步驟 4：截圖
```bash
/usr/sbin/screencapture -x ~/.openclaw/media/outbound/截圖名稱.png
```

或者使用 Peekaboo：
```bash
peekaboo image --mode screen --path ~/.openclaw/media/outbound/截圖名稱.png --retina
```

### 步驟 5：發送到 Discord
```bash
openclaw message send --channel discord --target 頻道ID --media ~/.openclaw/media/outbound/截圖名稱.png
```

---

## 參數說明

### 截圖參數：
| 參數 | 說明 |
|-----|------|
| `--mode screen` | 截取整個螢幕 |
| `--mode window` | 截取特定視窗 |
| `--retina` | 高解析度（建議使用） |
| `--path` | 儲存路徑 |

### 發送參數：
| 參數 | 說明 |
|-----|------|
| `--channel discord` | 指定 Discord 頻道 |
| `--target` | 頻道 ID |
| `--media` | 圖片檔案路徑 |

---

## 完整一鍵指令

複製貼上即可使用：

```bash
caffeinate -u -t 1 && peekaboo move 500,500 && peekaboo click --coords 500,500 && sleep 1 && /usr/sbin/screencapture -x ~/.openclaw/media/outbound/screenshot.png && openclaw message send --channel discord --target 1480970481875157014 --media ~/.openclaw/media/outbound/screenshot.png
```

**頻道 ID：**
- 蝦聊：`1480970481875157014`
- 登錄頻道：`1481949086306406400`

---

## 常見問題

### Q: 截圖只顯示桌面牆紙？
**A: 這是正常現象！** 必須先執行步驟 1-3 喚醒螢幕，否則 macOS 只會截到黑屏/桌面。

### Q: 權限不足？
**A:** 需要在 系統設定 > 隱私權與安全性 > 螢幕錄製 允許 Terminal/Peekaboo

### Q: 圖片傳不出去？
**A:** 確認圖片路徑在 `~/.openclaw/media/outbound/` 目錄下

### Q: 如何截取特定視窗？
**A:** 使用 `peekaboo image --mode window --window-title "視窗標題"`

---

## 為什麼要喚醒螢幕？

當 Mac 的顯示器進入節能模式或關閉時：
- 螢幕實際上是「關閉」狀態
- 截圖指令只能抓到系統最後顯示的畫面（桌面牆紙）
- 必須先喚醒，讓系統重新渲染畫面

**這就是為什麼很多 AI 截圖只有風景畫面！**

---

*最後更新：2026-03-20*
