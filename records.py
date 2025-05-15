# records.py
from auth import connect_db


def mark_word(username, word, mastered, db_path=None):
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO records (username, word, mastered)
            VALUES (?, ?, ?)
        ''', (username, word.lower(), mastered))
        conn.commit()

def get_mastered_words(username, db_path=None):
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT word FROM records
            WHERE username = ? AND mastered = 1
        ''', (username,))
        return [row[0] for row in cursor.fetchall()]

def get_unfamiliar_words(username, db_path=None):
    """获取不熟的单词（mastered=0）"""
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT word FROM records
            WHERE username = ? AND mastered = 0
        ''', (username,))
        return [row[0] for row in cursor.fetchall()]

def get_unknown_words(username, db_path=None):
    """获取不认识的单词（mastered=-1）"""
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT word FROM records
            WHERE username = ? AND mastered = -1
        ''', (username,))
        return [row[0] for row in cursor.fetchall()]


    
def get_all_records(username, db_path=None):
    with connect_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT word, mastered FROM records
            WHERE username = ?
        ''', (username,))
        return cursor.fetchall()
