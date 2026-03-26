#!/usr/bin/env python3
# 股票深度研究報告 - 每日 20:00 執行

import requests
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
import re
import urllib3
urllib3.disable_warnings()

FONT_PATH = '/System/Library/Fonts/STHeiti Medium.ttc'
BG_COLOR = '#2d2d2d'
font_prop = FontProperties(fname=FONT_PATH)
BAR_WIDTH = 0.35

DISCORD_TOKEN = "MTQ4MTI3NTg2MjYxMDYwODI4NQ.GFMBXg.FbVHlCk4P-dpT_SMR6BUj2UzNN5Ahm_HjTpUVA"
CHANNEL_ID = "1481483157575569409"
STOCKS = [('2330.TW', '台積電'), ('6223.TWO', '旺矽'), ('4772.TWO', '台特化')]

def get_wantgoo_news(limit=6):
    headers = {'User-Agent': 'Mozilla/5.0'}
    news_list = []
    try:
        list_url = "https://www.wantgoo.com/news/category/頭條/list"
        resp = requests.get(list_url, headers=headers, timeout=10, verify=False)
        items = resp.json().get('data', [])[:limit]
        for item in items:
            news_id = item['id']
            headline = item['headline']
            category = item['category']
            detail_url = f"https://www.wantgoo.com/news/{news_id}/detail"
            detail_resp = requests.get(detail_url, headers=headers, timeout=10, verify=False)
            summary = ""
            tags = []
            if detail_resp.status_code == 200:
                detail = detail_resp.json()
                summary = detail.get('summary', '') or ''
                tags = detail.get('tags', [])
            news_list.append({
                'source': '玩股網',
                'id': news_id,
                'headline': headline,
                'category': category,
                'summary': summary[:200] if summary else '',
                'tags': tags
            })
    except Exception as e:
        print(f"玩股網錯誤: {e}")
    return news_list

def get_ftchinese_news(limit=3):
    headers = {'User-Agent': 'Mozilla/5.0'}
    news_list = []
    try:
        url = "https://www.ftchinese.com/rss/news"
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
        for item in items[:limit]:
            title = re.search(r'<title><!\[CDATA\[([^\]]+)\]\]></title>', item)
            desc = re.search(r'<description><!\[CDATA\[([^\]]+)\]\]></description>', item)
            if title:
                headline = title.group(1)
                summary = desc.group(1) if desc else ''
                summary = re.sub(r'<[^>]+>', '', summary).strip()
                news_list.append({
                    'source': 'FT中文網',
                    'headline': headline,
                    'category': '國際財經',
                    'summary': summary[:200]
                })
    except Exception as e:
        print(f"FT錯誤: {e}")
    return news_list

def analyze_news_impact(news_list):
    keywords_map = {
        '半導體': ['半導體', '晶片', '台積電', 'AI', '輝達', 'nvidia', '晶圓'],
        '地緣政治': ['川普', '伊朗', '中美', '貿易戰', '關稅', '制裁'],
        '原物料': ['石油', '銅', '鋼鐵', '鋁', '原物料', '大宗物資'],
        '科技股': ['蘋果', 'google', 'meta', 'amazon', '微軟', '電子'],
        '中國/陸股': ['陸股', 'A股', '港股', '阿里巴巴', '騰訊', '京東'],
        '台灣': ['台股', '台灣', '央行', '利率', '基本面'],
    }
    analyzed = []
    for news in news_list:
        text = news['headline'] + ' ' + news.get('summary', '')
        impact = []
        sectors = []
        if any(k in text for k in ['台積電', '半導體', '晶片']) or '台股' in news['category']:
            impact.append('對台灣半導體/科技股有影響')
            sectors.extend(['半導體', '科技股', '台股大盤'])
        if any(k in text for k in ['伊朗', '石油', '中東', '油價']):
            impact.append('影響能源/原物料報價')
            sectors.extend(['原物料', '航運', '能源'])
        if any(k in text for k in ['中美', '關稅', '制裁', '中國', '陸股']):
            impact.append('影響中概股/陸港股')
            sectors.extend(['陸股', '港股', '中概股'])
        if any(k in text for k in ['川普', 'Fed', '升息', '降息', '利率']):
            impact.append('影響全球金融市場情緒')
            sectors.extend(['金融股', '科技股', '新興市場'])
        if 'AI' in text or 'nvidia' in text.lower() or '輝達' in text:
            impact.append('對AI概念股/科技供應鏈有影響')
            sectors.extend(['AI概念', '科技股', '半導體'])
        if not impact:
            impact.append('目前對台股直接影響有限')
        news['impact'] = impact
        news['affected_sectors'] = list(set(sectors)) if sectors else ['觀察中']
        analyzed.append(news)
    return analyzed

