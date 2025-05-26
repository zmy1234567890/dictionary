#app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from auth import connect_db,init_db, register_user, validate_user
from lookup import Dictionary
from records import mark_word, get_mastered_words, get_unfamiliar_words, get_unknown_words, get_user_progress,get_daily_count,get_last_7_days_learning_counts,get_total_words_learned,schedule_next_review,get_review_list,get_today_review_words,get_today_reviewed_words,get_last_7_days_review_counts
from quiz import start_quiz_EC, start_quiz_CE
from datetime import date,datetime, timedelta
import random
import os
# 创建 Flask 应用
app = Flask(__name__)
app.secret_key = 'secret-key' # 设置会话密钥
# 初始化数据库结构
init_db()
# 获取当前 data 目录下所有 JSON 词典文件
def get_dict_files():
    dict_dir = "data"
    return [f for f in os.listdir(dict_dir) if f.endswith(".json")]

'''判断用户登录状态'''
@app.route('/')
def index():
    # 如果用户已登录，则跳转主页；否则跳转登录页
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

'''登录页面'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 登录页处理逻辑
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = validate_user(username, password)
        if user:
            session['username'] = username
            flash('登录成功！')
            return redirect(url_for('home'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')

'''注销登录：清除当前用户 session'''
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('selected_dict', None)
    flash('已注销登录')
    return redirect(url_for('login'))

'''主页'''
@app.route('/home', methods=['GET', 'POST'])
def home():
    # 主页面展示逻辑
    if 'username' not in session:
        return redirect(url_for('login')) # 未登录用户重定向至登录页
    
    username = session['username']
    dict_files = get_dict_files() # 获取词书列表

    # 用户选择词典文件时记录下来
    if request.method == 'POST' and 'dict_select' in request.form:
        session['selected_dict'] = request.form['dict_select']
    
    selected_dict = session.get('selected_dict', dict_files[0])
    dictionary = Dictionary(os.path.join('data', selected_dict))# 加载词典

    word_info = None

    if request.method == 'POST':
        # 查单词
        if 'lookup_word' in request.form:
            word = request.form['lookup_word'].strip().lower()
            word_info = dictionary.lookup(word)

        # 标记熟悉程度
        elif 'mark_word' in request.form:
            word = request.form['word']
            level = int(request.form['level'])

            # 标记熟悉程度
            mark_word(username, word, selected_dict, mastered=level)
            flash(f'单词"{word}"标记成功！')

            # 如果是模糊或不认识，则加入复习计划
            if level in (-1, 0):
                print(f"Adding {word} to review schedule")
                schedule_next_review(username, word, selected_dict, level, correct=-1)

        # 设置每日词数
        elif 'set_daily_count' in request.form:
            try:
                session['daily_count'] = int(request.form['daily_count'])
            except (ValueError, TypeError):
                flash('请输入有效的每日词数')

    # 获取熟悉/不熟/未学单词
    mastered = get_mastered_words(username, selected_dict)
    unknown = get_unknown_words(username, selected_dict)
    unfamiliar = get_unfamiliar_words(username, selected_dict)

    # 获取今日学习词数
    today_str = date.today().isoformat()
    today_learned_count = get_daily_count(username, today_str, selected_dict)

    # 从 session 中读取每日词数（用于显示）,如果用户未设置每日学习目标，设置默认值为 20
    daily_count = session.get('daily_count', '')
    if daily_count is None:
        daily_count = 20
        session['daily_count'] = 20
    # 渲染主页模板，传入词库及统计数据
    return render_template('home.html',
                           username=username,
                           dict_files=dict_files,
                           selected_dict=selected_dict,
                           word_info=word_info,
                           mastered=mastered,
                           unknown=unknown,
                           unfamiliar=unfamiliar,
                           daily_count=daily_count,
                           today_learned_count=today_learned_count)


'''个人中心：用户学习数据可视化页面'''
@app.route("/profile", methods=["GET", "POST"])
def profile():
    # 用户学习数据可视化页面（进度、复习曲线、掌握比例）
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']

    conn = connect_db()
    cursor = conn.cursor()

    dict_files = get_dict_files()
    
    # 词书选择处理
    if request.method == 'POST' and 'dict_select' in request.form:
        session['selected_dict'] = request.form['dict_select']
    selected_dict = session.get('selected_dict', dict_files[0])

    # 加载词典及学习状态
    mastered = get_mastered_words(username, selected_dict)
    unknown = get_unknown_words(username, selected_dict)
    unfamiliar = get_unfamiliar_words(username, selected_dict)

    dict_path = os.path.join("data", selected_dict)
    dictionary = Dictionary(dict_path)

    dictionary_words = set(dictionary.dictionary.keys())
    # 统计总学习进度
    mastered_count = len(mastered)
    unfamiliar_count = len(unfamiliar)
    unknown_count = len(unknown)
    learned_count = mastered_count + unfamiliar_count + unknown_count
    total_count = len(dictionary_words)

    mastered_percent = round((mastered_count / total_count) * 100, 1) if total_count else 0
    unfamiliar_percent = round((unfamiliar_count / total_count) * 100, 1) if total_count else 0
    unknown_percent = round((unknown_count / total_count) * 100, 1) if total_count else 0

    # 今日学习数量
    today_str = date.today().isoformat()
    today_learned_count = get_daily_count(username, today_str, selected_dict)

    # 今日学习的掌握比例（用于进度条）
    cursor.execute('''
        SELECT mastered FROM daily_progress
        WHERE username = ? AND date = ? AND dict_file = ?
    ''', (username, today_str, selected_dict))
    rows = cursor.fetchall()

    today_total = len(rows) or 1  # 防止除0
    today_mastered_count = sum(1 for (m,) in rows if m == 1)
    today_unfamiliar_count = sum(1 for (m,) in rows if m == 0)
    today_unknown_count = sum(1 for (m,) in rows if m == -1)

    today_mastered_percent = round(today_mastered_count / today_total * 100, 1)
    today_unfamiliar_percent = round(today_unfamiliar_count / today_total * 100, 1)
    today_unknown_percent = round(today_unknown_count / today_total * 100, 1)

    # 取学习与复习曲线数据(近7天)
    learning7_counts = get_last_7_days_learning_counts(username,selected_dict, cursor)
    review7_counts = get_last_7_days_review_counts(username, selected_dict,cursor)
    days = [(datetime.today() - timedelta(days=i)).strftime('%m-%d') for i in reversed(range(7))]
    # 总词汇学习量与今日复习信息
    total_learned = get_total_words_learned(username, selected_dict,cursor)
    pending_reviews = get_review_list(username, selected_dict)

    today_review_words = get_today_review_words(username, selected_dict)
    today_reviewed_words = get_today_reviewed_words(username, selected_dict)
    today_reviewed_words_count = len(today_reviewed_words)
    today_plan_review_words_count = len(today_reviewed_words) + len(today_review_words)

    daily_count = session.get('daily_count', '')

    conn.close()
    # 渲染个人进度页
    return render_template(
        "profile.html",
        username=username,
        mastered=mastered,
        unfamiliar=unfamiliar,
        unknown=unknown,
        selected_dict=selected_dict,
        mastered_count=mastered_count,
        unfamiliar_count=unfamiliar_count,
        unknown_count=unknown_count,
        learned_count=learned_count,
        total_count=total_count,
        daily_count=daily_count,
        mastered_percent=mastered_percent,
        unfamiliar_percent=unfamiliar_percent,
        unknown_percent=unknown_percent,
        today_learned_count=today_learned_count,
        days=days,
        learning7_counts=learning7_counts,
        review7_counts=review7_counts,
        total_learned=total_learned,
        pending_reviews=pending_reviews,
        today_reviewed_words_count=today_reviewed_words_count,
        today_plan_review_words_count=today_plan_review_words_count,
        today_mastered_percent=today_mastered_percent,
        today_unfamiliar_percent=today_unfamiliar_percent,
        today_unknown_percent=today_unknown_percent
    )

'''学习页面'''
@app.route('/learn', methods=['GET', 'POST'])
def learn():
    # 用户学习未接触过的单词页面
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    dict_files = get_dict_files()
    # 处理词典选择
    if request.method == 'POST' and not request.is_json and 'dict_select' in request.form:
        session['selected_dict'] = request.form['dict_select']

    selected_dict = session.get('selected_dict', dict_files[0])
    dict_path = os.path.join("data", selected_dict)
    dictionary = Dictionary(dict_path)
    all_words = list(dictionary.dictionary.keys())
    # 获取当前用户该词典下的学习记录
    user_progress = get_user_progress(username, selected_dict)
    learn_list = [w for w in all_words if w not in user_progress]

    paged_learn_list = learn_list
    total_words = len(learn_list)

    # 获取今日学习词数
    today_str = date.today().isoformat()
    today_learned_count = get_daily_count(username, today_str, selected_dict)

    # 从 session 中读取每日词数（用于显示）
    daily_count = session.get('daily_count', '')
    daily_count = int(daily_count) if daily_count else 20
    # 处理用户标记熟悉度行为
    if request.method == 'POST' and not request.is_json:
        if 'word' in request.form and 'level' in request.form:
            word = request.form['word']
            level = int(request.form['level'])
            if word in all_words:
                mark_word(username, word, selected_dict, level)
                user_progress[word] = level

                if level in (-1, 0):  # 仅对 模糊 或 不认识 进入复习计划
                    print("[DEBUG] Scheduling review for word:", word)
                    schedule_next_review(username, word, selected_dict, level, correct=-1)

            # 标记全部单词时，直接跳转首页
            all_marked = all(w in user_progress for w in paged_learn_list)
            if all_marked:
                return redirect(url_for('home'))

            return redirect(url_for('learn'))
    # 提取展示单词详细信息（翻译与例句）
    entries = []
    for w in paged_learn_list:
        info = dictionary.lookup(w)
        if info:
            entries.append(info)

    return render_template('learn.html',
                           words=entries,
                           total=total_words,
                           daily_count=int(daily_count),
                           today_learned_count=int(today_learned_count))

''''''
@app.route('/review', methods=['GET', 'POST'])
def review():
    # 用户每日复习单词页面（根据记忆曲线安排）
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    dict_files = get_dict_files()
    selected_dict = session.get('selected_dict', dict_files[0])
    if not selected_dict:
        return redirect(url_for('home'))

    dict_path = os.path.join("data", selected_dict)
    dictionary = Dictionary(dict_path)

    user_progress = get_user_progress(username, selected_dict)
    review_words = get_today_review_words(username, selected_dict)

    # ---- 处理 GET：开始一次新的测试 ----
    if request.method == 'GET' and 'mode' in request.args:
        mode = request.args['mode']
        if not review_words:
            return render_template('review_Interpretation.html', finished=True, score=0, total=0)
        # 根据模式生成题目（英译中 or 中译英）
        if mode == 'definition':
            questions = start_quiz_EC(dictionary, review_words)
        elif mode == 'spelling':
            questions = start_quiz_CE(dictionary, review_words)
        else:
            return redirect(url_for('home'))
        # 将复习任务存入 session
        session['review_questions'] = questions
        session['review_mode'] = mode
        session['review_index'] = 0
        session['review_answers'] = []
        session['review_finished_flag'] = False  # ✅ 初始化状态标记

        return redirect(url_for('review'))

    # ---- 加载当前状态 ----
    questions = session.get('review_questions', [])
    mode = session.get('review_mode', '')
    index = session.get('review_index', 0)
    answers = session.get('review_answers', [])

    if not questions or not mode:
        return redirect(url_for('home'))

    # ---- 处理 POST 提交 ----
    if request.method == 'POST':
        action = request.form.get('action')

        # 处理答题选择
        if 'choice' in request.form:
            selected = request.form['choice']
            correct = questions[index]['answer']
            if correct == selected:
                is_correct =1
            else:
                is_correct = 0
            # 记录用户本题选择情况
            if len(answers) <= index:
                answers.append({'selected': selected, 'correct': correct, 'is_correct': is_correct})
            else:
                answers[index] = {'selected': selected, 'correct': correct, 'is_correct': is_correct}

            session['review_answers'] = answers

        # 导航操作
        if action == 'next' and index < len(questions) - 1:
            index += 1
        elif action == 'prev' and index > 0:
            index -= 1

        session['review_index'] = index

    # ---- 再次加载状态：确保答案已更新 ----
    answers = session.get('review_answers', [])
    finished = len(answers) == len(questions)
    score = sum(1 for ans in answers if ans.get('is_correct'))

    # ---- 全部完成后：统一更新进度----
    if finished and not session.get('review_finished_flag'):
        for i, answer in enumerate(answers):
            word = questions[i].get('word')
            is_correct = answer.get('is_correct')
            if word:
                mastered = user_progress.get(word)
                if mastered in (-1, 0):
                    schedule_next_review(username, word, selected_dict, mastered, correct=is_correct)

        session['review_finished_flag'] = True  # ✅ 防止重复执行

    # ---- 渲染页面 ----
    current_question = questions[index]
    current_answer = answers[index] if index < len(answers) else None

    return render_template(
        'review_Interpretation.html' if mode == 'definition' else 'review_Spelling.html',
        question=current_question,
        selected=current_answer['selected'] if current_answer else None,
        is_correct=current_answer['is_correct'] if current_answer else None,
        current=index,
        total=len(questions),
        score=score,
        finished=finished
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

