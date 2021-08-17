# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 11:06:39 2021

@author: cjcho
"""
import pyproj
import pandas as pd
import numpy as np
from netCDF4 import Dataset as NetCDFFile
import os
from rpy2.robjects.packages import importr
import rpy2.robjects as ro
ro.r('install.packages(c("sp","gstat"))')

def gstat_idw(lon,lat,values,pred_lon,pred_lat):
    r_f=ro.r('''
        library(sp)
        library(gstat)
         f<-function(lon,lat,values,pred_lon,pred_lat){
             pred=data.frame(lon=pred_lon,lat=pred_lat)
             coordinates(pred)=~lon+lat
             df=data.frame(lon,lat,values)
             coordinates(df)=~lon+lat
    
         return(idw(values~1, df,pred)$var1.pred)
            }
         ''')
    return r_f(ro.FloatVector(lon),
               ro.FloatVector(lat),
               ro.FloatVector(values),
               ro.FloatVector(pred_lon),
               ro.FloatVector(pred_lat),
               )

def wgs84_to_tm(longitude, latitude):
    proj_lonlat = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs')
    proj_xy = pyproj.Proj('+proj=tmerc +lat_0=38 +lon_0=127.5 +k=0.9996 +x_0=1000000 +y_0=2000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs')
    return pyproj.transform( proj_lonlat, proj_xy, longitude, latitude )

def tm_to_wgs84(x, y):
    proj_lonlat = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs')
    proj_xy = pyproj.Proj('+proj=tmerc +lat_0=38 +lon_0=127.5 +k=0.9996 +x_0=1000000 +y_0=2000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs')
    return pyproj.transform( proj_xy, proj_lonlat, x, y )

def contiTimeForm(df,time_var_name,freq):
    df_=df.copy()
    df_=df_.set_index([time_var_name])
    dt_range=pd.date_range(min(df_.index),max(df_.index),freq=freq)
    na_date=set(dt_range)-set(df_.index)
    df_=pd.concat([df_,pd.DataFrame(columns=df_.columns,index=na_date)],axis=0)
    df_=df_.sort_index()
    df_=df_.reset_index().rename(columns={"index": "times"})
    return df_


def create_vars(df,R=6371000):
    """
    https://www.igismap.com/formula-to-find-bearing-or-heading-angle-between-two-points-latitude-longitude/
    http://colaweb.gmu.edu/dev/clim301/lectures/wind/wind-uv
    """
    #create degrees
    df_=df.copy()
    df_[['p_lat','p_lon']]=df_[['Latitude','Longitude']].shift(1)
    df_[['lat_rad','lon_rad','p_lat_rad','p_lon_rad']]=df_[['Latitude', 'Longitude','p_lat','p_lon']]*np.pi/180
    del_lon=df_['lon_rad']-df_['p_lon_rad']
    
    x=np.cos(df_['lat_rad'])*np.sin(del_lon)
    y=np.cos(df_['p_lat_rad'])*np.sin(df_['lat_rad'])-np.sin(df_['p_lat_rad'])*np.cos(df_['lat_rad'])*np.cos(del_lon)
    df_['degrees']=np.where(np.arctan(x/y)*180/np.pi>=0,np.arctan(x/y)*180/np.pi,360+np.arctan(x/y)*180/np.pi)
    
    #create distance
    df_['x'],df_['y']=wgs84_to_tm(df_['Longitude'].values,df_['Latitude'].values)
    df_[['p_x','p_y']]=df_[['x','y']].shift(periods=1)
    df_['dist']=np.sqrt(((df_['x']-df_['p_x'])**2)+((df_['y']-df_['p_y'])**2))
    df_['U_dist']=df_['dist']*np.cos(df_['degrees']*np.pi/180)
    df_['V_dist']=df_['dist']*np.sin(df_['degrees']*np.pi/180)
    df_[['p_U_dist','p_V_dist']]=df_[['U_dist','V_dist']].shift(periods=1)
    return df_


def read_ecmwf(ecmwf_dir):
    ecmwf_files = [i for i in os.listdir(ecmwf_dir) if i.endswith('nc')]
    ecmwf_files.sort()
    dates=list();wus=list();wvs=list()
    for fi,fn in enumerate(ecmwf_files):
        cnt_file = f'{ecmwf_dir}/{fn}'
        enc=NetCDFFile(cnt_file)
        if fi==0:
            for i in enc.variables:
                print(enc.variables[i])
            longitude=enc.variables['longitude'][:]
            latitude=enc.variables['latitude'][:]
        date=enc.variables['time'][:].data
        wu=enc.variables['u10'][:].data
        wv=enc.variables['v10'][:].data
        if len(wv.shape)==4:
            dates.append(date)
            wus.append(
                np.concatenate(
                    (wu[:2160,0,:,:],
                     wu[2160:,1,:,:])))
            wvs.append(
                np.concatenate(
                    (wv[:2160,0,:,:],
                     wv[2160:,1,:,:])))
        else:
            dates.append(date)
            wus.append(wu)
            wvs.append(wv)
        enc.close()
        
    dt_ecmwf=[pd.to_datetime('1900-01-01')+\
              pd.to_timedelta(int(h+9),unit='h') for h in np.concatenate(dates)]
    dt_ecmwf=np.array(dt_ecmwf).flatten()
    wv=np.concatenate(wvs)
    wu=np.concatenate(wus)
    return longitude,latitude,dt_ecmwf,wu,wv


def export_date(date,wu,wv,longitude,latitude,dt_ecmwf):
    idx=np.where(dt_ecmwf==date)
    return pd.DataFrame({'wu':wu[idx,:,:].flatten(),
                         'wv':wv[idx,:,:].flatten(),
                        'lon':np.array(longitude.tolist()*len(latitude)),
                        'lat':np.array([np.repeat(i,len(longitude))
                                         for i in latitude]).flatten()}
                       )
