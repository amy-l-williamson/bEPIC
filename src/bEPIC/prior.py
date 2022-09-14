#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 14:02:35 2022

@author: amy
"""


def generate_prior_seismicity_catalog():
    from libcomcat.search import search
    from datetime import datetime
    import pandas as pd
    import os
    
    bepic=os.environ['BEPIC']
    region = [-135, -112, 30, 50]
    earthquake = search(starttime=datetime(2000, 1, 1, 0, 0), endtime=datetime.now(),minlatitude=region[2], 
                        maxlatitude=region[3], minlongitude=region[0], maxlongitude=region[1],
                        minmagnitude=3)
    
    columns=['ANSS ID','date','timestamp','lon','lat','depth','mag']
    df = pd.DataFrame(columns=columns)
    for eq in earthquake:
        df.loc[len(df.index)] = [eq.id,str(eq.time),eq.time.timestamp(),eq.longitude,eq.latitude,eq.depth,eq.magnitude]
    

    df.to_csv(bepic+'/data/prior_seismicity_catalog.txt',sep='\t',index=False) 
    
    
   

def compute_prior(CenterPoint,GridSize,GridSpacing,ANSS_timestamp=None):
    from scipy.stats import kde
    import pandas as pd
    import numpy as np
    from bEPIC import geospatial_util
    import os
    from datetime import datetime
    bepic=os.environ['BEPIC']
    
    
    
    if os.path.exists(bepic+'/data/prior_seismicity_catalog.txt')==False:
        print('cannot find catalog... building a new one....')
        generate_prior_seismicity_catalog()
        
        
        
        
    (grid_lons,grid_lats,_,_,
     _,_) = geospatial_util.make_grid(CenterPoint,GridSize,GridSpacing)
    
    
    
    
    prior_df = pd.read_csv(bepic+'/data/prior_seismicity_catalog.txt',sep='\t')
    
    
    
    if ANSS_timestamp==None:
        ANSS_timestamp = datetime.now().timestamp()
        
        
    mag_floor=3
    #-------- get all seismicity that occured in grid search area
    #         and before the earthquake (for replay events)
    lon = np.array(prior_df['lon'])
    lat = np.array(prior_df['lat'])
    mag = np.array(prior_df['mag'])
    t   = np.array(prior_df['timestamp'])
    idx = np.where( (lon <= np.max(grid_lons))  
                   & (lon >= np.min(grid_lons)) 
                   & (lat <= np.max(grid_lats))  
                   & (lat >= np.min(grid_lats))
                   & (mag >= mag_floor)
                   & (t < ANSS_timestamp))[0]
    
    
    
    
    lon = lon[idx]
    lat = lat[idx]
    t   = t[idx]
    
    
    # convert everything to cartesian
    xx,yy =  geospatial_util.LL2cartd(lon,lat,grid_lons[0],grid_lats[0],0)            # past seismicity
    x,y   =  geospatial_util.LL2cartd(grid_lons,grid_lats,grid_lons[0],grid_lats[0],0) # grid nodes

    xx=xx/1000  # to kilometers
    yy=yy/1000  #
    x=x/1000    #
    y=y/1000    #
    
    
    # run the KDE function
    k = kde.gaussian_kde(np.vstack((xx,yy)),bw_method='scott')
   
    
    spread = np.max(k._data_covariance)
    k._data_covariance = np.identity(2) * spread
    k._data_inv_cov = np.linalg.inv(k._data_covariance)
    k.covariance = k._data_covariance * k.factor**2  # THIS 


    k.inv_cov = k._data_inv_cov / k.factor**2
    
    
    xi, yi = np.mgrid[np.min(x):np.max(x):(len(x))*1j, np.min(y):np.max(y):len(y)*1j]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))
    prior_seis = (zi.reshape(xi.shape).T)
    
    best_location_prior = np.where(prior_seis == np.max(prior_seis))
    prior_lon  =   grid_lons[best_location_prior[1][0]]
    prior_lat  =   grid_lats[best_location_prior[0][0]]
    
    return(prior_seis,prior_lon,prior_lat)
