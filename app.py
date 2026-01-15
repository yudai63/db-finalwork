from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def get_categories():
    conn = get_db_connection()
    categories = conn.execute(
        "SELECT * FROM categories ORDER BY name"
    ).fetchall()
    conn.close()
    return categories

# ===== 一覧（＋月選択）=====
@app.route("/")
def index():
    month = request.args.get("month")  # 例: 2025-12
    conn = get_db_connection()

    if month:
        expenses = conn.execute("""
            SELECT e.id, e.date, e.amount, e.memo, c.name AS category
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.date LIKE ?
            ORDER BY e.date ASC
        """, (month + "%",)).fetchall()
    else:
        expenses = conn.execute("""
            SELECT e.id, e.date, e.amount, e.memo, c.name AS category
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            ORDER BY e.date ASC
        """).fetchall()

    total = sum(e["amount"] for e in expenses)

    months = conn.execute("""
        SELECT DISTINCT substr(date,1,7) AS month
        FROM expenses
        ORDER BY month DESC
    """).fetchall()

    conn.close()
    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        months=months,
        selected_month=month
    )

# ===== 新規追加 =====
@app.route("/add", methods=["GET", "POST"])
def add():
    categories = get_categories()

    if request.method == "POST":
        date = request.form["date"]
        amount = int(request.form["amount"])
        memo = request.form.get("memo", "")

        if request.form["category"] == "new":
            new_cat = request.form["new_category"]
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO categories (name) VALUES (?)", (new_cat,))
            category_id = cur.lastrowid
            conn.commit()
        else:
            category_id = int(request.form["category"])
            conn = get_db_connection()

        conn.execute("""
            INSERT INTO expenses (date, category_id, amount, memo)
            VALUES (?, ?, ?, ?)
        """, (date, category_id, amount, memo))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    today = datetime.today().strftime("%Y-%m-%d")
    return render_template("add.html", categories=categories, today=today)

# ===== 編集 =====
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db_connection()
    expense = conn.execute(
        "SELECT * FROM expenses WHERE id=?", (id,)
    ).fetchone()
    categories = get_categories()

    if request.method == "POST":
        date = request.form["date"]
        amount = int(request.form["amount"])
        memo = request.form.get("memo", "")

        if request.form["category"] == "new":
            new_cat = request.form["new_category"]
            cur = conn.cursor()
            cur.execute("INSERT INTO categories (name) VALUES (?)", (new_cat,))
            category_id = cur.lastrowid
        else:
            category_id = int(request.form["category"])

        conn.execute("""
            UPDATE expenses
            SET date=?, category_id=?, amount=?, memo=?
            WHERE id=?
        """, (date, category_id, amount, memo, id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn.close()
    return render_template(
        "edit.html", expense=expense, categories=categories
    )

# ===== 削除 =====
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
