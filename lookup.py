# lookup.py
import json
import os

class Dictionary:
    def __init__(self, dict_path="data/dictionary5500.json"):
        self.dict_path = dict_path
        self.load_dict(dict_path)

    def load_dict(self, dict_path):
        with open(dict_path, "r", encoding="utf-8") as f:
            raw_dict = json.load(f)
        self.dictionary = {k.lower(): v for k, v in raw_dict.items()}

    def lookup(self, word):
        word = word.lower().strip()
        result = {}
        if word in self.dictionary:
            entry = self.dictionary[word]
            result["word"] = word
            result["translation"] = entry["translation"]
            result["examples"] = entry.get("examples", [])
        else:
            result["error"] = "not_found"
        return result









