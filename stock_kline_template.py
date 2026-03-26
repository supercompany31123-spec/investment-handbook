# K線圖繪圖設定
# 模板代碼

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
import yfinance as yf
import pandas as pd
import numpy as np

# === 設定參數 ===
STOCK_CODE = '6223.TWO'  # 股票代碼
PERIOD = "3mo"            # 資料週期: 1mo, 2mo, 3mo, 6mo, 1y 等
FONT_PATH = '/System/Library/Fonts/STHeiti Medium.ttc'  # 中文字體
BAR_WIDTH = 0.35
BG_COLOR = '#2d2d2d'  # 深灰色背景

# === 繪圖函數 ===
def plot_kline(stock_code, period, output_path):
    # 字體
    font_prop = FontProperties(fname=FONT_PATH)
    
    # 取得數據
    df = yf.download(stock_code, period=period, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 計算均線
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA10'] = df['Close'].rolling(window=10).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    # 計算 MACD
    exp12 = df['Close'].ewm(span=12, adjust=False).mean()
    exp26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp12 - exp26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal']
    
    # 設定
    x = np.arange(len(df))
    
    # 創建圖表
    fig = plt.figure(figsize=(14, 12), facecolor=BG_COLOR)
    gs = fig.add_gridspec(3, 1, height_ratios=[5, 1, 1], hspace=0)
    
    # === 第一個面板: K線 + 均線 ===
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(BG_COLOR)
    
    for i in range(len(df)):
        open_p = df['Open'].iloc[i]
        close_p = df['Close'].iloc[i]
        high_p = df['High'].iloc[i]
        low_p = df['Low'].iloc[i]
        
        if close_p >= open_p:
            color = '#ff0000'
        else:
            color = '#00c000'
        
        ax1.plot([i, i], [low_p, high_p], color=color, linewidth=0.8)
        body_bottom = min(open_p, close_p)
        body_height = abs(close_p - open_p)
        ax1.bar(i, body_height, bottom=body_bottom, width=BAR_WIDTH, color=color, edgecolor=color)
    
    ax1.plot(x, df['MA5'].values, color='#FFD700', linewidth=1)
    ax1.plot(x, df['MA10'].values, color='#4169E1', linewidth=1)
    ax1.plot(x, df['MA20'].values, color='#9370DB', linewidth=1)
    
    ax1.set_title(f'{stock_code} K線圖', fontproperties=font_prop, fontsize=14, color='white')
    ax1.set_ylabel('股價', fontproperties=font_prop, color='white')
    
    # 自定義圖例 - 對應顏色
    legend_elements = [
        Line2D([0], [0], color='#FFD700', lw=1, label='MA5'),
        Line2D([0], [0], color='#4169E1', lw=1, label='MA10'),
        Line2D([0], [0], color='#9370DB', lw=1, label='MA20'),
    ]
    ax1.legend(handles=legend_elements, loc='upper left', fontsize=8, facecolor=BG_COLOR, labelcolor='white')
    
    ax1.grid(True, alpha=0.3, color='gray')
    ax1.set_xlim(-1, len(df))
    ax1.tick_params(axis='x', labelbottom=False)
    ax1.tick_params(axis='y', labelcolor='white')
    for spine in ax1.spines.values():
        spine.set_color('white')
    
    # === 第二個面板: MACD ===
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.set_facecolor(BG_COLOR)
    
    hist_data = df['Histogram'].values
    colors_hist = ['#ff0000' if h >= 0 else '#00c000' for h in hist_data]
    ax2.bar(x, hist_data, width=BAR_WIDTH, color=colors_hist, edgecolor='none')
    ax2.plot(x, df['MACD'].values, color='#FFD700', linewidth=1)
    ax2.plot(x, df['Signal'].values, color='#4169E1', linewidth=1)
    ax2.axhline(y=0, color='white', linewidth=0.5)
    ax2.set_ylabel('MACD', fontproperties=font_prop, fontsize=9, color='white')
    
    # 自定義圖例
    legend_elements2 = [
        Line2D([0], [0], color='#FFD700', lw=1, label='DIF'),
        Line2D([0], [0], color='#4169E1', lw=1, label='Signal'),
    ]
    ax2.legend(handles=legend_elements2, loc='upper left', fontsize=7, facecolor=BG_COLOR, labelcolor='white')
    
    ax2.grid(True, alpha=0.3, color='gray')
    ax2.tick_params(axis='x', labelbottom=False)
    ax2.tick_params(axis='y', labelcolor='white')
    for spine in ax2.spines.values():
        spine.set_color('white')
    
    # === 第三個面板: 成交量 ===
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.set_facecolor(BG_COLOR)
    
    vol_data = df['Volume'].values
    close_data = df['Close'].values
    colors_vol = ['#00c000' if (i == 0 or close_data[i] >= close_data[i-1]) else '#ff0000' for i in range(len(vol_data))]
    ax3.bar(x, vol_data, width=BAR_WIDTH, color=colors_vol, edgecolor='none')
    
    # Y軸除以1000顯示 (1000, 2000, 3000...)
    ax3.set_ylabel('VOL', fontproperties=font_prop, fontsize=9, color='white')
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}'))
    ax3.tick_params(axis='y', labelcolor='white')
    
    ax3.set_xlabel('日期', fontproperties=font_prop, color='white')
    ax3.grid(True, alpha=0.3, color='gray')
    ax3.tick_params(axis='x', labelcolor='white')
    for spine in ax3.spines.values():
        spine.set_color('white')
    
    # X軸日期
    ax3.set_xticks(x[::10])
    ax3.set_xticklabels([d.strftime('%m/%d') for d in df.index[::10]], rotation=45, fontsize=8, color='white')
    
    fig.savefig(output_path, bbox_inches='tight')
    print(f"圖已儲存: {output_path}")

# === 使用範例 ===
if __name__ == "__main__":
    plot_kline('6223.TWO', '3mo', '/Users/wuxiaoyin/.openclaw/workspace/6223_kline.png')
