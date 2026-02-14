#!/usr/bin/env python3
"""
Multi-Language Coding Contest Platform
Flask-based offline coding contest system for college labs.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import hashlib
import uuid
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime, timedelta
import time
from threading import Thread, Lock
from queue import Queue, PriorityQueue
import itertools
import json
from src.judge import judge_submission
from src.multi_judge import judge_multiple_tests
import config
from src.test_case_parser import parse_test_case_file, import_test_cases_to_db, redistribute_points
from src.export_utils import export_submissions_csv, export_code_zip, export_leaderboard_csv

# ============================================================================
# Simple Cache for Performance
# ============================================================================

class SimpleCache:
    """Simple in-memory cache with TTL."""
    def __init__(self):
        self.cache = {}
        self.lock = Lock()
    
    def get(self, key):
        with self.lock:
            if key in self.cache:
                value, expiry = self.cache[key]
                if time.time() < expiry:
                    return value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key, value, ttl=60):
        with self.lock:
            self.cache[key] = (value, time.time() + ttl)
    
    def clear(self):
        with self.lock:
            self.cache.clear()

# Global cache instance
cache = SimpleCache()

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Initialize SocketIO for real-time updates - Optimized
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='threading',
    # Performance optimizations
    ping_timeout=60,          # Longer timeout to reduce pings
    ping_interval=25,         # Less frequent pings
    max_http_buffer_size=1e6, # 1MB buffer
    engineio_logger=False,    # Disable verbose logging
    logger=False,             # Disable verbose logging
    # Connection management
    always_connect=False,     # Don't force reconnection
    transports=['websocket', 'polling']  # Prefer websocket
)

# Allowed programming languages
ALLOWED_LANGUAGES = ['python', 'c', 'cpp', 'java']

# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging():
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'server.log')

    handler = RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=3)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.INFO)
    werkzeug_logger.addHandler(handler)

setup_logging()

# ============================================================================
# Database Helper Functions
# ============================================================================

def get_db():
    """Get database connection with optimizations."""
    conn = sqlite3.connect(config.DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        settings = getattr(config, 'DB_PRAGMA_SETTINGS', {})
        conn.execute(f"PRAGMA journal_mode={settings.get('journal_mode', 'WAL')};")
        conn.execute(f"PRAGMA synchronous={settings.get('synchronous', 'NORMAL')};")
        conn.execute(f"PRAGMA busy_timeout={settings.get('busy_timeout', 10000)};")
        if 'cache_size' in settings:
            conn.execute(f"PRAGMA cache_size={settings['cache_size']};")
        if 'temp_store' in settings:
            conn.execute(f"PRAGMA temp_store={settings['temp_store']};")
        # Memory-mapped I/O for faster reads (keep existing default)
        conn.execute('PRAGMA mmap_size=268435456;')  # 256MB
    except sqlite3.Error:
        pass
    return conn

def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def parse_starter_code(raw_code):
    """Parse starter code mapping stored as JSON or raw string."""
    if not raw_code:
        return {}
    try:
        data = json.loads(raw_code)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {'default': raw_code}

def get_problem_code_map(problem_id, code_type='starter'):
    """Fetch code from problem_code table for all languages.
    
    Args:
        problem_id: The problem ID
        code_type: 'starter' or 'solution'
    
    Returns:
        dict: {language: code} mapping
    """
    conn = get_db()
    field = 'starter_code' if code_type == 'starter' else 'solution_code'
    
    rows = conn.execute(f'''
        SELECT language, {field}
        FROM problem_code
        WHERE problem_id = ?
    ''', (problem_id,)).fetchall()
    
    conn.close()
    
    code_map = {}
    for row in rows:
        if row[1]:  # If code exists
            code_map[row[0]] = row[1]
    
    return code_map

def default_starter_map(problem_mode='stdin', function_name='solve'):
    """Server-side default starter code (mirrors front-end defaults)."""
    is_function = problem_mode == 'function'
    return {
        'python': (
            f"def {function_name}(data):\n    # data will contain the input in the format described\n    return \"\""
            if is_function else
            "import sys\n\n\ndef main():\n    data = sys.stdin.read().strip()\n    # Write your logic here\n    # print(result)\n\nif __name__ == '__main__':\n    main()\n"
        ),
        'cpp': (
            f'std::string {function_name}(const std::string& data) {{\n    // return the answer\n    return \"\";\n}}'
            if is_function else
            "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n\n    // Write your logic here\n\n    return 0;\n}\n"
        ),
        'c': (
            f"#include <stdlib.h>\n#include <string.h>\n\nchar* {function_name}(const char* data) {{\n    // return result (malloc a string)\n    char* out = (char*)malloc(1);\n    out[0] = '\\0';\n    return out;\n}}"
            if is_function else
            "#include <stdio.h>\n\nint main() {\n    // Write your logic here\n    return 0;\n}\n"
        ),
        'java': (
            f"class Solution {{\n    public String {function_name}(String data) {{\n        // return the answer\n        return \"\";\n    }}\n}}"
            if is_function else
            "import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        // Write your logic here\n    }\n}\n"
        ),
        'default': ''
    }

def get_setting(conn, key, default=''):
    row = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
    if not row:
        # Persist default for future use
        conn.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, default))
        conn.commit()
        return default
    return row['value']

# ============================================================================
# Authentication Decorators
# ============================================================================

from functools import wraps

@app.before_request
def check_single_session():
    """Verify that the current session is the active one for this user."""
    # Skip check for static files, login, logout and help
    if not request.endpoint or request.path.startswith('/static') or request.endpoint in ('login', 'logout', 'help_page', 'index'):
        return
        
    if 'user_id' in session:
        user_id = session['user_id']
        current_token = session.get('session_token')
        
        # Admins are exempt from single-session rule
        if session.get('role') == 'admin':
            return
            
        conn = get_db()
        user = conn.execute('SELECT session_token FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        
        if user and user['session_token'] != current_token:
            # Token mismatch - someone else logged in
            session.clear()
            msg = 'Your account was logged in from another device. Please login again.'
            if request.is_json:
                return jsonify({'error': msg}), 401
            return redirect(url_for('login', error=msg))

def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def set_setting(conn, key, value):
    conn.execute('INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value',
                 (key, value))

def log_admin_action(action, details=None):
    """Log admin action to database for audit trail."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return
    
    try:
        conn = get_db()
        ip_address = request.remote_addr if request else None
        conn.execute('''
            INSERT INTO admin_logs (admin_id, action, details, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], action, details, ip_address))
        conn.commit()
        conn.close()
        app.logger.info(f"Admin action: {action} by user {session.get('username')} - {details}")
        
        # Real-time WebSocket update for Admin Dashboard
        try:
            socketio.emit('admin_log_append', {
                'admin': session.get('username'),
                'action': action,
                'details': details or '-',
                'created_at': datetime.utcnow().isoformat() + 'Z'
            }, room='admin')
        except: pass
    except Exception as e:
        app.logger.error(f"Failed to log admin action: {e}")

# ============================================================================
# Submission Queue System
# ============================================================================

# Priority-aware queue for deadline bursts
if getattr(config, 'PRIORITY_QUEUE_ENABLED', False):
    submission_queue = PriorityQueue()
    _seq_counter = itertools.count()
    def enqueue_task(task, priority=1):
        submission_queue.put((priority, next(_seq_counter), task))
else:
    submission_queue = Queue()
    def enqueue_task(task, priority=1):
        submission_queue.put(task)

submission_results = {}  # Store results by submission ID
results_lock = Lock()
threads_started = False
threads_lock = Lock()

def start_background_services():
    """Start judge workers, watchdog, and timer thread exactly once."""
    global threads_started
    with threads_lock:
        if threads_started:
            return
        # Start background judge workers
        worker_count = getattr(config, 'NUM_JUDGE_WORKERS', getattr(config, 'MAX_CONCURRENT_JUDGES', 10))
        app.logger.info(f"Starting {worker_count} judge worker threads...")
        for i in range(worker_count):
            Thread(target=judge_worker, daemon=True, name=f"JudgeWorker-{i}").start()
        
        # Start watchdog thread
        app.logger.info("Starting watchdog worker thread...")
        Thread(target=watchdog_worker, daemon=True, name="WatchdogWorker").start()
        
        # Start timer sync thread
        app.logger.info("Starting timer sync thread...")
        Thread(target=timer_sync_thread, daemon=True, name="TimerSyncWorker").start()
        
        threads_started = True

def judge_worker():
    """Background worker to process submissions from queue."""
    while True:
        raw = submission_queue.get()
        if isinstance(raw, tuple) and len(raw) == 3:
            _, _, task = raw  # Unpack priority queue item
        else:
            task = raw
        if task is None:
            break
        
        submission_id = task['submission_id']
        app.logger.info(f"Judging submission {submission_id} (Problem: {task.get('problem_id')}, User: {task.get('username')})")
        
        try:
            # Get all test cases for this problem
            conn = get_db()
            test_cases_raw = conn.execute('''
                SELECT input, expected_output, is_sample, points, test_order
                FROM test_cases
                WHERE problem_id = ?
                ORDER BY test_order
            ''', (task['problem_id'],)).fetchall()
            
            # If no test cases exist, fall back to legacy single test
            if not test_cases_raw:
                problem = conn.execute('''
                    SELECT test_input, expected_output
                    FROM problems
                    WHERE id = ?
                ''', (task['problem_id'],)).fetchone()
                conn.close()
                
                if problem and problem['test_input']:
                    # Use legacy single test case
                    test_cases = [{
                        'input': problem['test_input'],
                        'expected_output': problem['expected_output'],
                        'is_sample': False,
                        'points': 100
                    }]
                else:
                    # No tests at all - mark as error
                    conn = get_db()
                    conn.execute('''
                        UPDATE submissions 
                        SET output = ?, verdict = ?, judging_status = 'completed',
                            points_awarded = 0, tests_passed = 0, tests_total = 0
                        WHERE id = ?
                    ''', ('ERROR: No test cases configured for this problem', 'CE', submission_id))
                    conn.commit()
                    conn.close()
                    
                    with results_lock:
                        submission_results[submission_id] = {
                            'verdict': 'CE',
                            'output': 'ERROR: No test cases configured for this problem',
                            'message': 'Configuration Error',
                            'user_id': task.get('user_id')
                        }
                    continue
            else:
                conn.close()
                # Convert to list of dicts
                test_cases = [{
                    'input': tc[0],
                    'expected_output': tc[1],
                    'is_sample': bool(tc[2]),
                    'points': tc[3]
                } for tc in test_cases_raw]
            
            # Execute multi-test judging
            result = judge_multiple_tests(
                task['language'],
                task['code'],
                test_cases,
                mode=task.get('problem_mode', 'stdin'),
                function_name=task.get('function_name', 'solve')
            )
            
            # Format output with test results
            output_lines = [result['message']]
            for test_result in result['test_results']:
                if test_result['is_sample'] or test_result['verdict'] != 'AC':
                    output_lines.append(f"Test {test_result['test_num']}: {test_result['verdict']}")
                    if test_result['verdict'] != 'AC' and test_result['output']:
                        output_lines.append(f"Output: {test_result['output'][:200]}")
            
            output = '\n'.join(output_lines)
            verdict = result['verdict']
            
            # Save to database
            conn = get_db()
            try:
                conn.execute('''
                    UPDATE submissions 
                    SET output = ?, verdict = ?, judging_status = 'completed',
                        points_awarded = ?, tests_passed = ?, tests_total = ?
                    WHERE id = ?
                ''', (
                    output,
                    verdict,
                    result.get('points', 0),
                    result.get('total_passed', 0),
                    result.get('total_tests', 0),
                    submission_id
                ))
            except sqlite3.OperationalError:
                conn.execute('''
                    UPDATE submissions 
                    SET output = ?, verdict = ?, judging_status = 'completed'
                    WHERE id = ?
                ''', (output, verdict, submission_id))
            conn.commit()
            conn.close()
            app.logger.info(f"Judging completed for submission {submission_id} (Verdict: {verdict})")
            
            # Store result
            with results_lock:
                submission_results[submission_id] = {
                    'verdict': verdict,
                    'output': output,
                    'message': result['message'],
                    'total_passed': result['total_passed'],
                    'total_tests': result['total_tests'],
                    'user_id': task.get('user_id')
                }
            
            # Emit real-time update to user
            try:
                user_id = task.get('user_id')
                if user_id:
                    payload = {
                        'submission_id': submission_id,
                        'problem_id': task['problem_id'],
                        'problem_title': task.get('problem_title', 'Unknown Problem'),
                        'verdict': verdict,
                        'message': result['message'],
                        'total_passed': result['total_passed'],
                        'total_tests': result['total_tests'],
                        'points': result.get('points', 0),
                        'max_points': task.get('total_marks', 100),
                        'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'username': task.get('username', 'Anonymous'),
                        'language': task.get('language', 'unknown')
                    }
                    # Emit to specific user only (reduces broadcast load)
                    socketio.emit('submission_update', payload, room=f'user_{user_id}', namespace='/')
                    
                    # Only notify admins if they're in the admin room (lazy loading)
                    socketio.emit('admin_submission_update', payload, room='admin', namespace='/')
                
                # Emit leaderboard update only to leaderboard room (not broadcast)
                # This prevents unnecessary updates to users not viewing leaderboard
                socketio.emit('leaderboard_update', {
                    'user_id': user_id,
                    'problem_id': task['problem_id']
                }, room='leaderboard', namespace='/')
            except Exception as emit_error:
                app.logger.error(f'SocketIO emit error: {emit_error}')
                
        except Exception as e:
            # Handle errors
            try:
                conn = get_db()
                try:
                    conn.execute('''
                        UPDATE submissions 
                        SET output = ?, verdict = ?, judging_status = 'completed',
                            points_awarded = 0, tests_passed = 0, tests_total = 0
                        WHERE id = ?
                    ''', (str(e), 'RE', submission_id))
                except sqlite3.OperationalError:
                    conn.execute('''
                        UPDATE submissions 
                        SET output = ?, verdict = ?, judging_status = 'completed'
                        WHERE id = ?
                    ''', (str(e), 'RE', submission_id))
                conn.commit()
                conn.close()
            except Exception:
                pass
            with results_lock:
                submission_results[submission_id] = {
                    'verdict': 'RE',
                    'output': str(e),
                    'message': 'System error during judging',
                    'user_id': task.get('user_id')
                }
        
        submission_queue.task_done()

# Judge workers are started in the __main__ block to ensure clean startup

# Watchdog thread to detect stuck submissions
def watchdog_worker():
    """Monitor for submissions stuck in PENDING status."""
    interval = getattr(config, 'WATCHDOG_INTERVAL', 60)
    timeout_seconds = getattr(config, 'STUCK_SUBMISSION_TIMEOUT', 300)
    while True:
        try:
            time.sleep(interval)
            
            conn = get_db()
            cutoff = (datetime.now() - timedelta(seconds=timeout_seconds)).strftime('%Y-%m-%d %H:%M:%S')
            
            stuck = conn.execute('''
                SELECT id, submitted_at FROM submissions
                WHERE verdict = 'PENDING' AND submitted_at < ?
            ''', (cutoff,)).fetchall()
            
            if stuck:
                app.logger.warning(f"Watchdog: Found {len(stuck)} stuck submissions")
                
                # Mark as system error and allow resubmission
                for sub in stuck:
                    conn.execute('''
                        UPDATE submissions
                        SET verdict = 'RE',
                            output = 'System Error: Judging timed out. Please contact admin.',
                            judging_status = 'completed',
                            points_awarded = 0,
                            tests_passed = 0,
                            tests_total = 0
                        WHERE id = ?
                    ''', (sub['id'],))
                    app.logger.warning(f"Watchdog: Recovered submission {sub['id']}")
                
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            app.logger.error(f"Watchdog error: {e}")

# Watchdog thread is started in the __main__ block

def get_verdict_message(verdict):
    """Get user-friendly message for verdict."""
    messages = {
        'AC': 'Accepted! Your solution is correct.',
        'PC': 'Partial Credit. Some test cases passed.',
        'WA': 'Wrong Answer. Your output does not match expected output.',
        'CE': 'Compilation Error. Please check your syntax.',
        'RE': 'Runtime Error. Your program crashed during execution.',
        'TLE': 'Time Limit Exceeded. Your program took too long to execute.'
    }
    return messages.get(verdict, 'Unknown verdict')

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    if request.path.startswith('/api/') or request.is_json:
        return jsonify({'error': 'Resource not found'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    app.logger.error(f'Internal error: {error}')
    if request.path.startswith('/api/') or request.is_json:
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions."""
    app.logger.error(f'Unhandled exception: {e}', exc_info=True)
    
    # Pass through HTTP errors
    if isinstance(e, Exception) and hasattr(e, 'code'):
        return e
    
    # Handle non-HTTP exceptions
    if request.path.startswith('/api/') or request.is_json:
        return jsonify({'error': 'An unexpected error occurred'}), 500
    return render_template('500.html'), 500

# ============================================================================
# Authentication Routes
# ============================================================================

@app.route('/')
def index():
    """Redirect to login or dashboard based on session."""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, hash_password(password))
        ).fetchone()
        
        if user:
            # Single Session Logic: Generate unique token
            session_token = str(uuid.uuid4())
            conn.execute('UPDATE users SET session_token = ? WHERE id = ?', (session_token, user['id']))
            conn.commit()
            conn.close()

            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['session_token'] = session_token
            
            if user['role'] == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('dashboard'))
        else:
            conn.close()
            error = 'Invalid credentials'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    return redirect(url_for('login'))

# ============================================================================
# Student Routes
# ============================================================================

@app.route('/dashboard')
def dashboard():
    """Student dashboard showing active contests."""
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    conn = get_db()
    leaderboard_enabled = get_setting(conn, 'leaderboard_enabled', '1') == '1'
    show_scores_to_students = get_setting(conn, 'show_scores_to_students', '1') == '1'
    show_difficulty_to_students = get_setting(conn, 'show_difficulty_to_students', '1') == '1'
    
    # Get active/upcoming contests
    contests = conn.execute('''
        SELECT id, title, description, start_time, end_time, is_active
        FROM contests
        WHERE is_active = 1
        ORDER BY start_time ASC
    ''').fetchall()
    
    # Get user's recent submissions
    submissions = conn.execute('''
        SELECT s.*, p.title as problem_title
        FROM submissions s
        JOIN problems p ON s.problem_id = p.id
        WHERE s.user_id = ?
        ORDER BY s.submitted_at DESC
        LIMIT 10
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    # Process contests to add status
    now = datetime.now()
    contests_list = []
    for c in contests:
        start = datetime.fromisoformat(c['start_time'])
        end = datetime.fromisoformat(c['end_time'])
        if now < start:
            status = 'Upcoming'
            status_class = 'info'
        elif now > end:
            status = 'Ended'
            status_class = 'secondary'
        else:
            status = 'Running'
            status_class = 'success'
            
        contests_list.append({
            'id': c['id'],
            'title': c['title'],
            'description': c['description'],
            'start_time': c['start_time'],
            'end_time': c['end_time'],
            'status': status,
            'status_class': status_class
        })
    
    return render_template('dashboard.html', contests=contests_list, submissions=submissions, leaderboard_enabled=leaderboard_enabled, show_scores_to_students=show_scores_to_students, show_difficulty_to_students=show_difficulty_to_students)

@app.route('/help')
def help_page():
    """Help and reference page for all users."""
    return render_template('help.html')

@app.route('/contest/<int:contest_id>')
def view_contest(contest_id):
    """View problems for a specific contest."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db()
    leaderboard_enabled = get_setting(conn, 'leaderboard_enabled', '1') == '1'
    show_scores_to_students = get_setting(conn, 'show_scores_to_students', '1') == '1'
    show_difficulty_to_students = get_setting(conn, 'show_difficulty_to_students', '1') == '1'
    contest = conn.execute('SELECT * FROM contests WHERE id = ?', (contest_id,)).fetchone()
    
    if not contest:
        conn.close()
        return redirect(url_for('dashboard'))
    if session.get('role') != 'admin' and not contest['is_active']:
        conn.close()
        return redirect(url_for('dashboard'))
        
    # Check if contest is accessible
    now = datetime.now()
    start_time = datetime.fromisoformat(contest['start_time'])
    
    # Allow access if running or ended (for practice), or if admin
    # Strict mode: Only if running?
    # Let's allow viewing if it has started.
    if now < start_time and session.get('role') != 'admin':
        flash('Contest has not started yet', 'error')
        conn.close()
        return redirect(url_for('dashboard'))
        
    first_problem = conn.execute('''
        SELECT id FROM problems 
        WHERE contest_id = ? AND enabled = 1 
        ORDER BY id LIMIT 1
    ''', (contest_id,)).fetchone()
    
    conn.close()
    
    if first_problem:
        return redirect(url_for('problem', problem_id=first_problem['id']))
    else:
        flash('No problems available for this contest yet.', 'info')
        return redirect(url_for('dashboard'))

@app.route('/contest/<int:contest_id>/spa')
def contest_spa(contest_id):
    """Single-page application for contest problems"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    contest = conn.execute('SELECT * FROM contests WHERE id = ?', (contest_id,)).fetchone()
    conn.close()
    
    if not contest:
        return redirect(url_for('dashboard'))
    
    return render_template('contest_spa.html', contest=contest)


@app.route('/api/student/contest/<int:contest_id>/problems')
def get_student_contest_problems(contest_id):
    """API endpoint for SPA to fetch problem list."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    
    # Check if contest is active and accessible (unless admin)
    if session.get('role') != 'admin':
        contest = conn.execute('SELECT is_active, start_time FROM contests WHERE id = ?', (contest_id,)).fetchone()
        if not contest:
            conn.close()
            return jsonify({'error': 'Contest not found'}), 404
            
        if not contest['is_active']:
             conn.close()
             return jsonify({'error': 'Contest is not active'}), 403
        
        if datetime.now() < datetime.fromisoformat(contest['start_time']):
             conn.close()
             return jsonify({'error': 'Contest has not started'}), 403

    # Get problems
    problems = conn.execute('''
        SELECT id, title, problem_type 
        FROM problems 
        WHERE contest_id = ? AND enabled = 1
        ORDER BY id
    ''', (contest_id,)).fetchall()
    
    # Get user status for each problem
    result = []
    for p in problems:
        # Check verdict
        status = conn.execute('''
            SELECT verdict 
            FROM submissions 
            WHERE user_id = ? AND problem_id = ?
            ORDER BY 
                CASE WHEN verdict = 'AC' THEN 1 ELSE 2 END,
                submitted_at DESC
            LIMIT 1
        ''', (session['user_id'], p['id'])).fetchone()
        
        solved = False
        attempted = False
        
        if status:
            attempted = True
            if status['verdict'] == 'AC':
                solved = True
                
        result.append({
            'id': p['id'],
            'title': p['title'],
            'problem_type': p['problem_type'],
            'solved': solved,
            'attempted': attempted
        })
        
    conn.close()
    return jsonify(result)

@app.route('/api/proctor_log', methods=['POST'])
def proctor_log():
    """Log proctoring events"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    event = data.get('event')
    timestamp = data.get('timestamp')
    
    # Log to admin_logs table
    conn = get_db()
    conn.execute('''
        INSERT INTO admin_logs (admin_id, action, details, ip_address)
        VALUES (?, ?, ?, ?)
    ''', (session['user_id'], 'PROCTOR_EVENT', f"{event} at {timestamp}", request.remote_addr))
    conn.commit()
    conn.close()
    
    # WebSocket update for Admin
    try:
        socketio.emit('proctor_log_append', {
            'admin': session.get('username'),
            'action': event,
            'details': f"{event} at {timestamp}",
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }, room='admin')
    except: pass
    
    return jsonify({'success': True})

@app.route('/problem/<int:problem_id>')
def problem(problem_id):
    """Display problem details and code editor."""
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    conn = get_db()
    leaderboard_enabled = get_setting(conn, 'leaderboard_enabled', '1') == '1'
    show_scores_to_students = get_setting(conn, 'show_scores_to_students', '1') == '1'
    show_difficulty_to_students = get_setting(conn, 'show_difficulty_to_students', '1') == '1'
    problem = conn.execute('SELECT * FROM problems WHERE id = ?', (problem_id,)).fetchone()
    
    if not problem:
        conn.close()
        return "Problem not found", 404
    
    # Enforce contest window for students (view-only gate) to prevent early access
    if session.get('role') != 'admin' and problem['contest_id']:
        contest = conn.execute('SELECT start_time, end_time, is_active FROM contests WHERE id = ?', (problem['contest_id'],)).fetchone()
        if contest:
            if not contest['is_active']:
                conn.close()
                flash('Contest is not active', 'error')
                return redirect(url_for('dashboard'))
            start_time = datetime.fromisoformat(contest['start_time'].replace('T', ' '))
            end_time = datetime.fromisoformat(contest['end_time'].replace('T', ' '))
            now = datetime.now()
            if now < start_time:
                conn.close()
                flash('Contest has not started yet', 'error')
                return redirect(url_for('dashboard'))
            if now > end_time + timedelta(seconds=getattr(config, 'GRACE_PERIOD', 30)):
                conn.close()
                flash('Contest has ended', 'error')
                return redirect(url_for('dashboard'))
    
    # Get user's previous submissions for this problem
    submissions = conn.execute('''
        SELECT * FROM submissions
        WHERE user_id = ? AND problem_id = ?
        ORDER BY submitted_at DESC
    ''', (session['user_id'], problem_id)).fetchall()
    
    # Get sample test cases (visible to students)
    sample_tests = conn.execute('''
        SELECT input, expected_output, test_order
        FROM test_cases
        WHERE problem_id = ? AND is_sample = 1
        ORDER BY test_order
    ''', (problem_id,)).fetchall()
    
    # Get all problems in the same contest for navigation
    contest_problems = []
    if problem and problem['contest_id']:
        contest_problems = conn.execute('''
            SELECT p.id, p.title, p.problem_type,
                   (SELECT COUNT(*) FROM submissions s 
                    WHERE s.problem_id = p.id AND s.user_id = ? AND s.verdict = 'AC') as solved,
                   (SELECT COUNT(*) FROM submissions s 
                    WHERE s.problem_id = p.id AND s.user_id = ?) as attempted
            FROM problems p
            WHERE p.contest_id = ? AND p.enabled = 1
            ORDER BY p.id
        ''', (session['user_id'], session['user_id'], problem['contest_id'])).fetchall()
    
    # Get latest submission result for this problem
    latest_submission = submissions[0] if submissions else None
    
    conn.close()
    
    # Try to get starter code from problem_code table first
    starter_map = get_problem_code_map(problem_id, 'starter')
    
    # Fallback to legacy starter_code field if problem_code table is empty
    if not starter_map:
        starter_map = parse_starter_code(problem['starter_code']) if 'starter_code' in problem.keys() else {}
    
    # Final fallback to default templates
    if not starter_map:
        starter_map = default_starter_map(problem.get('problem_mode') or 'stdin', problem.get('function_name') or 'solve')
    
    return render_template(
        'problem.html',
        problem=problem,
        submissions=submissions,
        sample_tests=sample_tests,
        starter_code_map=json.dumps(starter_map),
        leaderboard_enabled=leaderboard_enabled,
        contest_problems=contest_problems,
        latest_submission=latest_submission,
        show_scores_to_students=show_scores_to_students,
        show_difficulty_to_students=show_difficulty_to_students
    )

@app.route('/run/<int:problem_id>', methods=['POST'])
def run(problem_id):
    """Run code with sample input (doesn't save submission)."""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Rate limiting for run
        if 'last_run_time' in session:
            elapsed = time.time() - session['last_run_time']
            if elapsed < config.RUN_COOLDOWN:
                return jsonify({
                    'error': f'Please wait {config.RUN_COOLDOWN - int(elapsed)} seconds before running again'
                }), 429
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        language = data.get('language')
        code = data.get('code')
        
        # Validate language
        if not language or language not in ALLOWED_LANGUAGES:
            return jsonify({
                'error': f'Invalid language. Allowed languages: {", ".join(ALLOWED_LANGUAGES)}'
            }), 400
        
        if not code or not code.strip():
            return jsonify({'error': 'Code cannot be empty'}), 400
        
        # Code size limit
        if len(code) > config.MAX_CODE_SIZE:
            return jsonify({
                'error': f'Code exceeds maximum size limit ({config.MAX_CODE_SIZE} bytes)'
            }), 400
        
        # Update last run time
        session['last_run_time'] = time.time()
        
        # Get problem details and sample test cases
        conn = get_db()
        try:
            problem = conn.execute('''
                SELECT p.problem_mode, p.function_name, p.contest_id,
                       c.start_time, c.end_time, c.is_active,
                       p.sample_input, p.sample_output
                FROM problems p
                LEFT JOIN contests c ON p.contest_id = c.id
                WHERE p.id = ?
            ''', (problem_id,)).fetchone()
            
            if not problem:
                conn.close()
                return jsonify({'error': 'Problem not found'}), 404
            
            # Enforce contest window for run (students only)
            if session.get('role') != 'admin' and problem['contest_id']:
                if not problem['is_active']:
                    conn.close()
                    return jsonify({'error': 'Contest is currently inactive'}), 403
                
                start_time = datetime.fromisoformat(problem['start_time'].replace('T', ' '))
                end_time = datetime.fromisoformat(problem['end_time'].replace('T', ' '))
                now = datetime.now()
                grace_period_seconds = getattr(config, 'GRACE_PERIOD', 30)
                
                if now < start_time:
                    conn.close()
                    return jsonify({'error': f'Contest has not started yet. Starts at {start_time.strftime("%Y-%m-%d %H:%M:%S")}'}) , 403
                if now > end_time + timedelta(seconds=grace_period_seconds):
                    conn.close()
                    return jsonify({'error': f'Contest has ended. Ended at {end_time.strftime("%Y-%m-%d %H:%M:%S")}'}) , 403
            
            # Get all sample test cases (is_sample = 1)
            sample_tests_raw = conn.execute('''
                SELECT input, expected_output 
                FROM test_cases 
                WHERE problem_id = ? AND is_sample = 1
                ORDER BY test_order
            ''', (problem_id,)).fetchall()
            
            # If no sample tests in database, fall back to problem's sample_input/output
            if not sample_tests_raw:
                if problem['sample_input']:
                    # Use fallback sample from problems table
                    sample_tests = [{
                        'input': problem['sample_input'], 
                        'expected_output': problem['sample_output'],
                        'is_sample': True,
                        'points': 0
                    }]
                else:
                    conn.close()
                    return jsonify({'error': 'No sample test cases available'}), 404
            else:
                # Convert to list of dicts
                sample_tests = [{
                    'input': tc[0], 
                    'expected_output': tc[1],
                    'is_sample': True,
                    'points': 0  # Sample tests don't award points
                } for tc in sample_tests_raw]
        finally:
            conn.close()
        
        problem_mode = problem['problem_mode'] if 'problem_mode' in problem.keys() else 'stdin'
        function_name = problem['function_name'] if 'function_name' in problem.keys() else 'solve'
        
        # Run against all sample tests using multi_judge
        result = judge_multiple_tests(
            language,
            code,
            sample_tests,
            mode=problem_mode,
            function_name=function_name
        )
        
        # Format output for display
        output_lines = [result['message']]
        for test_result in result['test_results']:
            output_lines.append(f"\nSample Test {test_result['test_num']}: {test_result['verdict']}")
            if test_result['verdict'] != 'AC' and test_result['output']:
                output_lines.append(f"  Your output: {test_result['output'][:200]}")
        
        return jsonify({
            'verdict': result['verdict'],
            'output': '\n'.join(output_lines),
            'message': result['message'],
            'total_passed': result['total_passed'],
            'total_tests': result['total_tests'],
            'is_sample': True
        })
    except Exception as e:
        app.logger.error(f"Error in run route: {e}")
        return jsonify({'error': 'Internal server error. Please try again.'}), 500

@app.route('/submit/<int:problem_id>', methods=['POST'])
def submit(problem_id):
    """Handle code submission."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Allow admins to submit for testing
    # if session.get('role') != 'student': ... (removed restriction)
    
    # Rate limiting for submit
    if 'last_submit_time' in session:
        elapsed = time.time() - session['last_submit_time']
        if elapsed < config.SUBMISSION_COOLDOWN:
            return jsonify({
                'error': f'Please wait {config.SUBMISSION_COOLDOWN - int(elapsed)} seconds before submitting again'
            }), 429
    
    contest_id = None
    # Check contest time window (skip for admins)
    contest_end_time = None
    if session.get('role') != 'admin':
        conn = get_db()
        # Check which contest this problem belongs to
        problem_contest = conn.execute(
            'SELECT contest_id, enabled FROM problems WHERE id = ?', 
            (problem_id,)
        ).fetchone()
        
        if not problem_contest:
            conn.close()
            return jsonify({'error': 'Problem not found'}), 404
            
        if not problem_contest['enabled']:
             conn.close()
             return jsonify({'error': 'Problem is currently disabled'}), 403
             
        contest_id = problem_contest['contest_id']
        
        if contest_id:
            contest = conn.execute('''
                SELECT start_time, end_time, is_active
                FROM contests
                WHERE id = ?
            ''', (contest_id,)).fetchone()
            
            if contest:
                now = datetime.now()
                start_time = datetime.fromisoformat(contest['start_time'])
                end_time = datetime.fromisoformat(contest['end_time'])
                contest_end_time = end_time
                
                if now < start_time:
                    conn.close()
                    return jsonify({
                        'error': f'Contest has not started yet. Starts at {start_time.strftime("%Y-%m-%d %H:%M:%S")}'
                    }), 403
                
                # Allow submissions made within grace period after contest end
                # This ensures submissions clicked before deadline are accepted
                grace_period_seconds = getattr(config, 'GRACE_PERIOD', 30)
                if now > end_time + timedelta(seconds=grace_period_seconds):
                    conn.close()
                    return jsonify({
                        'error': f'Contest has ended. Ended at {end_time.strftime("%Y-%m-%d %H:%M:%S")}'
                    }), 403
                    
                if not contest['is_active']:
                     conn.close()
                     return jsonify({'error': 'Contest is currently inactive'}), 403
        
        conn.close()
    
    data = request.get_json()
    language = data.get('language')
    code = data.get('code')
    
    # Validate language
    if not language or language not in ALLOWED_LANGUAGES:
        return jsonify({
            'error': f'Invalid language. Allowed languages: {", ".join(ALLOWED_LANGUAGES)}'
        }), 400
    
    if not code or not code.strip():
        return jsonify({'error': 'Code cannot be empty'}), 400
    
    # Code size limit
    if len(code) > config.MAX_CODE_SIZE:
        return jsonify({
            'error': f'Code exceeds maximum size limit ({config.MAX_CODE_SIZE} bytes)'
        }), 400
    
    # Update last submit time
    session['last_submit_time'] = time.time()
    
    # Get problem test case
    conn = get_db()
    problem_row = conn.execute(
        'SELECT title, total_marks, test_input, expected_output, problem_mode, function_name FROM problems WHERE id = ?',
        (problem_id,)
    ).fetchone()
    
    if not problem_row:
        conn.close()
        return jsonify({'error': 'Problem not found'}), 404
    
    # Convert Row to dict for safe .get access patterns
    problem = dict(problem_row)
    
    # Create submission record with 'queued' status
    # Use local time for submissions to match contest start/end times which are typically entered as local
    cursor = conn.execute('''
        INSERT INTO submissions (user_id, problem_id, contest_id, language, code, output, verdict, judging_status, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
    ''', (session['user_id'], problem_id, contest_id, language, code, '', 'PENDING', 'queued'))
    
    submission_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    app.logger.info(f"Submission {submission_id} received from {session['username']} for problem {problem_id} (Lang: {language})")
    
    problem_mode = problem['problem_mode'] if 'problem_mode' in problem.keys() else 'stdin'
    function_name = problem['function_name'] if 'function_name' in problem.keys() else 'solve'

    # Add to judging queue
    # Determine queue priority (lower is higher priority)
    priority = 1
    if getattr(config, 'PRIORITY_QUEUE_ENABLED', False) and contest_id and contest_end_time:
        # If within priority window before contest end, boost priority
        seconds_left = (contest_end_time - datetime.now()).total_seconds()
        if seconds_left <= getattr(config, 'PRIORITY_WINDOW_SECONDS', 60):
            priority = 0

    enqueue_task({
        'submission_id': submission_id,
        'problem_id': problem_id,
        'problem_title': problem['title'],
        'user_id': session['user_id'],
        'username': session['username'],
        'language': language,
        'code': code,
        'problem_mode': problem_mode,
        'function_name': function_name,
        'total_marks': problem['total_marks'] if 'total_marks' in problem.keys() else 100
    }, priority=priority)
    
    # Emit queued event for real-time UI updates
    queued_payload = {
        'submission_id': submission_id,
        'problem_id': problem_id,
        'problem_title': problem['title'],
        'username': session['username'],
        'status': 'queued',
        'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'language': language
    }
    socketio.emit('submission_queued', queued_payload, room=f"user_{session['user_id']}")
    socketio.emit('admin_submission_queued', queued_payload, room='admin')
    
    # Wait for result (Synchronous fallback for students with stuck UIs)
    # This allows students to get their result by clicking Submit again without refreshment
    max_wait = 15  # 15 seconds max wait
    start_wait = time.time()
    while time.time() - start_wait < max_wait:
        with results_lock:
            if submission_id in submission_results:
                result = submission_results.pop(submission_id)
                # Ensure the verdict is final
                if result.get('verdict') != 'PENDING':
                    result['submission_id'] = submission_id
                    return jsonify(result)
        time.sleep(0.5)

    # If it takes too long, return pending (the UI will then start its own polling/socket logic if available)
    return jsonify({
        'submission_id': submission_id,
        'verdict': 'PENDING',
        'message': 'Submission is being processed. Please wait a moment...',
        'is_sample': False
    })

@app.route('/api/submission/<int:submission_id>')
def get_submission_result(submission_id):
    """Poll for submission result."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Check if result is ready in memory
    with results_lock:
        if submission_id in submission_results:
            # Security check: must belong to user or be admin
            if session.get('role') == 'admin' or submission_results[submission_id].get('user_id') == session['user_id']:
                result = submission_results.pop(submission_id)
                return jsonify(result)
            else:
                return jsonify({'error': 'Unauthorized'}), 401
    
    # Check database for result (must belong to user or be admin)
    conn = get_db()
    if session.get('role') == 'admin':
        submission = conn.execute(
            'SELECT verdict, output, judging_status FROM submissions WHERE id = ?',
            (submission_id,)
        ).fetchone()
    else:
        submission = conn.execute(
            'SELECT verdict, output, judging_status FROM submissions WHERE id = ? AND user_id = ?',
            (submission_id, session['user_id'])
        ).fetchone()
    conn.close()
    
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404
    
    if submission['judging_status'] == 'completed':
        return jsonify({
            'verdict': submission['verdict'],
            'output': submission['output'],
            'message': get_verdict_message(submission['verdict']),
            'is_sample': False
        })
    else:
        return jsonify({
            'verdict': 'PENDING',
            'message': 'Still judging...',
            'is_sample': False
        })

def get_verdict_message(verdict):
    """Get user-friendly message for verdict."""
    messages = {
        'AC': 'Accepted! Your solution is correct.',
        'PC': 'Partial Credit. Some test cases passed.',
        'WA': 'Wrong Answer. Your output does not match expected output.',
        'CE': 'Compilation Error. Please check your syntax.',
        'RE': 'Runtime Error. Your program crashed during execution.',
        'TLE': 'Time Limit Exceeded. Your program took too long to execute.',
        'PENDING': 'Submission is being judged...'
    }
    return messages.get(verdict, 'Unknown verdict')

# ============================================================================
# Leaderboard Routes
# ============================================================================

@app.route('/leaderboard')
def leaderboard():
    """Public leaderboard page."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    leaderboard_enabled = get_setting(conn, 'leaderboard_enabled', '1') == '1'
    if session.get('role') != 'admin' and not leaderboard_enabled:
        conn.close()
        return render_template('leaderboard.html', leaderboard_enabled=False)
    if session.get('role') == 'admin':
        contests = conn.execute('SELECT id, title FROM contests ORDER BY start_time DESC').fetchall()
    else:
        contests = conn.execute('SELECT id, title FROM contests WHERE is_active = 1 AND show_leaderboard = 1 ORDER BY start_time DESC').fetchall()
    conn.close()
    return render_template('leaderboard.html', leaderboard_enabled=True, contests=contests)

@app.route('/api/leaderboard')
@login_required
def api_leaderboard():
    """API endpoint for leaderboard data (HackerRank Style)."""
    contest_id = request.args.get('contest_id', type=int)
    conn = get_db()
    leaderboard_enabled = get_setting(conn, 'leaderboard_enabled', '1') == '1'
    if session.get('role') != 'admin' and not leaderboard_enabled:
        conn.close()
        return jsonify({'error': 'Leaderboard is disabled'}), 403
    
    # Logic:
    # 1. Total Points = sum of best points_awarded per problem
    # 2. Problems Solved = count of problems with best_points > 0
    # 3. Time Penalty = sum of earliest submission time achieving best points

    contest_start_sql = "0"
    params = []
    problem_filter = ""
    problem_filter_p2 = ""
    if contest_id:
        contest = conn.execute('SELECT start_time, show_leaderboard FROM contests WHERE id = ?', (contest_id,)).fetchone()
        if contest:
            if session.get('role') != 'admin' and not contest['show_leaderboard']:
                conn.close()
                return jsonify({'error': 'Leaderboard for this contest is disabled by admin'}), 403
            contest_start_sql = f"strftime('%s', '{contest['start_time']}')"
        problem_filter = "WHERE s.contest_id = ?"
        problem_filter_p2 = "WHERE s2.contest_id = ?"
        params.append(contest_id)
    else:
        # No contest filter -> avoid gigantic penalties by zero-basing each best submission
        contest_start_sql = "strftime('%s', best.best_time)"

    query = f'''
        SELECT 
            u.username,
            COALESCE(SUM(best.best_points), 0) as total_points,
            COUNT(DISTINCT CASE WHEN best.best_points > 0 THEN best.problem_id END) as problems_solved,
            COALESCE(SUM(CASE 
                WHEN best.best_points > 0 THEN 
                    (strftime('%s', best.best_time) - {contest_start_sql})
                ELSE 0 
            END), 0) as total_time_penalty
        FROM users u
        LEFT JOIN (
            SELECT s.user_id, s.problem_id,
                   MAX(COALESCE(s.points_awarded, 0)) as best_points,
                   MIN(CASE 
                        WHEN COALESCE(s.points_awarded, 0) = mx.best_points AND mx.best_points > 0 THEN s.submitted_at
                       END) as best_time
            FROM submissions s
            JOIN (
                SELECT s2.user_id, s2.problem_id, MAX(COALESCE(s2.points_awarded, 0)) as best_points
                FROM submissions s2
                {problem_filter_p2}
                GROUP BY s2.user_id, s2.problem_id
            ) mx ON mx.user_id = s.user_id AND mx.problem_id = s.problem_id
            {problem_filter}
            GROUP BY s.user_id, s.problem_id
        ) best ON u.id = best.user_id
        WHERE u.role = 'student'
        GROUP BY u.id, u.username
        ORDER BY total_points DESC, total_time_penalty ASC
    '''
    
    # Note: The above query simplifies things. Real HackerRank logic often counts ALL AC submissions? 
    # No, usually you get points once. The subquery `s` gets the "effective" submission.
    # If a user solves it, `s` will select the AC submission. If multiple AC, earliest one.
    # If only non-AC, it selects earliest non-AC (which contributes 0 points).
    
    query_params = params + params
    leaderboard_data = conn.execute(query, query_params).fetchall()
    conn.close()
    
    result = []
    for idx, row in enumerate(leaderboard_data, 1):
        total_seconds = int(row['total_time_penalty'] or 0)
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        
        if h > 0:
            time_str = f"{h:02d}:{m:02d}:{s:02d}"
        else:
            time_str = f"{m:02d}:{s:02d}"

        result.append({
            'rank': idx,
            'username': row['username'],
            'points': round(float(row['total_points'] or 0), 2),
            'problems_solved': int(row['problems_solved'] or 0),
            'time_str': time_str
        })
    
    return jsonify(result)

@app.route('/submission_status/<int:submission_id>')
def submission_status(submission_id):
    """Get the current status of a submission (for polling)."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db()
    sub = conn.execute('''
        SELECT s.verdict, s.output, s.judging_status, s.tests_passed, s.tests_total, s.points_awarded, p.total_marks
        FROM submissions s
        JOIN problems p ON s.problem_id = p.id
        WHERE s.id = ? AND s.user_id = ?
    ''', (submission_id, session['user_id'])).fetchone()
    show_scores = get_setting(conn, 'show_scores_to_students', '1') == '1'
    conn.close()
    
    if not sub:
        return jsonify({'error': 'Submission not found'}), 404
    
    response = {
        'verdict': sub['verdict'],
        'output': sub['output'] or '',
        'total_passed': sub['tests_passed'],
        'total_tests': sub['tests_total'],
        'message': 'Judging complete' if sub['judging_status'] == 'completed' else 'Judging in progress...'
    }
    
    if show_scores:
        response['points'] = sub['points_awarded']
        response['max_points'] = sub['total_marks']
        
    return jsonify(response)

# ============================================================================
# Admin Routes
# ============================================================================

@app.route('/admin')
def admin():
    """Admin dashboard."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db()
    
    # Get all users
    users = conn.execute('SELECT * FROM users ORDER BY id').fetchall()
    
    # Get all problems
    problems = conn.execute('SELECT * FROM problems ORDER BY id').fetchall()
    
    # Get all submissions (increased limit for realistic data)
    submissions = conn.execute('''
        SELECT s.*, u.username, p.title as problem_title
        FROM submissions s
        JOIN users u ON s.user_id = u.id
        JOIN problems p ON s.problem_id = p.id
        ORDER BY s.submitted_at DESC
        LIMIT 1000
    ''').fetchall()

    # Contests with problems (server-rendered fallback for Contest Management)
    contests = conn.execute('''
        SELECT 
            c.*,
            COUNT(p.id) as problem_count
        FROM contests c
        LEFT JOIN problems p ON c.id = p.contest_id
        GROUP BY c.id
        ORDER BY c.created_at DESC
    ''').fetchall()

    contests_with_problems = []
    for c in contests:
        problems_in = conn.execute('''
            SELECT p.*
            FROM problems p
            WHERE p.contest_id = ?
            ORDER BY p.id
        ''', (c['id'],)).fetchall()
        contests_with_problems.append({
            'contest': c,
            'problems': problems_in
        })

    unassigned_problems = conn.execute('''
        SELECT p.*
        FROM problems p
        WHERE p.contest_id IS NULL OR p.contest_id = ''
        ORDER BY p.id
    ''').fetchall()
    
    leaderboard_enabled = get_setting(conn, 'leaderboard_enabled', '1') == '1'
    show_scores_to_students = get_setting(conn, 'show_scores_to_students', '1') == '1'
    show_difficulty_to_students = get_setting(conn, 'show_difficulty_to_students', '1') == '1'
    conn.close()
    
    return render_template(
        'admin.html',
        users=users,
        problems=problems,
        submissions=submissions,
        leaderboard_enabled=leaderboard_enabled,
        show_scores_to_students=show_scores_to_students,
        show_difficulty_to_students=show_difficulty_to_students,
        contests_with_problems=contests_with_problems,
        unassigned_problems=unassigned_problems
    )

@app.route('/admin/create_user', methods=['POST'])
def create_user():
    """Create new user (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() if request.is_json else request.form
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'student')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            (username, hash_password(password), role)
        )
        conn.commit()
        return jsonify({'message': f"User '{username}' created successfully"})
    except sqlite3.IntegrityError:
        return jsonify({'error': f"Username '{username}' already exists"}), 400
    finally:
        conn.close()

