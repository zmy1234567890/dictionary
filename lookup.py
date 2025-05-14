# lookup.py

import json

with open("data/dictionary5500.json", "r", encoding="utf-8") as f:
    raw_dict = json.load(f)
    dictionary = {k.lower(): v for k, v in raw_dict.items()}

def lookup(word):
    word = word.lower().strip()
    result = {}
    if word in dictionary:
        entry = dictionary[word]
        result["word"] = word
        result["translation"] = entry["translation"]
        result["examples"] = entry.get("examples", [])
    else:
        result["error"] = "not_found"
    return result






