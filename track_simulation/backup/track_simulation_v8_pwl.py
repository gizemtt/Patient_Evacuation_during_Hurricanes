from scipy.stats import norm
import math
import gmplot
import geopandas as gpd
import numpy as np
import pandas as pd

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

def read_nwm_track(_file_location, _file_name):
    this_file = _file_location + _file_name
    track = pd.read_csv(this_file)
    forecast_hours = [12, 24, 36, 48, 72, 96, 120]
    df = pd.DataFrame()
    for i in forecast_hours:
        this_df = track.loc[track['forecast hour'] == i]
        df = df.append(this_df)

    print(df)
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
    # # DEFINE 6 CITIES LINES AND FIND THE INTERSECTION
    # city_1 = [29.88, -93.94]    # Port Arthur, tx
    # city_2 = [27.91, -97.15]    # Aransas pass, tx [lat, lon]
    # city_3 = [27.91, -97.15]    # Aransas pass, tx [lat, lon]
    # city_4 = [26.20, -98.23]    # McAllen, TX
    # city_5 = [27.80, -97.39]    # Corpus Christi, TX
    # city_6 = [25.90, -97.50]    # brownsville, tx

    # DEFINE 3 CITIES TO FIND TEXAS COASTAL LINE
    city_1 = [29.88, -93.94]    # Port Arthur, tx
    city_2 = [27.80, -97.39]    # Corpus Christi, TX
    city_3 = [25.90, -97.50]    # brownsville, tx

    # border_1_lat = [city_1[0], city_2[0]]
    # border_1_lon = [city_1[1], city_2[1]]
    # border_2_lat = [city_3[0], intersection[0]]
    # border_2_lon = [city_3[1], intersection[1]]
    # border_3_lat = [intersection[0], city_6[0]]
    # border_3_lon = [intersection[1], city_6[1]]

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
        output_intersection = output_intersection = [min_key, dict_intersection[min_key]]

        # return output_intersection
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

    # print("dict_intersection : ", dict_intersection)
    # print("dict_intersection_distance : ", dict_intersection_distance)
    try:
        min_key = min(dict_intersection_distance, key=dict_intersection_distance.get)
        output_intersection = [min_key, dict_intersection[min_key]]
    except ValueError:
        output_intersection = 'empty'

    # min_key = min(dict_intersection_distance, key=dict_intersection_distance.get)
    # output_intersection = [min_key, dict_intersection[min_key]]
    return output_intersection  # Format: [border#, [lat, lon]

