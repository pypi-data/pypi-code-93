# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 10:55:47 2021

@author: tianxi
"""
# from urllib.request import urlopen, Request
import json
import os
from pathlib import Path
import api_knmi_xt
import requests
import sys
import logging
import re
import pandas as pd
import numpy as np
import pickle
# Initializatoin: set up loggers
logging.basicConfig(#filename='knmi.log',
                    #encoding='utf-8',
                    filemode='a',
                    # stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
# define child functions
def file_list(API_URL, DATASET_NAME, DATASET_VERSION, key):
    # get available list --> seems only able to show first 10
    req = requests.get(
        # f"{API_URL}/datasets/{DATASET_NAME}/versions/{DATASET_VERSION}/files?startAfterFilename=harm40_v1_p1_{date}{hour}.tar",
        f"{API_URL}/datasets/{DATASET_NAME}/versions/{DATASET_VERSION}/files",
        headers={"Authorization": key}
    )
    # with urlopen(req) as list_files_response:
    #     files = json.load(list_files_response).get("files")
    files = req.json()['files']
    return files

def get_file(filename, tmpdirname, key, API_URL, DATASET_NAME, DATASET_VERSION):
    # download files
    req = requests.get(
        f"{API_URL}/datasets/{DATASET_NAME}/versions/{DATASET_VERSION}/files/{filename}/url",
        headers={"Authorization": key}
    )
    
    download_url = req.json().get("temporaryDownloadUrl")
    dataset_file_response = requests.get(download_url)
        
    if dataset_file_response.status_code != 200:
        logging.error("Unable to download file using download URL")
        sys.exit(1)
        
    p = Path(tmpdirname, filename)
    p.write_bytes(dataset_file_response.content)
    
    
def find_2030_2050(file_names, DATASET_NAME):
    lst_select = [] # select where 2030 and 2050
    lst_name = []
    for i in range(len(file_names)):
        if '2030' in file_names[i]['filename']:
            lst_select.append(i)
            lst_name.append('M2030')
        elif 'GL_2050' in file_names[i]['filename']:
            lst_select.append(i)
            lst_name.append('GL2050')
        elif 'GH_2050' in file_names[i]['filename']:
            lst_select.append(i)
            lst_name.append('GH2050')
        elif 'WL_2050' in file_names[i]['filename']:
            lst_select.append(i)
            lst_name.append('WL2050')
        elif 'WH_2050' in file_names[i]['filename']:
            lst_select.append(i)
            lst_name.append('WH2050')
    if 'upper' in DATASET_NAME:
        lst_name = [name+'U' for name in lst_name]
    elif 'lower' in DATASET_NAME:
        lst_name = [name+'L' for name in lst_name]
    elif 'centr' in DATASET_NAME:
        lst_name = [name+'C' for name in lst_name]
    return dict(zip(lst_name, lst_select))
    
def find_latlon_knmi(case='Prec', show=True):
    if case == 'Prec':
        df_all = pd.read_csv(Path(r'knmi14', r'default_prec.txt'), header=None)   
        nr_nm = 7
        nr_lat = 10
        nr_lon = 11
        nr_strat = 5
    elif case == 'Evap':
        df_all = pd.read_csv(Path(r'knmi14', r'default_evap.txt'), header=None, error_bad_lines=False)   
        nr_nm = 8
        nr_lat = 11
        nr_lon = 12
        nr_strat = 1
    elif case == 'Temp':
        df_all = pd.read_csv(Path(r'knmi14', r'default_temp.txt'), header=None, error_bad_lines=False)   
        nr_nm = 6
        nr_lat = 9
        nr_lon = 10
        nr_strat = 1
        
    # only once operation:
    nm_stat = df_all.loc[nr_nm,:]
    nm_stat = re.findall(r'\S+', nm_stat[0])[nr_strat:]
    # only once operation:
    lat_stat = df_all.loc[nr_lat,:]
    lat_stat = re.findall(r'\S+', lat_stat[0])[1:]
    # only once operation:
    lon_stat = df_all.loc[nr_lon,:]
    lon_stat = re.findall(r'\S+', lon_stat[0])[1:]
    # generate of df
    df = pd.DataFrame(zip(nm_stat, lat_stat, lon_stat), columns=['Num', 'lon', 'lat'])
    for i, item in enumerate(df.columns):
        try:
            df[item] = pd.to_numeric(df[item], downcast="float")
        except:
            pass
    
    if show == True:
        import plotly.express as px
        from plotly.offline import plot
        fig = px.scatter_mapbox(df, lat="lat", lon="lon", hover_name=df['Num'],
                               zoom=9, height=500)
        fig.update_layout(mapbox_style="open-street-map")
        margin_len = 10
        fig.update_layout(margin={"r":margin_len,"t":margin_len,"l":margin_len,"b":margin_len})
        fig.update_traces(marker_size=12,  marker_color = '#636EFA')
        plot(fig)
    return df

def download_by_name(file_names, api_key, API_URL, DATASET_NAME, DATASET_VERSION, idx, tmpdirname = './knmi14'):
    # filter names
    dict_3050 = find_2030_2050(file_names, DATASET_NAME)
    
    # download 
    data={}
    for item in dict_3050:
        file_name = file_names[dict_3050[item]]['filename']
        if not os.path.isdir(tmpdirname): 
            os.makedirs(tmpdirname)
        if not Path(tmpdirname,file_name).is_file():
            get_file(file_name, tmpdirname, api_key, API_URL, DATASET_NAME, DATASET_VERSION)
        df_all = pd.read_csv(Path(tmpdirname,file_name), header=None, delimiter="\t")
        
        # retrieve obs
        lst_obs = []
        for i in range(12, len(df_all)):
            temp = df_all.loc[i,:]
            temp = re.findall(r'\S+', temp[0])[1:]
            lst_obs.append(temp[idx])
        if len(lst_obs) > 10957:
            lst_obs = lst_obs[-10957:]
        elif len(lst_obs) == 10956:
            lst_obs.insert(0, 0)
        data[item] = lst_obs
    try:
        df_data = pd.DataFrame(data)
    except:
        df_data
    return df_data

#%% 
# retrieve knmi14 scenarios from knmi's website
def generate_knmi14(regenerate=True):
    if regenerate==True:
        api_key = api_knmi_xt.key_xtian
        
        # only once operation; show measurement locations
        df_prec = find_latlon_knmi(case='Prec', show=True)
        df_temp = find_latlon_knmi(case='Temp', show=False)
        df_evap = find_latlon_knmi(case='Evap', show=False)
    
    
        # define database settings
        API_URL = "https://api.dataplatform.knmi.nl/open-data"
        DATASET_VERSION = "3.2"
    
        cases = ['Prec', 'Temp', 'Evap']
        dict_all = {}
    
        for case in cases:
            if case == 'Prec':
                DATASET_NAME = "knmi14_neerslag_centr" # average
                idx = list(df_prec['Num']).index(161.) # Eelde, by observing
                logging.info('Processing precipitation...')
            elif case == 'Temp':
                DATASET_NAME = "knmi14_gemiddelde_temperatuur"  # average
                idx = list(df_temp['Num']).index(280.) # Eelde, by observing
                logging.info('Processing temperature...')
            elif case == 'Evap':
                DATASET_NAME = "knmi14_referentieverdamping" # only one choice
                logging.info('Processing evaporation...')
        
            # find names
            file_names = file_list(API_URL, DATASET_NAME, DATASET_VERSION, key=api_key) # list all files
            
            # download and process
            df = download_by_name(file_names, api_key, API_URL, DATASET_NAME, DATASET_VERSION, idx, tmpdirname = './knmi14')
            dt = pd.date_range(start='1/1/1981', end='12/31/2010', freq='D')
            df.index = dt
            dict_all[case] = df
        
        with open('knmi14.pkl', 'wb') as writer:
            pickle.dump(dict_all, writer)
    else:
        with open('knmi14.pkl', 'rb') as reader:
            dict_all = pickle.load(reader)
    return dict_all



# # test 
# dict_all = generate_knmi14(regenerate=True)