def create_chart(stock_code, stock_name):
    df = yf.download(stock_code, period="6mo", progress=False)
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
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    x = np.arange(len(df))
    fig = plt.figure(figsize=(16, 14), facecolor=BG_COLOR)
    gs = fig.add_gridspec(3, 1, height_ratios=[4, 1, 1], hspace=0.05)
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(BG_COLOR)
    for i in range(len(df)):
        o = df['Open'].iloc[i]
        c = df['Close'].iloc[i]
        h = df['High'].iloc[i]
        l = df['Low'].iloc[i]
        color = '#ff0000' if c >= o else '#00c000'
        ax1.plot([i, i], [l, h], color=color, linewidth=0.7)
        ax1.bar(i, abs(c-o), bottom=min(o,c), width=BAR_WIDTH, color=color, edgecolor=color)
    ax1.plot(x, df['MA5'].values, color='#FFD700', linewidth=1.5, label='MA5')
    ax1.plot(x, df['MA10'].values, color='#4169E1', linewidth=1.5, label='MA10')
    ax1.plot(x, df['MA20'].values, color='#9370DB', linewidth=1.5, label='MA20')
    ax1.set_title(f'{stock_name} ({stock_code}) - 半年技術分析', fontproperties=font_prop, fontsize=18, color='white', pad=15)
    ax1.set_ylabel('股價', fontproperties=font_prop, fontsize=14, color='white')
    ax1.legend(handles=[Line2D([0],[0],color='#FFD700',lw=2,label='MA5'),
                  Line2D([0],[0],color='#4169E1',lw=2,label='MA10'),
                  Line2D([0],[0],color='#9370DB',lw=2,label='MA20')],
                 loc='upper left', fontsize=12, facecolor=BG_COLOR, labelcolor='white')
    ax1.grid(True, alpha=0.3, color='gray')
    ax1.set_xlim(-1, len(df))
    ax1.tick_params(axis='x', labelbottom=False)
    ax1.tick_params(axis='y', labelcolor='white', labelsize=11)
    for s in ax1.spines.values(): s.set_color('white')
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.set_facecolor(BG_COLOR)
    hd = df['Histogram'].values
    ch = ['#ff0000' if h >= 0 else '#00c000' for h in hd]
    ax2.bar(x, hd, width=BAR_WIDTH, color=ch, edgecolor='none')
    ax2.plot(x, df['MACD'].values, color='#FFD700', linewidth=1.5)
    ax2.plot(x, df['Signal'].values, color='#4169E1', linewidth=1.5)
    ax2.axhline(y=0, color='white', linewidth=1)
    ax2.set_ylabel('MACD', fontproperties=font_prop, fontsize=13, color='white')
    ax2.legend(handles=[Line2D([0],[0],color='#FFD700',lw=1.5,label='DIF'),
                       Line2D([0],[0],color='#4169E1',lw=1.5,label='Signal')],
                      loc='upper left', fontsize=10, facecolor=BG_COLOR, labelcolor='white')
    ax2.grid(True, alpha=0.3, color='gray')
    ax2.tick_params(axis='x', labelbottom=False)
    ax2.tick_params(axis='y', labelcolor='white', labelsize=10)
    for s in ax2.spines.values(): s.set_color('white')
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.set_facecolor(BG_COLOR)
    ax3.plot(x, df['RSI'].values, color='#FFD700', linewidth=1.5)
    ax3.axhline(y=70, color='red', linewidth=1, linestyle='--', alpha=0.7)
    ax3.axhline(y=30, color='green', linewidth=1, linestyle='--', alpha=0.7)
    ax3.axhline(y=50, color='white', linewidth=0.8, linestyle=':')
    ax3.fill_between(x, 70, 100, alpha=0.2, color='red')
    ax3.fill_between(x, 0, 30, alpha=0.2, color='green')
    ax3.set_ylabel('RSI(14)', fontproperties=font_prop, fontsize=13, color='white')
    ax3.set_ylim(0, 100)
    ax3.grid(True, alpha=0.3, color='gray')
    ax3.set_xticks(x[::25])
    ax3.set_xticklabels([d.strftime('%Y/%m/%d') for d in df.index[::25]], rotation=45, fontsize=10, color='white')
    ax3.tick_params(axis='y', labelcolor='white', labelsize=10)
    ax3.tick_params(axis='x', labelcolor='white')
    for s in ax3.spines.values(): s.set_color('white')
    output = f'/Users/wuxiaoyin/.openclaw/workspace/{stock_code}_chart.png'
    plt.savefig(output, bbox_inches='tight', facecolor=BG_COLOR)
    plt.close()
    return output

