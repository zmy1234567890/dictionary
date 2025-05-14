import unittest
from lookup import lookup  # 引入 lookup.py 中的 lookup 函数

class TestLookup(unittest.TestCase):
    
    def test_lookup_existing_word_with_examples(self):
        result = lookup("apply")
        self.assertNotIn("error", result)  # 确保没有错误
        self.assertEqual(result["word"], "apply")  # 确保返回的单词正确
        self.assertIsInstance(result["examples"], list)  # 确保返回的例句是列表
        self.assertGreater(len(result["examples"]), 0)  # 确保例句列表非空

    def test_lookup_existing_word_no_examples(self):
        result = lookup("defensive")
        self.assertNotIn("error", result)  # 确保没有错误
        self.assertEqual(result["word"], "defensive")  # 确保返回的单词正确
        self.assertEqual(result["examples"], [])  # 确保例句列表为空

    def test_lookup_non_existing_word(self):
        result = lookup("unknownword")
        self.assertIn("error", result)  # 确保返回错误信息
        self.assertEqual(result["error"], "not_found")  # 确保错误信息为 "not_found"

if __name__ == "__main__":
    unittest.main()



