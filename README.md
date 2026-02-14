# Multi-Language Coding Contest Platform

A local-first, multi-language coding contest platform (Flask + Socket.IO) built for college labs and timed contests. It includes:

- A web UI for admins/students
- A queue-based judge (Python/C/C++/Java)
- Contests, problems, test cases, leaderboards
- Scripts to convert/import problem packs (folder ⇄ JSON ⇄ DB)

## Quick Start (Local)

### 1) Create + activate a virtual environment

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```bash
pip install -r coding-contest/requirements.txt
```

### 3) Initialize the database (creates default admin)
```bash
cd coding-contest
python init_db.py
cd ..
```

### 4) Run the server
```bash
cd coding-contest
python app.py
```

Open: `http://localhost:8080`

Default admin (created by `coding-contest/init_db.py`):
- Username: `admin`
- Password: `RelicAdmin!2026`

## Documentation (Minimal Set)

- `docs/DEPLOYMENT.md` — lab/production deployment checklist and ops
- `docs/ADMIN_AND_CONTENT.md` — admin workflows + importing problem packs

## Repo Layout (What matters)

- `coding-contest/` — the web app + judge
  - `coding-contest/app.py` — Flask routes + Socket.IO events
  - `coding-contest/config.py` — runtime configuration (PORT, DB_PATH, workers, etc.)
  - `coding-contest/init_db.py` — creates DB schema + default admin user
  - `coding-contest/data/contest.db` — SQLite DB (default location)
  - `coding-contest/logs/server.log` — server logs
- `round1_full_pack_optionA_solutions/` — example contest pack (descriptions, testcases, starter code, solutions) + `json_output/`
- Root scripts (run from repo root):
  - `batch_convert_to_json.py` — folder pack → JSON files
  - `convert_to_json.py` — single problem folder → JSON
  - `import_questions_to_db.py` — JSON file/dir → SQLite DB
  - `create_shattered_syntax_contest.py` — imports the bundled pack as a contest
  - `verify_all_solutions.py` — sanity-checks Python solutions vs `testcases.txt`

## Key Environment Variables

Set these before launching `coding-contest/app.py` (see `coding-contest/config.py`):

- `PORT` — HTTP port (default `8080`)
- `DB_PATH` — SQLite path (default `coding-contest/data/contest.db`)
- `SECRET_KEY` — Flask session signing key (default is hardcoded; set your own for real deployments)
- `MAX_CONCURRENT_JUDGES`, `NUM_JUDGE_WORKERS` — concurrency tuning (defaults `30`)
- `PYTHON_BIN` — python executable used by the judge (defaults to `python` on Windows, `python3` elsewhere)

## Troubleshooting

- Port in use: set `PORT` (or stop the conflicting process).
- `gcc/g++/javac` not found: install compilers and ensure they are on PATH.
- “database is locked”: stop extra server instances; SQLite WAL is enabled, but multiple writers can still contend.
- Don’t expose this to the public internet as-is: the judge executes untrusted code (see security notes in `docs/DEPLOYMENT.md`).
