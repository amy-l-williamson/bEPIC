#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 13:34:37 2022

@author: amy
"""
import numpy as np
from bEPIC import geospatial_util,data_util
  



def calculate_likelihood(CenterPoint,sta_df,velocity_model,GridSize=200,GridSpacing=2):
    
    
    (grid_lons,grid_lats,grid_x,grid_y,
     grid_x_ravel,grid_y_ravel) = geospatial_util.make_grid(CenterPoint,GridSize,GridSpacing)


    
    sigma=1
    eq_depth = 8.0  # km
    
    n = len(sta_df['longitude'])        # number of active stations
    p = len(grid_x)                    # number of grid nodes in x (or y) direction
    m = len(grid_x_ravel)              # total number of grid nodes  (p*p)
    
    
    
    
    stax,stay =  geospatial_util.LL2cartd(np.array(sta_df['longitude']),
                               np.array(sta_df['latitude']),
                               CenterPoint[0],CenterPoint[1],0) # convert station locations to cart. ref. frame

    # find distance between each grid node and each station
    # this is an (m x n) sized matrix
    station_distance = np.sqrt(  np.square(np.subtract(np.tile(grid_x_ravel,(n,1)).T, np.tile(stax/1000,(m,1)) )) 
                               + np.square(np.subtract(np.tile(grid_y_ravel,(n,1)).T, np.tile(stay/1000,(m,1)) ))
                               + eq_depth**2)  # distance in km
    
    
    # find the P-wave travel time from each grid node and each station
    # this is an (m x n) sized matrix
    if velocity_model =='h2p+ak135':  
        ttf = data_util.travel_time_function(velocity_model)
        travel_time = ttf(np.ravel(station_distance)).reshape(m,n)
    elif velocity_model == 'constant':
        travel_time = station_distance / 6.0
        
    # the average of all the station P-wave travel times at each grid node
    # this is a vector of length m
    average_OT   = np.mean( np.subtract(np.tile(sta_df['trigger time'],(m,1)) , travel_time),axis=1) 
    
    
    # the (forward) modeled trigger time for each station from each grid node
    # this is an (m x n) sized matrix
    trigger_time_calc = np.add(np.tile(average_OT ,(n,1)).T,travel_time )
    
   
    # the misfit between the observed and forward modeled travel times
    # misfit = |modeled - observed|^2 
    # this is an (m x n) sized matrix
    tt_error = np.abs(np.subtract(trigger_time_calc,np.tile(sta_df['trigger time'],(m,1))))**2

    
    misfit =  np.sum(tt_error,axis=1).reshape(p,p)
    # get the likelihood (L(m|d)) L for the model m given the observation of the data d
    
    # first get the likelhood per each station
    # this is an (m x n) sized matrix
    rho = np.exp(-0.5*(tt_error/(sta_df['sigma'].values**2)))
    
    # then get the combined likelihood
    #  this is a (p x p) sized matrix
    like=np.prod(rho,axis=1).reshape(p,p)
    
    
    best_location  =  np.where(like == np.max(like))
    likelihood_lon =  grid_lons[best_location[1][0]]
    likelihood_lat =  grid_lats[best_location[0][0]]  
    
    return(like,misfit,likelihood_lon,likelihood_lat)

