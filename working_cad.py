"""Stdlib-only project facade for component-owned output policy and type dispatch."""
import importlib.util
from pathlib import Path

_path = Path(__file__).resolve().parent / "components/build_policy/working.py"
_spec = importlib.util.spec_from_file_location("_project_build_policy", _path)
_policy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_policy)
enabled = _policy.enabled
validate = _policy.validate
geometry_parameters = _policy.geometry_parameters
builder_name = _policy.builder_name
resolve_builder = _policy.resolve_builder

solidcraft_mode = _policy.solidcraft_mode
