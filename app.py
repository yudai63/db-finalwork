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
    categories = conn.execute("""
        SELECT *
        FROM categories
        WHERE id IN (SELECT DISTINCT category_id FROM expenses)
           OR is_fixed = 1
        ORDER BY
            CASE name
                WHEN '食費' THEN 1
                WHEN '交通費' THEN 2
                WHEN '生活用品' THEN 3
                WHEN '書籍' THEN 4
                WHEN '趣味' THEN 5
                WHEN 'その他' THEN 6
                ELSE 100
            END,
            name
    """).fetchall()
    conn.close()
    return categories


def get_or_create_category(conn, name):
    cur = conn.cursor()
    row = cur.execute(
        "SELECT id FROM categories WHERE name=?",
        (name,)
    ).fetchone()
    if row:
        return row["id"]
    cur.execute(
        "INSERT INTO categories (name, is_fixed) VALUES (?, 0)",
        (name,)
    )
    return cur.lastrowid

def cleanup_unused_categories(conn):
    conn.execute("""
        DELETE FROM categories
        WHERE is_fixed = 0
        AND id NOT IN (SELECT DISTINCT category_id FROM expenses)
    """)

@app.route("/")
def index():
    month = request.args.get("month")
    conn = get_db_connection()

    if month:
        expenses = conn.execute("""
            SELECT e.id, e.date, e.amount, e.memo, c.name AS category
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.date LIKE ?
            ORDER BY e.date ASC
        """, (month + "%",)).fetchall()

        graph_data = conn.execute("""
            SELECT c.name, SUM(e.amount) AS total
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.date LIKE ?
            GROUP BY c.name
        """, (month + "%",)).fetchall()
    else:
        expenses = conn.execute("""
            SELECT e.id, e.date, e.amount, e.memo, c.name AS category
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            ORDER BY e.date ASC
        """).fetchall()

        graph_data = conn.execute("""
            SELECT c.name, SUM(e.amount) AS total
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            GROUP BY c.name
        """).fetchall()

    total = sum(e["amount"] for e in expenses)

    months = conn.execute("""
        SELECT DISTINCT substr(date,1,7) AS month
        FROM expenses
        ORDER BY month DESC
    """).fetchall()

    conn.close()

    labels = [r["name"] for r in graph_data]
    values = [r["total"] for r in graph_data]

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        months=months,
        selected_month=month,
        labels=labels,
        values=values
    )

@app.route("/add", methods=["GET","POST"])
def add():
    categories = get_categories()

    if request.method == "POST":
        conn = get_db_connection()
        cur = conn.cursor()

        if request.form["category"] == "new":
            category_id = get_or_create_category(
                conn, request.form["new_category"]
            )
        else:
            category_id = int(request.form["category"])

        cur.execute("""
            INSERT INTO expenses (date, category_id, amount, memo)
            VALUES (?,?,?,?)
        """, (
            request.form["date"],
            category_id,
            int(request.form["amount"]),
            request.form.get("memo","")
        ))

        cleanup_unused_categories(conn)

        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    today = datetime.today().strftime("%Y-%m-%d")
    return render_template("add.html", categories=categories, today=today)

@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    conn = get_db_connection()
    expense = conn.execute(
        "SELECT * FROM expenses WHERE id=?", (id,)
    ).fetchone()
    categories = get_categories()

    if request.method == "POST":
        cur = conn.cursor()

        if request.form["category"] == "new":
            category_id = get_or_create_category(
                conn, request.form["new_category"]
            )
        else:
            category_id = int(request.form["category"])

        cur.execute("""
            UPDATE expenses
            SET date=?, category_id=?, amount=?, memo=?
            WHERE id=?
        """, (
            request.form["date"],
            category_id,
            int(request.form["amount"]),
            request.form.get("memo",""),
            id
        ))

        cleanup_unused_categories(conn)

        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn.close()
    return render_template(
        "edit.html", expense=expense, categories=categories
    )

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM expenses WHERE id=?", (id,))
    cleanup_unused_categories(conn)
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
