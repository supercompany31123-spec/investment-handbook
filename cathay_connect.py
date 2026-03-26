from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

# 連接到已存在的 Chrome（調試模式）
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

print("連接到已存在的 Chrome...")
driver = webdriver.Chrome(options=chrome_options)

try:
    # 前往網頁
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
    print("請查看瀏覽器上的驗證碼，告訴我後我會立刻填入並送出")
    print("（不要關閉這個終端機視窗，也不要關閉瀏覽器）\n")
    
    # 保持程式執行
    while True:
        time.sleep(1)
        
except Exception as e:
    print(f"發生錯誤：{e}")
    
finally:
    driver.quit()
