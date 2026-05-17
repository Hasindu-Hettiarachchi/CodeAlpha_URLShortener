from flask import Flask
import sqlite3
import random
import string

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()

    cursor.execute("""
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
    short_code = ""

    for i in range(length):
        short_code += random.choice(characters)

    return short_code

@app.route("/")
def home():
    return "URL Shortener Backend is running"

if __name__ == "__main__":
    init_db()
    app.run(debug=True)