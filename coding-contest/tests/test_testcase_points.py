import sqlite3

from src.test_case_parser import import_test_cases_to_db


def test_hidden_points_sum_to_total_marks(app_client):
    client, flask_app = app_client
    conn = sqlite3.connect(flask_app.config.DB_NAME)
    conn.row_factory = sqlite3.Row

    # Insert a problem with total_marks=100
    conn.execute(
        """
        INSERT INTO problems (title, description, input_format, output_format,
                              sample_input, sample_output, test_input, expected_output,
                              total_marks, enabled)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            "Sum Hidden Points",
            "desc",
            "in",
            "out",
            "1",
            "1",
            "1",
            "1",
            100,
        ),
    )
    problem_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Build 3 sample + 4 hidden testcases
    tests = []
    for i in range(7):
        tests.append(
            {
                "input": f"{i}",
                "expected_output": f"{i}",
                "is_sample": i < 3,
                "points": 0,
            }
        )

    import_test_cases_to_db(conn, problem_id, tests, total_marks=100)

    # Sum hidden points
    total = conn.execute(
        "SELECT SUM(points) FROM test_cases WHERE problem_id=? AND is_sample=0",
        (problem_id,),
    ).fetchone()[0]

    samples_points = conn.execute(
        "SELECT SUM(points) FROM test_cases WHERE problem_id=? AND is_sample=1",
        (problem_id,),
    ).fetchone()[0]

    assert round(total, 2) == 100.0
    assert samples_points == 0

    conn.close()
