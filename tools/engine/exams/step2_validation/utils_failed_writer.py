import json
from pathlib import Path
from datetime import datetime
import shutil


RAW_DATABASE_ROOT = Path("raw_database")
FAILED_ROOT = RAW_DATABASE_ROOT / "failed"


def now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def write_failed_exam(
    raw_exam_path: Path,
    raw_exam_uid: str,
    validation_report: dict,
):
    """
    Ghi exam FAILED vào raw_database/failed/<raw_exam_uid>/
    """

    failed_dir = FAILED_ROOT / raw_exam_uid
    failed_dir.mkdir(parents=True, exist_ok=True)

    # 1️⃣ copy raw exam (v1.json → raw.json)
    raw_target = failed_dir / "raw.json"
    shutil.copy(raw_exam_path, raw_target)

    # 2️⃣ ghi validation_report.json
    report_path = failed_dir / "validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(validation_report, f, ensure_ascii=False, indent=2)

    # 3️⃣ ghi meta.json
    meta = {
        "raw_exam_uid": raw_exam_uid,
        "status": "FAILED",
        "failed_at": now_iso(),
        "reason": "schema or logic validation failed",
    }

    meta_path = failed_dir / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return failed_dir
