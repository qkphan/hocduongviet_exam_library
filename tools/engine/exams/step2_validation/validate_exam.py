import sys
from base_validator import validate_json, ValidationErrorReport

SCHEMA_PATH = "tools/schema/exams/exam.schema.json"


def main(exam_path):
    try:
        validate_json(exam_path, SCHEMA_PATH)
        print("PASS: library exam schema")
    except ValidationErrorReport as e:
        print("FAIL: library exam schema")
        for err in e.errors:
            print(f"- {err['path']}: {err['message']}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_exam.py <exam.json>")
        sys.exit(2)

    main(sys.argv[1])
