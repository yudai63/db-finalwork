from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "db.sqlite3"

# DB接続
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# 初期カテゴリ取得
def get_categories():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return categories

#  一覧表示 
@app.route("/")
def index():
    conn = get_db_connection()
    expenses = conn.execute("""
        SELECT e.id, e.date, e.amount, e.memo, c.name as category
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        ORDER BY e.date DESC
    """).fetchall()
    total = sum([row["amount"] for row in expenses])
    conn.close()
    return render_template("index.html", expenses=expenses, total=total)

#  新規追加 
@app.route("/add", methods=["GET", "POST"])
def add():
    categories = get_categories()
    if request.method == "POST":
        date = request.form["date"]
        category_id = request.form["category"]
        amount = request.form["amount"]
        memo = request.form.get("memo", "")
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO expenses (date, category_id, amount, memo) VALUES (?, ?, ?, ?)",
            (date, category_id, amount, memo)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add.html", categories=categories)

#  編集（Update） 
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db_connection()
    expense = conn.execute("SELECT * FROM expenses WHERE id=?", (id,)).fetchone()
    categories = get_categories()
    if request.method == "POST":
        date = request.form["date"]
        category_id = request.form["category"]
        amount = request.form["amount"]
        memo = request.form.get("memo", "")
        conn.execute(
            "UPDATE expenses SET date=?, category_id=?, amount=?, memo=? WHERE id=?",
            (date, category_id, amount, memo, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    conn.close()
    return render_template("edit.html", expense=expense, categories=categories)

#  削除 
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
