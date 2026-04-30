from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

import yaml

from webserver.config_app import TAXONOMY_FIELD_COUNT, taxonomy_key


def list_part_directories(parts_dir: Path) -> dict[str, Path]:
    parts_dir = Path(parts_dir)
    if not parts_dir.exists():
        return {}
    return {
        child.name: child
        for child in sorted(parts_dir.iterdir(), key=lambda item: item.name.lower())
        if child.is_dir()
    }


def build_directory_signature(part_dir: Path) -> tuple[int, int, int]:
    part_dir = Path(part_dir)
    file_count = 0
    total_size = 0
    newest_mtime = 0
    for file_path in part_dir.rglob("*"):
        if not file_path.is_file():
            continue
        stat = file_path.stat()
        file_count += 1
        total_size += int(stat.st_size)
        newest_mtime = max(newest_mtime, int(stat.st_mtime_ns))
    return (file_count, total_size, newest_mtime)


def _humanize_slug(value: str) -> str:
    return value.replace("_", " ").strip().title()


def _build_taxonomy_breadcrumb(taxonomy_pairs: list[dict[str, Any]]) -> str:
    return " / ".join(pair["label"] for pair in taxonomy_pairs)


def _taxonomy_pairs(data: dict[str, Any]) -> list[dict[str, Any]]:
    pairs = []
    for index in range(1, TAXONOMY_FIELD_COUNT + 1):
        key = taxonomy_key(index)
        value = data.get(key, "")
        if value in (None, ""):
            continue
        pairs.append(
            {
                "key": key,
                "index": index,
                "value": str(value),
                "label": _humanize_slug(str(value)),
            }
        )
    return pairs


def _build_search_text(record: dict[str, Any]) -> str:
    values = [
        record.get("id", ""),
        record.get("name", ""),
        record.get("name_space", ""),
        record.get("name_proper", ""),
    ]
    values.extend(pair["value"] for pair in record["taxonomy_pairs"])
    values.extend(pair["label"] for pair in record["taxonomy_pairs"])
    for field_name, field_value in record.get("data", {}).items():
        if field_name.startswith("taxonomy_"):
            continue
        if isinstance(field_value, list):
            values.extend(str(item) for item in field_value if item not in (None, ""))
        elif field_value not in (None, ""):
            values.append(str(field_value))
    return " ".join(str(value) for value in values if value).lower()


def _search_field_text(field_name: str, record: dict[str, Any]) -> str:
    values: list[str] = []
    if field_name == "id":
        values.append(record.get("id", ""))
    elif field_name == "name":
        values.extend(
            [
                record.get("name", ""),
                record.get("name_space", ""),
            ]
        )
    elif field_name == "name_proper":
        values.append(record.get("name_proper", ""))
    elif field_name == "taxonomy":
        combined_taxonomy = record.get("data", {}).get("taxonomy", "")
        if isinstance(combined_taxonomy, list):
            values.extend(str(item) for item in combined_taxonomy if item not in (None, ""))
        elif combined_taxonomy not in (None, ""):
            values.append(str(combined_taxonomy))
        values.extend(pair["value"] for pair in record.get("taxonomy_pairs", []))
        values.extend(pair["label"] for pair in record.get("taxonomy_pairs", []))
        values.append(record.get("taxonomy_breadcrumb", ""))
    elif field_name == "working_manual":
        for manual_value in record.get("working_manual", {}).values():
            if isinstance(manual_value, list):
                values.extend(str(item) for item in manual_value if item not in (None, ""))
            elif manual_value not in (None, ""):
                values.append(str(manual_value))
    else:
        combined_value = record.get("data", {}).get(field_name, "")
        if isinstance(combined_value, list):
            values.extend(str(item) for item in combined_value if item not in (None, ""))
        elif combined_value not in (None, ""):
            values.append(str(combined_value))

    return " ".join(str(value) for value in values if value).lower()


def _build_search_index(record: dict[str, Any], search_field_names: list[str]) -> dict[str, str]:
    return {
        field_name: _search_field_text(field_name, record)
        for field_name in search_field_names
    }


def _list_part_files(part_dir: Path) -> list[dict[str, Any]]:
    files = []
    for file_path in sorted(part_dir.rglob("*")):
        if not file_path.is_file():
            continue
        relative_path = file_path.relative_to(part_dir).as_posix()
        files.append(
            {
                "name": file_path.name,
                "relative_path": relative_path,
                "suffix": file_path.suffix.lower(),
                "size": file_path.stat().st_size,
                "is_image": _is_image_file(relative_path),
            }
        )
    return files


def _is_image_file(relative_path: str) -> bool:
    suffix = Path(relative_path).suffix.lower()
    return suffix in {".png", ".svg", ".jpg", ".jpeg", ".webp", ".gif"}


def _pick_preview_file(
    files: list[dict[str, Any]],
    preview_priority: list[str] | None,
) -> str | None:
    if not files:
        return None

    image_files = [file for file in files if file["is_image"]]
    if not image_files:
        return None

    patterns = [pattern.strip() for pattern in (preview_priority or []) if str(pattern).strip()]
    for pattern in patterns:
        wildcard = any(char in pattern for char in "*?[]")
        for file in image_files:
            candidates = [file["relative_path"], file["name"]]
            if wildcard:
                if any(fnmatch.fnmatch(candidate.lower(), pattern.lower()) for candidate in candidates):
                    return file["relative_path"]
            else:
                if any(candidate.lower() == pattern.lower() for candidate in candidates):
                    return file["relative_path"]

    return image_files[0]["relative_path"]


