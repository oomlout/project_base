import copy
import opsc
import oobb
import yaml
import os
import scad_help
import math

def main(**kwargs):
    make_scad(**kwargs)

def make_scad(**kwargs):
    typ = scad_help.get_typ(**kwargs)
    oomp_mode = "project"
    #oomp_mode = "oobb"
    filt = ""
    build_variables = scad_help.get_build_variables(typ, filter=filt)
    if True:
        kwargs["filter"] = build_variables["filter"]
        kwargs["save_type"] = build_variables["save_type"]
        kwargs["navigation"] = build_variables["navigation"]
        kwargs["overwrite"] = build_variables["overwrite"]
        kwargs["modes"] = build_variables["modes"]
        kwargs["oomp_mode"] = oomp_mode
        kwargs["oomp_run"] = build_variables["oomp_run"]

    project_name = scad_help.get_project_name(__file__)

    scad_help.add_default_project_kwargs(kwargs, project_name, oomp_mode)

    parts = get_parts(kwargs, project_name, oomp_mode)
    
    kwargs["parts"] = parts

    scad_help.make_parts(**kwargs)

    if kwargs["navigation"]:
        scad_help.generate_navigation(sort=scad_help.get_navigation_sort())

def get_parts(kwargs, project_name, oomp_mode):
    parts = []
    part_default = scad_help.get_default_part(project_name)

    heights = [1,4]    
    widths = [1,3,4]
    depths = [90, 128]
    extras = [3]
    names = []
    names.append("shelf")
    names.append("shelf_stack")
    if True:    
        for height in heights:
            for width in widths:
                for depth in depths:
                    for extra in extras:
                        for name in names:
                            shelf_count = extra
                            
                            part = copy.deepcopy(part_default)
                            p3 = copy.deepcopy(kwargs)
                            p3["width"] = width
                            p3["height"] = height
                            p3["thickness"] = depth
                            p3["shelf_count"] = shelf_count
                            p3["extra"] = f"{shelf_count}_shelf_count"
                            part["kwargs"] = p3
                            nam = name
                            part["name"] = nam
                            if oomp_mode == "oobb":
                                p3["oomp_size"] = nam
                            parts.append(part)




    return parts

def get_base(thing, **kwargs):

    prepare_print = kwargs.get("prepare_print", False)
    width = kwargs.get("width", 1)
    height = kwargs.get("height", 1)
    depth = kwargs.get("thickness", 3)                    
    rot = kwargs.get("rot", [0, 0, 0])
    pos = kwargs.get("pos", [0, 0, 0])
    extra = kwargs.get("extra", "")
    
    #add plate
    p3 = copy.deepcopy(kwargs)
    p3["type"] = "positive"
    p3["shape"] = f"oobb_plate"    
    p3["depth"] = depth
    #p3["holes"] = True         uncomment to include default holes
    #p3["m"] = "#"
    pos1 = copy.deepcopy(pos)         
    p3["pos"] = pos1
    oobb.append_full(thing,**p3)
    
    #add holes seperate
    p3 = copy.deepcopy(kwargs)
    p3["type"] = "p"
    p3["shape"] = f"oobb_holes"
    p3["both_holes"] = True  
    p3["depth"] = depth
    p3["holes"] = "perimeter"
    #p3["m"] = "#"
    pos1 = copy.deepcopy(pos)         
    p3["pos"] = pos1
    oobb.append_full(thing,**p3)

    #add a test screw_countersunk
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "p"
        p3["shape"] = f"screw_countersunk"
        p3["depth"] = depth
        p3["radius_name"] = "m3"
        pos1 = copy.deepcopy(pos)         
        p3["pos"] = pos1
        p3["m"] = "#"
        oobb.append_full(thing,**p3)

    if prepare_print:
        scad_help.prepare_base_for_print(thing, pos, **kwargs)

