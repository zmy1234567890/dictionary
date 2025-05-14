import csv

# 只保留英文和中文句子
valid_langs = {"eng", "cmn"}

# 保存所有英文和中文句子
sentences = {}
langs = {}

with open("sentences.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        if len(row) != 3:
            continue
        sid, lang, text = row
        if lang in valid_langs:
            sentences[sid] = text
            langs[sid] = lang

# 提取英中句对
pairs = []

with open("links.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        if len(row) != 2:
            continue
        sid1, sid2 = row
        if sid1 in langs and sid2 in langs:
            lang1, lang2 = langs[sid1], langs[sid2]
            if {lang1, lang2} == {"eng", "cmn"}:
                if lang1 == "eng":
                    eng, zh = sentences[sid1], sentences[sid2]
                else:
                    eng, zh = sentences[sid2], sentences[sid1]
                pairs.append((eng, zh))

# 保存前 10000 对到 CSV 文件
with open("eng_cmn_examples.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["English", "Chinese"])
    for pair in pairs[:10000]:
        writer.writerow(pair)

print(f"成功提取 {len(pairs)} 条英文-中文例句对")
