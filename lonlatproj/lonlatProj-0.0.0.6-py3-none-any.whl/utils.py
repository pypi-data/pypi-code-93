# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 11:06:39 2021

@author: cjcho
"""
import pyproj
import pandas as pd
import numpy as np

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
    return df_