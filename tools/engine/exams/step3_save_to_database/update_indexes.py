import json
import sys
from pathlib import Path
from datetime import datetime, timezone


RAW_INDEX_PATH = Path("raw_database/index.json")
LIB_INDEX_PATH = Path("hocduongviet_library/index.json")


def load_json(path: Path, default):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def update_raw_index(raw_exam_uid, library_exam_uid):
    index = load_json(RAW_INDEX_PATH, {"raw_exams": []})

    # tránh duplicate
    for entry in index["raw_exams"]:
        if entry["raw_exam_uid"] == raw_exam_uid:
            entry["linked_library_exam_uid"] = library_exam_uid
            entry["status"] = "PROMOTED"
            entry["updated_at"] = utc_now()
            save_json(RAW_INDEX_PATH, index)
            return

    # nếu chưa tồn tại
    index["raw_exams"].append({
        "raw_exam_uid": raw_exam_uid,
        "linked_library_exam_uid": library_exam_uid,
        "status": "PROMOTED",
        "created_at": utc_now(),
        "updated_at": utc_now()
    })

    save_json(RAW_INDEX_PATH, index)


def update_library_index(library_exam_uid):
    index = load_json(LIB_INDEX_PATH, {"library_exams": []})

    # không thêm trùng
    for entry in index["library_exams"]:
        if entry["library_exam_uid"] == library_exam_uid:
            entry["updated_at"] = utc_now()
            save_json(LIB_INDEX_PATH, index)
            return

    index["library_exams"].append({
        "library_exam_uid": library_exam_uid,
        "status": "ACTIVE",
        "published_at": utc_now()
    })

    save_json(LIB_INDEX_PATH, index)


def main(raw_exam_uid, library_exam_uid):
    update_raw_index(raw_exam_uid, library_exam_uid)
    update_library_index(library_exam_uid)

    print("✓ Indexes updated")
    print(f"  - raw_exam_uid: {raw_exam_uid}")
    print(f"  - library_exam_uid: {library_exam_uid}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: update_indexes.py <raw_exam_uid> <library_exam_uid>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
