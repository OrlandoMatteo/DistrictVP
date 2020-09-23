
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
from pymongo import MongoClient
from PIL import Image
import numpy as np
from osgeo import gdal

client=MongoClient()
croppedRaster=glob.glob('/media/HD/rasterCropped/*')


def pixel2coord(col, row):
    #Returns global coordinates to pixel center using base-0 raster index
    xp = a * col + b * row + a * 0.5 + b * 0.5 + c
    yp = d * col + e * row + d * 0.5 + e * 0.5 + f
    return[xp, yp]

if __name__=="__main__":
    print("Starting...")
    nOfRaster=len(croppedRaster)
    for i,raster in enumerate(croppedRaster):
        im = np.array(Image.open(raster))
        ds = gdal.Open(raster)

        # unravel GDAL affine transform parameters
        c, a, b, f, d, e = ds.GetGeoTransform()
            
        notNull=np.count_nonzero(~np.isnan(im))
        rasterShape=im.shape
        collection=client.raster[raster.split('/')[-1]]
        completion=0

        print(f"Analyzing raster {i} of {nOfRaster} ({i*100/nOfRaster}%)")
        for i in range(rasterShape[0]):
            for j in range(rasterShape[1]):
                if not np.isnan(im[i][j]):
                    geojson={"type":"Point","coordinates":[]}
                    geojson["coordinates"]=pixel2coord(i,j)
                    collection.insert_one(geojson)
                    completion+=1
                    print(f'Completed at {completion/notNull:.4}%\r', end="")
        
