import sys
from base_validator import validate_json, ValidationErrorReport

SCHEMA_PATH = "tools/schema/db/raw_index.schema.json"


def main(index_path):
    try:
        validate_json(index_path, SCHEMA_PATH)
        print("PASS: raw_database index")
    except ValidationErrorReport as e:
        print("FAIL: raw_database index")
        for err in e.errors:
            print(f"- {err['path']}: {err['message']}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_raw_index.py <index.json>")
        sys.exit(2)

    main(sys.argv[1])
