import geopandas as gpd
import pandas as pd
import shapely.speedups
from get_hospitals import getHospitals

# ----------------------------------------------------------------------------
# USE A SAMPLE SCENARIO TO IDENTIFY SLOSH GRID BLOCKS FOR HOSPITAL LOCATIONS
# ----------------------------------------------------------------------------

def identify_block():
    scenario_key = ['n', '3', '05i2', '5-1']
    shapely.speedups.enable()
    _location = 'mac'
    if _location == 'mac':
        path_shp_file = '/Users/kyoung/Box Sync/github/data/slosh/shp/'
        path_coordinates = '/Users/kyoung/Box Sync/github/data/location/'
    else:
        path_shp_file = '/work/06447/kykim/pelo/data/slosh/psurge/'
        path_coordinates = '/work/06447/kykim/pelo/data/location/'

    # NEW LOCATION FILE
    list_hospitals = getHospitals(1, 1, 20)
    df_coordinates = list_hospitals[1]
    coordinates = gpd.GeoDataFrame(df_coordinates, geometry=gpd.points_from_xy(df_coordinates.longitude, df_coordinates.latitude))
    coordinates = coordinates.reset_index(drop=True)

    direction_folder = scenario_key[0] + '/'
    sh_file = scenario_key[0] + scenario_key[1] + scenario_key[2] + '.shp'
    sf = gpd.read_file(path_shp_file + direction_folder + sh_file)

    dict_grid = {}
    list_hospitals = []
    for i in range(len(sf)):
        shp = sf.iloc[i]
        # this_point = sf['Poly_id'][i]
        # shp = sf.loc[sf['Poly_id'] == this_point]
        if len(shp) == 0:
            continue
        pip_mask = coordinates.within(shp['geometry'])
        pip_data = coordinates.loc[pip_mask]
        grid_location = list(pip_data.code)
        if len(grid_location) != 0:
            for j in grid_location:
                dict_grid[j] = shp['Poly_id']
        if i % 1000 == 0:
            print(i)

    output_file = 'hospital_grid_index.csv'
    with open(path_coordinates + output_file, 'w') as w:
        for key, value in dict_grid.items():
            w.write("%s,%s\n" % (key, value))


def create_basin_shp():
    _location = 'mac'
    if _location == 'mac':
        path_shp_file = '/Users/kyoung/Box Sync/github/data/slosh/shp/'
        path_coordinates = '/Users/kyoung/Box Sync/github/data/location/'
    else:
        path_shp_file = '/work/06447/kykim/pelo/data/slosh/psurge/'
        path_coordinates = '/work/06447/kykim/pelo/data/location/'

    # GENERATE SCENARIO KEYS
    direction = ['wsw', 'w', 'wnw', 'nw', 'nnw', 'n', 'nne', 'ne']
    intensity = ['3']
    speed_tide = ['05i2']
    shp_list = []

    for d in direction:
        print("STATUS: direciton ", d)

        for i in intensity:
            for s in speed_tide:

                # FIND MAX EXTENT OF SURGE
                direction_folder = d + '/'
                scenario_name = ('%s%s%s' % (d, i, s))
                sh_file = scenario_name + '.shp'
                sf = gpd.read_file(path_shp_file + direction_folder + sh_file)

                sff = sf[sf[scenario_name] != 99.9]
                sff['surge'] = 0
                sfff = sff[['geometry', 'surge']]
                sf0 = sfff.dissolve(by='surge')
                shp_list.append(sf0)

    print("STATUS: Merge shapes")
    rdf = gpd.GeoDataFrame(pd.concat(shp_list, ignore_index=True))
    rdf['surge'] = 0
    rdf_final = rdf.dissolve(by='surge')
    print(rdf_final)

    path_basin = '/Users/kyoung/Box Sync/github/data/location/basin_shp/'
    basin_file = 'slosh_basin_all.shp'
    rdf_final.to_file(path_basin + basin_file)


def find_coastal_hospitals():
    shapely.speedups.enable()
    _location = 'mac'
    path_hospitals = '/Users/kyoung/Box Sync/github/frontier/input/'
    file_hospitals = 'stage_output.csv'

    # GET HOSPITAL LOCATION COORDINATES
    df_hospitals = pd.read_csv(path_hospitals + file_hospitals)
    coordinates = gpd.GeoDataFrame(df_hospitals, geometry=gpd.points_from_xy(df_hospitals['LONGITUDE'], df_hospitals['LATITUDE']))
    coordinates = coordinates.reset_index(drop=True)

    # READ BASIN SHAPE FILE
    path_basin = '/Users/kyoung/Box Sync/github/data/location/basin_shp/'
    basin_file = 'slosh_basin_all.shp'
    sf = gpd.read_file(path_basin + basin_file)

    # FIND HOSPITALS WITHIN THE BASIN
    pip_mask = coordinates.within(sf.iloc[0]['geometry'])
    pip_data = coordinates[pip_mask]
    coastal_hospitals = pip_data['code'].tolist()

    output_file = 'coastal_hospitals.csv'
    with open(path_hospitals + output_file, 'w') as w:
        w.write("%s\n" % 'sender')
        for i in coastal_hospitals:
            w.write("%s\n" % i)
