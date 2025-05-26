#users.py
'''
简易用户系统，支持注册和登录，并设计了单词学习记录表（记录用户单词学习状态）
'''

import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "dictlearn.db")

def connect_db():
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS records (
            username TEXT,
            word TEXT,
            mastered INTEGER,          -- -1: 不认识, 0: 模糊, 1: 熟悉等
            review_stage INTEGER DEFAULT 0,,    -- 当前复习阶段
            next_review TEXT,        -- 下次复习日期 (YYYY-MM-DD)
            last_review TEXT,        -- 上次复习日期 (YYYY-MM-DD)
            dict_file TEXT,
            PRIMARY KEY (username, word, dict_file),
            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
        )
    ''')


    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_progress (
            username TEXT,
            word TEXT,
            dict_file TEXT,
            date TEXT,
            mastered INTEGER
            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def validate_user(username, password):
    """
    验证用户登录，返回 user_id 或 None
    """
    conn = connect_db()
    cursor = conn.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None
