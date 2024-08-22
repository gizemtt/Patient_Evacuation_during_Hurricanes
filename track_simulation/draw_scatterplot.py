import gmplot
import os

def scatterplot(scenario_name, dict_set, coordinates, start_date, end_date):
    dict_SLOSH = dict_set[0]
    dict_NWM = dict_set[1]

    sender_SLOSH = dict_SLOSH.keys()
    sender_NWM = dict_NWM.keys()
    sender_BOTH = dict_SLOSH.keys() & dict_NWM.keys()
    color_code = ['blue', 'teal', 'indigo']
    location_list = [sender_SLOSH, sender_NWM, sender_BOTH]

    map_center = [29.76, -95.37]    # Houston, TX
    gmap = gmplot.GoogleMapPlotter(map_center[0], map_center[1], 8)
    gmap.apikey = 'AIzaSyB9QlHsyVOEcVUDJZFju2S0xeOSfcfAfEk'

    for i in range(len(location_list)):
        marker_color = color_code[i]
        sender_list = location_list[i]

        list_lon = []
        list_lat = []
        for j in sender_list:
            lat = coordinates['latitude'][coordinates['code'] == j]
            lon = coordinates['longitude'][coordinates['code'] == j]
            list_lon.append(lon)
            list_lat.append(lat)

        gmap.scatter(list_lat, list_lon, marker_color, size=1000, marker=True)

    map_name = 'map' + '_' + scenario_name + '_' + start_date + '_' + end_date + '.html'
    output_directory = start_date + '_' + end_date
    output_location = '/Users/kyoung/Box Sync/github/maps/' + output_directory

    try:
        os.mkdir(output_location)
        print("Directory Created")
    except FileExistsError:
        pass

    gmap.draw(output_location + '/' + map_name)
