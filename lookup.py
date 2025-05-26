'''
加载JSON格式的词典文件，快速查找单词的翻译和例句
'''
# lookup.py
import json
import os

class Dictionary:
    def __init__(self, dict_path="data/dictionary5500.json"):
        """
        初始化词典类实例，默认加载指定路径的词典文件。
        :param dict_path: JSON 格式词典文件的路径
        """
        self.dict_path = dict_path
        self.load_dict(dict_path)# 加载词典内容

    def load_dict(self, dict_path):
        """
        从 JSON 文件中加载词典，将所有单词转为小写作为键，便于查询。
        :param dict_path: 字典文件路径
         """
        with open(dict_path, "r", encoding="utf-8") as f:
            raw_dict = json.load(f)
        self.dictionary = {k.lower(): v for k, v in raw_dict.items()}

    def lookup(self, word):
        """
        查找单词，返回对应的翻译与例句；若未找到，返回错误信息。
        :param word: 待查询的英文单词
        :return: 包含翻译、例句或错误信息的字典
        """
        word = word.lower().strip()# 统一小写并去除空格
        result = {}
        if word in self.dictionary:
            entry = self.dictionary[word]
            result["word"] = word
            result["translation"] = entry["translation"]# 获取翻译
            result["examples"] = entry.get("examples", []) # 获取例句，若无则返回空列表
        else:
            result["error"] = "not_found"# 单词不在词典中
        return result









