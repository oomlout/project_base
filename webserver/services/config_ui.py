from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_MANUAL_FIELDS = [
    {
        "name": "content",
        "label": "Content",
        "help_text": "One item per line.",
    },
    {
        "name": "taxonomy",
        "label": "Taxonomy",
        "help_text": "One item per line.",
    },
]

DEFAULT_SEARCH_FIELDS = [
    {
        "name": "id",
        "label": "ID",
    },
    {
        "name": "name",
        "label": "Name",
    },
    {
        "name": "name_proper",
        "label": "Proper Name",
    },
    {
        "name": "taxonomy",
        "label": "Taxonomy",
    },
    {
        "name": "working_manual",
        "label": "Manual Details",
    },
]

DEFAULT_UI_CONFIG = {
    "preview_priority": [
        "3dpr.png",
        "3dpr.jpg",
        "3dpr.webp",
        "label_oomp.svg",
        "initial_generated_icon.png",
        "3dpr.svg",
        "*.png",
        "*.svg",
        "*.jpg",
        "*.jpeg",
        "*.webp",
        "*.gif",
    ],
    "manual_fields": DEFAULT_MANUAL_FIELDS,
    "search_fields": {
        "available": DEFAULT_SEARCH_FIELDS,
        "default_selected": ["id"],
    },
}


def _copy_default_manual_fields() -> list[dict[str, str]]:
    return [dict(field) for field in DEFAULT_MANUAL_FIELDS]


def _copy_default_search_fields() -> list[dict[str, str]]:
    return [dict(field) for field in DEFAULT_SEARCH_FIELDS]


def _humanize_field_name(name: str) -> str:
    return name.replace("_", " ").strip().title()


def _normalize_manual_fields(raw_fields: Any) -> list[dict[str, str]]:
    if not isinstance(raw_fields, list):
        return _copy_default_manual_fields()

    normalized: list[dict[str, str]] = []
    seen_names: set[str] = set()
    for entry in raw_fields:
        if isinstance(entry, dict):
            name = str(entry.get("name", "")).strip()
            if not name or name in seen_names:
                continue
            normalized.append(
                {
                    "name": name,
                    "label": str(entry.get("label") or _humanize_field_name(name)),
                    "help_text": str(entry.get("help_text") or "One item per line."),
                }
            )
            seen_names.add(name)
            continue

        if isinstance(entry, str):
            name = entry.strip()
            if not name or name in seen_names:
                continue
            normalized.append(
                {
                    "name": name,
                    "label": _humanize_field_name(name),
                    "help_text": "One item per line.",
                }
            )
            seen_names.add(name)

    if not normalized:
        return _copy_default_manual_fields()
    return normalized


def _normalize_search_fields(raw_search_fields: Any) -> dict[str, Any]:
    default_available = _copy_default_search_fields()
    default_selected = ["id"]
    config = {
        "available": default_available,
        "default_selected": list(default_selected),
    }
    if not isinstance(raw_search_fields, dict):
        return config

    raw_available = raw_search_fields.get("available", default_available)
    available: list[dict[str, str]] = []
    seen_names: set[str] = set()
    if isinstance(raw_available, list):
        for entry in raw_available:
            if isinstance(entry, dict):
                name = str(entry.get("name", "")).strip()
                if not name or name in seen_names:
                    continue
                available.append(
                    {
                        "name": name,
                        "label": str(entry.get("label") or _humanize_field_name(name)),
                    }
                )
                seen_names.add(name)
                continue
            if isinstance(entry, str):
                name = entry.strip()
                if not name or name in seen_names:
                    continue
                available.append(
                    {
                        "name": name,
                        "label": _humanize_field_name(name),
                    }
                )
                seen_names.add(name)

    if not available:
        available = default_available
        seen_names = {field["name"] for field in available}

    raw_default_selected = raw_search_fields.get("default_selected", default_selected)
    selected: list[str] = []
    if isinstance(raw_default_selected, list):
        for entry in raw_default_selected:
            name = str(entry).strip()
            if name and name in seen_names and name not in selected:
                selected.append(name)

    if not selected:
        selected = [field["name"] for field in available if field["name"] == "id"] or [available[0]["name"]]

    return {
        "available": available,
        "default_selected": selected,
    }


def load_ui_config(config_path: Path | str) -> dict[str, Any]:
    path = Path(config_path)
    config = {
        "preview_priority": list(DEFAULT_UI_CONFIG["preview_priority"]),
        "manual_fields": _copy_default_manual_fields(),
        "search_fields": _normalize_search_fields(DEFAULT_UI_CONFIG["search_fields"]),
    }
    if not path.exists():
        return config

    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}

    if not isinstance(loaded, dict):
        return config

    preview_priority = loaded.get("preview_priority", config["preview_priority"])
    if not isinstance(preview_priority, list):
        preview_priority = config["preview_priority"]

    normalized = []
    for entry in preview_priority:
        if entry is None:
            continue
        text = str(entry).strip()
        if text:
            normalized.append(text)

    if normalized:
        config["preview_priority"] = normalized

    config["manual_fields"] = _normalize_manual_fields(
        loaded.get("manual_fields", config["manual_fields"])
    )
    config["search_fields"] = _normalize_search_fields(
        loaded.get("search_fields", config["search_fields"])
    )

    return config
