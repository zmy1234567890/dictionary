import unittest
import tempfile
import json
import os
from lookup import Dictionary

class TestDictionary(unittest.TestCase):
    def setUp(self):
        # 创建临时词典文件
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.json')
        self.test_data = {
            "apple": {
                "translation": "苹果",
                "examples": ["I ate an apple."]
            },
            "banana": {
                "translation": "香蕉",
                "examples": ["Bananas are yellow."]
            }
        }
        json.dump(self.test_data, self.temp_file)
        self.temp_file.close()

        # 加载 Dictionary 类
        self.dict = Dictionary(self.temp_file.name)

    def tearDown(self):
        try:
            os.remove(self.temp_file.name)
        except Exception as e:
            print(f"⚠️ 警告：无法删除临时词库：{e}")

    def test_lookup_existing_word(self):
        result = self.dict.lookup("apple")
        self.assertEqual(result["word"], "apple")
        self.assertEqual(result["translation"], "苹果")
        self.assertIn("I ate an apple.", result["examples"])

    def test_lookup_nonexistent_word(self):
        result = self.dict.lookup("orange")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "not_found")

    def test_lookup_case_insensitive(self):
        result = self.dict.lookup("BANANA")
        self.assertEqual(result["translation"], "香蕉")

if __name__ == '__main__':
    unittest.main()




