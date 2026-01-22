# tools/engine/exams/step1_preparation/ingest_raw_exam.py

import json
import sys
import uuid
import os
from datetime import datetime

RAW_DB_ROOT = "raw_database"
VALID_SOURCES = {"ui", "ai", "imported"}


# -----------------------
# Utils
# -----------------------
def now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def abort(msg):
    print(f"[INGEST ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


# -----------------------
# Main ingest logic
# -----------------------
def ingest(raw_exam_path: str, source: str) -> str:
    if source not in VALID_SOURCES:
        abort(f"Invalid source '{source}', must be one of {VALID_SOURCES}")

    if not os.path.isfile(raw_exam_path):
        abort(f"File not found: {raw_exam_path}")

    # Load JSON
    try:
        with open(raw_exam_path, "r", encoding="utf-8") as f:
            exam = json.load(f)
    except Exception as e:
        abort(f"Invalid JSON: {e}")

    # Generate UID
    raw_exam_uid = f"raw_{uuid.uuid4()}"

    # Backup original meta if exists
    if "meta" in exam:
        exam["_original_meta"] = exam["meta"]

    # Normalize meta (pipeline authority)
    exam["meta"] = {
        "raw_exam_uid": raw_exam_uid,
        "source": source,
        "ingested_at": now_iso(),
        "status": "INGESTED",
        "version": 1,
    }

    # Time-based folder
    now = datetime.utcnow()
    year = f"{now.year:04d}"
    month = f"{now.month:02d}"

    base_dir = os.path.join(
        RAW_DB_ROOT,
        "exams",
        source,
        year,
        month,
        raw_exam_uid,
    )

    ensure_dir(base_dir)

    # Save v1.json
    v1_path = os.path.join(base_dir, "v1.json")
    with open(v1_path, "w", encoding="utf-8") as f:
        json.dump(exam, f, ensure_ascii=False, indent=2)

    # Create history.json
    history = {
        "raw_exam_uid": raw_exam_uid,
        "events": [
            {
                "event": "INGEST",
                "source": source,
                "time": now_iso(),
                "detail": f"Ingested from {raw_exam_path}",
            }
        ],
    }

    history_path = os.path.join(base_dir, "history.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return raw_exam_uid


# -----------------------
# CLI entry
# -----------------------
if __name__ == "__main__":
    if len(sys.argv) != 3:
        abort("Usage: ingest_raw_exam.py <raw_exam.json> <ui|ai|imported>")

    raw_exam_path = sys.argv[1]
    source = sys.argv[2]

    uid = ingest(raw_exam_path, source)

    # IMPORTANT: print UID only (for GitHub Actions)
    print(uid)
