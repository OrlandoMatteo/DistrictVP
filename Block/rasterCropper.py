from rasterio.mask import mask
import rasterio
from shapely.geometry import MultiPolygon, Point, shape,Polygon
import fiona
import rasterio
import os
import numpy as np
from rasterio.plot import show
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
from fiona.crs import from_epsg
import os
import matplotlib.pyplot as plt
import gdal
import glob


# Openf file with the roofs for a single block
src=fiona.open("blockRoofs.shp")
pol=MultiPolygon([shape(building["geometry"]) for building in src])

rasterfiles=glob.glob('/media/HD/raster/*[!.aux.xml,!.dbf,!.py,!.csv,!.qpj]')
gdf=gpd.GeoSeries(pol)
basePath='/media/HD/blockRaster/'

l=len(rasterfiles)

print ("Start cropping")
i=0
for raster in rasterfiles:
    i+=1
    print(f'Completed at {i*100/l:.2}%\r', end="")
    data=rasterio.open(raster)
    clippedImg,clippedTrans=mask(dataset=data,shapes=gdf,crop=True)
    out_meta = data.meta.copy()
    out_meta.update({"driver": "GTiff",
                    "height": clippedImg.shape[1],
                    "width": clippedImg.shape[2],
                    "transform": clippedTrans}
                            )
    out_file=raster.replace('raster','blockRaster')
    with rasterio.open(out_file, "w",**out_meta) as dest:
            dest.write(clippedImg)
