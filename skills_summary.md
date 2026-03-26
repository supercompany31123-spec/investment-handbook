# 🦞 龍蝦技能總覽

## 📋 技能列表

| 技能名稱 | 功用 |
|---------|------|
| **Peekaboo** | 👀 截圖、自動化操作 macOS UI、點擊移動滑鼠 |
| **elite-longterm-memory** | 🧠 長期記憶系統、向量搜尋、雲端備份 |
| **find-skills** | 🔍 搜尋和發現新技能 |
| **gog** | 📧 Gmail、Google Calendar、Drive、Sheets、Docs 管理 |
| **mac-tts** | 🎙️ 文字轉語音、用 Mac 內建聲音說話 |
| **openai-whisper** | 🎤 語音轉文字（本地端，無需 API Key）|
| **openclaw-tavily-search** | 🌐 網路搜尋（需要 Tavily API Key）|
| **proactive-agent-lite** | 🚀 主動式 Agent 行為模式 |
| **self-improving-agent** | 📝 學習錯誤、持續改進 |
| **skill-vetter** | 🔒 資安審查、安裝前檢查技能安全性 |
| **sonos** | 🔊 控制 Sonos 喇叭（播放、暫停、音量）|
| **weather** | ☁️ 查詢天氣（免費、無需 API Key）|

---

## 📱 常用指令快速查詢

### 截圖
```
peekaboo image --mode screen --path ~/.openclaw/media/outbound/screenshot.png --retina
```

### 天氣
```
weather 台北
```

### 發語音
```
say -v "Meijia" "你好！"
```

### Gmail
```
gog gmail list
gog gmail send --to "xxx@email.com" --subject "主旨" --body "內容"
```

---

## ⚙️ 需要額外設定的技能

| 技能 | 需要的設定 |
|-----|-----------|
| gog | Google OAuth 認證 ✅ 已完成 |
| openclaw-tavily-search | 需要 Tavily API Key |
| sonos | 需要安裝 sonoscli |
| openai-whisper | 需要 `brew install openai-whisper` |

---

*最後更新：2026-03-19*
