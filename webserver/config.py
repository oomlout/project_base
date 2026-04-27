from __future__ import annotations

from copy import deepcopy

APP_TITLE = "Parts Explorer"
TAXONOMY_FIELD_COUNT = 15
DEFAULT_FAMILY = "generic"


def taxonomy_key(index: int) -> str:
    return f"taxonomy_{index}"


def build_generic_taxonomy_fields() -> list[dict]:
    fields = []
    for index in range(1, TAXONOMY_FIELD_COUNT + 1):
        fields.append(
            {
                "name": taxonomy_key(index),
                "label": f"Taxonomy {index}",
                "input_type": "text",
                "required": index == 1,
                "maps_to": taxonomy_key(index),
                "transform": "slug",
                "placeholder": f"taxonomy level {index}",
                "help_text": "Leave blank to stop the chain at this level."
                if index > 1
                else "Top-level taxonomy bucket used for navigation.",
            }
        )
    return fields


GENERIC_FIELDS = build_generic_taxonomy_fields()

PART_FAMILY_CONFIGS = {
    "generic": {
        "label": "Generic taxonomy entry",
        "description": "Direct control over taxonomy_1 to taxonomy_15.",
        "defaults": {},
        "fields": deepcopy(GENERIC_FIELDS),
        "derived_objects": [],
    },
    "wire_hole_cover": {
        "label": "Wire hole cover",
        "description": "Preconfigured hole cover entry with dimension-driven taxonomy labels.",
        "defaults": {
            "taxonomy_1": "organizing",
            "taxonomy_2": "electrical",
            "taxonomy_3": "wire",
            "taxonomy_4": "hole_cover",
        },
        "fields": [
            {
                "name": "diameter",
                "label": "Diameter (mm)",
                "input_type": "number",
                "required": True,
                "maps_to": "taxonomy_5",
                "format": "{value}_mm_diameter",
                "store_raw": True,
                "placeholder": "40",
            },
            {
                "name": "depth",
                "label": "Depth (mm)",
                "input_type": "number",
                "required": True,
                "maps_to": "taxonomy_6",
                "format": "{value}_mm_depth",
                "store_raw": True,
                "placeholder": "15",
            },
            {
                "name": "hole_top_diameter",
                "label": "Top hole diameter (mm)",
                "input_type": "number",
                "required": True,
                "maps_to": "taxonomy_7",
                "format": "{value}_mm_hole_top_diameter",
                "store_raw": True,
                "placeholder": "30",
            },
            {
                "name": "taxonomy_14",
                "label": "Manufacturer",
                "input_type": "text",
                "required": False,
                "maps_to": "taxonomy_14",
                "transform": "slug",
                "placeholder": "optional",
            },
            {
                "name": "taxonomy_15",
                "label": "Manufacturer part number",
                "input_type": "text",
                "required": False,
                "maps_to": "taxonomy_15",
                "transform": "slug",
                "placeholder": "optional",
            },
        ],
        "derived_objects": [
            {
                "key": "oobb_details",
                "static": {"oobb_name": "hole_cover"},
                "from_fields": {
                    "diameter": "diameter",
                    "depth": "depth",
                    "hole_top_diameter": "hole_top_diameter",
                },
            }
        ],
    },
}
