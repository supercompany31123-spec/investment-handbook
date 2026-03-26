from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# 檔案路徑
CAPTCHA_FILE = "/tmp/captcha.txt"

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--incognito")

driver = webdriver.Chrome(options=chrome_options)

try:
    print("打開網頁...")
    driver.get("https://www.cathaybk.com.tw/promotion/")
    time.sleep(3)
    
    print("填入身份資料...")
    driver.find_element(By.ID, "ID").send_keys("A129013019")
    driver.find_element(By.ID, "BirthDate").send_keys("19870419")
    driver.find_element(By.XPATH, "//label[@for='CheckAgreement']").click()
    
    print("\n✅ 第一步完成！請提供：驗證碼-刷新時間-關鍵字")
    print("例如：1836-15:59:59.800-蝦皮\n")
    
    last_content = ""
    
    while True:
        try:
            with open(CAPTCHA_FILE, "r") as f:
                content = f.read().strip()
            
            if content and content != last_content:
                print(f"\n檢測到輸入: {content}")
                parts = content.split("-")
                
                captcha = parts[0].strip() if len(parts) > 0 else ""
                refresh_time = parts[1].strip() if len(parts) > 1 else ""
                keyword = parts[2].strip() if len(parts) > 2 else ""
                
                if captcha:
                    print(f"填入驗證碼: {captcha}")
                    driver.find_element(By.ID, "Captcha").send_keys(captcha)
                    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
                    time.sleep(2)
                    print("✅ 已送出驗證！")
                
                if refresh_time:
                    print(f"等待刷新時間: {refresh_time}")
                    try:
                        time_parts = refresh_time.split(":")
                        target_hour = int(time_parts[0])
                        target_min = int(time_parts[1])
                        sec_ms = time_parts[2].split(".")
                        target_sec = int(sec_ms[0])
                        target_ms = int(sec_ms[1]) if len(sec_ms) > 1 else 0
                        
                        while True:
                            now = time.localtime()
                            current_hour = now.tm_hour
                            current_min = now.tm_min
                            current_sec = now.tm_sec
                            current_ms = int((time.time() % 1) * 1000)
                            
                            if (current_hour > target_hour or 
                                (current_hour == target_hour and current_min > target_min) or
                                (current_hour == target_hour and current_min == target_min and current_sec > target_sec) or
                                (current_hour == target_hour and current_min == target_min and current_sec == target_sec and current_ms >= target_ms)):
                                print(f"時間到！刷新 ({current_hour}:{current_min}:{current_sec}.{current_ms})")
                                driver.refresh()
                                time.sleep(1)
                                break
                            
                            time.sleep(0.01)
                    except Exception as e:
                        print(f"時間解析錯誤: {e}")
                
                if keyword:
                    print(f"查找包含'{keyword}'的活動...")
                    
                    refresh_count = 0
                    max_refresh = 1
                    
                    while refresh_count <= max_refresh:
                        time.sleep(0.3)
                        
                        try:
                            # 使用新的選擇器結構
                            campaigns = driver.find_elements(By.CSS_SELECTOR, ".campaign-name")
                            
                            success = False
                            
                            for campaign in campaigns:
                                if keyword in campaign.text:
                                    try:
                                        # 找活動名稱的父元素，然後找同層級的按鈕
                                        parent_td = campaign.find_element(
                                            By.XPATH,
                                            "./ancestor::div[contains(@class, 'td')][1]/following-sibling::div"
                                        )
                                        sign_button = parent_td.find_element(By.CSS_SELECTOR, ".btn.btn-sign")
                                        sign_button.click()
                                        print("✅ 成功點擊活動按鈕！")
                                        success = True
                                        break
                                    except Exception as e:
                                        print(f"找到活動但無法點擊按鈕: {e}")
                            
                            if success:
                                print("✅ 成功找到活動按鈕！")
                                print("腳本結束")
                                break
                            else:
                                print(f"找不到包含'{keyword}'的活動")
                                if refresh_count < max_refresh:
                                    print(f"刷新頁面...")
                                    driver.refresh()
                                    time.sleep(1)
                                    refresh_count += 1
                                else:
                                    print("腳本結束")
                                    break
                                
                        except Exception as e:
                            print(f"查找失敗: {e}")
                            print("腳本結束")
                            break
                    
                    if success:
                        break
                
                last_content = content
                with open(CAPTCHA_FILE, "w") as f:
                    f.write("")
                
                print("\n等待下一個命令...")
                
        except FileNotFoundError:
            pass
        
        time.sleep(0.5)
        
except Exception as e:
    print(f"錯誤：{e}")
    
finally:
    print("\n腳本結束")