def track_simulator(_landfall_track, _numScenario, _output_location, _reference):
    # STEP 1: GET THE EARLIEST LANDFALL TIME AND LOCATION
    index_landfall = _landfall_track['status'].index(1)
    landfall_time = _landfall_track['time'][index_landfall]
    landfall_lat = _landfall_track['coordinates'][index_landfall][0]    # 27.5N
    landfall_lon = _landfall_track['coordinates'][index_landfall][1]    # 97.5W

    # STEP 2: DEFINE THE CONE OF RADIUS
    # -- Yr 2019 2/3 probability circle
    conversion_factor = 1  # nautical miles to XXX
    cone_radius_yr19 = {0: 0 * conversion_factor,
                        12: 26 * conversion_factor,
                        24: 41 * conversion_factor,
                        36: 54 * conversion_factor,
                        48: 68 * conversion_factor,
                        72: 102 * conversion_factor,
                        96: 151 * conversion_factor,
                        120: 190 * conversion_factor}

   # -- Yr 2017 2/3 probability circle
    cone_radius = {0: 0 * conversion_factor,
                   12: 29 * conversion_factor,
                   24: 45 * conversion_factor,
                   36: 63 * conversion_factor,
                   48: 78 * conversion_factor,
                   72: 107 * conversion_factor,
                   96: 159 * conversion_factor,
                   120: 211 * conversion_factor}

    # STEP 3:  DEFINE THE REFERENCE POINT FOR STORM DIRECTION
    # -- A line using hurricane tracks
    reference_direction = {'current': index_landfall, 'bf_landfall': 1}
    hurricane_center = [landfall_lat, landfall_lon]
    landfall_lat_bf = _landfall_track['coordinates'][index_landfall - reference_direction[_reference]][0]    # 27.5N
    landfall_lon_bf = _landfall_track['coordinates'][index_landfall - reference_direction[_reference]][1]    # 97.5W
    endpoint = [landfall_lat_bf, landfall_lon_bf]
    track_line = get_line(hurricane_center, endpoint)

    # -- Get slope of the perpendicular line
    p_line_slope = -1 / track_line[0]
    p_line_intercept = landfall_lat - p_line_slope * landfall_lon
    p_line = [p_line_slope, p_line_intercept]

    # create new landfall points
    z_score = norm.ppf(5 / 6)
    radius = cone_radius[landfall_time]  # unit = nautical miles
    sigma = radius / z_score             # unit = nautical miles

    list_percentile = []
    dict_landfall = {}
    list_lon = []
    list_lat = []

    for i in range(_numScenario + 1):
        if (i == 0 or i == _numScenario):
            continue
        percentile = i / _numScenario
        d = abs(norm.ppf(percentile)) * sigma
        dist = d / 60  # in decimal
        rad = math.atan(p_line[0])
        if percentile <= 0.5:
            multiplier = -1
        else:
            multiplier = 1
        new_lon = round(multiplier * dist * math.cos(rad) + landfall_lon, 3)
        new_lat = round(multiplier * dist * math.sin(rad) + landfall_lat, 3)
        new_center = [new_lat, new_lon]
        dict_landfall[i] = new_center
        list_percentile.append(percentile)
        list_lon.append(new_lon)
        list_lat.append(new_lat)

    print("Landfall center location: ", hurricane_center)
    print("Potential landfall locations: ", dict_landfall)

    list_track_lat = []
    list_track_lon = []
    for i in range(len(_landfall_track['coordinates'])):
        list_track_lat.append(_landfall_track['coordinates'][i][0])
        list_track_lon.append(_landfall_track['coordinates'][i][1])

    gmap = gmplot.GoogleMapPlotter(landfall_lat, landfall_lon, 8)
    gmap.apikey = 'AIzaSyB9QlHsyVOEcVUDJZFju2S0xeOSfcfAfEk'
    gmap.scatter(list_lat, list_lon, 'red', size=400, marker=True)
    gmap.scatter(list_track_lat, list_track_lon, 'blue', size=400, marker=True)
    nm_to_m = 1852
    return dict_landfall

