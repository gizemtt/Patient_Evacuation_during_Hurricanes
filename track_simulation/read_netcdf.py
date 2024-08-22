from netCDF4 import Dataset
import numpy as np
from scipy.stats import norm
import math
import gmplot


file_name = 'nwm.t00z.medium_range.forcing.f004.conus.nc.nc'
file_location = '/Users/kyoung/Box Sync/Researc_personal/Code/python/netcdf/'

nc_file = file_location + file_name
fh = Dataset(nc_file, mode='r')
# print(fh)
print(fh.variables.keys())
print("")
rain = fh.variables['RAINRATE']
print(rain)

print("")
print("")

for d in fh.dimensions.items():
    print(d)

print("")
print("")

print(rain.dimensions)
print(rain.shape)

print("")
print("")

t = fh.variables['time']
x, y = fh.variables['x'], fh.variables['y']
print(t)
print("")
print(x)
print("")
print(y)

print("")
time = t[:]
print(time)
xx, yy = x[:], y[:]
print('shape of rain variable: %s' % repr(rain.shape))
rainslice = rain[0, xx > xx.max() / 2, yy > yy.max() / 2]
print('shape of rain slice: %s' % repr(rainslice.shape))


print("")
coordinate = fh.variables['ProjectionCoordinateSystem']
