# main.py
import os
from auth import init_db, register, login, logout, admin_menu
from lookup import Dictionary
from records import mark_word, get_mastered_words, get_unfamiliar_words,get_unknown_words


def select_dictionary():
    dict_dir = "data"
    files = [f for f in os.listdir(dict_dir) if f.endswith(".json")]
    if not files:
        print("❌ 没有找到任何词库！")
        return None
    print("\n可用词库：")
    for idx, f in enumerate(files, start=1):
        print(f"{idx}. {f}")
    choice = input("请选择词库编号：")
    try:
        idx = int(choice) - 1
        return os.path.join(dict_dir, files[idx])
    except (ValueError, IndexError):
        print("无效选择")
        return None

def user_menu(username):
    dict_path = select_dictionary()
    if not dict_path:
        print("未选择词库，返回主菜单。")
        return
    
    dictionary = Dictionary(dict_path)

    while True:
        print(f"\n=== {username} 的学习菜单（词库：{os.path.basename(dict_path)}） ===")
        print("1. 查单词并标记熟悉程度")
        print("2. 查看掌握的单词")
        print("3. 查看不认识的单词")
        print("4. 查看不熟的单词")
        print("5. 更换词库")
        print("6. 返回主菜单")
        choice = input("请选择操作：")

        if choice == "1":
            word = input("请输入要查找的英文单词：").strip().lower()
            result = dictionary.lookup(word)
            if "error" in result:
                print("❌ 未找到该单词。")
            else:
                print(f"\n📘 单词: {result['word']}")
                print(f"📖 释义: {result['translation']}")
                print("📚 例句:")
                for ex in result["examples"]:
                    print(f" - {ex}")
                
                print("\n请选择熟悉程度：")
                print("1. 掌握")
                print("2. 不熟")
                print("3. 不认识")
                level = input("请输入编号：")
                if level == "1":
                    mark_word(username, word, mastered=1)
                elif level == "2":
                    mark_word(username, word, mastered=0)
                elif level == "3":
                    mark_word(username, word, mastered=-1)
                else:
                    print("无效输入，未记录。")

        elif choice == "2":
            mastered = get_mastered_words(username)
            print("\n✅ 掌握的单词：")
            if mastered:
                for w in mastered:
                    print("-", w)
            else:
                print("（暂无）")

        elif choice == "3":
            unknown = get_unknown_words(username)
            print("\n⚠️ 不认识的单词：")
            if unknown:
                for w in unknown:
                    print("-", w)
            else:
                print("（暂无）")
        
        elif choice == "4":
            unfamiliar = get_unfamiliar_words(username)
            print("\n⚠️ 不熟的单词：")
            if unfamiliar:
                for w in unfamiliar:
                    print("-", w)
            else:
                print("（暂无）")
        
        elif choice == "5":
            new_path = select_dictionary()
            if new_path:
                dict_path = new_path
                dictionary.load_dict(dict_path)

        elif choice == "6":
            break

        else:
            print("无效选项，请重试。")


def main():
    print("=== 背单词系统 ===")
    init_db()

    while True:
        print("\n主菜单：")
        print("1. 注册")
        print("2. 登录")
        print("3. 退出")
        choice = input("请选择操作：")

        if choice == "1":
            register()

        elif choice == "2":
            username, is_admin = login()
            if username:
                if is_admin:
                    print(f"管理员 {username} 登录成功")
                    admin_menu()
                else:
                    user_menu(username)
                logout()
        
        elif choice == "3":
            print("退出程序。")
            break

        else:
            print("无效输入，请重新选择。")

if __name__ == "__main__":
    main()
