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
    print("打開玉山網頁...")
    driver.get("https://card.esunbank.com.tw/EsunCreditweb/txnservice/identify?PRJCD=ALLACTIV#b")
    time.sleep(5)
    
    # 填入身份證字號
    print("填入身份證字號...")
    driver.find_element(By.ID, "iInputCHID").send_keys("A129013019")
    time.sleep(0.5)
    
    # 填入出生年月日
    print("填入出生年月日...")
    driver.find_element(By.ID, "iInputDTBR").send_keys("0760419")
    time.sleep(0.5)
    
    # 勾選第一個選項
    print("勾選第一個選項...")
    try:
        elem = driver.find_element(By.ID, "agree-01")
        driver.execute_script("arguments[0].click();", elem)
    except:
        try:
            elem = driver.find_element(By.XPATH, "//input[@id='agree-01']")
            driver.execute_script("arguments[0].click();", elem)
        except:
            print("  無法勾選 agree-01")
    
    # 勾選第二個選項
    print("勾選第二個選項...")
    try:
        elem = driver.find_element(By.ID, "agree-02")
        driver.execute_script("arguments[0].click();", elem)
    except:
        try:
            elem = driver.find_element(By.XPATH, "//input[@id='agree-02']")
            driver.execute_script("arguments[0].click();", elem)
        except:
            print("  無法勾選 agree-02")
    
    print("\n✅ 第一步完成！請提供：驗證碼-送出時間-活動關鍵字")
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
                submit_time = parts[1].strip() if len(parts) > 1 else ""
                keyword = parts[2].strip() if len(parts) > 2 else ""
                
                # 填入驗證碼
                if captcha:
                    print(f"填入驗證碼: {captcha}")
                    driver.find_element(By.ID, "iInputCaptcha").send_keys(captcha)
                
                # 等待時間點擊送出按鈕
                if submit_time:
                    print(f"等待送出時間: {submit_time}")
                    try:
                        time_parts = submit_time.split(":")
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
                                print(f"時間到！點擊送出按鈕")
                                try:
                                    driver.find_element(By.ID, "check").click()
                                except:
                                    try:
                                        driver.execute_script("document.getElementById('check').click()")
                                    except:
                                        print("  無法點擊送出按鈕")
                                print("✅ 已點擊送出按鈕")
                                time.sleep(1)
                                break
                            
                            time.sleep(0.01)
                    except Exception as e:
                        print(f"時間解析錯誤: {e}")
                
                # 查找活動關鍵字
                if keyword:
                    print(f"查找包含'{keyword}'的活動...")
                    
                    try:
                        # 找到所有 class="fitBtn btns" 的 <a> 元素
                        buttons = driver.find_elements(By.CSS_SELECTOR, "a.fitBtn.btns")
                        
                        found = False
                        
                        for btn in buttons:
                            try:
                                onclick = btn.get_attribute("onclick") or ""
                                if keyword in onclick:
                                    print(f"✅ 找到活動: {onclick[:50]}...")
                                    # 點擊同一個 <a> 元素
                                    btn.click()
                                    print("✅ 成功點擊登錄按鈕！")
                                    found = True
                                    break
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
    
finally:
    print("\n腳本結束")
