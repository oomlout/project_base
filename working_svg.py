import copy
import opsvg
import yaml
import os
import svg_help
import svg_styles


def main(**kwargs):
    make_svg(**kwargs)

def make_svg(**kwargs):
    typ = svg_help.get_typ(**kwargs)
    oomp_mode = "project"
    #oomp_mode = "oobb"
    filt = ""
    build_variables = svg_help.get_build_variables(typ, filter=filt)
    if True:
        kwargs["filter"] = build_variables["filter"]
        kwargs["save_type"] = build_variables["save_type"]
        kwargs["navigation"] = build_variables["navigation"]
        kwargs["overwrite"] = build_variables["overwrite"]
        kwargs["oomp_mode"] = oomp_mode
    parts = get_parts(kwargs, oomp_mode)

    kwargs["parts"] = parts

    svg_help.make_parts(**kwargs)

    if kwargs["navigation"]:
        oobb_style = False
        sort = svg_help.get_navigation_sort(oobb_style=oobb_style)
        svg_help.generate_navigation(sort=sort)


def get_parts(kwargs, oomp_mode):
    parts = []

    #load parts from parts/folder/working.yaml
    parts_directory = os.path.join(os.path.dirname(__file__), "parts")
    if not os.path.isdir(parts_directory):
        return parts

    for folder in os.listdir(parts_directory):
        folder_path = os.path.join(parts_directory, folder)
        if not os.path.isdir(folder_path):
            continue

        working_yaml_path = os.path.join(folder_path, "working.yaml")
        if not os.path.isfile(working_yaml_path):
            continue

        with open(working_yaml_path, "r", encoding="utf-8") as infile:
            loaded_part = yaml.safe_load(infile)

        if not isinstance(loaded_part, dict):
            continue

        svg_details_raw = loaded_part.get("svg_details")
        # Accept either a single dict or a list of dicts.
        if isinstance(svg_details_raw, list):
            # Use the first entry to derive kwargs / oobb_name; the full list
            # is kept intact in part["svg_details"] for make_svg_generic.
            svg_details = svg_details_raw[0] if svg_details_raw else {}
        elif isinstance(svg_details_raw, dict):
            svg_details = svg_details_raw
        else:
            continue  # no recognisable svg_details — skip

        part = loaded_part

        part_kwargs = copy.deepcopy(kwargs)
        part_kwargs.update(copy.deepcopy(loaded_part.get("kwargs", {})))
        _SD_META = {"svg_name", "filename_extra", "width", "height", "depth", "styles",
                    "extra", "radius_name"}
        svg_details_safe = {k: v for k, v in svg_details.items()
                            if k not in _SD_META or (k in ("width", "height", "depth") and isinstance(v, (int, float)))}
        part_kwargs.update(copy.deepcopy(svg_details_safe))

        # stylesheet name override from yaml: svg_details.stylesheet: "jazzy"
        if "stylesheet" in svg_details:
            part_kwargs["stylesheet"] = svg_details["stylesheet"]

        # per-part style overrides from yaml: svg_details.styles: {plate: {color: "#FF0000"}}
        yaml_styles = svg_details.get("styles", {})
        if isinstance(yaml_styles, dict) and yaml_styles:
            existing = part_kwargs.get("part_styles", {})
            part_kwargs["part_styles"] = svg_styles.merge(
                svg_styles.get_stylesheet(part_kwargs.get("stylesheet", "default")),
                {**existing, **yaml_styles}
            ) if not existing else {**existing, **yaml_styles}

        part["kwargs"] = part_kwargs
        part["oobb_name"] = part.get("oobb_name", svg_details.get("svg_name", "default"))

        if oomp_mode == "oobb":
            part["kwargs"]["oomp_size"] = part["oobb_name"]

        parts.append(part)

    return parts


def get_base(thing, **kwargs):

    prepare_print = kwargs.get("prepare_print", False)
    width = kwargs.get("width", 1)
    height = kwargs.get("height", 1)
    depth = kwargs.get("depth", 3)
    rot = kwargs.get("rot", [0,0,0])
    pos = kwargs.get("pos", [0,0,0])
    extra = kwargs.get("extra", "")



    #add plate
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["shape"] = f"oobb_plate"
        p3["depth"] = depth
        #p3["m"] = "#"
        pos1 = copy.deepcopy(pos)
        p3["pos"] = pos1
        opsvg.se(thing,**p3)

    #add holes
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["shape"] = f"oobb_holes"
        p3["depth"] = depth
        p3["radius_name"] = "m6"
        #p3["m"] = "#"
        pos1 = copy.deepcopy(pos)
        p3["pos"] = pos1
        opsvg.se(thing,**p3)

    #add text
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["shape"] = f"text"
        p3["text"] = "Base Plate"
        p3["size"] = 10.0
        p3["font"] = "sans-serif"
        p3["halign"] = "left"
        p3["valign"] = "center"
        p3["color"] = "#000000"
        #p3["m"] = "#"
        pos1 = copy.deepcopy(pos)
        p3["pos"] = pos1
        opsvg.se(thing,**p3)

    if prepare_print:
        svg_help.prepare_base_for_print(thing, pos, **kwargs)


