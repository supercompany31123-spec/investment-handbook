from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# 验证码文件路径
CAPTCHA_FILE = "/tmp/captcha.txt"
LAST_CAPTCHA = ""

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

try:
    # 打開網頁
    print("打開網頁...")
    driver.get("https://www.cathaybk.com.tw/promotion/")
    time.sleep(3)
    
    # 填入身份證字號
    print("填入身份證字號...")
    driver.find_element(By.ID, "ID").send_keys("A129013019")
    
    # 填入出生年月日
    print("填入出生年月日...")
    driver.find_element(By.ID, "BirthDate").send_keys("19870419")
    
    # 勾選
    print("勾選...")
    driver.find_element(By.XPATH, "//label[@for='CheckAgreement']").click()
    
    print("\n✅ 第一步完成！")
    print("請在 Discord 告訴我驗證碼，然後把驗證碼寫入 /tmp/captcha.txt")
    print("（例如：echo 1234 > /tmp/captcha.txt）")
    print("Python 會每秒檢查一次文件，檢測到就會立刻填入並送出！\n")
    
    # 進入等待循環
    while True:
        try:
            with open(CAPTCHA_FILE, "r") as f:
                captcha = f.read().strip()
            
            # 如果文件內容變了，就填入並送出
            if captcha and captcha != LAST_CAPTCHA:
                print(f"檢測到驗證碼：{captcha}")
                
                # 填入驗證碼
                driver.find_element(By.ID, "Captcha").send_keys(captcha)
                
                # 點擊確認送出
                driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
                
                print("✅ 已送出！")
                
                # 刪除文件內容，避免重複
                LAST_CAPTCHA = captcha
                with open(CAPTCHA_FILE, "w") as f:
                    f.write("")
                
                break
                
        except FileNotFoundError:
            pass
        
        time.sleep(1)  # 每秒檢查一次
        
except Exception as e:
    print(f"錯誤：{e}")
    
finally:
    input("\n按 Enter 結束...")
    driver.quit()
