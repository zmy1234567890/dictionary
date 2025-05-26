import pytest
from quiz import start_quiz_EC, start_quiz_CE

# 测试夹具
@pytest.fixture
def mock_dictionary():
    class MockDict:
        def __init__(self):
            self.data = {
                "apple": {"translation": "苹果"},
                "banana": {"translation": "香蕉"},
                "cat": {"translation": "猫"},
                "dog": {"translation": "狗"},
                "elephant": {"translation": "大象"}
            }
        
        def lookup(self, word):
            return self.data.get(word, {})
    
    return MockDict()

# 功能测试
@pytest.mark.parametrize("total_questions,expected_count", [
    (5, 5),
    (10, 5),
    (0, 0),
    (-3, 0)
])
def test_quiz_ec(mock_dictionary, total_questions, expected_count):
    result = start_quiz_EC(mock_dictionary, ["apple", "banana"], total_questions)
    assert len(result) == expected_count
    for q in result:
        assert len(q["options"]) == 4
        assert q["answer"] in q["options"]
        assert q["options"].count(q["answer"]) == 1

# 边界测试
def test_empty_marked_words(mock_dictionary):
    result = start_quiz_EC(mock_dictionary, [], 5)
    assert len(result) == 0

def test_no_translation(mock_dictionary):
    result = start_quiz_EC(mock_dictionary, ["cat"], 5)
    assert len(result) == 0

# 干扰项验证
def test_distinct_options(mock_dictionary):
    result = start_quiz_CE(mock_dictionary, ["apple"], 1)
    options = result[0]["options"]
    assert len(set(options)) == 4  # 确保无重复选项
    assert options[0] == "苹果"  # 正确答案在首位
    assert all(w not in ["apple"] for w in options[1:])

# 随机性控制
def test_random_seed(mock_dictionary, capsys):
    # 固定随机种子保证可重复性
    import random
    random.seed(42)
    
    result = start_quiz_EC(mock_dictionary, ["apple", "banana"], 2)
    expected_questions = [
        {'word': 'banana', 'question': 'banana'},  # 具体内容根据实现确定
        {'word': 'apple', 'question': 'apple'}
    ]
    assert result == expected_questions