def get_fill_in_the_blanks(thing, **kwargs):
    svg_help.get_fill_in_the_blanks(thing, **kwargs)


def get_a4_sheet(thing, **kwargs):
    svg_help.get_a4_sheet(thing, **kwargs)


def get_label_76x50(thing, **kwargs):
    svg_help.get_label_76x50(thing, **kwargs)


def _default_label_boxes():
    """Default 3 × 4 grid matching the Project Bolt tin insert photo.

    Top row is 0.5 units tall (narrow label strip);
    the three lower rows are each 1.0 units tall.
    Total: 3 wide × 3.5 high = 12 boxes.
    """
    boxes = []
    n = 1
    layout = [
        (0.0, 0.5),   # top narrow row
        (0.5, 1.0),
        (1.5, 1.0),
        (2.5, 1.0),
    ]
    for (row_y, row_h) in layout:
        for col in range(3):
            boxes.append({
                "x": float(col),
                "y": row_y,
                "w": 1.0,
                "h": row_h,
                "name": f"box_{n}",
            })
            n += 1
    return boxes


def get_internal_label_sheet(thing, **kwargs):
    """Proportional grid label sheet for tin inserts.

    No dark background — boxes sit directly on the card, separated by the
    card's own fill showing through the gap.  Corner radii are computed per
    corner so junctions and card edges look geometrically correct:

      r_inner  = gap_mm / 2   — inner corners: arc exactly fills the gap void
      r_outer  = card_r - card_margin_mm  — outer corners: parallel to card edge

    Parameters
    ----------
    unit_mm        : float  — physical size of one grid unit in mm   (default 42.0)
    grid_w         : float  — grid width in units                    (default 3.0)
    grid_h         : float  — grid height in units                   (default 3.5)
    card_margin_mm : float  — card fill visible around the grid      (default 2.0)
                              unit_mm=42, grid_w=3, margin=2 → card_w=130 mm
    card_r         : float  — card corner radius in mm               (default 8.0)
    gap_frac       : float  — gap between boxes as fraction of unit_mm (default 0.07)
    boxes          : list   — list of box dicts.  Each dict may contain:
                               x, y        — top-left position in units (required)
                               w, h        — size in units              (required)
                               name        — identifier string          (default "box_N")
                               text        — display text               (defaults to name)
                               style       — box fill style             (default "plate.cell")
                               text_style      — text style             (default "label")
                               text_size       — font size override mm  (default from style)
                               halign          — text alignment         (default "center";
                                                 auto "left" when lined)
                               valign          — vertical alignment     (default "center";
                                                 auto "top" when lined)
                               lined           — fill box with ruled    (default False)
                                                 lines for handwriting
                               line_spacing_mm — spacing between lines  (default 6.0 mm)
                               (any extra keys are preserved and ignored)
    stylesheet     : str    — stylesheet name                        (default "project_bolt")
    """
    prepare_print  = kwargs.get("prepare_print", False)
    pos            = kwargs.get("pos", [0, 0, 0])
    unit_mm        = float(kwargs.get("unit_mm",         42.0))
    grid_w         = float(kwargs.get("grid_w",           3.0))
    grid_h         = float(kwargs.get("grid_h",           3.5))
    card_margin_mm = float(kwargs.get("card_margin_mm",   2.0))
    card_r         = float(kwargs.get("card_r",           8.0))
    gap_frac       = float(kwargs.get("gap_frac",         0.07))
    boxes          = kwargs.get("boxes", _default_label_boxes())

    # ── Derived dimensions ────────────────────────────────────────────────────
    sheet_w  = grid_w * unit_mm                       # 126.0 mm
    sheet_h  = grid_h * unit_mm                       # 147.0 mm
    card_w   = sheet_w + 2 * card_margin_mm           # 130.0 mm
    card_h   = sheet_h + 2 * card_margin_mm           # 151.0 mm
    gap_mm   = gap_frac * unit_mm                     #   2.94 mm

    # Corner radius rules:
    #   inner: arc radius = gap/2 → arc exactly reaches the gap centreline,
    #          filling the void where four box corners meet
    #   outer: parallel to the card's own rounded corner
    r_inner  = gap_mm / 2
    r_outer  = max(card_r - card_margin_mm, 0.0)

    _EPS = 1e-3   # tolerance for edge-touching checks

    def _radii(bx, by, bw, bh):
        """Return (r_tl, r_tr, r_br, r_bl) for a box at grid position (bx,by)."""
        at_left   = bx              < _EPS
        at_top    = by              < _EPS
        at_right  = (bx + bw - grid_w) > -_EPS
        at_bottom = (by + bh - grid_h) > -_EPS
        tl = r_outer if (at_left  and at_top)    else r_inner
        tr = r_outer if (at_right and at_top)    else r_inner
        br = r_outer if (at_right and at_bottom) else r_inner
        bl = r_outer if (at_left  and at_bottom) else r_inner
        return tl, tr, br, bl

    # ── Stylesheet ────────────────────────────────────────────────────────────
    if "styles" not in thing or not thing.get("styles"):
        sheet_name = kwargs.get("stylesheet", "project_bolt")
        thing["styles"] = svg_styles.get_stylesheet(sheet_name)

    # ── Card fill (drawn first — border comes last) ───────────────────────────
    pos1 = copy.deepcopy(pos)
    opsvg.se(thing, shape="rounded_rectangle", style="plate",
             size=[card_w, card_h, 0], r=card_r, pos=pos1,
             stroke="none", stroke_width=0)

    # ── Boxes ─────────────────────────────────────────────────────────────────
    # Box centre in Y-up coords (origin = card centre = sheet centre):
    #   cx = -sheet_w/2 + unit_mm*(bx + bw/2)
    #   cy =  sheet_h/2 - unit_mm*(by + bh/2)
    # gap_mm cancels in the centre calculation; only affects w_mm / h_mm.
    for i, box in enumerate(boxes):
        bx         = float(box.get("x", 0))
        by         = float(box.get("y", 0))
        bw         = float(box.get("w", 1))
        bh         = float(box.get("h", 1))
        name       = box.get("name",       f"box_{i + 1}")
        text       = box.get("text",       name)
        box_style  = box.get("style",      "plate.cell")
        txt_style  = box.get("text_style", "label")
        txt_size   = box.get("text_size",  None)
        lined      = bool(box.get("lined", False))
        line_spc   = float(box.get("line_spacing_mm", 6.0))

        # lined boxes default to top-left anchored text; explicit values win
        halign = box.get("halign", "left"   if lined else "center")
        valign = box.get("valign", "top"    if lined else "center")

        w_mm = bw * unit_mm - gap_mm
        h_mm = bh * unit_mm - gap_mm
        cx   = -sheet_w / 2 + unit_mm * (bx + bw / 2)
        cy   =  sheet_h / 2 - unit_mm * (by + bh / 2)

        tl, tr, br, bl = _radii(bx, by, bw, bh)

        pos1    = copy.deepcopy(pos)
        pos1[0] += cx
        pos1[1] += cy

        # 1. Box fill
        opsvg.se(thing, shape="rrect_corners", style=box_style,
                 size=[w_mm, h_mm, 0],
                 r_tl=tl, r_tr=tr, r_br=br, r_bl=bl,
                 pos=pos1)

        # 2. Ruled lines (drawn before text so text sits on top)
        if lined:
            pad_x      = gap_mm * 1.5          # horizontal inset
            pad_y      = gap_mm                # top / bottom inset
            rule_w     = w_mm - 2 * pad_x
            rule_thick = 0.35
            y_from_top = pad_y + line_spc * 0.65   # first line
            while y_from_top + rule_thick / 2 < h_mm - pad_y:
                # Y-up offset from box centre: positive = up
                line_dy = h_mm / 2 - y_from_top
                lpos    = copy.deepcopy(pos)
                lpos[0] += cx
                lpos[1] += cy + line_dy
                opsvg.se(thing, shape="rect", style="rule",
                         size=[rule_w, rule_thick, 0], pos=lpos)
                y_from_top += line_spc

        # 3. Text — anchor point offset so halign/valign align to box edge
        padding = gap_mm
        off_x = {"left":  -(w_mm / 2 - padding),
                 "right":  (w_mm / 2 - padding),
                 "center": 0.0}.get(halign, 0.0)
        off_y = {"top":    (h_mm / 2 - padding),    # Y-up: positive = up
                 "bottom": -(h_mm / 2 - padding),
                 "center": 0.0}.get(valign, 0.0)

        txt_pos    = copy.deepcopy(pos)
        txt_pos[0] += cx + off_x
        txt_pos[1] += cy + off_y

        txt_kwargs = dict(halign=halign, valign=valign)
        if txt_size is not None:
            txt_kwargs["size"] = txt_size
        opsvg.se(thing, shape="text", style=txt_style,
                 text=text, pos=txt_pos, **txt_kwargs)

    # ── Card border (drawn last — on top of everything) ───────────────────────
    pos1 = copy.deepcopy(pos)
    opsvg.se(thing, shape="rounded_rectangle", style="plate.outline",
             size=[card_w, card_h, 0], r=card_r, pos=pos1)

    if prepare_print:
        svg_help.prepare_base_for_print(thing, pos, **kwargs)


if __name__ == '__main__':
    kwargs = {}
    main(**kwargs)
