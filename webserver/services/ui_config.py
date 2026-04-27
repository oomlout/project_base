from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

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
    ]
}


def load_ui_config(config_path: Path | str) -> dict[str, Any]:
    path = Path(config_path)
    config = dict(DEFAULT_UI_CONFIG)
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

    return config
