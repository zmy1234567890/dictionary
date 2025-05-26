import pytest
from datetime import datetime, timedelta
from records import (
    mark_word, get_mastered_words, get_unfamiliar_words,
    get_unknown_words, get_user_progress, get_daily_count,
    get_total_words_learned, get_today_progress_distribution,
    get_last_7_days_learning_counts, schedule_next_review,
    get_review_list, get_today_review_words,
    get_today_reviewed_words
)
from auth import init_db

# 测试夹具
@pytest.fixture(scope="module")
def db_connection():
    test_db = "test_users.db"
    init_db(db_path=test_db)
    conn = sqlite3.connect(test_db)
    yield conn
    conn.close()
    os.remove(test_db)

# 时间冻结夹具
@pytest.fixture
def frozen_time():
    from freezegun import freeze_time
    return freeze_time("2024-03-20")

# 基础功能测试
def test_mark_word(db_connection):
    mark_word("user1", "apple", "dict1", 1, db_path=db_connection)
    assert "apple" in get_mastered_words("user1", "dict1", db_connection)
    assert get_total_words_learned("user1", "dict1", db_connection.cursor()) == 1

# 时间敏感测试
def test_daily_progress(frozen_time, db_connection):
    mark_word("user1", "apple", "dict1", 1, db_path=db_connection)
    assert get_daily_count("user1", "2024-03-20", "dict1", db_connection) == 1

# 复习调度测试
def test_schedule_next_review(db_connection):
    mark_word("user1", "apple", "dict1", -1, db_path=db_connection)
    
    # 初次学习
    schedule_next_review("user1", "apple", "dict1", -1, 0)
    with connect_db(db_path=db_connection) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT next_review FROM records WHERE username='user1' AND word='apple'")
        assert cursor.fetchone()[0] == datetime.today().date().isoformat()

    # 正确回答
    schedule_next_review("user1", "apple", "dict1", 0, 1)
    with connect_db(db_path=db_connection) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT next_review FROM records WHERE username='user1' AND word='apple'")
        assert isinstance(cursor.fetchone()[0], date)

# 查询功能测试
@pytest.mark.parametrize("status,expected", [
    ("mastered", ["apple"]),
    ("unfamiliar", []),
    ("unknown", [])
])
def test_status_queries(db_connection, status, expected):
    mark_word("user1", "apple", "dict1", 1, db_path=db_connection)
    query_func = {
        "mastered": get_mastered_words,
        "unfamiliar": get_unfamiliar_words,
        "unknown": get_unknown_words
    }[status]
    assert query_func("user1", "dict1", db_connection) == expected

# 统计功能测试
def test_progress_statistics(db_connection):
    mark_word("user1", "apple", "dict1", 1, db_path=db_connection)
    mark_word("user1", "banana", "dict1", 0, db_path=db_connection)
    
    progress = get_user_progress("user1", "dict1", db_connection)
    assert progress["apple"] == 1
    assert progress["banana"] == 0

    distribution = get_today_progress_distribution("user1", "2024-03-20", "dict1")
    assert sum(distribution.values()) == 100
    assert distribution["mastered_percent"] == 50.0

# 边界测试
def test_edge_cases(db_connection):
    # 空用户测试
    assert get_total_words_learned("unknown", "dict1", db_connection.cursor()) == 0
    
    # 超大词库测试
    for i in range(1000):
        mark_word("user1", f"word{i}", "dict1", 1, db_path=db_connection)
    assert len(get_all_records("user1", "dict1", db_connection)) == 1000

# 性能测试
def test_performance(db_connection, benchmark):
    benchmark.pedantic(
        get_last_7_days_learning_counts,
        args=("user1", "dict1", db_connection.cursor()),
        rounds=100
    )