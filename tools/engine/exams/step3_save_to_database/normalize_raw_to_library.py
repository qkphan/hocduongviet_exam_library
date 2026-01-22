import json
import uuid
from datetime import datetime
from collections import defaultdict
from pathlib import Path


def normalize(raw_exam_path, output_path):
    with open(raw_exam_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    questions = raw["exam"]["questions"]

    cognitive_sum = defaultdict(float)
    total_weight = 0.0

    for q in questions:
        cog = q.get("cognitive")
        if not cog:
            continue
        level = cog["level"]
        weight = cog.get("weight", 1.0)
        cognitive_sum[level] += weight
        total_weight += weight

    cognitive_summary = {
        k: round(v / total_weight * 100, 2)
        for k, v in cognitive_sum.items()
    }

    library_exam = {
        "meta": {
            "library_exam_uid": str(uuid.uuid4()),
            "raw_exam_uid": raw["meta"]["raw_exam_uid"],
            "validated_at": datetime.utcnow().isoformat() + "Z",
            "status": "LIBRARY",
            "cognitive_summary": cognitive_summary,
        },
        "exam": raw["exam"]
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(library_exam, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import sys
    normalize(sys.argv[1], sys.argv[2])
