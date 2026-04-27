from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from webserver.services.taxonomy_builder import build_part_id, build_taxonomy_payload, format_value, slugify


class ValidationError(ValueError):
    pass


def _parse_number(value: str) -> int | float:
    numeric = float(value)
    if numeric.is_integer():
        return int(numeric)
    return numeric


def _parse_value(raw_value: str, input_type: str) -> Any:
    value = raw_value.strip()
    if value == "":
        return ""
    if input_type == "number":
        return _parse_number(value)
    return value


def _mapped_value(field: dict[str, Any], parsed_value: Any) -> str:
    if parsed_value in ("", None):
        return ""
    value = parsed_value
    if field.get("format"):
        value = field["format"].format(value=format_value(parsed_value))
    if field.get("transform") == "slug":
        value = slugify(value)
    return str(value)


def _build_derived_objects(
    family_config: dict[str, Any],
    parsed_values: dict[str, Any],
) -> dict[str, Any]:
    derived_objects = {}
    for definition in family_config.get("derived_objects", []):
        payload = dict(definition.get("static", {}))
        for destination_key, source_key in definition.get("from_fields", {}).items():
            value = parsed_values.get(source_key, "")
            if value not in ("", None):
                payload[destination_key] = value
        if payload:
            derived_objects[definition["key"]] = payload
    return derived_objects


def build_payload(form_data: dict[str, str], family_config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    payload: dict[str, Any] = build_taxonomy_payload()
    payload.update(family_config.get("defaults", {}))
    parsed_values: dict[str, Any] = {}

    for field in family_config.get("fields", []):
        field_name = field["name"]
        raw_value = form_data.get(field_name, "")
        parsed_value = _parse_value(raw_value, field.get("input_type", "text"))
        parsed_values[field_name] = parsed_value

        if field.get("required") and parsed_value in ("", None):
            raise ValidationError(f"{field['label']} is required.")

        mapped_key = field.get("maps_to")
        if mapped_key:
            payload[mapped_key] = _mapped_value(field, parsed_value)

        if field.get("store_raw") and parsed_value not in ("", None):
            payload[field.get("raw_key", field_name)] = parsed_value

    payload.update(_build_derived_objects(family_config, parsed_values))

    part_id = build_part_id(payload)
    if not part_id:
        raise ValidationError("At least one taxonomy value is required to create a part id.")

    return part_id, payload


def write_source_entry(
    source_dir: Path,
    form_data: dict[str, str],
    family_config: dict[str, Any],
) -> dict[str, Any]:
    part_id, payload = build_payload(form_data, family_config)
    target_directory = Path(source_dir) / part_id
    target_file = target_directory / "working.yaml"
    if target_directory.exists():
        raise ValidationError(f"Part '{part_id}' already exists in parts_source.")

    target_directory.mkdir(parents=True, exist_ok=False)
    with target_file.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=False, sort_keys=True)

    return {
        "part_id": part_id,
        "target_directory": target_directory,
        "target_file": target_file,
        "payload": payload,
    }
