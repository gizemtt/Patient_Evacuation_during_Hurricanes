import geopandas as gpd
import pandas as pd
import shapely.speedups

def read_shapefile(shfile, list_landfall):
    sf = gpd.read_file(shfile)
    sf = sf.sort_values(by=['TAU'], ascending=True)
    advisory = {}
    advisory['adv_number'] = sf.ADVISNUM.unique()[0]
    list_time = []
    list_coordinate = []
    for i in range(len(sf)):
        list_time.append(sf.iloc[i].TAU)
        list_coordinate.append([sf.iloc[i].LAT, sf.iloc[i].LON])
    advisory['status'] = list_landfall
    advisory['coordinates'] = list_coordinate
    advisory['time'] = list_time
    return advisory


def getSurge(_location):
    shapely.speedups.enable()
    if _location == 'mac':
        shapefile_location = '/Users/kyoung/Box Sync/github/pelo/input/data/slosh/psurge/'
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

    file_extension = '.shp'
    product_type = 'gt'
    datum = 'agl'
    list_advisory = ['18']
    dict_advisory = {'15': '2017082406',
                     '16': '2017082412',
                     '18': '2017082418',
                     '20': '2017082506', }

    if product_type == 'e':
        this_folder = 'exceedance'
        list_set = [10, 20, 30, 40, 50]

        if datum == 'dat':
            suffix = 1
        else:
            suffix = 17

    else:
        this_folder = 'gt'

        if datum == 'dat':
            list_set = [2, 3, 4, 5, 6, 7, 8, 9, 10]
            suffix = 1
        else:
            list_set = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
            suffix = 17

    for i in list_advisory:
        this_advisory = i
        set_num = 0
        for j in list_set:
            this_set = j
            shapefile_folder = "%s_Harvey_Adv%s_%s%s_cum_%s_%s" % (dict_advisory[list_advisory[0]], this_advisory, product_type, this_set, datum, suffix)
            shapefile_name = "%s_Harvey_Adv%s_%s%s_cum_%s_%s%s" % (dict_advisory[list_advisory[0]], this_advisory, product_type, this_set, datum, suffix, file_extension)
            shapefile_path = "%s%s/%s/%s" % (shapefile_location, this_folder, shapefile_folder, shapefile_name)
            polys = gpd.read_file(shapefile_path)

            dict_affected = {}
            for k in polys['POINTID']:
                this_point = k
                shp = polys.loc[polys['POINTID'] == this_point]
                if len(shp) == 0:
                    continue
                psurge_output = float(shp[shp.columns[1]])
                shp.reset_index(drop=True, inplace=True)
                pip_mask = coordinates.within(shp.loc[0, 'geometry'])
                pip_data = coordinates.loc[pip_mask]
                affected_locations = list(pip_data.code)

                for l in affected_locations:
                    if product_type == 'e':
                        dict_affected[l] = round(psurge_output * 0.3048, 3)  # ft-to-meters conversion
                    else:
                        dict_affected[l] = round(psurge_output / 100, 4)
            print(shp.loc[0, 'geometry'])

            if j <= 9:
                height_col = '0' + str(j)
            else:
                height_col = j

            if product_type == 'e':
                col_name = "%s_%s%s" % ('surge', product_type, height_col)
            else:
                col_name = "%s_%s%s" % ('probability', product_type, height_col)

            if set_num == 0:
                df = pd.DataFrame(dict_affected.items(), columns=['code', col_name])
            else:
                df[col_name] = df['code'].map(dict_affected)
            print(dict_affected)
            set_num = set_num + 1

        df.sort_values(by=['code'])

    return df

# pd.set_option('display.max_columns', 30)
# pd.set_option('display.width', 1000)

# ----------------------------------------------------------------------
# ORIGINAL getSurge FUNCTION: TO FIND SURGE VALUE FROM PSURGE OUTPUT
# ----------------------------------------------------------------------

def getPSurge(_location):
    shapely.speedups.enable()
    if _location == 'mac':
        shapefile_location = '/Users/kyoung/Box Sync/github/pelo/input/data/slosh/psurge/'
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

    file_extension = '.shp'
    product_type = 'gt'
    datum = 'agl'
    list_advisory = ['18']
    dict_advisory = {'15': '2017082406',
                     '16': '2017082412',
                     '18': '2017082418',
                     '20': '2017082506', }

    if product_type == 'e':
        this_folder = 'exceedance'
        list_set = [10, 20, 30, 40, 50]

        if datum == 'dat':
            suffix = 1
        else:
            suffix = 17

    else:
        this_folder = 'gt'

        if datum == 'dat':
            list_set = [2, 3, 4, 5, 6, 7, 8, 9, 10]
            suffix = 1
        else:
            list_set = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
            suffix = 17

    for i in list_advisory:
        this_advisory = i
        set_num = 0
        for j in list_set:
            this_set = j
            shapefile_folder = "%s_Harvey_Adv%s_%s%s_cum_%s_%s" % (dict_advisory[list_advisory[0]], this_advisory, product_type, this_set, datum, suffix)
            shapefile_name = "%s_Harvey_Adv%s_%s%s_cum_%s_%s%s" % (dict_advisory[list_advisory[0]], this_advisory, product_type, this_set, datum, suffix, file_extension)
            shapefile_path = "%s%s/%s/%s" % (shapefile_location, this_folder, shapefile_folder, shapefile_name)
            polys = gpd.read_file(shapefile_path)

            dict_affected = {}
            for k in polys['POINTID']:
                this_point = k
                shp = polys.loc[polys['POINTID'] == this_point]
                if len(shp) == 0:
                    continue
                psurge_output = float(shp[shp.columns[1]])
                shp.reset_index(drop=True, inplace=True)
                # print(shp)
                # print(shp.loc[0, 'geometry'])
                pip_mask = coordinates.within(shp.loc[0, 'geometry'])
                pip_data = coordinates.loc[pip_mask]
                affected_locations = list(pip_data.code)

                for l in affected_locations:
                    if product_type == 'e':
                        dict_affected[l] = round(psurge_output * 0.3048, 3)  # ft-to-meters conversion
                    else:
                        dict_affected[l] = round(psurge_output / 100, 4)

            if j <= 9:
                height_col = '0' + str(j)
            else:
                height_col = j

            if product_type == 'e':
                col_name = "%s_%s%s" % ('surge', product_type, height_col)
            else:
                col_name = "%s_%s%s" % ('probability', product_type, height_col)

            if set_num == 0:
                df = pd.DataFrame(dict_affected.items(), columns=['code', col_name])
            else:
                df[col_name] = df['code'].map(dict_affected)
            print(dict_affected)
            set_num = set_num + 1

        df.sort_values(by=['code'])

    return df
