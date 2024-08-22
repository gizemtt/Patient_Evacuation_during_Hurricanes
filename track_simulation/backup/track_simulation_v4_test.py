import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt


# STEP 1: CONVERT HOSPITAL LOCATION CSV FILE TO GEOPANDAS DATAFRAME
coordinate_file_location = '/Users/kyoung/Box Sync/Researc_personal/Code/python/vehicle_assignment/input/data/location/coordinate_lookup_reduced.csv'
coordinatesDF = pd.read_csv(coordinate_file_location)

geometry = [Point(xy) for xy in zip(coordinatesDF.longitude, coordinatesDF.latitude)]
crs = {'init': 'epsg:2263'}  # http://www.spatialreference.org/ref/epsg/2263/
coordinatesGDF = gpd.GeoDataFrame(coordinatesDF, crs=crs, geometry=geometry)
senderGDF = coordinatesGDF[coordinatesGDF['type'] == 'Sender']
senderGDF = senderGDF.reset_index(drop=True)

# STEP 2: IMPORT SLOSH SHAPE OUTPUTS INTO GEOPANDAS DATAFRAME
file_location = '/Users/kyoung/Box Sync/Researc_personal/Code/python/vehicle_assignment/shape_files/'
file_name = 'ene410i1.shp'
shp_file = file_location + file_name
sf = gpd.read_file(shp_file)
col_surge = 'surge'
sf_columns = sf.columns.values
sf_columns[3] = col_surge
sf.columns = sf_columns
# sf = sf[sf[col_surge] != 99.9]
sf.loc[sf[col_surge] == 99.9, col_surge] = 0
sf = sf[sf[col_surge] >= 0]
sf = sf.reset_index(drop=True)


# STEP 3: FIND THE INTERSECTION BETWEEN HOSPITALS AND SLOSH GEODATAFRAME
fig, ax = plt.subplots()
sf.plot(ax=ax, facecolor='gray')
senderGDF.plot(ax=ax, color='gold', markersize=2)
# plt.tight_layout()
plt.show()
# gpd.sjoin(senderGDF, sf[['i-index', 'geometry']], how='left', op='within')
# gpd.sjoin(senderGDF, sf, how='innter', op='intersects')

# STEP 4: FIND SURGE VALUES FOR INTERSECTIONS
intersection_file_name = 'intersection.csv'
intersection_file_location = '/Users/kyoung/Box Sync/Researc_personal/Code/python/vehicle_assignment/input/data/location/'
intersectionDF = pd.read_csv(intersection_file_location + intersection_file_name)
intersectionDF = intersectionDF[intersectionDF.type == 'Sender']
intersectionDF = intersectionDF.reset_index(drop=True)

intersectionDF[(intersectionDF['i-index'] == 160) & (intersectionDF['j-index'] == 78)]['code'].values

directionSet = ['wsw', 'w', 'wnw', 'nw', 'nnw', 'n', 'nne', 'ne', 'ene']
categorySet = ['0', '1', '2', '3', '4', '5']
tideSet = ['05i2', '10i2', '15i2']
tideSet_average = ["05i1", "10i1", "15i1"]

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
