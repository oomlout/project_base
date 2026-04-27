
import copy
import itertools

from requests import options

from oomp_populate_helper import write_extras


def main(**kwargs):
    # Define default input dict with all required fields
    default_input = {
        "taxonomy_1": "organizing",
        "taxonomy_2": "electrical",
        "taxonomy_3": "wire",
        "taxonomy_4": "hole_cover",
        "taxonomy_5": "",
        "taxonomy_6": "",
        "taxonomy_7": "",
        "taxonomy_8": "",
        # Add any additional details here
    }
     
    
    #### define extra entries
    #taxonomy_3 hole_diameter
    #taxonomy_4 
    #taxonomy_5 
    #taxonomy_6 
    #taxonomy_7 
    #taxonomy_14 manufacturer
    #taxonomy_15 manufacturer_part_number
    options = []
    #define single parts (take the default options add one with the extra details)
    option = {}
    
    ############################# examples
    #flourescent green # multiline example
    if False:        
        #taxonomy_4 80 gsm        
        option["taxonomy_4"] = "80_gsm"
        option["taxonomy_5"] = "green_flourescent"
        option["taxonomy_14"] = "papago"
        option["taxonomy_15"] = "21403"
        options.append(copy.deepcopy(option))
    
    #flourescent green # singleline example
    if False:        
        options.append({"taxonomy_4": "80_gsm",       "taxonomy_5": "green_flourescent",  "taxonomy_14": "papago",    "taxonomy_15": "21403"})
        
    #40_mm diameter 15_mm depth
    if True:        
        option["taxonomy_3"] = "40_mm_diameter"
        option["diameter"] = 40
        option["taxonomy_4"] = "15_mm_depth"
        option["depth"] = 15
        #option["taxonomy_5"] = ""
        #option["taxonomy_14"] = "papago"
        #option["taxonomy_15"] = "21403"
        options.append(copy.deepcopy(option))
    


    ###### oobb_details stuff
    if True:
        for option in options:
            #option = options[option_id]
            oobb_details = {}
            oobb_details["oobb_name"] = "hole_cover"            
            oobb_details["diameter"] = option.get("diameter", None)            
            oobb_details["depth"] = option.get("depth", None)
            option["oobb_details"] = oobb_details
    

    extras = []
    for option in options:
        extra = copy.deepcopy(default_input)
        extra.update(option)
        
        
        extras.append(extra)



    write_extras(extras, default_input)



# Call main automatically
if __name__ == "__main__":
    main()
