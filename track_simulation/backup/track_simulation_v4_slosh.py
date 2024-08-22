from scipy.stats import norm
import math
import gmplot
import geopandas as gpd

def read_shapefile(shfile):
    sf = gpd.read_file(shfile)
    sf = sf.sort_values(by=['TAU'], ascending=True)
    advisory = {}
    advisory['adv_number'] = sf.ADVISNUM.unique()[0]
    list_time = []
    list_coordinate = []
    for i in range(len(sf)):
        list_time.append(sf.iloc[i].TAU)
        list_coordinate.append([sf.iloc[i].LAT, sf.iloc[i].LON])
    list_landfall = [0, 0, 0, 0, 0, 1, 1, 1]  # manual input of landfall status
    advisory['status'] = list_landfall
    advisory['coordinates'] = list_coordinate
    advisory['time'] = list_time
    return advisory

def convert_decimal(input):
    decimal = math.floor(input)
    minute = math.floor(60 * abs(input - decimal))
    second = int(round(3600 * abs(decimal - input) - 60 * minute, 0))
    output = [decimal, minute, second]
    return output

def get_intersection(line1, line2):
    lon = (line2[1] - line1[1]) / (line1[0] - line2[0])
    lat = lon * line1[0] + line1[1]
    output = [lat, lon]
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

