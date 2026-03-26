from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

# 設定 Chrome 選項
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 無頭模式（不顯示瀏覽器）
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 建立瀏覽器驅動
driver = webdriver.Chrome(options=chrome_options)

try:
    # 第一步：打開網頁
    print("第一步：打開網頁...")
    driver.get("https://www.cathaybk.com.tw/promotion/")
    time.sleep(3)  # 等待網頁載入
    
    print(f"網頁標題：{driver.title}")
    
    # 第二步：找到 id="ID" 的元素並填入資料
    print("第二步：填入身份證字號...")
    id_input = driver.find_element(By.ID, "ID")
    id_input.clear()
    id_input.send_keys("A129013019")
    print("已填入身份證字號：A129013019")
    
    # 第三步：填入出生年月日 (id="BirthDate")
    print("第三步：填入出生年月日...")
    birth_input = driver.find_element(By.ID, "BirthDate")
    birth_input.clear()
    birth_input.send_keys("19870419")
    print("已填入出生年月日：19870419")
    
    # 第四步：填入驗證碼 (id="Captcha")
    # 注意：每次刷新驗證碼都會變，需要先辨識
    print("第四步：填入驗證碼...")
    # 這裡先留空，等待你告訴我驗證碼
    # 讓我截圖讓你確認目前進度
    driver.save_screenshot("/Users/wuxiaoyin/.openclaw/workspace/step3_done.png")
    print("截圖已儲存：step3_done.png")
    
    print("\n✅ 前三步驟完成！")
    print("請告訴我驗證碼，我會繼續填入並送出")
    print("瀏覽器會保持開啟")
    
    # 保持瀏覽器開啟
    while True:
        time.sleep(1)

except Exception as e:
    print(f"發生錯誤：{e}")
    import traceback
    traceback.print_exc()
    
finally:
    driver.quit()
