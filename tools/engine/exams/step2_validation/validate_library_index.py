# import json
# import sys
# from pathlib import Path
# from jsonschema import Draft7Validator

# SCHEMA_PATH = Path("tools/schema/exams/library_exam.schema.json")


# def main(library_exam_path):
#     with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
#         schema = json.load(f)

#     with open(library_exam_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     validator = Draft7Validator(schema)
#     errors = list(validator.iter_errors(data))

#     if errors:
#         for e in errors:
#             print("ERROR:", e.message)
#         return 1

#     print("LIBRARY EXAM VALIDATION: PASSED")
#     return 0


# if __name__ == "__main__":
#     sys.exit(main(sys.argv[1]))


import sys
from base_validator import validate_json, ValidationErrorReport

SCHEMA_PATH = "tools/schema/exams/library_exam.schema.json"

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
        print("Usage: validate_library_exam.py <library_exam.json>")
        sys.exit(2)

    main(sys.argv[1])

