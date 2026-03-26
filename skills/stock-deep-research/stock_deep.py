#!/usr/bin/env python3
# 股票深度研究報告 - 每日 20:00 執行
# 包含：技術分析 + 法人動向 + 新聞摘要 + 市場影響分析

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
import subprocess
import json
urllib3.disable_warnings()

FONT_PATH = '/System/Library/Fonts/STHeiti Medium.ttc'
BG_COLOR = '#2d2d2d'
font_prop = FontProperties(fname=FONT_PATH)
BAR_WIDTH = 0.35

DISCORD_TOKEN = "MTQ4MTI3NTg2MjYxMDYwODI4NQ.GFMBXg.FbVHlCk4P-dpT_SMR6BUj2UzNN5Ahm_HjTpUVA"
CHANNEL_ID = "1481483157575569409"
STOCKS = [('2330.TW', '台積電'), ('6223.TWO', '旺矽'), ('4772.TWO', '台特化')]

# ============ Playwright 新聞取得 ============
def get_news_playwright():
    """用 Playwright 取得 JS 動態網頁的新聞"""
    news_list = []
    
    js_code = '''
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const results = [];
  
  // Yahoo 股市
  try {
    const page = await browser.newPage();
    await page.goto('https://tw.stock.yahoo.com/news/market', { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(2000);
    const yahooNews = await page.evaluate(() => {
      const links = document.querySelectorAll('a');
      const result = [];
      links.forEach(link => {
        const text = link.textContent.trim();
        if (text.length > 15 && text.length < 80 && !text.includes('Yahoo') && !text.includes('信箱') && !text.includes('股市') && !text.includes('會員') && !text.includes('功能')) {
          result.push(text);
        }
      });
      return [...new Set(result)].slice(0, 8);
    });
    results.push({ source: 'Yahoo股市', items: yahooNews });
    await page.close();
  } catch(e) { results.push({ source: 'Yahoo股市', error: e.message }); }
  
  // 鉅亨網
  try {
    const page = await browser.newPage();
    await page.goto('https://www.cnyes.com/', { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(2000);
    const cnyesNews = await page.evaluate(() => {
      const links = document.querySelectorAll('a');
      const result = [];
      links.forEach(link => {
        const text = link.textContent.trim();
        if (text.length > 15 && text.length < 80 && !text.includes('鉅亨') && !text.includes('APP') && !text.includes('服務') && !text.includes('功能')) {
          result.push(text);
        }
      });
      return [...new Set(result)].slice(0, 8);
    });
    results.push({ source: '鉅亨網', items: cnyesNews });
    await page.close();
  } catch(e) { results.push({ source: '鉅亨網', error: e.message }); }
  
  console.log(JSON.stringify(results));
  await browser.close();
})();
'''
    
    try:
        result = subprocess.run(
            ['node', '-e', js_code],
            capture_output=True,
            text=True,
            timeout=120,
            cwd='/Users/wuxiaoyin/.openclaw/workspace'
        )
        if result.returncode == 0 and result.stdout:
            news_list = json.loads(result.stdout)
    except Exception as e:
        print(f"Playwright 錯誤: {e}")
    
    return news_list

# ============ 玩股網 API ============
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

