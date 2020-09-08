import gdal
import numpy as np
from rasterstats import *
import pandas as pd
import dec
import time
from rasterstats import zonal_stats
import geopandas as gpd
from affine import Affine


def main():
    start_time = time.time()
    latitude = 45.0619883  # latitude  N
    longitude = 7.6602814  # longitude E
    elevation = 250  # meters above the sea

    df = pd.read_csv('/home/bottaccioli/per_sara/2013.csv', sep=";", index_col='Date Time', decimal=',')
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize('Europe/Rome',ambiguous='infer')

    models = ['Karatasou']
    #models = ['Engerer2','Skartevit2','Skartevit1','Erbs','Reindl']
    #models=['Karatasou','Ruiz','Skartevit1','Engerer2','Erbs','Reindl']
    for model in models:
        print(model)
        i=0
        df=dec.main(latitude,longitude,elevation,model,df)
        geodf = gpd.read_file("/home/bottaccioli/per_sara/primo/primo.shp",crs='4326')
        geodf=geodf.set_index(['FID'])
        radiation = geodf.copy()
        rad=geodf.copy()
        radiation=radiation.drop(['geometry'],axis=1)
        month={1:'17',2:'47',3:'75',4:'105',5:'135',6:'162',7:'198',8:'228',9:'258',10:'288',11:'318',12:'344'}
        hour={4:'04',5:'05',6:'06',7:'07',8:'08',9:'09',10:'10',11:'11',12:'12',13:'13',14:'14',15:'15',16:'16',17:'17',18:'18',19:'19',20:'20',21:'21',22:'22'}
        minute={0:'00',15:'25',30:'50',45:'75'}
        Linke={1:3.5,2:4.3,3:4,4:4.2,5:4.6,6:4.6,7:4.4,8:4.5,9:4.3,10:4,11:4.4,12:4.4}
        directory='/home/bottaccioli/raster_crocetta/' 
       
        for dfix in df.index:
            i=i+1
            print model, str(i)+"of"+str(len(df))
            
            if df.ix[dfix]['zenith']<85:
                index=dfix
                if index.dst().seconds!=0:
                    if dfix < pd.to_datetime('27/03/2013').tz_localize('Europe/Rome'):
                        index=dfix-pd.DateOffset(hours=1.25)
                    else:
                        index=dfix-pd.DateOffset(hours=1.00)
                    beam=directory+'beam_'+month[index.month]+'_'+hour[index.hour]+'.'+minute[index.minute]
                    diff=directory+ 'diff_'+month[index.month]+'_'+hour[index.hour]+'.'+minute[index.minute]
                    glob , gt = glob_real(beam,diff,df.ix[index,'k_b'],df.ix[index,'k_d'])
                    stats=point_value(geodf,glob,gt)
                    radiation[index]=stats.values()
                else:
                    beam=directory+'beam_'+month[index.month]+'_'+hour[index.hour]+'.'+minute[index.minute]
                    diff=directory+ 'diff_'+month[index.month]+'_'+hour[index.hour]+'.'+minute[index.minute]
                    glob , gt = glob_real(beam,diff,df.ix[index,'k_b'],df.ix[index,'k_d'])
                    stats=point_value(geodf,glob,gt)
                    if dfix < pd.to_datetime('27/03/2013').tz_localize('Europe/Rome'):
                        radiation[index-pd.DateOffset(hours=0.25)]=stats.values()
                    else:
                        print 'fava'
                        radiation[index]=stats.values()

                glob=None
        radiation=radiation.transpose()
        print("--- %s seconds ---" % (time.time() - start_time))
        radiation=radiation.join(df['T_ex'])
        radiation.to_csv('primo_rad.csv')    
        #return radiation

def point_value(geodf,rast,gt):
    res={}
    for ind in geodf.index:
        res[ind]=query(geodf.ix[ind,'x'],geodf.ix[ind,'y'],rast,gt)
    return res

def query(x,y,rast,gt):
    px = int(round((x - gt[0]) / gt[1]))
    py = int(round((y - gt[3]) / gt[5]))
    return rast[px,py]
    
def glob_real(sbeam,sdiff,kb,kd):
    b1=gdal.Open(sbeam)
    beam= np.array(b1.GetRasterBand(1).ReadAsArray())
    d1 =gdal.Open(sdiff)
    diff=np.array(d1.GetRasterBand(1).ReadAsArray())
    g1 = beam*kb+diff*kd
    # Get raster georeference info
    gt = b1.GetGeoTransform()
    b1=None
    d1=None
    return g1 ,gt


if __name__ == "__main__":
    import sys
    main()
