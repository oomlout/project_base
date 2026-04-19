import copy
import opsc
import oobb
import oobb_base
import yaml
import os
import scad_help

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

    parts = get_parts(kwargs, project_name, oomp_mode, test=build_variables["test"])
    
    kwargs["parts"] = parts

    scad_help.make_parts(**kwargs)

    if kwargs["navigation"]:
        scad_help.generate_navigation(sort=scad_help.get_navigation_sort())

def get_parts(kwargs, project_name, oomp_mode, test=False):
    parts = []
    part_default = scad_help.get_default_part(project_name)

    part = copy.deepcopy(part_default)
    p3 = copy.deepcopy(kwargs)
    p3["width"] = 2
    p3["height"] = 3
    p3["thickness"] = 30
    #p3["extra"] = ""
    part["kwargs"] = p3
    nam = "drawer_basic"
    part["name"] = nam

    if oomp_mode == "oobb":
        p3["oomp_size"] = nam

    if not test:
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
    oobb_base.append_full(thing,**p3)
    
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
    oobb_base.append_full(thing,**p3)

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
        oobb_base.append_full(thing,**p3)

    if prepare_print:
        scad_help.prepare_base_for_print(thing, pos, **kwargs)

def get_drawer_basic(thing, **kwargs):

    prepare_print = kwargs.get("prepare_print", False)
    width = kwargs.get("width", 1)
    height = kwargs.get("height", 1)
    depth = kwargs.get("thickness", 3)                    
    rot = kwargs.get("rot", [0, 0, 0])
    pos = kwargs.get("pos", [0, 0, 0])
    extra = kwargs.get("extra", "")
    
    if False:
        #add plate
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "positive"
        p3["shape"] = f"oobb_plate"    
        p3["depth"] = depth
        #p3["holes"] = True         uncomment to include default holes
        #p3["m"] = "#"
        pos1 = copy.deepcopy(pos)         
        p3["pos"] = pos1
        oobb_base.append_full(thing,**p3)
        
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
        oobb_base.append_full(thing,**p3)

    #add the cubes
    width_mm = width * 42 - 3
    height_mm = height * 42 - 3
    depth_mm = depth
    thickness_wall = 1.5
    if True:
        #base
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "positive"
        p3["shape"] = f"oobb_cube"
        p3["size"] = [width_mm, height_mm, thickness_wall]
        pos1 = copy.deepcopy(pos)         
        p3["pos"] = pos1
        oobb_base.append_full(thing,**p3)
        #front and back
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "positive"
        p3["shape"] = f"oobb_cube"
        p3["size"] = [width_mm, thickness_wall, depth_mm]
        pos1 = copy.deepcopy(pos)        
        pos1[2] += 0
        poss = []
        pos11 = copy.deepcopy(pos1)
        pos11[1] += (height_mm - thickness_wall) / 2
        poss.append(pos11)
        pos12 = copy.deepcopy(pos1)
        pos12[1] -= (height_mm - thickness_wall) / 2
        poss.append(pos12)
        p3["pos"] = poss
        oobb_base.append_full(thing,**p3)
        #sides
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "positive"
        p3["shape"] = f"oobb_cube"
        p3["size"] = [thickness_wall, height_mm, depth_mm]
        pos1 = copy.deepcopy(pos)
        pos1[0] += 0
        pos1[2] += 0
        poss = []
        pos11 = copy.deepcopy(pos1)
        pos11[0] += (width_mm - thickness_wall) / 2
        poss.append(pos11)
        pos12 = copy.deepcopy(pos1)
        pos12[0] -= (width_mm - thickness_wall) / 2
        poss.append(pos12)
        p3["pos"] = poss
        oobb_base.append_full(thing,**p3)

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
        oobb_base.append_full(thing,**p3)

    if prepare_print:
        scad_help.prepare_base_for_print(thing, pos, **kwargs)

if __name__ == '__main__':
    kwargs = {}
    main(**kwargs)