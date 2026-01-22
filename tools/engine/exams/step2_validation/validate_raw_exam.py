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


def main(raw_exam_path):
    data = load_json(raw_exam_path)

    schema_errors = validate_schema(data)
    logic_errors, logic_warnings = validate_logic(data)

    result = {
        "status": "PASSED",
        "schema_errors": schema_errors,
        "logic_errors": logic_errors,
        "warnings": logic_warnings,
    }

    if schema_errors or logic_errors:
        result["status"] = "FAILED"

    report_path = Path(raw_exam_path).with_name("validation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"VALIDATION STATUS: {result['status']}")
    return 0 if result["status"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
