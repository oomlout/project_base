from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_DEFAULT_TAGS = ["id"] + [f"taxonomy_{i}" for i in range(1, 16)]

DEFAULT_QUICK_SUMMARY_CONFIG: dict[str, Any] = {
    "tags": list(_DEFAULT_TAGS),
}


def load_quick_summary_config(config_path: Path | str) -> dict[str, Any]:
    path = Path(config_path)
    config = {"tags": list(_DEFAULT_TAGS)}
    if not path.exists():
        return config

    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}

    if not isinstance(loaded, dict):
        return config

    raw_tags = loaded.get("tags")
    if isinstance(raw_tags, list):
        normalized = [str(tag).strip() for tag in raw_tags if str(tag).strip()]
        if normalized:
            config["tags"] = normalized

    return config
