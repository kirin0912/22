import sqlite3
from typing import List, Dict, Any, Optional


def create_connection() -> sqlite3.Connection:
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn


def create_table() -> None:
    with create_connection() as conn:
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS llm_books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL UNIQUE,
                    author TEXT,
                    price INTEGER,
                    link TEXT
                )
            ''')
            conn.commit()
        except sqlite3.Error as e:
            print(f"建立資料表時發生錯誤: {e}")


def insert_books(books: List[Dict[str, Any]]) -> int:
    create_table()
    inserted_count = 0
    
    with create_connection() as conn:
        try:
            for book in books:
                cursor = conn.execute('''
                    INSERT OR IGNORE INTO llm_books (title, author, price, link)
                    VALUES (?, ?, ?, ?)
                ''', (book['title'], book['author'], book['price'], book['link']))
                
                if cursor.rowcount > 0:
                    inserted_count += 1
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"插入資料時發生錯誤: {e}")
    
    return inserted_count


def search_books_by_title(keyword: str) -> List[sqlite3.Row]:
    with create_connection() as conn:
        try:
            cursor = conn.execute('''
                SELECT * FROM llm_books 
                WHERE title LIKE ?
                ORDER BY title
            ''', (f'%{keyword}%',))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"搜尋資料時發生錯誤: {e}")
            return []


def search_books_by_author(keyword: str) -> List[sqlite3.Row]:
    with create_connection() as conn:
        try:
            cursor = conn.execute('''
                SELECT * FROM llm_books 
                WHERE author LIKE ?
                ORDER BY title
            ''', (f'%{keyword}%',))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"搜尋資料時發生錯誤: {e}")
            return []
