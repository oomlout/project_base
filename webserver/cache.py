from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Any

from webserver.services import parts_repository


@dataclass
class CacheSummary:
    loaded: int = 0
    changed: int = 0
    removed: int = 0
    scanned: int = 0
    errors: list[str] = field(default_factory=list)


class PartsCache:
    def __init__(self, parts_dir: Path, preview_priority: list[str] | None = None):
        self.parts_dir = Path(parts_dir)
        self.preview_priority = list(preview_priority or [])
        self._lock = RLock()
        self._records: dict[str, dict[str, Any]] = {}
        self._signatures: dict[str, tuple[int, int, int]] = {}
        self._errors: list[str] = []

    def set_preview_priority(self, preview_priority: list[str]) -> None:
        with self._lock:
            self.preview_priority = list(preview_priority)

    def load_all(self) -> CacheSummary:
        with self._lock:
            records, signatures, errors = parts_repository.scan_parts(
                self.parts_dir,
                self.preview_priority,
            )
            self._records = records
            self._signatures = signatures
            self._errors = errors
            return CacheSummary(
                loaded=len(records),
                changed=len(records),
                removed=0,
                scanned=len(signatures),
                errors=list(errors),
            )

    def reload_changed(self) -> CacheSummary:
        with self._lock:
            changed = 0
            removed = 0
            errors = []
            current_dirs = parts_repository.list_part_directories(self.parts_dir)
            current_ids = set(current_dirs.keys())
            known_ids = set(self._records.keys())

            for part_id, part_dir in current_dirs.items():
                signature = parts_repository.build_directory_signature(part_dir)
                if self._signatures.get(part_id) == signature:
                    continue
                try:
                    record = parts_repository.load_part_record(
                        part_dir,
                        self.parts_dir,
                        self.preview_priority,
                    )
                except Exception as exc:
                    errors.append(f"{part_id}: {exc}")
                    continue
                if record is None:
                    continue
                self._records[part_id] = record
                self._signatures[part_id] = signature
                changed += 1

            for removed_id in sorted(known_ids - current_ids):
                self._records.pop(removed_id, None)
                self._signatures.pop(removed_id, None)
                removed += 1

            self._errors = errors
            return CacheSummary(
                loaded=len(self._records),
                changed=changed,
                removed=removed,
                scanned=len(current_dirs),
                errors=list(errors),
            )

    def get_part(self, part_id: str) -> dict[str, Any] | None:
        with self._lock:
            record = self._records.get(part_id)
            if record is None:
                return None
            return dict(record)

    def get_parts(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(record) for record in self._records.values()]

    def get_errors(self) -> list[str]:
        with self._lock:
            return list(self._errors)
