#!/usr/bin/env python3
"""
Export utilities for contest data.
Generates CSV files and ZIP archives for admin download.
"""

import csv
import io
import zipfile
from datetime import datetime

def export_leaderboard_csv(conn):
    """Export leaderboard to CSV format."""
    # Get leaderboard data
    users = conn.execute('''
        SELECT 
            u.username,
            COUNT(DISTINCT CASE WHEN s.verdict = 'AC' THEN s.problem_id END) as solved,
            COUNT(s.id) as total_submissions,
            MAX(s.submitted_at) as last_submission
        FROM users u
        LEFT JOIN submissions s ON u.id = s.user_id
        WHERE u.role = 'student'
        GROUP BY u.id, u.username
        ORDER BY solved DESC, total_submissions ASC
    ''').fetchall()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Rank', 'Username', 'Problems Solved', 'Total Submissions', 'Last Submission'])
    
    # Write data
    for rank, user in enumerate(users, 1):
        writer.writerow([
            rank,
            user['username'],
            user['solved'],
            user['total_submissions'],
            user['last_submission'] or 'N/A'
        ])
    
    return output.getvalue()

def export_submissions_csv(conn):
    """Export all submissions to CSV format."""
    submissions = conn.execute('''
        SELECT 
            s.id,
            u.username,
            p.title as problem,
            s.language,
            s.verdict,
            s.submitted_at
        FROM submissions s
        JOIN users u ON s.user_id = u.id
        JOIN problems p ON s.problem_id = p.id
        ORDER BY s.submitted_at DESC
    ''').fetchall()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Submission ID', 'Username', 'Problem', 'Language', 'Verdict', 'Submitted At'])
    
    # Write data
    for sub in submissions:
        writer.writerow([
            sub['id'],
            sub['username'],
            sub['problem'],
            sub['language'],
            sub['verdict'],
            sub['submitted_at']
        ])
    
    return output.getvalue()

def export_code_zip(conn):
    """Export all submitted code as ZIP archive."""
    submissions = conn.execute('''
        SELECT 
            s.id,
            u.username,
            p.title as problem,
            s.language,
            s.code,
            s.verdict,
            s.submitted_at
        FROM submissions s
        JOIN users u ON s.user_id = u.id
        JOIN problems p ON s.problem_id = p.id
        ORDER BY u.username, p.id, s.submitted_at
    ''').fetchall()
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Group by user
        for sub in submissions:
            # Create filename: username/problem_title/submission_id_verdict.ext
            ext_map = {
                'python': 'py',
                'c': 'c',
                'cpp': 'cpp',
                'java': 'java',
            }
            ext = ext_map.get(sub['language'], 'txt')
            
            # Sanitize filenames
            username = sub['username'].replace('/', '_')
            problem = sub['problem'].replace('/', '_').replace(' ', '_')
            
            filename = f"{username}/{problem}/submission_{sub['id']}_{sub['verdict']}.{ext}"
            
            # Add code to ZIP
            zip_file.writestr(filename, sub['code'])
        
        # Add README
        readme = f"""Contest Code Export
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This archive contains all submitted code from the contest.

Structure:
- username/
  - problem_name/
    - submission_ID_VERDICT.ext

Verdicts:
- AC: Accepted (Correct)
- WA: Wrong Answer
- CE: Compilation Error
- RE: Runtime Error
- TLE: Time Limit Exceeded
"""
        zip_file.writestr('README.txt', readme)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()
