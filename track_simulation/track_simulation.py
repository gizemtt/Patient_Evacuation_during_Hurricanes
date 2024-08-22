from scipy.stats import norm
import math
import gmplot
import geopandas as gpd
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from gmplot import GoogleMapPlotter


class CustomGoogleMapPlotter(GoogleMapPlotter):
    def __init__(self, center_lat, center_lng, zoom, apikey='',
                 map_type='satellite'):
        if apikey == '':
            try:
                with open('apikey.txt', 'r') as apifile:
                    apikey = apifile.readline()
            except FileNotFoundError:
                pass
        super().__init__(center_lat, center_lng, zoom, apikey)

        self.map_type = map_type
        assert(self.map_type in ['roadmap', 'satellite', 'hybrid', 'terrain'])

    def write_map(self, f):
        f.write('\t\tvar centerlatlng = new google.maps.LatLng(%f, %f);\n' %
                (self.center[0], self.center[1]))
        f.write('\t\tvar myOptions = {\n')
        f.write('\t\t\tzoom: %d,\n' % (self.zoom))
        f.write('\t\t\tcenter: centerlatlng,\n')

        # Change this line to allow different map types
        f.write('\t\t\tmapTypeId: \'{}\'\n'.format(self.map_type))

        f.write('\t\t};\n')
        f.write(
            '\t\tvar map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);\n')
        f.write('\n')

    def color_scatter(self, lats, lngs, values=None, colormap='coolwarm',
                      size=None, marker=False, s=None, **kwargs):
        def rgb2hex(rgb):
            """ Convert RGBA or RGB to #RRGGBB """
            rgb = list(rgb[0:3])  # remove alpha if present
            rgb = [int(c * 255) for c in rgb]
            hexcolor = '#%02x%02x%02x' % tuple(rgb)
            return hexcolor

        if values is None:
            colors = [None for _ in lats]
        else:
            cmap = plt.get_cmap(colormap)
            norm = Normalize(vmin=min(values), vmax=max(values))
            scalar_map = ScalarMappable(norm=norm, cmap=cmap)
            colors = [rgb2hex(scalar_map.to_rgba(value)) for value in values]
        for lat, lon, c in zip(lats, lngs, colors):
            self.scatter(lats=[lat], lngs=[lon], c=c, size=size, marker=marker,
                         s=s, **kwargs)

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

def read_nwm_track(_input_file):
    this_file = _input_file
    track = pd.read_csv(this_file)
    forecast_hours = [12, 24, 36, 48, 72, 96, 120]
    df = pd.DataFrame()
    for i in forecast_hours:
        this_df = track.loc[track['forecast hour'] == i]
        df = df.append(this_df)
    list_time = []
    list_coordinate = []
    for i in range(len(df)):
        list_time.append(df.iloc[i]['forecast hour'])
        list_coordinate.append([df.iloc[i]['lat'], df.iloc[i]['lon']])

    advisory = {}
    advisory['adv_number'] = '2017082400z'
    advisory['status'] = list(df['Ocean/Land'].astype(int).values)
    advisory['coordinates'] = list_coordinate
    advisory['time'] = list_time
    return advisory

def get_texascoast():
    # DEFINE 3 CITIES TO FIND TEXAS COASTAL LINE
    city_1 = [29.88, -93.94]    # Port Arthur, tx
    city_2 = [27.80, -97.39]    # Corpus Christi, TX
    city_3 = [25.90, -97.50]    # brownsville, tx

    # GET BOARDER LINES [DICTIONARY]
    dict_border_lines = {}
    dict_border_intersect = {}
    list_border = []
    border1 = get_line(city_1, city_2)
    border2 = get_line(city_2, city_3)
    border_intersection = get_intersection(border1, border2)
    border1_lat = [city_1[0], border_intersection[0]]
    border1_lon = [city_1[1], border_intersection[1]]
    border2_lat = [border_intersection[0], city_3[0]]
    border2_lon = [border_intersection[1], city_3[1]]
    dict_border_lines[1] = [border1, border1_lat, border1_lon]
    dict_border_lines[2] = [border2, border2_lat, border2_lon]
    dict_border_intersect[1] = border_intersection
    list_border = [dict_border_lines, dict_border_intersect]
    print(border1)
    print(border2)
    print(border_intersection)

    return list_border

def convert_decimal(input):
    decimal = math.floor(input)
    minute = math.floor(60 * abs(input - decimal))
    second = int(round(3600 * abs(decimal - input) - 60 * minute, 0))
    output = [decimal, minute, second]
    return output

def convert_distance_degree(input):
    distance = 60 * input[0] + input[1]
    return distance

def get_intersection(line1, line2):
    lon = (line2[1] - line1[1]) / (line1[0] - line2[0])
    lat = lon * line1[0] + line1[1]
    output = [lat, lon]
    return output

def get_distance(_point1, _point2):
    distance = math.sqrt((abs(_point1[0] - _point2[0]))**2 + (abs(_point1[1] - _point2[1]))**2)
    # in decimal
    return distance

def closest(lst, k):
    lst = np.asarray(lst)
    idx = (np.abs(lst - k)).argmin()
    return lst[idx]

def get_key(my_dict, val):
    list_key = []
    for key, value in my_dict.items():
        if val == value:
            list_key.append(key)
    return list_key

