# Deployment Guide (Lab / Production-ish)

This platform is designed to run on a single machine for a lab-style contest (≈50 students submitting near the deadline). The default settings in `coding-contest/config.py` are tuned for burst load.

If you only need to run it locally, `README.md` is enough. Use this guide when you want a repeatable “host machine” setup.

## 1) Prerequisites (install once)

- Python 3.9+
- For multi-language judging:
  - C: `gcc`
  - C++: `g++`
  - Java: `javac` + `java`
- Recommended: run on an SSD (SQLite + compilation + temp files benefit a lot)

Windows notes:
- Install MinGW-w64 (GCC/G++) and add its `bin` directory to PATH.
- Install an OpenJDK (11+) and add `bin` to PATH.

## 2) One-time project setup

From the repo root:

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r coding-contest/requirements.txt
```

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r coding-contest/requirements.txt
```

## 3) Initialize the database

```bash
cd coding-contest
python init_db.py
```

This creates `coding-contest/data/contest.db` and inserts a default admin account (`admin` / `RelicAdmin!2026`).

## 4) Configure runtime settings (recommended)

All settings live in `coding-contest/config.py` and can be overridden via environment variables.

Recommended environment variables for a real lab host:

- `SECRET_KEY` (required for any real deployment)
- `PORT` (default `8080`)
- `DB_PATH` (optional; default is inside `coding-contest/data/`)

Windows (PowerShell):
```powershell
$env:PORT="8080"
$env:SECRET_KEY="change-me-long-random"
# Optional:
# $env:DB_PATH="D:\\contest\\contest.db"
```

macOS/Linux:
```bash
export PORT=8080
export SECRET_KEY='change-me-long-random'
# Optional:
# export DB_PATH=/srv/contest/contest.db
```

## 5) Run the server

```bash
cd coding-contest
python app.py
```

Open:
- Local: `http://localhost:8080`
- LAN: `http://<host-ip>:8080`

### Firewall (Windows)
```powershell
netsh advfirewall firewall add rule name="Relic8080" dir=in action=allow protocol=TCP localport=8080
```

## 6) Pre-contest checklist

1. Start the server and confirm `/login` and `/admin` load.
2. Login as admin, create student accounts (or bulk import).
3. Import problems/contest content (see `docs/ADMIN_AND_CONTENT.md`).
4. Smoke-test judging end-to-end:
   ```bash
   cd coding-contest
   python tools/comprehensive_test.py
   ```

Optional (dev deps):
```bash
pip install -r coding-contest/requirements-dev.txt
cd coding-contest
pytest
```

## 7) Operations

- Logs: `coding-contest/logs/server.log`
- DB: `coding-contest/data/contest.db` (plus `contest.db-wal` / `contest.db-shm` while running)
- Restart: stop the process and run again
- If you see “database is locked”: ensure only one server process is using the DB; keep the DB on local disk (not a network share)

## 8) Backups (important)

SQLite WAL means you should stop the server before taking a clean backup.

Safe manual backup:
1. Stop the server
2. Copy `coding-contest/data/contest.db`
3. (If present) also copy `coding-contest/data/contest.db-wal` and `coding-contest/data/contest.db-shm`
4. Start the server

## 9) Security notes (read before exposing anywhere)

This system executes user-submitted code. Treat it as **unsafe** to expose directly to the public internet unless you add real sandboxing.

Minimum hardening for a lab:
- Set `SECRET_KEY` (don’t use the default).
- Change the default admin password immediately.
- Keep it on a private LAN; don’t port-forward it to the internet.
- Run on a dedicated machine/account with minimal privileges.
