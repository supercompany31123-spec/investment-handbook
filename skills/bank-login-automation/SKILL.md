---
name: bank-login-automation
description: 銀行信用卡活動登錄自動化。當需要執行玉山銀行或國泰世華銀行的信用卡活動登錄時使用此技能。包含自動截圖回傳 Discord、驗證碼輸入、活動關鍵字匹配等流程。
---

# Bank Login Automation

## 腳本位置

`/Users/wuxiaoyin/.openclaw/workspace/`

## 腳本清單

### 玉山銀行

| 帳戶 | 腳本 | 版本 |
|------|------|------|
| TMD | `esun_rush_v4_TMD.py` | v4 ✅ |
| HY | `esun_rush_v4_HY.py` | v4 ✅ |

- [玉山銀行 v4 詳細流程](esun_v4.md)

### 國泰世華銀行

| 帳戶 | 腳本 | 版本 |
|------|------|------|
| TMD | `cathay_rush_v4_TMD.py` | v4 ✅ |
| HY | `cathay_rush_v4_HY.py` | v4 ✅ |
| TEST | `cathay_rush_v4_TEST.py` | v4 ✅ |

- [國泰世華銀行 v4 詳細流程](cathay_v4.md)

## 驗證碼格式

```
驗證碼-時間-活動關鍵字
例如：12345-17:00:01.000-壽險
```

### 玉山
時間代表「送出」時間

### 國泰
時間代表「刷新頁面」時間

## Discord 頻道

- 頻道 ID：`1481949086306406400`