def find_direction(point1, reference_point):
    point_line = get_line(point1, reference_point)
    point_slope = point_line[0]

    # Define available directions
    point_lat = point1[0]
    point_lon = point1[1]
    reference_lat = reference_point[0]
    reference_lon = reference_point[1]

    # define
    if (point_lat <= reference_lat) & (point_lon <= reference_lon):
        possible_directions = ['wsw', 'w']
    elif (point_lat >= reference_lat) & (point_lon <= reference_lon):
        possible_directions = ['w', 'wnw', 'nw', 'nnw', 'n']
    elif (point_lat >= reference_lat) & (point_lon >= reference_lon):
        possible_directions = ['n', 'nne', 'ne']

    # Slopes of SLOSH directions
    dict_slope = {'wsw': 0.5,
                  'w': 0,
                  'wnw': -0.5,
                  'nw': -1,
                  'nnw': -2,
                  'n': 5,
                  'nne': 2,
                  'ne': 1,
                  'ene': 0.5}

    dict_closest_direction = {}
    for direction in possible_directions:
        dict_closest_direction[direction] = abs(dict_slope[direction] - point_slope)

    minimum_value = min(dict_closest_direction.values())
    min_direction = [key for key in dict_closest_direction if dict_closest_direction[key] == minimum_value]

    if len(min_direction) == 1:
        min_direction = min_direction[0]

    return min_direction

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

def get_intersection_border(_border_list, _line, _reference, _direction, _indicator):
    dict_direction = {1: 'wsw',
                      2: 'w',
                      3: 'wnw',
                      4: 'nw',
                      5: 'nnw',
                      6: 'n',
                      7: 'nne',
                      8: 'ne',
                      9: 'ene'}
    reference_lon = _reference[1]
    reference_lat = _reference[0]
    dict_intersection = {}
    dict_intersection_distance = {}

    _border = _border_list[0]
    if _line[0] == 999:
        for i in _border:
            intersection_lat = _border[i][0][0] * _line[1] + _border[i][0][1]
            intersection_lon = _line[1]
            if intersection_lat <= reference_lat:
                continue
            else:
                this_intersection = [intersection_lat, intersection_lon]
                dict_intersection[i] = this_intersection
                dict_intersection_distance[i] = get_distance(this_intersection, _reference)

        min_key = min(dict_intersection_distance, key=dict_intersection_distance.get)
        output_intersection = [min_key, dict_intersection[min_key]]

    else:
        if get_key(dict_direction, _direction)[0] < 6:
            for i in _border:
                this_intersection = get_intersection(_border[i][0], _line)
                if this_intersection[1] >= reference_lon:
                    continue
                else:
                    dict_intersection[i] = this_intersection
                    dict_intersection_distance[i] = get_distance(this_intersection, _reference)
        elif get_key(dict_direction, _direction)[0] > 6:
            for i in _border:
                this_intersection = get_intersection(_border[i][0], _line)
                if this_intersection[1] <= reference_lon:
                    continue
                else:
                    dict_intersection[i] = this_intersection
                    dict_intersection_distance[i] = get_distance(this_intersection, _reference)
        else:
            if _indicator == 0:
                for i in _border:
                    this_intersection = get_intersection(_border[i][0], _line)
                    if this_intersection[1] >= reference_lon:
                        continue
                    else:
                        dict_intersection[i] = this_intersection
                        dict_intersection_distance[i] = get_distance(this_intersection, _reference)
            elif _indicator == 1:
                for i in _border:
                    this_intersection = get_intersection(_border[i][0], _line)
                    if this_intersection[1] <= reference_lon:
                        continue
                    else:
                        dict_intersection[i] = this_intersection
                        dict_intersection_distance[i] = get_distance(this_intersection, _reference)
    try:
        min_key = min(dict_intersection_distance, key=dict_intersection_distance.get)
        output_intersection = [min_key, dict_intersection[min_key]]
    except ValueError:
        output_intersection = 'empty'

    return output_intersection  # Format: [border#, [lat, lon]

