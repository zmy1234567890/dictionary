# main.py
import auth
print(auth.__file__)
def main():
    current_user = None

    while True:
        print("\n=== 英语学习系统 ===")
        if not current_user:
            print("1. 注册")
            print("2. 登录")
            print("3. 退出")
            choice = input("选择操作：")

            if choice == "1":
                current_user = auth.register()
            elif choice == "2":
                current_user = auth.login()
            elif choice == "3":
                break
        else:
            print(f"\n欢迎，{current_user}！")
            print("1. 查询单词（TODO）")
            print("2. 注销")
            choice = input("选择操作：")

            if choice == "1":
                print("查询功能待实现。")
            elif choice == "2":
                current_user = auth.logout()

if __name__ == "__main__":
    main()
