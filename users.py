# users.py
import sqlite3

def connect_db():
    return sqlite3.connect("data/dictlearn.db")

def create_tables():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT NOT NULL
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS word_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    word TEXT,
                    status TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                 )''')
    conn.commit()
    conn.close()

def register(username, password):
    conn = connect_db()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print("注册成功")
    except sqlite3.IntegrityError:
        print("用户名已存在")
    conn.close()

def login(username, password):
    conn = connect_db()
    cursor = conn.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]  # 返回 user_id
    else:
        print("用户名或密码错误")
        return None
