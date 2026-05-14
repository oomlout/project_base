from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Flask

from webserver.cache import PartsCache
from webserver.services import config_form, config_part_source, config_port, config_quick_summary, config_ui


def normalize_parts_dirs(
    parts_dirs: Path | str | list[Path | str] | tuple[Path | str, ...],
) -> list[Path]:
    if isinstance(parts_dirs, (Path, str)):
        candidates = [parts_dirs]
    else:
        candidates = list(parts_dirs or [])

    normalized: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        path = Path(candidate).resolve(strict=False)
        key = str(path).lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(path)
    return normalized


def build_parts_source_config(parts_dirs: list[Path]) -> dict[str, Any]:
    return {
        "directories": [str(path) for path in parts_dirs],
        "resolved_directories": list(parts_dirs),
    }


def initialize_runtime(app: Flask, config_overrides: dict[str, Any] | None = None) -> None:
    part_source_override_provided = bool(
        config_overrides and ("PARTS_DIRS" in config_overrides or "PARTS_DIR" in config_overrides)
    )
    app.config["PARTS_SOURCE_CONFIG_LOCKED"] = part_source_override_provided

    if part_source_override_provided:
        override_value = (
            app.config["PARTS_DIRS"]
            if config_overrides and "PARTS_DIRS" in config_overrides
            else app.config["PARTS_DIR"]
        )
        resolved_parts_dirs = normalize_parts_dirs(override_value)
        loaded_part_source_config = build_parts_source_config(resolved_parts_dirs)
    else:
        loaded_part_source_config = config_part_source.load_part_source_config(
            Path(app.config["CONFIG_PART_SOURCE_PATH"]),
            Path(app.config["REPO_ROOT"]),
        )
        resolved_parts_dirs = normalize_parts_dirs(loaded_part_source_config["resolved_directories"])

    app.config["CONFIG_PART_SOURCE"] = loaded_part_source_config
    app.config["PARTS_DIRS"] = resolved_parts_dirs
    if resolved_parts_dirs:
        app.config["PARTS_DIR"] = resolved_parts_dirs[0]

    print("[parts] Loading parts from:")
    if resolved_parts_dirs:
        for parts_dir in resolved_parts_dirs:
            print(f"  {parts_dir}")
    else:
        print("  (no directories configured)")

    loaded_ui_config = config_ui.load_ui_config(Path(app.config["CONFIG_UI_PATH"]))
    loaded_form_config = config_form.load_form_config(
        Path(app.config["CONFIG_FORM_BASE_PATH"]),
        Path(app.config["CONFIG_FORM_PATH"]),
    )
    loaded_port_config = config_port.load_port_config(Path(app.config["CONFIG_PORT_PATH"]))
    loaded_quick_summary_config = config_quick_summary.load_quick_summary_config(Path(app.config["CONFIG_QUICK_SUMMARY_PATH"]))
    app.config["CONFIG_UI"] = loaded_ui_config
    app.config["CONFIG_FORM"] = loaded_form_config
    app.config["CONFIG_PORT"] = loaded_port_config
    app.config["CONFIG_QUICK_SUMMARY"] = loaded_quick_summary_config
    app.config["HOST"] = loaded_port_config["host"]
    app.config["PORT"] = loaded_port_config["port"]

    cache = PartsCache(
        app.config["PARTS_DIRS"],
        loaded_ui_config["preview_priority"],
        [field["name"] for field in loaded_ui_config["search_fields"]["available"]],
    )
    cache.load_all()
    loaded_parts = cache.get_parts()

    # --- startup table ---
    rows: list[tuple[str, str]] = []
    for parts_dir in (resolved_parts_dirs or []):
        dir_count = sum(1 for p in loaded_parts if str(p.get("source_parts_dir", "")) == str(parts_dir))
        rows.append((str(parts_dir), str(dir_count)))
    if not rows:
        rows.append(("(no directories configured)", "0"))
    rows.append(("TOTAL", str(len(loaded_parts))))

    col1_w = max(len(r[0]) for r in rows)
    col2_w = max(len(r[1]) for r in rows)
    sep = f"+-{'-' * col1_w}-+-{'-' * col2_w}-+"
    header = f"| {'Directory':<{col1_w}} | {'Parts':>{col2_w}} |"
    print()
    print(sep)
    print(header)
    print(sep)
    for i, (path_str, count_str) in enumerate(rows):
        if i == len(rows) - 1 and len(rows) > 1:
            print(sep)
        print(f"| {path_str:<{col1_w}} | {count_str:>{col2_w}} |")
    print(sep)
    print()
    # ---------------------

    app.config["PARTS_CACHE"] = cache


def reload_ui_config(app: Flask) -> tuple[dict[str, Any], bool]:
    previous = app.config.get("CONFIG_UI", {})
    current = config_ui.load_ui_config(Path(app.config["CONFIG_UI_PATH"]))
    app.config["CONFIG_UI"] = current
    app.config["PARTS_CACHE"].set_preview_priority(current["preview_priority"])
    app.config["PARTS_CACHE"].set_search_field_names(
        [field["name"] for field in current["search_fields"]["available"]]
    )
    return current, current != previous


def reload_part_source_config(app: Flask) -> tuple[dict[str, Any], bool]:
    previous = app.config.get("CONFIG_PART_SOURCE", {})
    if app.config.get("PARTS_SOURCE_CONFIG_LOCKED"):
        current = build_parts_source_config(normalize_parts_dirs(app.config.get("PARTS_DIRS", [])))
        app.config["CONFIG_PART_SOURCE"] = current
        return current, False

    current = config_part_source.load_part_source_config(
        Path(app.config["CONFIG_PART_SOURCE_PATH"]),
        Path(app.config["REPO_ROOT"]),
    )
    previous_dirs = normalize_parts_dirs(previous.get("resolved_directories", []))
    current_dirs = normalize_parts_dirs(current["resolved_directories"])
    app.config["CONFIG_PART_SOURCE"] = current
    app.config["PARTS_DIRS"] = current_dirs
    if current_dirs:
        app.config["PARTS_DIR"] = current_dirs[0]
    app.config["PARTS_CACHE"].set_parts_dirs(current_dirs)
    return current, current_dirs != previous_dirs
