import copy
import os
import sys
import yaml

import opsvg
import svg_variables as _sv
import svg_styles as _ss
import svg_a4


###### utilities


def get_typ(**kwargs):
    typ = kwargs.get("typ", "")

    if typ == "":
        #setup
        #typ = "all"
        typ = "fast"
        #typ = "manual"

    return typ


def get_build_variables(typ, filter=""):
    if typ == "all":
        return {
            "filter": "",
            "save_type": "all",
            "navigation": True,
            "overwrite": True,
        }

    if typ == "fast":
        return {
            "filter": "",
            "save_type": "all",
            "navigation": False,
            "overwrite": True,
        }

    if typ == "manual":
        return {
            "filter": "",
            #"filter": "label"
            "save_type": "none",
            #"save_type": "all"
            "navigation": True,
            #"navigation": False
            "overwrite": True,
        }

    raise ValueError(f"Unknown typ: {typ}")


def get_navigation_sort(oobb_style=False):
    sort = []
    #sort.append("extra")
    sort.append("oobb_name")
    sort.append("width")
    sort.append("height")
    return sort


def prepare_base_for_print(thing, pos, **kwargs):
    # SVG is a flat 2-D format — there is no Z axis to flip for printing.
    # This stub exists so builder functions that call it remain compatible
    # with the working_scad.py pattern.
    pass


def make_parts(**kwargs):
    parts          = kwargs.get("parts", [])
    filter         = kwargs.get("filter", "")

    #make the parts
    if True:
        for part in parts:
            oobb_name = part.get("oobb_name", "default")
            extra = part["kwargs"].get("extra", "")
            if filter in oobb_name or filter in extra:
                print(f"making {part['oobb_name']}")
                make_svg_generic(part)
            else:
                print(f"skipping {part['oobb_name']}")


def make_svg_generic(part):

    # fetching variables
    oobb_name    = part.get("oobb_name", "default")
    project_name = part.get("project_name", "default")

    kwargs = part.get("kwargs", {})

    save_type      = kwargs.get("save_type",      "all")
    overwrite      = kwargs.get("overwrite",       True)

    kwargs["type"] = f"{project_name}_{oobb_name}"

    thing = get_default_thing(**kwargs)
    thing.update(part)

    import working_svg
    svg_name = part.get("svg_details", {}).get("svg_name", oobb_name)
    try:
        func = getattr(working_svg, f"get_{svg_name}")
    except AttributeError:
        func = None
    if callable(func):
        func(thing, **kwargs)
    else:
        working_svg.get_base(thing, **kwargs)

    oomp_mode = kwargs.get("oomp_mode", "project")

    if oomp_mode == "project":
        descmain = ""
        current_description_main = thing.get("description_main", "default")
        current_size = thing.get("size", "default")
        new_size = current_size.replace(f"{project_name}_", "")
        descmain = f"{new_size}_{current_description_main}"
        kwargs["oomp_description_main"] = f"{descmain}"
        descextra = ""
        current_description_extra = thing.get("description_extra", "")
        descextra = f"{current_description_extra}"
        kwargs["oomp_description_extra"] = f"{descextra}"
    elif oomp_mode == "oobb":
        current_description_main = thing.get("description_main", "default")
        descmain = f"{current_description_main}"
        descextra = thing.get("extra", "")
        if descextra != "":
            descextra = f"{descextra}_extra"
        kwargs["oomp_description_main"] = f"{current_description_main}"
        kwargs["oomp_description_extra"] = f"{descextra}"
        kwargs["oomp_size"] = f"{part['oobb_name']}"

    oomp_keys = ["classification", "type", "size", "color", "description_main", "description_extra"]
    oomp_id = part.get("id", "")
    if oomp_id == "":
        for key in oomp_keys:
            deet = part.get(key, "")
            deet = deet.replace(".", "_")
            if deet != "":
                oomp_id += f"{deet}_"
        oomp_id = oomp_id[:-1]
    if oomp_id == "":
        oomp_id = oobb_name
    part["id"] = oomp_id
    folder = f"parts/{oomp_id}"

    if save_type != "all":
        print(f"  dry-run — would write to {folder}/")
        return thing

    if not os.path.isdir(folder):
        os.makedirs(folder)

    # svg
    svg_path = os.path.join(folder, "working_svg.svg")
    opsvg.opsvg_make_object(svg_path, thing["svg_components"], overwrite=overwrite)

    # a4 presentation sheet
    svg_a4.make_a4_sheet(svg_path, folder, part, thing)

    # working.yaml — partial dump (mirrors scad_help)
    yaml_file = f"{folder}/working.yaml"
    with open(yaml_file, "w", encoding="utf-8") as file:
        part_new = copy.deepcopy(part)
        kwargs_new = part_new.get("kwargs", {})
        kwargs_new.pop("save_type", "")
        part_new["kwargs"] = kwargs_new
        part_new["project_name"] = os.getcwd()
        part_new["id_svg"] = thing.get("id", oomp_id)
        # svg_details lets get_parts() reload this part from disk.
        svg_details = {}
        svg_details["svg_name"] = part.get("svg_details", {}).get("svg_name", oobb_name)
        for k in ["width", "height", "depth", "extra", "radius_name"]:
            v = kwargs.get(k, "")
            if v != "" and v != 0:
                svg_details[k] = v
        part_new["svg_details"] = svg_details
        part_new.pop("thing", "")
        yaml.dump(part_new, file, allow_unicode=True)

    # thing.yaml — full dump (mirrors scad_help)
    yaml_file = f"{folder}/thing.yaml"
    with open(yaml_file, "w", encoding="utf-8") as file:
        part_new = copy.deepcopy(part)
        kwargs_new = part_new.get("kwargs", {})
        kwargs_new.pop("save_type", "")
        part_new["kwargs"] = kwargs_new
        part_new["project_name"] = os.getcwd()
        part_new["id_svg"] = thing.get("id", oomp_id)
        part_new["thing"] = _serialisable(thing)
        yaml.dump(part_new, file, allow_unicode=True)

    print(f"done {oomp_id}")
    return thing


