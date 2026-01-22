import json
import sys
from pathlib import Path
from jsonschema import Draft7Validator

# ==============================
# CONSTANTS (PIPELINE CONTRACT)
# ==============================
RAW_DB_EXAMS_DIR = Path("raw_database/exams")
SCHEMA_PATH = Path("tools/schema/exams/raw_exam.schema.json")

# ==============================
# UTILS
# ==============================
def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def abort(msg):
    print(f"❌ {msg}", file=sys.stderr)
    return 1


# ==============================
# VALIDATORS
# ==============================
def validate_schema(data):
    schema = load_json(SCHEMA_PATH)
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    return [e.message for e in errors]


def validate_logic(exam):
    errors = []
    warnings = []

    exam_obj = exam.get("exam", {})
    questions = exam_obj.get("questions", [])

    for i, q in enumerate(questions, start=1):
        qid = q.get("id", f"Q{i}")

        # MCQ phải có >= 4 options
        if q.get("type") == "mcq":
            options = q.get("options", [])
            if len(options) < 4:
                errors.append(f"{qid}: MCQ must have at least 4 options")

        # Khuyến nghị metadata
        if "cognitive" not in q:
            warnings.append(f"{qid}: missing cognitive information")

        if "maps_to" not in q:
            warnings.append(f"{qid}: missing knowledge/skill mapping")

    return errors, warnings


# ==============================
# FILE DISCOVERY (KEY CHANGE)
# ==============================
def discover_ingested_exams():
    """
    Find all ingested raw exam versions (v*.json)
    Example path:
    raw_database/exams/ai/2026/01/raw_xxx/v1.json
    """
    if not RAW_DB_EXAMS_DIR.exists():
        return []

    return sorted(RAW_DB_EXAMS_DIR.glob("**/v*.json"))


# ==============================
# MAIN (CI ENTRYPOINT)
# ==============================
def main():
    raw_exam_files = discover_ingested_exams()

    if not raw_exam_files:
        return abort("No ingested raw exams found in raw_database/exams")

    overall_status = "PASSED"

    for exam_path in raw_exam_files:
        print(f"\n🔍 Validating {exam_path}")

        try:
            data = load_json(exam_path)
        except Exception as e:
            print(f"❌ Failed to load JSON: {e}")
            overall_status = "FAILED"
            continue

        schema_errors = validate_schema(data)
        logic_errors, logic_warnings = validate_logic(data)

        status = "PASSED"
        if schema_errors or logic_errors:
            status = "FAILED"
            overall_status = "FAILED"

        report = {
            "raw_exam_uid": data.get("meta", {}).get("raw_exam_uid"),
            "source": data.get("meta", {}).get("source"),
            "version": exam_path.name,
            "status": status,
            "schema_errors": schema_errors,
            "logic_errors": logic_errors,
            "warnings": logic_warnings,
        }

        report_path = exam_path.with_name("validation_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"➡️ {exam_path}: {status}")

    print(f"\nFINAL STATUS: {overall_status}")
    return 0 if overall_status == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())
