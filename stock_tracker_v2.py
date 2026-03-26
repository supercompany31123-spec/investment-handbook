#!/usr/bin/env python3
# 股票每日追蹤腳本 - 自動傳送到 Discord

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
import re
import urllib3
import sys
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 設定
FONT_PATH = '/System/Library/Fonts/STHeiti Medium.ttc'
BAR_WIDTH = 0.35
BG_COLOR = '#2d2d2d'
STOCKS = [
    ('2330.TW', '台積電'),
    ('6223.TWO', '旺矽'),
    ('4772.TWO', '台特化')
]
PERIOD = "3mo"
DISCORD_TOKEN = "MTQ4MTI3NTg2MjYxMDYwODI4NQ.GFMBXg.FbVHlCk4P-dpT_SMR6BUj2UzNN5Ahm_HjTpUVA"
CHANNEL_ID = "1481483157575569409"

font_prop = FontProperties(fname=FONT_PATH)

def plot_kline(stock_code, stock_name, output_path):
    df = yf.download(stock_code, period=PERIOD, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA10'] = df['Close'].rolling(window=10).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    exp12 = df['Close'].ewm(span=12, adjust=False).mean()
    exp26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp12 - exp26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal']
    
    x = np.arange(len(df))
    
    fig = plt.figure(figsize=(14, 12), facecolor=BG_COLOR)
    gs = fig.add_gridspec(3, 1, height_ratios=[5, 1, 1], hspace=0)
    
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(BG_COLOR)
    for i in range(len(df)):
        open_p, close_p = df['Open'].iloc[i], df['Close'].iloc[i]
        high_p, low_p = df['High'].iloc[i], df['Low'].iloc[i]
        color = '#ff0000' if close_p >= open_p else '#00c000'
        ax1.plot([i, i], [low_p, high_p], color=color, linewidth=0.8)
        ax1.bar(i, abs(close_p - open_p), bottom=min(open_p, close_p), width=BAR_WIDTH, color=color, edgecolor=color)
    ax1.plot(x, df['MA5'].values, color='#FFD700', linewidth=1)
    ax1.plot(x, df['MA10'].values, color='#4169E1', linewidth=1)
    ax1.plot(x, df['MA20'].values, color='#9370DB', linewidth=1)
    ax1.set_title(f'{stock_name} ({stock_code}) K線圖', fontproperties=font_prop, fontsize=14, color='white')
    ax1.set_ylabel('股價', fontproperties=font_prop, color='white')
    legend_elements = [Line2D([0], [0], color='#FFD700', lw=1, label='MA5'), Line2D([0], [0], color='#4169E1', lw=1, label='MA10'), Line2D([0], [0], color='#9370DB', lw=1, label='MA20')]
    ax1.legend(handles=legend_elements, loc='upper left', fontsize=8, facecolor=BG_COLOR, labelcolor='white')
    ax1.grid(True, alpha=0.3, color='gray')
    ax1.set_xlim(-1, len(df))
    ax1.tick_params(axis='x', labelbottom=False)
    ax1.tick_params(axis='y', labelcolor='white')
    for spine in ax1.spines.values(): spine.set_color('white')
    
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.set_facecolor(BG_COLOR)
    hist_data = df['Histogram'].values
    colors_hist = ['#ff0000' if h >= 0 else '#00c000' for h in hist_data]
    ax2.bar(x, hist_data, width=BAR_WIDTH, color=colors_hist, edgecolor='none')
    ax2.plot(x, df['MACD'].values, color='#FFD700', linewidth=1)
    ax2.plot(x, df['Signal'].values, color='#4169E1', linewidth=1)
    ax2.axhline(y=0, color='white', linewidth=0.5)
    ax2.set_ylabel('MACD', fontproperties=font_prop, fontsize=9, color='white')
    legend_elements2 = [Line2D([0], [0], color='#FFD700', lw=1, label='DIF'), Line2D([0], [0], color='#4169E1', lw=1, label='Signal')]
    ax2.legend(handles=legend_elements2, loc='upper left', fontsize=7, facecolor=BG_COLOR, labelcolor='white')
    ax2.grid(True, alpha=0.3, color='gray')
    ax2.tick_params(axis='x', labelbottom=False)
    ax2.tick_params(axis='y', labelcolor='white')
    for spine in ax2.spines.values(): spine.set_color('white')
    
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.set_facecolor(BG_COLOR)
    vol_data = df['Volume'].values
    close_data = df['Close'].values
    colors_vol = ['#00c000' if (i == 0 or close_data[i] >= close_data[i-1]) else '#ff0000' for i in range(len(vol_data))]
    ax3.bar(x, vol_data, width=BAR_WIDTH, color=colors_vol, edgecolor='none')
    ax3.set_ylabel('VOL', fontproperties=font_prop, fontsize=9, color='white')
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}'))
    ax3.tick_params(axis='y', labelcolor='white')
    ax3.set_xlabel('日期', fontproperties=font_prop, color='white')
    ax3.grid(True, alpha=0.3, color='gray')
    ax3.tick_params(axis='x', labelcolor='white')
    for spine in ax3.spines.values(): spine.set_color('white')
    ax3.set_xticks(x[::10])
    ax3.set_xticklabels([d.strftime('%m/%d') for d in df.index[::10]], rotation=45, fontsize=8, color='white')
    
    fig.savefig(output_path, bbox_inches='tight')
    plt.close()
    return df

