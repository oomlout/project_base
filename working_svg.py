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

        svg_details = loaded_part.get("svg_details")
        if not isinstance(svg_details, dict):
            continue

        part = loaded_part

        part_kwargs = copy.deepcopy(kwargs)
        part_kwargs.update(copy.deepcopy(loaded_part.get("kwargs", {})))
        svg_details_safe = {k: v for k, v in svg_details.items()
                            if k not in ("width", "height", "depth", "styles") or isinstance(v, (int, float))}
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

def _split_title(title):
    """Split a title string into two display lines for the fill-in-the-blanks card.

    Splits on the first '\\n' if present, otherwise at the space closest to the
    midpoint.  Returns (line1, line2) — line2 is empty if the title is a single word.
    """
    if "\n" in title:
        parts = title.split("\n", 1)
        return parts[0].strip(), parts[1].strip()
    words = title.split()
    if len(words) <= 1:
        return title, ""
    mid = len(words) // 2
    return " ".join(words[:mid]), " ".join(words[mid:])


def get_fill_in_the_blanks(thing, **kwargs):
    """100 × 159 mm fill-in card — Project Bolt tin label style.

    Layout
    ------
    ┌─────────────────────────────────────────┐  ← single thick outer border (r=8)
    │                                         │
    │              Prototyping                │  ← title line 1 (bold)
    │                  Tin                    │  ← title line 2 (bold)
    │                                         │
    │  _______________________________________│  ← 4 ruled blank lines
    │  _______________________________________│
    │  _______________________________________│
    │  _______________________________________│
    │                                         │
    ├────────────────────────┬────────────────┤  ← table row 1 (edge to edge)
    │  (category / label)    │    Contents    │     2 cols: light | dark
    ├─────────┬──────────────┼────────────────┤  ← table rows 2-3 (edge to edge)
    │         │              │                │     3 equal cols
    ├─────────┼──────────────┼────────────────┤
    │         │              │                │
    └─────────┴──────────────┴────────────────┘

    Parameters (all optional kwargs)
    ----------------------------------
    title         : str   — card title, split to 2 lines automatically
                           (default "Prototyping Tin")
    table_label   : str   — text in the dark right-hand header cell
                           (default "Contents")
    title_size    : float — font size for the title in mm (default 14.0)
    num_lines     : int   — number of ruled blank lines (default 4)
    stylesheet    : str   — stylesheet name or list (default "project_bolt")
    """
    prepare_print  = kwargs.get("prepare_print", False)
    pos            = kwargs.get("pos", [0, 0, 0])
    title          = kwargs.get("title", "Prototyping Tin")
    table_label    = kwargs.get("table_label", "Contents")
    title_size     = kwargs.get("title_size", 14.0)
    num_lines      = kwargs.get("num_lines", 4)

    # ── Stylesheet ────────────────────────────────────────────────────────────
    if "styles" not in thing or not thing.get("styles"):
        sheet_name = kwargs.get("stylesheet", "project_bolt")
        thing["styles"] = svg_styles.get_stylesheet(sheet_name)

    # ── Card geometry ─────────────────────────────────────────────────────────
    card_w  = 100.0
    card_h  = 159.0
    r_outer = 8.0    # corner radius

    # ── Card fill only (border is drawn last so it sits on top) ──────────────
    pos1 = copy.deepcopy(pos)
    opsvg.se(thing, shape="rounded_rectangle", style="plate",
             size=[card_w, card_h, 0], r=r_outer, pos=pos1,
             stroke="none", stroke_width=0)

    # ── Title (1 or 2 lines, bold display font) ───────────────────────────────
    line1, line2 = _split_title(title)
    line_spacing = title_size * 1.25   # comfortable inter-line gap

    if line2:
        # Two-line: centre the pair vertically in the title zone
        title1_y = 61.0
        title2_y = title1_y - line_spacing
    else:
        # Single line: sit higher in the title zone
        title1_y = 53.0
        title2_y = None

    pos1 = copy.deepcopy(pos)
    pos1[1] += title1_y
    opsvg.se(thing, shape="text", style="label.title",
             text=line1, size=title_size,
             halign="center", valign="center", pos=pos1)

    if title2_y is not None:
        pos1 = copy.deepcopy(pos)
        pos1[1] += title2_y
        opsvg.se(thing, shape="text", style="label.title",
                 text=line2, size=title_size,
                 halign="center", valign="center", pos=pos1)

    # ── Ruled blank lines ─────────────────────────────────────────────────────
    rule_line_w  = 86.0   # width of each ruled line
    rule_line_h  = 0.35   # thickness (rendered as a thin filled rect)
    rule_top_y   = 20.0   # y of first line (from centre, Y-up)
    rule_spacing = 11.0   # gap between consecutive lines

    for i in range(num_lines):
        pos1 = copy.deepcopy(pos)
        pos1[1] += rule_top_y - i * rule_spacing
        opsvg.se(thing, shape="rect", style="rule",
                 size=[rule_line_w, rule_line_h, 0], pos=pos1)

    # ── Bottom table (edge-to-edge — lines reach the card border) ─────────────
    table_w        = card_w           # full card width: 100 mm
    table_left     = -card_w / 2     # x = -50
    table_right    = +card_w / 2     # x = +50
    card_bottom_y  = -card_h / 2     # y = -79.5  (card's bottom edge)

    row1_h = 14.0   # header-label row
    row2_h = 18.0   # first data row
    row3_h = 18.0   # second data row

    # Pin the table flush to the card bottom
    table_bottom_y = card_bottom_y                            # -79.5
    table_top_y    = table_bottom_y + row1_h + row2_h + row3_h  # -29.5

    row1_bot_y = table_top_y  - row1_h                       # -43.5
    row2_bot_y = row1_bot_y   - row2_h                       # -61.5

    # y-centres of each row
    row1_cy = (table_top_y + row1_bot_y) / 2                 # -36.5
    row2_cy = (row1_bot_y  + row2_bot_y) / 2                 # -52.5
    row3_cy = (row2_bot_y  + table_bottom_y) / 2             # -70.5

    # Row 1 column geometry
    left_w   = table_w * 0.60                                 # 60 mm
    right_w  = table_w - left_w                              # 40 mm
    left_cx  = table_left  + left_w  / 2                     # -20
    right_cx = table_right - right_w / 2                     # +30

    # Row 1: left cell fill (light grey, no border)
    pos1 = copy.deepcopy(pos)
    pos1[0] += left_cx
    pos1[1] += row1_cy
    opsvg.se(thing, shape="rect", style="plate.light",
             size=[left_w, row1_h, 0], pos=pos1,
             stroke="none", stroke_width=0)

    # Row 1: right "Contents" cell fill (dark, no border)
    pos1 = copy.deepcopy(pos)
    pos1[0] += right_cx
    pos1[1] += row1_cy
    opsvg.se(thing, shape="rect", style="header",
             size=[right_w, row1_h, 0], pos=pos1,
             stroke="none", stroke_width=0)

    # "Contents" label text (white on dark)
    pos1 = copy.deepcopy(pos)
    pos1[0] += right_cx
    pos1[1] += row1_cy
    opsvg.se(thing, shape="text", style="header.label",
             text=table_label, size=7.0,
             halign="center", valign="center", pos=pos1)

    # ── Table grid lines ──────────────────────────────────────────────────────
    line_t   = 0.4      # line thickness in mm
    line_col = "#2E2E2E"

    def hline(y, x1=table_left, x2=table_right):
        """Thin horizontal line from x1 to x2 at y."""
        p = copy.deepcopy(pos)
        p[0] += (x1 + x2) / 2
        p[1] += y
        opsvg.se(thing, shape="rect", color=line_col, stroke="none", stroke_width=0,
                 size=[x2 - x1, line_t, 0], pos=p)

    def vline(x, y_top, y_bot):
        """Thin vertical line from y_top down to y_bot at x (Y-up coords)."""
        p = copy.deepcopy(pos)
        p[0] += x
        p[1] += (y_top + y_bot) / 2
        opsvg.se(thing, shape="rect", color=line_col, stroke="none", stroke_width=0,
                 size=[line_t, y_top - y_bot, 0], pos=p)

    # Horizontal rules: top of table, after row1, after row2
    # (no bottom rule — the card border closes the table at the bottom)
    hline(table_top_y)
    hline(row1_bot_y)
    hline(row2_bot_y)

    # Row 1 vertical divider: left 60 mm / right 40 mm
    row1_div_x = table_left + left_w                          # +10
    vline(row1_div_x, table_top_y, row1_bot_y)

    # Rows 2 & 3 vertical dividers: three equal columns
    # Extended to card_bottom_y so they pierce the border (border drawn last)
    col_w  = table_w / 3                                      # 33.33 mm
    div1_x = table_left + col_w                               # -16.67
    div2_x = table_left + col_w * 2                           # +16.67
    vline(div1_x, row1_bot_y, card_bottom_y)
    vline(div2_x, row1_bot_y, card_bottom_y)

    # ── Card border (drawn last — paints over any fill that bleeds to the edge)
    pos1 = copy.deepcopy(pos)
    opsvg.se(thing, shape="rounded_rectangle", style="plate.outline",
             size=[card_w, card_h, 0], r=r_outer, pos=pos1)

    if prepare_print:
        svg_help.prepare_base_for_print(thing, pos, **kwargs)


