import numpy as np
import pandas as pd

# dff: dstaframe from defined huc6 and catchid
def get_stage(dff, discharge):  # e.g., get_stage('120100', 15085173, 800) string, int, float

    col_discharge = dff.columns.tolist()[len(dff.columns) - 1]
    array = np.array(dff[col_discharge])
    list_output = []
    idx = (np.abs(array - discharge)).argmin()
    list_output.append(idx)

    if array[idx] - discharge < 0:
        idx2 = idx + 1
    else:
        idx2 = idx - 1
    list_output.append(idx2)
    list_output.sort()

    # interporlate
    slope = (dff.iloc[list_output[1]].Stage - dff.iloc[list_output[0]].Stage) / (dff.iloc[list_output[1]][col_discharge] - dff.iloc[list_output[0]][col_discharge])
    stage = slope * (discharge - dff.iloc[list_output[0]][col_discharge]) + dff.iloc[list_output[0]].Stage

    return stage

if __name__ == "__main__":

    # Load max discharge csv file
    # Step 1: load discharge file
    # columns should include: huc6, catchid, max_discharge
    # for example a row should look [location_id, latitude, longitude, huc6, catchid, max_discharge]

    # Step 2: Remove NaN

    # Iterate over locations
    max_discharge_url = 'aa'  # define a location
    max_discharge = 'max_discharge.csv'
    df_discharge = pd.read_csv(max_discharge_url + max_discharge)

    huc6_list = df_discharge.huc6.unique().tolist()

    for this_huc6 in huc6_list:
        url = '/home/jupyter/tacc-work/hand/version-0.2.1/files/'
        set_url = url + this_huc6 + '/'
        table_name = ('hydrogeo-fulltable-%s.csv' % this_huc6)
        df_ratingcurve = pd.read_csv(set_url + table_name)

        this_df = df_discharge[df_discharge.huc6 == this_huc6]

        for i in range(len(this_df)):
            dict_stage = {}
            this_location = this_df.iloc[i].location_id
            this_catchid = this_df.iloc[i].catchid
            this_discharge = this_df.iloc[i].max_discharge
            dff = df_ratingcurve[df_ratingcurve.CatchId == this_catchid]
            dict_stage[location_id] = get_stage(dff, discharge)

        df_discharge['stage'] = df_discharge['location_id'].map(dict_stage)

    output_file_name = 'stage_output.xlsx'
    output_file_location = '/work/06447/kykim/hand/input_discharge/'
    output_thread = output_file_name + output_file_location
    df_discharge.to_excel(output_file_name)
