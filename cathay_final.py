from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get("https://www.cathaybk.com.tw/promotion/")
    time.sleep(3)
    
    # 填入身份證和出生年月日
    driver.find_element(By.ID, "ID").send_keys("A129013019")
    driver.find_element(By.ID, "BirthDate").send_keys("19870419")
    driver.find_element(By.XPATH, "//label[@for='CheckAgreement']").click()
    
    print("第一步完成！請在下方輸入驗證碼：")
    
    # 等待用戶輸入驗證碼
    captcha = input("驗證碼: ")
    
    # 填入驗證碼
    driver.find_element(By.ID, "Captcha").send_keys(captcha)
    
    # 點擊確認送出
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    
    print("完成！")
    input("按 Enter 結束...")
    
except Exception as e:
    print(f"錯誤：{e}")
    
finally:
    driver.quit()