@app.route('/admin/settings', methods=['POST'])
def update_settings():
    """Update global site settings (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() if request.is_json else request.form
    leaderboard_enabled = '1' if data.get('leaderboard_enabled') in (True, '1', 1, 'on', 'true') else '0'
    show_scores_to_students = '1' if data.get('show_scores_to_students') in (True, '1', 1, 'on', 'true') else '0'
    show_difficulty_to_students = '1' if data.get('show_difficulty_to_students') in (True, '1', 1, 'on', 'true') else '0'

    conn = get_db()
    set_setting(conn, 'leaderboard_enabled', leaderboard_enabled)
    set_setting(conn, 'show_scores_to_students', show_scores_to_students)
    set_setting(conn, 'show_difficulty_to_students', show_difficulty_to_students)
    conn.commit()
    log_admin_action('UPDATE_SETTINGS', f'Leaderboard: {leaderboard_enabled}, Show Scores: {show_scores_to_students}, Show Difficulty: {show_difficulty_to_students}')
    conn.close()

    return jsonify({'message': 'Settings updated'})

@app.route('/admin/create_problem', methods=['POST'])
def create_problem():
    """Create new problem (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json() if request.is_json else request.form
        
        # Required fields validation
        required_fields = {
            'title': 'Problem title',
            'problem_type': 'Problem type',
            'problem_mode': 'Problem mode',
            'function_name': 'Function name'
        }
        
        for field, label in required_fields.items():
            value = data.get(field, '').strip()
            if not value:
                return jsonify({'error': f'{label} is required'}), 400
        
        title = data.get('title').strip()
        description = data.get('description').strip()
        input_format = data.get('input_format', '')
        output_format = data.get('output_format', '')
        constraints = data.get('constraints', '')
        sample_input = data.get('sample_input', '')
        sample_output = data.get('sample_output', '')
        test_input = data.get('test_input', sample_input)
        expected_output = data.get('expected_output', sample_output)
        problem_type = data.get('problem_type', 'coding')
        contest_id = data.get('contest_id')
        starter_code = data.get('starter_code', '')
        starter_code_map = data.get('starter_code_map', '')
        problem_mode = data.get('problem_mode', None)
        function_name = data.get('function_name', 'solve')
        
        # Get total marks with validation
        try:
            total_marks = int(data.get('total_marks', 100))
            if total_marks < 1 or total_marks > 1000000:
                return jsonify({'error': 'Total marks must be between 1 and 1000000'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Total marks must be a valid number'}), 400
        
        conn = get_db()
        
        # Auto-set problem mode based on type if not specified
        if problem_mode is None:
            problem_mode = 'function' if problem_type == 'coding' else 'stdin'

        cursor = conn.execute('''
            INSERT INTO problems (
                title, description, input_format, output_format, constraints,
                sample_input, sample_output, test_input, expected_output,
                problem_type, total_marks, starter_code, contest_id, enabled,
                problem_mode, function_name, reference_solution, difficulty
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
        ''', (title, description, input_format, output_format, constraints,
              sample_input, sample_output, test_input, expected_output,
              problem_type, total_marks,
              starter_code_map if starter_code_map else starter_code,
              int(contest_id) if contest_id and contest_id != '' else None,
              problem_mode, function_name, data.get('reference_solution', ''),
              data.get('difficulty', 'easy')))
        problem_id = cursor.lastrowid
        
        # Save multi-language code to problem_code table if provided
        starter_code_dict = data.get('starter_code_dict', {})
        solution_code_dict = data.get('solution_code_dict', {})
        
        # If starter_code_map is a JSON string, parse it
        if starter_code_map and not starter_code_dict:
            try:
                starter_code_dict = json.loads(starter_code_map)
            except:
                pass
        
        # Save code for each language
        all_languages = set(list(starter_code_dict.keys()) + list(solution_code_dict.keys()))
        for lang in all_languages:
            starter = starter_code_dict.get(lang, '')
            solution = solution_code_dict.get(lang, data.get('reference_solution', ''))
            
            if starter or solution:
                conn.execute('''
                    INSERT OR REPLACE INTO problem_code (problem_id, language, solution_code, starter_code)
                    VALUES (?, ?, ?, ?)
                ''', (problem_id, lang, solution, starter))
        
        conn.commit()
        conn.close()
        
        # Log admin action
        log_admin_action('CREATE_PROBLEM', f'Created problem: {title} (ID: {problem_id})')
        
        return jsonify({
            'message': 'Problem created successfully',
            'problem_id': problem_id
        })
    
    except Exception as e:
        app.logger.error(f'Error creating problem: {str(e)}')
        return jsonify({'error': f'Failed to create problem: {str(e)}'}), 500


# ============================================================================
# Additional Admin Routes (Phase 1b)
# ============================================================================


@app.route('/admin/reset_password', methods=['POST'])
def reset_password():
    """Reset a user's password (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')
    
    if not user_id or not new_password:
        return jsonify({'error': 'Missing user_id or new_password'}), 400
    
    conn = get_db()
    conn.execute(
        'UPDATE users SET password = ? WHERE id = ?',
        (hash_password(new_password), user_id)
    )
    conn.commit()
    log_admin_action('RESET_PASSWORD', f'User ID: {user_id}')
    conn.close()
    
    return jsonify({'success': True, 'message': 'Password reset successfully'})

@app.route('/admin/bulk_reset_passwords', methods=['POST'])
def bulk_reset_passwords():
    """Reset passwords for all users or specific role (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() if request.is_json else request.form
    new_password = data.get('new_password', 'password123')
    role_filter = data.get('role', 'student')  # Default to students only
    
    if not new_password:
        return jsonify({'error': 'Password cannot be empty'}), 400
    
    conn = get_db()
    
    # Get users to reset (exclude admin to be safe)
    if role_filter == 'all':
        users = conn.execute(
            'SELECT id, username FROM users WHERE role != ?',
            ('admin',)
        ).fetchall()
    else:
        users = conn.execute(
            'SELECT id, username FROM users WHERE role = ?',
            (role_filter,)
        ).fetchall()
    
    if not users:
        conn.close()
        return jsonify({'error': f'No users found with role: {role_filter}'}), 404
    
    # Reset passwords
    hashed_password = hash_password(new_password)
    for user in users:
        conn.execute(
            'UPDATE users SET password = ? WHERE id = ?',
            (hashed_password, user['id'])
        )
    
    conn.commit()
    conn.close()
    
    # Log the action
    log_admin_action(
        'BULK_PASSWORD_RESET',
        f"Reset passwords for {len(users)} users (role: {role_filter})"
    )
    
    return jsonify({
        'success': True,
        'message': f'Successfully reset passwords for {len(users)} users',
        'count': len(users),
        'users': [u['username'] for u in users]
    })

@app.route('/admin/edit_problem/<int:problem_id>', methods=['POST'])
def edit_problem(problem_id):
    """Edit a problem (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() if request.is_json else request.form
    conn = get_db()

    existing = conn.execute('SELECT contest_id FROM problems WHERE id = ?', (problem_id,)).fetchone()
    existing_contest_id = existing['contest_id'] if existing else None

    if 'contest_id' in data:
        contest_id_val = data.get('contest_id')
        if contest_id_val in (None, ''):
            contest_id = None
        else:
            contest_id = int(contest_id_val)
    else:
        contest_id = existing_contest_id

    conn.execute('''
        UPDATE problems 
        SET title = ?, description = ?, input_format = ?, output_format = ?,
            sample_input = ?, sample_output = ?, test_input = ?, expected_output = ?,
            problem_type = ?, total_marks = ?, starter_code = ?, contest_id = ?,
            problem_mode = ?, function_name = ?, constraints = ?, reference_solution = ?, difficulty = ?
        WHERE id = ?
    ''', (
        data.get('title'),
        data.get('description'),
        data.get('input_format', ''),
        data.get('output_format', ''),
        data.get('sample_input', ''),
        data.get('sample_output', ''),
        data.get('test_input', data.get('sample_input', '')),
        data.get('expected_output', data.get('sample_output', '')),
        data.get('problem_type', 'coding'),
        int(data.get('total_marks', 100)),
        data.get('starter_code_map', data.get('starter_code', '')),
        contest_id,
        data.get('problem_mode', 'stdin'),
        data.get('function_name', 'solve'),
        data.get('constraints', ''),
        data.get('reference_solution', ''),
        data.get('difficulty', 'easy'),
        problem_id
    ))
    
    # Update multi-language code in problem_code table if provided
    starter_code_dict = data.get('starter_code_dict', {})
    solution_code_dict = data.get('solution_code_dict', {})
    
    # If starter_code_map is a JSON string, parse it
    starter_code_map = data.get('starter_code_map', '')
    if starter_code_map and not starter_code_dict:
        try:
            starter_code_dict = json.loads(starter_code_map)
        except:
            pass
    
    # Save code for each language
    all_languages = set(list(starter_code_dict.keys()) + list(solution_code_dict.keys()))
    for lang in all_languages:
        starter = starter_code_dict.get(lang, '')
        solution = solution_code_dict.get(lang, data.get('reference_solution', ''))
        
        if starter or solution:
            conn.execute('''
                INSERT OR REPLACE INTO problem_code (problem_id, language, solution_code, starter_code)
                VALUES (?, ?, ?, ?)
            ''', (problem_id, lang, solution, starter))
    
    conn.commit()

    # Redistribution of points if total_marks changed
    try:
        new_total_marks = int(data.get('total_marks', 100))
        
        hidden_tests = conn.execute(
            'SELECT id FROM test_cases WHERE problem_id = ? AND is_sample = 0',
            (problem_id,)
        ).fetchall()
        
        if new_total_marks > 0:
            redistribute_points(conn, problem_id, new_total_marks)
            conn.commit()
    except Exception as e:
        app.logger.error(f"Error redistributing points: {e}")

    log_admin_action('EDIT_PROBLEM', f'Edited problem ID: {problem_id}, Title: {data.get("title")}')
    conn.close()
    
    return jsonify({'success': True, 'message': 'Problem updated successfully'})

@app.route('/admin/test_problem/<int:problem_id>', methods=['POST'])
def test_problem(problem_id):
    """Test a problem with its test cases using reference solutions for all languages (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        solutions = data.get('solutions', {})  # Dict of {language: code}
        problem_mode = data.get('problem_mode', 'stdin')
        function_name = data.get('function_name', 'solve')
        
        if not solutions:
            return jsonify({'error': 'No reference solutions provided'}), 400
        
        conn = get_db()
        
        # Get all test cases for this problem
        test_cases = conn.execute('''
            SELECT id, input, expected_output, is_sample, points
            FROM test_cases
            WHERE problem_id = ?
            ORDER BY test_order, id
        ''', (problem_id,)).fetchall()
        
        conn.close()
        
        if not test_cases:
            return jsonify({'error': 'No test cases found for this problem'}), 400
        
        # Test each language
        all_results = {}
        
        for language, code in solutions.items():
            if not code or not code.strip():
                continue
                
            results = []
            passed = 0
            total = len(test_cases)
            
            for test_case in test_cases:
                test_input = test_case['input']
                expected_output = test_case['expected_output'].strip()
                
                # Judge the solution (returns tuple)
                verdict, actual_output = judge_submission(
                    language=language,
                    code=code,
                    test_input=test_input,
                    expected_output=expected_output,
                    mode=problem_mode,
                    function_name=function_name
                )
                
                is_correct = verdict == 'AC'
                if is_correct:
                    passed += 1
                
                results.append({
                    'test_id': test_case['id'],
                    'is_sample': bool(test_case['is_sample']),
                    'points': test_case['points'],
                    'verdict': verdict,
                    'passed': is_correct,
                    'input': test_input[:100] + '...' if len(test_input) > 100 else test_input,
                    'expected': expected_output[:100] + '...' if len(expected_output) > 100 else expected_output,
                    'actual': actual_output[:100] + '...' if len(actual_output) > 100 else actual_output,
                    'error': ''
                })
            
            all_results[language] = {
                'passed': passed,
                'total': total,
                'test_results': results
            }
        
        log_admin_action('TEST_PROBLEM', f'Tested problem ID: {problem_id} with {len(solutions)} language(s)')
        
        return jsonify({
            'success': True,
            'results': all_results
        })
        
    except Exception as e:
        app.logger.error(f'Error testing problem: {str(e)}')
        return jsonify({'error': f'Test failed: {str(e)}'}), 500

@app.route('/admin/delete_problem/<int:problem_id>', methods=['POST'])
def delete_problem(problem_id):
    """Delete a problem (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    conn.execute('DELETE FROM submissions WHERE problem_id = ?', (problem_id,))
    conn.execute('DELETE FROM problems WHERE id = ?', (problem_id,))
    conn.commit()
    conn.close()
    
    log_admin_action('DELETE_PROBLEM', f'Problem ID: {problem_id}')
    
    return jsonify({'success': True, 'message': 'Problem deleted successfully'})

@app.route('/admin/toggle_problem/<int:problem_id>', methods=['POST'])
def toggle_problem(problem_id):
    """Toggle problem enabled/disabled (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    problem = conn.execute('SELECT enabled, title FROM problems WHERE id = ?', (problem_id,)).fetchone()
    if not problem:
        conn.close()
        return jsonify({'error': 'Problem not found'}), 404
    
    new_status = 0 if problem['enabled'] else 1
    status_text = 'enabled' if new_status else 'disabled'
    conn.execute('UPDATE problems SET enabled = ? WHERE id = ?', (new_status, problem_id))
    conn.commit()
    log_admin_action('TOGGLE_PROBLEM', f'Problem: {problem["title"]} (ID: {problem_id}) set to {status_text}')
    conn.close()
    
    return jsonify({
        'success': True,
        'enabled': bool(new_status),
        'message': f'Problem {"enabled" if new_status else "disabled"}'
    })

@app.route('/admin/rejudge_problem/<int:problem_id>', methods=['POST'])
def rejudge_problem(problem_id):
    """Rejudge all submissions for a problem."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    subs = conn.execute('''
        SELECT s.id, s.language, s.code, s.user_id, u.username 
        FROM submissions s
        JOIN users u ON s.user_id = u.id
        WHERE s.problem_id = ?
    ''', (problem_id,)).fetchall()
    problem = conn.execute('SELECT problem_mode, function_name, title FROM problems WHERE id = ?', (problem_id,)).fetchone()
    
    problem_mode = problem['problem_mode'] if problem and 'problem_mode' in problem.keys() else 'stdin'
    function_name = problem['function_name'] if problem and 'function_name' in problem.keys() else 'solve'
    problem_title = problem['title'] if problem else f'Problem #{problem_id}'
    
    for s in subs:
        conn.execute('UPDATE submissions SET judging_status = ?, verdict = ? WHERE id = ?', ('queued', 'PENDING', s['id']))
        
        payload = {
            'submission_id': s['id'],
            'problem_id': problem_id,
            'problem_title': problem_title,
            'user_id': s['user_id'],
            'username': s['username'],
            'language': s['language'],
            'code': s['code'],
            'problem_mode': problem_mode,
            'function_name': function_name,
            'total_marks': problem['total_marks'] if problem and 'total_marks' in problem.keys() else 100,
            'status': 'queued',
            'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        enqueue_task(payload, priority=1)
        
        # Emit queued events
        socketio.emit('submission_queued', payload, room=f"user_{s['user_id']}")
        socketio.emit('admin_submission_queued', payload, room='admin')
        
    conn.commit()
    conn.close()
    
    # Log admin action
    log_admin_action('REJUDGE_PROBLEM', f'Problem: {problem_title} (ID: {problem_id}), Submissions: {len(subs)}')
    
    return jsonify({'message': f'Queued {len(subs)} submissions for rejudging'})


@app.route('/api/active_contests')
@login_required
def active_contests():
    """Get list of active/upcoming contests for student dashboard."""
    conn = get_db()
    contests = conn.execute('''
        SELECT id, title, start_time, end_time, is_active
        FROM contests
        WHERE is_active = 1
        ORDER BY start_time ASC
    ''').fetchall()
    conn.close()
    
    now = datetime.now()
    result = []
    
    for c in contests:
        start_time = datetime.fromisoformat(c['start_time'])
        end_time = datetime.fromisoformat(c['end_time'])
        
        if now < start_time:
            status = 'upcoming'
        elif now > end_time:
            status = 'ended'
        else:
            status = 'running'
            
        result.append({
            'id': c['id'],
            'title': c['title'],
            'start_time': c['start_time'],
            'end_time': c['end_time'],
            'status': status,
            'server_time': now.isoformat()
        })
        
    return jsonify(result)

@app.route('/api/contest_status/<int:contest_id>')
@login_required
def contest_status(contest_id):
    """Get status for a specific contest."""
    conn = get_db()
    contest = conn.execute('SELECT title, start_time, end_time, is_active FROM contests WHERE id = ?', (contest_id,)).fetchone()
    conn.close()
    
    if not contest:
        return jsonify({'error': 'Contest not found'}), 404
        
    now = datetime.now()
    start_time = datetime.fromisoformat(contest['start_time'])
    end_time = datetime.fromisoformat(contest['end_time'])
    
    if now < start_time:
        status = 'upcoming'
    elif now > end_time:
        status = 'ended'
    else:
        status = 'running'
        
    return jsonify({
        'id': contest_id,
        'title': contest['title'],
        'start_time': contest['start_time'],
        'end_time': contest['end_time'],
        'status': status,
        'active': bool(contest['is_active']),
        'server_time': now.isoformat()
    })

@app.route('/admin/contests')
def list_contests():
    """List all contests with problem counts (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    contests = conn.execute('''
        SELECT 
            c.*,
            COUNT(p.id) as problem_count
        FROM contests c
        LEFT JOIN problems p ON c.id = p.contest_id
        GROUP BY c.id
        ORDER BY c.created_at DESC
    ''').fetchall()
    conn.close()
    
    result = []
    for contest in contests:
        result.append({
            'id': contest['id'],
            'title': contest['title'],
            'description': contest['description'],
            'start_time': contest['start_time'],
            'end_time': contest['end_time'],
            'is_active': bool(contest['is_active']),
            'show_leaderboard': bool(dict(contest).get('show_leaderboard', True)),
            'problem_count': contest['problem_count']
        })
    
    return jsonify(result)

@app.route('/admin/contest/<int:contest_id>/problems')
def contest_problems(contest_id):
    """List all problems for a specific contest (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    if contest_id == 0:
        query = '''
            SELECT p.*, 
                   (SELECT COUNT(*) FROM submissions s WHERE s.problem_id = p.id) as submission_count,
                   (SELECT COUNT(*) FROM submissions s WHERE s.problem_id = p.id AND s.verdict = 'AC') as ac_count
            FROM problems p
            WHERE p.contest_id IS NULL OR p.contest_id = ''
            ORDER BY p.id
        '''
        problems = conn.execute(query).fetchall()
    else:
        query = '''
            SELECT p.*, 
                   (SELECT COUNT(*) FROM submissions s WHERE s.problem_id = p.id) as submission_count,
                   (SELECT COUNT(*) FROM submissions s WHERE s.problem_id = p.id AND s.verdict = 'AC') as ac_count
            FROM problems p
            WHERE p.contest_id = ?
            ORDER BY p.id
        '''
        problems = conn.execute(query, (contest_id,)).fetchall()
    conn.close()
    
    result = []
    for p in problems:
        result.append({
            'id': p['id'],
            'title': p['title'],
            'description': p['description'],
            'enabled': bool(p['enabled']),
            'submission_count': p['submission_count'],
            'ac_count': p['ac_count'],
            'problem_type': p['problem_type'],
            'round_number': p['round_number'],
            'problem_mode': p['problem_mode'],
            'function_name': p['function_name'],
            'difficulty': p['difficulty']
        })
    
    return jsonify(result)

@app.route('/admin/problems_list')
def problems_list():
    """List all problems (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    problems = conn.execute('''
        SELECT p.*, 
               (SELECT COUNT(*) FROM submissions s WHERE s.problem_id = p.id) as submission_count,
               (SELECT COUNT(*) FROM submissions s WHERE s.problem_id = p.id AND s.verdict = 'AC') as ac_count
        FROM problems p
        ORDER BY p.id DESC
    ''').fetchall()
    conn.close()

    result = []
    for p in problems:
        result.append({
            'id': p['id'],
            'title': p['title'],
            'description': p['description'],
            'enabled': bool(p['enabled']),
            'contest_id': p['contest_id'],
            'submission_count': p['submission_count'],
            'ac_count': p['ac_count'],
            'problem_type': p['problem_type'],
            'round_number': p['round_number'],
            'problem_mode': p['problem_mode'],
            'function_name': p['function_name'],
            'difficulty': p['difficulty']
        })
    return jsonify(result)

@app.route('/admin/create_contest', methods=['POST'])
def create_contest():
    """Create a new contest (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() if request.is_json else request.form
    title = data.get('title') or data.get('name')
    description = data.get('description', '')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    
    if not title:
        return jsonify({'error': 'Contest title is required'}), 400
        
    if not start_time or not end_time:
        return jsonify({'error': 'Start and End times are required'}), 400
    
    show_leaderboard = 1 if data.get('show_leaderboard') not in (False, '0', 0, 'false') else 0
    
    conn = get_db()
    cursor = conn.execute('''
        INSERT INTO contests (title, description, start_time, end_time, is_active, show_leaderboard)
        VALUES (?, ?, ?, ?, 1, ?)
    ''', (title, description, start_time, end_time, show_leaderboard))
    contest_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Log admin action
    log_admin_action('CREATE_CONTEST', f'Title: {title}, Start: {start_time}, End: {end_time}')
    
    return jsonify({'message': 'Contest created successfully', 'contest_id': contest_id})

@app.route('/admin/edit_contest/<int:contest_id>', methods=['POST'])
def edit_contest(contest_id):
    """Edit an existing contest (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() if request.is_json else request.form
    title = data.get('title') or data.get('name')
    description = data.get('description')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    is_active = data.get('is_active')
    
    conn = get_db()
    
    # Dynamic update based on provided fields
    fields = []
    values = []
    if title:
        fields.append('title = ?')
        values.append(title)
    if description is not None:
        fields.append('description = ?')
        values.append(description)
    if start_time:
        fields.append('start_time = ?')
        values.append(start_time)
    if end_time:
        fields.append('end_time = ?')
        values.append(end_time)
    if is_active is not None:
        fields.append('is_active = ?')
        values.append(1 if is_active else 0)
    
    show_leaderboard = data.get('show_leaderboard')
    if show_leaderboard is not None:
        fields.append('show_leaderboard = ?')
        values.append(1 if show_leaderboard in (True, '1', 1, 'on', 'true') else 0)
        
    values.append(contest_id)
    
    if fields:
        conn.execute(f'UPDATE contests SET {", ".join(fields)} WHERE id = ?', values)
        conn.commit()
        log_admin_action('EDIT_CONTEST', f'Edited contest ID: {contest_id}, Title: {title}')
        
    conn.close()
    return jsonify({'message': 'Contest updated successfully'})

@app.route('/admin/toggle_contest/<int:contest_id>', methods=['POST'])
def toggle_contest(contest_id):
    """Enable/disable (activate/deactivate) a contest (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    
    # Get current status
    contest = conn.execute('SELECT is_active, title FROM contests WHERE id = ?', (contest_id,)).fetchone()
    if not contest:
        conn.close()
        return jsonify({'error': 'Contest not found'}), 404
    
    new_status = 0 if contest['is_active'] else 1
    status_text = 'activated' if new_status else 'deactivated'
    
    # Update contest status
    conn.execute('UPDATE contests SET is_active = ? WHERE id = ?', (new_status, contest_id))
    conn.commit()
    conn.close()
    
    # Log admin action
    log_admin_action('TOGGLE_CONTEST', f'Contest: {contest["title"]} (ID: {contest_id}), New Status: {status_text}')
    
    return jsonify({'message': f'Contest {status_text} successfully', 'is_active': bool(new_status)})

@app.route('/admin/delete_contest/<int:contest_id>', methods=['POST'])
def delete_contest(contest_id):
    """Delete a contest and all associated problems and submissions (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    try:
        contest_title = conn.execute('SELECT title FROM contests WHERE id = ?', (contest_id,)).fetchone()
        contest_title = contest_title['title'] if contest_title else f'ID: {contest_id}'

        # 1. Delete all submissions for problems in this contest
        conn.execute('''
            DELETE FROM submissions 
            WHERE contest_id = ? OR problem_id IN (SELECT id FROM problems WHERE contest_id = ?)
        ''', (contest_id, contest_id))
        
        # 2. Delete all test cases for problems in this contest
        conn.execute('''
            DELETE FROM test_cases 
            WHERE problem_id IN (SELECT id FROM problems WHERE contest_id = ?)
        ''', (contest_id,))
        
        # 3. Delete all problems in this contest
        conn.execute('DELETE FROM problems WHERE contest_id = ?', (contest_id,))
        
        # 4. Delete the contest itself
        conn.execute('DELETE FROM contests WHERE id = ?', (contest_id,))
        
        conn.commit()
        log_admin_action('DELETE_CONTEST', f'Deleted contest: {contest_title}')
        return jsonify({'success': True, 'message': 'Contest and all associated data deleted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Failed to delete contest: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/admin/assign_problem/<int:problem_id>', methods=['POST'])
def assign_problem(problem_id):
    """Assign a problem to a contest (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() if request.is_json else request.form
    contest_id = data.get('contest_id')
    
    if contest_id is None:
        return jsonify({'error': 'Contest ID is required'}), 400
    
    conn = get_db()
    
    # Verify contest exists
    contest_title = "Unassigned"
    if contest_id != '':
        contest = conn.execute('SELECT id, title FROM contests WHERE id = ?', (contest_id,)).fetchone()
        if not contest:
            conn.close()
            return jsonify({'error': 'Contest not found'}), 404
        contest_title = contest['title']
    
    problem_title = conn.execute('SELECT title FROM problems WHERE id = ?', (problem_id,)).fetchone()
    problem_title = problem_title['title'] if problem_title else f'ID: {problem_id}'

    # Update problem
    conn.execute('UPDATE problems SET contest_id = ? WHERE id = ?', 
                 (contest_id if contest_id != '' else None, problem_id))
    conn.commit()
    log_admin_action('ASSIGN_PROBLEM', f'Problem: {problem_title} (ID: {problem_id}) assigned to contest: {contest_title} (ID: {contest_id if contest_id != "" else "None"})')
    conn.close()
    
    return jsonify({'message': 'Problem assigned successfully'})

@app.route('/admin/stats')
def admin_stats():
    """Get platform statistics for the admin dashboard (Live & General)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    
    # General Stats
    stats = {
        'total_users': conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count'],
        'total_problems': conn.execute('SELECT COUNT(*) as count FROM problems').fetchone()['count'],
        'total_submissions': conn.execute('SELECT COUNT(*) as count FROM submissions').fetchone()['count'],
        'total_contests': conn.execute('SELECT COUNT(*) as count FROM contests').fetchone()['count']
    }
    
    # Live Stats
    pending_count = conn.execute("SELECT COUNT(*) FROM submissions WHERE judging_status = 'queued' OR judging_status = 'processing'").fetchone()[0]
    conn.close()
    
    # Active Workers
    stats['queue_size'] = submission_queue.qsize()
    stats['pending_submissions'] = pending_count
    stats['active_workers'] = config.MAX_CONCURRENT_JUDGES
    
    return jsonify(stats)

@app.route('/api/admin/users')
def list_users_api():
    """Get list of users (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    users = conn.execute('SELECT id, username, role FROM users ORDER BY id DESC').fetchall()
    conn.close()
    
    return jsonify([dict(u) for u in users])

@app.route('/api/admin/submissions')
def list_submissions_api():
    """Get recent submissions (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    submissions = conn.execute('''
        SELECT s.id, s.submitted_at, s.verdict, s.judging_status, 
               u.username, p.title as problem_title, p.id as problem_id, s.language
        FROM submissions s
        JOIN users u ON s.user_id = u.id
        JOIN problems p ON s.problem_id = p.id
        ORDER BY s.submitted_at DESC
        LIMIT 50
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(s) for s in submissions])

@app.route('/api/admin/submissions_search')
def submissions_search():
    """Search submissions with filters (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    username = request.args.get('username', '').strip()
    problem = request.args.get('problem', '').strip()
    verdict = request.args.get('verdict', '').strip()
    contest_id = request.args.get('contest_id', '').strip()
    limit = request.args.get('limit', '50').strip()

    try:
        limit_val = min(max(int(limit), 1), 500)
    except ValueError:
        limit_val = 50

    where = []
    params = []
    if username:
        where.append("u.username LIKE ?")
        params.append(f"%{username}%")
    if problem:
        where.append("p.title LIKE ?")
        params.append(f"%{problem}%")
    if verdict:
        where.append("s.verdict = ?")
        params.append(verdict)
    if contest_id:
        where.append("s.contest_id = ?")
        params.append(contest_id)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    conn = get_db()
    submissions = conn.execute(f'''
        SELECT s.id, s.submitted_at, s.verdict, s.judging_status, 
               u.username, p.title as problem_title, p.id as problem_id, s.language, s.contest_id
        FROM submissions s
        JOIN users u ON s.user_id = u.id
        JOIN problems p ON s.problem_id = p.id
        {where_sql}
        ORDER BY s.submitted_at DESC
        LIMIT ?
    ''', (*params, limit_val)).fetchall()
    conn.close()

    return jsonify([dict(s) for s in submissions])

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete a user (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Don't delete yourself
    if user_id == session['user_id']:
        return jsonify({'error': 'Cannot delete your own account'}), 400
        
    conn = get_db()
    username = conn.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
    username = username['username'] if username else f'ID: {user_id}'
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    log_admin_action('DELETE_USER', f'Deleted user: {username} (ID: {user_id})')
    conn.close()
    
    return jsonify({'success': True, 'message': 'User deleted successfully'})

@app.route('/admin/bulk_create_users', methods=['POST'])
def bulk_create_users():
    """Create multiple users at once (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    users_text = request.form.get('users_text', '')
    if not users_text.strip():
        return jsonify({'error': 'No users provided'}), 400
    
    lines = users_text.strip().split('\n')
    created = []
    errors = []
    
    conn = get_db()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 2:
            errors.append(f'Invalid format: {line}')
            continue
        
        username = parts[0]
        password = parts[1]
        role = parts[2] if len(parts) > 2 else 'student'
        
        if role not in ['admin', 'student']:
            errors.append(f'Invalid role for {username}: {role}')
            continue
        
        try:
            conn.execute(
                'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                (username, hash_password(password), role)
            )
            created.append(username)
        except sqlite3.IntegrityError:
            errors.append(f'Username already exists: {username}')
    
    conn.commit()
    log_admin_action('BULK_CREATE_USERS', f'Created {len(created)} users')
    conn.close()
    
    return jsonify({
        'created': created,
        'errors': errors,
        'total_created': len(created),
        'total_errors': len(errors)
    })

@app.route('/admin/problem/<int:problem_id>/upload_test_cases', methods=['POST'])
def upload_test_cases(problem_id):
    """Upload test cases from file (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        content = file.read().decode('utf-8')
        test_cases = parse_test_case_file(content)
        
        conn = get_db()
        
        # Get total marks for the problem
        problem = conn.execute('SELECT total_marks FROM problems WHERE id = ?', (problem_id,)).fetchone()
        total_marks = problem['total_marks'] if problem and 'total_marks' in problem.keys() else 100
        
        # Import test cases
        count = import_test_cases_to_db(conn, problem_id, test_cases)
        
        # No need to redistribute here, import_test_cases_to_db handles it
        
        conn.commit()
        log_admin_action('UPLOAD_TEST_CASES', f'Problem ID: {problem_id}, Count: {count}')
        conn.close()
        
        return jsonify({'message': f'Successfully imported {count} test cases. Points distributed automatically based on total marks ({total_marks}).'})
        
    return jsonify({'error': 'Upload failed'}), 500

@app.route('/admin/upload_problem_image', methods=['POST'])
def upload_problem_image():
    """Upload an image for problem description (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
    filename = file.filename.lower()
    if not any(filename.endswith('.' + ext) for ext in allowed_extensions):
        return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, SVG, WEBP'}), 400
    
    try:
        # Generate unique filename
        import secrets
        ext = filename.rsplit('.', 1)[1]
        unique_filename = f"{secrets.token_hex(16)}.{ext}"
        
        # Save file
        upload_folder = os.path.join(app.root_path, 'static', 'problem_images')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)
        
        # Return URL
        image_url = f"/static/problem_images/{unique_filename}"
        log_admin_action('UPLOAD_IMAGE', f'Image: {unique_filename}')
        
        return jsonify({
            'success': True,
            'url': image_url,
            'filename': unique_filename
        })
    except Exception as e:
        app.logger.error(f'Error uploading image: {str(e)}')
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/admin/reset_contest', methods=['POST'])
def reset_contest():
    """Clear all submissions (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    submission_count = conn.execute('SELECT COUNT(*) as count FROM submissions').fetchone()['count']
    conn.execute('DELETE FROM submissions')
    conn.commit()
    conn.close()
    
    # Log admin action
    log_admin_action('RESET_CONTEST', f'Deleted {submission_count} submissions')
    
    return jsonify({'message': 'Contest reset successfully. All submissions cleared.'})

@app.route('/admin/clear_students', methods=['POST'])
def clear_students():
    """Delete all student accounts (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    conn.execute("DELETE FROM users WHERE role = 'student'")
    conn.commit()
    log_admin_action('CLEAR_STUDENTS', 'Deleted all student accounts')
    conn.close()
    
    return jsonify({'message': 'All student accounts deleted successfully.'})

@app.route('/admin/export_leaderboard')
def export_leaderboard():
    """Export leaderboard to CSV."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    conn = get_db()
    csv_data = export_leaderboard_csv(conn)
    conn.close()
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=leaderboard.csv"}
    )

@app.route('/admin/view_submission/<int:submission_id>')
def view_submission(submission_id):
    """View a submission's code/output (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    sub = conn.execute('''
        SELECT s.*, u.username, p.title as problem_title
        FROM submissions s
        JOIN users u ON s.user_id = u.id
        JOIN problems p ON s.problem_id = p.id
        WHERE s.id = ?
    ''', (submission_id,)).fetchone()
    conn.close()

    if not sub:
        return jsonify({'error': 'Submission not found'}), 404

    return jsonify({
        'id': sub['id'],
        'username': sub['username'],
        'problem_title': sub['problem_title'],
        'language': sub['language'],
        'verdict': sub['verdict'],
        'code': sub['code'],
        'output': sub['output'] or ''
    })


@app.route('/api/problem_details/<int:problem_id>')
def get_problem_details(problem_id):
    """Get problem details for editing (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    problem = conn.execute('SELECT * FROM problems WHERE id = ?', (problem_id,)).fetchone()
    
    if not problem:
        conn.close()
        return jsonify({'error': 'Problem not found'}), 404
    
    # Get all language code from problem_code table
    code_rows = conn.execute('''
        SELECT language, solution_code, starter_code
        FROM problem_code
        WHERE problem_id = ?
    ''', (problem_id,)).fetchall()
    
    conn.close()
    
    problem_dict = dict(problem)
    
    # Add code maps
    solutions = {}
    starter_codes = {}
    for row in code_rows:
        lang = row[0]
        if row[1]:  # solution_code
            solutions[lang] = row[1]
        if row[2]:  # starter_code
            starter_codes[lang] = row[2]
    
    if solutions:
        problem_dict['solutions'] = solutions
    if starter_codes:
        problem_dict['starter_codes'] = starter_codes
    
    return jsonify(problem_dict)

@app.route('/api/student/problem/<int:problem_id>')
def get_student_problem(problem_id):
    """Get problem details and test cases for student view."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db()
    problem = conn.execute('SELECT * FROM problems WHERE id = ?', (problem_id,)).fetchone()
    
    if not problem:
        conn.close()
        return jsonify({'error': 'Problem not found'}), 404
        
    # Get sample test cases
    sample_tests = conn.execute('''
        SELECT input, expected_output, description 
        FROM test_cases 
        WHERE problem_id = ? AND is_sample = 1
        ORDER BY test_order
    ''', (problem_id,)).fetchall()
    
    # Check if we should show scores (based on contest settings if applicable)
    show_scores = get_setting(conn, 'show_scores_to_students', '1') == '1'
    
    conn.close()
    
    # Try to get starter code from problem_code table first
    starter_map = get_problem_code_map(problem_id, 'starter')
    
    # Fallback to legacy starter_code field if problem_code table is empty
    if not starter_map:
        starter_map = parse_starter_code(problem['starter_code'])
    
    # Final fallback to default templates
    if not starter_map:
        starter_map = default_starter_map(problem['problem_mode'], problem['function_name'])

    response = {
        'id': problem['id'],
        'title': problem['title'],
        'description': problem['description'],
        'input_format': problem['input_format'],
        'output_format': problem['output_format'],
        'constraints': problem['constraints'] or '',
        'problem_type': problem['problem_type'],
        'problem_mode': problem['problem_mode'],
        'function_name': problem['function_name'],
        'total_marks': problem['total_marks'],
        'sample_input': problem['sample_input'],
        'sample_output': problem['sample_output'],
        'sample_tests': [dict(tc) for tc in sample_tests],
        'starter_code_map': json.dumps(starter_map),
        'contest_id': problem['contest_id'],
        'show_scores': show_scores
    }
    
    return jsonify(response)



@app.route('/admin/problem/<int:problem_id>/test_cases')
def list_test_cases(problem_id):
    """List test cases for a problem (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    test_cases = conn.execute('SELECT * FROM test_cases WHERE problem_id = ? ORDER BY test_order', (problem_id,)).fetchall()
    conn.close()
    return jsonify([dict(tc) for tc in test_cases])

@app.route('/admin/problem/<int:problem_id>/add_test_case', methods=['POST'])
def add_test_case(problem_id):
    """Add a test case to a problem (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    input_data = data.get('input', '')
    expected_output = data.get('expected_output', '')
    is_sample = data.get('is_sample', 0)
    
    conn = get_db()
    
    # Get total marks for the problem
    problem = conn.execute('SELECT total_marks FROM problems WHERE id = ?', (problem_id,)).fetchone()
    total_marks = problem['total_marks'] if problem and 'total_marks' in problem.keys() else 100
    
    # Add the test case with 0 points initially
    conn.execute('''
        INSERT INTO test_cases (problem_id, input, expected_output, is_sample, points)
        VALUES (?, ?, ?, ?, 0)
    ''', (problem_id, input_data, expected_output, is_sample))
    
    # Redistribute points equally among all hidden test cases
    if not is_sample:
        hidden_tests = conn.execute(
            'SELECT id FROM test_cases WHERE problem_id = ? AND is_sample = 0',
            (problem_id,)
        ).fetchall()
        
        if len(hidden_tests) > 0:
            points_per_test = float(total_marks) / len(hidden_tests)
            for test in hidden_tests:
                conn.execute('UPDATE test_cases SET points = ? WHERE id = ?', (points_per_test, test['id']))
    
    conn.commit()
    log_admin_action('ADD_TEST_CASE', f'Problem ID: {problem_id}, Sample: {is_sample}')
    conn.close()
    return jsonify({'message': 'Test case added successfully'})

@app.route('/admin/delete_test_case/<int:test_case_id>', methods=['POST'])
def delete_test_case(test_case_id):
    """Delete a test case (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    conn.execute('DELETE FROM test_cases WHERE id = ?', (test_case_id,))
    conn.commit()
    log_admin_action('DELETE_TEST_CASE', f'Test Case ID: {test_case_id}')
    conn.close()
    return jsonify({'message': 'Test case deleted successfully'})

@app.route('/admin/logs')
def admin_logs():
    """Get admin action logs for audit trail (excluding proctor events)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    limit = request.args.get('limit', 50, type=int)
    
    conn = get_db()
    logs = conn.execute('''
        SELECT al.*, u.username
        FROM admin_logs al
        JOIN users u ON al.admin_id = u.id
        WHERE al.action != 'PROCTOR_EVENT'
        ORDER BY al.created_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    
    result = []
    for log in logs:
        result.append({
            'admin': log['username'],
            'action': log['action'],
            'details': log['details'],
            'ip_address': log['ip_address'],
            'created_at': log['created_at']
        })
    return jsonify(result)

@app.route('/admin/proctor_logs')
def admin_proctor_logs():
    """Get proctoring events (fullscreen exits, tab switches)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    limit = request.args.get('limit', 50, type=int)
    
    conn = get_db()
    logs = conn.execute('''
        SELECT al.*, u.username
        FROM admin_logs al
        JOIN users u ON al.admin_id = u.id
        WHERE al.action = 'PROCTOR_EVENT'
        ORDER BY al.created_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    
    result = []
    for log in logs:
        result.append({
            'admin': log['username'],
            'action': log['action'],
            'details': log['details'],
            'ip_address': log['ip_address'],
            'created_at': log['created_at']
        })
    return jsonify(result)

@app.route('/admin/detailed_leaderboard')
def admin_detailed_leaderboard():
    """Get detailed leaderboard with per-contest breakdown (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    
    # Get all contests
    contests = conn.execute('SELECT id, title, start_time FROM contests ORDER BY id').fetchall()
    
    # Get all users with their total scores
    users = conn.execute('''
        SELECT u.id, u.username, u.role
        FROM users u
        WHERE u.role = 'student'
        ORDER BY u.username
    ''').fetchall()
    
    result = []
    for user in users:
        user_data = {
            'user_id': user['id'],
            'username': user['username'],
            'total_points': 0,
            'total_problems_solved': 0,
            'total_time_penalty': 0,
            'highest_score': 0,
            'contests': {}
        }
        
        # Get scores per contest
        for contest in contests:
            contest_score = conn.execute('''
                SELECT 
                    COALESCE(SUM(best.best_points), 0) as points,
                    COUNT(DISTINCT CASE WHEN best.best_points > 0 THEN best.problem_id END) as solved,
                    COALESCE(SUM(CASE 
                        WHEN best.best_points > 0 AND best.best_time IS NOT NULL THEN 
                            CASE 
                                WHEN (julianday(best.best_time) - julianday(?)) * 86400 > 0 
                                THEN (julianday(best.best_time) - julianday(?)) * 86400
                                ELSE 0
                            END
                        ELSE 0 
                    END), 0) as time_penalty
                FROM (
                    SELECT 
                        s.problem_id, 
                        MAX(COALESCE(s.points_awarded, 0)) as best_points,
                        MIN(CASE 
                            WHEN COALESCE(s.points_awarded, 0) = (
                                SELECT MAX(COALESCE(s2.points_awarded, 0))
                                FROM submissions s2
                                WHERE s2.user_id = s.user_id AND s2.problem_id = s.problem_id
                            ) THEN s.submitted_at
                        END) as best_time
                    FROM submissions s
                    JOIN problems p ON s.problem_id = p.id
                    WHERE s.user_id = ? AND p.contest_id = ?
                    GROUP BY s.problem_id
                ) best
            ''', (contest['start_time'], contest['start_time'], user['id'], contest['id'])).fetchone()
            
            user_data['contests'][contest['title']] = {
                'points': int(contest_score['points'] or 0),
                'solved': int(contest_score['solved'] or 0)
            }
            contest_points = int(contest_score['points'] or 0)
            user_data['total_points'] += contest_points
            user_data['total_problems_solved'] += int(contest_score['solved'] or 0)
            user_data['total_time_penalty'] += int(contest_score['time_penalty'] or 0)
            
            # Track highest score from any single contest
            if contest_points > user_data['highest_score']:
                user_data['highest_score'] = contest_points
        
        result.append(user_data)
    
    conn.close()
    
    # Sort by total points (descending), then by time penalty (ascending - lower is better)
    result.sort(key=lambda x: (-x['total_points'], x['total_time_penalty']))
    
    # Add ranks
    for idx, user in enumerate(result, 1):
        user['rank'] = idx
    
    return jsonify(result)

@app.route('/admin/user_scorecard/<int:user_id>')
def admin_user_scorecard(user_id):
    """Get detailed scorecard for a specific user (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    
    # Get user info
    user = conn.execute('SELECT id, username, role FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    # Get all contests
    contests = conn.execute('SELECT id, title FROM contests ORDER BY id').fetchall()
    
    scorecard = {
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'total_points': 0,
        'total_problems_solved': 0,
        'total_submissions': 0,
        'contests': []
    }
    
    # Get overall stats
    overall_stats = conn.execute('''
        SELECT 
            COUNT(*) as total_submissions,
            COUNT(DISTINCT problem_id) as problems_attempted,
            SUM(CASE WHEN verdict = 'AC' THEN 1 ELSE 0 END) as ac_count
        FROM submissions
        WHERE user_id = ?
    ''', (user_id,)).fetchone()
    
    scorecard['total_submissions'] = overall_stats['total_submissions']
    scorecard['problems_attempted'] = overall_stats['problems_attempted']
    scorecard['ac_submissions'] = overall_stats['ac_count']
    
    # Get per-contest breakdown
    for contest in contests:
        # Get problems in this contest
        problems = conn.execute('''
            SELECT id, title, difficulty, total_marks
            FROM problems
            WHERE contest_id = ?
            ORDER BY id
        ''', (contest['id'],)).fetchall()
        
        contest_data = {
            'contest_id': contest['id'],
            'contest_title': contest['title'],
            'total_points': 0,
            'problems_solved': 0,
            'problems': []
        }
        
        for problem in problems:
            # Get best submission for this problem
            best_sub = conn.execute('''
                SELECT 
                    MAX(COALESCE(points_awarded, 0)) as best_points,
                    COUNT(*) as attempts,
                    MAX(CASE WHEN verdict = 'AC' THEN 1 ELSE 0 END) as solved
                FROM submissions
                WHERE user_id = ? AND problem_id = ?
            ''', (user_id, problem['id'])).fetchone()
            
            # Get all submissions for this problem
            submissions = conn.execute('''
                SELECT id, submitted_at, verdict, points_awarded, language, 
                       code, tests_passed, tests_total, output
                FROM submissions
                WHERE user_id = ? AND problem_id = ?
                ORDER BY submitted_at DESC
            ''', (user_id, problem['id'])).fetchall()
            
            problem_data = {
                'problem_id': problem['id'],
                'problem_title': problem['title'],
                'difficulty': problem['difficulty'],
                'total_marks': problem['total_marks'],
                'best_points': int(best_sub['best_points'] or 0),
                'attempts': best_sub['attempts'],
                'solved': bool(best_sub['solved']),
                'submissions': [dict(s) for s in submissions]
            }
            
            contest_data['problems'].append(problem_data)
            contest_data['total_points'] += problem_data['best_points']
            if problem_data['solved']:
                contest_data['problems_solved'] += 1
        
        scorecard['contests'].append(contest_data)
        scorecard['total_points'] += contest_data['total_points']
        scorecard['total_problems_solved'] += contest_data['problems_solved']
    
    conn.close()
    return jsonify(scorecard)

@app.route('/admin/contest_leaderboard/<int:contest_id>')
def admin_contest_leaderboard(contest_id):
    """Get leaderboard for a specific contest (admin only)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    
    # Get contest info
    contest = conn.execute('SELECT id, title, start_time FROM contests WHERE id = ?', (contest_id,)).fetchone()
    if not contest:
        conn.close()
        return jsonify({'error': 'Contest not found'}), 404
    
    # Get leaderboard for this contest with time for sorting (but not displayed)
    leaderboard = conn.execute('''
        SELECT 
            u.id as user_id,
            u.username,
            COALESCE(SUM(best.best_points), 0) as total_points,
            COUNT(DISTINCT CASE WHEN best.best_points > 0 THEN best.problem_id END) as problems_solved,
            COUNT(DISTINCT best.problem_id) as problems_attempted,
            COALESCE(SUM(CASE 
                WHEN best.best_points > 0 AND best.best_time IS NOT NULL THEN 
                    CASE 
                        WHEN (julianday(best.best_time) - julianday(?)) * 86400 > 0 
                        THEN (julianday(best.best_time) - julianday(?)) * 86400
                        ELSE 0
                    END
                ELSE 0 
            END), 0) as time_penalty
        FROM users u
        LEFT JOIN (
            SELECT 
                s.user_id, 
                s.problem_id, 
                MAX(COALESCE(s.points_awarded, 0)) as best_points,
                MIN(CASE 
                    WHEN COALESCE(s.points_awarded, 0) = (
                        SELECT MAX(COALESCE(s2.points_awarded, 0))
                        FROM submissions s2
                        JOIN problems p2 ON s2.problem_id = p2.id
                        WHERE s2.user_id = s.user_id AND s2.problem_id = s.problem_id AND p2.contest_id = ?
                    ) THEN s.submitted_at
                END) as best_time
            FROM submissions s
            JOIN problems p ON s.problem_id = p.id
            WHERE p.contest_id = ?
            GROUP BY s.user_id, s.problem_id
        ) best ON u.id = best.user_id
        WHERE u.role = 'student'
        GROUP BY u.id, u.username
        ORDER BY total_points DESC, time_penalty ASC, problems_solved DESC
    ''', (contest['start_time'], contest['start_time'], contest_id, contest_id)).fetchall()
    
    conn.close()
    
    result = {
        'contest_id': contest['id'],
        'contest_title': contest['title'],
        'leaderboard': []
    }
    
    # Include time_penalty in response for display
    for idx, row in enumerate(leaderboard, 1):
        result['leaderboard'].append({
            'rank': idx,
            'user_id': row['user_id'],
            'username': row['username'],
            'points': round(float(row['total_points'] or 0), 2),
            'problems_solved': int(row['problems_solved'] or 0),
            'problems_attempted': int(row['problems_attempted'] or 0),
            'time_penalty': int(row['time_penalty'] or 0)
        })
    
    return jsonify(result)

@app.route('/health')
def health():
    """Lightweight health check for lab monitoring."""
    try:
        conn = get_db()
        conn.execute('SELECT 1')
        pending = conn.execute(
            "SELECT COUNT(*) as count FROM submissions WHERE judging_status != 'completed'"
        ).fetchone()['count']
        conn.close()
        status = 'ok'
    except Exception as e:
        app.logger.error('Health check failed: %s', str(e))
        status = 'error'
        pending = -1
    return jsonify({
        'status': status,
        'queue_size': submission_queue.qsize(),
        'pending_submissions': pending
    })

# ============================================================================
# SocketIO Event Handlers (Real-Time Updates) - Optimized
# ============================================================================

# Track connected clients to avoid unnecessary emissions
connected_clients = set()
connected_clients_lock = Lock()

@socketio.on('connect')
def handle_connect():
    """Handle client connection - optimized."""
    if 'user_id' in session:
        user_id = session['user_id']
        # Join user's personal room for submission updates
        join_room(f'user_{user_id}')
        
        # Track connection
        with connected_clients_lock:
            connected_clients.add(user_id)
        
        app.logger.info(f'User {user_id} connected to WebSocket')
        emit('connected', {'message': 'Connected to real-time updates'}, room=f'user_{user_id}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection - optimized."""
    if 'user_id' in session:
        user_id = session['user_id']
        leave_room(f'user_{user_id}')
        
        # Remove from tracking
        with connected_clients_lock:
            connected_clients.discard(user_id)
        
        app.logger.info(f'User {user_id} disconnected from WebSocket')

@socketio.on('join_leaderboard')
def handle_join_leaderboard():
    """Join leaderboard room for live updates."""
    join_room('leaderboard')
    emit('joined_leaderboard', {'message': 'Subscribed to leaderboard updates'})

@socketio.on('join_admin')
def handle_join_admin():
    """Join admin room for live submission feed."""
    if session.get('role') == 'admin':
        join_room('admin')
        emit('joined_admin', {'message': 'Subscribed to admin live feed'})

@socketio.on('leave_leaderboard')
def handle_leave_leaderboard():
    """Leave leaderboard room."""
    leave_room('leaderboard')

@socketio.on('broadcast')
def handle_broadcast(data):
    """Broadcast message to all connected clients."""
    if session.get('role') == 'admin':
        message = data.get('message')
        if message:
            # Use socketio.emit to include the sender
            socketio.emit('broadcast', {
                'message': message,
                'sender': session.get('username', 'Admin'),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            app.logger.info(f'Admin broadcast: {message}')

@socketio.on('ping')
def handle_ping():
    """Handle ping for connection keep-alive."""
    emit('pong', {'timestamp': time.time()})

# ============================================================================
# Main Block
# ============================================================================

def timer_sync_thread():
    """Background thread to sync contest timers - optimized for minimal load."""
    while True:
        try:
            with app.app_context():
                conn = get_db()
                active_contests = conn.execute(
                    "SELECT id, title, start_time, end_time FROM contests WHERE is_active = 1"
                ).fetchall()
                conn.close()
                
                # Only emit if there are active contests
                if not active_contests:
                    time.sleep(5)  # Check less frequently if no active contests
                    continue
                
                now = datetime.now()
                contests_data = []
                for c in active_contests:
                    try:
                        # Flexible date parsing
                        def parse_dt(s):
                            s = s.replace('T', ' ')
                            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
                                try: return datetime.strptime(s, fmt)
                                except: pass
                            return datetime.fromisoformat(s.replace(' ', 'T'))

                        start = parse_dt(c['start_time'])
                        end = parse_dt(c['end_time'])
                        
                        if now < start:
                            status = 'upcoming'
                            remaining = (start - now).total_seconds()
                        elif now < end:
                            status = 'running'
                            remaining = (end - now).total_seconds()
                        else:
                            status = 'ended'
                            remaining = 0
                        
                        contests_data.append({
                            'id': c['id'],
                            'status': status,
                            'remaining': int(remaining)
                        })
                    except Exception as e:
                        app.logger.error(f"Timer sync error for contest {c['id']}: {e}")
                
                # Emit timer updates (broadcast to all connected clients)
                socketio.emit('timer_update', {
                    'server_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'contests': contests_data
                }, namespace='/')
        except Exception as e:
            app.logger.error(f"Global timer sync error: {e}")
        
        # Reduced frequency: 2 seconds instead of 1 (50% less load)
        time.sleep(2)

# Start background services when module is imported (per process)
start_background_services()

if __name__ == '__main__':
    # Start background services (idempotent)
    start_background_services()
    
    # Try to find an available port
    import socket
    
    def is_port_available(port):
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return True
        except OSError:
            return False
    
    # Try ports in sequence (prefer configured port first)
    preferred_port = getattr(config, 'PORT', 8080)
    ports_to_try = [preferred_port, 8080, 8081, 8082, 8083, 8084, 8085, 5000, 5001, 5002, 9000, 10000]
    # Deduplicate while preserving order
    seen = set()
    ports_to_try = [p for p in ports_to_try if not (p in seen or seen.add(p))]
    selected_port = None
    
    for port in ports_to_try:
        if is_port_available(port):
            selected_port = port
            break
    
    if selected_port is None:
        print("\n" + "="*60)
        print("ERROR: No available ports found!")
        print("="*60)
        print("\nTried ports:", ", ".join(map(str, ports_to_try)))
        print("\nPlease free up one of these ports or specify a different port.")
        exit(1)
    
    print("\n" + "="*60)
    print("Multi-Language Coding Contest Platform")
    print("="*60 + "\n")
    print(f"✓ Server starting at http://localhost:{selected_port}")
    print(f"✓ Real-time updates enabled (WebSocket)")
    print(f"✓ Default admin credentials: admin / RelicAdmin!2026")
    
    if selected_port != 8080:
        print(f"\n⚠️  Note: Port 8080 was busy, using port {selected_port} instead")
    
    print("\nPress Ctrl+C to stop the server\n")
    
    # Use socketio.run() instead of app.run() for WebSocket support
    try:
        socketio.run(app, host='0.0.0.0', port=selected_port, debug=config.DEBUG, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("Server stopped by user")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n\nError starting server: {e}\n")
        exit(1)
