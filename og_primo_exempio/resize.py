import scipy.io as sio
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from functools import partial
from joblib import Parallel, delayed
from interval import Interval, IntervalSet
import time
import multiprocessing as mp

def main():
    df=pd.read_csv('primo_rad.csv')
    df=df.set_index(df.columns[0])
    df=df.transpose()
    print df.columns
    df=df.drop(['T_ex'])
    cords=df.as_matrix(columns=['x','y'])
    gt=[7.6445503225, 5.4065168747250134e-06,  0.0,  45.07436634583334,  0.0, -5.406516856707135e-06]

    index=np.zeros(cords.shape)
    index[:,1]=((cords[:,1] - gt[3]) / gt[5]).round()
    index[:,0]=((cords[:,0] - gt[0]) / gt[1]).round()

    
    index=index.astype(int)
    index[:,0]=index[:,0]-min(index[:,0])+1
    index[:,1]=index[:,1]-min(index[:,1])+1
    row=max(index[:,1])
    col=max(index[:,0])
    length=len(df.columns[3:])
    col1=col*55/20
    row1=row*55/20
    
    image=np.empty([row+1,col+1,length])
    image20=np.empty([row1,col1,length])
    image[:]=np.nan
    image20[:]=np.nan
    image=image.astype(np.float32)
    image20=image20.astype(np.float32)

    for z in xrange(length):
        image[index[:,1],index[:,0],z]=df[df.columns[z]].astype(np.float32)

    now=time.time()

    #parallel map returns a list
    pool=mp.Pool(processes=16)
    res=pool.map(meanInterp,(image[:,:,z] for z in xrange(0,image.shape[2])))
    pool.close()
    #copy the data to array
    for i in xrange(0,image.shape[2]):
        image20[:,:,i]=res[i]
        
        
    print time.time()-now,'s'
    save={'matrix':image}
    sio.savemat('primo_50',save)
    try:
        save={'matrix':image20}
        sio.savemat('primo_20',save)
        save={'matrix':image20[:length/2]}
        sio.savemat('primo_20_1',save)
        save={'matrix':image20[length/2:]}
        sio.savemat('primo_20_2',save)
    except:
        pass
    return image,image20

def overlap(rect1, rect2):
  """Calculate the overlap between two rectangles"""
  xInterval = Interval(rect1[0][0], rect1[1][0]) & Interval(rect2[0][0], rect2[1][0])
  yInterval = Interval(rect1[0][1], rect1[1][1]) & Interval(rect2[0][1], rect2[1][1])
  area = (xInterval.upper_bound - xInterval.lower_bound) * (yInterval.upper_bound - yInterval.lower_bound)
  return area


def meanInterp(data):
    m=126
    n=286
    newData = np.zeros((m,n))
    mOrig, nOrig = data.shape

    hBoundariesOrig, vBoundariesOrig = np.linspace(0,1,mOrig+1), np.linspace(0,1,nOrig+1)
    hBoundaries, vBoundaries = np.linspace(0,1,m+1), np.linspace(0,1,n+1)

    for iOrig in range(mOrig):
      for jOrig in range(nOrig):
        for i in range(m):
          if hBoundaries[i+1] <= hBoundariesOrig[iOrig]: continue
          if hBoundaries[i] >= hBoundariesOrig[iOrig+1]: break
          for j in range(n):
            if vBoundaries[j+1] <= vBoundariesOrig[jOrig]: continue
            if vBoundaries[j] >= vBoundariesOrig[jOrig+1]: break

            boxCoords = ((hBoundaries[i], vBoundaries[j]),(hBoundaries[i+1], vBoundaries[j+1]))
            origBoxCoords = ((hBoundariesOrig[iOrig], vBoundariesOrig[jOrig]),(hBoundariesOrig[iOrig+1], vBoundariesOrig[jOrig+1]))

            newData[i][j] += overlap(boxCoords, origBoxCoords) * data[iOrig][jOrig] / (hBoundaries[1] * vBoundaries[1])

    return newData
    
if __name__ == "__main__":
    import sys
    main()