def load_part_record(
    part_dir: Path,
    parts_dir: Path,
    preview_priority: list[str] | None = None,
    search_field_names: list[str] | None = None,
) -> dict[str, Any] | None:
    working_yaml = Path(part_dir) / "working.yaml"
    if not working_yaml.exists():
        return None
    with working_yaml.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        return None

    working_manual_path = Path(part_dir) / "working_manual.yaml"
    working_manual: dict[str, Any] = {}
    working_manual_error: str | None = None
    if working_manual_path.exists():
        try:
            with working_manual_path.open("r", encoding="utf-8") as handle:
                loaded_manual = yaml.safe_load(handle) or {}
        except Exception as exc:
            working_manual_error = str(exc)
        else:
            if isinstance(loaded_manual, dict):
                working_manual = loaded_manual
            else:
                working_manual_error = "working_manual.yaml must contain a YAML mapping."

    combined_data = dict(data)
    combined_data.update(working_manual)

    part_id = part_dir.name
    taxonomy_pairs = _taxonomy_pairs(combined_data)
    files = _list_part_files(part_dir)
    preview_file = _pick_preview_file(files, preview_priority)
    image_files = [file for file in files if _is_image_file(file["relative_path"])]
    record = {
        "id": part_id,
        "name": combined_data.get("name_proper") or combined_data.get("name") or _humanize_slug(part_id),
        "name_space": combined_data.get("name_space") or part_id.replace("_", " "),
        "name_proper": combined_data.get("name_proper") or _humanize_slug(part_id),
        "directory": combined_data.get("directory") or part_dir.relative_to(parts_dir.parent).as_posix(),
        "part_dir": str(part_dir),
        "relative_dir": part_dir.relative_to(parts_dir).as_posix(),
        "data": combined_data,
        "taxonomy_pairs": taxonomy_pairs,
        "taxonomy_values": {pair["key"]: pair["value"] for pair in taxonomy_pairs},
        "taxonomy_breadcrumb": _build_taxonomy_breadcrumb(taxonomy_pairs),
        "preview_file": preview_file,
        "files": files,
        "file_count": len(files),
        "image_count": len(image_files),
        "working_yaml": data,
        "working_manual": working_manual,
        "working_manual_exists": working_manual_path.exists(),
        "working_manual_error": working_manual_error,
        "signature": build_directory_signature(part_dir),
    }
    record["search_index_by_field"] = _build_search_index(record, list(search_field_names or ["id"]))
    record["search_text"] = _build_search_text(record)
    return record


def scan_parts(
    parts_dir: Path,
    preview_priority: list[str] | None = None,
    search_field_names: list[str] | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, tuple[int, int, int]], list[str]]:
    records: dict[str, dict[str, Any]] = {}
    signatures: dict[str, tuple[int, int, int]] = {}
    errors: list[str] = []
    for part_id, part_dir in list_part_directories(parts_dir).items():
        try:
            record = load_part_record(part_dir, parts_dir, preview_priority, search_field_names)
        except Exception as exc:
            errors.append(f"{part_id}: {exc}")
            continue
        if record is None:
            continue
        records[part_id] = record
        signatures[part_id] = record["signature"]
    return records, signatures, errors


def filter_parts(
    parts: list[dict[str, Any]],
    taxonomy_filters: dict[str, str],
    query: str = "",
    selected_search_fields: list[str] | None = None,
) -> list[dict[str, Any]]:
    active_query = query.strip().lower()
    active_fields = list(selected_search_fields or [])
    filtered = []
    for part in parts:
        include = True
        for key, value in taxonomy_filters.items():
            if not value:
                continue
            if part["taxonomy_values"].get(key) != value:
                include = False
                break
        if not include:
            continue
        if active_query:
            if active_fields:
                haystack = " ".join(
                    part.get("search_index_by_field", {}).get(field_name, "")
                    for field_name in active_fields
                )
            else:
                haystack = part.get("search_text", "")
            if active_query not in haystack:
                continue
        filtered.append(part)
    return sorted(filtered, key=lambda item: item["name"].lower())


def build_taxonomy_navigation(
    parts: list[dict[str, Any]],
    active_filters: dict[str, str],
) -> dict[str, Any]:
    selected_pairs = []
    for index in range(1, TAXONOMY_FIELD_COUNT + 1):
        key = taxonomy_key(index)
        value = active_filters.get(key, "")
        if not value:
            break
        selected_pairs.append(
            {"key": key, "index": index, "value": value, "label": _humanize_slug(value)}
        )

    parent_filters = {pair["key"]: pair["value"] for pair in selected_pairs}
    next_index = len(selected_pairs) + 1
    options = []
    if next_index <= TAXONOMY_FIELD_COUNT:
        counts: dict[str, int] = {}
        for part in parts:
            matches_parent = True
            for key, value in parent_filters.items():
                if part["taxonomy_values"].get(key) != value:
                    matches_parent = False
                    break
            if not matches_parent:
                continue
            next_value = part["taxonomy_values"].get(taxonomy_key(next_index), "")
            if not next_value:
                continue
            counts[next_value] = counts.get(next_value, 0) + 1
        options = [
            {
                "key": taxonomy_key(next_index),
                "value": value,
                "label": _humanize_slug(value),
                "count": count,
            }
            for value, count in sorted(counts.items(), key=lambda item: (item[0].lower(), item[1]))
        ]

    return {
        "selected": selected_pairs,
        "next_key": taxonomy_key(next_index) if next_index <= TAXONOMY_FIELD_COUNT else None,
        "next_index": next_index if next_index <= TAXONOMY_FIELD_COUNT else None,
        "options": options,
    }