def get_a4_sheet(thing, **kwargs):
    """A4-sized demo sheet — demonstrates every primitive shape component."""

    prepare_print = kwargs.get("prepare_print", False)
    depth = kwargs.get("depth", 3)
    pos   = kwargs.get("pos", [0, 0, 0])

    sheet_width  = 210.0
    sheet_height = 297.0
    content_inset  = 10.0
    content_width  = sheet_width  - 2 * content_inset
    content_height = sheet_height - 2 * content_inset

    thing["styles"] = svg_styles.get_stylesheet("minimal")


    # background sheet
    pos1 = copy.deepcopy(pos)
    opsvg.se(thing, shape="rect", style="plate",
             size=[sheet_width, sheet_height, depth], pos=pos1)

    # content area (slightly lighter inset)
    pos1 = copy.deepcopy(pos)
    opsvg.se(thing, shape="rounded_rectangle", style="plate.light",
             size=[content_width, content_height, depth], r=5.0, pos=pos1)

    # title text
    pos1 = copy.deepcopy(pos)
    pos1[1] += sheet_height / 2 - 30.0
    opsvg.se(thing, shape="text", style="header.label",
             text="A4 Demo Sheet", size=14.0, pos=pos1)

    # subtitle
    pos1 = copy.deepcopy(pos)
    pos1[1] += sheet_height / 2 - 48.0
    opsvg.se(thing, shape="text", style="header.label",
             text="oomlout SVG pipeline", size=7.0, pos=pos1)

    # version label (bottom-right, mono)
    pos1 = copy.deepcopy(pos)
    pos1[0] += sheet_width  / 2 - 8.0
    pos1[1] -= sheet_height / 2 - 8.0
    opsvg.se(thing, shape="text", style="label.mono",
             text="v1.0", size=4.0, halign="right", valign="center", pos=pos1)

    # triangle marker (top-right corner)
    pos1 = copy.deepcopy(pos)
    pos1[0] += sheet_width  / 2 - 20.0
    pos1[1] += sheet_height / 2 - 20.0
    opsvg.se(thing, shape="polygon", style="plate.accent",
             points=[[0, 4], [-6, -4], [6, -4]], pos=pos1)

    # corner punch (top-left)
    pos1 = copy.deepcopy(pos)
    pos1[0] -= sheet_width  / 2 - 20.0
    pos1[1] += sheet_height / 2 - 20.0
    opsvg.se(thing, shape="circle", style="hole",
             r=4.0, pos=pos1)

    # adjustment slot (bottom-centre)
    pos1 = copy.deepcopy(pos)
    pos1[1] -= sheet_height / 2 - 20.0
    opsvg.se(thing, shape="slot", style="slot",
             r=3.0, w=40.0, pos=pos1)

    if prepare_print:
        svg_help.prepare_base_for_print(thing, pos, **kwargs)


