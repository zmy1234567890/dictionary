import pandas as pd
import json

def build_dictionary(words_csv, examples_csv, output_json):
    # 加载数据
    words_df = pd.read_csv(words_csv)
    examples_df = pd.read_csv(examples_csv)

    # 建立一个 dict
    dictionary = {}

    # 遍历单词列表
    for _, row in words_df.iterrows():
        word = str(row['Words']).strip().lower()
        translation = str(row['Translation']).strip()

        # 找出包含该单词的例句（最多两个）
        matched = examples_df[examples_df['English'].str.contains(rf'\b{word}\b', case=False, na=False)]
        examples = []
        for _, ex_row in matched.head(2).iterrows():
            examples.append({
                "en": ex_row["English"].strip(),
                "cn": ex_row["Chinese"].strip()
            })

        # 添加到词典
        dictionary[word] = {
            "translation": translation,
            "examples": examples
        }

    # 保存为 JSON 文件
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=2)

    print(f"字典已成功保存为 {output_json}")

# 用法示例
if __name__ == "__main__":
    build_dictionary("7000_TOEFL.csv", "eng_cmn_examples.csv", "dictionaryTOEFL.json")




