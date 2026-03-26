---
name: esun-login-automation
description: 玉山銀行信用卡活動登錄自動化腳本（v4版本）。執行玉山銀行刷信用卡活動的自動化登錄流程。
---

# 玉山銀行登錄自動化 v4

## 腳本位置

`/Users/wuxiaoyin/.openclaw/workspace/esun_rush_v4_TMD.py`
`/Users/wuxiaoyin/.openclaw/workspace/esun_rush_v4_HY.py`

## 帳號資訊

| 帳戶 | 身份證 | 生日 |
|------|--------|------|
| TMD | A129013019 | 0760419 |
| HY | F226228024 | 0750506 |

## 執行環境

```bash
cd /Users/wuxiaoyin/.openclaw/workspace
source venv/bin/activate
python3 esun_rush_v4_TMD.py   # 玉山 TMD
python3 esun_rush_v4_HY.py     # 玉山 HY
```

## v4 自動化流程

### 詳細步驟

1. **開啟 Chrome 並打開玉山活動頁面**
   - URL: `https://card.esunbank.com.tw/EsunCreditweb/txnservice/identify?PRJCD=ALLACTIV#b`
   - 使用無痕模式開啟

2. **填入登入資訊**
   - 身份證字號（自動填入）
   - 出生年月日（格式：MMDDYY，自動填入）

3. **勾選同意選項**
   - 勾選「agree-01」
   - 勾選「agree-02」

4. **截圖並發送到 Discord**
   - 使用 `screencapture` 截圖
   - 自動發送到 Discord 頻道 `1481949086306406400`
   - 等待使用者提供驗證碼

5. **等待驗證碼檔案**
   - 監控 `/tmp/captcha.txt` 檔案
   - 格式：`驗證碼-送出時間-活動關鍵字`
   - 例如：`12345-15:59:59.800-壽險`

6. **時間到自動點擊送出**
   - 精確等到指定時間（精準到毫秒）
   - 點擊「送出」按鈕

7. **查找並點擊活動**
   - 在頁面中搜尋符合關鍵字的活動按鈕
   - 點擊「登錄」按鈕

8. **等待成功彈窗**
   - 等待 3 秒讓成功彈窗出現

9. **截圖並發送到 Discord**
   - 截圖記錄結果
   - 自動發送到 Discord

10. **關閉 Chrome 並結束程式**
    - 等待 2 秒
    - 關閉 Chrome 瀏覽器
    - 結束 Python 程式
    - Terminal 自然關閉

## 驗證碼格式

```
驗證碼-送出時間-活動關鍵字
```

### 範例

```
12345-15:59:59.800-壽險
45678-16:00:01.000-分期
```

### 時間格式說明

- `HH:MM:SS.mmm`
- `HH` = 小時（24小時制）
- `MM` = 分鐘
- `SS` = 秒鐘
- `mmm` = 毫秒

## 執行方式（透過 OpenClaw 控制 Terminal）

### 標準流程

1. 確保 `/tmp/captcha.txt` 是空的
2. 讓 OpenClaw 開啟 Terminal 並執行腳本
3. 腳本會自動截圖發到 Discord
4. 使用者提供驗證碼資訊
5. OpenClaw 寫入驗證碼到 `/tmp/captcha.txt`
6. 腳本自動完成後續流程

### 終止舊程式

```bash
pkill -9 -f "python.*esun"
pkill -9 -f "chromedriver"
```

### 執行新程式

```bash
osascript -e 'tell application "Terminal" to activate'
osascript -e 'tell application "Terminal" to do script "cd ~/.openclaw/workspace && source venv/bin/activate && python3 esun_rush_v4_TMD.py" in front window'
```

## 常見問題

### Q: 為什麼要找「壽險」關鍵字？
A: 每個活動有不同的關鍵字，需要根據實際活動名稱填寫。例如「壽險保費」、「分期」、「蝦皮」等。

### Q: 時間來不及等到怎麼辦？
A: 可以選擇未來的時間點，例如 `23:59:59.000`，有足夠的時間輸入驗證碼。

### Q: 為什麼要等待 3 秒？
A: 為了截圖到成功登錄的彈窗，需要等待系統反應。

## 版本歷史

- **v4**：最終版，完整流程優化
  - 加入等待 3 秒截圖成功彈窗
  - 2 秒後關閉 Chrome
  - 自然結束程式，Terminal 自動關閉

- **v3**：加入 Discord 通知

- **v2**：加入檔案監控

- **v1**：基礎版本