# ============ 法人買賣資料 (Playwright) ============
def get_institutional_data():
    """用 Playwright 取得個股法人買賣超資料"""
    js_code = r'''
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const results = {};
  
  const stocks = [
    { code: '2330.TW', name: '台積電' },
    { code: '6223.TWO', name: '旺矽' },
    { code: '4772.TWO', name: '台特化' }
  ];
  
  for (const stock of stocks) {
    try {
      const page = await browser.newPage();
      const url = `https://tw.stock.yahoo.com/quote/${stock.code}/institutional-trading`;
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(2000);
      
      const text = await page.evaluate(() => document.body.innerText);
      const lines = text.split('\n');
      
      const data = { stock: stock.name, code: stock.code, found: {} };
      
      // 找 "法人買賣總覽" 的位置，從那裡開始解析
      // 格式：
      //   外資 / 投信 / 自營商  (header)
      //   買進數字
      //   賣出數字  
      //   買賣超數字
      //   連買連賣註解
      
      let sectionStart = -1;
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes('法人買賣總覽')) {
          sectionStart = i;
          break;
        }
      }
      
      if (sectionStart >= 0) {
        // 在這個區塊找數字
        let foreignCount = 0;
        let investmentCount = 0;
        let dealerCount = 0;
        
        for (let i = sectionStart; i < Math.min(sectionStart + 50, lines.length); i++) {
          const line = lines[i].trim();
          const nextLine = lines[i+1] ? lines[i+1].trim() : '';
          const next2Line = lines[i+2] ? lines[i+2].trim() : '';
          const next3Line = lines[i+3] ? lines[i+3].trim() : '';
          
          // 如果這一行包含數字且下一行也包含數字，可能是法人數據
          if (line.match(/^[\-\d,]+$/) && nextLine.match(/^[\-\d,]+$/) && next2Line.match(/^[\-\d,]+$/)) {
            const num1 = parseInt(line.replace(/,/g, ''));
            const num2 = parseInt(nextLine.replace(/,/g, ''));
            const num3 = parseInt(next2Line.replace(/,/g, ''));
            
            // 根據已經解析了多少組來判斷是誰
            if (foreignCount === 0 && num1 !== 0) {
              data.found.foreign_buy = num1;
              data.found.foreign_sell = num2;
              data.found.foreign_net = num3;
              foreignCount = 1;
            } else if (investmentCount === 0 && num1 !== 0) {
              data.found.investment_buy = num1;
              data.found.investment_sell = num2;
              data.found.investment_net = num3;
              investmentCount = 1;
            } else if (dealerCount === 0 && num1 !== 0) {
              data.found.dealer_buy = num1;
              data.found.dealer_sell = num2;
              data.found.dealer_net = num3;
              dealerCount = 1;
            }
          }
        }
      }
      
      // 解析歷史資料 (近5日)
      const history = [];
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        // 日期格式: 2026/03/23
        if (/^\d{4}\/\d{2}\/\d{2}$/.test(line)) {
          const date = line;
          const fNet = parseInt((lines[i+1] || '').replace(/,/g, '')) || 0;
          const iNet = parseInt((lines[i+2] || '').replace(/,/g, '')) || 0;
          const dNet = parseInt((lines[i+3] || '').replace(/,/g, '')) || 0;
          
          if (fNet !== 0 || iNet !== 0 || dNet !== 0) {
            if (history.length < 5) {
              history.push({ date, foreign: fNet, investment: iNet, dealer: dNet });
            }
          }
        }
      }
      data.history = history;
      
      results[stock.code] = data;
      await page.close();
    } catch(e) {
      results[stock.code] = { stock: stock.name, code: stock.code, error: e.message };
    }
  }
  
  console.log(JSON.stringify(results));
  await browser.close();
})();
'''
    
    try:
        result = subprocess.run(
            ['node', '-e', js_code],
            capture_output=True,
            text=True,
            timeout=180,
            cwd='/Users/wuxiaoyin/.openclaw/workspace'
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"法人資料取得錯誤: {e}")
    return {}

# ============ 新聞統整分析 ============
# ============ 新聞統整分析 ============
def consolidate_news(all_news):
    """將多來源新聞統整成幾個主題"""
    themes = {
        '地緣政治/中東': [],
        '半導體/科技': [],
        '中國/陸股': [],
        '台灣宏觀': [],
        '能源/原物料': [],
        '其他': []
    }
    
    for news in all_news.get('wantgoo', []):
        text = news['headline'] + ' ' + news.get('summary', '')
        
        if any(k in text for k in ['伊朗', '川普', '中東', '石油', '油價', '戰爭']):
            themes['地緣政治/中東'].append(news)
        elif any(k in text for k in ['半導體', '晶片', 'AI', '輝達', '台積電', '科技', '光電子']):
            themes['半導體/科技'].append(news)
        elif any(k in text for k in ['中國', '陸股', 'A股', '港股', '阿里巴巴', '騰訊']):
            themes['中國/陸股'].append(news)
        elif any(k in text for k in ['台股', '台灣', '央行', '利率', '基本面', '經濟']):
            themes['台灣宏觀'].append(news)
        elif any(k in text for k in ['石油', '銅', '鋼鐵', '能源', '原物料', '大宗']):
            themes['能源/原物料'].append(news)
        else:
            themes['其他'].append(news)
    
    for source, items in all_news.get('playwright', []):
        for headline in items:
            news = {'source': source, 'headline': headline, 'summary': '', 'category': ''}
            
            if any(k in headline for k in ['伊朗', '川普', '中東', '石油', '油價', '戰爭', '美伊']):
                themes['地緣政治/中東'].append(news)
            elif any(k in headline for k in ['半導體', '晶片', 'AI', '輝達', '台積電', '科技', 'nvidia', '電力']):
                themes['半導體/科技'].append(news)
            elif any(k in headline for k in ['中國', '陸股', 'A股', '港股', '阿里巴巴', '騰訊', '京東']):
                themes['中國/陸股'].append(news)
            elif any(k in headline for k in ['台股', '台灣', '央行', '利率', 'Fed', '升息', '降息']):
                themes['台灣宏觀'].append(news)
            elif any(k in headline for k in ['石油', '銅', '鋼鐵', '能源', '原物料', '油價']):
                themes['能源/原物料'].append(news)
            else:
                themes['其他'].append(news)
    
    return themes

