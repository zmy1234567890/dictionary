import sqlite3
import json
import os
from getpass import getpass
from datetime import datetime

DB_PATH = "users.db"
DICT_JSON = "D:\c_course\dictionary\data\dictionary3500.json"  # 你之前生成的 JSON 文件路径

# 初始化数据库（只运行一次）
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS learned_words (
            user_id INTEGER,
            word TEXT,
            learned_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS query_history (
            user_id INTEGER,
            word TEXT,
            queried_at TEXT,
            mastered INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

# 注册功能
def register():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    username = input("请输入用户名：")
    password = input("请输入密码（明文输入）: ")
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print("✅ 注册成功！")
        return {"username": username, "id": cur.lastrowid}
    except sqlite3.IntegrityError:
        print("❌ 用户名已存在")
    return None

# 登录功能
def login():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    username = input("请输入用户名：")
    password = getpass("请输入密码：")
    cur.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    result = cur.fetchone()
    if result:
        print("✅ 登录成功！")
        return {"username": username, "id": result[0]}
    else:
        print("❌ 用户名或密码错误")
    return None

# 查询功能
def lookup_word(user_id):
    if (os.path.exists(DICT_JSON) == False) :
        print("没有找到词典")
        return
    
    with open(DICT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    word = input("请输入要查询的英文单词：").strip().lower()
    
    if word in data:
        item = data[word]
        print(f"\n📌 单词：{word}")
        print(f"📖 释义：{item['translation']}")
        for i, ex in enumerate(item['examples']):
            print(f"🔹 例句{i+1}：{ex['en']}")
            print(f"        翻译：{ex['cn']}")
        
        mastered = input("你是否掌握该单词？(y/n)：").lower() == 'y'

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        now = datetime.now().isoformat()
        cur.execute("INSERT INTO query_history (user_id, word, queried_at, mastered) VALUES (?, ?, ?, ?)",
                    (user_id, word, now, int(mastered)))
        if mastered:
            cur.execute("INSERT INTO learned_words (user_id, word, learned_at) VALUES (?, ?, ?)",
                        (user_id, word, now))
        conn.commit()
        conn.close()
    else:
        print("❌ 未找到该单词")

# 查看记录
def view_records(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT word, learned_at FROM learned_words WHERE user_id = ? ORDER BY learned_at DESC", (user_id,))
    rows = cur.fetchall()
    if rows:
        print("\n📚 已掌握的单词：")
        for word, date in rows:
            print(f"- {word} (学于：{date[:10]})")
    else:
        print("⚠️ 你还没有掌握任何单词。")
    conn.close()

# 主程序
def main():
    init_db()
    print("📘 多用户词汇学习系统")
    user = None
    while not user:
        print("\n1. 注册\n2. 登录\n3. 退出")
        choice = input("选择操作：")
        if choice == '1':
            user = register()
        elif choice == '2':
            user = login()
        elif choice == '3':
            return

    while True:
        print(f"\n欢迎，{user['username']}！")
        print("1. 查词\n2. 查看学习记录\n3. 注销")
        choice = input("选择操作：")
        if choice == '1':
            lookup_word(user['id'])
        elif choice == '2':
            view_records(user['id'])
        elif choice == '3':
            print("✅ 已注销。再见！")
            break

if __name__ == '__main__':
    main()



