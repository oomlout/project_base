
import copy
import itertools

from requests import options

from oomp_populate_helper import build_oomp_id, write_extras


def main(**kwargs):
    
    options = []
    
    

    if True:
        option = {}
        option["width"] = "1"
        option["height"] = "1"
        option["name"] = "test"
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
            option["taxonomy_1"] = f"first_item"  
            option["taxonomy_2"] = f"second_item"             
            value_name = "code"
            value = option.get(value_name, None)
            option["taxonomy_3"] = f"{value}_{value_name}"
            #oobb details
            if False:
                pass
                oobb_details = {}
                #taxonomy_4 hole_cover
                oobb_details["oobb_name"] = option_type
                oobb_details["diameter"] = option.get("diameter", None)            
                oobb_details["depth"] = option.get("depth", None)
                option["oobb_details"] = oobb_details
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
