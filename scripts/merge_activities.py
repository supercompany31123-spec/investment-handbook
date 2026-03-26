#!/usr/bin/env python3
"""
合併 bank_activities.html 和 activities.html 到 shrimp_report.html
"""

import os
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(SCRIPT_DIR)
BANK_FILE = os.path.join(WORKSPACE_DIR, 'bank_activities.html')
ACTIVITIES_FILE = os.path.join(WORKSPACE_DIR, 'activities.html')
OUTPUT_FILE = os.path.join(WORKSPACE_DIR, 'shrimp_report.html')

def extract_body_content(html_content, pattern):
    """擷取 HTML 中的主要內容區塊"""
    match = re.search(pattern, html_content, re.DOTALL)
    return match.group(1) if match else ""

def create_merged_html(bank_content, activities_content):
    """建立合併後的 HTML"""
    
    # 提取 bank activities 的內容
    bank_body = extract_body_content(bank_content, r'<div class="sidebar">(.*?)<div class="footer">')
    bank_main = extract_body_content(bank_content, r'<div class="main-content">(.*?)<div class="footer">')
    
    # 提取 activities 的內容
    activities_body = extract_body_content(activities_content, r'<div class="sidebar">(.*?)<div class="main-content">')
    activities_main = extract_body_content(activities_content, r'<div class="main-content">(.*?)</div>\s*</div>\s*</div>\s*</div>\s*<script>')
    
    merged_html = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>活動整理 - 信用卡 & 富宇</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: "PingFang TC", "Microsoft JhengHei", sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; display: flex; min-height: 80vh; }
        .tabs { width: 200px; background: #2c3e50; padding: 20px 0; display: flex; flex-direction: column; border-radius: 20px 0 0 20px; }
        .tabs h2 { color: white; font-size: 1.1em; padding: 0 20px 20px; border-bottom: 1px solid #34495e; margin-bottom: 20px; }
        .tab-btn { padding: 15px 20px; color: #bdc3c7; cursor: pointer; transition: all 0.3s; border: none; background: none; text-align: left; font-size: 1em; display: flex; align-items: center; gap: 10px; }
        .tab-btn:hover { background: #34495e; color: white; }
        .tab-btn.active { background: #667eea; color: white; }
        .tab-btn .icon { font-size: 1.3em; }
        .content-wrapper { flex: 1; display: none; overflow: hidden; }
        .content-wrapper.active { display: flex; }
        .container-inner { display: flex; width: 100%; background: white; border-radius: 0 20px 20px 0; overflow: hidden; flex: 1; }
        .sidebar { width: 220px; background: #f8f9fa; padding: 20px; border-right: 1px solid #eee; }
        .sidebar h3 { font-size: 0.95em; color: #333; margin-bottom: 12px; margin-top: 15px; }
        .sidebar h3:first-child { margin-top: 0; }
        .filter-group label { display: block; padding: 8px 12px; margin-bottom: 5px; border-radius: 8px; cursor: pointer; transition: all 0.3s; color: #555; font-size: 0.9em; }
        .filter-group label:hover { background: #e9ecef; }
        .filter-group input[type="checkbox"] { display: none; }
        .filter-group label span { display: block; padding: 8px 12px; margin-bottom: 5px; border-radius: 8px; background: white; transition: all 0.3s; font-size: 0.9em; }
        .bank .filter-group input[type="checkbox"]:checked + span { background: #667eea; color: white; }
        .activities .filter-group input[type="checkbox"]:checked + span { background: #9d8854; color: white; }
        .select-wrapper { margin-bottom: 15px; }
        .month-select, .status-select { width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #ddd; font-size: 0.95em; background: white; cursor: pointer; }
        .main-content { flex: 1; padding: 25px; max-height: 90vh; overflow-y: auto; }
        .header { color: white; padding: 30px; text-align: center; border-radius: 20px 20px 0 0; margin: -25px -25px 20px -25px; }
        .bank .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .activities .header { background: linear-gradient(135deg, #9d8854 0%, #6b5a3e 100%); }
        .header h1 { font-size: 1.6em; margin-bottom: 8px; }
        .header p { opacity: 0.9; font-size: 0.95em; }
        .bank-section, .source-section { padding: 15px 0; border-bottom: 1px solid #eee; }
        .section-title { font-size: 1.4em; color: #333; margin-bottom: 18px; display: flex; align-items: center; gap: 10px; }
        .platform { margin-bottom: 22px; }
        .platform-name { font-size: 1.1em; margin-bottom: 12px; font-weight: bold; }
        .bank .platform-name { color: #667eea; }
        .activities .platform-name { color: #9d8854; }
        .activity { background: #f8f9fa; border-radius: 12px; padding: 15px; margin-bottom: 12px; border-left: 4px solid; }
        .bank .activity { border-left-color: #667eea; }
        .activities .activity { border-left-color: #9d8854; }
        .activity-title { font-weight: bold; font-size: 1em; color: #333; margin-bottom: 8px; }
        .activity-info { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 6px; font-size: 0.85em; color: #555; }
        .activity-info span { display: flex; align-items: center; gap: 4px; }
        .label { font-weight: bold; color: #333; }
        .tag { display: inline-block; color: white; padding: 2px 7px; border-radius: 4px; font-size: 0.75em; margin-right: 4px; }
        .bank .tag { background: #667eea; }
        .activities .tag { background: #9d8854; }
        .footer { background: #f8f9fa; padding: 15px; text-align: center; color: #666; font-size: 0.8em; margin-top: 20px; }
        .hidden { display: none !important; }
        @media (max-width: 768px) { .container { flex-direction: column; } .tabs { width: 100%; flex-direction: row; padding: 0; border-radius: 20px 20px 0 0; overflow-x: auto; } .tabs h2 { display: none; } .tab-btn { padding: 12px 15px; white-space: nowrap; } .sidebar { width: 100%; border-right: none; border-bottom: 1px solid #eee; } .activity-info { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="tabs">
            <h2>📋 活動總覽</h2>
            <button class="tab-btn active" onclick="switchTab('bank')">
                <span class="icon">💳</span> 信用卡活動
            </button>
            <button class="tab-btn" onclick="switchTab('activities')">
                <span class="icon">🏠</span> 活動追蹤
            </button>
        </div>

        <!-- 信用卡活動內容 -->
        <div class="content-wrapper bank active" id="content-bank">
            <div class="container-inner">
                <div class="sidebar">
                    <h3>📅 選擇月份</h3>
                    <div class="select-wrapper">
                        <select class="month-select" id="monthSelect" onchange="filterByMonth()">
                            <option value="2026-03" selected>2026年3月（最新）</option>
                        </select>
                    </div>
                    <h3>🏷️ 篩選電商平台</h3>
                    <div class="filter-group">
                        <label><input type="checkbox" id="filter-shopee" checked onchange="filterActivities()"><span>🦐 蝦皮購物</span></label>
                        <label><input type="checkbox" id="filter-momo" checked onchange="filterActivities()"><span>🛍️ momo購物</span></label>
                        <label><input type="checkbox" id="filter-coupang" checked onchange="filterActivities()"><span>🚀 酷澎</span></label>
                    </div>
                    <h3>🏦 篩選銀行</h3>
                    <div class="filter-group">
                        <label><input type="checkbox" id="filter-esun" checked onchange="filterActivities()"><span>🏦 玉山銀行</span></label>
                        <label><input type="checkbox" id="filter-cathay" checked onchange="filterActivities()"><span>💳 國泰世華</span></label>
                    </div>
                </div>
                <div class="main-content">
                    <div class="header">
                        <h1>💳 信用卡電商活動整理</h1>
                        <p>玉山銀行 x 國泰世華銀行</p>
                    </div>
                    ''' + bank_main + '''
                    <div class="footer">
                        <p>⚠️ 活動內容可能隨時變動，請以官方公告為準</p>
                        <p>資料更新日期：每月1號</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- 富宇活動內容 -->
        <div class="content-wrapper activities" id="content-activities">
            <div class="container-inner">
                <div class="sidebar">
                    <h3>🏷️ 篩選來源</h3>
                    <div class="filter-group">
                        <label><input type="checkbox" id="filter-website2" checked onchange="filterActivities2()"><span>🏠 富宇官網</span></label>
                    </div>
                </div>
                <div class="main-content">
                    <div class="header">
                        <h1>🏠 富宇活動整理</h1>
                        <p>家族活動 / 課程體驗 / 優惠計畫</p>
                    </div>
                    ''' + activities_main + '''
                    <div class="footer">
                        <p>⚠️ 活動內容可能隨時變動，請以官方公告為準</p>
                        <p>資料更新日期：2026年3月16日</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.closest('.tab-btn').classList.add('active');
            document.querySelectorAll('.content-wrapper').forEach(content => content.classList.remove('active'));
            document.getElementById('content-' + tabName).classList.add('active');
        }

        function filterByMonth() {
            const selectedMonth = document.getElementById('monthSelect').value;
            document.querySelectorAll('.month-group').forEach(group => {
                group.classList.toggle('hidden', group.getAttribute('data-month') !== selectedMonth);
            });
            filterActivities();
        }
        
        function filterActivities() {
            const showShopee = document.getElementById('filter-shopee').checked;
            const showMomo = document.getElementById('filter-momo').checked;
            const showCoupang = document.getElementById('filter-coupang').checked;
            const showEsun = document.getElementById('filter-esun').checked;
            const showCathay = document.getElementById('filter-cathay').checked;

            document.querySelectorAll('#content-bank .platform').forEach(platform => {
                const platformName = platform.getAttribute('data-platform');
                if (platformName === 'shopee' && !showShopee) platform.classList.add('hidden');
                else if (platformName === 'momo' && !showMomo) platform.classList.add('hidden');
                else if (platformName === 'coupang' && !showCoupang) platform.classList.add('hidden');
                else platform.classList.remove('hidden');
            });

            document.querySelectorAll('#content-bank .bank-section').forEach(bank => {
                const bankName = bank.getAttribute('data-bank');
                if (bankName === 'esun' && !showEsun) bank.classList.add('hidden');
                else if (bankName === 'cathay' && !showCathay) bank.classList.add('hidden');
                else bank.classList.remove('hidden');
            });
        }

        function filterActivities2() {
            const showWebsite = document.getElementById('filter-website2') ? document.getElementById('filter-website2').checked : true;
            document.querySelectorAll('#content-activities .source-section').forEach(source => {
                source.classList.toggle('hidden', !showWebsite);
            });
        }
        
        filterByMonth();
    </script>
</body>
</html>'''
    
    return merged_html

def main():
    print("=== 開始合併 HTML ===")
    print(f"時間: {datetime.now()}")
    print(f"來源1: {BANK_FILE}")
    print(f"來源2: {ACTIVITIES_FILE}")
    print(f"輸出: {OUTPUT_FILE}")
    
    try:
        with open(BANK_FILE, 'r', encoding='utf-8') as f:
            bank_content = f.read()
        
        with open(ACTIVITIES_FILE, 'r', encoding='utf-8') as f:
            activities_content = f.read()
        
        merged = create_merged_html(bank_content, activities_content)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(merged)
        
        print("✅ 合併完成！")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        exit(1)

if __name__ == '__main__':
    main()
