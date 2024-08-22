import gdal
import geopandas
import numpy

fn =
ds = gdal.Open(fn)

band1 = ds.GetRasterBand(1).ReadAsArray()
print(band1.shape)
