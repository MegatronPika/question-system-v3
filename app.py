#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import random
import datetime
import time
import os
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# 数据文件路径
QUESTIONS_FILE = 'full_questions.json'
USER_DATA_FILE = os.environ.get('USER_DATA_FILE', 'user_data.json')

# 检查是否在Railway环境中
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') is not None

# 全局缓存
_questions_cache = None
_questions_cache_time = 0
CACHE_DURATION = 300  # 缓存5分钟

# 确保数据目录存在
DATA_DIR = os.path.dirname(USER_DATA_FILE) if os.path.dirname(USER_DATA_FILE) else '.'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

def load_questions():
    """加载题目数据（带缓存）"""
    global _questions_cache, _questions_cache_time
    
    current_time = time.time()
    
    # 检查缓存是否有效
    if (_questions_cache is not None and 
        current_time - _questions_cache_time < CACHE_DURATION):
        return _questions_cache
    
    # 尝试从pickle缓存加载
    try:
        import pickle
        with open('questions_cache.pkl', 'rb') as f:
            cache_data = pickle.load(f)
        _questions_cache = cache_data['questions']
        _questions_cache_time = current_time
        print(f"Questions loaded from cache: {len(_questions_cache)} questions")
        return _questions_cache
    except Exception as e:
        print(f"Cache loading failed: {e}, falling back to JSON")
        
        # 回退到JSON加载
        try:
            with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            _questions_cache = data['questions']
            _questions_cache_time = current_time
            print(f"Questions loaded from JSON: {len(_questions_cache)} questions")
            return _questions_cache
        except Exception as e2:
            print(f"Error loading questions: {e2}")
            # 如果加载失败但有缓存，返回缓存
            if _questions_cache is not None:
                return _questions_cache
            # 否则返回空列表
            return []