def get_tech_data(code):
    df = yf.download(code, period="6mo", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    close = df['Close'].dropna()
    ma5 = close.rolling(5).mean().iloc[-1]
    ma10 = close.rolling(10).mean().iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]
    ma60 = close.rolling(60).mean().iloc[-1] if len(close) >= 60 else None
    current = close.iloc[-1]
    low_20 = df['Low'].tail(20).min()
    high_20 = df['High'].tail(20).max()
    low_60 = df['Low'].tail(60).min() if len(df) >= 60 else low_20
    vol_avg = df['Volume'].tail(20).mean()
    vol_today = df['Volume'].iloc[-1]
    vol_ratio = vol_today / vol_avg if vol_avg > 0 else 1
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = (100 - (100 / (1 + rs))).iloc[-1]
    exp12 = close.ewm(span=12, adjust=False).mean()
    exp26 = close.ewm(span=26, adjust=False).mean()
    macd = exp12.iloc[-1] - exp26.iloc[-1]
    return {
        'current': current, 'ma5': ma5, 'ma10': ma10, 'ma20': ma20, 'ma60': ma60,
        'low_20': low_20, 'high_20': high_20, 'low_60': low_60,
        'rsi': rsi, 'macd': macd, 'vol_ratio': vol_ratio
    }

def send_discord(content=None, file_path=None, filename=None):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    headers = {"Authorization": f"Bot {DISCORD_TOKEN}"}
    if file_path:
        with open(file_path, "rb") as f:
            files = {"file": (filename, f.read(), "image/png")}
            data = {"content": content} if content else {"content": ""}
            return requests.post(url, headers=headers, files=files, data=data)
    else:
        return requests.post(url, headers=headers, json={"content": content})

# 主程式
print("="*60)
print("開始股票深度研究報告...")
print("="*60)

send_discord(content="="*50 + "\n📊 股票深度研究報告 - " + pd.Timestamp.now().strftime('%Y/%m/%d') + "\n" + "="*50)

# 技術分析
print("\n取得技術數據...")
data_all = {}
for code, name in STOCKS:
    chart_path = create_chart(code, name)
    data_all[code] = get_tech_data(code)
    send_discord(content=f"=== {name} ({code}) 技術分析圖 ===", 
                 file_path=chart_path, 
                 filename=f"{name}_chart.png")
    print(f"  {name} 圖表已發送")

