import pytest
from auth import init_db, validate_user, delete_user, update_password
from auth import get_all_users, get_all_records
import sqlite3
import os

# 测试夹具
@pytest.fixture(scope="module")
def db_connection():
    # 创建临时数据库
    test_db = "test_users.db"
    conn = sqlite3.connect(test_db)
    yield conn
    conn.close()
    os.remove(test_db)

def test_init_db(db_connection):
    init_db(db_path=test_db)
    cursor = db_connection.cursor()
    
    # 验证表结构
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    assert set(columns) == {"username", "password", "is_admin"}

    # 验证admin账户
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    admin = cursor.fetchone()
    assert admin[2] == 1  # is_admin验证

def test_password_security(db_connection):
    init_db(db_path=test_db)
    # 测试明文存储漏洞
    cursor = db_connection.cursor()
    cursor.execute("SELECT password FROM users WHERE username='admin'")
    stored_pw = cursor.fetchone()[0]
    assert stored_pw == "admin123"  # 明文存储警告

def test_login_cases(db_connection):
    init_db(db_path=test_db)
    
    # 正确登录
    success, is_admin, msg = validate_user("admin", "admin123", test_db)
    assert success and is_admin

    # 错误密码
    success, _, msg = validate_user("admin", "wrongpass", test_db)
    assert not success and "错误" in msg

    # 不存在用户
    success, _, msg = validate_user("unknown", "nopass", test_db)
    assert not success and "错误" in msg

def test_admin_operations(db_connection):
    init_db(db_path=test_db)
    
    # 普通用户创建
    with connect_db(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES ('user1', 'pass1', 0)")
        conn.commit()

    # 权限验证
    success, is_admin, _ = validate_user("user1", "pass1", test_db)
    assert not is_admin

    # 删除用户测试
    assert delete_user("user1", test_db)
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='user1'")
    assert cursor.fetchone() is None

def test_data_integrity(db_connection):
    init_db(db_path=test_db)
    
    # 添加测试数据
    with connect_db(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES ('test', 'testpw', 0)")
        cursor.execute("INSERT INTO records VALUES ('test', 'apple', 1, 0, '2024-03-20', '2024-03-19', 'dict')")
        conn.commit()

    # 级联删除测试
    delete_user("test", test_db)
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM records WHERE username='test'")
    assert cursor.fetchone() is None

def test_edge_cases(db_connection):
    init_db(db_path=test_db)
    
    # 超长用户名
    long_name = "a"*256
    with connect_db(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES (?, 'pass', 0)", (long_name,))
        conn.commit()
    
    # 特殊字符密码
    special_pw = "!@#$%^&*()"
    with connect_db(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES ('spec', ?, 0)", (special_pw,))
        conn.commit()



