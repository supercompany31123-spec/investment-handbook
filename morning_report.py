#!/usr/bin/env python3
# 早盤晨報 - 每日 08:00 自動推播

import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import re
import urllib3
urllib3.disable_warnings()

FONT_PATH = '/System/Library/Fonts/STHeiti Medium.ttc'
BG_COLOR = '#1a1a2e'
font_prop = FontProperties(fname=FONT_PATH)

DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN', '')
CHANNEL_ID = "1481483157575569409"

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

def get_market_data():
    """取得市場數據"""
    print("取得市場數據...")
    
    us_stocks = {
        '^GSPC': 'S&P 500',
        '^IXIC': 'Nasdaq',
        '^DJI': 'Dow Jones',
        'TSM': '台積電 ADR',
        'NVDA': 'NVIDIA',
        'TSLA': 'Tesla'
    }
    
    stock_data = {}
    for code, name in us_stocks.items():
        try:
            ticker = yf.Ticker(code)
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_close = hist['Close'].iloc[-1]
                change = curr_close - prev_close
                pct = (change / prev_close) * 100
                stock_data[name] = {
                    'curr': curr_close,
                    'change': change,
                    'pct': pct
                }
                print(f"  {name}: {curr_close:.2f} ({pct:+.2f}%)")
        except Exception as e:
            print(f"  {name}: 錯誤 - {e}")
    
    # 指標
    indicators = {}
    ind_names = {'^VIX': 'VIX', '^TNX': 'US10Y', 'DX-Y.NYB': 'DXY', 'CL=F': 'WTI原油'}
    for code, name in ind_names.items():
        try:
            ticker = yf.Ticker(code)
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                prev = hist['Close'].iloc[-2]
                curr = hist['Close'].iloc[-1]
                pct = ((curr - prev) / prev) * 100
                indicators[name] = {'curr': curr, 'pct': pct}
                print(f"  {name}: {curr:.2f} ({pct:+.2f}%)")
        except Exception as e:
            print(f"  {name}: 錯誤")
    
    return stock_data, indicators

def create_indicators_chart(indicators):
    """生成指標儀表板（30日趨勢線）"""
    import yfinance as yf
    
    # 取得歷史數據
    hist_data = {}
    codes = {'VIX': '^VIX', 'US10Y': '^TNX', 'DXY': 'DX-Y.NYB', 'WTI': 'CL=F'}
    for name, code in codes.items():
        try:
            ticker = yf.Ticker(code)
            hist = ticker.history(period="30d")
            if len(hist) > 0:
                hist_data[name] = hist['Close'].tail(30)
        except:
            pass
    
    fig = plt.figure(figsize=(14, 10), facecolor=BG_COLOR)
    
    # VIX
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.set_facecolor(BG_COLOR)
    if 'VIX' in hist_data:
        data = hist_data['VIX'].values
        ax1.plot(range(len(data)), data, color='orange', linewidth=2)
        ax1.fill_between(range(len(data)), data, alpha=0.3, color='orange')
        ax1.axhline(y=20, color='yellow', linestyle='--', alpha=0.7, label='不安區 (20)')
        ax1.axhline(y=30, color='red', linestyle='--', alpha=0.7, label='恐慌區 (30)')
        ax1.set_title(f"VIX 恐慌指數: {indicators.get('VIX', {}).get('curr', 0):.2f}", fontproperties=font_prop, color='white', fontsize=14)
    else:
        ax1.set_title("VIX 恐慌指數: N/A", fontproperties=font_prop, color='white')
    ax1.legend(facecolor=BG_COLOR, labelcolor='white', fontsize=8)
    ax1.tick_params(colors='white')
    for spine in ax1.spines.values(): spine.set_color('white')
    
    # US10Y
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.set_facecolor(BG_COLOR)
    if 'US10Y' in hist_data:
        data = hist_data['US10Y'].values
        ax2.plot(range(len(data)), data, color='green', linewidth=2)
        ax2.fill_between(range(len(data)), data, alpha=0.3, color='green')
        ax2.set_title(f"10年美債收益率: {indicators.get('US10Y', {}).get('curr', 0):.2f}%", fontproperties=font_prop, color='white', fontsize=14)
    else:
        ax2.set_title("10年美債收益率: N/A", fontproperties=font_prop, color='white')
    ax2.tick_params(colors='white')
    for spine in ax2.spines.values(): spine.set_color('white')
    
    # DXY
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.set_facecolor(BG_COLOR)
    if 'DXY' in hist_data:
        data = hist_data['DXY'].values
        ax3.plot(range(len(data)), data, color='blue', linewidth=2)
        ax3.fill_between(range(len(data)), data, alpha=0.3, color='blue')
        ax3.axhline(y=100, color='white', linestyle=':', alpha=0.5, label='中性 (100)')
        ax3.set_title(f"美元指數 DXY: {indicators.get('DXY', {}).get('curr', 0):.2f}", fontproperties=font_prop, color='white', fontsize=14)
    else:
        ax3.set_title("美元指數 DXY: N/A", fontproperties=font_prop, color='white')
    ax3.legend(facecolor=BG_COLOR, labelcolor='white', fontsize=8)
    ax3.tick_params(colors='white')
    for spine in ax3.spines.values(): spine.set_color('white')
    
    # WTI
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.set_facecolor(BG_COLOR)
    if 'WTI' in hist_data:
        data = hist_data['WTI'].values
        ax4.plot(range(len(data)), data, color='purple', linewidth=2)
        ax4.fill_between(range(len(data)), data, alpha=0.3, color='purple')
        ax4.set_title(f"WTI 原油: ${indicators.get('WTI原油', {}).get('curr', 0):.2f}", fontproperties=font_prop, color='white', fontsize=14)
    else:
        ax4.set_title("WTI 原油: N/A", fontproperties=font_prop, color='white')
    ax4.tick_params(colors='white')
    for spine in ax4.spines.values(): spine.set_color('white')
    
    plt.tight_layout()
    output = '/Users/wuxiaoyin/.openclaw/workspace/morning_indicators.png'
    plt.savefig(output, bbox_inches='tight', facecolor=BG_COLOR, dpi=100)
    plt.close()
    return output