def get_news(stock_code, stock_name):
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://tw.stock.yahoo.com/quote/{stock_code}/news"
    try:
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        pattern = r'>([^<]*' + stock_code.split('.')[0] + r'[^<]{5,60})<'
        news = re.findall(pattern, resp.text)
        news = [n.strip() for n in news[2:5]] if news else []
        
        if news:
            conclusions = []
            for n in news:
                n = n.replace('【公告】', '').replace('旺矽', '').replace('台特化', '').replace('台積電', '').strip()
                if len(n) > 30:
                    n = n[:30] + '...'
                conclusions.append(n)
            return conclusions
        else:
            return ["目前無重大新聞"]
    except:
        return ["無法取得新聞"]
        return []

def get_price(stock_code):
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://tw.stock.yahoo.com/quote/{stock_code}"
    try:
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        price = re.search(r'"price"\s*:\s*"([^"]+)"', resp.text)
        change = re.search(r'"change"\s*:\s*"([^"]+)"', resp.text)
        return price.group(1) if price else '-', change.group(1) if change else '-'
    except:
        return '-', '-'

def analyze(df, stock_name):
    last_close = df['Close'].iloc[-1]
    ma5 = df['MA5'].iloc[-1]
    ma10 = df['MA10'].iloc[-1]
    ma20 = df['MA20'].iloc[-1]
    macd = df['MACD'].iloc[-1]
    signal = df['Signal'].iloc[-1]
    hist = df['Histogram'].iloc[-1]
    
    # 趨勢判斷
    trend = "盤整" if abs(last_close - ma20) / ma20 < 0.05 else ("多頭" if last_close > ma20 else "空頭")
    if ma5 > ma10 > ma20:
        trend = "多頭排列"
    elif ma5 < ma10 < ma20:
        trend = "空頭排列"
    
    # MACD 判斷
    macd_signal = "偏多" if macd > signal else "偏空"
    
    # 建議
    if trend == "多頭排列" and macd > signal:
        action = "續抱或分批進場"
    elif trend == "空頭排列" or macd < signal:
        action = "保守看待或減碼"
    else:
        action = "觀望為主"
    
    analysis = f"""## {stock_name} 分析

### 技術面
- **股價**：{last_close:,.0f} 元
- **均線**：MA5 {ma5:,.0f} / MA10 {ma10:,.0f} / MA20 {ma20:,.0f}
- **趨勢**：{trend}
- **MACD**：DIF {macd:,.2f} / Signal {signal:,.2f} → {macd_signal}

### 建議
- **{action}**

---
"""
    return analysis

def send_discord(message, image_path=None):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    headers = {"Authorization": f"Bot {DISCORD_TOKEN}"}
    
    if image_path:
        with open(image_path, "rb") as f:
            files = {"file": (f"stock.png", f.read(), "image/png")}
            data = {"content": message}
            resp = requests.post(url, headers=headers, files=files, data=data)
    else:
        data = {"content": message}
        resp = requests.post(url, headers=headers, json=data)
    
    return resp.status_code

# 主程式
print("=" * 50)
print("開始生成股票報告...")
print("=" * 50)

all_analysis = "# 📈 股票每日追蹤報告\n\n"

for stock_code, stock_name in STOCKS:
    print(f"處理 {stock_name} ({stock_code})...")
    
    # 畫圖
    output_file = f'/Users/wuxiaoyin/.openclaw/workspace/{stock_code}_kline.png'
    df = plot_kline(stock_code, stock_name, output_file)
    
    # 取得價格
    price, change = get_price(stock_code)
    
    # 取得新聞
    news = get_news(stock_code, stock_name)
    
    # 分析
    analysis = analyze(df, stock_name)
    
    # 加入報告
    all_analysis += f"### 💰 股價：{price} 元 (漲跌 {change})\n\n"
    if news:
        all_analysis += "**最新新聞：**\n"
        for n in news[:2]:
            all_analysis += f"- {n[:50]}...\n"
        all_analysis += "\n"
    all_analysis += analysis

# 傳送到 Discord
print("\n傳送到 Discord...")
status = send_discord(all_analysis)
print(f"Discord 狀態: {status}")

print("\n完成!")