def surge_simulator(_landfall_track, _numScenario, _output_location, _reference, _border_list):
    _border = _border_list[0]
    for border in _border_list[1]:
        _border_intersect = _border_list[1][border]

    print("SURGE SIM - border_intersect: ", _border_intersect)

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
    print(landfall_time_bf)
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

    # DEFINE THE CONE OF UNCERTAINTY AT BORDER AND FIND SIGMA
    dist_ref_median_intersect = get_distance(endpoint, median_border_intersection)
    dist_ref_hurricane_center = get_distance(endpoint, hurricane_center)
    cou_border = dist_ref_median_intersect / dist_ref_hurricane_center * (radius - radius_bf) + radius_bf
    sigma_crossing = cou_border / z_score

    # PICK CANDIDATE STORM DIRECTIONS
    # min_storm_direction_number = max(storm_direction_number[0] - 3, 1)
    # max_storm_direction_number = min(storm_direction_number[0] + 3, 10)
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

        print("run: ", i)
        print("this_storm_direction: ", this_storm_direction)

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
    print("Landfall Locatiosn:")
    print(dict_landfall)
    print("")
    print("Scenario Prob:")
    print(dict_landfall_prob)

    # DRAW MAP
    gmap = gmplot.GoogleMapPlotter(landfall_lat, landfall_lon, 8)
    gmap.apikey = 'AIzaSyB9QlHsyVOEcVUDJZFju2S0xeOSfcfAfEk'

    # draw hurricane track
    list_track_lat = []
    list_track_lon = []
    for i in range(len(_landfall_track['coordinates'])):
        this_lat = _landfall_track['coordinates'][i][0]
        this_lon = _landfall_track['coordinates'][i][1]
        list_track_lat.append(this_lat)
        list_track_lon.append(this_lon)
        # gmap.marker(this_lat, this_lon, title=_landfall_track['time'][i])  # add labels
        gmap.marker(this_lat, this_lon, 'blue', title='this title')  # add labels
    # gmap.scatter(list_track_lat, list_track_lon, 'blue', size=400, marker=True)

    # draw landfall points
    list_lon = []
    list_lat = []
    for key, value in dict_landfall.items():
        list_lon.append(value[1][1])
        list_lat.append(value[1][0])
    gmap.scatter(list_lat, list_lon, 'red', size=400, marker=True)

    # draw crossing point
    gmap.marker(median_border_intersection[0], median_border_intersection[1], 'orange')

    # draw reference points
    list_reference_lon = [landfall_lon, landfall_lon_bf]
    list_reference_lat = [landfall_lat, landfall_lat_bf]
    gmap.scatter(list_reference_lat, list_reference_lon, 'green', size=400, marker=True)

    nm_to_m = 1852

    #  DRAW PIECEWISE LINEAR COASTLINES
    border_width = 5
    gmap.plot(_border[1][1], _border[1][2], color='green', edge_width=border_width)
    gmap.plot(_border[2][1], _border[2][2], color='green', edge_width=border_width)

    # DRAW CONE OF UNCERTAINTY ALONG THE HURRICANE TRACK
    # for i in range(len(_landfall_track['time'])):
    #     gmap.circle(_landfall_track['coordinates'][i][0], _landfall_track['coordinates'][i][1], radius=cone_radius[_landfall_track['time'][i]] * nm_to_m, color='green', alpha=0.2)

    # DRAW CONE OF UNCERTAINTY AT LANDFALL HOUR
    gmap.circle(hurricane_center[0], hurricane_center[1], radius=cone_radius[landfall_time] * nm_to_m, color='green', alpha=0.2)

    # DRAW CONE OF UNCERTAINTY AT CROSSING
    gmap.circle(median_border_intersection[0], median_border_intersection[1], radius=cou_border * nm_to_m, color='orange', alpha=0.5)
    _type = 'surge'
    map_name = 'map' + str(_landfall_track['adv_number']) + '_' + _type + '_' + _reference + '.html'
    gmap.draw(_output_location + map_name)

    return dict_landfall