def get_fundamental_data():
    """取得基本面資料"""
    print("\n取得基本面資料...")
    
    stocks = {
        '2330.TW': '台積電',
        '6223.TWO': '旺矽',
        '4772.TWO': '台特化'
    }
    
    fundamental_data = {}
    
    for code, name in stocks.items():
        try:
            ticker = yf.Ticker(code)
            info = ticker.info
            
            # 估值
            pe = info.get('trailingPE', 0) or 0
            pb = info.get('priceToBook', 0) or 0
            eps = info.get('trailingEps', 0) or 0
            
            # 殖利率（Yahoo 直接回傳百分比數值，如 1.33 = 1.33%）
            div_yield = info.get('dividendYield', 0) or 0
            div_pct = div_yield
            
            # 成長
            rev_growth = info.get('revenueGrowth', 0) or 0
            if isinstance(rev_growth, float):
                rev_growth_pct = rev_growth * 100
            else:
                rev_growth_pct = rev_growth
            
            # 獲利能力
            gross_margin = info.get('grossMargins', 0) or 0
            oper_margin = info.get('operatingMargins', 0) or 0
            roe = info.get('returnOnEquity', 0) or 0
            
            # 52週位置
            high_52w = info.get('fiftyTwoWeekHigh', 0) or 0
            low_52w = info.get('fiftyTwoWeekLow', 0) or 0
            curr_price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0) or 0
            
            if high_52w > low_52w:
                pos_52w = ((curr_price - low_52w) / (high_52w - low_52w)) * 100
            else:
                pos_52w = 50
            
            fundamental_data[code] = {
                'name': name,
                'pe': pe,
                'pb': pb,
                'eps': eps,
                'div_yield': div_pct,
                'rev_growth': rev_growth_pct,
                'gross_margin': gross_margin * 100 if gross_margin else 0,
                'oper_margin': oper_margin * 100 if oper_margin else 0,
                'roe': roe * 100 if roe else 0,
                'pos_52w': pos_52w,
                'high_52w': high_52w,
                'low_52w': low_52w,
                'curr_price': curr_price
            }
            
            print(f"  {name}: P/E={pe:.1f}, ROE={roe*100:.1f}%, 殖利率={div_pct:.2f}%")
            
        except Exception as e:
            print(f"  {name}: 錯誤 - {e}")
    
    return fundamental_data


