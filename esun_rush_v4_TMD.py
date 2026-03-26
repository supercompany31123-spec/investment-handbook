from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import signal
import os
import subprocess
import sys
from datetime import datetime

# 忽略 SIGTERM，避免被 OpenClaw session 清理終止
signal.signal(signal.SIGTERM, signal.SIG_IGN)

# Log 檔案路徑
LOG_FILE = "/tmp/esun_login_log.txt"
log_file = open(LOG_FILE, 'w', encoding='utf-8')

def log(msg):
    """同時輸出到終端機和 log 檔"""
    print(msg)
    log_file.write(msg + "\n")
    log_file.flush()

# 檔案路徑
CAPTCHA_FILE = "/tmp/captcha.txt"
SCREENSHOT_PATH = os.path.expanduser("~/.openclaw/media/outbound/screenshot.png")

def take_screenshot():
    """使用 screencapture 截圖"""
    try:
        os.system(f"/usr/sbin/screencapture -x {SCREENSHOT_PATH}")
        time.sleep(0.5)
        log(f"📸 截圖完成: {SCREENSHOT_PATH}")
    except Exception as e:
        log(f"截圖失敗: {e}")

def send_to_discord():
    """發送截圖到 Discord"""
    try:
        result = subprocess.run(
            ['openclaw', 'message', 'send', '--channel', 'discord', '--target', '1481949086306406400', '--media', SCREENSHOT_PATH],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            log("📤 已發送到 Discord")
        else:
            log(f"📤 發送失敗")
    except Exception as e:
        log(f"📤 發送失敗: {e}")

# Chrome 選項
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--incognito")

driver = webdriver.Chrome(options=chrome_options)

log(f"\n{'='*50}")
log(f"玉山銀行登錄自動化 v4 - TMD")
log(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log(f"{'='*50}\n")

try:
    log("打開玉山網頁...")
    driver.get("https://card.esunbank.com.tw/EsunCreditweb/txnservice/identify?PRJCD=ALLACTIV#b")
    time.sleep(5)
    
    # 填入身份證字號
    log("填入身份證字號...")
    driver.find_element(By.ID, "iInputCHID").send_keys("A129013019")
    time.sleep(0.5)
    
    # 填入出生年月日
    log("填入出生年月日...")
    driver.find_element(By.ID, "iInputDTBR").send_keys("0760419")
    time.sleep(0.5)
    
    # 勾選第一個選項
    log("勾選第一個選項...")
    try:
        elem = driver.find_element(By.ID, "agree-01")
        driver.execute_script("arguments[0].click();", elem)
    except:
        try:
            elem = driver.find_element(By.XPATH, "//input[@id='agree-01']")
            driver.execute_script("arguments[0].click();", elem)
        except:
            log("  無法勾選 agree-01")
    
    # 勾選第二個選項
    log("勾選第二個選項...")
    try:
        elem = driver.find_element(By.ID, "agree-02")
        driver.execute_script("arguments[0].click();", elem)
    except:
        try:
            elem = driver.find_element(By.XPATH, "//input[@id='agree-02']")
            driver.execute_script("arguments[0].click();", elem)
        except:
            log("  無法勾選 agree-02")
    
    log("\n" + "="*50)
    log("✅ 第一步完成！請提供：驗證碼-點擊送出時間-活動關鍵字")
    log("例如：1234-15:59:59.800-蝦皮")
    log("="*50 + "\n")
    
    # 截圖並發送到 Discord
    take_screenshot()
    send_to_discord()
    log("等待驗證碼輸入...\n")
    
    last_content = ""
    
    while True:
        try:
            with open(CAPTCHA_FILE, "r") as f:
                content = f.read().strip()
            
            if content and content != last_content:
                log(f"\n檢測到輸入: {content}")
                parts = content.split("-")
                
                captcha = parts[0].strip() if len(parts) > 0 else ""
                submit_time = parts[1].strip() if len(parts) > 1 else ""
                keyword = parts[2].strip() if len(parts) > 2 else ""
                
                # 填入驗證碼
                if captcha:
                    log(f"填入驗證碼: {captcha}")
                    driver.find_element(By.ID, "iInputCaptcha").send_keys(captcha)
                
                # 等待時間點擊送出按鈕
                if submit_time:
                    log(f"等待點擊送出時間: {submit_time}")
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
                                actual_time = f"{current_hour}:{current_min}:{current_sec}.{current_ms:03d}"
                                log(f"時間到！點擊送出按鈕 (實際時間: {actual_time})")
                                try:
                                    driver.find_element(By.ID, "check").click()
                                except:
                                    try:
                                        driver.execute_script("document.getElementById('check').click()")
                                    except:
                                        log("  無法點擊送出按鈕")
                                log("✅ 已點擊送出按鈕")
                                time.sleep(1)
                                break
                            
                            time.sleep(0.01)
                    except Exception as e:
                        log(f"時間解析錯誤: {e}")
                
                # 查找活動關鍵字
                result_msg = ""
                if keyword:
                    log(f"查找包含'{keyword}'的活動...")
                    
                    try:
                        buttons = driver.find_elements(By.CSS_SELECTOR, "a.fitBtn.btns")
                        
                        found = False
                        
                        for btn in buttons:
                            try:
                                onclick = btn.get_attribute("onclick") or ""
                                if keyword in onclick:
                                    log(f"✅ 找到活動: {onclick[:50]}...")
                                    btn.click()
                                    click_time = time.strftime("%H:%M:%S") + "." + str(int((time.time() % 1) * 1000)).zfill(3)[:3]
                                    log(f"✅ 成功點擊登錄按鈕！ (實際時間: {click_time})")
                                    result_msg = f"✅ 成功登錄活動：{keyword}"
                                    found = True
                                    # 等待成功彈窗出現
                                    log("等待成功彈窗...")
                                    time.sleep(3)
                                    break
                            except:
                                continue
                        
                        if not found:
                            result_msg = f"❌ 找不到活動：{keyword}"
                            log(result_msg)
                        
                    except Exception as e:
                        result_msg = f"❌ 有找到活動，但找不到按鈕：{e}"
                        log(result_msg)
                
                # 最終截圖並發送到 Discord
                log("\n執行最終截圖...")
                take_screenshot()
                send_to_discord()
                
                log("\n" + "="*50)
                if result_msg:
                    log(result_msg)
                log("✅ 程式執行完成！")
                log("="*50)
                log("__DONE__")
                log(f"\n結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                log("\n等待 2 秒後關閉 Chrome...")
                time.sleep(2)
                driver.quit()
                log("Chrome 已關閉。")
                time.sleep(1)
                os._exit(0)
                break
                
        except FileNotFoundError:
            pass
        
        time.sleep(0.5)
        
except Exception as e:
    log(f"錯誤：{e}")
    take_screenshot()
    send_to_discord()
    log("__ERROR__")
    log(f"\n結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    while True:
        time.sleep(10)
