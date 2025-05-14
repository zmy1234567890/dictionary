import unittest
import tempfile
import os
import sqlite3
from unittest.mock import patch
from auth import init_db, register, login, logout

class TestAuth(unittest.TestCase):
    def setUp(self):
        # 创建一个临时文件路径，不打开文件
        fd, self.db_path = tempfile.mkstemp()
        os.close(fd)  # 关闭文件描述符，避免文件占用
        init_db(self.db_path)

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except PermissionError:
            print(f"⚠️ 警告：无法删除 {self.db_path}，可能仍被占用。")

    @patch("builtins.input", side_effect=["testuser", "password123"])
    def test_register_new_user(self, mock_input):
        username = register(db_path=self.db_path)
        self.assertEqual(username, "testuser")

    @patch("builtins.input", side_effect=["testuser", "password123"])
    def test_register_existing_user(self, mock_input):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("testuser", "password123"))
        username = register(db_path=self.db_path)
        self.assertIsNone(username)

    @patch("builtins.input", side_effect=["testuser", "password123"])
    def test_login_success(self, mock_input):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("testuser", "password123"))
        username = login(db_path=self.db_path)
        self.assertEqual(username, "testuser")

    @patch("builtins.input", side_effect=["testuser", "wrongpass"])
    def test_login_fail(self, mock_input):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("testuser", "password123"))
        username = login(db_path=self.db_path)
        self.assertIsNone(username)

    def test_logout(self):
        result = logout()
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()