def get_shelf(thing, **kwargs):

    prepare_print = kwargs.get("prepare_print", False)
    width = kwargs.get("width", 1)
    height = kwargs.get("height", 1)
    depth = kwargs.get("thickness", 3)                    
    rot = kwargs.get("rot", [0, 0, 0])
    pos = kwargs.get("pos", [0, 0, 0])
    extra = kwargs.get("extra", "")
    
    shelf_count = kwargs.get("shelf_count", 1)

    #add the cubes
    width_mm = width * 42
    height_mm = height * 42
    depth_mm = depth        
    thickness_wall = 3
    thickness_floor = 3
    if True:
        #base
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "positive"
        p3["shape"] = f"oobb_cube"
        p3["size"] = [width_mm, height_mm, depth_mm]
        pos1 = copy.deepcopy(pos)         
        pos1[0] += 0
        p3["pos"] = pos1
        #p3["m"] = "#"
        oobb.append_full(thing,**p3)
        
        #add the shelf cutouts
        if True:
            spacing = (depth_mm - thickness_floor) / shelf_count
            shelf_height = spacing - thickness_wall
            p3 = copy.deepcopy(kwargs)
            p3["type"] = "negative"
            p3["shape"] = f"oobb_cube"
            wid = width_mm - thickness_wall * 2
            hei = height_mm - thickness_wall 
            dep = shelf_height
            p3["size"] = [wid, hei, dep]
            pos1 = copy.deepcopy(pos)
            pos1[1] += -thickness_wall/2
            pos1[2] += thickness_floor
            #p3["m"] = "#"
            poss = []
            for i in range(shelf_count):
                pos11 = copy.deepcopy(pos1)
                pos11[2] += i * spacing
                poss.append(pos11)
            p3["pos"] = poss
            oobb.append_full(thing,**p3)

    #add a width x height array of gridfinity_tbase_tile
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "positive"
        p3["shape"] = f"gridfinity_base_tile"
        p3["width"] = width
        p3["height"] = height
        pos1 = copy.deepcopy(pos)         
        pos1[2] += 1.5
        poss = []
        for i in range(width):
            for j in range(height):
                pos11 = copy.deepcopy(pos1)
                pos11[0] += (i - (width - 1) / 2) * 42
                pos11[1] += (j - (height - 1) / 2) * 42
                poss.append(pos11)
        p3["pos"] = poss
        #p3["m"] = "#"   
        oobb.append_full(thing,**p3)

    #add a width x depth array of gridfinity_base_tile on the back
    if True:
        depth_tiles = max(1, math.floor(depth_mm / 42))
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "positive"
        p3["shape"] = f"gridfinity_base_tile"
        p3["rot"] = [90, 0, 0]
        pos1 = copy.deepcopy(pos)
        pos1[1] += height_mm / 2 + 4.5
        pos1[2] += depth_mm / 2 + 8
        poss = []
        for i in range(width):
            for j in range(depth_tiles):
                pos11 = copy.deepcopy(pos1)
                pos11[0] += (i - (width - 1) / 2) * 42
                pos11[2] += (j - (depth_tiles - 1) / 2) * 42
                poss.append(pos11)
        p3["pos"] = poss
        oobb.append_full(thing,**p3)

    #add a test screw_countersunk
    if False:
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "p"
        p3["shape"] = f"screw_countersunk"
        p3["depth"] = depth
        p3["radius_name"] = "m3"
        pos1 = copy.deepcopy(pos)         
        p3["pos"] = pos1
        p3["m"] = "#"
        oobb.append_full(thing,**p3)

    if prepare_print:
        scad_help.prepare_base_for_print(thing, pos, **kwargs)


