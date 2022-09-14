#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 10:15:50 2022

@author: amy
"""

# initialize by seeing if everything is in the correct directory structure and if a .run file
# exists


 
def initialize_bEPIC_event(postgres_id):
    from bEPIC import data_util
    import os
    import shutil
    
    bepic=os.environ['BEPIC']
    if type(postgres_id) != str:
        postgres_id = str(postgres_id).zfill(6)
        
        
    # look to see if directory does in fact exist
    if os.path.exists(bepic+'/event_logs/'+postgres_id)==False:
        print('directory does note exists')
        
    else:
        # if it does exist, check and add the right subfolders
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/EPIC/')==False:
            print(' ... making an EPIC output directory')
            os.mkdir(bepic+'/event_logs/'+postgres_id+'/EPIC/')
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/plots/')==False:
            print(' ... making a plots output directory')
            os.mkdir(bepic+'/event_logs/'+postgres_id+'/plots/')
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/bEPIC/')==False:
            print(' ... making a bEPIC output directory')
            os.mkdir(bepic+'/event_logs/'+postgres_id+'/bEPIC/')
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/USGS/')==False:
            print(' ... making a USGS output directory')
            os.mkdir(bepic+'/event_logs/'+postgres_id+'/USGS/')
            
        # move files to approriate folders
        location_log_file          = postgres_id+'_epic_location_log.txt'
        event_summary_log_file     = postgres_id+'_event_summary_log.txt'
        station_summary_log_file   = postgres_id+'_station_summary_log.txt'
        station_counts_log_file    = postgres_id+'_station_counts_log.txt'
        event_triggers_log_file    = postgres_id+'_event_triggers_log.txt'
        location_triggers_log_file = postgres_id+'_location_triggers_log.txt'
        misc_log_file              = postgres_id+'_misc_log.txt'
        
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/'+location_log_file)==True:
            shutil.move(bepic+'/event_logs/'+postgres_id+'/'+location_log_file, 
                        bepic+'/event_logs/'+postgres_id+'/EPIC/'+location_log_file)
            
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/'+event_summary_log_file)==True:
            shutil.move(bepic+'/event_logs/'+postgres_id+'/'+event_summary_log_file, 
                        bepic+'/event_logs/'+postgres_id+'/EPIC/'+event_summary_log_file)
        
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/'+station_summary_log_file)==True:
            shutil.move(bepic+'/event_logs/'+postgres_id+'/'+station_summary_log_file, 
                        bepic+'/event_logs/'+postgres_id+'/EPIC/'+station_summary_log_file)
        
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/'+station_counts_log_file)==True:
            shutil.move(bepic+'/event_logs/'+postgres_id+'/'+station_counts_log_file, 
                        bepic+'/event_logs/'+postgres_id+'/EPIC/'+station_counts_log_file)
        
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/'+event_triggers_log_file)==True:
            shutil.move(bepic+'/event_logs/'+postgres_id+'/'+event_triggers_log_file, 
                        bepic+'/event_logs/'+postgres_id+'/EPIC/'+event_triggers_log_file)
            
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/'+location_triggers_log_file)==True:
            shutil.move(bepic+'/event_logs/'+postgres_id+'/'+location_triggers_log_file, 
                        bepic+'/event_logs/'+postgres_id+'/EPIC/'+location_triggers_log_file)
        
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/'+misc_log_file)==True:
            shutil.move(bepic+'/event_logs/'+postgres_id+'/'+misc_log_file, 
                        bepic+'/event_logs/'+postgres_id+'/EPIC/'+misc_log_file)
        
        #  generate a .run file if none exists
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/'+postgres_id+'.run')==False:
            print(' ... event needs a .run file')
            print(' ... creating a .run file for event id '+postgres_id)
            data_util.generate_run_file(postgres_id)
        
        # if the USGS folder does not have an event log, attempt to find one
        if os.path.exists(bepic+'/event_logs/'+postgres_id+'/USGS/'+'usgs_event_summary.txt')==False:
            print(' ... no USGS event found ... attempting to find one')
            data_util.search_for_USGS_event(postgres_id)



def run_bEPIC(postgres_id,velocity_model,GridSize,GridSpacing):
        
    #----------------------------------------------------------------------------#    
    from bEPIC import locate,likelihood,magnitude,prior,posterior
    import pandas as pd
    import numpy as np
    import os
    
    bepic=os.environ['BEPIC']
    if type(postgres_id) != str:
        postgres_id = str(postgres_id).zfill(6)
          
    run_df = pd.read_csv(bepic+'/event_logs/'+postgres_id+'/'+postgres_id+'.run')   # read the .run file
    run_df['sigma']=np.ones(len(run_df))
    #-----------------------------------------------------------------#
    version = 0
    
    while version <= np.max(np.unique(run_df['version'])  ):
        print('postgres id: ',postgres_id,'| version: ',version,'|')
        
        relocate = True
        #------- get the stations that were active at this step
        idx    =   np.where(  (run_df['version']==version) & 
                              (run_df['tterr'] > -999)   )[0]  
        sta_df =   run_df.iloc[idx].reset_index(drop=True)
            
            
        if version==0:   
            CenterPoint= locate.get_two_station_location(sta_df) 
            
            columns = ['version','num stations','likelihood lon','likelihood lat',
                       'likelihood mag','prior lon','prior lat','posterior lon','posterior lat','posterior mag']
            bEPIC_df = pd.DataFrame(columns = columns)
        else:
            CenterPoint = [bEPIC_df['posterior lon'].iloc[-1],bEPIC_df['posterior lat'].iloc[-1]]
            
            if len(sta_df) == bEPIC_df['num stations'].iloc[-1]:
                relocate = False
        
        if relocate==True:
            #------------------------------------------------------------------------#
            # likelihood function
            (likelihood_function,misfit,
             likelihood_lon,likelihood_lat) = likelihood.calculate_likelihood(CenterPoint,sta_df,velocity_model,GridSize,GridSpacing)
            
            #------------------------------------------------------------------------#    
            # prior seismicity
            prior_function,prior_lon,prior_lat = prior.compute_prior(CenterPoint,GridSize,GridSpacing,ANSS_timestamp=None)         
    
            #------------------------------------------------------------------------#
            # posterior 
            post,posterior_lon,posterior_lat = posterior.compute_posterior(CenterPoint,GridSize,GridSpacing,prior_function,likelihood_function)
     
            #------------------------------------------------------------------------#
        
        else:
            likelihood_lon =  bEPIC_df['likelihood lon'].iloc[-1]
            likelihood_lat =  bEPIC_df['likelihood lat'].iloc[-1]
            
            posterior_lon = bEPIC_df['posterior lon'].iloc[-1]
            posterior_lat = bEPIC_df['posterior lat'].iloc[-1]
        
        
        likelihood_mag  =  magnitude.compute_magnitude(run_df,version,[likelihood_lon,likelihood_lat])
        posterior_mag   =  magnitude.compute_magnitude(run_df,version,[posterior_lon,posterior_lat])
        
        #------------------------------------------------------------------------#
        # write to dataframe
        bEPIC_df.loc[len(bEPIC_df.index)] = [version, int(len(sta_df)),
                                             likelihood_lon,likelihood_lat,likelihood_mag, 
                                             prior_lon, prior_lat,
                                             posterior_lon,posterior_lat,posterior_mag]
        #------------------------------------------------------------------------#
        version += 1
    
    bEPIC_df.to_csv(bepic+'/event_logs/'+postgres_id+'/bEPIC/'+postgres_id+'_bEPIC_log.txt',sep='\t',index=False)


