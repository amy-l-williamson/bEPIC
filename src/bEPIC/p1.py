#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 12:04:01 2022

@author: amy
"""

import sys
import os
import shutil
import gzip
import urllib.request




import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd

def parse_log(log_file,event_log_dir,event_id,epic_id):
    print('paring event long for epic event id '+epic_id)
    ee=0
    #-----------------------------------------------------------------------------#
    file1 = open(log_file, 'r')
    Lines = file1.readlines()

    #------------------------------------------------------------------------------------------------------------------#
    columns = ['eventid','version','event lat','event lon','depth','mag','time','latu','lonu','depu',
               'magu','timeu','lk','nTb','nSb','nT','nS','ave','rms','fitOK','splitOK','near',
               'statrig','active','inact','nsta','percent','prcntOK','mindist','maxdist','distOK',
               'azspan','MOK','nSOK','LOK','Tdif','tpave','pdave','TF','TOK','AZOK','AOK','Ast','alert_time']
    event_summary_df = pd.DataFrame(columns=columns)

    #------------------------------------------------------------------------------------------------------------------#
    columns = ['eventid','version','update','order','sta','chan','net','loc','lat','lon','trigger time','rsmp','tsmp',
               'log taup','taup snr','dsmp','log pd','pd snr','assoc','tpmag','utpm','pdmag','updm','uch','ukm','upd',
               'ups','utp','uts','tel','tsec','distkm','azimuth','TF','tterr','azerror','incid','plen','sps']
    event_triggers_df = pd.DataFrame(columns=columns)


    #------------------------------------------------------------------------------------------------------------------#
    columns = ['eventid','version','nT','index','sta','chan','net','loc','lat','lon','U','dist','tt','tterr']
    location_triggers_df = pd.DataFrame(columns=columns)

    #------------------------------------------------------------------------------------------------------------------#
    columns = ['eventid','version','event lat','event lon','time','mindist','maxdist','percent','near sta cnt','sta trig cnt',
               'active','inactive','nsta']
    station_summary_df = pd.DataFrame(columns=columns)


    #------------------------------------------------------------------------------------------------------------------#
    columns = ['eventid','version','event lat','event lon','depth','sta','chan','net','loc','lat','lon','date','tt',
               'dist','ttok','dok','nttok','ndok','ttmin','ttmax','relo','nlat','nlon','ndep','ntime','nrms','nave',
               'fitok','dmin','mdok','percent','pok']
    a_df = pd.DataFrame(columns=columns)
    #------------------------------------------------------------------------------------------------------------------#
    columns=['eventid','version','sta','net','lat','lon','cluster','dist','tt','time','time check','active',
             'trig','clu','ctrig']
    station_counts_df = pd.DataFrame(columns=columns)

    #------------------------------------------------------------------------------------------------------------------#
    columns = ['eventid','version','s','lat0','lon0','dep0','time0','lat','lon','depth','time','ddist','avefit','rmsfit','nT','nS']
    epic_location_df = pd.DataFrame(columns =columns)


    for k in range(len(Lines)):
        l0 = list(filter(None, Lines[k].split('|')))[-1]
        l = list(filter(None, l0.split(' ')))
        #------------------------------------------------------------------------------------------------------------------------------------#
        if ('E:I:' in l) or ('E:I:F:' in l):
            # THIS IS THE EVENT INFORMATION
            if l[1]==epic_id:
                #print(l)
                ee=1
                
                
                event_summary_df.loc[len(event_summary_df)] =[int(l[1]),int(l[2]),
                                                            float(l[3]),float(l[4]),
                                                            float(l[5]) ,float(l[6]),l[7],
                                                            'latu':float(l[8]),'lonu':float(l[9]),'depu':float(l[10]),
                                                            'magu':float(l[11]),'timeu':float(l[12]),'lk':float(l[13]),
                                                            'nTb':int(l[14]),'nSb':int(l[15]),'nT':int(l[16]),'nS':int(l[17]),
                                                            'ave':float(l[18]) ,'rms':float(l[19]),'fitOK':int(l[20]),
                                                            'splitOK':int(l[21]),'near':int(l[22]),
                                                            'statrig':int(l[23]),'active':int(l[24]),
                                                            'inact':int(l[25]),'nsta':int(l[26]),'percent':float(l[27]),
                                                            'prcntOK':int(l[28]),'mindist':float(l[29]),'maxdist':float(l[30]),
                                                            'distOK':int(l[31]),'azspan':float(l[32]),'MOK':int(l[33]),
                                                            'nSOK':int(l[34]),'LOK':int(l[35]),'Tdif':float(l[36]),
                                                            'tpave':float(l[37]),'pdave':float(l[38]),'TF':float(l[39]),
                                                            'TOK':int(l[40]),'AZOK':int(l[41]),'AOK':int(l[42]),
                                                            'Ast':l[43],'alert_time':l[44].split('\n')[0]]
                
                
                event_summary_df = event_summary_df.append({'eventid': int(l[1]),'version':int(l[2]),
                                                            'event lat':float(l[3]),'event lon':float(l[4]),
                                                            'depth':float(l[5]) ,'mag':float(l[6]),'time':l[7],
                                                            'latu':float(l[8]),'lonu':float(l[9]),'depu':float(l[10]),
                                                            'magu':float(l[11]),'timeu':float(l[12]),'lk':float(l[13]),
                                                            'nTb':int(l[14]),'nSb':int(l[15]),'nT':int(l[16]),'nS':int(l[17]),
                                                            'ave':float(l[18]) ,'rms':float(l[19]),'fitOK':int(l[20]),
                                                            'splitOK':int(l[21]),'near':int(l[22]),
                                                            'statrig':int(l[23]),'active':int(l[24]),
                                                            'inact':int(l[25]),'nsta':int(l[26]),'percent':float(l[27]),
                                                            'prcntOK':int(l[28]),'mindist':float(l[29]),'maxdist':float(l[30]),
                                                            'distOK':int(l[31]),'azspan':float(l[32]),'MOK':int(l[33]),
                                                            'nSOK':int(l[34]),'LOK':int(l[35]),'Tdif':float(l[36]),
                                                            'tpave':float(l[37]),'pdave':float(l[38]),'TF':float(l[39]),
                                                            'TOK':int(l[40]),'AZOK':int(l[41]),'AOK':int(l[42]),
                                                            'Ast':l[43],'alert_time':l[44].split('\n')[0]}, ignore_index=True)
        #------------------------------------------------------------------------------------------------------------------------------------#
        #------------------------------------------------------------------------------------------------------------------------------------#
        if ('E:I:T:' in l):
            #--------------------- EVENT INFO TRIGGER ------------------------#
            if l[1]==epic_id:
                event_triggers_df = event_triggers_df.append({'eventid': l[1],'version':int(l[2]),'update':int(l[3]),'order':int(l[4]),
                                                            'sta':l[5],'chan':l[6],'net':l[7],'loc':l[8],'lat':float(l[9]),'lon':float(l[10]),
                                                            'trigger time':l[11], 'rsmp':int(l[12]),'tsmp':int(l[13]),'log taup':float(l[14]),
                                                            'taup snr':float(l[15]),'dsmp':int(l[16]),'log pd':float(l[17]),'pd snr':float(l[18]),
                                                            'assoc':l[19] ,'tpmag':float(l[20]),'utpm':int(l[21]),'pdmag':float(l[22]),
                                                            'updm':int(l[23]),'uch':int(l[24]),'ukm':int(l[25]),
                                                            'upd':int(l[26]),'ups':int(l[27]),'utp':int(l[28]),'uts':int(l[29]),'tel':int(l[30]),
                                                            'tsec':float(l[31]),'distkm':float(l[32]) ,'azimuth':float(l[33]) ,'TF':int(l[34]),
                                                            'tterr':float(l[35]),'azerror':float(l[36]) ,'incid':float(l[37]),
                                                            'plen':int(l[38]),'sps':float(l[39])}, ignore_index=True)
        #------------------------------------------------------------------------------------------------------------------------------------#
        if 'L:T:' in l:
            # THIS IS A LOCATION TRIGGER LINE
            if l[1]==epic_id:
                location_triggers_df =location_triggers_df.append({'eventid': l[1],'version':int(l[2]),
                                                                   'nT':int(l[3]),'index':int(l[4]),
                                                                   'sta':l[5],'chan':l[6],'net':l[7],'loc':l[8],'lat':float(l[9]),
                                                                   'lon':float(l[10]),'U':int(l[11]),'dist':float(l[12]),
                                                                   'tt':float(l[13]),'tterr':float(l[14])},ignore_index=True)
        #------------------------------------------------------------------------------------------------------------------------------------#    
        if 'E:S:' in l:
            #STATION COUNT SUMMARY
            if l[1]==epic_id:
                station_summary_df = station_summary_df.append({'eventid': l[1],'version':int(l[2]),
                                                                'event lat':float(l[3]),'event lon':float(l[4]),
                                                                'time':l[5],'mindist':float(l[6]),
                                                                'maxdist':float(l[7]),'percent':float(l[8]),
                                                                'near sta cnt':int(l[9]),'sta trig cnt':int(l[10]),
                                                                'active':int(l[11]),'inactive':int(l[12]),'nsta':int(l[13])},ignore_index=True)
        #------------------------------------------------------------------------------------------------------------------------------------#    
        if "A:" in l:
            if l[1]==epic_id:

                a_df = a_df.append({'eventid': l[1],'version':int(l[2]),'event lat':float(l[3]),'event lon':float(l[4]),
                                    'depth':float(l[5]),'sta':l[6],'chan':l[7],'net':l[8],'loc':l[9],
                                    'lat':float(l[10]),'lon':float(l[11]),'date':l[12],
                                    'tt':float(l[13]),'dist':float(l[14]),'ttok':int(l[15]),
                                    'dok':int(l[16]),'nttok':int(l[17]),'ndok':int(l[18]),'ttmin':float(l[19]),'ttmax':float(l[20]),
                                    'relo':int(l[21]),'nlat':float(l[22]),'nlon':float(l[23]),
                                    'ndep':float(l[24]),'ntime':l[25],'nrms':float(l[26]),'nave':float(l[27]),
                                    'fitok':int(l[28]),'dmin':float(l[29]),'mdok':int(l[30]),'percent':float(l[31]),'pok':int(l[32])},ignore_index=True)
        #------------------------------------------------------------------------------------------------------------------------------------#    
        if 'E:C:' in l:
            #STATION COUNT DETAILS 
            if l[1]==epic_id:
                station_counts_df =station_counts_df.append({'eventid': l[1],'version':int(l[2]),
                                                             'sta':l[3],'net':l[4],'lat':float(l[5]),'lon':float(l[6]),
                                                             'cluster':l[7],'dist':float(l[8]),'tt':float(l[9]),'time':l[10],
                                                             'time check':float(l[11]),'active':int(l[12]),
                                                             'trig':int(l[13]),'clu':int(l[14]),'ctrig':int(l[15])},ignore_index=True)
        #------------------------------------------------------------------------------------------------------------------------------------#    
        if 'L:E:' in l:
            # THIS IS A LOCATION ALGORITHM LINE
            if l[1]==epic_id:
                epic_location_df = epic_location_df.append({'eventid': l[1],'version':int(l[2]),
                                                            's':int(l[3]),'lat0':float(l[4]),'lon0':float(l[5]),
                                                            'dep0':float(l[6]),'time0':l[7],'lat':float(l[8]),'lon':float(l[9]),
                                                            'depth':float(l[10]),'time':l[11],'ddist':float(l[12]),'avefit':float(l[13]),
                                                            'rmsfit':float(l[14]),'nT':int(l[15]),'nS':int(l[16])},ignore_index=True)
        #------------------------------------------------------------------------------------------------------------------------------------#    



    # need to save the dataframes
    if ee ==1:
        if os.path.exists(event_log_dir+event_id+'/')==False:
            os.mkdir(event_log_dir+event_id+'/')
        event_summary_df.to_csv(event_log_dir+event_id+'/'+event_id+'_event_summary_log.txt',sep='\t',index=False)
        event_triggers_df.to_csv(event_log_dir+event_id+'/'+event_id+'_event_triggers_log.txt',sep='\t',index=False)
        location_triggers_df.to_csv(event_log_dir+event_id+'/'+event_id+'_location_triggers_log.txt',sep='\t',index=False)
        station_summary_df.to_csv(event_log_dir+event_id+'/'+event_id+'_station_summary_log.txt',sep='\t',index=False)
        a_df.to_csv(event_log_dir+event_id+'/'+event_id+'_misc_log.txt',sep='\t',index=False)
        station_counts_df.to_csv(event_log_dir+event_id+'/'+event_id+'_station_counts_log.txt',sep='\t',index=False)
        epic_location_df.to_csv(event_log_dir+event_id+'/'+event_id+'_epic_location_log.txt',sep='\t',index=False)
        
        
        
###########################################################################################        
#-------------------------------------------------------------#
# VARIABLE 1 needs to be instance
# VARIABLE 2 needs to be day
# VARIABLE 2 needs to be postges_d

instance = sys.argv[1]
day = sys.argv[2]
postgres_id = sys.argv[3]
epic_id = sys.argv[4]

#-------------------------------------------------------------#
instance = instance.replace(" ", "").split('@')[-1]


event_log_dir='/home/gcl/RA/williamson/EPIC_processed_logs/'
log_location='/home/gcl/RA/williamson/EPIC_unprocessed_logs/'
log_file = log_location+instance+'_'+day+'.log'



event_id = str(postgres_id)


if os.path.exists(event_log_dir+event_id+'/'+event_id+'_event_summary_log.txt')==False:
    try:
        url='http://131.215.66.120/'+instance+'/epic/epic_'+day+'.log.gz'
        if os.path.exists(log_location+instance+'_'+day+'.log')==False:
            print(' ... downloading log file from EPIC archive')
            urllib.request.urlretrieve(url,log_location+instance+'_'+day+'.log.gz')
            with gzip.open(log_location+instance+'_'+day+'.log.gz', 'rb') as f_in:
                with open(log_location+instance+'_'+day+'.log', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            print(' ... log file '+instance+'_'+day+'.log alread exsists')
        try:
            print(' ... parsing log file ...')
            parse_log(log_file,event_log_dir,event_id,epic_id)
            #os.remove(log_file)
            os.remove(log_file+'.gz')
        except:
            a=1
    except:
        print(' ... erorr: file not found')

else:
    print(' ... event already has a local log file. exiting....')

