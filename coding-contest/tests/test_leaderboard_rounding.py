import sqlite3
from datetime import datetime, timedelta


def login_admin(client):
    return client.post("/login", data={"username": "admin", "password": "RelicAdmin!2026"})


def seed_user(conn, username):
    conn.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, 'student')",
        (username, ""),
    )
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def test_leaderboard_returns_decimal_points(app_client):
    client, flask_app = app_client
    conn = sqlite3.connect(flask_app.config.DB_NAME)
    conn.row_factory = sqlite3.Row

    # Admin already exists from init_db
    login_admin(client)

    # Contest & problem
    start = datetime.now() - timedelta(minutes=10)
    end = datetime.now() + timedelta(minutes=10)
    conn.execute(
        """
        INSERT INTO contests (title, description, start_time, end_time, is_active, show_leaderboard)
        VALUES (?, ?, ?, ?, 1, 1)
        """,
        ("LB Test", "desc", start.isoformat(sep=" "), end.isoformat(sep=" ")),
    )
    contest_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    conn.execute(
        """
        INSERT INTO problems (title, description, input_format, output_format,
                              sample_input, sample_output, test_input, expected_output,
                              total_marks, contest_id, enabled, problem_mode, function_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'stdin', 'solve')
        """,
        (
            "Decimal Points",
            "desc",
            "in",
            "out",
            "1",
            "1",
            "1",
            "1",
            100,
            contest_id,
        ),
    )
    problem_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Students
    alice_id = seed_user(conn, "alice")
    bob_id = seed_user(conn, "bob")

    # Submissions with fractional points (use points_awarded directly)
    conn.execute(
        """
        INSERT INTO submissions (user_id, problem_id, contest_id, code, language, points_awarded, verdict, judging_status, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, 'AC', 'completed', datetime('now'))
        """,
        (alice_id, problem_id, contest_id, "print(1)", "python", 33.33),
    )
    conn.execute(
        """
        INSERT INTO submissions (user_id, problem_id, contest_id, code, language, points_awarded, verdict, judging_status, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, 'AC', 'completed', datetime('now'))
        """,
        (bob_id, problem_id, contest_id, "print(1)", "python", 66.67),
    )
    conn.commit()

    # Login as alice to call /api/leaderboard
    client.post("/login", data={"username": "alice", "password": "password123"})
    resp = client.get(f"/api/leaderboard?contest_id={contest_id}")
    assert resp.status_code == 200
    data = resp.get_json()

    # ensure decimal points are preserved (not truncated)
    alice_row = next(row for row in data if row["username"] == "alice")
    bob_row = next(row for row in data if row["username"] == "bob")
    assert alice_row["points"] == 33.33
    assert bob_row["points"] == 66.67

    conn.close()
