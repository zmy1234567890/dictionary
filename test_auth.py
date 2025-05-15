# auth_test.py

from auth import init_db, register, login, admin_menu

def user_menu(username):
    print(f"\n欢迎 {username} 进入普通用户菜单（这里你可以添加学习功能）")
    input("按 Enter 返回主菜单...")

def main():
    print("==== 认证系统测试程序 ====")
    init_db()  # 初始化数据库（含默认 admin）

    while True:
        print("\n主菜单：")
        print("1. 注册")
        print("2. 登录")
        print("3. 退出")
        choice = input("请选择：")

        if choice == "1":
            register()

        elif choice == "2":
            username, is_admin = login()
            if username:
                if is_admin:
                    print(f"\n欢迎管理员 {username} 登录")
                    admin_menu()
                else:
                    user_menu(username)

        elif choice == "3":
            print("退出程序。")
            break

        else:
            print("无效选择，请重试。")

if __name__ == "__main__":
    main()



