from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from webserver.app import create_app
from webserver.config import PART_FAMILY_CONFIGS
from webserver.services import ui_config
from webserver.services.parts_repository import load_part_record
from webserver.services.source_writer import write_source_entry


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, allow_unicode=False, sort_keys=True)


class WebserverAppTests(unittest.TestCase):
    def test_add_route_writes_yaml_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            parts_dir = root / "parts"
            source_dir = root / "parts_source"
            parts_dir.mkdir()
            source_dir.mkdir()

            app = create_app(
                {
                    "TESTING": True,
                    "PARTS_DIR": parts_dir,
                    "PARTS_SOURCE_DIR": source_dir,
                    "SECRET_KEY": "test",
                }
            )
            client = app.test_client()
            response = client.post(
                "/add",
                data={
                    "family": "generic",
                    "taxonomy_1": "organizing",
                    "taxonomy_2": "electrical",
                    "taxonomy_3": "wire",
                    "taxonomy_4": "clip",
                },
                follow_redirects=True,
            )

            self.assertEqual(response.status_code, 200)
            target = source_dir / "organizing_electrical_wire_clip" / "working.yaml"
            self.assertTrue(target.exists())

    def test_explore_route_renders(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            parts_dir = root / "parts"
            source_dir = root / "parts_source"
            part_dir = parts_dir / "organizing_electrical_wire_clip"
            parts_dir.mkdir()
            source_dir.mkdir()
            write_yaml(
                part_dir / "working.yaml",
                {
                    "name_proper": "Wire Clip",
                    "taxonomy_1": "organizing",
                    "taxonomy_2": "electrical",
                    "taxonomy_3": "wire",
                    "taxonomy_4": "clip",
                },
            )

            app = create_app(
                {
                    "TESTING": True,
                    "PARTS_DIR": parts_dir,
                    "PARTS_SOURCE_DIR": source_dir,
                    "SECRET_KEY": "test",
                }
            )
            client = app.test_client()
            response = client.get("/explore")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Wire Clip", response.data)
            self.assertIn(b"Taxonomy", response.data)

    def test_fast_reload_updates_changed_part(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            parts_dir = root / "parts"
            source_dir = root / "parts_source"
            part_dir = parts_dir / "organizing_electrical_wire_clip"
            parts_dir.mkdir()
            source_dir.mkdir()
            write_yaml(
                part_dir / "working.yaml",
                {
                    "name_proper": "Wire Clip",
                    "taxonomy_1": "organizing",
                    "taxonomy_2": "electrical",
                    "taxonomy_3": "wire",
                    "taxonomy_4": "clip",
                },
            )

            app = create_app(
                {
                    "TESTING": True,
                    "PARTS_DIR": parts_dir,
                    "PARTS_SOURCE_DIR": source_dir,
                    "SECRET_KEY": "test",
                }
            )
            cache = app.config["PARTS_CACHE"]
            first_name = cache.get_part("organizing_electrical_wire_clip")["name"]
            self.assertEqual(first_name, "Wire Clip")

            write_yaml(
                part_dir / "working.yaml",
                {
                    "name_proper": "Wire Clip Updated",
                    "taxonomy_1": "organizing",
                    "taxonomy_2": "electrical",
                    "taxonomy_3": "wire",
                    "taxonomy_4": "clip",
                },
            )

            summary = cache.reload_changed()
            updated_name = cache.get_part("organizing_electrical_wire_clip")["name"]
            self.assertGreaterEqual(summary.changed, 1)
            self.assertEqual(updated_name, "Wire Clip Updated")

    def test_preview_priority_prefers_yaml_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            parts_dir = root / "parts"
            source_dir = root / "parts_source"
            part_dir = parts_dir / "organizing_electrical_wire_clip"
            parts_dir.mkdir()
            source_dir.mkdir()
            write_yaml(
                part_dir / "working.yaml",
                {
                    "name_proper": "Wire Clip",
                    "taxonomy_1": "organizing",
                    "taxonomy_2": "electrical",
                    "taxonomy_3": "wire",
                    "taxonomy_4": "clip",
                },
            )
            (part_dir / "initial_generated_icon.png").write_bytes(b"icon")
            (part_dir / "3dpr.png").write_bytes(b"preview")
            config_path = root / "ui_config.yaml"
            write_yaml(config_path, {"preview_priority": ["initial_generated_icon.png", "3dpr.png", "*.png"]})

            loaded = ui_config.load_ui_config(config_path)
            record = load_part_record(part_dir, parts_dir, loaded["preview_priority"])

            self.assertEqual(record["preview_file"], "initial_generated_icon.png")

    def test_fast_reload_promotes_to_full_reload_when_ui_config_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            parts_dir = root / "parts"
            source_dir = root / "parts_source"
            config_path = root / "ui_config.yaml"
            part_dir = parts_dir / "organizing_electrical_wire_clip"
            parts_dir.mkdir()
            source_dir.mkdir()
            write_yaml(
                part_dir / "working.yaml",
                {
                    "name_proper": "Wire Clip",
                    "taxonomy_1": "organizing",
                    "taxonomy_2": "electrical",
                    "taxonomy_3": "wire",
                    "taxonomy_4": "clip",
                },
            )
            (part_dir / "3dpr.png").write_bytes(b"preview")
            (part_dir / "initial_generated_icon.png").write_bytes(b"icon")
            write_yaml(config_path, {"preview_priority": ["3dpr.png", "initial_generated_icon.png"]})

            app = create_app(
                {
                    "TESTING": True,
                    "PARTS_DIR": parts_dir,
                    "PARTS_SOURCE_DIR": source_dir,
                    "UI_CONFIG_PATH": config_path,
                    "SECRET_KEY": "test",
                }
            )
            client = app.test_client()
            self.assertEqual(app.config["PARTS_CACHE"].get_part("organizing_electrical_wire_clip")["preview_file"], "3dpr.png")

            write_yaml(config_path, {"preview_priority": ["initial_generated_icon.png", "3dpr.png"]})
            response = client.post("/reload/fast", follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b"promoted itself to a full cache rebuild", response.data)
            self.assertEqual(
                app.config["PARTS_CACHE"].get_part("organizing_electrical_wire_clip")["preview_file"],
                "initial_generated_icon.png",
            )

    def test_source_writer_builds_hole_cover_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "parts_source"
            source_dir.mkdir()
            result = write_source_entry(
                source_dir,
                {
                    "diameter": "40",
                    "depth": "15",
                    "hole_top_diameter": "30",
                    "taxonomy_14": "",
                    "taxonomy_15": "",
                },
                PART_FAMILY_CONFIGS["wire_hole_cover"],
            )

            self.assertEqual(
                result["part_id"],
                "organizing_electrical_wire_hole_cover_40_mm_diameter_15_mm_depth_30_mm_hole_top_diameter",
            )
            self.assertEqual(result["payload"]["oobb_details"]["oobb_name"], "hole_cover")


if __name__ == "__main__":
    unittest.main()
