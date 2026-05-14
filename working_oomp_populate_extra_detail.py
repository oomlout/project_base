import working_oomp_populate

def main(**kwargs):
    extras = kwargs.get("extras", [])
    extras_dict = {}
    for extra in extras:
        oomp_id =  working_oomp_populate.build_oomp_id(extra)
        extras_dict[oomp_id] = extra

    ######add notes here
    current = "warehouse_storage_kallax_front_room_location_d_column_3_row"
    if False:
        extras_dict[current]["content_taxonomy_1"] = "three_d_print"
        extras_dict[current]["content_taxonomy_2"] = "filament"
        extras_dict[current]["content_taxonomy_3"] = "empty_spool"
        extras_dict[current]["content_id"] = "three_d_print_filament_empty_spool"
    