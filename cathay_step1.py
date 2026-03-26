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
    
    # 填入身份證字號
    driver.find_element(By.ID, "ID").send_keys("A129013019")
    
    # 填入出生年月日
    driver.find_element(By.ID, "BirthDate").send_keys("19870419")
    
    # 勾選
    driver.find_element(By.XPATH, "//label[@for='CheckAgreement']").click()
    
    driver.save_screenshot("/Users/wuxiaoyin/.openclaw/workspace/step1.png")
    print("第一步完成！瀏覽器會一直開著")
    
    # 保持瀏覽器開啟
    while True:
        time.sleep(1)
        
except Exception as e:
    print(f"錯誤：{e}")
    
finally:
    # 不關閉
    pass