def analyze_theme_impact(theme_name, news_list):
    """分析每個主題對市場的影響"""
    if not news_list:
        return None
    
    impacts = []
    affected = []
    
    if theme_name == '地緣政治/中東':
        impacts.append("影響市場風險情緒")
        impacts.append("若中東衝突緩解，風險資產可能反彈")
        impacts.append("若衝突升級，原物料/能源股可能受惠")
        affected.extend(['科技股', '航運股', '能源股', '新興市場'])
    
    elif theme_name == '半導體/科技':
        impacts.append("AI/半導體需求趨勢，持續關注")
        impacts.append("若與台積電相關，影響供應鏈")
        affected.extend(['半導體', 'AI概念', '科技股', '台股大盤'])
    
    elif theme_name == '中國/陸股':
        impacts.append("中美貿易緊張，可能影響科技供應鏈")
        impacts.append("陸股/港股氣氛影響投資信心")
        affected.extend(['陸股', '港股', '中概股', '科技供應鏈'])
    
    elif theme_name == '台灣宏觀':
        impacts.append("利率政策影響資金流向")
        impacts.append("台股基本面持續觀察")
        affected.extend(['金融股', '台股大盤', '所有類股'])
    
    elif theme_name == '能源/原物料':
        impacts.append("原物料價格波動影響成本")
        impacts.append("通膨壓力影響央行政策")
        affected.extend(['能源股', '航運股', '原物料', '製造成本'])
    
    if not impacts:
        impacts.append("需持續觀察後續發展")
    
    return {
        'theme': theme_name,
        'news_count': len(news_list),
        'key_news': [n['headline'] for n in news_list[:3]],
        'impacts': impacts,
        'affected': list(set(affected))
    }

# ============ 圖表生成 ============
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

# ========== 主程式 ==========
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
    # 選擇趨勢 emoji
    trend_emoji = "📈" if ma5 > ma20 else "📉" if ma5 < ma20 else "📊"
    rsi_emoji = "🔥" if d['rsi'] > 70 else "💧" if d['rsi'] < 30 else "➡️"
    macd_emoji = "🟢" if d['macd'] > 0 else "🔴"
    vol_emoji = "📈" if d['vol_ratio'] > 1.2 else "📉" if d['vol_ratio'] < 0.8 else "➡️"
    
    analysis = f"""
{trend_emoji} {name}（{code}）技術分析

💰 現價：{d['current']:.0f} 元
📊 均線：MA5={ma5:.0f} / MA10={ma10:.0f} / MA20={ma20:.0f} / MA60={ma60_str}

【趨勢判斷】
  {trend_emoji} 均線排列：{trend}
  {rsi_emoji} RSI(14)：{d['rsi']:.1f} → {rsi_status}
  {macd_emoji} MACD：{macd_status} 動能
  {vol_emoji} 量能：{vol_status}（今日/均量 {d['vol_ratio']:.1f}x）

【支撐與壓力】
  🛡️ 支撐：{d['low_20']:.0f}（20日低）/ {d['low_60']:.0f}（60日低）
  🎯 壓力：{d['high_20']:.0f}（20日高）
"""
    send_discord(content=analysis)
    print(f"  {name}分析已發送")

# 法人買賣超
print("\n取得法人買賣超資料...")
send_discord(content="\n" + "="*50 + "\n💼 三大法人買賣超\n" + "="*50)

institutional = get_institutional_data()
print(f"  取得法人資料: {len(institutional)} 檔")

for code, name in STOCKS:
    inst = institutional.get(code, {})
    if 'error' in inst:
        send_discord(content=f"{name}: 無法取得法人資料")
        continue
    
    f = inst.get('found', {})
    history = inst.get('history', [])[:3]  # 最近3天
    
    # 使用 JavaScript 解析出來的 key 名稱
    f_buy = f.get('foreign_buy', 0)
    f_sell = f.get('foreign_sell', 0)
    f_net = f.get('foreign_net', 0)
    i_buy = f.get('investment_buy', 0)
    i_sell = f.get('investment_sell', 0)
    i_net = f.get('investment_net', 0)
    d_buy = f.get('dealer_buy', 0)
    d_sell = f.get('dealer_sell', 0)
    d_net = f.get('dealer_net', 0)
    
    # 計算三日累計
    total_3day = sum(h.get('foreign', 0) for h in history) if history else 0
    
    # 判斷訊號（根據淨買賣超）
    signals = []
    if f_net < -200:
        signals.append("外援偏空")
    elif f_net > 200:
        signals.append("外援偏多")
    
    if i_net > 0:
        signals.append("投信偏多")
    elif i_net < 0:
        signals.append("投信偏空")
    
    if d_net > 0:
        signals.append("自營商偏多")
    elif d_net < 0:
        signals.append("自營商偏空")
    
    signal_str = " / ".join(signals) if signals else "大致持平"
    
    # 格式化張數顯示
    def fmt(n):
        if isinstance(n, int):
            return f"{n:,}"
        return str(n)
    
    # 選擇法人 emoji
    f_emoji = "🔴" if f_net < 0 else "🟢"
    i_emoji = "🔴" if i_net < 0 else "🟢"
    d_emoji = "🔴" if d_net < 0 else "🟢"
    
    total_net = f_net + i_net + d_net
    total_emoji = "🔴" if total_net < 0 else "🟢"
    
    msg = f"""
🏛️ {name}（{code}）

【當日法人買賣 · 單位：張】

  {f_emoji} 外資：買進 {fmt(f_buy)} / 賣出 {fmt(f_sell)} / 淨額 {f_net:+,}
  {i_emoji} 投信：買進 {fmt(i_buy)} / 賣出 {fmt(i_sell)} / 淨額 {i_net:+,}
  {d_emoji} 自營：買進 {fmt(d_buy)} / 賣出 {fmt(d_sell)} / 淨額 {d_net:+,}

  {total_emoji} 三大法人合計：{total_net:+,} 張
  📅 近3日累計：{total_3day:+,} 張

⚡ 市場訊號：{signal_str}
"""
    send_discord(content=msg)
    print(f"  {name}法人資料已發送")

    print(f"  {name}法人資料已發送")

