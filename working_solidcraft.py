"""Generate native SolidCraft files; additional exports are opt-in."""
import argparse
import copy
import json
import os
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
CAD_API = "solidcraft"
# Optional cosmetic detail for positive screws, nuts and bearings.
RENDER_DETAIL = False
# Generate only native .solidcraft files by default.
EXPORT_STL = False
EXPORT_EXTRAS = False  # STEP and PNG previews.
VERIFY_SOLIDCRAFT = False


def get_plate(thing, **kwargs):
    """Define the native plate using the project's copy-and-update recipe style."""
    from oobb_solidcraft import api as oobb

    if RENDER_DETAIL:
        kwargs.setdefault("render_detail", True)
    prepare_print = kwargs.get("prepare_print", False)
    width = kwargs.get("width", 1)
    height = kwargs.get("height", 1)
    depth = kwargs.get("depth", 3)
    pos = kwargs.get("pos", [0, 0, 0])

    # Add plate.
    if width == 1 and height == 1:
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "positive"
        p3["shape"] = "oobb_plate"
        p3["depth"] = depth
        p3["pos"] = copy.deepcopy(pos)
        oobb.append_full(thing, **p3)
    else:
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "positive"
        p3["shape"] = "oobb_rounded_rectangle_rounded"
        p3["radius_rounded"] = 1.5
        p3["size"] = [width * 15 - 1, height * 15 - 1, depth]
        p3["pos"] = copy.deepcopy(pos)
        oobb.append_full(thing, **p3)

    # Add both hole families at exactly the plate depth.
    p3 = copy.deepcopy(kwargs)
    p3["type"] = "p"
    p3["shape"] = "oobb_holes"
    p3["both_holes"] = True
    p3["depth"] = depth
    p3["holes"] = "all"
    p3["pos"] = copy.deepcopy(pos)
    oobb.append_full(thing, **p3)

    if prepare_print:
        from oobb_solidcraft._loader import load
        load("prepare_print").prepare_base_for_print(thing, pos, **kwargs)


# Shared support is stdlib-only here; CAD imports run in the configured Python.
def launch_support():
    import importlib.util
    config = json.loads((PROJECT / "solidcraft/config.json").read_text(encoding="utf-8"))
    helper = Path(os.environ.get("OOBB_SOLIDCRAFT_ROOT", config["helper_root"]))
    path = helper / "components/project_launcher/working.py"
    if not path.is_file():
        raise RuntimeError(f"SolidCraft launcher unavailable: {path}; check solidcraft/config.json")
    spec = importlib.util.spec_from_file_location("_project_solidcraft_launcher", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def configuration():
    return launch_support().configuration(PROJECT)


def main(*, solidcraft_context=None, **kwargs):
    context = dict(solidcraft_context or {})
    context.setdefault("export_stl", EXPORT_STL)
    context.setdefault("export_extras", EXPORT_EXTRAS)
    context["verify_solidcraft"] = kwargs.pop("verify_solidcraft", context.get("verify_solidcraft", VERIFY_SOLIDCRAFT))
    return launch_support().main(project_dir=PROJECT, solidcraft_context=context, **kwargs)


def publish(summary):
    if not any(result["status"] == "success" for result in summary["results"]):
        return
    return launch_support().publish(summary, project_dir=PROJECT)


def worker(part_filter, modes, *, export_stl=False, export_extras=False, verify_solidcraft=False, recipe_source=None):
    return launch_support().worker(part_filter, modes, project_dir=PROJECT, export_stl=export_stl, export_extras=export_extras, verify_solidcraft=verify_solidcraft, recipe_source=recipe_source)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build every enabled part as native SolidCraft only; other exports are opt-in.")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    execution = parser.add_mutually_exclusive_group()
    execution.add_argument('--desktop', dest='execution_mode', action='store_const', const='desktop')
    execution.add_argument('--headless', dest='execution_mode', action='store_const', const='headless')
    parser.add_argument('--speed', type=float, default=1, help='Desktop playback speed, 0.25 to 8.')
    parser.add_argument('--definition', default=None, help='Saved definition.json or self-contained native design for desktop playback.')
    parser.add_argument("--filter", default="", help="Optional part ID substring; default builds all parts.")
    parser.add_argument("--recipe-source", choices=["working_solidcraft", "working_scad"], default=None,
                        help="Override the recipe source; working_scad reuses its get_<type> functions.")
    parser.add_argument("--modes", nargs="+", choices=["true", "3dpr"], default=None)
    parser.add_argument("--stl", action=argparse.BooleanOptionalAction, default=EXPORT_STL,
                        help="Also export STL files (default: off).")
    parser.add_argument('--extras', action=argparse.BooleanOptionalAction, default=EXPORT_EXTRAS,
                        help='Also generate STEP and PNG previews (default: off).')
    parser.add_argument('--verify', action=argparse.BooleanOptionalAction, default=VERIFY_SOLIDCRAFT,
                        help='Run reference geometry, reopening and export verification (default: off).')
    args = parser.parse_args()
    modes = args.modes or configuration()["modes"]
    if args.worker:
        worker(args.filter, modes, export_stl=args.stl, export_extras=args.extras, verify_solidcraft=args.verify, recipe_source=args.recipe_source)
    else:
        context = {"part_filter": args.filter, "modes": modes, "export_stl": args.stl, "export_extras": args.extras, "verify_solidcraft": args.verify, "recipe_source": args.recipe_source}
        if args.execution_mode:
            context.update(execution_mode=args.execution_mode, playback_speed=args.speed, definition_path=args.definition)
        main(solidcraft_context=context)