def track_simulator(_landfall_track, _numScenario, _output_location):
    index_landfall = _landfall_track['status'].index(1)
    landfall_time = _landfall_track['time'][index_landfall]
    landfall_lat = _landfall_track['coordinates'][index_landfall][0]    # 27.5N
    landfall_lon = _landfall_track['coordinates'][index_landfall][1]    # 97.5W

    conversion_factor = 1  # nautical miles to XXX
    # Yr 2019 2/3 probability circle
    cone_radius_yr19 = {0: 0 * conversion_factor,
                        12: 26 * conversion_factor,
                        24: 41 * conversion_factor,
                        36: 54 * conversion_factor,
                        48: 68 * conversion_factor,
                        72: 102 * conversion_factor,
                        96: 151 * conversion_factor,
                        120: 190 * conversion_factor}

   # Yr 2017 2/3 probability circle
    cone_radius = {0: 0 * conversion_factor,
                   12: 29 * conversion_factor,
                   24: 45 * conversion_factor,
                   36: 63 * conversion_factor,
                   48: 78 * conversion_factor,
                   72: 107 * conversion_factor,
                   96: 159 * conversion_factor,
                   120: 211 * conversion_factor}

    # DEFINE 6 CITIES LINES AND FIND THE INTERSECTION
    city_1 = [29.88, -93.94]    # Port Arthur, tx
    city_2 = [27.91, -97.15]    # Aransas pass, tx [lat, lon]
    city_3 = [27.91, -97.15]    # Aransas pass, tx [lat, lon]
    city_4 = [26.20, -98.23]    # McAllen, TX
    city_5 = [27.80, -97.39]    # Corpus Christi, TX
    city_6 = [25.90, -97.50]    # brownsville, tx

    # get border lines
    border1 = get_line(city_1, city_2)
    border2 = get_line(city_3, city_4)
    border3 = get_line(city_5, city_6)
    intersection = get_intersection(border2, border3)

    border_1_lat = [city_1[0], city_2[0]]
    border_1_lon = [city_1[1], city_2[1]]
    border_2_lat = [city_3[0], intersection[0]]
    border_2_lon = [city_3[1], intersection[1]]
    border_3_lat = [intersection[0], city_6[0]]
    border_3_lon = [intersection[1], city_6[1]]

    # a line using hurricane tracks: landfall location and location 12 hours ahead of landfall
    hurricane_center = [landfall_lat, landfall_lon]
    landfall_lat_bf = _landfall_track['coordinates'][index_landfall - 1][0]    # 27.5N
    landfall_lon_bf = _landfall_track['coordinates'][index_landfall - 1][1]    # 97.5W
    endpoint_4 = [landfall_lat_bf, landfall_lon_bf]
    track_line = get_line(hurricane_center, endpoint_4)

    # Get slope of the perpendicular line
    p_line_slope = -1 / track_line[0]
    p_line_intercept = landfall_lat - p_line_slope * landfall_lon
    guide_line = [p_line_slope, p_line_intercept]

    # create new landfall points
    z_score = norm.ppf(5 / 6)
    radius = cone_radius[landfall_time]  # unit = nautical miles
    sigma = radius / z_score             # unit = nautical miles

    list_percentile = []
    list_landfall = []
    list_lon = []
    list_lat = []

    for i in range(_numScenario + 1):
        if (i == 0 or i == _numScenario):
            continue
        percentile = i / _numScenario
        d = abs(norm.ppf(percentile)) * sigma
        dist = d / 60  # in decimal
        rad = math.atan(guide_line[0])
        if percentile <= 0.5:
            multiplier = -1
        else:
            multiplier = 1
        new_lon = round(multiplier * dist * math.cos(rad) + landfall_lon, 3)
        new_lat = round(multiplier * dist * math.sin(rad) + landfall_lat, 3)
        new_center = [new_lat, new_lon]
        list_landfall.append(new_center)
        list_percentile.append(percentile)
        list_lon.append(new_lon)
        list_lat.append(new_lat)

    print("Landfall center location: ", hurricane_center)
    print("Potential landfall locations: ", list_landfall)

    list_track_lat = []
    list_track_lon = []
    for i in range(len(_landfall_track['coordinates'])):
        list_track_lat.append(_landfall_track['coordinates'][i][0])
        list_track_lon.append(_landfall_track['coordinates'][i][1])

    gmap = gmplot.GoogleMapPlotter(landfall_lat, landfall_lon, 8)
    gmap.apikey = 'AIzaSyB9QlHsyVOEcVUDJZFju2S0xeOSfcfAfEk'
    gmap.scatter(list_lat, list_lon, 'red', size=400, marker=True)
    gmap.scatter(list_track_lat, list_track_lon, 'blue', size=400, marker=True)
    nm_to_meter = 1852

    # create 2/3 circle
    # unmute to add 2/3 circles to all locations
    # for i in range(len(_landfall_track['time'])):
    #      gmap.circle(_landfall_track['coordinates'][i][0], _landfall_track['coordinates'][i][1], radius=cone_radius[_landfall_track['time'][i]] * nm_to_meter, color='yellow', alpha=0.3)

    gmap.circle(hurricane_center[0], hurricane_center[1], radius=cone_radius[landfall_time] * nm_to_meter, color='yellow', alpha=0.3)

    # create piecewise linear coastlines
    border_width = 5
    gmap.plot(border_1_lat, border_1_lon, color='green', edge_width=border_width)
    gmap.plot(border_2_lat, border_2_lon, color='green', edge_width=border_width)
    gmap.plot(border_3_lat, border_3_lon, color='green', edge_width=border_width)

    map_name = 'map' + str(_landfall_track['adv_number']) + '_' + str(_numScenario) + '.html'
    gmap.draw(_output_location + map_name)

    return list_landfall


if __name__ == "__main__":
    numSegment = 6  # number of segments (example: 4 segments creates 3 (= 4-1) landfall locations)
    file_name = 'al092017-015_5day_pts.shp'
    file_location = '/Users/kyoung/Downloads/al092017_5day_015/'  # modify for your location

    file_name = 'al092017-016_5day_pts.shp'
    file_location = '/Users/kyoung/Downloads/al092017_5day_016/'  # modify for your location

    shp_file = file_location + file_name
    advisory = read_shapefile(shp_file)
    output_location = '/Users/kyoung/Desktop/maps/'  # modify for your location
    landfall_locations = track_simulator(advisory, numSegment, output_location)
