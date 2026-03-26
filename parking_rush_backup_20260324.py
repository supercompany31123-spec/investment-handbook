from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions
import time
import random

def human_delay():
    """模擬人類輸入延遲"""
    time.sleep(random.uniform(0.3, 0.8))

def type_like_human(element, text):
    """模擬人類輸入文字"""
    driver.execute_script("arguments[0].click();", element)
    time.sleep(random.uniform(0.3, 0.6))
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.15, 0.35))

def js_click(driver, element):
    """用 JavaScript 點擊"""
    driver.execute_script("arguments[0].click();", element)
    time.sleep(random.uniform(0.3, 0.5))

# 高強度反檢測設置
chrome_options = ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-plugins")
chrome_options.add_argument("--disable-images")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-first-run")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)

# 移除自動化檢測
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['zh-TW', 'zh', 'en-US', 'en'] });
        window.chrome = { runtime: {} };
    """
})

try:
    print("打開停車場預約網頁...")
    driver.get("https://pcc.youparking.com.tw/parkingreserve/#/reservedindex/1")
    
    print("  ⏳ 等待頁面載入...")
    time.sleep(5)
    
    print("  🌐 模擬人類瀏覽頁面...")
    for _ in range(3):
        driver.execute_script(f"window.scrollBy(0, {random.randint(100, 300)})")
        time.sleep(random.uniform(0.5, 1.0))
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(2)
    
    # 步驟1: 勾選
    print("步驟1: 勾選...")
    try:
        checkbox = driver.find_element(By.CSS_SELECTOR, ".v-input--selection-controls__ripple")
        js_click(driver, checkbox)
        print("  ✅ 已勾選")
        print("  ⏳ 等待驗證...")
        time.sleep(random.uniform(2, 3))
    except Exception as e:
        print(f"  ❌ 勾選失敗: {e}")
    
    # 步驟2: 點擊按鈕
    print("步驟2: 點擊按鈕...")
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, ".v-btn__content")
        for btn in buttons:
            if btn.is_displayed():
                js_click(driver, btn)
                print("  ✅ 已點擊")
                break
        time.sleep(random.uniform(2, 3))
    except Exception as e:
        print(f"  ❌ 點擊失敗: {e}")
    
    # 步驟3: 找到今天的日期行，然後點擊預約按鈕
    print("步驟3: 查找預約按鈕...")
    try:
        from datetime import datetime, timedelta
        import pytz
        taipei_tz = pytz.timezone('Asia/Taipei')
        target_date = datetime.now(taipei_tz) + timedelta(days=20)
        today = target_date.strftime("%Y-%m-%d")
        print(f"  目標日期: {today}")
        
        rows = driver.find_elements(By.CSS_SELECTOR, "tr")
        found = False
        
        for row in rows:
            try:
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                for cell in cells:
                    if today in cell.text:
                        print(f"  ✅ 找到日期行: {cell.text[:20]}...")
                        try:
                            btn = cell.find_element(By.XPATH, "./following-sibling::td//button")
                            if btn.is_displayed() and btn.is_enabled():
                                js_click(driver, btn)
                                print("  ✅ 已點擊預約按鈕")
                                found = True
                                break
                        except Exception as e:
                            print(f"  ❌ 找不到預約按鈕: {e}")
                        if found:
                            break
                if found:
                    break
            except:
                continue
        
        if not found:
            print("  ❌ 找不到今天的日期")
    except Exception as e:
        print(f"  ❌ 查找失敗: {e}")
    
    print("  ⏳ 等待表單加載...")
    time.sleep(random.uniform(2, 3))
    
    # 步驟4: 填入數量
    print("步驟4: 填入數量...")
    try:
        driver.execute_script("window.scrollBy(0, 200)")
        time.sleep(0.5)
        
        quantity_input = driver.find_element(By.CSS_SELECTOR, "input[id^='input-'][maxlength='2']")
        quantity_input.click()
        human_delay()
        quantity_input.send_keys(Keys.BACKSPACE)
        human_delay()
        type_like_human(quantity_input, "3")
        print("  ✅ 已填入數量")
        time.sleep(random.uniform(1, 2))
    except Exception as e:
        print(f"  ❌ 填入數量失敗: {e}")
    
    # 步驟5: 填入姓名
    print("步驟5: 填入姓名...")
    try:
        driver.execute_script("window.scrollBy(0, 100)")
        time.sleep(0.3)
        
        name_input = driver.find_element(By.CSS_SELECTOR, "input[id^='input-'][maxlength='20']")
        type_like_human(name_input, "吳澤旻")
        print("  ✅ 已填入姓名")
        time.sleep(random.uniform(1, 2))
    except Exception as e:
        print(f"  ❌ 填入姓名失敗: {e}")
    
    # 步驟6: 填入車牌
    print("步驟6: 填入車牌...")
    try:
        driver.execute_script("window.scrollBy(0, 100)")
        time.sleep(0.3)
        
        plate_input = driver.find_element(By.CSS_SELECTOR, "input[id^='input-'][maxlength='10']")
        type_like_human(plate_input, "BZU-0560")
        print("  ✅ 已填入車牌")
        time.sleep(random.uniform(1, 2))
    except Exception as e:
        print(f"  ❌ 填入車牌失敗: {e}")
    
    # 模擬人類滾動網頁
    print("  🌐 模擬人類滾動網頁...")
    for i in range(3):
        driver.execute_script(f"window.scrollBy(0, {random.randint(100, 300)})")
        time.sleep(random.uniform(0.3, 0.6))
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(random.uniform(1, 2))
    
    # 步驟7: 點擊送出按鈕
    print("步驟7: 點擊送出...")
    try:
        driver.execute_script("window.scrollBy(0, 200)")
        time.sleep(0.5)
        
        spans = driver.find_elements(By.CSS_SELECTOR, "span.v-btn__content")
        for span in spans:
            if "送出" in span.text:
                js_click(driver, span)
                print("  ✅ 已點擊送出")
                break
    except Exception as e:
        print(f"  ❌ 點擊送出失敗: {e}")
    
    print("\n✅ 預約流程完成！")
    
except Exception as e:
    print(f"錯誤：{e}")
    
finally:
    print("\n腳本結束")
    print("瀏覽器保持開啟60秒以便查看結果...")
    time.sleep(60)
    driver.quit()
