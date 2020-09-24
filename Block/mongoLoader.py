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
from osgeo import gdal, ogr
import rasterio
import rasterio.features
import rasterio.warp
import time


client=MongoClient()
croppedRaster=glob.glob('/media/HD/blockRaster/*')

fileName='/media/HD/blockRaster/beam_228_1200'

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
        startTime=time.time()
        for i in np.arange(rasterShape[0]):
            for j in np.arange(rasterShape[1]):
                if not np.isnan(im[i][j]):
                    geojson={"type":"Point","coordinates":[],"properties":{"value":None}}
                    geojson["coordinates"]=pixel2coord(i,j)
                    geojson["properties"]["value"]=float(im[i][j])
                    collection.insert_one(geojson)
                    completion+=1
                    print(f'Completed at {completion*100/notNull:.4} %% \r', end="")
        endTime=time.time()
        estLeft=((nOfRaster-i)*(endTime-startTime))/60
        print(f"Completed in {endTime-startTime} s. Estimated finish in {estLeft} minutes ({estLeft/60} h)")
    
    # with rasterio.open(fileName) as dataset:
    #     ds = gdal.Open(fileName)
    #     c, a, b, f, d, e = ds.GetGeoTransform()

    # # Read the dataset's valid data mask as a ndarray.
    #     mask = dataset.dataset_mask()
    #     w=dataset.width
    #     h=dataset.height
    #     for i in range(w):
    #         for j in range(h):
    #             [x,y]=pixel2coord(i,j)
    #             for val in dataset.sample([(x, y)]):
    #                 if not np.isnan(val) and val[0]!=0:
    #                     print(val)