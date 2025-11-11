from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import re
from typing import List, Dict, Any


def setup_driver() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def extract_price(price_text: str) -> int:
    try:
        numbers = re.findall(r'\d+', price_text)
        if numbers:
            return int(numbers[-1])
        return 0
    except (ValueError, IndexError):
        return 0


def scrape_books_page(driver: webdriver.Chrome) -> List[Dict[str, Any]]:
    books = []
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-searchbox"))
        )
        
        book_elements = driver.find_elements(By.CSS_SELECTOR, "div.table-td")
        
        for book_element in book_elements:
            try:
                title_element = book_element.find_element(By.CSS_SELECTOR, "h4 a")
                title = title_element.text.strip()
                link = title_element.get_attribute('href')
                
                try:
                    author_elements = book_element.find_elements(By.CSS_SELECTOR, "p.author a")
                    authors = [author.text.strip() for author in author_elements if author.text.strip()]
                    author = ', '.join(authors) if authors else 'N/A'
                except NoSuchElementException:
                    author = 'N/A'
                
                try:
                    price_element = book_element.find_element(By.CSS_SELECTOR, "p.price, .price")
                    price_text = price_element.text
                    price = extract_price(price_text)
                except NoSuchElementException:
                    price = 0
                
                if title and link:
                    books.append({
                        'title': title,
                        'author': author,
                        'price': price,
                        'link': link
                    })
                    
            except NoSuchElementException:
                continue
                
    except TimeoutException:
        print("等待頁面載入逾時")
    
    return books


def scrape_all_books() -> List[Dict[str, Any]]:
    all_books = []
    driver = setup_driver()
    
    try:
        print("正在開啟博客來首頁...")
        driver.get("https://www.books.com.tw/")
        
        print("尋找搜尋框...")
        search_box = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "key"))
        )
        search_box.clear()
        search_box.send_keys("LLM")
        print("已輸入關鍵字 LLM，正在提交搜尋...")
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(3)
        
        print("正在尋找圖書分類選項...")
        
        # 等待搜尋結果頁面完全載入
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.mod_b, div.searchbook, div.mod"))
        )
        
        # 多種可能的圖書分類選擇器
        book_category_selectors = [
            "//label[contains(text(), '圖書')]",
            "//span[contains(text(), '圖書')]",
            "//a[contains(text(), '圖書')]",
            "//li[contains(text(), '圖書')]",
            "//div[contains(text(), '圖書')]",
            "//input[@value='BKA']/../label",
            "//input[@name='cat' and @value='BKA']/../label",
            "//*[contains(text(), '圖書') and contains(text(), '(')]",
            "//label[contains(@for, 'BKA')]",
            "//input[@id='BKA']/../label"
        ]
        
        book_category = None
        for selector in book_category_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.text.strip()
                    if '圖書' in text and ('(' in text or ')' in text):  # 尋找包含圖書和數量的文字
                        if element.is_displayed() and element.is_enabled():
                            book_category = element
                            print(f"找到圖書分類選項: '{text}' 使用選擇器: {selector}")
                            break
                if book_category:
                    break
            except Exception as e:
                print(f"嘗試選擇器 {selector} 時發生錯誤: {e}")
                continue
        
        if book_category:
            try:
                # 滾動到元素可見位置
                driver.execute_script("arguments[0].scrollIntoView(true);", book_category)
                time.sleep(1)
                
                # 嘗試點擊
                book_category.click()
                print(f"已點選圖書分類: {book_category.text}，等待頁面載入...")
                
                # 等待頁面重新載入
                time.sleep(5)
                
                # 等待新的搜尋結果載入
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.mod_b, div.searchbook, div.mod"))
                )
                
            except Exception as e:
                print(f"點選圖書分類時發生錯誤: {e}")
                # 如果點選失敗，嘗試使用 JavaScript 點擊
                try:
                    driver.execute_script("arguments[0].click();", book_category)
                    print("使用 JavaScript 點選圖書分類成功")
                    time.sleep(5)
                except Exception as e2:
                    print(f"JavaScript 點擊也失敗: {e2}")
        else:
            print("找不到圖書分類選項，將顯示當前頁面的分類選項...")
            # 顯示當前頁面可用的分類選項以便除錯
            try:
                category_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '圖書') or contains(text(), '書籍') or contains(@class, 'category') or contains(@class, 'filter')]")
                print("找到的可能分類元素:")
                for i, elem in enumerate(category_elements[:10]):  # 只顯示前10個
                    try:
                        print(f"  {i+1}. 文字: '{elem.text.strip()}' 標籤: {elem.tag_name}")
                    except:
                        pass
            except Exception as e:
                print(f"無法取得分類元素: {e}")
            
        current_url = driver.current_url
        print(f"當前網址: {current_url}")
        
        page_num = 1
        max_pages = 3
        
        while page_num <= max_pages:
            print(f"正在爬取第 {page_num} 頁...")
            
            page_books = scrape_books_page(driver)
            all_books.extend(page_books)
            
            print(f"第 {page_num} 頁爬取到 {len(page_books)} 本書")
            
            if len(page_books) == 0:
                print("當前頁面沒有書籍資料，可能已到最後一頁")
                break
            
            if page_num >= max_pages:
                print(f"已完成 {max_pages} 頁爬取，停止翻頁")
                break
            
            try:
                print("正在尋找下一頁按鈕...")
                
                next_buttons = [
                    "//a[contains(@class, 'nxt') and not(contains(@class, 'gray'))]",
                    "//a[text()='下一頁' and not(contains(@class, 'gray'))]",
                    "//a[contains(text(), '下一頁') and not(contains(@class, 'gray'))]",
                    "//div[@class='cnt_page']//a[last()]",
                    "//div[contains(@class, 'page')]//a[contains(@class, 'nxt')]",
                    "//a[@rel='next']"
                ]
                
                next_button = None
                for selector in next_buttons:
                    try:
                        elements = driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if element.is_enabled() and element.is_displayed():
                                class_attr = element.get_attribute('class') or ''
                                if 'gray' not in class_attr.lower() and 'disabled' not in class_attr.lower():
                                    next_button = element
                                    print(f"找到可用的下一頁按鈕: {selector}")
                                    break
                        if next_button:
                            break
                    except Exception:
                        continue
                
                if next_button:
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", next_button)
                    print(f"已點擊下一頁按鈕，等待第 {page_num + 1} 頁載入...")
                    time.sleep(4)
                    page_num += 1
                else:
                    print("找不到可用的下一頁按鈕，爬取完成")
                    break
                
            except Exception as e:
                print(f"翻頁時發生錯誤: {e}")
                break
                
    except Exception as e:
        print(f"爬取過程中發生錯誤: {e}")
    finally:
        driver.quit()
    
    return all_books