def load_user_data():
    """加载用户数据"""
    # 在Railway环境中，优先从持久化存储读取
    if IS_RAILWAY:
        # 尝试从持久化卷读取
        persistent_file = '/data/user_data.json'
        if os.path.exists(persistent_file):
            try:
                with open(persistent_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load from persistent storage: {e}")
        
        # 尝试从环境变量读取
        env_data = os.environ.get('USER_DATA_JSON')
        if env_data:
            try:
                return json.loads(env_data)
            except json.JSONDecodeError:
                print("Warning: Invalid JSON in USER_DATA_JSON environment variable")
    
    # 从本地文件读取
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {
        'users': {},
        'user_profiles': {},
        'wrong_questions': {},
        'exam_records': {}
    }

def save_user_data(data):
    """保存用户数据"""
    # 转换set为list以便JSON序列化
    for user_id in data['users']:
        if 'answered_questions' in data['users'][user_id]:
            data['users'][user_id]['answered_questions'] = list(data['users'][user_id]['answered_questions'])
        if 'wrong_questions' in data['users'][user_id]:
            data['users'][user_id]['wrong_questions'] = list(data['users'][user_id]['wrong_questions'])
        if 'important_questions' in data['users'][user_id]:
            data['users'][user_id]['important_questions'] = list(data['users'][user_id]['important_questions'])
    
    # 在Railway环境中，保存到持久化存储
    if IS_RAILWAY:
        try:
            # 保存到持久化卷
            persistent_file = '/data/user_data.json'
            os.makedirs('/data', exist_ok=True)
            with open(persistent_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            print(f"Data saved to persistent storage: {persistent_file}")
        except Exception as e:
            print(f"Warning: Failed to save to persistent storage: {e}")
    
    # 保存到本地文件（确保数据持久化）
    try:
        # 确保目录存在
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # 先保存到临时文件，然后重命名（原子操作）
        temp_file = f"{USER_DATA_FILE}.tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        # 原子性地重命名文件
        os.replace(temp_file, USER_DATA_FILE)
        print(f"Data saved to local file: {USER_DATA_FILE}")
        
    except Exception as e:
        print(f"Error saving user data: {e}")
        # 如果保存失败，尝试直接保存
        try:
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e2:
            print(f"Critical error: Failed to save user data: {e2}")

def get_client_ip():
    """获取客户端IP"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def get_user_agent():
    """获取用户代理"""
    return request.headers.get('User-Agent', '')

def create_session_id():
    """创建会话ID"""
    ip = get_client_ip()
    user_agent = get_user_agent()
    return hashlib.md5(f"{ip}:{user_agent}".encode()).hexdigest()

def is_logged_in():
    """检查用户是否已登录"""
    return 'user_id' in session

def require_login(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_user_data():
    """获取当前用户数据"""
    user_data = load_user_data()
    user_id = session.get('user_id')
    
    if not user_id or user_id not in user_data['users']:
        return None, None
    
    # 将list转换回set
    if 'answered_questions' in user_data['users'][user_id]:
        user_data['users'][user_id]['answered_questions'] = set(user_data['users'][user_id]['answered_questions'])
    if 'wrong_questions' in user_data['users'][user_id]:
        user_data['users'][user_id]['wrong_questions'] = set(user_data['users'][user_id]['wrong_questions'])
    if 'important_questions' in user_data['users'][user_id]:
        # 转回 set 并规范化为整型ID（若可转换）
        imp_src = user_data['users'][user_id]['important_questions']
        try:
            iter_values = list(imp_src)
        except TypeError:
            iter_values = []
        norm_set = set()
        for v in iter_values:
            if isinstance(v, str) and v.isdigit():
                try:
                    norm_set.add(int(v))
                except Exception:
                    norm_set.add(v)
            else:
                norm_set.add(v)
        user_data['users'][user_id]['important_questions'] = norm_set
    
    if user_id not in user_data['wrong_questions']:
        user_data['wrong_questions'][user_id] = []
    
    if user_id not in user_data['exam_records']:
        user_data['exam_records'][user_id] = []
    
    return user_data, user_id

# 辅助函数：解析ISO时间
def _parse_iso(ts: str):
    try:
        return datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except Exception:
        try:
            return datetime.datetime.fromisoformat(ts)
        except Exception:
            return datetime.datetime.now()

# 辅助函数：按考试记录中的 answers 评分并完成考试
def _finalize_exam_from_record(user_data, user_id, exam_record):
    answers = exam_record.get('answers', {}) or {}
    total_score = 0
    wrong_answers = []
    for question in exam_record['questions']:
        qid = question['id']
        user_answer = answers.get(str(qid), '')
        correct_answer = question['correct_answer']
        if question['type'] == 2:
            if isinstance(user_answer, str):
                user_answer = [user_answer] if user_answer else []
            elif user_answer is None:
                user_answer = []
            is_correct = set(correct_answer.split(',')) == set(user_answer)
        else:
            is_correct = user_answer == correct_answer

        is_unanswered = (
            (question['type'] == 2 and (not user_answer)) or
            (question['type'] != 2 and (user_answer is None or user_answer == ''))
        )

        if is_correct:
            total_score += question['score']
            user_data['users'][user_id]['answered_questions'].add(qid)
        else:
            wrong_answers.append({
                'question_id': qid,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'question_content': question['content'],
                'analysis': question['analysis'],
                'type': question['type'],
                'score': question['score']
            })
            if not is_unanswered:
                user_data['users'][user_id]['wrong_questions'].add(qid)
                user_data['users'][user_id]['answered_questions'].add(qid)
                wrong_record = {
                    'question_id': qid,
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'question_content': question['content'],
                    'analysis': question['analysis'],
                    'type': question['type']
                }
                user_data['wrong_questions'][user_id].append(wrong_record)
                if qid not in user_data['users'][user_id]['wrong_count']:
                    user_data['users'][user_id]['wrong_count'][qid] = 0
                user_data['users'][user_id]['wrong_count'][qid] += 1

    exam_record['end_time'] = datetime.datetime.now().isoformat()
    exam_record['status'] = 'completed'
    exam_record['total_score'] = total_score
    exam_record['wrong_answers'] = wrong_answers
    save_user_data(user_data)
    return total_score, wrong_answers

@app.route('/')
def index():
    """主页"""
    if is_logged_in():
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user_data = load_user_data()
        
        # 检查用户名是否存在
        if username not in user_data['user_profiles']:
            return jsonify({'success': False, 'message': '用户名不存在'})
        
        # 验证密码
        if not check_password_hash(user_data['user_profiles'][username]['password'], password):
            return jsonify({'success': False, 'message': '密码错误'})
        
        # 登录成功
        session['user_id'] = username
        session['session_id'] = create_session_id()
        session['login_time'] = datetime.datetime.now().isoformat()
        
        # 更新用户登录信息
        user_data['user_profiles'][username]['last_login'] = datetime.datetime.now().isoformat()
        user_data['user_profiles'][username]['last_ip'] = get_client_ip()
        user_data['user_profiles'][username]['last_user_agent'] = get_user_agent()
        
        save_user_data(user_data)
        
        return jsonify({'success': True, 'message': '登录成功'})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # 验证输入
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'})
        
        if len(username) < 3:
            return jsonify({'success': False, 'message': '用户名至少3个字符'})
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': '密码至少6个字符'})
        
        if password != confirm_password:
            return jsonify({'success': False, 'message': '两次输入的密码不一致'})
        
        user_data = load_user_data()
        
        # 检查用户名是否已存在
        if username in user_data['user_profiles']:
            return jsonify({'success': False, 'message': '用户名已存在'})
        
        # 创建新用户
        user_data['user_profiles'][username] = {
            'password': generate_password_hash(password),
            'created_time': datetime.datetime.now().isoformat(),
            'last_login': None,
            'last_ip': None,
            'last_user_agent': None
        }
        
        # 初始化用户数据
        user_data['users'][username] = {
            'answered_questions': set(),
            'wrong_questions': set(),
            'wrong_count': {},
            'important_questions': set()
        }
        
        user_data['wrong_questions'][username] = []
        user_data['exam_records'][username] = []
        
        save_user_data(user_data)
        
        return jsonify({'success': True, 'message': '注册成功，请登录'})
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/random_practice')
@require_login
def random_practice():
    """随机做题页面"""
    return render_template('random_practice.html')

@app.route('/get_random_question', methods=['POST'])
@require_login
def get_random_question():
	"""获取随机题目"""
	data = request.get_json()
	mode = data.get('mode', 'all')
	# 新增：题型筛选（0/None=所有，1=单选，2=多选，3=判断）
	type_filter = data.get('type_filter') or data.get('type') or 0
	try:
		type_filter = int(type_filter)
	except (TypeError, ValueError):
		type_filter = 0
	
	questions = load_questions()
	user_data, user_id = get_user_data()
	
	if not user_data or not user_id:
		return jsonify({'error': '用户数据不存在'})
	
	if mode == 'unanswered':
		answered = user_data['users'][user_id]['answered_questions']
		available_questions = [q for q in questions if q['id'] not in answered]
		if not available_questions:
			return jsonify({'error': '已刷完所有题库，请选择全量题库或者错题库进行练习'})
	elif mode == 'wrong':
		wrong_questions = user_data['users'][user_id]['wrong_questions']
		available_questions = [q for q in questions if q['id'] in wrong_questions]
		if not available_questions:
			return jsonify({'error': '暂无错题记录'})
	elif mode == 'important':
		important = user_data['users'][user_id].get('important_questions', set())
		available_questions = [q for q in questions if q['id'] in important]
		if not available_questions:
			return jsonify({'error': '暂无重点题，请在题目详情中标记后再来试试'})
	else:
		available_questions = questions
	
	# 按题型筛选
	if type_filter in (1, 2, 3):
		available_questions = [q for q in available_questions if int(q.get('type', 0)) == type_filter]
		if not available_questions:
			return jsonify({'error': '所选题型暂无可用题目，请更换题型或模式'})
	
	question = random.choice(available_questions)
	
	# 如果是未做题库模式，立即将该题目标记为已做，避免重复
	if mode == 'unanswered':
		user_data['users'][user_id]['answered_questions'].add(question['id'])
		save_user_data(user_data)
	
	important_set = user_data['users'][user_id].get('important_questions', set())
	return jsonify({
		'id': question['id'],
		'number': question.get('number'),
		'content': question['content'],
		'options': question['options'],
		'type': question['type'],
		'score': question['score'],
		'is_important': (question['id'] in important_set)
	})

@app.route('/submit_answer', methods=['POST'])
@require_login
def submit_answer():
    """提交答案"""
    data = request.get_json()
    question_id = data.get('question_id')
    user_answer = data.get('answer')  # 可能是字符串或列表
    
    questions = load_questions()
    question = next((q for q in questions if q['id'] == question_id), None)
    
    if not question:
        return jsonify({'error': '题目不存在'})
    
    user_data, user_id = get_user_data()
    
    if not user_data or not user_id:
        return jsonify({'error': '用户数据不存在'})
    
    # 只有在题目未被标记为已做时才添加（避免在未做题库模式下重复添加）
    if question_id not in user_data['users'][user_id]['answered_questions']:
        user_data['users'][user_id]['answered_questions'].add(question_id)
    
    # 处理多选题答案
    if question['type'] == 2:  # 多选题
        # 确保user_answer是列表格式
        if isinstance(user_answer, str):
            user_answer = [user_answer] if user_answer else []
        elif user_answer is None:
            user_answer = []
        
        # 多选题答案比较
        correct_answers = set(question['correct_answer'].split(','))
        user_answers = set(user_answer)
        is_correct = correct_answers == user_answers
    else:
        # 单选题和判断题
        is_correct = user_answer == question['correct_answer']
    
    if not is_correct:
        user_data['users'][user_id]['wrong_questions'].add(question_id)
        
        wrong_record = {
            'question_id': question_id,
            'user_answer': user_answer,
            'correct_answer': question['correct_answer'],
            'timestamp': datetime.datetime.now().isoformat(),
            'question_content': question['content'],
            'analysis': question['analysis'],
            'type': question['type']
        }
        user_data['wrong_questions'][user_id].append(wrong_record)
        
        if question_id not in user_data['users'][user_id]['wrong_count']:
            user_data['users'][user_id]['wrong_count'][question_id] = 0
        user_data['users'][user_id]['wrong_count'][question_id] += 1
    
    save_user_data(user_data)
    
    return jsonify({
        'is_correct': is_correct,
        'correct_answer': question['correct_answer'],
        'analysis': question['analysis']
    })

@app.route('/exam')
@require_login
def exam():
    """考试页面"""
    return render_template('exam.html')

@app.route('/start_exam', methods=['POST'])
@require_login
def start_exam():
    """开始考试（如有未完成考试则恢复）"""
    user_data, user_id = get_user_data()
    # 若已有进行中的考试，先尝试恢复
    for record in reversed(user_data['exam_records'][user_id]):
        if record.get('status') == 'ongoing':
            # 计算剩余时间，默认60分钟
            duration = record.get('duration_seconds', 3600)
            elapsed = (datetime.datetime.now() - _parse_iso(record['start_time'])).total_seconds()
            time_left = max(0, int(duration - elapsed))
            if time_left <= 0:
                _finalize_exam_from_record(user_data, user_id, record)
                break
            return jsonify({
                'exam_id': record['exam_id'],
                'questions': record['questions'],
                'answers': record.get('answers', {}),
                'time_left': time_left
            })

    # 创建新考试
    questions = load_questions()
    single_choice = [q for q in questions if q['type'] == 1]
    multi_choice = [q for q in questions if q['type'] == 2]
    true_false = [q for q in questions if q['type'] == 3]
    exam_questions = (
        random.sample(single_choice, 50) +
        random.sample(true_false, 50) +
        random.sample(multi_choice, 50)
    )
    exam_id = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    exam_info = {
        'exam_id': exam_id,
        'start_time': datetime.datetime.now().isoformat(),
        'questions': exam_questions,
        'status': 'ongoing',
        'answers': {},
        'duration_seconds': 3600
    }
    user_data['exam_records'][user_id].append(exam_info)
    save_user_data(user_data)
    return jsonify({'exam_id': exam_id, 'questions': exam_questions, 'answers': {}, 'time_left': 3600})

@app.route('/submit_exam', methods=['POST'])
@require_login
def submit_exam():
    """提交考试"""
    data = request.get_json()
    exam_id = data.get('exam_id')
    answers = data.get('answers', {})
    
    user_data, user_id = get_user_data()
    
    exam_record = None
    for record in user_data['exam_records'][user_id]:
        if record['exam_id'] == exam_id:
            exam_record = record
            break
    
    if not exam_record:
        return jsonify({'error': '考试记录不存在'})
    
    # 将答案存入记录并统一评分与结算
    exam_record['answers'] = answers
    total_score, wrong_answers = _finalize_exam_from_record(user_data, user_id, exam_record)
    return jsonify({'total_score': total_score, 'wrong_answers': wrong_answers})

@app.route('/save_exam_progress', methods=['POST'])
@require_login
def save_exam_progress():
    """保存考试作答进度（不评分）"""
    data = request.get_json() or {}
    exam_id = data.get('exam_id')
    answers = data.get('answers', {}) or {}
    user_data, user_id = get_user_data()
    if not user_data or not user_id:
        return jsonify({'success': False, 'message': '用户数据不存在'})
    if not exam_id:
        return jsonify({'success': False, 'message': '缺少考试ID'})
    for record in reversed(user_data['exam_records'][user_id]):
        if record.get('exam_id') == exam_id and record.get('status') == 'ongoing':
            record['answers'] = answers
            record['last_saved'] = datetime.datetime.now().isoformat()
            save_user_data(user_data)
            return jsonify({'success': True})
    return jsonify({'success': False, 'message': '考试不存在或已结束'})

@app.route('/wrong_questions')
@require_login
def wrong_questions():
    """错题记录页面"""
    return render_template('wrong_questions.html')

@app.route('/question_bank')
@require_login
def question_bank():
    """全量题库页面"""
    return render_template('question_bank.html')

@app.route('/important_bank')
@require_login
def important_bank():
    """重点题库页面"""
    return render_template('important_bank.html')

@app.route('/test_simple')
def test_simple():
    """简单测试页面"""
    return render_template('test_simple.html')

@app.route('/get_wrong_questions', methods=['POST'])
@require_login
def get_wrong_questions():
    """获取错题记录"""
    data = request.get_json()
    sort_by = data.get('sort_by', 'timestamp')
    
    user_data, user_id = get_user_data()
    wrong_records = user_data['wrong_questions'][user_id]
    
    # 加载题库数据以获取完整题目信息
    questions = load_questions()
    questions_dict = {q['id']: q for q in questions}
    
    # 统计每个题目的做错次数
    question_wrong_count = {}
    for record in wrong_records:
        question_id = record['question_id']
        if question_id not in question_wrong_count:
            question_wrong_count[question_id] = 0
        question_wrong_count[question_id] += 1
    
    # 为每个错题记录添加做错次数和完整题目信息
    for record in wrong_records:
        question_id = record['question_id']
        # 使用从wrong_records统计的实际做错次数，而不是从wrong_count字段
        record['wrong_count'] = question_wrong_count[question_id]
        
        # 添加完整的题目信息
        if question_id in questions_dict:
            question = questions_dict[question_id]
            record['options'] = question.get('options', [])
            record['full_content'] = question.get('content', record['question_content'])
            record['number'] = question.get('number')
        # 添加是否重点
        important_set = user_data['users'][user_id].get('important_questions', set())
        record['is_important'] = question_id in important_set
    
    questions_by_type = {
        1: [],
        2: [],
        3: []
    }
    
    for record in wrong_records:
        questions_by_type[record['type']].append(record)
    
    for q_type in questions_by_type:
        if sort_by == 'timestamp':
            questions_by_type[q_type].sort(key=lambda x: x['timestamp'], reverse=True)
        elif sort_by == 'count':
            questions_by_type[q_type].sort(key=lambda x: x['wrong_count'], reverse=True)
        elif sort_by == 'id':
            questions_by_type[q_type].sort(key=lambda x: x['question_id'])
    
    return jsonify({
        'single_choice': questions_by_type[1],
        'multi_choice': questions_by_type[2],
        'true_false': questions_by_type[3]
    })

@app.route('/get_question_bank', methods=['POST'])
@require_login
def get_question_bank():
    """获取全量题库数据"""
    data = request.get_json()
    type_filter = data.get('type_filter', 'all')
    status_filter = data.get('status_filter', 'all')
    sort_by = data.get('sort_by', 'id')
    # 全局默认页码
    default_page = data.get('page', 1)
    page_size = data.get('page_size', 100)  # 每页100道题
    # 各题型独立页码（未提供则使用默认）
    page_single = int(data.get('page_single', default_page))
    page_multi = int(data.get('page_multi', default_page))
    page_true_false = int(data.get('page_true_false', default_page))
    
    questions = load_questions()
    user_data, user_id = get_user_data()
    
    if not user_data or not user_id:
        return jsonify({'error': '用户数据不存在'})
    
    # 获取用户答题信息
    answered_questions = user_data['users'][user_id]['answered_questions']
    wrong_questions = user_data['users'][user_id]['wrong_questions']
    wrong_count = user_data['users'][user_id].get('wrong_count', {})
    important_set = user_data['users'][user_id].get('important_questions', set())
    
    # 获取错题记录的时间信息
    wrong_records = user_data['wrong_questions'][user_id]
    wrong_times = {}
    for record in wrong_records:
        question_id = record['question_id']
        if question_id not in wrong_times:
            wrong_times[question_id] = record['timestamp']
    
    # 处理每个题目，添加用户状态信息
    processed_questions = []
    for question in questions:
        question_id = question['id']
        is_answered = question_id in answered_questions
        is_wrong = question_id in wrong_questions
        
        # 计算做错次数
        wrong_count_num = 0
        if is_wrong:
            # 从错题记录中统计实际做错次数
            for record in wrong_records:
                if record['question_id'] == question_id:
                    wrong_count_num += 1
        
        # 获取最后做题时间
        last_answered_time = None
        if is_answered:
            if question_id in wrong_times:
                last_answered_time = wrong_times[question_id]
            else:
                # 如果没有错题记录，说明是做对的，使用当前时间作为默认值
                last_answered_time = datetime.datetime.now().isoformat()
        
        # 格式化时间显示
        if last_answered_time:
            try:
                dt = datetime.datetime.fromisoformat(last_answered_time.replace('Z', '+00:00'))
                last_answered_time = dt.strftime('%Y-%m-%d %H:%M')
            except:
                last_answered_time = last_answered_time[:16]  # 简单截取
        
        processed_question = {
            'id': question['id'],
            'number': question.get('number'),
            'type': question['type'],
            'is_answered': is_answered,
            'is_wrong': is_wrong,
            'wrong_count': wrong_count_num,
            'last_answered_time': last_answered_time,
            'is_important': question_id in important_set
        }
        
        # 应用筛选条件
        include_question = True
        
        # 题型筛选
        if type_filter != 'all' and str(question['type']) != type_filter:
            include_question = False
        
        # 状态筛选
        if status_filter == 'unanswered' and is_answered:
            include_question = False
        elif status_filter == 'correct' and (not is_answered or is_wrong):
            include_question = False
        elif status_filter == 'wrong' and not is_wrong:
            include_question = False
        elif status_filter == 'frequent_wrong' and (not is_wrong or wrong_count_num < 3):
            include_question = False
        elif status_filter == 'important' and (question_id not in important_set):
            include_question = False
        
        if include_question:
            processed_questions.append(processed_question)
    
    # 根据题型分类并分别排序
    by_type = {1: [], 2: [], 3: []}
    for q in processed_questions:
        by_type[q['type']].append(q)

    def sort_list(lst):
        if sort_by == 'id':
            lst.sort(key=lambda x: x['id'])
        elif sort_by == 'wrong_count':
            lst.sort(key=lambda x: x['wrong_count'], reverse=True)
        elif sort_by == 'last_answered':
            lst.sort(key=lambda x: (x['last_answered_time'] is None, x['last_answered_time']), reverse=True)
        return lst

    by_type[1] = sort_list(by_type[1])
    by_type[2] = sort_list(by_type[2])
    by_type[3] = sort_list(by_type[3])

    # 各题型分页
    def paginate(lst, page_num):
        total = len(lst)
        start = (page_num - 1) * page_size
        end = start + page_size
        return lst[start:end], {
            'total_count': total,
            'current_page': page_num,
            'total_pages': (total + page_size - 1) // page_size,
            'has_next': end < total,
            'has_prev': page_num > 1
        }

    single_slice, single_meta = paginate(by_type[1], page_single)
    multi_slice, multi_meta = paginate(by_type[2], page_multi)
    true_false_slice, true_false_meta = paginate(by_type[3], page_true_false)

    return jsonify({
        'single_choice': single_slice,
        'multi_choice': multi_slice,
        'true_false': true_false_slice,
        'single_pagination': single_meta,
        'multi_pagination': multi_meta,
        'true_false_pagination': true_false_meta
    })

@app.route('/get_important_bank', methods=['POST'])
@require_login
def get_important_bank():
    """获取重点题库数据（按题型独立分页）"""
    data = request.get_json() or {}
    sort_by = data.get('sort_by', 'id')
    default_page = data.get('page', 1)
    page_size = data.get('page_size', 100)
    page_single = int(data.get('page_single', default_page))
    page_multi = int(data.get('page_multi', default_page))
    page_true_false = int(data.get('page_true_false', default_page))

    questions = load_questions()
    user_data, user_id = get_user_data()
    if not user_data or not user_id:
        return jsonify({'error': '用户数据不存在'})

    answered = user_data['users'][user_id].get('answered_questions', set())
    wrong_set = user_data['users'][user_id].get('wrong_questions', set())
    important_set = user_data['users'][user_id].get('important_questions', set())
    wrong_records = user_data['wrong_questions'][user_id]

    # 统计错题次数与最后时间
    wrong_times = {}
    wrong_count_map = {}
    for record in wrong_records:
        qid = record['question_id']
        wrong_times.setdefault(qid, record['timestamp'])
        wrong_count_map[qid] = wrong_count_map.get(qid, 0) + 1

    processed = []
    for q in questions:
        if q['id'] not in important_set:
            continue
        qid = q['id']
        is_answered = qid in answered
        is_wrong = qid in wrong_set
        wrong_cnt = wrong_count_map.get(qid, 0)
        last_time = None
        if is_answered:
            last_time = wrong_times.get(qid, datetime.datetime.now().isoformat())
            try:
                dt = datetime.datetime.fromisoformat(last_time.replace('Z', '+00:00'))
                last_time = dt.strftime('%Y-%m-%d %H:%M')
            except:
                last_time = (last_time or '')[:16]
        processed.append({
            'id': qid,
            'number': q.get('number'),
            'type': q['type'],
            'is_answered': is_answered,
            'is_wrong': is_wrong,
            'wrong_count': wrong_cnt,
            'last_answered_time': last_time,
            'is_important': True
        })

    by_type = {1: [], 2: [], 3: []}
    for item in processed:
        by_type[item['type']].append(item)

    def sort_list(lst):
        if sort_by == 'id':
            lst.sort(key=lambda x: x['id'])
        elif sort_by == 'wrong_count':
            lst.sort(key=lambda x: x['wrong_count'], reverse=True)
        elif sort_by == 'last_answered':
            lst.sort(key=lambda x: (x['last_answered_time'] is None, x['last_answered_time']), reverse=True)
        return lst

    by_type[1] = sort_list(by_type[1])
    by_type[2] = sort_list(by_type[2])
    by_type[3] = sort_list(by_type[3])

    def paginate(lst, page_num):
        total = len(lst)
        start = (page_num - 1) * page_size
        end = start + page_size
        return lst[start:end], {
            'total_count': total,
            'current_page': page_num,
            'total_pages': (total + page_size - 1) // page_size,
            'has_next': end < total,
            'has_prev': page_num > 1
        }

    single_slice, single_meta = paginate(by_type[1], page_single)
    multi_slice, multi_meta = paginate(by_type[2], page_multi)
    true_false_slice, true_false_meta = paginate(by_type[3], page_true_false)

    return jsonify({
        'single_choice': single_slice,
        'multi_choice': multi_slice,
        'true_false': true_false_slice,
        'single_pagination': single_meta,
        'multi_pagination': multi_meta,
        'true_false_pagination': true_false_meta
    })

@app.route('/get_question_detail', methods=['POST'])
@require_login
def get_question_detail():
    """获取单个题目的详细信息"""
    data = request.get_json()
    question_id = data.get('question_id')
    
    if not question_id:
        return jsonify({'error': '题目ID不能为空'})
    
    questions = load_questions()
    user_data, user_id = get_user_data()
    
    if not user_data or not user_id:
        return jsonify({'error': '用户数据不存在'})
    
    # 统一ID类型后查找题目（兼容字符串/数字）
    question = next((q for q in questions if str(q['id']) == str(question_id)), None)
    if not question:
        return jsonify({'error': '题目不存在'})
    
    # 获取用户答题信息
    answered_questions = user_data['users'][user_id]['answered_questions']
    wrong_questions = user_data['users'][user_id]['wrong_questions']
    
    # 获取错题记录的时间信息
    wrong_records = user_data['wrong_questions'][user_id]
    wrong_times = {}
    for record in wrong_records:
        if record['question_id'] == question_id:
            wrong_times[question_id] = record['timestamp']
    
    # 计算做错次数
    wrong_count_num = 0
    for record in wrong_records:
        if record['question_id'] == question_id:
            wrong_count_num += 1
    
    # 获取最后做题时间
    last_answered_time = None
    if question_id in answered_questions:
        if question_id in wrong_times:
            last_answered_time = wrong_times[question_id]
        else:
            last_answered_time = datetime.datetime.now().isoformat()
        
        # 格式化时间显示
        if last_answered_time:
            try:
                dt = datetime.datetime.fromisoformat(last_answered_time.replace('Z', '+00:00'))
                last_answered_time = dt.strftime('%Y-%m-%d %H:%M')
            except:
                last_answered_time = last_answered_time[:16]
    
    # 构建题目详情
    question_detail = {
        'id': question['id'],
        'number': question.get('number'),
        'content': question['content'],
        'type': question['type'],
        'options': question['options'],
        'correct_answer': question['correct_answer'],
        'analysis': question.get('analysis', ''),
        'is_answered': question_id in answered_questions,
        'is_wrong': question_id in wrong_questions,
        'wrong_count': wrong_count_num,
        'last_answered_time': last_answered_time
    }
    # 在非考试场景返回重点题标志
    important_set = user_data['users'][user_id].get('important_questions', set())
    question_detail['is_important'] = question['id'] in important_set
    
    return jsonify({'success': True, 'question': question_detail})

@app.route('/toggle_important', methods=['POST'])
@require_login
def toggle_important():
    """标记/取消标记重点题"""
    data = request.get_json()
    question_id = data.get('question_id')
    mark = bool(data.get('mark', True))
    
    if not question_id:
        return jsonify({'success': False, 'message': '题目ID不能为空'})
    
    user_data, user_id = get_user_data()
    if not user_data or not user_id:
        return jsonify({'success': False, 'message': '用户数据不存在'})
    
    if 'important_questions' not in user_data['users'][user_id]:
        user_data['users'][user_id]['important_questions'] = set()
    
    if mark:
        user_data['users'][user_id]['important_questions'].add(question_id)
    else:
        user_data['users'][user_id]['important_questions'].discard(question_id)
    
    save_user_data(user_data)
    return jsonify({'success': True, 'is_important': mark})

@app.route('/get_user_stats', methods=['POST'])
@require_login
def get_user_stats():
    """获取用户统计数据"""
    user_data, user_id = get_user_data()
    
    if not user_data or not user_id:
        return jsonify({'success': False, 'message': '用户数据不存在'})
    
    # 加载题库数据
    questions = load_questions()
    total_questions = len(questions)
    
    # 计算统计数据
    answered_count = len(user_data['users'][user_id]['answered_questions'])
    wrong_count = len(user_data['users'][user_id]['wrong_questions'])
    unanswered_count = total_questions - answered_count
    
    # 获取考试记录数量
    exam_count = len(user_data['exam_records'][user_id])
    
    # 计算平均分数
    avg_score = 0
    if exam_count > 0:
        total_score = sum(record.get('total_score', 0) for record in user_data['exam_records'][user_id] if record.get('status') == 'completed')
        avg_score = round(total_score / exam_count, 1)
    
    stats = {
        'total_questions': total_questions,
        'answered_count': answered_count,
        'unanswered_count': unanswered_count,
        'wrong_count': wrong_count,
        'exam_count': exam_count,
        'avg_score': avg_score
    }
    
    return jsonify({'success': True, 'stats': stats})

@app.route('/get_exam_records', methods=['POST'])
@require_login
def get_exam_records():
    """获取考试记录"""
    user_data, user_id = get_user_data()
    
    if not user_data or not user_id:
        return jsonify({'success': False, 'message': '用户数据不存在'})
    
    data = request.get_json() or {}
    try:
        page = int(data.get('page', 1))
    except Exception:
        page = 1
    try:
        page_size = int(data.get('page_size', 10))
    except Exception:
        page_size = 10
    
    # 对超时但仍为进行中的考试进行自动结算
    now = datetime.datetime.now()
    updated = False
    for record in user_data['exam_records'][user_id]:
        if record.get('status') == 'ongoing':
            duration = record.get('duration_seconds', 3600)
            elapsed = (now - _parse_iso(record['start_time'])).total_seconds()
            if elapsed >= duration:
                _finalize_exam_from_record(user_data, user_id, record)
                updated = True
    if updated:
        # 保存后直接继续使用内存对象的 exam_records 即可
        pass
    
    # 获取最近的考试记录，按开始时间倒序排列
    exam_records = sorted(
        user_data['exam_records'][user_id],
        key=lambda x: x.get('start_time', ''),
        reverse=True
    )
    total = len(exam_records)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
    page = max(1, min(page, max(total_pages, 1)))
    start = (page - 1) * page_size
    end = start + page_size
    records_slice = exam_records[start:end]

    return jsonify({
        'success': True,
        'records': records_slice,
        'pagination': {
            'current_page': page,
            'page_size': page_size,
            'total_count': total,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
    })

@app.route('/get_exam_detail', methods=['POST'])
@require_login
def get_exam_detail():
    """获取考试详情"""
    data = request.get_json()
    exam_id = data.get('exam_id')
    
    if not exam_id:
        return jsonify({'success': False, 'message': '考试ID不能为空'})
    
    user_data, user_id = get_user_data()
    
    if not user_data or not user_id:
        return jsonify({'success': False, 'message': '用户数据不存在'})
    
    # 查找指定的考试记录
    exam_record = None
    for record in user_data['exam_records'][user_id]:
        if record['exam_id'] == exam_id:
            exam_record = record
            break
    
    if not exam_record:
        return jsonify({'success': False, 'message': '考试记录不存在'})
    
    # 加载题库数据以获取完整的题目信息
    questions = load_questions()
    question_map = {q['id']: q for q in questions}
    
    # 构建考试详情
    exam_detail = {
        'exam_id': exam_record['exam_id'],
        'start_time': exam_record['start_time'],
        'end_time': exam_record.get('end_time'),
        'status': exam_record['status'],
        'total_score': exam_record.get('total_score', 0),
        'questions': []
    }
    
    # 添加题目详情
    important_set = user_data['users'][user_id].get('important_questions', set())
    for question in exam_record['questions']:
        question_id = question['id']
        full_question = question_map.get(question_id, question)
        
        exam_detail['questions'].append({
            'id': question_id,
            'number': full_question.get('number', question.get('number')),
            'content': full_question.get('content', question.get('content', '')),
            'type': question['type'],
            'options': full_question.get('options', []),
            'correct_answer': question['correct_answer'],
            'score': question['score'],
            'analysis': full_question.get('analysis', ''),
            'is_important': question_id in important_set
        })
    
    # 添加错题信息（如果有）
    if exam_record.get('wrong_answers'):
        exam_detail['wrong_answers'] = exam_record['wrong_answers']
    # 若进行中的考试带有已保存答案，也返回，便于前端显示“继续作答”
    if exam_record.get('status') == 'ongoing':
        exam_detail['answers'] = exam_record.get('answers', {})
    
    return jsonify({'success': True, 'exam_detail': exam_detail})

@app.route('/api/backup', methods=['GET'])
def api_backup():
    """API备份接口（管理员专用）"""
    # 简单的安全检查：检查请求头中的特殊标识
    backup_key = request.headers.get('X-Backup-Key')
    if backup_key != 'question_bank_backup_2025':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # 读取用户数据
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
        else:
            user_data = {
                'users': {},
                'user_profiles': {},
                'wrong_questions': {},
                'exam_records': {}
            }
        
        # 添加备份元数据
        backup_data = {
            'backup_time': datetime.datetime.now().isoformat(),
            'backup_version': '1.0',
            'data': user_data
        }
        
        return jsonify(backup_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile')
@require_login
def profile():
    """用户资料页面"""
    user_data, user_id = get_user_data()
    if user_data and user_id:
        profile_info = user_data['user_profiles'][user_id]
        return render_template('profile.html', profile=profile_info, user_id=user_id)
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port) 