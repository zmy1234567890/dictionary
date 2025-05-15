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
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    with connect_db(db_path) as conn:
        cursor = conn.cursor()

        # 创建 users 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        ''')

        # 创建 records 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                username TEXT,
                word TEXT,
                mastered INTEGER,
                PRIMARY KEY (username, word),
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        ''')

        # 添加默认管理员（如果不存在）
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                ("admin", "admin123", 1)
            )

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
        cursor.execute("SELECT is_admin FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()
        if result:
            is_admin = bool(result[0])
            print("登录成功，欢迎", username)
            return username, is_admin
        else:
            print("用户名或密码错误")
            return None, False


def logout():
    print("已注销登录。")
    return None

def admin_menu(db_path=None):
    while True:
        print("\n管理员菜单：")
        print("1. 查看所有用户")
        print("2. 删除用户")
        print("3. 修改用户密码")
        print("4. 查看学习记录")
        print("5. 退出管理员菜单")
        choice = input("请输入选项：")
        
        if choice == "1":
            with connect_db(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, password, is_admin FROM users")
                for row in cursor.fetchall():
                    role = "管理员" if row[2] else "普通用户"
                    print(f"用户名: {row[0]}, 密码: {row[1]}, 类型: {role}")

        elif choice == "2":
            username = input("请输入要删除的用户名：")
            with connect_db(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                conn.commit()
                print("用户已删除（如果存在）")

        elif choice == "3":
            username = input("要修改密码的用户名：")
            new_pw = input("新密码：")
            with connect_db(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_pw, username))
                conn.commit()
                print("密码已更新（如果用户存在）")

        elif choice == "4":
            with connect_db(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, word, mastered FROM records")
                for row in cursor.fetchall():
                    status = "已掌握" if row[2] else "未掌握"
                    print(f"用户: {row[0]} | 单词: {row[1]} | 状态: {status}")

        elif choice == "5":
            print("退出管理员菜单。")
            break
        else:
            print("无效选项。")
