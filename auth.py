#auth.py
'''
带管理员权限的用户系统，支持用户注册、登录验证、密码修改和删除用户，关联了一个学习记录表（记录用户已掌握的单词）
'''

import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "users.db")

def connect_db(db_path=None):
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    return sqlite3.connect(db_path)

def init_db(db_path=None):
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    with connect_db(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                username TEXT,
                word TEXT,
                mastered INTEGER,          -- -1: 不认识, 0: 模糊, 1: 熟悉等
                review_stage INTEGER DEFAULT 0,   -- 当前复习阶段
                next_review TEXT,        -- 下次复习日期 (YYYY-MM-DD)
                last_review TEXT,        -- 上次复习日期 (YYYY-MM-DD)
                dict_file TEXT,
                PRIMARY KEY (username, word, dict_file),
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_progress (
                username TEXT,
                word TEXT,
                dict_file TEXT,
                date TEXT,
                mastered INTEGER
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        ''')

        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                ("admin", "admin123", 1)
            )
        conn.commit()

def validate_user(username, password, db_path=None):
    """验证登录，返回 (success, is_admin, message)"""
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()
        if result:
            is_admin = bool(result[0])
            return True, is_admin, "登录成功"
        else:
            return False, False, "用户名或密码错误"

def get_all_users(db_path=None):
    """获取所有用户信息，返回列表[(username, password, is_admin), ...]"""
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password, is_admin FROM users")
        return cursor.fetchall()

def delete_user(username, db_path=None):
    """删除指定用户名，返回是否成功"""
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        return cursor.rowcount > 0

def update_password(username, new_password, db_path=None):
    """更新指定用户名密码，返回是否成功"""
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
        conn.commit()
        return cursor.rowcount > 0

def get_all_records(db_path=None):
    """获取所有学习记录，返回列表[(username, word, mastered), ...]"""
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, word, mastered FROM records")
        return cursor.fetchall()
