
import copy
import itertools

from requests import options

from oomp_populate_helper import build_oomp_id, write_extras


def main(**kwargs):
    
    options = []
    #define single parts (take the default options add one with the extra details)
    option = {}
    

    if True:
          
        option["person"] = "maya"
        option["reason"] = "birthday"
        option["age"] = "6"
        option["theme_1"] = "star"
        option["theme_2"] = ""
        option["theme_3"] = ""
        option["theme_4"] = ""
        option["theme_5"] = ""
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
            option["taxonomy_3"] = f"{option.get('reason', '')}_reason"
            option["taxonomy_4"] = f"{option.get('age', '')}_age"
            theme_string = ""
            for i in range(1, 6):
                theme_string += f"{option.get(f'theme_{i}', '')}_"
            theme_string = theme_string.rstrip("_")          
            option["taxonomy_5"] = f"{theme_string}_theme"
            option["taxonomy_6"] = f"{option.get('person', '')}_person"
            if False:
                pass
                oobb_details = {}
                #taxonomy_4 hole_cover
                oobb_details["oobb_name"] = option_type
                oobb_details["diameter"] = option.get("diameter", None)            
                oobb_details["depth"] = option.get("depth", None)
                option["oobb_details"] = oobb_details
    

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
