import pandas as pd
import gmplot
import json
import requests
import geopandas as gpd
import matplotlib.pyplot as plt
import fiona
import numpy as np
from get_hospitals import getHospitals


def readRawData(input_file):
    print("Reading CSV")
    path = '/Users/kyoung/Box Sync/github/data/gov/'

    df = pd.read_csv(path + input_file)
    df = df[df['STATE'] == 'TX']

    tsa_file_name = 'trauma_service_areas.csv'
    df_tsa = pd.read_csv(path + tsa_file_name)

    cmoc_tsa = ['Q', 'R', 'H']
    dict_cmoc_tsa = {}
    for i in cmoc_tsa:
        list_county = df_tsa[df_tsa['TSA'] == i]['COUNTY'].tolist()
        dict_cmoc_tsa[i] = list_county

    df_output = pd.DataFrame()

    for i in dict_cmoc_tsa.keys():
        for j in dict_cmoc_tsa[i]:
            county = j.upper()
            df_county = df[df['COUNTY'] == county]
            df_output = df_output.append(df_county)

    df_output = df_output.reset_index(drop=True)
    print("CSV Read")
    print("")

    return df_output


def getLatLng(location_string, apikey=""):
    apikey = 'AIzaSyB9QlHsyVOEcVUDJZFju2S0xeOSfcfAfEk'
    geocode = requests.get(
        'https://maps.googleapis.com/maps/api/geocode/json?address="%s"&key=%s' % (location_string, apikey))
    geocode = json.loads(geocode.text)
    latlng_dict = geocode['results'][0]['geometry']['location']
    return latlng_dict['lat'], latlng_dict['lng']


def writeFile(input_file, df):
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LONGITUDE, df.LATITUDE), crs="EPSG:4326")

    path_output = '/Users/kyoung/Box Sync/github/data/gis/'

    # Shapefile
    facility_type = input_file[1]
    file_name = '%s.shp' % (facility_type)
    gdf.to_file(path_output + 'shp/' + file_name)
    print("Shapefile Saved")

    # KML file
    fiona.supported_drivers['KML'] = 'rw'
    kml_file = '%s.kml' % (facility_type)
    gdf.to_file(path_output + 'kml/' + kml_file, driver='KML')
    print('KML file Saved')
    print("")


def getCountyGDF(df):
    # get all TX county boundaries
    path = '/Users/kyoung/Box Sync/github/data/gis/shp/'
    directory = 'Texas_County_Boundaries/'
    file_name = 'Texas_County_Boundaries.shp'
    txcounty = gpd.read_file(path + directory + file_name)

    # get counties of CMOC
    path = '/Users/kyoung/Box Sync/github/data/gov/'
    tsa_file_name = 'trauma_service_areas.csv'
    df_tsa = pd.read_csv(path + tsa_file_name)

    cmoc_tsa = ['Q', 'R', 'H']
    dict_cmoc_tsa = {}
    for i in cmoc_tsa:
        list_county = df_tsa[df_tsa['TSA'] == i]['COUNTY'].tolist()
        dict_cmoc_tsa[i] = list_county

    county_list = []
    for key in dict_cmoc_tsa.keys():
        for i in dict_cmoc_tsa[key]:
            county_list.append(i.upper())

    # choose only OPEN and none -999 locations as data input
    df = df[df['STATUS'] == 'OPEN']
    df = df[df['BEDS'] != -999]

    # get total bed counts of CMOC counties
    dict_beds = {}
    dict_facility = {}
    for i in county_list:
        sum_bed = df[df['COUNTY'] == i]['BEDS'].sum()
        facility_count = len(df[df['COUNTY'] == i])
        this_key = i.title()
        dict_beds[this_key] = sum_bed
        dict_facility[this_key] = facility_count

    county_list = [i.title() for i in county_list]

    # create a GDF of CMOC counties
    cmocCounty = gpd.GeoDataFrame()
    for i in county_list:
        cmocCounty = cmocCounty.append(txcounty[txcounty['CNTY_NM'] == i])

    # add a TTL_BEDS column to CMOC county gdf
    cmocCounty['TTL_BEDS'] = cmocCounty['CNTY_NM'].map(dict_beds)
    cmocCounty['TTL_FACILITY'] = cmocCounty['CNTY_NM'].map(dict_facility)

    return cmocCounty

