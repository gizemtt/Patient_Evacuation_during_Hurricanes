from netCDF4 import Dataset
import numpy as np
from scipy.stats import norm
import math
import gmplot

def convert_decimal(input):
    decimal = math.floor(input)
    minute = math.floor(60 * abs(input - decimal))
    second = int(round(3600 * abs(decimal - input) - 60 * minute, 0))
    output = [decimal, minute, second]
    return output

def convert_degree(input):
    degree = input[0]
    decimal = input[1] / 60 + input[2] / 3600
    output = degree + decimal
    return output

def get_line(point1, point2):
    slope = (point1[0] - point2[0]) / (point1[1] - point2[1])
    intercept = point1[0] - (slope * point1[1])
    parameters = [slope, intercept]
    return parameters


def track_simulator(_landfall_track, _numScenario):
    file_name = 'nwm.t00z.medium_range.forcing.f004.conus.nc.nc'
    file_location = '/Users/kyoung/Box Sync/Researc_personal/Code/python/netcdf/'

    nc_file = file_location + file_name
    fh = Dataset(nc_file, mode='r')

    index_landfall = _landfall_track['status'].index(1)
    landfall_time = _landfall_track['time'][index_landfall]
    landfall_lat = _landfall_track['coordinates'][index_landfall][0]    # 27.5N
    landfall_lon = _landfall_track['coordinates'][index_landfall][1]    # 97.5W

    conversion_factor = 1  # nautical miles to miles
    cone_radius = {12: 26 * conversion_factor,
                   24: 41 * conversion_factor,
                   36: 54 * conversion_factor,
                   48: 68 * conversion_factor,
                   72: 102 * conversion_factor,
                   96: 151 * conversion_factor,
                   120: 190 * conversion_factor}

    # define two lines and fine the intersection
    # using two cities
    # city_1 = [26.90, -99.27]    # zapata, tx [lat, lon]
    # city_2 = [29.88, -93.94]   # port arthur, tx [lat, lon]
    city_1 = [27.91, -97.15]    # Aransas pass, tx [lat, lon]
    city_2 = [29.30, -94.80]    # Galveston, tx
    city_3 = [26.11, -97.17]    # south padre island, tx
    city_4 = [28.09, -97.83]    # mathis, tx
    city_5 = [25.90, -97.50]    # brownsville, tx
    city_6 = [28.02, -97.05]    # rockport, tx

    endpoint_1 = [26.90, -99.27]    # zapata, tx [lat, lon]
    endpoint_2 = [29.88, -93.94]   # port arthur, tx [lat, lon]
    pwlinear_1 = get_line(city_1, city_2)
    pwlinear_2 = get_line(city_3, city_4)
    pwlinear_3 = get_line(city_5, city_6)
    set_pwlinear = [pwlinear_1, pwlinear_2, pwlinear_3]

    # calculate hurricane track line
    endpoint_1 = [landfall_lat, landfall_lon]
    landfall_lat_bf = _landfall_track['coordinates'][index_landfall - 1][0]    # 27.5N
    landfall_lon_bf = _landfall_track['coordinates'][index_landfall - 1][1]    # 97.5W
    endpoint_2 = [landfall_lat_bf, landfall_lon_bf]
    trackline = get_line(endpoint_1, endpoint_2)

    # using hurricane tracks: landfall location and location 12 hours ahead of landfall
    endpoint_1 = [landfall_lat, landfall_lon]
    landfall_lat_bf = _landfall_track['coordinates'][index_landfall - 1][0]    # 27.5N
    landfall_lon_bf = _landfall_track['coordinates'][index_landfall - 1][1]    # 97.5W
    endpoint_2 = [landfall_lat_bf, landfall_lon_bf]
    slope_2 = (endpoint_1[0] - endpoint_2[0]) / (endpoint_1[1] - endpoint_2[1])
    intercept_2 = endpoint_1[0] - (slope_2 * endpoint_1[1])

    # location crossing two lines
    lon = (intercept_2 - intercept_1) / (slope_1 - slope_2)
    lat = slope_1 * lon + intercept_1
    center = [lat, lon]

    # create new landfall points
    z_score = norm.ppf(5 / 6)
    radius = cone_radius[landfall_time]  # unit = miles
    sigma = radius / z_score                 # unit = miles

    list_percentile = []
    list_center = []
    list_lon = []
    list_lat = []

    for i in range(_numScenario + 1):
        if (i == 0 or i == _numScenario):
            continue
        percentile = i / _numScenario
        d = abs(norm.ppf(percentile)) * sigma
        dist = d / 60  # in decimal
        rad = math.atan(slope_1)
        if percentile <= 0.5:
            multiplier = -1
        else:
            multiplier = 1
        new_lon = multiplier * dist * math.cos(rad) + lon
        new_lat = multiplier * dist * math.sin(rad) + lat
        new_center = [new_lat, new_lon]
        list_center.append(new_center)
        list_percentile.append(percentile)
        list_lon.append(new_lon)
        list_lat.append(new_lat)

    print(list_center)
    print(list_percentile)
    print(list_lon)
    print(list_lat)
    print(center)

    # hurricane_tracks = [[22.4, -93.0], [23.8, -93.9], [25.1, -95.2], [26.4, -96.3], [28.6, -97.3]]
    # _landfall_track['coordinates'] = [[24.9, -94.2], [26.0, -95.3], [27.3, -96.3], [28.3, -97.0], [29.0, -97.7]]
    list_track_lat = []
    list_track_lon = []
    for i in range(len(_landfall_track['coordinates'])):
        list_track_lat.append(_landfall_track['coordinates'][i][0])
        list_track_lon.append(_landfall_track['coordinates'][i][1])

    list_endpoint_lat = [city_1[0], city_2[0]]
    list_endpoint_lon = [city_1[1], city_2[1]]

    gmap = gmplot.GoogleMapPlotter(lat, lon, 8)
    gmap.apikey = 'AIzaSyB9QlHsyVOEcVUDJZFju2S0xeOSfcfAfEk'
    gmap.scatter(list_lat, list_lon, 'red', size=400, marker=True)
    gmap.scatter(list_track_lat, list_track_lon, 'blue', size=400, marker=True)
    gmap.scatter(list_endpoint_lat, list_endpoint_lon, 'green', size=400, marker=True)
    map_name = 'map' + str(_landfall_track['advisory']) + '_' + str(_numScenario) + '.html'
    output_location = '/Users/kyoung/Desktop/maps/'
    gmap.draw(output_location + map_name)


# Hurricane Harvey Advisory 13
# _landfall_track = {'time': [0, 12, 24, 36, 48],
#                    'coordinates': [[22.4, -93.0], [23.8, -93.9], [25.1, -95.2], [26.4, -96.3], [28.6, -97.3]],
#                    'status': [0, 0, 0, 0, 1],
#                    'advisory': 13}

# _landfall_track = {'time': [0, 12, 24, 36, 48],
#                    'coordinates': [[24.9, -94.2], [26.0, -95.3], [27.3, -96.3], [28.3, -97.0], [29.0, -97.7]],
#                    'status': [0, 0, 0, 1, 1],
#                    'advisory': 16}

_landfall_track = {'time': [0, 12, 24, 36, 48],
                   'coordinates': [[27.6, -96.8], [28.4, -97.3], [28.8, -97.5], [28.9, -97.6], [28.3, -96.8]],
                   'status': [0, 1, 1, 1, 1],
                   'advisory': 21}

_numScenario = 4
track_simulator(_landfall_track, _numScenario)