def generate_navigation(folder="parts", sort=["oobb_name", "width", "height"]):
    #crawl through all directories in parts/ and load all working.yaml files
    parts = {}
    for root, dirs, files in os.walk(folder):
        if "working.yaml" in files:
            yaml_file = os.path.join(root, "working.yaml")
            if root != folder:
                with open(yaml_file, "r", encoding="utf-8") as file:
                    part = yaml.safe_load(file)
                    part["folder"] = root
                    part_name = root.replace(f"{folder}", "")
                    part_name = part_name.replace("/", "").replace("\\", "")
                    parts[part_name] = part
                    print(f"Loaded {yaml_file}")

    for part_id in parts:
        if part_id != "":
            part = parts[part_id]

            if "kwargs" in part:
                kwarg_copy = copy.deepcopy(part["kwargs"])
                folder_navigation = "navigation_svg"
                folder_source = part["folder"]
                folder_extra = ""
                for s in sort:
                    if s == "oobb_name":
                        ex = part.get("oobb_name", "default")
                    else:
                        ex = kwarg_copy.get(s, "default")
                        if isinstance(ex, list):
                            ex_string = ""
                            for e in ex:
                                ex_string += f"{e}_"
                            ex = ex_string[:-1]
                            ex = ex.replace(".", "d")
                    folder_extra += f"{s}_{ex}/"

                folder_extra = folder_extra.replace(".", "d")
                folder_destination = f"{folder_navigation}/{folder_extra}"
                if not os.path.exists(folder_destination):
                    os.makedirs(folder_destination)
                if os.name == "nt":
                    command = f'xcopy "{folder_source}" "{folder_destination}" /E /I /Y'
                    print(command)
                    os.system(command)
                else:
                    os.system(f"cp -r {folder_source}/. {folder_destination}")


def get_default_thing(**kwargs):
    # Resolve stylesheet: kwargs may carry "stylesheet" name or a full "styles" dict
    sheet_name = kwargs.get("stylesheet", "default")
    styles     = kwargs.get("styles", None)
    if styles is None:
        styles = _ss.get_stylesheet(sheet_name)
    else:
        styles = copy.deepcopy(styles)

    # Apply any per-part style overrides passed as part_styles
    part_styles = kwargs.get("part_styles", {})
    if part_styles:
        styles = _ss.merge(styles, part_styles)

    thing = {
        "oobb_name":         kwargs.get("oobb_name",         ""),
        "type":              kwargs.get("type",              ""),
        "description":       kwargs.get("description",       ""),
        "classification":    kwargs.get("classification",    "svg"),
        "size":              kwargs.get("size",              ""),
        "color":             kwargs.get("color",             ""),
        "description_main":  kwargs.get("description_main",  ""),
        "description_extra": kwargs.get("description_extra", ""),
        "width":             kwargs.get("width",  1),
        "height":            kwargs.get("height", 1),
        "depth":             kwargs.get("depth",  3),
        "extra":             kwargs.get("extra",  ""),
        "width_mm":          (kwargs.get("width",  1) if isinstance(kwargs.get("width",  1), (int, float)) else 1) * _sv.OSP - _sv.OSP_MINUS,
        "height_mm":         (kwargs.get("height", 1) if isinstance(kwargs.get("height", 1), (int, float)) else 1) * _sv.OSP - _sv.OSP_MINUS,
        "depth_mm":          kwargs.get("depth",  3),
        "svg_components":    [],
        "styles":            styles,
    }
    return thing


def id_from_part(part):
    oomp_keys = ["classification", "type", "size", "color", "description_main", "description_extra"]
    oomp_id = part.get("id", "")
    if not oomp_id:
        for key in oomp_keys:
            val = str(part.get(key, "")).replace(".", "_").strip()
            if val:
                oomp_id += f"{val}_"
        oomp_id = oomp_id.rstrip("_")
    if not oomp_id:
        oomp_id = part.get("oobb_name", "unnamed")
    return oomp_id


def _serialisable(obj, _depth=0):
    if _depth > 10:
        return str(obj)
    if isinstance(obj, dict):
        return {k: _serialisable(v, _depth + 1) for k, v in obj.items()
                if not callable(v)}
    if isinstance(obj, (list, tuple)):
        return [_serialisable(i, _depth + 1) for i in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)
