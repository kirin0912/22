from scraper import scrape_all_books
from database import insert_books, search_books_by_title, search_books_by_author
from typing import List
import sqlite3


def display_menu() -> None:
    print("\n" + "="*50)
    print("      博客來 LLM 書籍資料庫管理系統")
    print("="*50)
    print("1. 更新書籍資料庫")
    print("2. 查詢書籍")
    print("3. 離開系統")
    print("="*50)


def display_search_menu() -> None:
    print("\n" + "-"*30)
    print("       查詢選項")
    print("-"*30)
    print("1. 依書名查詢")
    print("2. 依作者查詢")
    print("3. 返回主選單")
    print("-"*30)


def display_books(books: List[sqlite3.Row]) -> None:
    if not books:
        print("查無資料")
        return
    
    print(f"\n找到 {len(books)} 本書籍：")
    print("-" * 80)
    
    for i, book in enumerate(books, 1):
        print(f"{i}. 書名: {book['title']}")
        print(f"   作者: {book['author']}")
        print(f"   價格: {book['price']} 元")
        print(f"   連結: {book['link']}")
        print("-" * 80)


def update_database() -> None:
    print("\n開始爬取博客來書籍資料...")
    print("此過程可能需要幾分鐘，請耐心等候...")
    
    try:
        books = scrape_all_books()
        
        if books:
            inserted_count = insert_books(books)
            print(f"\n爬取完成！總共抓取 {len(books)} 本書")
            print(f"成功新增 {inserted_count} 本新書至資料庫")
        else:
            print("未能爬取到任何書籍資料")
            
    except Exception as e:
        print(f"更新資料庫時發生錯誤: {e}")


def search_books() -> None:
    while True:
        display_search_menu()
        
        try:
            choice = input("請選擇查詢方式 (1-3): ").strip()
            
            if choice == "1":
                keyword = input("請輸入書名關鍵字: ").strip()
                if keyword:
                    books = search_books_by_title(keyword)
                    display_books(books)
                else:
                    print("請輸入有效的關鍵字")
                    
            elif choice == "2":
                keyword = input("請輸入作者關鍵字: ").strip()
                if keyword:
                    books = search_books_by_author(keyword)
                    display_books(books)
                else:
                    print("請輸入有效的關鍵字")
                    
            elif choice == "3":
                break
                
            else:
                print("無效的選項，請重新選擇")
                
        except KeyboardInterrupt:
            print("\n操作已取消")
            break
        except Exception as e:
            print(f"查詢時發生錯誤: {e}")


def main() -> None:
    print("歡迎使用博客來 LLM 書籍資料庫管理系統")
    
    while True:
        display_menu()
        
        try:
            choice = input("請選擇功能 (1-3): ").strip()
            
            if choice == "1":
                update_database()
                
            elif choice == "2":
                search_books()
                
            elif choice == "3":
                print("感謝使用，再見！")
                break
                
            else:
                print("無效的選項，請重新選擇")
                
        except KeyboardInterrupt:
            print("\n\n程式已結束，再見！")
            break
        except Exception as e:
            print(f"程式執行時發生錯誤: {e}")


if __name__ == "__main__":
    main()
