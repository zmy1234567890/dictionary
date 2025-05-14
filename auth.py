import sqlite3
import os

# 默认数据库路径
BASE_DIR = os.path.dirname(__file__)
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "users.db")

def connect_db(db_path=None):
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    return sqlite3.connect(db_path)

def init_db(db_path=None):
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                username TEXT,
                word TEXT,
                mastered INTEGER,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        ''')
        conn.commit()

def register(db_path=None):
    username = input("请输入用户名：")
    password = input("请输入密码：")
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            print("该用户名已存在，请更换。")
            return None
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print("注册成功！")
        return username

def login(db_path=None):
    username = input("用户名：")
    password = input("密码：")
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        if cursor.fetchone():
            print("登录成功，欢迎", username)
            return username
        else:
            print("用户名或密码错误")
            return None

def logout():
    print("已注销登录。")
    return None
