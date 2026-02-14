import os
import importlib
import tempfile
import shutil
import pytest


@pytest.fixture()
def app_client():
    """
    Spin up a fresh app + temp DB for each test.
    Background workers are disabled via env to avoid extra threads.
    """
    # Isolate database and worker counts
    tmp_dir = tempfile.mkdtemp(prefix="contest_test_")
    db_path = os.path.join(tmp_dir, "test.db")
    os.environ["DB_PATH"] = db_path
    # Use minimal but valid worker counts to satisfy config validation
    os.environ["MAX_CONCURRENT_JUDGES"] = "1"
    os.environ["NUM_JUDGE_WORKERS"] = "1"

    # Reload config/init_db to pick up env overrides
    import config
    import init_db

    importlib.reload(config)
    importlib.reload(init_db)

    # Initialize schema
    init_db.init_database()

    # Import app after config is ready
    import app as flask_app
    importlib.reload(flask_app)

    with flask_app.app.test_client() as client:
        # Expose DB path on test client for helpers
        client.db_path = flask_app.config.DB_NAME
        yield client, flask_app

    shutil.rmtree(tmp_dir, ignore_errors=True)