def track_simulator(_landfall_track, _dict_input):
    print("---RUN TRACK SIMULATOR---")

    # get inputs from dcit_track_input
    _output_location = _dict_input['output_location']
    _input_adv = _dict_input['track_input_type']
    _reference = _dict_input['reference']
    _numQuantile = int(_dict_input['numQuantile'])
    _numSegment = _numQuantile + 1

    # STEP 1: GET THE EARLIEST LANDFALL TIME AND LOCATION
    index_landfall = _landfall_track['status'].index(1)
    landfall_time = _landfall_track['time'][index_landfall]
    landfall_lat = _landfall_track['coordinates'][index_landfall][0]    # 27.5N
    landfall_lon = _landfall_track['coordinates'][index_landfall][1]    # 97.5W

    # STEP 2: DEFINE THE CONE OF RADIUS
    # --- Yr 2019 2/3 probability circle
    conversion_factor = 1  # nautical miles to XXX
    # cone_radius_yr19 = {0: 0 * conversion_factor,
    #                     12: 26 * conversion_factor,
    #                     24: 41 * conversion_factor,
    #                     36: 54 * conversion_factor,
    #                     48: 68 * conversion_factor,
    #                     72: 102 * conversion_factor,
    #                     96: 151 * conversion_factor,
    #                     120: 190 * conversion_factor}

   # --- Yr 2017 2/3 probability circle
    cone_radius = {0: 0 * conversion_factor,
                   12: 29 * conversion_factor,
                   24: 45 * conversion_factor,
                   36: 63 * conversion_factor,
                   48: 78 * conversion_factor,
                   72: 107 * conversion_factor,
                   96: 159 * conversion_factor,
                   120: 211 * conversion_factor}

    # STEP 3:  DEFINE THE REFERENCE POINT FOR STORM DIRECTION
    # --- A line using hurricane tracks
    reference_direction = {'current': index_landfall, 'bf_landfall': 1}
    hurricane_center = [landfall_lat, landfall_lon]
    landfall_lat_bf = _landfall_track['coordinates'][index_landfall - reference_direction[_reference]][0]    # 27.5N
    landfall_lon_bf = _landfall_track['coordinates'][index_landfall - reference_direction[_reference]][1]    # 97.5W
    landfall_time_bf = _landfall_track['time'][index_landfall - reference_direction[_reference]]
    endpoint = [landfall_lat_bf, landfall_lon_bf]
    track_line = get_line(hurricane_center, endpoint)

    # STEP 4:  FIND COASTLINE AND INTERSECTION AND CONE OF UNCERTAINTY AT THE INTERSECTION
    # -- Get TX coastline
    tx_coast = get_texascoast()

    # -- Get intersection between coastline and trackline
    dict_crossing_intersection = {}
    dict_crossing_distance = {}
    dict_coastlines = tx_coast[0]

    for i in dict_coastlines:
        border_line = dict_coastlines[i][0]
        crossing = get_intersection(track_line, border_line)
        border_distance = get_distance(crossing, endpoint)
        dict_crossing_intersection[i] = crossing
        dict_crossing_distance[i] = border_distance

    median_border_number = min(dict_crossing_distance, key=dict_crossing_distance.get)
    median_border_intersection = dict_crossing_intersection[median_border_number]
    median_crossing = [median_border_number, median_border_intersection]
    median_coastline = dict_coastlines[median_border_number][0]

    # -- Find new cone of uncertainty at coastline_intersect_point
    z_score = norm.ppf(5 / 6)
    radius = cone_radius[landfall_time]  # unit = nautical miles
    radius_bf = cone_radius[landfall_time_bf]
    dist_ref_median_intersect = get_distance(endpoint, median_border_intersection)
    dist_ref_hurricane_center = get_distance(endpoint, hurricane_center)
    cou_border = dist_ref_median_intersect / dist_ref_hurricane_center * (radius - radius_bf) + radius_bf
    sigma = cou_border / z_score
    median_landfall_time = dist_ref_median_intersect / dist_ref_hurricane_center * 24
    print("LANDFALL TIME: ", str(median_landfall_time + 48))
    print("COU: ", cou_border)
    print("MBI :", median_border_intersection)

    # STEP 5: FIND THE INTERSECTIONS
    list_percentile = []
    dict_landfall = {}
    list_lon = []
    list_lat = []
    list_direction = []

    for i in range(_numSegment + 1):
        if (i == 0 or i == _numSegment):
            continue
        percentile = i / _numSegment
        d = abs(norm.ppf(percentile)) * sigma
        dist = d / 60  # in decimal
        rad = math.atan(median_coastline[0])
        if percentile <= 0.5:
            multiplier = -1
        else:
            multiplier = 1
        new_lon = multiplier * dist * math.cos(rad) + median_border_intersection[1]
        new_lat = multiplier * dist * math.sin(rad) + median_border_intersection[0]
        temp_new_center = [new_lat, new_lon]

        # define a line connecting reference point and new center created
        percentile_line = get_line(temp_new_center, endpoint)

        # iterate among coastlines and find the closest
        dict_percentile_point_distance = {}
        dict_percentile_point_intersection = {}
        for j in dict_coastlines:
            percentile_point = get_intersection(dict_coastlines[j][0], percentile_line)
            percentile_point_distance = get_distance(endpoint, percentile_point)
            dict_percentile_point_distance[j] = percentile_point_distance
            dict_percentile_point_intersection[j] = percentile_point

        list_key = []
        for key, value in dict_percentile_point_intersection.items():
            if (percentile < 0.5) & (value[1] >= median_border_intersection[1]):
                list_key.append(key)
            elif (percentile > 0.5) & (value[1] <= median_border_intersection[1]):
                list_key.append(key)

        for l in list_key:
            del(dict_percentile_point_distance[l])

        closest_coastline_number = min(dict_percentile_point_distance, key=dict_percentile_point_distance.get)
        if median_border_number == closest_coastline_number:
            new_center = temp_new_center
        else:
            dist_remaining = dist - get_distance(median_border_intersection, tx_coast[1][1])
            closet_coastline = dict_coastlines[closest_coastline_number][0]
            this_rad = math.atan(closet_coastline[0])
            new_lon = multiplier * dist_remaining * math.cos(this_rad) + tx_coast[1][1][1]
            new_lat = multiplier * dist_remaining * math.sin(this_rad) + tx_coast[1][1][0]
            new_center = [new_lat, new_lon]

        dict_landfall[i] = new_center
        list_percentile.append(percentile)
        list_lon.append(new_lon)
        list_lat.append(new_lat)

        # Find closest SLOSH direction
        new_center_direction = find_direction(new_center, endpoint)   # order of find_direction inputs is important (new_center then median)
        list_direction.append(new_center_direction)

    # create a dataframe with landfall locations
    dict_locations = {'latitude': list_lat, 'longitude': list_lon, 'direction': list_direction}
    df_landfall_locations = pd.DataFrame(dict_locations)

    # sort dataframe from left to right orientation
    df_landfall_locations = df_landfall_locations.sort_values(by='longitude')
    df_landfall_locations = df_landfall_locations.reset_index(drop=True)

    location_index = []
    for i in range(_numQuantile):
        file_num = str(i + 1)
        this_index = '%s-%s' % (str(_numQuantile), file_num)
        location_index.append(this_index)

    df_landfall_locations['location'] = location_index
    cols = ['location', 'latitude', 'longitude', 'direction']
    df_landfall_locations = df_landfall_locations[cols]

    # add median crossing point
    dict_median_crossing = {'location': 'reference', 'latitude': median_crossing[1][0], 'longitude': median_crossing[1][1], 'direction': 'nan'}
    df_median_crossing = pd.DataFrame(dict_median_crossing, index=[0])
    df_landfall_locations = df_landfall_locations.append(df_median_crossing, ignore_index=True)
    landfall_locations_file = 'landfall_locations_5.csv'
    df_landfall_locations.to_csv(_output_location + landfall_locations_file, index=False)

    # DRAW GRAPH
    # gmap = gmplot.GoogleMapPlotter(landfall_lat, landfall_lon, 8)
    gmap = CustomGoogleMapPlotter(landfall_lat, landfall_lon, zoom=8, map_type='satellite')
    gmap.apikey = 'AIzaSyB9QlHsyVOEcVUDJZFju2S0xeOSfcfAfEk'
    nm_to_m = 1852

    list_track_lat = []
    list_track_lon = []
    for i in range(len(_landfall_track['coordinates'])):
        list_track_lat.append(_landfall_track['coordinates'][i][0])
        list_track_lon.append(_landfall_track['coordinates'][i][1])
        this_landfall_time = _landfall_track['time'][i]
        gmap.circle(_landfall_track['coordinates'][i][0], _landfall_track['coordinates'][i][1], radius=cone_radius[this_landfall_time] * nm_to_m, color='yellow', alpha=0.1)

    # gmap.scatter(list_lat, list_lon, 'red', size=400, marker=True)
    gmap.scatter(list_track_lat, list_track_lon, 'blue', size=400, marker=True)
    # gmap.scatter(list_reference_lat, list_reference_lon, 'green', size=400, marker=True)
    # gmap.marker(median_border_intersection[0], median_border_intersection[1], 'orange')
    gmap.plot(list_track_lat, list_track_lon, 'blue', edge_width=5)

    # DRAW PIECEWISE LINEAR COASTLINES
    nm_to_m = 1852
    border_width = 5
    borders = tx_coast[0]
    gmap.plot(borders[1][1], borders[1][2], color='green', edge_width=border_width)
    gmap.plot(borders[2][1], borders[2][2], color='green', edge_width=border_width)

    # DRAW CONE OF UNCERTAINTY
    # gmap.circle(hurricane_center[0], hurricane_center[1], radius=cone_radius[landfall_time] * nm_to_m, color='yellow', alpha=0.1)
    # gmap.circle(median_border_intersection[0], median_border_intersection[1], radius=cou_border * nm_to_m, color='orange', alpha=0.5)
    map_name = 'map_SS_%s_%s_%s_%s.html' % (str(_landfall_track['adv_number']), _input_adv, _reference, str(_numQuantile))
    gmap.draw(_output_location + map_name)

    print('Landfall Locations')
    print(dict_landfall)
    print('---DONE TRACK SIMULATOR---')
    print("")

    return dict_landfall


