import pandas as pd
from get_hospitals import getHospitals
import geopandas as gpd

def combine_shp():
    counties = ['Austin', 'Brazoria', 'Chambers', 'Colorado', 'Fort Bend', 'Galveston', 'Hardin', 'Harris', 'Jefferson', 'Liberty', 'Matagorda', 'Montgomery', 'Orange', 'Walker', 'Waller', 'Wharton']

    path_sh = '/Users/kyoung/Box Sync/github/data/shp/tx_county/'
    file_sh = 'County.shp'
    sf = gpd.read_file(path_sh + file_sh)

    region = []
    for i in range(len(sf)):
        if sf.iloc[i]['CNTY_NM'] in counties:
            indicator = 'y'
        else:
            indicator = 'n'
        region.append(indicator)
    sf['PH_65'] = region

    # get SETRAC COUNTIES MAP (shp: sff)
    sf_ph = sf.dissolve(by='PH_65')
    sff = sf_ph.drop(['n'])
    sff.to_file('/Users/kyoung/Box Sync/github/data/shp/tx_county/setrac_cnty.shp')

    # get HWM locations
    path_hwm = '/Users/kyoung/Box Sync/github/data/hwm/'
    file_hwm = 'FilteredHWMs.csv'
    df = pd.read_csv(path_hwm + file_hwm)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

    # FIND HWM LOCATIONS WITHIN PUBLIC HEALTH 6/5 REGIONS
    pip_mask = gdf.within(sff.iloc[0]['geometry'])
    pip_data = gdf.loc[pip_mask]
    file_output = 'ph_hwm.csv'
    pip_data.to_csv(path_hwm + file_output)


def getClosest(scale):
    hwm_file = '/Users/kyoung/Box Sync/github/data/hwm/ph_hwm.csv'
    temp_df_hwm = pd.read_csv(hwm_file)
    df_hwm = temp_df_hwm.dropna(subset=['height_above_gnd'])
    if scale == 0:
        num_hospitals = 20
    else:
        num_hospitals = 100  # can be any number
    hospital_dfs = getHospitals(1, scale, num_hospitals)
    df_sender = hospital_dfs[1]
    list_hospitals = df_sender['code'].tolist()

    list_output = []

    for i in list_hospitals:
        print(i)
        sender_lat = df_sender[df_sender['code'] == i]['latitude']
        sender_lon = df_sender[df_sender['code'] == i]['longitude']

        closest_dist = 100
        closest_location = 'empty'
        closest_location_hgt = 0
        list_closest_location = []
        for j in range(len(df_hwm)):
            reference_lat = df_hwm.iloc[j]['latitude']
            reference_lon = df_hwm.iloc[j]['longitude']

            distance_sq = abs(sender_lat - reference_lat) ** 2 + abs(sender_lon - reference_lon) ** 2
            distance = round(float(distance_sq ** 0.5), 3)

            if closest_dist > distance:
                closest_dist = distance
                closest_location = df_hwm.iloc[j]['hwm_id']
                closest_location_hgt = df_hwm.iloc[j]['height_above_gnd']
            elif closest_dist == distance:
                if closest_location_hgt < df_hwm.iloc[j]['height_above_gnd']:
                    closest_location = df_hwm.iloc[j]['hwm_id']
                    closest_location_hgt = df_hwm.iloc[j]['height_above_gnd']
                    closest_dist = distance
                else:
                    continue
            else:
                continue

        closest_dist = round(closest_dist, 4) * 111  # change distance in degree to km
        list_closest_location = [i, closest_location, closest_dist, closest_location_hgt]
        list_output.append(list_closest_location)

    cols = ['sender', 'hwm_id', 'distance', 'height_above_gnd']
    df = pd.DataFrame(list_output, columns=cols)
    df.to_csv('/Users/kyoung/Box Sync/github/data/hwm/sender_hwm_all.csv')
    df_cut = df[df['distance'] < 1.6]
    dff = df_cut.reset_index(drop=True)
    dff.to_csv('/Users/kyoung/Box Sync/github/data/hwm/sender_hwm.csv')

    return df

if __name__ == "__main__":
    scale = 1
    output = getClosest(scale)
