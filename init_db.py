import sqlite3

conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

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

# 初期カテゴリ
cur.execute("INSERT INTO categories (name) VALUES ('食費')")
cur.execute("INSERT INTO categories (name) VALUES ('交通費')")
cur.execute("INSERT INTO categories (name) VALUES ('趣味')")
cur.execute("INSERT INTO categories (name) VALUES ('その他')")

conn.commit()
conn.close()

print("DB初期化完了")
