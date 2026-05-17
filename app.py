import sqlite3
import string
import random
from flask import Flask, request, jsonify, redirect, render_template

app = Flask(__name__)
DATABASE = "urls.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            long_url TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def unique_short_code():
    conn = get_db()

    while True:
        code = generate_short_code()
        existing = conn.execute(
            "SELECT id FROM urls WHERE short_code = ?",
            (code,)
        ).fetchone()

        if not existing:
            conn.close()
            return code


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()

    if not data or "long_url" not in data:
        return jsonify({"error": "Please provide a 'long_url' in the request body."}), 400

    long_url = data["long_url"].strip()

    if not long_url:
        return jsonify({"error": "'long_url' cannot be empty."}), 400

    if not (long_url.startswith("http://") or long_url.startswith("https://")):
        return jsonify({"error": "URL must start with http:// or https://"}), 400

    short_code = unique_short_code()

    conn = get_db()
    conn.execute(
        "INSERT INTO urls (short_code, long_url) VALUES (?, ?)",
        (short_code, long_url)
    )
    conn.commit()
    conn.close()

    short_url = f"http://localhost:5000/{short_code}"

    return jsonify({
        "short_code": short_code,
        "short_url": short_url,
        "long_url": long_url
    }), 201


@app.route("/<short_code>")
def redirect_to_long(short_code):
    conn = get_db()
    row = conn.execute(
        "SELECT long_url FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": f"Short code '{short_code}' not found."}), 404

    return redirect(row["long_url"])


@app.route("/all", methods=["GET"])
def list_all():
    conn = get_db()
    rows = conn.execute("SELECT short_code, long_url FROM urls").fetchall()
    conn.close()

    result = [
        {
            "short_code": r["short_code"],
            "long_url": r["long_url"]
        }
        for r in rows
    ]

    return jsonify(result)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)