# records.py
from auth import connect_db

def mark_word(username, word, mastered=True):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO records (username, word, mastered)
            VALUES (?, ?, ?)
        ''', (username, word, int(mastered)))
        conn.commit()

def get_mastered_words(username):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT word FROM records
            WHERE username = ? AND mastered = 1
        ''', (username,))
        return [row[0] for row in cursor.fetchall()]

def get_unmastered_words(username):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT word FROM records
            WHERE username = ? AND mastered = 0
        ''', (username,))
        return [row[0] for row in cursor.fetchall()]