def track_simulator_stratified(_landfall_track, _dict_input):
    print("---RUN NWM TRACK SIMULATOR---")

    # get inputs of the function
    _output_location = _dict_input['output_location']
    _reference = _dict_input['reference']
    _input_adv = _dict_input['track_input_type']
    numSegment = int(dict_input['numSegment'])
    numSample = int(dict_input['numSample'])

    # STEP 1: GET THE EARLIEST LANDFALL TIME AND LOCATION
    index_landfall = _landfall_track['status'].index(1)
    landfall_time = _landfall_track['time'][index_landfall]
    landfall_lat = _landfall_track['coordinates'][index_landfall][0]    # 27.5N
    landfall_lon = _landfall_track['coordinates'][index_landfall][1]    # 97.5W

    # STEP 2: DEFINE THE CONE OF RADIUS
    # --- Yr 2019 2/3 probability circle
    conversion_factor = 1  # nautical miles to XXX

    # --- Yr 2017 2/3 probability circle
    cone_radius = {0: 0 * conversion_factor,
                   12: 29 * conversion_factor,
                   24: 45 * conversion_factor,
                   36: 63 * conversion_factor,
                   48: 78 * conversion_factor,
                   72: 107 * conversion_factor,
                   96: 159 * conversion_factor,
                   120: 211 * conversion_factor}

    # STEP 3:  DEFINE THE REFERENCE POINT FOR STORM DIRECTION
    # --- A line using hurricane tracks
    reference_direction = {'current': index_landfall, 'bf_landfall': 1}
    hurricane_center = [landfall_lat, landfall_lon]
    landfall_lat_bf = _landfall_track['coordinates'][index_landfall - reference_direction[_reference]][0]    # 27.5N
    landfall_lon_bf = _landfall_track['coordinates'][index_landfall - reference_direction[_reference]][1]    # 97.5W
    landfall_time_bf = _landfall_track['time'][index_landfall - reference_direction[_reference]]
    endpoint = [landfall_lat_bf, landfall_lon_bf]
    track_line = get_line(hurricane_center, endpoint)

    # STEP 4:  FIND COASTLINE AND INTERSECTION AND CONE OF UNCERTAINTY AT THE INTERSECTION
    # -- Get TX coastline
    tx_coast = get_texascoast()

    # -- Get intersection between coastline and trackline
    dict_crossing_intersection = {}
    dict_crossing_distance = {}
    dict_coastlines = tx_coast[0]

    for i in dict_coastlines:
        border_line = dict_coastlines[i][0]
        crossing = get_intersection(track_line, border_line)
        border_distance = get_distance(crossing, endpoint)
        dict_crossing_intersection[i] = crossing
        dict_crossing_distance[i] = border_distance

    median_border_number = min(dict_crossing_distance, key=dict_crossing_distance.get)
    median_border_intersection = dict_crossing_intersection[median_border_number]
    median_crossing = [median_border_number, median_border_intersection]
    median_coastline = dict_coastlines[median_border_number][0]
    print("median from nwm: ", median_crossing)
    # -- Find new cone of uncertainty at coastline_intersect_point
    z_score = norm.ppf(5 / 6)
    radius = cone_radius[landfall_time]  # unit = nautical miles
    radius_bf = cone_radius[landfall_time_bf]

    print("Landfall time: ", landfall_time)
    print("Landfall time: ", landfall_time_bf)
    dist_ref_median_intersect = get_distance(endpoint, median_border_intersection)
    dist_ref_hurricane_center = get_distance(endpoint, hurricane_center)
    cou_border = dist_ref_median_intersect / dist_ref_hurricane_center * (radius - radius_bf) + radius_bf
    sigma = cou_border / z_score

    median_landfall_time = dist_ref_median_intersect / dist_ref_hurricane_center * 24
    print("LANDFALL TIME: ", str(median_landfall_time + 48))
    print("COU: ", cou_border)
    print("MBI :", median_border_intersection)

    # STEP 5: DIVIDE DISTRIBUTION INTO EQUAL PROBABLE SEGMENTS
    segment_probability = 1 / numSegment
    probability = 0
    numScenarios = numSegment * numSample
    np.random.seed(1234)

    # Get 5 * 5 samples
    samples = []
    for i in range(numSegment):
        this_samples = np.random.uniform(probability, probability + segment_probability, numSample)
        samples = np.concatenate((samples, this_samples), axis=None)
        probability = probability + segment_probability

    print("SAMPLES: ", samples)
    samples[1] = 0.1
    print("SAMPLES: ", samples)

    # Get distances from the median point
    z_scores = []
    distances = []
    for i in samples:
        z = norm.ppf(i)
        d = (z * sigma) / 60  # convert distance to decimal
        z_scores.append(z)
        distances.append(d)

    median_coastline_slope = median_coastline[0]
    rad = math.atan(median_coastline_slope)

    # Calculate sampled location cooridnates : median border intersection form = [29.88, -93.94] lat, lon
    dict_landfall = {}
    list_lon = []
    list_lat = []
    list_direction = []
    for i in range(len(distances)):
        dist = distances[i]
        if dist < 0:
            multiplier = -1
        else:
            multiplier = 1

        new_lon = multiplier * abs(dist) * math.cos(rad) + median_border_intersection[1]
        new_lat = multiplier * abs(dist) * math.sin(rad) + median_border_intersection[0]
        temp_sampled_location = [new_lat, new_lon]

        # define a line connecting reference point and new center created
        line_to_sampled = get_line(temp_sampled_location, endpoint)

        # iterate among coastlines and find the closest
        dict_distance = {}
        dict_intersection = {}
        for j in dict_coastlines:
            sample_point = get_intersection(dict_coastlines[j][0], line_to_sampled)
            sample_point_distance = get_distance(endpoint, sample_point)
            dict_distance[j] = sample_point_distance
            dict_intersection[j] = sample_point

        list_key = []
        for key, value in dict_intersection.items():
            if (dist < 0) & (value[1] >= median_border_intersection[1]):
                list_key.append(key)
            elif (dist > 0) & (value[1] <= median_border_intersection[1]):
                list_key.append(key)

        for this_key in list_key:
            del(dict_distance[this_key])

        closest_coastline_number = min(dict_distance, key=dict_distance.get)
        if median_border_number == closest_coastline_number:
            new_center = temp_sampled_location
        else:
            dist_remaining = dist - get_distance(median_border_intersection, tx_coast[1][1])
            closet_coastline = dict_coastlines[closest_coastline_number][0]
            this_rad = math.atan(closet_coastline[0])
            new_lon = multiplier * dist_remaining * math.cos(this_rad) + tx_coast[1][1][1]
            new_lat = multiplier * dist_remaining * math.sin(this_rad) + tx_coast[1][1][0]
            new_center = [new_lat, new_lon]

        dict_landfall[i] = new_center
        list_lon.append(new_lon)
        list_lat.append(new_lat)

        # Find closest SLOSH direction
        new_center_direction = find_direction(new_center, endpoint)   # order of find_direction inputs is important (new_center then median)
        list_direction.append(new_center_direction)

    print(list_lon)
    print(list_lat)
    print(list_direction)

    # create a dataframe with landfall locations
    dict_locations = {'latitude': list_lat, 'longitude': list_lon, 'direction': list_direction}
    df_landfall_locations = pd.DataFrame(dict_locations)

    # sort dataframe from left to right orientation
    df_landfall_locations = df_landfall_locations.sort_values(by='longitude')
    df_landfall_locations = df_landfall_locations.reset_index(drop=True)

    location_index = []
    for i in range(numScenarios):
        file_num = str(i + 1)
        # if file_num < 10:
        #     file_num = '0' + str(file_num)
        # else:
        #     file_num = str(file_num)
        this_index = '%s-%s' % (str(numScenarios), file_num)
        location_index.append(this_index)

    df_landfall_locations['location'] = location_index
    cols = ['location', 'latitude', 'longitude', 'direction']
    df_landfall_locations = df_landfall_locations[cols]

    # add median crossing point
    dict_median_crossing = {'location': 'reference', 'latitude': median_crossing[1][0], 'longitude': median_crossing[1][1], 'direction': 'nan'}
    df_median_crossing = pd.DataFrame(dict_median_crossing, index=[0])
    df_landfall_locations = df_landfall_locations.append(df_median_crossing, ignore_index=True)
    landfall_locations_file = 'landfall_locations.csv'
    df_landfall_locations.to_csv(_output_location + landfall_locations_file, index=False)

    # STEP 6: DRAW GRAPH
    # gmap = gmplot.GoogleMapPlotter(landfall_lat, landfall_lon, 8)
    gmap = CustomGoogleMapPlotter(landfall_lat, landfall_lon, zoom=8, map_type='satellite')
    gmap.apikey = 'AIzaSyB9QlHsyVOEcVUDJZFju2S0xeOSfcfAfEk'
    nm_to_m = 1852

    color_map = {'cou': 'yellow',
                 'median': 'orange',
                 'track': 'blue',
                 'border': 'black',
                 'landfall': 'red'}

    # draw cone of uncertainty
    list_track_lat = []
    list_track_lon = []
    for i in range(len(_landfall_track['coordinates'])):
        list_track_lat.append(_landfall_track['coordinates'][i][0])
        list_track_lon.append(_landfall_track['coordinates'][i][1])
        this_landfall_time = _landfall_track['time'][i]
        # gmap.circle(_landfall_track['coordinates'][i][0], _landfall_track['coordinates'][i][1], radius=cone_radius[this_landfall_time] * nm_to_m, color=color_map['cou'], alpha=0.1)

    # # get previosly generated landfall locations
    # path = '/Users/kyoung/Box Sync/github/pelo/track_simulation/output/'
    # file_name = 'landfall_locations.csv'

    gmap.scatter(list_lat, list_lon, 'red', size=400, marker=True)
    gmap.scatter(list_track_lat, list_track_lon, color_map['track'], size=400, marker=True)
    gmap.plot(list_track_lat, list_track_lon, color_map['track'], edge_width=5)
    gmap.marker(median_border_intersection[0], median_border_intersection[1], color_map['median'])

    # DRAW PIECEWISE LINEAR COASTLINES
    nm_to_m = 1852
    border_width = 5
    borders = tx_coast[0]
    gmap.plot(borders[1][1], borders[1][2], color=color_map['border'], edge_width=border_width)
    # gmap.plot(borders[2][1], borders[2][2], color=color_map['border'], edge_width=border_width)
    gmap.plot([27.8000, 24.5062], [-97.39, -97.5806], color=color_map['border'], edge_width=border_width)   # modified to extend piecewise line to the southern most simulated point

    # DRAW CONE OF UNCERTAINTY
    # gmap.circle(hurricane_center[0], hurricane_center[1], radius=cone_radius[landfall_time] * nm_to_m, color=color_map['cou'], alpha=0.1)
    # gmap.circle(median_border_intersection[0], median_border_intersection[1], radius=cou_border * nm_to_m, edge_color='orange', alpha = 0,face_alpha = 0, color=color_map['median'])
    map_name = 'map_QSS_%s_%s_%s_%s.html' % (str(_landfall_track['adv_number']), _input_adv, _reference, str(numScenarios))

    gmap.draw(_output_location + map_name)

    print('Landfall Locations')
    print(dict_landfall)
    print('---DONE TRACK SIMULATOR---')
    print("")


