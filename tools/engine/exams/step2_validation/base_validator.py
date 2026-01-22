import json
from jsonschema import Draft7Validator


class ValidationErrorReport(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("JSON validation failed")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_json(instance_path: str, schema_path: str) -> None:
    instance = load_json(instance_path)
    schema = load_json(schema_path)

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)

    if errors:
        report = []
        for err in errors:
            report.append({
                "path": "/".join([str(p) for p in err.path]),
                "message": err.message
            })
        raise ValidationErrorReport(report)