def draw_map(_landfall_track, _dict_landfall, _output_location, _reference, _type):
    list_track_lat = []
    list_track_lon = []
    for i in range(len(_landfall_track['coordinates'])):
        list_track_lat.append(_landfall_track['coordinates'][i][0])
        list_track_lon.append(_landfall_track['coordinates'][i][1])

    index_landfall = _landfall_track['status'].index(1)
    landfall_time = _landfall_track['time'][index_landfall]
    landfall_lat = _landfall_track['coordinates'][index_landfall][0]    # 27.5N
    landfall_lon = _landfall_track['coordinates'][index_landfall][1]    # 97.5W
    hurricane_center = [landfall_lat, landfall_lon]

    # DEFINE THE REFERENCE POINT FOR STORM DIRECTION
    reference_direction = {'current': index_landfall, 'bf_landfall': 1}

    # a line using hurricane tracks: landfall location and location 12 hours ahead of landfall
    hurricane_center = [landfall_lat, landfall_lon]
    landfall_lat_bf = _landfall_track['coordinates'][index_landfall - reference_direction[_reference]][0]    # 27.5N
    landfall_lon_bf = _landfall_track['coordinates'][index_landfall - reference_direction[_reference]][1]    # 97.5W

    conversion_factor = 1  # nautical miles to XXX
    cone_radius = {0: 0 * conversion_factor,
                   12: 29 * conversion_factor,
                   24: 45 * conversion_factor,
                   36: 63 * conversion_factor,
                   48: 78 * conversion_factor,
                   72: 107 * conversion_factor,
                   96: 159 * conversion_factor,
                   120: 211 * conversion_factor}

    list_lon = []
    list_lat = []
    for key, value in _dict_landfall.items():
        list_lon.append(value[1])
        list_lat.append(value[0])

    list_reference_lon = [landfall_lon, landfall_lon_bf]
    list_reference_lat = [landfall_lat, landfall_lat_bf]

    gmap = gmplot.GoogleMapPlotter(landfall_lat, landfall_lon, 8)
    gmap.apikey = 'AIzaSyB9QlHsyVOEcVUDJZFju2S0xeOSfcfAfEk'
    gmap.scatter(list_lat, list_lon, 'red', size=400, marker=True)
    gmap.scatter(list_track_lat, list_track_lon, 'blue', size=400, marker=True)
    gmap.scatter(list_reference_lat, list_reference_lon, 'green', size=400, marker=True)
    nm_to_meter = 1852

    # create 2/3 circle
    # unmute to add 2/3 circles to all locations
    # for i in range(len(_landfall_track['time'])):
    #      gmap.circle(_landfall_track['coordinates'][i][0], _landfall_track['coordinates'][i][1], radius=cone_radius[_landfall_track['time'][i]] * nm_to_meter, color='yellow', alpha=0.3)

    gmap.circle(hurricane_center[0], hurricane_center[1], radius=cone_radius[landfall_time] * nm_to_meter, color='yellow', alpha=0.3)
    map_name = 'map' + str(_landfall_track['adv_number']) + '_' + _type + '_' + _reference + '.html'
    gmap.draw(_output_location + map_name)


if __name__ == "__main__":
    input_type = 'adv'  # ['adv', 'nwm']
    reference = 'bf_landfall'  # {'current': index_landfall, 'bf_landfall': 1}
    numSegment = 6  # number of segments (example: 4 segments creates 3 (= 4-1) landfall locations)
    output_location = '/Users/kyoung/Box Sync/github/maps/'  # modify for your location

    # STEP 1: CHOOSE WHICH FORECAST TO DEFINE THE HURRICANE TRACK
    if input_type == 'adv':
        # 1. PUBIC HURRICANE ADVISORY 15
        list_landfall = [0, 0, 0, 0, 1, 1, 1, 1]  # manual input of landfall status
        file_name = 'al092017-015_5day_pts.shp'
        file_location = '/Users/kyoung/Box Sync/github/noaa_forecast/al092017_5day_015/'  # modify for your location

        # 2. PUBIC HURRICANE ADVISORY 16
        # list_landfall = [0, 0, 0, 0, 1, 1, 1, 1]  # manual input of landfall status
        # file_name = 'al092017-016_5day_pts.shp'
        # file_location = '/Users/kyoung/Box Sync/github/noaa_forecast/al092017_5day_016/'  # modify for your location

        # 3. PUBIC HURRICANE ADVISORY 18
        # list_landfall = [0, 0, 0, 0, 1, 1, 1, 1]  # manual input of landfall status
        # file_name = 'al092017-018_5day_pts.shp'
        # file_location = '/Users/kyoung/Box Sync/github/noaa_forecast/al092017_5day_018/'  # modify for your location
        input_file = file_location + file_name
        advisory = read_shapefile(input_file, list_landfall)
    else:
        # 4. NWM FORECAST INPUT
        file_location = '/Users/kyoung/Box Sync/github/pelo/input/data/location/nwm/'
        file_name = '2017082400_nwm_med_range_storm_center.csv'
        input_file = file_location + file_name
        advisory = read_nwm_track(input_file)

    print("ADVISORY : ", advisory)

    # STEP 2: CHOOSE COASTLINE AND SIMULATE HURRICANE TRACKS
    borders = get_texascoast()
    dict_landfall_locations = track_simulator(advisory, numSegment, output_location, reference)
    draw_map(advisory, dict_landfall_locations, output_location, reference, input_type)

    # dict_landfall_surge = surge_simulator(advisory, numSegment, output_location, reference, borders)
