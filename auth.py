import json
import os

USER_FILE = "data/users.json"

# 初始化用户文件
def init_db():
    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2, ensure_ascii=False)

# 读取用户数据
def load_users():
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 保存用户数据
def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

# 主菜单
def main():
    init_db()
    users = load_users()
    
    while True:
        print("\n=== 英语学习系统 ===")
        print("1. 注册")
        print("2. 登录")
        print("3. 退出")
        choice = input("请选择操作：").strip()

        if choice == "1":
            username = input("输入新用户名：").strip()
            if username in users:
                print("用户名已存在！")
                continue
            password = input("设置密码：").strip()
            users[username] = {"password": password, "words": [], "records": []}
            save_users(users)
            print("注册成功！")

        elif choice == "2":
            username = input("用户名：").strip()
            password = input("密码：").strip()
            if username in users and users[username]["password"] == password:
                print(f"欢迎 {username} 登录成功！")
                change_password_menu(username, users)
            else:
                print("用户名或密码错误")

        elif choice == "3":
            print("退出系统，再见！")
            break

        else:
            print("无效操作，请重新选择。")

# 修改密码菜单
def change_password_menu(username, users):
    while True:
        print(f"\n=== {username} 的账户设置 ===")
        print("1. 修改密码")
        print("2. 返回主菜单")
        choice = input("请选择：").strip()
        
        if choice == "1":
            old_pwd = input("原密码：").strip()
            if users[username]["password"] == old_pwd:
                new_pwd = input("新密码：").strip()
                users[username]["password"] = new_pwd
                save_users(users)
                print("密码修改成功！")
            else:
                print("原密码错误")
        
        elif choice == "2":
            break
        else:
            print("无效选择，请重新输入。")

if __name__ == "__main__":
    main()