def plotGoogleMap(facility_input, latlng, df, map_name=""):
    facility_type = facility_input[1]

    gmap = gmplot.GoogleMapPlotter(latlng[0], latlng[1], zoom=9)
    gmap.apikey = 'AIzaSyB9QlHsyVOEcVUDJZFju2S0xeOSfcfAfEk'
    radius_dict = {'hospital': 20, 'nh': 20}
    color_map = {'RECEIVER': 'blue', 'SENDER': 'red', 'STAGING': 'green', "": 'orange'}
    column_map = {'RECEIVER': 'CAPACITY', 'SENDER': 'DEMAND', '': 'BEDS'}

    if len(df) == 1:
        df = df[0]
        df.columns = df.columns.str.upper()
        facility_CATEGORY = map_name

        for i in range(len(df)):
            lat = df.iloc[i]['LATITUDE']
            lon = df.iloc[i]['LONGITUDE']

            if facility_CATEGORY != 'STAGING':
                bed = df.iloc[i][column_map[map_name]]
                gmap.circle(lat, lon, radius=bed * radius_dict[facility_type], color=color_map[map_name], alpha=0.3)
            else:
                gmap.circle(lat, lon, radius=5000, color=color_map[facility_CATEGORY])

    else:
        for this_df in df:
            this_df.columns = this_df.columns.str.upper()
            facility_CATEGORY = this_df['CATEGORY'].unique()[0]

            for i in range(len(this_df)):
                lat = this_df.iloc[i]['LATITUDE']
                lon = this_df.iloc[i]['LONGITUDE']

                if facility_CATEGORY != 'STAGING':
                    bed = this_df.iloc[i][column_map[facility_CATEGORY]]
                    gmap.circle(lat, lon, radius=bed * radius_dict[facility_type], color=color_map[facility_CATEGORY], alpha=0.3)
                else:
                    gmap.circle(lat, lon, radius=5000, color=color_map[facility_CATEGORY])

    path = '/Users/kyoung/Box Sync/github/data/map/'
    file_name = 'map_%s%s.html' % (facility_type, map_name)
    gmap.draw(path + file_name)


def plotCountyMap(facility_input, df_facility, gdf_county):
    # create a plot
    fig, ax = plt.subplots(1, 1)
    gdf_county.boundary.plot(ax=ax, edgecolor='black', linewidth=0.5)
    bins = {'bins': [200, 400, 800, 1600, 3200, 6400, 12800, 25600]}
    gdf_county.plot(ax=ax, column='TTL_BEDS', cmap='OrRd', scheme='userdefined', classification_kwds=bins)

    # create a sidebar legend
    vmin = min(gdf_county['TTL_BEDS'])
    vmax = max(gdf_county['TTL_BEDS'])
    sm = plt.cm.ScalarMappable(cmap='OrRd', norm=plt.Normalize(vmin=vmin, vmax=vmax))

    # empty array for the data range
    sm._A = []

    # add the colorbar to the figure
    cbar = fig.colorbar(sm)

    # add facility locations to plot
    gdf_facility = gpd.GeoDataFrame(df_facility, geometry=gpd.points_from_xy(df_facility.LONGITUDE, df_facility.LATITUDE), crs="EPSG:4326")
    gdf_facility.plot(ax=ax, marker='o', color='red', markersize=4)

    # save image
    image_path = '/Users/kyoung/Box Sync/github/data/map/'
    image_name = 'countymap_%s.png' % (facility_input[1])
    fig.savefig(image_path + image_name, dpi=200)


def main(input_file):
    location_string = "Houston"
    latlng = getLatLng(location_string)
    df = readRawData(input_file[0])
    cmoc_gdf = getCountyGDF(df)
    writeFile(input_file, df)

    plotCountyMap(input_file, df, cmoc_gdf)
    plotGoogleMap(input_file, latlng, [df])

    df_locations = getHospitals(1, 1, 20)
    plotGoogleMap(input_file, latlng, [df_locations[0]], 'STAGING')
    plotGoogleMap(input_file, latlng, [df_locations[1]], 'SENDER')
    plotGoogleMap(input_file, latlng, [df_locations[2]], 'RECEIVER')
    plotGoogleMap(input_file, latlng, [df_locations[0], df_locations[1], df_locations[2]], 'ALL')

    return [df, cmoc_gdf, df_locations]

if __name__ == "__main__":
    input_file = ['Nursing_Homes.csv', 'nh']
    input_file = ['Hospitals.csv', 'hospital']

    list_output = main(input_file)
    df = list_output[0]
    gdf = list_output[1]
    dfs = list_output[2]

    if input_file[1] == 'hospital':
        print('HOSPITAL STATUS')
        table = pd.pivot_table(df, values=['NAME', 'BEDS'], index=['COUNTY', 'STATUS'], aggfunc={'BEDS': np.sum, 'NAME': len})

        print(table)
        print("")
        print('     NUMBER OF COUNTIES: %s' % len(df['COUNTY'].unique()))
        print('     NUMBER OF HOSPITALS: %s' % sum(table['NAME']))
        print('     NUMBER OF TOTAL BEDS: %s' % sum(table['BEDS']))
        print('     NUMBER OF AVAILABLE BEDS: %s' % str(sum(table['BEDS']) * 0.3))

        print("")
        df = df[df['STATUS'] == 'OPEN']
        df = df[df['BEDS'] != -999]
        table = pd.pivot_table(df, values=['NAME', 'BEDS'], index='COUNTY', aggfunc={'BEDS': np.sum, 'NAME': len})
        print(table)
        print("")
        print('     NUMBER OF COUNTIES: %s' % len(df['COUNTY'].unique()))
        print('     NUMBER OF HOSPITALS: %s' % sum(table['NAME']))
        print('     NUMBER OF TOTAL BEDS: %s' % sum(table['BEDS']))
        print('     NUMBER OF AVAILABLE BEDS: %s' % str(sum(table['BEDS']) * 0.3))

    else:
        print("NURSING HOME STATUS")
        table = pd.pivot_table(df, values=['NAME', 'BEDS'], index='COUNTY', aggfunc={'BEDS': np.sum, 'NAME': len})
        print(table)
        print("")
        print('     NUMBER OF COUNTIES: %s' % len(df['COUNTY'].unique()))
        print('     NUMBER OF NURSING HOMES: %s' % sum(table['NAME']))
