---
name: cathay-login-automation
description: 國泰世華銀行信用卡活動登錄自動化腳本（v4版本）。執行國泰世華銀行信用卡活動的自動化登錄流程。
---

# 國泰世華銀行登錄自動化 v4

## 腳本位置

`/Users/wuxiaoyin/.openclaw/workspace/cathay_rush_v4_TMD.py`
`/Users/wuxiaoyin/.openclaw/workspace/cathay_rush_v4_HY.py`
`/Users/wuxiaoyin/.openclaw/workspace/cathay_rush_v4_TEST.py`

## 帳號資訊

| 帳戶 | 身份證 | 生日 |
|------|--------|------|
| TMD | A129013019 | 19870419 |
| HY | F226228024 | 19860506 |
| TEST | F125691441 | 19830904 |

## 執行環境

```bash
cd /Users/wuxiaoyin/.openclaw/workspace
source venv/bin/activate
python3 cathay_rush_v4_TMD.py   # 國泰 TMD
python3 cathay_rush_v4_HY.py     # 國泰 HY
python3 cathay_rush_v4_TEST.py   # 國泰 TEST
```

## v4 自動化流程

### 詳細步驟

1. **開啟 Chrome 並打開國泰頁面**
   - URL: `https://www.cathaybk.com.tw/promotion/`
   - 使用無痕模式開啟

2. **填入登入資訊**
   - 身份證字號（自動填入）
   - 出生年月日（格式：YYYYMMDD，自動填入）

3. **勾選同意選項**
   - 勾選所有 `.checkbox.beValidate` 選項

4. **截圖並發送到 Discord**
   - 使用 `screencapture` 截圖
   - 自動發送到 Discord 頻道 `1481949086306406400`
   - 等待使用者提供驗證碼

5. **等待驗證碼檔案**
   - 監控 `/tmp/captcha.txt` 檔案
   - 格式：`驗證碼-刷新時間-活動關鍵字`
   - 例如：`12345-15:59:59.800-蝦皮`

6. **時間到自動刷新頁面**
   - 精確等到指定時間（精準到毫秒）
   - **刷新頁面**（國泰特色，與玉山不同）

7. **查找並點擊活動**
   - 在頁面中搜尋符合關鍵字的活動
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
驗證碼-刷新時間-活動關鍵字
```

### 範例

```
12345-15:59:59.800-蝦皮
45678-16:00:01.000-台塑
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
pkill -9 -f "python.*cathay"
pkill -9 -f "chromedriver"
```

### 執行新程式

```bash
osascript -e 'tell application "Terminal" to activate'
osascript -e 'tell application "Terminal" to do script "cd ~/.openclaw/workspace && source venv/bin/activate && python3 cathay_rush_v4_HY.py" in front window'
```

### 終止+執行一鍵指令

```bash
pkill -9 -f "python.*cathay" 2>/dev/null; pkill -9 -f "chromedriver" 2>/dev/null; sleep 1 && echo "" > /tmp/captcha.txt && osascript -e 'tell application "Terminal" to activate' && osascript -e 'tell application "Terminal" to do script "cd ~/.openclaw/workspace && source venv/bin/activate && python3 cathay_rush_v4_HY.py" in front window'
```

## 與玉山的差異

| 項目 | 玉山 | 國泰 |
|------|------|------|
| 網址 | 玉山銀行活動頁面 | 國泰世華活動頁面 |
| 驗證後動作 | 點擊「送出」按鈕 | **刷新頁面** |
| 活動選取 | CSS selector `a.fitBtn.btns` | 多層 DOM 結搆 `.link.campaign-name` + 按鈕 |

## 常見問題

### Q: 國泰為什麼要刷新頁面？
A: 國泰的機制是驗證後需要刷新頁面才會顯示最新的活動列表。

### Q: 時間來不及等到怎麼辦？
A: 可以選擇未來的時間點，例如 `23:59:59.000`，有足夠的時間輸入驗證碼。

### Q: 為什麼要等待 3 秒？
A: 為了截圖到成功登錄的彈窗，需要等待系統反應。

## 錯誤訊息

- **找不到活動** → 活動關鍵字沒有匹配到
- **有找到活動，但找不到按鈕** → 找到了活動但按鈕選取失敗

## 版本歷史

- **v4**：最終版，完整流程優化
  - 與玉山 v4 同步流程
  - 加入等待 3 秒截圖成功彈窗
  - 2 秒後關閉 Chrome
  - 自然結束程式，Terminal 自動關閉
  - 更詳細的錯誤訊息

- **v3**：加入 Discord 通知

- **v2**：加入檔案監控

- **v1**：基礎版本
