import json
import pytest
from lookup import Dictionary

# 测试夹具：创建临时测试词典
@pytest.fixture
def sample_dict(tmp_path):
    test_data = {
        "apple": {
            "translation": ["苹果", "苹果树"],
            "examples": ["I ate an apple.", "Apple is a fruit."]
        },
        "test": {
            "translation": ["测试"],
            "examples": ["This is a test."]
        }
    }
    file_path = tmp_path / "test_dict.json"
    file_path.write_text(json.dumps(test_data, ensure_ascii=False))
    return str(file_path)

# 测试正常功能
def test_load_dictionary(sample_dict):
    dict_obj = Dictionary(sample_dict)
    assert len(dict_obj.dictionary) == 2
    assert "apple" in dict_obj.dictionary
    assert "TEST" not in dict_obj.dictionary  # 验证已转为小写

# 参数化测试查找功能
@pytest.mark.parametrize("input_word,expected", [
    ("apple", {"word": "apple", "translation": ["苹果", "苹果树"], "examples": ["I ate an apple.", "Apple is a fruit."]}),
    ("TEST", {"word": "test", "translation": ["测试"], "examples": ["This is a test."]}),
    ("  Apple  ", {"word": "apple", "translation": ["苹果", "苹果树"], "examples": ["I ate an apple.", "Apple is a fruit."]}),
])
def test_valid_lookup(sample_dict, input_word, expected):
    dict_obj = Dictionary(sample_dict)
    result = dict_obj.lookup(input_word)
    assert result == expected

# 测试异常情况
def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        Dictionary("invalid/path.json")

def test_empty_input(sample_dict):
    dict_obj = Dictionary(sample_dict)
    assert "error" in dict_obj.lookup("")

def test_non_string_input(sample_dict):
    dict_obj = Dictionary(sample_dict)
    with pytest.raises(AttributeError):
        dict_obj.lookup(123)

# 测试边界情况
def test_case_insensitivity(sample_dict):
    dict_obj = Dictionary(sample_dict)
    assert dict_obj.lookup("APPLE")["word"] == "apple"

def test_partial_match(sample_dict):
    dict_obj = Dictionary(sample_dict)
    assert "error" in dict_obj.lookup("app")  # 不完全匹配应失败



