import json

# 加载词典 JSON 文件
with open("dictionary5500.json", "r", encoding="utf-8") as f:
    dictionary = json.load(f)

def lookup(word):
    word = word.lower().strip()
    if word in dictionary:
        entry = dictionary[word]
        print(f"\n 单词: {word}")
        print(f"释义: {entry['translation']}")
        if entry['examples']:
            print(" 例句:")
            for i, ex in enumerate(entry['examples'], 1):
                print(f"  {i}. {ex['en']}")
                print(f"     → {ex['cn']}")
        else:
            print("没有找到例句。")
    else:
        print("没有找到该单词。")

# 控制台循环查词
if __name__ == "__main__":
    print("英汉词典查词工具（输入 exit 退出）")
    while True:
        word = input("\n请输入英文单词： ")
        if word.lower() in ['exit', 'quit']:
            print("再见！")
            break
        lookup(word)
