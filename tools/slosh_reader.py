import geopandas as gpd
import pandas as pd
import shapely.speedups

def slosh(location, filename):
    fileLocation = location + filename

    try:
        sloshInput = pd.read_csv(fileLocation)
        sloshdf = pd.DataFrame(sloshInput)
        colList = list(sloshdf)
        sloshdf = sloshdf[sloshdf[colList[4]] != 99.9]
        output = sloshdf.reset_index(drop=True)

        return output

    except OSError:
        print("File Not Found")

def identify_block():
    scenario_key = ['n', '3', '05i2', '5-1']
    shapely.speedups.enable()
    _location = 'mac'
    if _location == 'mac':
        shapefile_location = '/Users/kyoung/Box Sync/github/slosh_sh_files/'
        coordinatesfile_location = '/Users/kyoung/Box Sync/github/pelo/input/data/location/'
    else:
        shapefile_location = '/work/06447/kykim/pelo/input/data/slosh/psurge/'
        coordinatesfile_location = '/work/06447/kykim/pelo/input/data/location/'

    coordinatesfile_name = 'coordinate_lookup.csv'
    coordinatesfile_path = coordinatesfile_location + coordinatesfile_name
    df_coordinates = pd.read_csv(coordinatesfile_path)
    df_coordinates = df_coordinates[df_coordinates.type == 'Sender']
    coordinates = gpd.GeoDataFrame(df_coordinates, geometry=gpd.points_from_xy(df_coordinates.longitude, df_coordinates.latitude))
    coordinates = coordinates.reset_index(drop=True)
    direction_folder = scenario_key[0] + '/'
    sh_file = scenario_key[0] + scenario_key[1] + scenario_key[2] + '.shp'
    sf = gpd.read_file(shapefile_location + direction_folder + sh_file)

    dict_grid = {}
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
        if i % 100 == 0:
            print(i)

    return dict_grid

def slosh_reader(_scenario_key):
    shapely.speedups.enable()
    _location = 'mac'
    if _location == 'mac':
        shapefile_location = '/Users/kyoung/Box Sync/github/slosh_sh_files/'
        coordinatesfile_location = '/Users/kyoung/Box Sync/github/pelo/input/data/location/'
    else:
        shapefile_location = '/work/06447/kykim/pelo/input/data/slosh/psurge/'
        coordinatesfile_location = '/work/06447/kykim/pelo/input/data/location/'

    coordinatesfile_name = 'coordinate_lookup.csv'
    coordinatesfile_path = coordinatesfile_location + coordinatesfile_name
    df_coordinates = pd.read_csv(coordinatesfile_path)
    df_coordinates = df_coordinates[df_coordinates.type == 'Sender']
    coordinates = gpd.GeoDataFrame(df_coordinates, geometry=gpd.points_from_xy(df_coordinates.longitude, df_coordinates.latitude))
    coordinates = coordinates.reset_index(drop=True)

    direction_folder = _scenario_key[0] + '/'
    sh_file = _scenario_key[0] + _scenario_key[1] + _scenario_key[2] + '.shp'
    sf = gpd.read_file(shapefile_location + direction_folder + sh_file)

    return [coordinates, sf]
