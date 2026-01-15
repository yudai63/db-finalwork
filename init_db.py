import sqlite3

conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()

# --- categories テーブル ---
cur.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    is_fixed INTEGER NOT NULL DEFAULT 0
)
""")

# --- expenses テーブル ---
cur.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    memo TEXT,
    FOREIGN KEY(category_id) REFERENCES categories(id)
)
""")

# --- 初期（固定）カテゴリ ---
fixed_categories = [
    "食費",
    "交通費",
    "趣味",
    "その他",
    "書籍",
    "生活用品"
]

for name in fixed_categories:
    cur.execute("""
    INSERT OR IGNORE INTO categories (name, is_fixed)
    VALUES (?, 1)
    """, (name,))

conn.commit()
conn.close()

print("DB初期化完了")