def get_news():
    """取得新聞"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    news_list = []
    
    # 玩股網
    try:
        url = "https://www.wantgoo.com/news/category/頭條/list"
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        items = resp.json().get('data', [])[:6]
        for item in items[:6]:
            news_id = item['id']
            headline = item['headline']
            category = item['category']
            detail_url = f"https://www.wantgoo.com/news/{news_id}/detail"
            detail_resp = requests.get(detail_url, headers=headers, timeout=10, verify=False)
            summary = ""
            if detail_resp.status_code == 200:
                detail = detail_resp.json()
                summary = detail.get('summary', '') or ''
            news_list.append({
                'source': '玩股網',
                'headline': headline,
                'category': category,
                'summary': summary[:200] if summary else ''
            })
    except Exception as e:
        print(f"玩股網錯誤: {e}")
    
    return news_list

def analyze_market(stock_data, indicators):
    """根據投資知識庫框架分析市場"""
    analysis = []
    
    # VIX 分析
    vix = indicators.get('VIX', {}).get('curr', 0)
    if vix > 30:
        analysis.append("🔴 VIX > 30，市場極度恐慌")
    elif vix > 20:
        analysis.append("🟡 VIX 在 20-30，市場開始不安")
    else:
        analysis.append("🟢 VIX < 20，市場相對穩定")
    
    # DXY 分析
    dxy = indicators.get('DXY', {}).get('curr', 0)
    if dxy > 105:
        analysis.append("🔴 DXY > 105，流動性危機信號")
    elif dxy > 100:
        analysis.append("🟡 DXY 在 100-105，美元偏強")
    else:
        analysis.append("🟢 DXY < 100，資金回流風險資產")
    
    # 油價分析
    oil = indicators.get('WTI原油', {}).get('curr', 0)
    if oil > 100:
        analysis.append("🔴 油價 > $100，通膨壓力大")
    elif oil > 80:
        analysis.append("🟡 油價在 $80-100，區間偏高")
    else:
        analysis.append("🟢 油價 < $80，通膨壓力緩解")
    
    return analysis

# 主程式
print("="*60)
print("開始早盤晨報...")
print("="*60)

today = pd.Timestamp.now().strftime('%Y/%m/%d')

# 發送開頭
send_discord(content=f"""🌅 美股晨報 · {today}
═══════════════════════════════════════""")

# 取得市場數據
stock_data, indicators = get_market_data()


# 儲存晨報到 JSON 檔
import json
from datetime import datetime

report_data = {
    'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
    'market': {
        'sp500': stock_data.get('S&P 500', {}),
        'nasdaq': stock_data.get('Nasdaq', {}),
        'dow': stock_data.get('Dow Jones', {}),
        'tsm': stock_data.get('台積電 ADR', {}),
        'nvda': stock_data.get('NVIDIA', {}),
        'tsla': stock_data.get('Tesla', {})
    },
    'indicators': indicators,
    'fundamental': fundamental_data
}

# 讀取現有歷史
try:
    with open('/Users/wuxiaoyin/.openclaw/workspace/reports_history.json', 'r') as f:
        history = json.load(f)
except:
    history = []

# 加入新報告
history.insert(0, report_data)

# 只保留最近30份
history = history[:30]

# 儲存
with open('/Users/wuxiaoyin/.openclaw/workspace/reports_history.json', 'w') as f:
    json.dump(history, f, ensure_ascii=False, indent=2)

print("  晨報已儲存到 reports_history.json")

# 取得基本面資料
fundamental_data = get_fundamental_data()

# 發送美股數據
us_msg = f"""
📊【美股昨日收盤】

  道瓊工業: {stock_data.get('Dow Jones', {}).get('curr', 0):,.2f} {'📈' if stock_data.get('Dow Jones', {}).get('pct', 0) > 0 else '📉'} {stock_data.get('Dow Jones', {}).get('pct', 0):+.2f}%
  S&P 500: {stock_data.get('S&P 500', {}).get('curr', 0):,.2f} {'📈' if stock_data.get('S&P 500', {}).get('pct', 0) > 0 else '📉'} {stock_data.get('S&P 500', {}).get('pct', 0):+.2f}%
  Nasdaq: {stock_data.get('Nasdaq', {}).get('curr', 0):,.2f} {'📈' if stock_data.get('Nasdaq', {}).get('pct', 0) > 0 else '📉'} {stock_data.get('Nasdaq', {}).get('pct', 0):+.2f}%

💹【個股表現】

  台積電 ADR (TSM): ${stock_data.get('台積電 ADR', {}).get('curr', 0):.2f} {'📈' if stock_data.get('台積電 ADR', {}).get('pct', 0) > 0 else '📉'} {stock_data.get('台積電 ADR', {}).get('pct', 0):+.2f}%
  NVIDIA (NVDA): ${stock_data.get('NVIDIA', {}).get('curr', 0):.2f} {'📈' if stock_data.get('NVIDIA', {}).get('pct', 0) > 0 else '📉'} {stock_data.get('NVIDIA', {}).get('pct', 0):+.2f}%  
  Tesla (TSLA): ${stock_data.get('Tesla', {}).get('curr', 0):.2f} {'📈' if stock_data.get('Tesla', {}).get('pct', 0) > 0 else '📉'} {stock_data.get('Tesla', {}).get('pct', 0):+.2f}%
