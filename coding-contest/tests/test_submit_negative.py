import json
import sqlite3
from datetime import datetime, timedelta


def setup_contest_problem(conn):
    start = datetime.now() - timedelta(minutes=5)
    end = datetime.now() + timedelta(minutes=5)
    conn.execute(
        "INSERT INTO contests (title, description, start_time, end_time, is_active, show_leaderboard) VALUES (?, ?, ?, ?, 1, 1)",
        ("Neg Tests", "desc", start.isoformat(sep=" "), end.isoformat(sep=" ")),
    )
    contest_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.execute(
        """
        INSERT INTO problems (title, description, input_format, output_format,
                              sample_input, sample_output, test_input, expected_output,
                              total_marks, contest_id, enabled, problem_mode, function_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 100, ?, 1, 'stdin', 'solve')
        """,
        ("Neg Problem", "desc", "in", "out", "1", "1", "1", "1", contest_id),
    )
    problem_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    return contest_id, problem_id


def login_student(client, username="student1"):
    # ensure user exists
    db_path = getattr(client, "db_path", None)
    conn = sqlite3.connect(db_path)
    from app import hash_password

    conn.execute(
        "INSERT OR REPLACE INTO users (username, password, role) VALUES (?, ?, 'student')",
        (username, hash_password("password123")),
    )
    conn.commit()
    conn.close()
    client.post(
        "/login",
        data={"username": username, "password": "password123"},
        follow_redirects=True,
    )


def test_submit_rejects_invalid_language(app_client):
    client, flask_app = app_client
    conn = sqlite3.connect(flask_app.config.DB_NAME)
    conn.row_factory = sqlite3.Row
    _, problem_id = setup_contest_problem(conn)
    conn.close()

    login_student(client)
    resp = client.post(
        f"/submit/{problem_id}",
        data=json.dumps({"language": "brainfuck", "code": "++"}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert "Invalid language" in resp.get_json()["error"]


def test_submit_rejects_empty_code(app_client):
    client, flask_app = app_client
    conn = sqlite3.connect(flask_app.config.DB_NAME)
    conn.row_factory = sqlite3.Row
    _, problem_id = setup_contest_problem(conn)
    conn.close()

    login_student(client)
    resp = client.post(
        f"/submit/{problem_id}",
        data=json.dumps({"language": "python", "code": "   "}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert "Code cannot be empty" in resp.get_json()["error"]


def test_submit_blocks_before_start(app_client):
    client, flask_app = app_client
    conn = sqlite3.connect(flask_app.config.DB_NAME)
    conn.row_factory = sqlite3.Row
    start = datetime.now() + timedelta(minutes=5)
    end = datetime.now() + timedelta(minutes=10)
    conn.execute(
        "INSERT INTO contests (title, description, start_time, end_time, is_active, show_leaderboard) VALUES (?, ?, ?, ?, 1, 1)",
        ("Future Contest", "desc", start.isoformat(sep=" "), end.isoformat(sep=" ")),
    )
    contest_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.execute(
        """
        INSERT INTO problems (title, description, input_format, output_format,
                              sample_input, sample_output, test_input, expected_output,
                              total_marks, contest_id, enabled, problem_mode, function_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 100, ?, 1, 'stdin', 'solve')
        """,
        ("Future Prob", "desc", "in", "out", "1", "1", "1", "1", contest_id),
    )
    problem_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.close()

    login_student(client)
    resp = client.post(
        f"/submit/{problem_id}",
        data=json.dumps({"language": "python", "code": "print(1)"}),
        content_type="application/json",
    )
    assert resp.status_code == 403
    assert "has not started yet" in resp.get_json()["error"]
