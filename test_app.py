import pytest
from flask import url_for
from datetime import datetime, timedelta
from app import app, init_db, get_dict_files
from auth import connect_db
from records import mark_word, get_user_progress
import json

# 测试夹具
@pytest.fixture(scope="module")
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
            yield client

# 数据准备夹具
@pytest.fixture
def create_test_user(client):
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    yield
    # 清理数据
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username='testuser'")
    conn.commit()
    conn.close()

# 功能测试
def test_login_logout(client):
    # 测试登录流程
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    assert response.status_code == 302
    assert 'username' in client.session

    # 测试注销流程
    response = client.get('/logout')
    assert 'username' not in client.session

# 会话管理测试
def test_session_persistence(client):
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    response = client.get('/home')
    assert b'Welcome, testuser' in response.data

# 主页功能测试
def test_home_page(client, create_test_user):
    response = client.get('/home')
    assert response.status_code == 302  # 重定向到登录

    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    response = client.get('/home')
    assert b'Learning Statistics' in response.data
    assert b'Study Plan' in response.data

# 学习功能测试
def test_learn_page(client, create_test_user):
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    response = client.get('/learn')
    assert b'New Words' in response.data
    assert b'Word List' in response.data

# 复习功能测试
def test_review_page(client, create_test_user):
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    response = client.get('/review')
    assert b'Review Mode' in response.data
    assert b'Start Review' in response.data

# 数据库操作测试
def test_mark_word(client, create_test_user):
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # 标记单词
    with client.session_transaction() as sess:
        sess['selected_dict'] = 'test_dict.json'
    
    response = client.post('/home', data={
        'mark_word': 'apple',
        'level': 1
    })
    assert b'Marked successfully' in response.data
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT mastered FROM records WHERE username='testuser' AND word='apple'")
    assert cursor.fetchone()[0] == 1
    conn.close()

# 时间敏感测试
def test_review_scheduling(client, create_test_user, freezer):
    freezer.move_to(datetime(2024, 3, 20))
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    with client.session_transaction() as sess:
        sess['selected_dict'] = 'test_dict.json'
    
    response = client.post('/home', data={
        'mark_word': 'apple',
        'level': 0
    })
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT next_review FROM records WHERE username='testuser' AND word='apple'")
    next_review = cursor.fetchone()[0]
    assert next_review == datetime(2024, 3, 21).date().isoformat()
    conn.close()

# 性能测试
def test_performance(client, benchmark):
    benchmark.pedantic(
        client.get,
        args=('/home',),
        rounds=100
    )