def surge_simulator(_landfall_track, _dict_input):
    print('---RUN SURGE SIMULATOR---')
    _border_list = get_texascoast()
    _border = _border_list[0]
    for border in _border_list[1]:
        _border_intersect = _border_list[1][border]

    print("SURGE SIM - border_intersect: ", _border_intersect)

    # get inputs from dict_input
    _output_location = _dict_input['output_location']
    _reference = _dict_input['reference']

    # Yr 2017 2/3 probability circle
    conversion_factor = 1
    cone_radius = {0: 0 * conversion_factor,
                   12: 29 * conversion_factor,
                   24: 45 * conversion_factor,
                   36: 63 * conversion_factor,
                   48: 78 * conversion_factor,
                   72: 107 * conversion_factor,
                   96: 159 * conversion_factor,
                   120: 211 * conversion_factor}

    dict_direction = {1: 'wsw',
                      2: 'w',
                      3: 'wnw',
                      4: 'nw',
                      5: 'nnw',
                      6: 'n',
                      7: 'nne',
                      8: 'ne',
                      9: 'ene'}

    dict_slope = {'wsw': 0.5,
                  'w': 0,
                  'wnw': -0.5,
                  'nw': -1,
                  'nnw': -2,
                  'n': 5,
                  'nne': 2,
                  'ne': 1,
                  'ene': 0.5}

    dict_guideline = {'wsw': [3 / 4, 1 / 4],
                      'w': [1 / 4, -1 / 4],
                      'wnw': [-1 / 4, -3 / 4],
                      'nw': [-3 / 4, -3 / 2],
                      'nnw': [-3 / 2, -4],
                      'n': [-4, 4],
                      'nne': [4, 3 / 2],
                      'ne': [3 / 2, 3 / 4],
                      'ene': [3 / 4, 1 / 4]}

    index_landfall = _landfall_track['status'].index(1)
    landfall_time = _landfall_track['time'][index_landfall]
    landfall_lat = _landfall_track['coordinates'][index_landfall][0]    # 27.5N
    landfall_lon = _landfall_track['coordinates'][index_landfall][1]    # 97.5W

    # DEFINE THE REFERENCE POINT FOR STORM DIRECTION
    reference_direction = {'current': index_landfall, 'bf_landfall': 1}

    # a line using hurricane tracks: landfall location and location 12 hours ahead of landfall
    hurricane_center = [landfall_lat, landfall_lon]
    landfall_lat_bf = _landfall_track['coordinates'][index_landfall - reference_direction[_reference]][0]    # 27.5N
    landfall_lon_bf = _landfall_track['coordinates'][index_landfall - reference_direction[_reference]][1]    # 97.5W
    landfall_time_bf = _landfall_track['time'][index_landfall - reference_direction[_reference]]
    endpoint = [landfall_lat_bf, landfall_lon_bf]
    track_line = get_line(hurricane_center, endpoint)
    z_score = norm.ppf(5 / 6)
    radius = cone_radius[landfall_time]  # unit = nautical miles
    radius_bf = cone_radius[landfall_time_bf]
    sigma = radius / z_score             # unit = nautical miles

    list_slope = [0, 0.5, 1, 2, 8, -0.5, -1, -2]
    temp_slope_storm = track_line[0]
    slope_storm = closest(list_slope, temp_slope_storm)
    storm_direction = get_key(dict_slope, slope_storm)
    print("STORM DIRECTION: ", storm_direction)
    if len(storm_direction) != 1:
        print('WSW or ENE')
    else:
        storm_direction_number = get_key(dict_direction, storm_direction[0])

    # FIND THE MEDIAN HURRICANE INTERSECTION
    dict_crossing_intersection = {}
    dict_crossing_distance = {}

    for i in _border:
        border_line = _border[i][0]
        crossing = get_intersection(track_line, border_line)
        border_distance = get_distance(crossing, endpoint)
        dict_crossing_intersection[i] = crossing
        dict_crossing_distance[i] = border_distance

    median_border_number = min(dict_crossing_distance, key=dict_crossing_distance.get)
    median_border_intersection = dict_crossing_intersection[median_border_number]
    median_crossing = [median_border_number, median_border_intersection]
    print("median from surge: ", median_crossing)

    # DEFINE THE CONE OF UNCERTAINTY AT BORDER AND FIND SIGMA
    dist_ref_median_intersect = get_distance(endpoint, median_border_intersection)
    dist_ref_hurricane_center = get_distance(endpoint, hurricane_center)
    cou_border = dist_ref_median_intersect / dist_ref_hurricane_center * (radius - radius_bf) + radius_bf
    sigma_crossing = cou_border / z_score

    # PICK CANDIDATE STORM DIRECTIONS
    min_storm_direction_number = 1
    max_storm_direction_number = 9

    # FIND LANDFALL LOCATIONS ALONG THE BORDER LINE
    dict_landfall = {}
    dict_landfall_prob = {}
    check_prob_sum = 0
    for i in range(max_storm_direction_number - min_storm_direction_number + 1):
        indicator = 2
        this_storm_number = i + min_storm_direction_number
        try:
            this_storm_direction = dict_direction[this_storm_number]
        except KeyError:
            continue

        if this_storm_direction != 'n':
            this_storm_slope = dict_slope[this_storm_direction]
            this_storm_intercept = landfall_lat_bf - this_storm_slope * landfall_lon_bf
            this_storm_line = [this_storm_slope, this_storm_intercept]
        else:
            this_storm_line = [999, landfall_lon_bf]

        _intersection = get_intersection_border(_border_list, this_storm_line, endpoint, this_storm_direction, indicator)
        if _intersection == 'empty':
            continue
        else:
            dict_landfall[this_storm_direction] = _intersection

        # FIND THE PROBABILITY
        if i == 0:
            indicator = 1
            mid_line_slope = dict_guideline[this_storm_direction][indicator]
            mid_line_intercept = endpoint[0] - mid_line_slope * endpoint[1]
            mid_line = [mid_line_slope, mid_line_intercept]
            mid_line_intersection = get_intersection_border(_border_list, mid_line, endpoint, this_storm_direction, indicator)  # Format: [border#, [lat, lon]

            # FIND DISTANCE FROM THE MEDIAN CROSSING
            if median_crossing[0] == mid_line_intersection[0]:
                _distance_from_median = get_distance(mid_line_intersection[1], median_crossing[1])
            elif median_crossing[0] != mid_line_intersection[0]:
                temp_distance = get_distance(mid_line_intersection[1], _border_intersect)
                _distance_from_median = temp_distance + get_distance(_border_intersect, median_crossing[1])

            distance_from_median_degree = convert_decimal(_distance_from_median)
            distance_from_median = convert_distance_degree(distance_from_median_degree)
            if median_crossing[1][1] - mid_line_intersection[1][1] > 0:
                distance_from_median = distance_from_median * -1
            mid_line_z_score = distance_from_median / sigma_crossing
            mid_line_prob = norm.cdf(mid_line_z_score)
            this_storm_prob = mid_line_prob
            dict_landfall_prob[this_storm_direction] = this_storm_prob
            check_prob_sum = check_prob_sum + this_storm_prob

        elif i == max_storm_direction_number - min_storm_direction_number:
            indicator = 0
            mid_line_slope = dict_guideline[this_storm_direction][indicator]
            mid_line_intercept = endpoint[0] - mid_line_slope * endpoint[1]
            mid_line = [mid_line_slope, mid_line_intercept]
            mid_line_intersection = get_intersection_border(_border_list, mid_line, endpoint, this_storm_direction, indicator)  # Format: [border#, [lat, lon]

            # FIND DISTANCE FROM THE MEDIAN CROSSING
            if median_crossing[0] == mid_line_intersection[0]:
                _distance_from_median = get_distance(mid_line_intersection[1], median_crossing[1])
            elif median_crossing[0] != mid_line_intersection[0]:
                temp_distance = get_distance(mid_line_intersection[1], _border_intersect)
                _distance_from_median = temp_distance + get_distance(_border_intersect, median_crossing[1])

            distance_from_median_degree = convert_decimal(_distance_from_median)
            distance_from_median = convert_distance_degree(distance_from_median_degree)
            if median_crossing[1][1] - mid_line_intersection[1][1] > 0:
                distance_from_median = distance_from_median * -1
            mid_line_z_score = distance_from_median / sigma_crossing
            mid_line_prob = 1 - norm.cdf(mid_line_z_score)
            this_storm_prob = mid_line_prob
            dict_landfall_prob[this_storm_direction] = this_storm_prob
            check_prob_sum = check_prob_sum + this_storm_prob
        else:
            mid_line_probs = []
            num_guide_lines = 2
            for i in range(num_guide_lines):
                indicator = i
                j = dict_guideline[this_storm_direction][i]
                mid_line_slope = j
                mid_line_intercept = endpoint[0] - mid_line_slope * endpoint[1]
                mid_line = [mid_line_slope, mid_line_intercept]
                mid_line_intersection = get_intersection_border(_border_list, mid_line, endpoint, this_storm_direction, indicator)  # Format: [border#, [lat, lon]

                # FIND DISTANCE FROM THE MEDIAN CROSSING
                if median_crossing[0] == mid_line_intersection[0]:
                    _distance_from_median = get_distance(mid_line_intersection[1], median_crossing[1])
                elif median_crossing[0] != mid_line_intersection[0]:
                    temp_distance = get_distance(mid_line_intersection[1], _border_intersect)
                    _distance_from_median = temp_distance + get_distance(_border_intersect, median_crossing[1])
                distance_from_median_degree = convert_decimal(_distance_from_median)
                distance_from_median = convert_distance_degree(distance_from_median_degree)
                if median_crossing[1][1] - mid_line_intersection[1][1] > 0:
                    distance_from_median = distance_from_median * -1
                mid_line_z_score = distance_from_median / sigma_crossing
                mid_line_prob = norm.cdf(mid_line_z_score)
                mid_line_probs.append(mid_line_prob)

            this_storm_prob = max(mid_line_probs) - min(mid_line_probs)
            dict_landfall_prob[this_storm_direction] = this_storm_prob
            check_prob_sum = check_prob_sum + this_storm_prob

    print("")
    print("Checksum: ", check_prob_sum)
    print("")
    print("Landfall Locations:")
    print(dict_landfall)
    print("")
    print("Scenario Prob:")
    print(dict_landfall_prob)

    # DRAW MAP
    # gmap = gmplot.GoogleMapPlotter(landfall_lat, landfall_lon, 8)
    gmap = CustomGoogleMapPlotter(landfall_lat, landfall_lon, zoom=8, map_type='satellite')
    gmap.apikey = 'AIzaSyB9QlHsyVOEcVUDJZFju2S0xeOSfcfAfEk'
    nm_to_m = 1852

    # draw hurricane track
    list_track_lat = []
    list_track_lon = []
    for i in range(len(_landfall_track['coordinates'])):
        this_lat = _landfall_track['coordinates'][i][0]
        this_lon = _landfall_track['coordinates'][i][1]
        list_track_lat.append(this_lat)
        list_track_lon.append(this_lon)
        this_landfall_time = _landfall_track['time'][i]
        # gmap.circle(_landfall_track['coordinates'][i][0], _landfall_track['coordinates'][i][1], radius=cone_radius[this_landfall_time] * nm_to_m, color='yellow', alpha=0.1)
        gmap.marker(this_lat, this_lon, 'blue', title='this title')  # add labels

    gmap.plot(list_track_lat, list_track_lon, 'blue', edge_width=5)

    # draw landfall points
    list_lon = []
    list_lat = []
    for key, value in dict_landfall.items():
        list_lon.append(value[1][1])
        list_lat.append(value[1][0])
    gmap.scatter(list_lat, list_lon, 'red', size=400, marker=True)

    # draw crossing point
    gmap.marker(median_border_intersection[0], median_border_intersection[1], 'orange')

    #  DRAW PIECEWISE LINEAR COASTLINES
    border_width = 5
    gmap.plot(_border[1][1], _border[1][2], color='green', edge_width=border_width)
    gmap.plot(_border[2][1], _border[2][2], color='green', edge_width=border_width)

    # DRAW CONE OF UNCERTAINTY AT LANDFALL HOUR
    # gmap.circle(hurricane_center[0], hurricane_center[1], radius=cone_radius[landfall_time] * nm_to_m, color='green', alpha=0.2)

    # DRAW CONE OF UNCERTAINTY AT CROSSING
    # gmap.circle(median_border_intersection[0], median_border_intersection[1], radius=cou_border * nm_to_m, color='orange', alpha=0.5)
    _type = 'surge'
    map_name = 'map' + str(_landfall_track['adv_number']) + '_' + _type + '_' + _reference + '.html'
    gmap.draw(_output_location + map_name)

    print('---DONE SURGE SIMULATOR---')
    print("")
    list_dict_landfall = [dict_landfall, dict_landfall_prob]

    # return list_dict_landfall

