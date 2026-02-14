# Admin + Content Guide

This guide covers:

- Admin workflows in the web UI (`/admin`)
- Recommended test case file format
- Importing problems/contests from the bundled problem packs (folder / JSON)

## 1) Admin login + core pages

Start the server (`cd coding-contest && python app.py`) and open:

- Login: `http://localhost:8080/login`
- Admin: `http://localhost:8080/admin`

Default admin is created by `coding-contest/init_db.py`:
- `admin` / `RelicAdmin!2026`

## 2) User management

In **Admin → User Management** you can:

- Create a single user (student/admin)
- Bulk create users (CSV text area)
- Bulk reset passwords (students only / all non-admin)

Bulk create format (one per line):
```
username,password,role
student1,pass123,student
proctor1,pass123,admin
```

## 3) Contest management

In **Admin → Contests** you can:

- Create a contest with start/end time
- Toggle active status
- Enable/disable contest leaderboard visibility

Student views:
- Contest page: `/contest/<id>`
- Contest SPA (kiosk-style): `/contest/<id>/spa`

## 4) Problems + test cases

In **Admin → Problems** you can create/edit problems with:

- Difficulty (`easy`, `medium`, `hard`)
- Mode:
  - `stdin`: classic input/output
  - `function`: student fills a named function (used by some problems)
- Total marks (points are redistributed across hidden test cases)

### Test case file format (upload)

Upload a text file in this format:
```txt
# Test Case 1 (Sample)
INPUT:
1 2
OUTPUT:
3

# Test Case 2 (Sample)
INPUT:
10 20
OUTPUT:
30

# Test Case 3 (Sample)
INPUT:
5
OUTPUT:
25

# Test Case 4 (Hidden)
INPUT:
100 200
OUTPUT:
300
```

Important behavior (see `coding-contest/src/test_case_parser.py`):
- The first **3** test cases are treated as **Sample** (visible, `0` points).
- Remaining test cases are **Hidden** (graded).
- Hidden test case points are redistributed so their sum equals the problem’s `total_marks` (with 2-decimal rounding).

## 5) Images in problem descriptions

Admins can insert images into problem descriptions using the “Insert Image” button in the problem editor.

Uploaded images are stored in:
- `coding-contest/static/problem_images/`

## 6) Importing problem packs (scripts)

This repo ships with an example pack in `round1_full_pack_optionA_solutions/`:

```
round1_full_pack_optionA_solutions/
  E1_Palindrome_Checker/
    description.txt
    testcases.txt
    Solution/
    starter_code/
  ...
  json_output/
```

There are two main workflows:

### Workflow A: Direct folder import (one-shot contest)

`create_shattered_syntax_contest.py` creates a contest and imports the bundled pack directly from the folder structure.

From repo root:
```bash
python create_shattered_syntax_contest.py
```

Notes:
- It reads `description.txt`, `testcases.txt`, and per-language code files.
- It uses `coding-contest/config.py` for the database path (`DB_PATH` / `DB_NAME`).

### Workflow B: JSON pipeline (edit + import/update)

1) Convert a pack to JSON:
```bash
python batch_convert_to_json.py round1_full_pack_optionA_solutions/
```
This writes individual JSON files to `round1_full_pack_optionA_solutions/json_output/`.

2) Import JSON into the platform DB:
```bash
python import_questions_to_db.py round1_full_pack_optionA_solutions/json_output/ "My Contest Name"
```

3) Update an existing contest (match by problem title within the contest):
```bash
python import_questions_to_db.py --update round1_full_pack_optionA_solutions/json_output/ "My Contest Name"
```

### JSON schema (what the importer expects)

Each JSON file follows the structure used by `import_questions_to_db.py`:

- Problem fields: `title`, `description`, `input_format`, `output_format`, `constraints`, `total_marks`, `problem_mode`, `problem_type`, `folder_name`
- `test_cases[]`: items with:
  - `type`: `Sample` or `Hidden`
  - `points`: `0` / numeric / `"auto"`
  - `input`, `output`
- `solutions`: code by language key (`python`, `cpp`, `java`, `c`)
- `starter_code`: starter code by language key

Importer notes:
- For `points: "auto"`, hidden test case points are computed as `total_marks // hidden_count`.
- If you need exact fractional distribution, use the admin upload path (it uses 2-decimal redistribution) or set explicit points per test case in JSON.

## 7) Verifying solution packs

To quickly verify the bundled pack’s **Python** solutions against `testcases.txt`:
```bash
python verify_all_solutions.py
```

This script:
- Finds `Solution/Solution.py` in each problem folder
- Runs each test case from `testcases.txt`
- Reports pass/fail and a summary
