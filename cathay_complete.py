from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 設定 Chrome 選項
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("detach", True)  # 保持瀏覽器開啟

# 建立瀏覽器驅動
driver = webdriver.Chrome(options=chrome_options)

try:
    # 打開網頁
    print("第一步：打開網頁...")
    driver.get("https://www.cathaybk.com.tw/promotion/")
    time.sleep(3)
    
    print(f"網頁標題：{driver.title}")
    
    # 填入身份證字號 id="ID"
    print("第二步：填入身份證字號...")
    id_input = driver.find_element(By.ID, "ID")
    id_input.send_keys("A129013019")
    print("已填入：A129013019")
    
    # 填入出生年月日 id="BirthDate"
    print("第三步：填入出生年月日...")
    birth_input = driver.find_element(By.ID, "BirthDate")
    birth_input.send_keys("19870419")
    print("已填入：19870419")
    
    # 填入驗證碼 id="Captcha"
    print("第四步：填入驗證碼...")
    # 請替換為正確的驗證碼
    captcha = input("請輸入驗證碼：")
    captcha_input = driver.find_element(By.ID, "Captcha")
    captcha_input.send_keys(captcha)
    print(f"已填入：{captcha}")
    
    # 勾選個資同意 (label for="CheckAgreement")
    print("第五步：勾選個資同意...")
    # 嘗試多種方式找到勾選框
    try:
        checkbox = driver.find_element(By.XPATH, "//label[@for='CheckAgreement']")
        checkbox.click()
        print("已勾選（透過 label）")
    except:
        try:
            checkbox = driver.find_element(By.ID, "CheckAgreement")
            checkbox.click()
            print("已勾選（透過 ID）")
        except:
            print("找不到勾選框，嘗試用 XPath 找 input")
            checkbox = driver.find_element(By.XPATH, "//input[@id='CheckAgreement']")
            checkbox.click()
            print("已勾選")
    
    # 點擊確認送出
    print("點擊確認送出...")
    submit_button = driver.find_element(By.ID, "submitBtn")
    submit_button.click()
    
    # 截圖
    time.sleep(2)
    driver.save_screenshot("/Users/wuxiaoyin/.openclaw/workspace/final.png")
    print("截圖已儲存：final.png")
    
    print("\n✅ 完成！")
    print("瀏覽器會保持開啟")
    
    while True:
        time.sleep(1)

except Exception as e:
    print(f"發生錯誤：{e}")
    import traceback
    traceback.print_exc()
    driver.save_screenshot("/Users/wuxiaoyin/.openclaw/workspace/error.png")
    print("錯誤截圖已儲存：error.png")
    
finally:
    pass  # 不要關閉瀏覽器