if __name__ == "__main__":
    path_input = '/Users/kyoung/Box Sync/github/pelo/track_simulation/input/'
    track_gen_file_input = 'input_track_gen.csv'
    path = path_input + track_gen_file_input  # ** CHANGE HERE **
    df = pd.read_csv(path)
    dict_input = dict(zip(df.parameter, df.value))
    print("INPUT")
    print(df)
    print("")

    ######
    '''
    OPTIONS FOR INPUT
    - track_input_type: 'adv' / 'nwm'
    - reference: 'current' / 'bf_landfall'
    - numSegment: 5
    - numSamples: 5
    '''
    ######

    # STEP 1: CHOOSE WHICH FORECAST TO DEFINE THE HURRICANE TRACK
    input_type = dict_input['track_input_type']
    if input_type == 'adv':
        # -- PUBIC HURRICANE ADVISORY 15
        list_landfall = [0, 0, 0, 0, 0, 1, 1, 1]  # manual input of landfall status
        file_name = 'al092017-015_5day_pts.shp'
        file_location = '/Users/kyoung/Box Sync/github/data/noaa_forecast/al092017_5day_015/'  # modify for your location
        input_file = file_location + file_name
        advisory = read_shapefile(input_file, list_landfall)
    else:
        # -- NWM FORECAST INPUT
        file_location = dict_input['nwm_track_file_location']
        file_name = dict_input['nwm_track_file_name']
        input_file = file_location + file_name
        advisory = read_nwm_track(input_file)

    # STEP 2: SIMULATE HURRICANE TRACKS
    # track_simulator(advisory, dict_input)
    track_simulator_stratified(advisory, dict_input)
    # surge_simulator(advisory, dict_input)
