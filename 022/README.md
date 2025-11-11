# 博客來 LLM 書籍爬蟲系統

這是一個使用 Python、Selenium 和 SQLite 開發的博客來書籍爬蟲系統，專門爬取 LLM 相關書籍資料。

## 功能特色

- 自動化爬取博客來網站的 LLM 相關書籍
- 支援多頁面爬取
- SQLite 資料庫儲存
- 命令列介面操作
- 書名和作者關鍵字搜尋

## 系統要求

- Python 3.7+
- Chrome 瀏覽器

## 安裝步驟

1. 安裝相依套件：
```bash
pip install -r requirements.txt
```

2. 執行程式：
```bash
python app.py
```

## 專案結構

```
├── app.py          # 主程式，提供命令列介面
├── scraper.py      # 網頁爬蟲功能
├── database.py     # 資料庫操作功能
├── requirements.txt # 相依套件列表
└── README.md       # 專案說明
```

## 使用說明

程式提供三個主要功能：

1. **更新書籍資料庫**：爬取博客來最新的 LLM 書籍資料
2. **查詢書籍**：依書名或作者進行關鍵字搜尋
3. **離開系統**：結束程式

## 技術細節

- 使用 Selenium WebDriver 進行網頁自動化
- Chrome headless 模式提升爬取效率
- SQLite 資料庫儲存，支援 UNIQUE 約束避免重複資料
- 完整的例外處理機制
- 符合 PEP8 編碼規範

## 資料庫結構

```sql
CREATE TABLE llm_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    author TEXT,
    price INTEGER,
    link TEXT
);
```

## 授權

本專案採用 MIT 授權條款。
