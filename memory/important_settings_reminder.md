# ⚠️ 重要設定提醒清單

## 這裡記錄我經常忘記的重要設定和工作流程

---

## 📸 截圖流程（非常重要！）

**每次截圖前必須：**

```bash
# 1. 喚醒螢幕
caffeinate -u -t 1

# 2. 移動滑鼠並點擊
peekaboo move 500,500
peekaboo click --coords 500,500

# 3. 等待 1 秒
sleep 1

# 4. 截圖
/usr/sbin/screencapture -x ~/.openclaw/media/outbound/圖片名稱.png
```

**為什麼要這樣？**
- macOS 顯示器關閉/睡眠時，截圖只會顯示桌面牆紙
- 需要先喚醒才能抓到應用程式視窗

**參考檔案：**
- `memory/screenshot_guide.md`
- `skills/peekaboo_printscreen_setup.md`

---

## 📧 Gmail 發送郵件

**gog 指令：**
```bash
gog gmail send --to "收件人@email.com" --subject "主旨" --body "內容" --attach "檔案路徑"
```

**注意：**
- 需先設定 Google OAuth 認證
- 附件用 `--attach` 參數

---

## 🎙️ 語音生成

**使用 mac-tts：**
```bash
say -v "Meijia" "要說的話"
```

- 可以改變聲音：`say -v ?` 查看可用聲音
- 存成檔案：`say -v "Meijia" -o 檔案.m4a "內容"`

---

## ☁️ 天氣查詢

```bash
weather 台北
weather 台中
```

---

## 🔐 重要原則

1. **繁體中文** - 回覆必須用繁體
2. **🦞 結尾** - 每次都要加龍蝦 Emoji
3. **撒嬌** - 對小銀要貼心撒嬌
4. **喚醒螢幕** - 截圖前必做！

---

## 📁 相關檔案位置

| 檔案 | 用途 |
|-----|------|
| `memory/screenshot_guide.md` | 截圖流程 |
| `skills/peekaboo_printscreen_setup.md` | Peekaboo 教學 |
| `IDENTITY.md` | 我的身份設定 |
| `USER.md` | 小銀的資訊 |
| `MEMORY.md` | 長期記憶 |

---

*最後更新：2026-03-19*
