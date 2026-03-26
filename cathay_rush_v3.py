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
    print("打開國泰網頁...")
    driver.get("https://www.cathaybk.com.tw/promotion/")
    time.sleep(3)
    
    # 填入身份證字號
    print("填入身份證字號...")
    driver.find_element(By.ID, "ID").send_keys("F226228024")
    
    # 填入出生年月日
    print("填入出生年月日...")
    driver.find_element(By.ID, "BirthDate").send_keys("19860506")
    
    # 勾選
    print("勾選...")
    try:
        checkboxes = driver.find_elements(By.CSS_SELECTOR, ".checkbox.beValidate")
        for cb in checkboxes:
            driver.execute_script("arguments[0].click();", cb)
            print("  已勾選")
    except Exception as e:
        print(f"勾選失敗: {e}")
    
    print("\n✅ 第一步完成！請提供：驗證碼-刷新時間-活動關鍵字")
    print("例如：1234-15:59:59.800-蝦皮\n")
    
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
                
                # 填入驗證碼並送出
                if captcha:
                    print(f"填入驗證碼: {captcha}")
                    driver.find_element(By.ID, "Captcha").send_keys(captcha)
                    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
                    time.sleep(2)
                    print("✅ 已送出驗證！")
                
                # 刷新並查找活動
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
                                time.sleep(0.1)
                                break
                            
                            time.sleep(0.01)
                    except Exception as e:
                        print(f"時間解析錯誤: {e}")
                
                # 查找活動關鍵字
                if keyword:
                    print(f"查找包含'{keyword}'的活動...")
                    
                    try:
                        # 找到所有 class="link campaign-name" 的元素
                        campaigns = driver.find_elements(By.CSS_SELECTOR, ".link.campaign-name")
                        
                        found = False
                        
                        for campaign in campaigns:
                            try:
                                text = campaign.text.strip()
                                if keyword in text:
                                    print(f"✅ 找到活動: {text}")
                                    
                                    # 找同行的按鈕
                                    # 先找父級 div，然後找同層級的 td
                                    try:
                                        # 找到 td.wtitle
                                        parent_td = campaign.find_element(By.XPATH, "./ancestor::div[contains(@class, 'td')][1]")
                                        # 找同層級的 td.tdbtnw
                                        sibling_td = parent_td.find_element(By.XPATH, "./following-sibling::div[contains(@class, 'tdbtnw')]")
                                        # 在 td.tdbtnw 裡找按鈕
                                        btn = sibling_td.find_element(By.CSS_SELECTOR, ".btn-sign")
                                        
                                        if btn.is_displayed() and btn.is_enabled():
                                            print("✅ 找到按鈕，點擊！")
                                            btn.click()
                                            print("✅ 成功點擊登錄按鈕！")
                                            found = True
                                            break
                                    except Exception as e:
                                        print(f"找按鈕失敗: {e}")
                                    
                            except:
                                continue
                        
                        if not found:
                            print(f"❌ 找不到包含'{keyword}'的活動")
                            print("（瀏覽器保持開啟）")
                        
                    except Exception as e:
                        print(f"查找失敗: {e}")
                        print("（瀏覽器保持開啟）")
                
                # 清空檔案
                last_content = content
                with open(CAPTCHA_FILE, "w") as f:
                    f.write("")
                
                print("\n等待下一個命令...")
                
        except FileNotFoundError:
            pass
        
        time.sleep(0.5)
        
except Exception as e:
    print(f"錯誤：{e}")
    print("（瀏覽器保持開啟）")
    # 不關閉瀏覽器，讓用戶查看
    
    while True:
        time.sleep(10)
