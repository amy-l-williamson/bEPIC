#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 11:18:41 2022

@author: amy
"""

       
def generate_run_file(postgres_id):
    import numpy as np
    import pandas as pd
    from datetime import datetime
    import os
    
    
    bepic=os.environ['BEPIC']


    station_trigger_log_file = bepic+'/event_logs/'+postgres_id+'/EPIC/'+postgres_id+'_event_triggers_log.txt'
    output_filename =  bepic+'/event_logs/'+postgres_id+'/'+postgres_id+'.run'
    
    
    #-----------------------------------------------------------------------------#
    v =  np.genfromtxt(station_trigger_log_file,usecols=[1],skip_header=1)
    o =  np.genfromtxt(station_trigger_log_file,usecols=[3],skip_header=1)

    station_sta   =  np.genfromtxt(station_trigger_log_file,usecols=[4], dtype='str',skip_header=1)
    station_chan  =  np.genfromtxt(station_trigger_log_file,usecols=[5], dtype='str',skip_header=1)
    station_net   =  np.genfromtxt(station_trigger_log_file,usecols=[6], dtype='str',skip_header=1)
    station_loc   =  np.genfromtxt(station_trigger_log_file,usecols=[7], dtype='str',skip_header=1)
    station_t_str =  np.genfromtxt(station_trigger_log_file,usecols=[10],dtype='str',skip_header=1)
    station_lon   =  np.genfromtxt(station_trigger_log_file,usecols=[9],skip_header=1)
    station_lat   =  np.genfromtxt(station_trigger_log_file,usecols=[8],skip_header=1)
    station_t_str =  np.genfromtxt(station_trigger_log_file,usecols=[10],dtype='str',skip_header=1)
    station_t     = []
    version       = []
    order         = []


    for i in range(len(station_t_str)):
        station_t = np.append(station_t,datetime.strptime(station_t_str[i], '%Y-%m-%dT%H:%M:%S.%f').timestamp())
        version   = np.append(version,int(v[i]))
        order     = np.append(order,int(o[i]))
    station_logpd = np.genfromtxt(station_trigger_log_file,usecols=[16],skip_header=1)
    station_tterr = np.genfromtxt(station_trigger_log_file,usecols=[34],skip_header=1)

    #--------------------------------------------------#
    df = pd.DataFrame({'version':version,
                       'order':order,
                       'station':station_sta,
                       'channel':station_chan,
                       'network':station_net,
                       'location':station_loc,
                       'longitude':station_lon,
                       'latitude':station_lat,
                       'trigger time':station_t,
                       'tterr':station_tterr,
                       'logPd':station_logpd})
    df = df.astype({'version':'int'})
    df = df.astype({'order':'int'})
    df.to_csv(output_filename,index=False)
    #--------------------------------------------------#    
    
def search_for_USGS_event(postgres_id):
    import pandas as pd        
    import numpy as np
    from datetime import datetime,timedelta
    from obspy.geodetics import gps2dist_azimuth
    from libcomcat.search import search
    import os
    
    
    bepic=os.environ['BEPIC']
    
    event_summary_df = pd.read_csv(bepic+'/event_logs/'+postgres_id+'/EPIC/'+postgres_id+'_event_summary_log.txt',sep='\t')
    EPIC_ot = datetime.strptime(event_summary_df['time'].iloc[-1], '%Y-%m-%dT%H:%M:%S.%f')
    dt=0
    dx=0
    found=False
    
    while found == False:
            # run the search
            km_radius_events = search(starttime=EPIC_ot-timedelta(seconds=dt), endtime=EPIC_ot+timedelta(seconds=dt),
                               maxradiuskm=dx, latitude=event_summary_df['event lat'].iloc[-1],
                               longitude=event_summary_df['event lon'].iloc[-1])
    
    
            if len(km_radius_events)==1:
    
                print('found event with dx: ',dx,' and dt: ',dt)
                USGS_event = km_radius_events[0]
                m,az1,az2 = gps2dist_azimuth(USGS_event.latitude, USGS_event.longitude, event_summary_df['event lat'].iloc[-1], event_summary_df['event lon'].iloc[-1])
                
                catalog_df = pd.DataFrame({'postgres id':postgres_id,'USGS ID':USGS_event.id,'USGS time':USGS_event.time.timestamp(),
                                                'USGS lat':USGS_event.latitude,'USGS lon':USGS_event.longitude,
                                                'USGS depth':USGS_event.depth,'USGS mag':USGS_event.magnitude},index=[0])   
                found = True
    
            elif len(km_radius_events)>1:
                # multiple events found
                dt=dt-1
                dx=dx-1
            else:
                dt=dt+5
                dx=dx+5
    
            if dx > 100:
                    print('this is getting out of hand, need a human to help')
    
                    found = True
                    catalog_df = pd.DataFrame({'postgres id':postgres_id,'USGS ID':np.nan,'USGS time':np.nan,
                                                    'USGS lat':np.nan,'USGS lon':np.nan,
                                                    'USGS depth':np.nan,'USGS mag':np.nan},index=[0])
    
    catalog_df.to_csv(bepic+'/event_logs/'+postgres_id+'/USGS/'+'usgs_event_summary.txt',sep='\t',index=False)



def travel_time_function(velocity_model):
    from scipy import interpolate
    import numpy as np
    import os
    
    
    bepic=os.environ['BEPIC']
    tt_file = bepic+'/data/h2p+ak135.080'
    
    tt_mod = np.genfromtxt(tt_file,skip_header=1)
    tt_mod_distance = tt_mod[:,0]
    tt_mod_time = tt_mod[:,1]
    ttf = interpolate.interp1d(tt_mod_distance, tt_mod_time)

    return(ttf)   






