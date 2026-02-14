#!/usr/bin/env python3
"""
Generate Word-compatible documents from JSON question packs.

Why RTF?
- No external dependencies (no python-docx / pandoc needed).
- Opens cleanly in Microsoft Word / Google Docs / LibreOffice.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional


DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2, "unknown": 3}

LANG_ORDER = ["python", "cpp", "java", "c"]
LANG_LABEL = {"python": "Python", "cpp": "C++", "java": "Java", "c": "C"}


@dataclass(frozen=True)
class Question:
    title: str
    folder_name: str
    contest: str
    problem_type: str
    problem_mode: str
    total_marks: str
    constraints: str
    description: str
    input_format: str
    output_format: str
    test_cases: list[dict[str, Any]]
    starter_code: dict[str, Any]
    solutions: dict[str, Any]
    source_file: Path


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def infer_difficulty(folder_name: str, total_marks: str = "") -> str:
    """
    Determine difficulty primarily from folder_name prefix (E/M/H).
    Fallback: infer from marks if possible (<=10 easy, <=20 medium, else hard).
    """
    if folder_name:
        ch = folder_name[0].upper()
        if ch == "E":
            return "easy"
        if ch == "M":
            return "medium"
        if ch == "H":
            return "hard"

    try:
        marks = int(str(total_marks).strip())
    except ValueError:
        return "unknown"

    if marks <= 10:
        return "easy"
    if marks <= 20:
        return "medium"
    return "hard"


def infer_order_number(folder_name: str) -> int:
    """
    Extract a numeric order from folder_name like:
      E1_Palindrome_Checker -> 1
      M2_Two_Sum -> 2
    If absent (e.g., E_Butterfly_Pattern_Star), returns a large number.
    """
    if not folder_name:
        return 10**9
    match = re.match(r"^[EMH](\d+)_", folder_name, re.IGNORECASE)
    if not match:
        return 10**9
    try:
        return int(match.group(1))
    except ValueError:
        return 10**9


def sanitize_filename(name: str) -> str:
    safe = name.strip()
    safe = re.sub(r"[\\/:*?\"<>|]+", "-", safe)
    safe = re.sub(r"\s+", " ", safe).strip()
    return safe or "questions"


def load_questions_from_dir(json_dir: Path) -> list[Question]:
    if not json_dir.exists() or not json_dir.is_dir():
        raise FileNotFoundError(f"JSON directory not found: {json_dir}")

    questions: list[Question] = []
    for json_file in sorted(json_dir.glob("*.json")):
        if not json_file.is_file():
            continue
        with json_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object in {json_file}, got: {type(data).__name__}")

        questions.append(
            Question(
                title=_as_str(data.get("title")),
                folder_name=_as_str(data.get("folder_name")),
                contest=_as_str(data.get("contest")),
                problem_type=_as_str(data.get("problem_type")),
                problem_mode=_as_str(data.get("problem_mode")),
                total_marks=_as_str(data.get("total_marks")),
                constraints=_as_str(data.get("constraints")),
                description=_as_str(data.get("description")),
                input_format=_as_str(data.get("input_format")),
                output_format=_as_str(data.get("output_format")),
                test_cases=list(data.get("test_cases") or []),
                starter_code=dict(data.get("starter_code") or {}),
                solutions=dict(data.get("solutions") or {}),
                source_file=json_file,
            )
        )

    return questions


def most_common(values: Iterable[str]) -> str:
    counts: dict[str, int] = {}
    for v in values:
        v = v.strip()
        if not v:
            continue
        counts[v] = counts.get(v, 0) + 1
    if not counts:
        return ""
    return max(counts.items(), key=lambda kv: kv[1])[0]


def rtf_escape(text: str) -> str:
    """
    Escape text for RTF. Supports basic Unicode via \\uN? sequences.
    """
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    out: list[str] = []
    for ch in text:
        code = ord(ch)
        if ch == "\\":
            out.append(r"\\")
        elif ch == "{":
            out.append(r"\{")
        elif ch == "}":
            out.append(r"\}")
        elif ch == "\n":
            out.append(r"\line ")
        elif ch == "\t":
            out.append(r"\tab ")
        elif code < 128:
            out.append(ch)
        else:
            # RTF uses signed 16-bit values for \u
            signed = code if code <= 0x7FFF else code - 0x10000
            out.append(rf"\u{signed}?")
    return "".join(out)


def rtf_paragraph(text: str) -> str:
    return f"{rtf_escape(text)}\\par\n"


def rtf_label_value(label: str, value: str) -> str:
    if not value.strip():
        return ""
    return f"\\b {rtf_escape(label)}:\\b0 {rtf_escape(value)}\\par\n"


def rtf_code_block(text: str) -> str:
    if not text.strip():
        return ""
    escaped = rtf_escape(text)
    return "{\\f1\\fs20 " + escaped + "}\\par\n"


def select_sample_tests(test_cases: list[dict[str, Any]], max_samples: int) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for tc in test_cases:
        tc_type = _as_str(tc.get("type")).strip().lower()
        is_sample = tc.get("is_sample")
        if tc_type == "sample" or is_sample is True:
            samples.append(tc)
    return samples[: max(0, max_samples)]


def count_hidden_tests(test_cases: list[dict[str, Any]]) -> int:
    hidden = 0
    for tc in test_cases:
        tc_type = _as_str(tc.get("type")).strip().lower()
        is_sample = tc.get("is_sample")
        if tc_type == "sample" or is_sample is True:
            continue
        hidden += 1
    return hidden


def ordered_languages(language_map: dict[str, Any]) -> list[str]:
    keys = list(language_map.keys())
    ordered: list[str] = []
    for lang in LANG_ORDER:
        if lang in language_map:
            ordered.append(lang)
    for lang in sorted(keys):
        if lang not in ordered:
            ordered.append(lang)
    return ordered


def question_sort_key(q: Question) -> tuple[int, int, str]:
    difficulty = infer_difficulty(q.folder_name, q.total_marks)
    difficulty_rank = DIFFICULTY_ORDER.get(difficulty, DIFFICULTY_ORDER["unknown"])
    order_num = infer_order_number(q.folder_name)
    return (difficulty_rank, order_num, q.title.lower())


def generate_rtf_document(
    *,
    contest_title: str,
    questions: list[Question],
    output_path: Path,
    max_sample_tests: int = 3,
) -> None:
    questions_sorted = sorted(questions, key=question_sort_key)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    total_questions = len(questions_sorted)
    total_marks_sum = 0
    for q in questions_sorted:
        try:
            total_marks_sum += int(str(q.total_marks).strip())
        except ValueError:
            pass

    parts: list[str] = []
    parts.append(r"{\rtf1\ansi\deff0")
    parts.append(r"{\fonttbl{\f0 Calibri;}{\f1 Consolas;}}")
    parts.append(r"\paperw12240\paperh15840\margl1440\margr1440\margt1440\margb1440")
    parts.append("\n")

    # Cover
    parts.append(rf"\fs52\b {rtf_escape(contest_title)}\b0\fs24\par" + "\n")
    parts.append(rf"\fs28\b Question Set\b0\fs24\par" + "\n")
    parts.append(rtf_paragraph(f"Generated: {generated_at}"))
    if total_marks_sum:
        parts.append(rtf_paragraph(f"Questions: {total_questions}    Total Marks: {total_marks_sum}"))
    else:
        parts.append(rtf_paragraph(f"Questions: {total_questions}"))
    parts.append(r"\par" + "\n")

    # Contents (manual)
    parts.append(rf"\fs32\b Contents\b0\fs24\par" + "\n")
    for idx, q in enumerate(questions_sorted, start=1):
        difficulty = infer_difficulty(q.folder_name, q.total_marks).capitalize()
        marks = str(q.total_marks).strip()
        suffix = []
        if marks:
            suffix.append(f"{marks} marks")
        if difficulty != "Unknown":
            suffix.append(difficulty)
        suffix_str = f" ({', '.join(suffix)})" if suffix else ""
        parts.append(rtf_paragraph(f"{idx}. {q.title}{suffix_str}"))

    parts.append(r"\page" + "\n")

    # Questions
    for idx, q in enumerate(questions_sorted, start=1):
        if idx != 1:
            parts.append(r"\page" + "\n")

        difficulty = infer_difficulty(q.folder_name, q.total_marks)
        sample_tests = select_sample_tests(q.test_cases, max_sample_tests)

        parts.append(rf"\fs36\b Q{idx}. {rtf_escape(q.title)}\b0\fs24\par" + "\n")
        parts.append(rtf_label_value("Contest", str(q.contest).strip()))
        parts.append(rtf_label_value("Folder Name", str(q.folder_name).strip()))
        parts.append(rtf_label_value("Difficulty", difficulty.capitalize() if difficulty != "unknown" else "Unknown"))
        parts.append(rtf_label_value("Problem Type", str(q.problem_type).strip()))
        parts.append(rtf_label_value("Problem Mode", str(q.problem_mode).strip()))
        parts.append(rtf_label_value("Total Marks", str(q.total_marks).strip()))

        parts.append(r"\par" + "\n")

        parts.append(rtf_label_value("Constraints", q.constraints))
        parts.append(rtf_label_value("Description", q.description))
        parts.append(rtf_label_value("Input Format", q.input_format))
        parts.append(rtf_label_value("Output Format", q.output_format))

        # Test cases (ALL)
        if q.test_cases:
            parts.append(r"\par" + "\n")
            parts.append(rf"\fs28\b Test Cases\b0\fs24\par" + "\n")

            for tc_index, tc in enumerate(q.test_cases, start=1):
                tc_type = _as_str(tc.get("type")).strip() or "Test"
                tc_points = _as_str(tc.get("points")).strip()
                tc_in = _as_str(tc.get("input"))
                tc_out = _as_str(tc.get("output"))

                header_suffix = []
                if tc_type:
                    header_suffix.append(tc_type)
                if tc_points:
                    header_suffix.append(f"{tc_points} points")
                suffix_str = f" ({', '.join(header_suffix)})" if header_suffix else ""

                parts.append(rf"\b Test Case {tc_index}{rtf_escape(suffix_str)}\b0\par" + "\n")
                parts.append(rtf_paragraph("Input:"))
                parts.append(rtf_code_block(tc_in))
                parts.append(rtf_paragraph("Output:"))
                parts.append(rtf_code_block(tc_out))
                parts.append(r"\par" + "\n")

        # Starter code (ALL)
        starter_map = q.starter_code
        if starter_map:
            parts.append(r"\par" + "\n")
            parts.append(rf"\fs28\b Starter Code\b0\fs24\par" + "\n")
            for lang in ordered_languages(starter_map):
                code = _as_str(starter_map.get(lang))
                label = LANG_LABEL.get(lang, lang)
                parts.append(rf"\b {rtf_escape(label)}\b0\par" + "\n")
                parts.append(rtf_code_block(code))
                parts.append(r"\par" + "\n")

        # Solutions (ALL)
        solutions_map = q.solutions
        if solutions_map:
            parts.append(r"\par" + "\n")
            parts.append(rf"\fs28\b Solutions\b0\fs24\par" + "\n")
            for lang in ordered_languages(solutions_map):
                code = _as_str(solutions_map.get(lang))
                label = LANG_LABEL.get(lang, lang)
                parts.append(rf"\b {rtf_escape(label)}\b0\par" + "\n")
                parts.append(rtf_code_block(code))
                parts.append(r"\par" + "\n")

        parts.append(r"\par" + "\n")

    parts.append("}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(parts), encoding="utf-8")


def generate_for_pack(
    *,
    json_dir: Path,
    output_dir: Path,
    title_override: Optional[str],
    samples: int,
) -> Path:
    questions = load_questions_from_dir(json_dir)
    contest_from_json = most_common(q.contest for q in questions)
    contest_title = title_override.strip() if title_override and title_override.strip() else contest_from_json or json_dir.name

    out_name = sanitize_filename(contest_title) + ".rtf"
    out_path = output_dir / out_name

    generate_rtf_document(
        contest_title=contest_title,
        questions=questions,
        output_path=out_path,
        max_sample_tests=samples,
    )
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Word-compatible RTF documents from JSON question packs.")
    parser.add_argument(
        "--output-dir",
        default="documents",
        help="Directory to write generated documents (default: documents/).",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=3,
        help="Max sample test cases per question to include (default: 3). Hidden tests are not included.",
    )
    parser.add_argument(
        "--pack",
        action="append",
        nargs="+",
        metavar=("JSON_DIR", "TITLE_OVERRIDE"),
        help=(
            "Pack definition: JSON_DIR [TITLE_OVERRIDE]. "
            "Repeat --pack for multiple packs. If omitted, generates for the two known packs in this repo."
        ),
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    samples = max(0, int(args.samples))

    jobs: list[tuple[Path, Optional[str]]] = []
    if args.pack:
        for pack_args in args.pack:
            if not pack_args:
                continue
            json_dir = Path(pack_args[0])
            title_override = pack_args[1] if len(pack_args) > 1 else None
            jobs.append((json_dir, title_override))
    else:
        # Defaults for this repo
        jobs = [
            (Path("coding_round2_struct/json_output"), "The Architect's Blueprint - Round 2 (Coding)"),
            (Path("round1_full_pack_optionA_solutions/json_output"), None),
        ]

    written: list[Path] = []
    for json_dir, title_override in jobs:
        out_path = generate_for_pack(
            json_dir=json_dir,
            output_dir=output_dir,
            title_override=title_override,
            samples=samples,
        )
        written.append(out_path)

    print("Generated documents:")
    for p in written:
        print(f"- {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
