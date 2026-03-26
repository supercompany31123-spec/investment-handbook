from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# 設定 Chrome 選項
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 建立瀏覽器驅動
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
    
    print("\n✅ 基本資料已填入")
    print("請在終端機輸入驗證碼，然後按 Enter：")
    print("（不要關閉瀏覽器）\n")
    
    # 等待用戶輸入驗證碼
    captcha = input("驗證碼: ")
    
    print(f"\n填入驗證碼: {captcha}")
    driver.find_element(By.ID, "Captcha").send_keys(captcha)
    
    # 勾選
    print("勾選個資同意...")
    driver.find_element(By.XPATH, "//label[@for='CheckAgreement']").click()
    
    # 點擊確認送出
    print("點擊確認送出...")
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    
    time.sleep(3)
    driver.save_screenshot("/Users/wuxiaoyin/.openclaw/workspace/final_result.png")
    print("\n✅ 完成！截圖已儲存")
    
    input("\n按 Enter 結束...")
        
except Exception as e:
    print(f"發生錯誤：{e}")
    
finally:
    driver.quit()
