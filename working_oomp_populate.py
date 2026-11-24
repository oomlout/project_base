
import copy
import itertools

from requests import options

from oomp_populate_helper import build_oomp_id, write_extras


def main(**kwargs):
    
    options = []
    
    

    if True:
        option = {}
        option["width"] = 3
        option["height"] = 5
        option["depth"] = 27
        option["oobb_type"] = "shortener_inline"
        options.append(copy.deepcopy(option))
        
    
    #load from working_manual.yaml
    if False:
        with open("working_manual.yaml", 'r', encoding='utf-8') as file:
            import yaml
            data = yaml.safe_load(file)
            options_yaml = data.get("options", [])
            for option_yaml in options_yaml:
                options.append(option_yaml)

    
    ###### populate taxonomy details and oobb details
    if True:
        for option in options:       
            option["taxonomy_1"] = f"oobb"  
            option["taxonomy_2"] = f"part"  
            option["taxonomy_3"] = f"holder"  
            option["taxonomy_4"] = f"electronic"
            option["taxonomy_5"] = f"wire"
            count = 6
            if True:
                value_name = "oobb_type"
                value = option.get(value_name, None)
                option[f"taxonomy_{count}"] = f"{value}_{value_name}"
            # oobb_type selects get_<type> independently in each backend.
            if option.get("oobb_type"):
                option["oobb_details"] = {                    
                    "run_scad": option.get("run_scad", True),
                    # True: native recipe; False: off; "working_scad": shared source.
                    "run_solidcraft": option.get("run_solidcraft", False),
                }
                option["oobb_details"].update(copy.deepcopy(option))
            #svg details
            if False:
                pass
                svg_details = {}
                svg_details["svg_name"] = option_type
                svg_details["svg_width"] = option.get("width", None)            
                svg_details["svg_height"] = option.get("height", None)
                option["svg_details"] = svg_details

    #load the options into full list
    extras = []
    for option in options:
        extra = {}
        extra.update(option)
        extras.append(extra)

    
    ######### add notes from an id string
    import working_oomp_populate_extra_detail
    working_oomp_populate_extra_detail.main(extras=extras)


    write_extras(extras)



# Call main automatically
if __name__ == "__main__":
    main()
