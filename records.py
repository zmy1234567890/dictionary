'''
单词学习记录系统，支持标记单词掌握程度（已掌握/模糊/不认识）并分类查询用户的学习记录
'''
# records.py
from auth import connect_db
from datetime import datetime, timedelta,date
import sqlite3

def mark_word(username, word, dict_file, mastered, db_path=None):
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO records (username, word, dict_file, mastered)
            VALUES (?, ?, ?, ?)
        ''', (username, word.lower(), dict_file, mastered))

        # 记录每日学习词数
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            INSERT INTO daily_progress (username, word, dict_file, date, mastered)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, word.lower(), dict_file, today, mastered))

        conn.commit()

def get_mastered_words(username, dict_file, db_path=None):
    """获取某词书中掌握的单词（mastered=1）"""
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT word FROM records
            WHERE username = ? AND dict_file = ? AND mastered = 1
        ''', (username, dict_file))
        return [row[0] for row in cursor.fetchall()]

def get_unfamiliar_words(username, dict_file, db_path=None):
    """获取某词书中模糊的单词（mastered=0）"""
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT word FROM records
            WHERE username = ? AND dict_file = ? AND mastered = 0
        ''', (username, dict_file))
        return [row[0] for row in cursor.fetchall()]

def get_unknown_words(username, dict_file, db_path=None):
    """获取某词书中不认识的单词（mastered=-1）"""
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT word FROM records
            WHERE username = ? AND dict_file = ? AND mastered = -1
        ''', (username, dict_file))
        return [row[0] for row in cursor.fetchall()]

def get_user_progress(username, dict_file, db_path=None):
    """
    返回字典 {word: mastered_level}，整合了掌握、新认识、不认识的所有单词状态
    """
    progress = {}
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT word, mastered FROM records
            WHERE username = ? AND dict_file = ?
        ''', (username, dict_file))
        rows = cursor.fetchall()
        for word, mastered in rows:
            progress[word] = mastered
    return progress

def get_all_records(username, dict_file, db_path=None):
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT word, mastered FROM records
            WHERE username = ? AND dict_file = ?
        ''', (username, dict_file))
        return cursor.fetchall()
    

'''
学习相关代码
'''
def get_daily_count(username, target_date, dict_file=None, db_path=None):
    """
    获取某用户在某日（字符串格式）学习的不同单词总数
    可选按词库过滤
    """
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        if dict_file:
            cursor.execute('''
                SELECT COUNT(DISTINCT word) FROM daily_progress
                WHERE username = ? AND date = ? AND dict_file = ?
            ''', (username, target_date, dict_file))
        else:
            cursor.execute('''
                SELECT COUNT(DISTINCT word) FROM daily_progress
                WHERE username = ? AND date = ?
            ''', (username, target_date))
        result = cursor.fetchone()
        return result[0] if result else 0

def get_total_words_learned(username, dict_file,cursor):
    """获取某用户学习的总单词数"""
    cursor.execute('''
        SELECT COUNT(DISTINCT word)
        FROM daily_progress
        WHERE username = ? AND dict_file = ?
    ''', (username,dict_file))
    return cursor.fetchone()[0] or 0

def get_today_progress_distribution(username, target_date, dict_file):
    """返回今天掌握 / 模糊 / 不认识 的单词比例（百分比）"""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT mastered FROM daily_progress
            WHERE username = ? AND date = ? AND dict_file = ?
        ''', (username, target_date, dict_file))
        rows = cursor.fetchall()

    total = len(rows) or 1  
    mastered_count = sum(1 for (m,) in rows if m == 1)
    unfamiliar_count = sum(1 for (m,) in rows if m == 0)
    unknown_count = sum(1 for (m,) in rows if m == -1)

    return {
        'mastered_percent': round(mastered_count / total * 100, 1),
        'unfamiliar_percent': round(unfamiliar_count / total * 100, 1),
        'unknown_percent': round(unknown_count / total * 100, 1)
    }

def get_last_7_days_learning_counts(username, dict_file, cursor):
    """获取最近7天学习的单词数，逆序返回"""
    counts = []
    for i in reversed(range(7)):  # 0到6，最近7天，逆序方便前端按时间顺序显示
        date_str = (datetime.today() - timedelta(days=i)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(DISTINCT word)
            FROM daily_progress
            WHERE username = ? AND dict_file = ? AND date = ?
        ''', (username, dict_file, date_str))
        count = cursor.fetchone()[0] or 0
        counts.append(count)
    return counts