for code, name in STOCKS:
    d = data_all[code]
    ma5, ma10, ma20 = d['ma5'], d['ma10'], d['ma20']
    if ma5 > ma10 > ma20:
        trend = "多頭排列"
    elif ma5 < ma10 < ma20:
        trend = "空頭排列"
    else:
        trend = "整理中"
    rsi_status = "超買" if d['rsi'] > 70 else "超賣" if d['rsi'] < 30 else "中性"
    macd_status = "多方" if d['macd'] > 0 else "空方"
    vol_status = "放量" if d['vol_ratio'] > 1.2 else "縮量" if d['vol_ratio'] < 0.8 else "正常"
    ma60_str = f"{d['ma60']:.0f}" if d['ma60'] else "N/A"
    analysis = f"""
=== {name} ({code}) 技術分析 ===

現價：{d['current']:.0f} 元
均線：MA5={ma5:.0f} / MA10={ma10:.0f} / MA20={ma20:.0f} / MA60={ma60_str}

趨勢判斷：
- 均線排列：{trend}
- RSI(14)：{d['rsi']:.1f} -> {rsi_status}
- MACD：{macd_status} 動能
- 量能：{vol_status}（今日/均量 {d['vol_ratio']:.1f}x）

支撐與壓力：
- 支撐：{d['low_20']:.0f}（20日低）/ {d['low_60']:.0f}（60日低）
- 壓力：{d['high_20']:.0f}（20日高）
"""
    send_discord(content=analysis)
    print(f"  {name}分析已發送")

# 新聞
print("\n取得新聞...")
send_discord(content="\n" + "="*50 + "\n📰 今日財經新聞摘要\n" + "="*50)

wantgoo_news = get_wantgoo_news(6)
analyzed_news = analyze_news_impact(wantgoo_news)

for i, news in enumerate(analyzed_news):
    sectors_str = ' / '.join(news['affected_sectors'])
    impact_str = ' / '.join(news['impact'])
    msg = f"""
{i+1}. {news['headline']}
   [{news['source']}] {news['category']}
   
   摘要：{news['summary'][:100]}...
   
   市場影響：{impact_str}
   影響類股：{sectors_str}
"""
    send_discord(content=msg)
    print(f"  新聞 {i+1} 已發送")

ft_news = get_ftchinese_news(3)
for i, news in enumerate(ft_news):
    msg = f"""
{len(analyzed_news)+i+1}. {news['headline']}
   [{news['source']}]
   
   摘要：{news['summary'][:100]}...
   
   市場影響：觀察國際金融市場情緒變化
   影響類股：全球市場
"""
    send_discord(content=msg)

# 總結
summary = f"""
================================================================
【總結】市場綜合判斷
================================================================

【三檔股票技術比較】

| 股票  | 現價  |  趨勢  | RSI |  操作  |
|--------|--------|--------|-----|--------|
| 台積電 | {data_all['2330.TW']['current']:.0f}  |  {"空頭" if data_all['2330.TW']['ma5'] < data_all['2330.TW']['ma20'] else "多頭"}  | {data_all['2330.TW']['rsi']:.1f} |  觀望  |
| 旺矽  | {data_all['6223.TWO']['current']:.0f}  |  {"多頭" if data_all['6223.TWO']['ma5'] > data_all['6223.TWO']['ma20'] else "空頭"}  | {data_all['6223.TWO']['rsi']:.1f} |  不追高  |
| 台特化 | {data_all['4772.TWO']['current']:.0f}  |  {"空頭" if data_all['4772.TWO']['ma5'] < data_all['4772.TWO']['ma20'] else "多頭"}  | {data_all['4772.TWO']['rsi']:.1f} |  減碼  |

【市場性質判斷】
這是「大盤弱勢導致的技術性修正」，而非基本面反轉。

【風險提示】
! 國際局勢不確定性高（美中晶片戰、中東油價）
! 成交量若持續萎縮，指數難有表現
! 請嚴守停損設定
================================================================
"""
send_discord(content=summary)
print("\n總結已發送")
print("\n完成！")
