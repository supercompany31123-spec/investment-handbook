from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# 設定 Chrome 選項
chrome_options = Options()
# chrome_options.add_argument("--headless")
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
    id_input = driver.find_element(By.ID, "ID")
    id_input.send_keys("A129013019")
    
    # 填入出生年月日
    print("填入出生年月日...")
    birth_input = driver.find_element(By.ID, "BirthDate")
    birth_input.send_keys("19870419")
    
    # 填入驗證碼
    print("填入驗證碼 8573...")
    captcha_input = driver.find_element(By.ID, "Captcha")
    captcha_input.send_keys("8573")
    
    # 勾選個資同意
    print("勾選個資同意...")
    checkbox = driver.find_element(By.ID, "CheckAgreement")
    checkbox.click()
    
    # 點擊確認送出
    print("點擊確認送出...")
    submit_button = driver.find_element(By.ID, "submitBtn")
    submit_button.click()
    
    # 截圖
    time.sleep(2)
    driver.save_screenshot("/Users/wuxiaoyin/.openclaw/workspace/done.png")
    print("截圖已儲存：done.png")
    
    print("\n✅ 完成！")
    print("瀏覽器會保持開啟")
    
    while True:
        time.sleep(1)

except Exception as e:
    print(f"發生錯誤：{e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()