"""
send_discord(content=us_msg)

# 發送基本面資料（手機好讀版）
if fundamental_data:
    fund_msg = """

📊【基本面資料】

"""
    for code, data in fundamental_data.items():
        # 評價狀態
        pe_status = "✅" if 10 < data['pe'] < 30 else "⚠️"
        roe_status = "✅" if data['roe'] > 20 else "✅" if data['roe'] > 15 else "⚠️"
        
        fund_msg += f"""
▸ {data['name']}
   P/E {data['pe']:.0f} {pe_status} | P/B {data['pb']:.1f}
   EPS {data['eps']:.1f}元 | 殖利率 {data['div_yield']:.2f}%
   營收 {data['rev_growth']:+.0f}% | ROE {data['roe']:.0f}%
   52週 {data['pos_52w']:.0f}%（{data['low_52w']:.0f}~{data['high_52w']:.0f}）
"""
    
    send_discord(content=fund_msg)
    print("  基本面資料已發送")

# 發送指標
ind_msg = f"""
🔑【關鍵指標】

  VIX 恐慌指數: {indicators.get('VIX', {}).get('curr', 0):.2f} ({indicators.get('VIX', {}).get('pct', 0):+.2f}%)
  → {'🟡 區間：開始不安，但脫離恐慌' if indicators.get('VIX', {}).get('curr', 0) < 30 else '🔴 恐慌區間'}

  10年美債收益率: {indicators.get('US10Y', {}).get('curr', 0):.2f}% ({indicators.get('US10Y', {}).get('pct', 0):+.2f}%)
  → {'收益率下降，避險情緒緩解' if indicators.get('US10Y', {}).get('pct', 0) < 0 else '收益率上升，市場謹慎'}

  美元指數 DXY: {indicators.get('DXY', {}).get('curr', 0):.2f} ({indicators.get('DXY', {}).get('pct', 0):+.2f}%)
  → {'DXY 回落，資金流出美元' if indicators.get('DXY', {}).get('curr', 0) < 100 else 'DXY 偏強，美元避險'}

  WTI 原油: ${indicators.get('WTI原油', {}).get('curr', 0):.2f} ({indicators.get('WTI原油', {}).get('pct', 0):+.2f}%)
  → {'油價回落，通膨壓力緩解' if indicators.get('WTI原油', {}).get('pct', 0) < 0 else '油價上升，通膨擔憂'}
"""
send_discord(content=ind_msg)

# 生成並發送指標圖表
try:
    chart_path = create_indicators_chart(indicators)
    send_discord(content="🌍【關鍵指標圖表】", file_path=chart_path, filename="morning_indicators.png")
    print("  指標圖表已發送")
except Exception as e:
    print(f"  圖表錯誤: {e}")

# 取得新聞
print("\n取得新聞...")
news_list = get_news()
print(f"  取得 {len(news_list)} 則新聞")

# 發送新聞摘要
if news_list:
    news_msg = """
🌐【今日重大新聞摘要】

═══════════════════════════════════════"""
    send_discord(content=news_msg)
    
    for news in news_list[:5]:
        # 根據分類給 emoji
        cat = news['category']
        if '國際政經' in cat or '美' in cat:
            emoji = '🌍'
        elif '科技' in cat or 'AI' in cat:
            emoji = '💻'
        elif '能源' in cat or '原油' in cat or '黃金' in cat:
            emoji = '⛽'
        elif '台股' in cat or '台灣' in cat:
            emoji = '🇹🇼'
        else:
            emoji = '📌'
        
        item_msg = f"""
{emoji}【{news['category']}】

📰 {news['headline']}

💡 {news['summary'][:100]}...
"""
        send_discord(content=item_msg)

# 市場分析
analysis = analyze_market(stock_data, indicators)
analysis_msg = f"""
═══════════════════════════════════════

💡【市場解讀】

  {'\n  '.join(analysis)}

═══════════════════════════════════════
🌅 晨報完畢 | 數據來源: Yahoo Finance / 玩股網
"""
send_discord(content=analysis_msg)

print("\n完成!")