# 新聞統整
print("\n取得並統整新聞...")
send_discord(content="\n" + "="*50 + "\n📰 今日新聞統整分析\n" + "="*50)

all_news = {'wantgoo': [], 'playwright': []}

wantgoo_news = get_wantgoo_news(6)
all_news['wantgoo'] = wantgoo_news
print(f"  玩股網: {len(wantgoo_news)} 則")

playwright_news = get_news_playwright()
all_news['playwright'] = playwright_news
print(f"  Playwright: {len(playwright_news)} 來源")

themes = consolidate_news(all_news)

valid_themes = []
for theme_name, news_list in themes.items():
    if news_list:
        analysis = analyze_theme_impact(theme_name, news_list)
        if analysis:
            valid_themes.append(analysis)

for t in valid_themes:
    affected_str = ' / '.join(t['affected'][:4])
    impacts_str = '\n   - '.join(t['impacts'])
    key_news = '\n   '.join([f"- {n[:40]}..." for n in t['key_news'][:2]])
    
    # 主題 emoji
    theme_emojis = {
        '地緣政治/中東': '🌍',
        '半導體/科技': '💻',
        '中國/陸股': '🇨🇳',
        '台灣宏觀': '🇹🇼',
        '能源/原物料': '⛽',
        '其他': '📌'
    }
    theme_emoji = theme_emojis.get(t['theme'], '📌')
    
    # 簡化影響類股顯示
    affected_short = ' / '.join(t['affected'][:3])
    
    msg = f"""
{theme_emoji}【{t['theme']}】({t['news_count']}則)

📰 {key_news}

💡 {impacts_str}

📊 影響：{affected_short}
"""
    send_discord(content=msg)
    print(f"  發送: {t['theme']}")

# 總結
summary = f"""
╔════════════════════════════════════════╗
║    📋 市場綜合判斷 · 總結報告    ║
╚════════════════════════════════════════╝

📊【三檔股票技術比較】

▸ 台積電
  現價 {data_all['2330.TW']['current']:.0f} 元｜{"📈多頭" if data_all['2330.TW']['ma5'] > data_all['2330.TW']['ma20'] else "📉空頭"}｜RSI {data_all['2330.TW']['rsi']:.1f}
  操作建議：觀望，嚴守停損

▸ 旺矽
  現價 {data_all['6223.TWO']['current']:.0f} 元｜{"📈多頭" if data_all['6223.TWO']['ma5'] > data_all['6223.TWO']['ma20'] else "📉空頭"}｜RSI {data_all['6223.TWO']['rsi']:.1f}
  操作建議：不追高，注意高位風險

▸ 台特化
  現價 {data_all['4772.TWO']['current']:.0f} 元｜{"📈多頭" if data_all['4772.TWO']['ma5'] > data_all['4772.TWO']['ma20'] else "📉空頭"}｜RSI {data_all['4772.TWO']['rsi']:.1f}
  操作建議：減碼，留意報價波動

{"⚠️【今日市場氛圍】地緣政治風險 - 中東局勢" if any(t['theme'] == '地緣政治/中東' for t in valid_themes) else "✅【今日市場氛圍】相對平靜"}

⚠️【風險提示】
🚨 國際局勢不確定性高，請嚴守停損設定
🚨 成交量持續萎縮，指數難有表現
🚨 美中科技戰 + 中東油價需持續關注
"""
send_discord(content=summary)
print("\n總結已發送")
print("\n完成！")