'''
复习相关代码
'''

def schedule_next_review(username, word, dict_file, mastered, correct, db_path="data/users.db"):
    from datetime import datetime, timedelta, date
    import sqlite3

    review_intervals = {
        -1: [0, 1, 2, 3, 7, 14, 30],  # 不认识的单词（含模糊）
         0: [0, 1, 3, 7, 14, 30]      # 熟悉的单词
    }

    today = datetime.today().date()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT review_stage, mastered FROM records
        WHERE username = ? AND word = ? AND dict_file = ?
    ''', (username, word, dict_file))
    row = cursor.fetchone()

    current_stage, current_mastered = row

    if correct == 1:
        new_mastered = current_mastered
        new_stage = (current_stage or 0) + 1  
        intervals = review_intervals.get(new_mastered, [0])
        if new_stage >= len(intervals):
            next_review = date(2099, 1, 1)  # 视为掌握
        else:
            next_review = today + timedelta(days=intervals[new_stage])

        cursor.execute('''
            UPDATE records
            SET mastered = ?, review_stage = ?, next_review = ?, last_review = ?
            WHERE username = ? AND word = ? AND dict_file = ?
        ''', (
            new_mastered, new_stage, next_review.isoformat(), today.isoformat(),
            username, word, dict_file
        ))
            
    elif correct == -1: # correct = -1代表新学习
        new_mastered = current_mastered
        new_stage = 0
        next_review = today


        cursor.execute('''
            UPDATE records
            SET mastered = ?, review_stage = ?, next_review = ?, last_review = ?
            WHERE username = ? AND word = ? AND dict_file = ?
        ''', (
            new_mastered, new_stage, next_review.isoformat(), date(2099, 1, 1),
            username, word, dict_file
        ))

    else:
        new_mastered = -1
        new_stage = 0
        next_review = today + timedelta(days=1)

        cursor.execute('''
            UPDATE records
            SET mastered = ?, review_stage = ?, next_review = ?, last_review = ?
            WHERE username = ? AND word = ? AND dict_file = ?
        ''', (
            new_mastered, new_stage, next_review.isoformat(), today.isoformat(),
            username, word, dict_file
        ))

    conn.commit()
    conn.close()

def get_review_list(username, dict_file, db_path="data/users.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    today = datetime.today().date()

    # 更新过期复习日期
    cursor.execute('''
        UPDATE records
        SET next_review = ?
        WHERE username = ? AND dict_file = ? AND next_review < ?
    ''', (today, username, dict_file, today))

    conn.commit()

    cursor.execute('''
        SELECT word, next_review FROM records
        WHERE username = ? AND dict_file = ? AND mastered != 1
        ORDER BY next_review ASC
    ''', (username, dict_file))
    results = cursor.fetchall()

    conn.close()
    return results

def get_today_review_words(username, dict_file, db_path="data/users.db"):
    from datetime import date
    import sqlite3

    today = date.today().isoformat() 

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 更新过期复习日期
    cursor.execute('''
        UPDATE records
        SET next_review = ?
        WHERE username = ? AND dict_file = ? AND next_review < ?
    ''', (today, username, dict_file, today))

    conn.commit()

    cursor.execute('''
        SELECT word FROM records
        WHERE username = ? AND dict_file = ? AND next_review = ?
    ''', (username, dict_file, today))

    words = [row[0] for row in cursor.fetchall()]
    conn.close()
    return words


def get_today_reviewed_words(username, dict_file, db_path="data/users.db"):
    """
    返回用户当天已经复习的单词列表（依据 last_review = 今天）
    """
    today_str = datetime.today().date().isoformat()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT word FROM records
        WHERE username = ? AND dict_file = ? AND last_review = ?
    ''', (username, dict_file, today_str))
    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]

def get_last_7_days_review_counts(username, dict_file, cursor):
    """获取最近7天复习的单词数，逆序返回"""
    counts = []
    for i in reversed(range(7)):
        date_str = (datetime.today() - timedelta(days=i)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(DISTINCT word)
            FROM records
            WHERE username = ? AND dict_file = ? AND last_review = ?
        ''', (username,dict_file, date_str))
        count = cursor.fetchone()[0] or 0
        counts.append(count)
    return counts