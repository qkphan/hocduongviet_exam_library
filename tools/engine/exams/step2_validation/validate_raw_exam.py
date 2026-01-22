import json
import sys
from pathlib import Path
from jsonschema import Draft7Validator
from utils_failed_writer import write_failed_exam

# ===============================
# CONSTANTS
# ===============================
RAW_EXAMS_ROOT = Path("raw_database/exams")
SCHEMA_PATH = Path("tools/schema/exams/raw_exam.schema.json")

# ===============================
# UTILS
# ===============================
def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_schema(data: dict):
    schema = load_json(SCHEMA_PATH)
    validator = Draft7Validator(schema)
    return [e.message for e in validator.iter_errors(data)]

def validate_logic(data: dict):
    errors = []
    warnings = []

    exam = data.get("exam", {})
    questions = exam.get("questions", [])

    if not questions:
        errors.append("Exam must contain at least one question")
        return errors, warnings

    for i, q in enumerate(questions, start=1):
        qid = q.get("id", f"Q{i}")
        qtype = q.get("type")

        if not qtype:
            errors.append(f"{qid}: missing question type")
            continue

        if qtype == "mcq":
            options = q.get("options", [])
            if len(options) < 4:
                errors.append(f"{qid}: MCQ must have at least 4 options")

            if q.get("correct") is None:
                errors.append(f"{qid}: MCQ missing correct answer")

        if "cognitive" not in q:
            warnings.append(f"{qid}: missing cognitive level")

        if "maps_to" not in q:
            warnings.append(f"{qid}: missing knowledge/skill mapping")

    return errors, warnings

# ===============================
# MAIN
# ===============================
def main():
    if not RAW_EXAMS_ROOT.exists():
        print("❌ raw_database/exams not found")
        return 1

    raw_files = sorted(RAW_EXAMS_ROOT.glob("**/v*.json"))
    if not raw_files:
        print("❌ No raw exam files found")
        return 1

    overall_failed = False

    for raw_exam_path in raw_files:
        print(f"\n🔍 Validating {raw_exam_path}")

        fs_uid = raw_exam_path.parent.name  # raw_exam_uid từ folder

        # -----------------------
        # Stage 1: Load JSON
        # -----------------------
        try:
            data = load_json(raw_exam_path)
        except Exception as e:
            write_failed_exam(
                raw_exam_path=raw_exam_path,
                raw_exam_uid=fs_uid,
                validation_report={
                    "stage": "load",
                    "error": str(e),
                },
            )
            print("❌ FAILED (load)")
            overall_failed = True
            continue

        json_uid = data.get("meta", {}).get("raw_exam_uid")

        # -----------------------
        # Stage 2: UID consistency
        # -----------------------
        if json_uid != fs_uid:
            write_failed_exam(
                raw_exam_path=raw_exam_path,
                raw_exam_uid=fs_uid,
                validation_report={
                    "stage": "uid_mismatch",
                    "filesystem_uid": fs_uid,
                    "json_uid": json_uid,
                },
            )
            print("❌ FAILED (uid mismatch)")
            overall_failed = True
            continue

        # -----------------------
        # Stage 3: Schema
        # -----------------------
        schema_errors = validate_schema(data)
        if schema_errors:
            write_failed_exam(
                raw_exam_path=raw_exam_path,
                raw_exam_uid=fs_uid,
                validation_report={
                    "stage": "schema",
                    "schema_errors": schema_errors,
                },
            )
            print("❌ FAILED (schema)")
            overall_failed = True
            continue

        # -----------------------
        # Stage 4: Logic
        # -----------------------
        logic_errors, warnings = validate_logic(data)
        if logic_errors:
            write_failed_exam(
                raw_exam_path=raw_exam_path,
                raw_exam_uid=fs_uid,
                validation_report={
                    "stage": "logic",
                    "logic_errors": logic_errors,
                    "warnings": warnings,
                },
            )
            print("❌ FAILED (logic)")
            overall_failed = True
            continue

        print("✅ PASSED")

    return 1 if overall_failed else 0


if __name__ == "__main__":
    sys.exit(main())