def get_label_76x50(thing, **kwargs):
    """76.2 × 50.4 mm adhesive label — demonstrates text, header bar, and bullet."""

    prepare_print = kwargs.get("prepare_print", False)
    depth = kwargs.get("depth", 3)
    pos   = kwargs.get("pos", [0, 0, 0])

    label_width   = 76.2
    label_height  = 50.4
    header_height = 12.0
    header_y      = label_height / 2 - header_height / 2

    # label body
    pos1 = copy.deepcopy(pos)
    opsvg.se(thing, shape="rounded_rectangle", style="plate",
             size=[label_width, label_height, depth], r=3.0, pos=pos1)

    # header bar
    pos1 = copy.deepcopy(pos)
    pos1[1] += header_y
    opsvg.se(thing, shape="rect", style="header",
             size=[label_width, header_height, depth], pos=pos1)

    # header title
    pos1 = copy.deepcopy(pos)
    pos1[1] += header_y
    opsvg.se(thing, shape="text", style="header.label",
             text="OOMLOUT", size=9.0, pos=pos1)

    # bullet mark (accent dot)
    pos1 = copy.deepcopy(pos)
    pos1[0] -= label_width / 2 - 8.0
    pos1[1] += header_y - header_height - 4.0
    opsvg.se(thing, shape="circle", style="plate.accent",
             r=1.5, pos=pos1)

    # part name
    pos1 = copy.deepcopy(pos)
    pos1[0] -= label_width / 2 - 13.0
    pos1[1] += header_y - header_height - 4.0
    opsvg.se(thing, shape="text", style="label",
             text="Bracket  4 x 2", size=5.0, halign="left", valign="center", pos=pos1)

    # description (muted)
    pos1 = copy.deepcopy(pos)
    pos1[0] -= label_width / 2 - 6.0
    pos1[1] += header_y - header_height - 11.0
    opsvg.se(thing, shape="text", style="label.muted",
             text="L-shaped laser-cut plate", size=4.0, halign="left", valign="center", pos=pos1)

    # part number footer (mono, bottom-right)
    pos1 = copy.deepcopy(pos)
    pos1[0] += label_width  / 2 - 4.0
    pos1[1] -= label_height / 2 - 5.0
    opsvg.se(thing, shape="text", style="label.mono",
             text="OOBB-BKT-4x2-001", size=3.0, halign="right", valign="center", pos=pos1)

    if prepare_print:
        svg_help.prepare_base_for_print(thing, pos, **kwargs)


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
