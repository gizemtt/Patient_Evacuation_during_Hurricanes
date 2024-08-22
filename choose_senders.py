import pandas as pd
import os
import geopandas as gpd
# from tools.combine_nwm_scenarios import combine_nwm_output

# ---------------------------------------------------------
# SENDER GENERATION FUNCTION WITH PRECIPITATION TRANSLATION
# ---------------------------------------------------------

def senderGen(scenario_number, dict_hospital_grid, dict_path, dict_parameter, df_stage, df_sender):

    # GET INPUT PARAMETER INFORMATION
    threshold_height_inches = int(dict_parameter['threshold_height'])   # in inches
    path_data = dict_path['data']
    path_slosh = dict_path['slosh']
    list_sender = df_sender.code.tolist()

    # GET ELEVATION (in meters)
    dict_elevation = {}

    for i in range(len(df_sender)):
        this_objectid = df_sender.iloc[i]['id']
        this_code = df_sender.iloc[i]['nid']
        this_elevation = df_stage[df_stage['id'] == this_objectid]['dem'].values[0]
        dict_elevation[this_code] = this_elevation

    # GET MAX NWM HEIGHT DATA
    dict_hand = dict(zip(df_stage.code, df_stage['hand']))

    # DEFINE FLOOD THRESHOLD
    inches_to_meters = 0.0254
    ft_to_meters = 0.3048
    threshold_height_m = threshold_height_inches * inches_to_meters  # thresold height for surge: 2 meters

    # --------------------------------------------
    # GET SENDERS FROM SLOSH
    # EXAMPLE: scenario_number = ['n', '3', '05i2', '5-1']
    # --------------------------------------------
    this_slosh_scenario = scenario_number[0] + scenario_number[1] + scenario_number[2]
    this_slosh_scenario_file = this_slosh_scenario + '.shp'
    slosh_file_location = path_slosh + '\\meow\\shp\\' + scenario_number[0]
    sf_slosh = gpd.read_file( os.path.join(slosh_file_location , this_slosh_scenario_file))
    sf_slosh = sf_slosh[sf_slosh[this_slosh_scenario] != 99.9]
    sf_slosh['surge'] = sf_slosh[this_slosh_scenario] + sf_slosh['topography']

    sender_dict_SLOSH = {}
    for i in list_sender:
        this_nid = df_sender.loc[df_sender['code'] == i]['nid'].values[0]
        if this_nid in list(dict_hospital_grid.keys()):
            sender_elevation = dict_elevation[this_nid]
            sender_grid = dict_hospital_grid[this_nid]

            try:
                sender_surge = sf_slosh[sf_slosh['Poly_id'] == sender_grid]['surge'].values[0] * ft_to_meters
            except IndexError:
                continue

            relative_depth = sender_surge - sender_elevation  # unit: meters
            sender_depth = max(relative_depth, 0)

            if sender_depth > threshold_height_m:
                sender_dict_SLOSH[i] = sender_depth

        else:
            continue

    # --------------------
    # GET SENDERS FROM NWM
    # --------------------
    this_nwm_scenario = scenario_number[3]
    dict_stage = dict(zip(df_stage.code, df_stage[this_nwm_scenario]))

    dict_depth = {key: float(dict_stage[key]) - dict_hand.get(key, 0) for key in dict_stage.keys()}
    sender_dict_NWM = dict((k, v) for k, v in dict_depth.items() if v > threshold_height_m)

    # -----------------------------------
    # COMBINE SENDERS FROM SLOSH AND NWM
    # -----------------------------------
    inundated = {k: max(i for i in (sender_dict_SLOSH.get(k), sender_dict_NWM.get(k)) if i) for k in sender_dict_SLOSH.keys() | sender_dict_NWM}
    print("    Number of senders [SLOSH, NWM, ALL]: ", [len(sender_dict_SLOSH.keys()), len(sender_dict_NWM.keys()), len(inundated.keys())])
    # print(inundated.keys())
    print('')
    set_inundated = [sender_dict_SLOSH, sender_dict_NWM, inundated]

    return set_inundated
