
import copy
import os
import yaml


def build_oomp_id(d):
    fields = [
        d.get("taxonomy_1", ""),
        d.get("taxonomy_2", ""),
        d.get("taxonomy_3", ""),
        d.get("taxonomy_4", ""),
        d.get("taxonomy_5", ""),
        d.get("taxonomy_6", ""),
        d.get("taxonomy_7", ""),
        d.get("taxonomy_8", "")
    ]
    # Only include non-empty fields, join with underscores
    return '_'.join([str(f).strip().replace(' ', '_') for f in fields if f])


def main(**kwargs):
    # Define default input dict with all required fields
    default_input = {
        "taxonomy_1": "electrical",
        "taxonomy_2": "extension_lead",
        "taxonomy_3": "uk_socket",
        "taxonomy_4": "6_outlet",
        "taxonomy_5": "pro_elec",
        "taxonomy_6": "2068",
        "taxonomy_7": "",
        "taxonomy_8": "",
        # Add any additional details here
    }
     
    
    #### define extra entries
    
    options = []
    if True:
        option = {}
        #reason 600 house points        
        option["source_main_url"] = "https://uk.farnell.com/pro-elec/2068-10m/extension-lead-6way-10m/dp/1286484#anchorTechnicalDOCS"
        options.append(option)
    
    #define parts here
    if True:
        option = {}
        option["oobb"] = True
        option["width"] = 1
        option["height"] = 1
        option["depth"] = 3
        #name oobb_holder
        option["name"] = "holder"
        options.append(option)

    extras = []
    for option in options:
        extra = copy.deepcopy(default_input)
        extra.update(option)
        
        
        extras.append(extra)

    write_extras(extras, default_input)

def write_extras(extras, default_input):
    
    for input_dict in extras:
        oobb = input_dict.get("oobb", False)
        if oobb:
            oomp_id_item = build_oomp_id(input_dict)
            new_dict = copy.deepcopy(input_dict)
            #"" out all taxonom 1-15
            for i in range(1, 18):
                new_dict[f"taxonomy_{i}"] = ""
            #redefine start with oobb
            count = 1
            new_dict[f"taxonomy_{count}"] = "oobb"
            count += 1
            name = input_dict.get("name", "")
            if name:
                new_dict[f"taxonomy_{count}"] = name
                count += 1
            width = input_dict.get("width", 1)
            new_dict[f"taxonomy_{count}"] = f"{width}_width"
            count += 1
            height = input_dict.get("height", 1)
            new_dict[f"taxonomy_{count}"] = f"{height}_height"
            count += 1
            depth = input_dict.get("depth", 1)
            new_dict[f"taxonomy_{count}"] = f"{depth}_depth"
            count += 1
            extra = input_dict.get("extra", "")            
            if extra:
                new_dict[f"taxonomy_{count}"] = extra
                count += 1
            #add oomp_id_item to details
            #check currrent oomp_id length
            test_id = build_oomp_id(new_dict)
            max_length = 200
            length_total = len(test_id) + len(oomp_id_item) + 1
            oomp_id_include = oomp_id_item
            if length_total > max_length:
                #calculate how many characters to remove from oomp_id_item
                excess_length = length_total - max_length
                oomp_id_include = oomp_id_item[:-excess_length]
            new_dict[f"taxonomy_{count}"] = oomp_id_include
            input_dict = new_dict            
        details = copy.deepcopy(default_input)
        details.update(input_dict)
        oomp_id = build_oomp_id(details)
        if not oomp_id:
            oomp_id = "default_empty"
        folder_path = os.path.join("parts_source", oomp_id)
        os.makedirs(folder_path, exist_ok=True)
        yaml_path = os.path.join(folder_path, "working.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(details, f, allow_unicode=True)
        #check for files in source_file
        filenames = ["datasheet.pdf", "image.jpg", "diagram.af"]
        oomp_id = build_oomp_id(details)
        for filename in filenames:
            source_path = os.path.join("source_file", f"{oomp_id}_{filename}")
            if os.path.exists(source_path):
                dest_path = os.path.join(folder_path, filename)
                if not os.path.exists(dest_path):
                    with open(source_path, "rb") as src_file:
                        with open(dest_path, "wb") as dst_file:
                            dst_file.write(src_file.read())
            else:
                pass
                #print(f"Warning: Source file {filename} not found in source_files directory.")
        


# Call main automatically
if __name__ == "__main__":
    main()
