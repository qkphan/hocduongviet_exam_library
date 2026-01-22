import json
import sys
from pathlib import Path
from jsonschema import Draft7Validator

SCHEMA_PATH = Path("tools/schema/exams/raw_exam.schema.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema(data):
    schema = load_json(SCHEMA_PATH)
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    return [e.message for e in errors]


def validate_logic(exam):
    errors = []
    warnings = []

    questions = exam["exam"]["questions"]

    for i, q in enumerate(questions, start=1):
        qid = q.get("id", f"Q{i}")

        # MCQ: phải có options >= 4
        if q["type"] == "mcq":
            options = q.get("options", [])
            if len(options) < 4:
                errors.append(f"{qid}: MCQ must have at least 4 options")

        # Cognitive khuyến nghị
        if "cognitive" not in q:
            warnings.append(f"{qid}: missing cognitive information")

        # Mapping khuyến nghị
        if "maps_to" not in q:
            warnings.append(f"{qid}: missing knowledge/skill mapping")

    return errors, warnings


def main():
    if not RAW_EXAMS_DIR.exists():
        print("❌ raw_exams/ directory not found")
        return 1

    raw_files = sorted(RAW_EXAMS_DIR.glob("raw_*.json"))

    if not raw_files:
        print("❌ No raw exam files found")
        return 1

    overall_status = "PASSED"
    reports = []

    for raw_exam_path in raw_files:
        print(f"🔍 Validating {raw_exam_path.name}")

        data = load_json(raw_exam_path)

        schema_errors = validate_schema(data)
        logic_errors, logic_warnings = validate_logic(data)

        status = "PASSED"
        if schema_errors or logic_errors:
            status = "FAILED"
            overall_status = "FAILED"

        report = {
            "raw_exam": raw_exam_path.name,
            "status": status,
            "schema_errors": schema_errors,
            "logic_errors": logic_errors,
            "warnings": logic_warnings,
        }

        report_path = raw_exam_path.with_suffix(".validation.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        reports.append(report)

    print(f"\nFINAL STATUS: {overall_status}")
    return 0 if overall_status == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())

