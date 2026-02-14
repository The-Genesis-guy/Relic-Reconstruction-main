#!/usr/bin/env python3
"""
PRODUCTION CONFIG - High Concurrency for Last-Second Submissions
Handles 50+ simultaneous submissions at contest deadline
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'
IS_WINDOWS = os.name == 'nt'
PYTHON_BIN = os.environ.get('PYTHON_BIN', 'python' if IS_WINDOWS else 'python3')

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# DATABASE - Optimized for High Concurrency
# ============================================================================
DB_NAME = os.environ.get('DB_PATH', str(DATA_DIR / 'contest.db'))

DB_PRAGMA_SETTINGS = {
    'journal_mode': 'WAL',
    'synchronous': 'NORMAL',
    'busy_timeout': 30000,  # ✅ INCREASED: 30s timeout (was 5s)
    'foreign_keys': 'ON',
    'cache_size': -64000,  # ✅ INCREASED: 64MB cache (was 10MB)
    'temp_store': 'MEMORY',  # ✅ NEW: Use RAM for temp tables
}

# ============================================================================
# JUDGING - Scaled for 50+ Concurrent Submissions
# ============================================================================
MAX_CODE_SIZE = 50000
MAX_OUTPUT_SIZE = 200000
JUDGE_TIMEOUT = 5

# ✅ CRITICAL FIX: Increase workers to handle burst load
MAX_CONCURRENT_JUDGES = int(os.environ.get('MAX_CONCURRENT_JUDGES', 30))  # Was 10
NUM_JUDGE_WORKERS = int(os.environ.get('NUM_JUDGE_WORKERS', 30))  # Was 4

# ✅ NEW: Queue prioritization for last-minute submissions
PRIORITY_QUEUE_ENABLED = True
PRIORITY_WINDOW_SECONDS = 60  # Last 60s of contest = high priority

# ============================================================================
# RATE LIMITING - Relaxed for contest end
# ============================================================================
SUBMISSION_COOLDOWN = int(os.environ.get('SUBMISSION_COOLDOWN', 3))  # Reduced from 10
RUN_COOLDOWN = int(os.environ.get('RUN_COOLDOWN', 2))  # Reduced from 3

# ============================================================================
# CONTEST SETTINGS
# ============================================================================
GRACE_PERIOD = int(os.environ.get('GRACE_PERIOD', 60))  # ✅ INCREASED: 60s grace (was 30s)

# ✅ NEW: Watchdog for stuck submissions during high load
WATCHDOG_INTERVAL = 30  # Check every 30s (was 60s)
STUCK_SUBMISSION_TIMEOUT = 180  # 3 minutes before marking as stuck

# ============================================================================
# SERVER SETTINGS
# ============================================================================
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 8080))
DEBUG = False

# SECRET_KEY for session signing - Set to a fixed value for stability during restarts
SECRET_KEY = os.environ.get('SECRET_KEY', 'relic-reconstruction-2026-production-key-v1')

# ============================================================================
# LOGGING
# ============================================================================
LOG_FILE = LOGS_DIR / 'server.log'
LOG_LEVEL = 'INFO'
LOG_MAX_BYTES = 5_000_000  # 5MB
LOG_BACKUP_COUNT = 5

# ============================================================================
# SUPPORTED LANGUAGES
# ============================================================================
ALLOWED_LANGUAGES = ['python', 'c', 'cpp', 'java']

LANGUAGE_CONFIG = {
    # Use the detected python binary so Windows hosts (python.exe) work without edits
    'python': {'extension': '.py', 'compile_cmd': None, 'run_cmd': [PYTHON_BIN, '{file}']},
    'c': {'extension': '.c', 'compile_cmd': ['gcc', '-o', '{output}', '{file}', '-lm'], 'run_cmd': ['{output}']},
    'cpp': {'extension': '.cpp', 'compile_cmd': ['g++', '-o', '{output}', '{file}', '-std=c++17'], 'run_cmd': ['{output}']},
    'java': {'extension': '.java', 'compile_cmd': ['javac', '{file}'], 'run_cmd': ['java', '-cp', '{dir}', '{classname}']},
}

VERDICT_MESSAGES = {
    'AC': 'Accepted! Your solution is correct.',
    'PC': 'Partial Credit. Some test cases passed.',
    'WA': 'Wrong Answer. Your output does not match expected output.',
    'CE': 'Compilation Error. Please check your syntax.',
    'RE': 'Runtime Error. Your program crashed during execution.',
    'TLE': 'Time Limit Exceeded. Your program took too long to execute.',
    'MLE': 'Memory Limit Exceeded. Your program used too much memory.',
    'PENDING': 'Submission is being judged...',
}

def validate_config():
    """Validate configuration settings"""
    if MAX_CODE_SIZE <= 0:
        raise ValueError("MAX_CODE_SIZE must be positive")
    if JUDGE_TIMEOUT <= 0:
        raise ValueError("JUDGE_TIMEOUT must be positive")
    if MAX_CONCURRENT_JUDGES <= 0:
        raise ValueError("MAX_CONCURRENT_JUDGES must be positive")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY cannot be empty")
    if PORT < 1 or PORT > 65535:
        raise ValueError("PORT must be between 1 and 65535")
    
    # ✅ NEW: Warn if workers seem insufficient
    import warnings
    if MAX_CONCURRENT_JUDGES < 20:
        warnings.warn(
            f"MAX_CONCURRENT_JUDGES={MAX_CONCURRENT_JUDGES} may be insufficient for 50+ concurrent submissions. "
            "Recommended: 30+",
            RuntimeWarning
        )

validate_config()