def get_shelf_stack(thing, **kwargs):

    prepare_print = kwargs.get("prepare_print", False)
    width = kwargs.get("width", 1)
    height = kwargs.get("height", 1)
    depth = kwargs.get("thickness", 3)                    
    rot = kwargs.get("rot", [0, 0, 0])
    pos = kwargs.get("pos", [0, 0, 0])
    extra = kwargs.get("extra", "")
    
    shelf_count = kwargs.get("shelf_count", 1)

    width_mm = width * 42
    height_mm = height * 42
    depth_mm = depth
    thickness_wall = 3
    thickness_floor = 3
    stack_clearance = kwargs.get("stack_clearance", 0.35)
    bead_height = kwargs.get("bead_height", 1.2)
    print_shift = kwargs.get("print_shift", width_mm + 120)
    spacing = (depth_mm - thickness_floor) / max(1, shelf_count)
    bead_radius = kwargs.get("bead_radius", max(0.8, thickness_wall / 2 - stack_clearance))
    socket_radius = bead_radius + stack_clearance
    positive_bead_radius = max(0.1, bead_radius - 0.15 / 2)
    positive_length_shrink = kwargs.get("positive_length_shrink", 0.5)
    slice_bounds = [[0, thickness_floor]]
    bottom_bump_trim = kwargs.get("bottom_bump_trim", 5)
    back_bump_trim = kwargs.get("back_bump_trim", 0)
    non_base_slice_extra = kwargs.get("non_base_slice_extra", 10)
    first_slice_relief = kwargs.get("first_slice_relief", 0)
    bead_z_offset = kwargs.get("bead_z_offset", bead_radius)
    positive_bead_z_extra = kwargs.get("positive_bead_z_extra", bead_radius)
    positive_bead_x_offset = kwargs.get("positive_bead_x_offset", -bead_radius / 2)

    for i in range(max(1, shelf_count)):
        start_z = thickness_floor + i * spacing
        end_z = thickness_floor + (i + 1) * spacing
        slice_bounds.append([start_z, end_z])

    def add_cube(part_type, size, position, mark=""):
        p3 = copy.deepcopy(kwargs)
        p3["type"] = part_type
        p3["shape"] = "oobb_cube"
        p3["size"] = size
        p3["pos"] = position
        if mark != "":
            p3["m"] = mark
        oobb.append_full(thing, **p3)

    def add_cylinder(part_type, depth_value, radius_value, position, rotation, mark=""):
        p3 = copy.deepcopy(kwargs)
        p3["type"] = part_type
        p3["shape"] = "oobb_cylinder"
        p3["depth"] = depth_value
        p3["radius"] = radius_value
        pos1 = copy.deepcopy(position)
        # oobb_cylinder applies a depth/2 z shift before rotation, so compensate
        # here for horizontal cylinders to keep the bead on the intended plane.
        if rotation != [0, 0, 0]:
            pos1[2] += depth_value / 2
        # Shift horizontal cylinders back by half their length so the rotated
        # primitive lands on the intended wall centerline.
        if rotation == [90, 0, 0]:
            if part_type in ["positive", "positive_positive"]:
                pos1[1] += depth_value / 2
        if rotation == [0, 90, 0]:
            pos1[0] += depth_value / 2
        p3["pos"] = pos1
        p3["rot"] = rotation
        p3["zz"] = "center"
        if mark != "":
            p3["m"] = mark
        oobb.append_full(thing, **p3)

    def add_slice_clipping(module_pos, slice_start, slice_end):
        trim_size_xy = [width_mm + 80, height_mm + 80, depth_mm + 80]

        if slice_start > 0:
            clip_relief = first_slice_relief if slice_start == thickness_floor else 0
            add_cube(
                "negative",
                [trim_size_xy[0], trim_size_xy[1], slice_start + non_base_slice_extra - clip_relief],
                [module_pos[0], module_pos[1], module_pos[2] - non_base_slice_extra],
            )

        top_trim_height = depth_mm - slice_end + 80
        if top_trim_height > 0:
            add_cube(
                "negative",
                [trim_size_xy[0], trim_size_xy[1], top_trim_height],
                [module_pos[0], module_pos[1], module_pos[2] + slice_end],
            )

    def add_gridfinity_bump_trimming(module_pos, trim_bottom):
        if back_bump_trim > 0:
            add_cube(
                "negative",
                [width_mm + 20, back_bump_trim, depth_mm + 20],
                [module_pos[0], module_pos[1] + height_mm / 2, module_pos[2] - 10],
                "#",
            )

    def add_stack_interface(module_pos, slice_start, slice_end, add_bead, add_socket):
        upper_interface_drop = thickness_wall * 3 / 4 if slice_start > thickness_floor else 0
        first_interface_relief = first_slice_relief if slice_start == thickness_floor else 0
        socket_z = module_pos[2] + slice_end
        if slice_start == thickness_floor:
            bead_z = module_pos[2] + thickness_floor
        else:
            bead_z = module_pos[2] + slice_start + bead_z_offset + positive_bead_z_extra - upper_interface_drop - first_interface_relief
        side_depth = max(1, height_mm - thickness_wall)
        back_depth = max(1, width_mm - thickness_wall * 2)

        if add_bead:
            cylinders = [
                (side_depth - positive_length_shrink, positive_bead_radius, [module_pos[0] - width_mm / 2 + thickness_wall / 2, module_pos[1], bead_z], [90, 0, 0]),
                (side_depth - positive_length_shrink, positive_bead_radius, [module_pos[0] + width_mm / 2 - thickness_wall / 2, module_pos[1], bead_z], [90, 0, 0]),
                (back_depth - positive_length_shrink, positive_bead_radius, [module_pos[0] - back_depth + positive_bead_x_offset, module_pos[1] + height_mm / 2 - thickness_wall / 2, bead_z], [0, 90, 0]),
            ]
            for depth_value, radius_value, position, rotation in cylinders:
                add_cylinder("positive_positive", depth_value, radius_value, position, rotation)

        if add_socket:
            sockets = [
                (side_depth, socket_radius, [module_pos[0] - width_mm / 2 + thickness_wall / 2, module_pos[1] + side_depth / 2, socket_z], [90, 0, 0]),
                (side_depth, socket_radius, [module_pos[0] + width_mm / 2 - thickness_wall / 2, module_pos[1] + side_depth / 2, socket_z], [90, 0, 0]),
                (back_depth, socket_radius, [module_pos[0] - back_depth, module_pos[1] + height_mm / 2 - thickness_wall / 2, socket_z], [0, 90, 0]),
            ]
            for depth_value, radius_value, position, rotation in sockets:
                add_cylinder("negative", depth_value, radius_value, position, rotation, "#")

    for i, bounds in enumerate(slice_bounds):
        slice_start = bounds[0]
        slice_end = bounds[1]
        module_pos = copy.deepcopy(pos)
        module_pos[0] += i * print_shift

        p3 = copy.deepcopy(kwargs)
        p3["prepare_print"] = False
        p3["pos"] = module_pos
        get_shelf(thing, **p3)

        # add_cube(
        #     "positive",
        #     [width_mm + 200, depth_mm + 200, 1],
        #     [module_pos[0], module_pos[1], module_pos[2] + thickness_floor + spacing],
        #     "#",
        # )

        add_gridfinity_bump_trimming(module_pos, trim_bottom=i > 0)
        add_slice_clipping(module_pos, slice_start, slice_end)
        add_stack_interface(
            module_pos,
            slice_start,
            slice_end,
            add_bead=i > 0,
            add_socket=i < len(slice_bounds) - 1,
        )

    #add a test screw_countersunk
    if False:
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "p"
        p3["shape"] = f"screw_countersunk"
        p3["depth"] = depth
        p3["radius_name"] = "m3"
        pos1 = copy.deepcopy(pos)         
        p3["pos"] = pos1
        p3["m"] = "#"
        oobb.append_full(thing,**p3)

    if prepare_print:
        scad_help.prepare_base_for_print(thing, pos, **kwargs)

if __name__ == '__main__':
    kwargs = {}
    main(**kwargs)
