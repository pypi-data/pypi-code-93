#!/usr/bin/env python3
# -fire CLI
###############################################
#
# READ H5 file a
#
# AND convert it to influx
# df2infl
#
#
################################################
from fire import Fire
from tdb_io.version import __version__
import pandas as pd


from pymongo import MongoClient
import pymongo # to get ASCENDING
import datetime
import time

from influxdb import InfluxDBClient
import os
import socket



#=======================================================================

def read_h5( hdf5name , key = "" , fulltext = False, return_none = True ):
    """
read h5 file to pandas DataFrame
flags: -f | --fulltext :  show all rows
    """
    print("i...  ========================= hdf5  part =============")
    print("D... key==",key)
    if key!="":
        print("D... using the key ==", key)
    with pd.HDFStore(hdf5name) as hdf:
        keysavailable=hdf.keys()
        print("i... keys         :",  keysavailable)
        if len(keysavailable)==1:
            key=keysavailable[0]
            print("D... *** only one key available *** opening this key ***")

        keyok=False
        for i in hdf.keys():
            # i = i[1:]
            print("required:{}   seen: {}".format(key,i) )
            if i==key:
                keyok=True
        if keyok:
            keyname= key
        else:
            print("D... no valid key selected:",key)
            quit()
        print("i... selected key :",  keyname )

    print("D... Reading",hdf5name, keyname)
    df=pd.read_hdf( hdf5name, keyname )
    print("_"*40,"info")
    df.info()

    #df_reader = hdf.select('my_table_id', chunksize=10000)
    #df = pd.read_hdf( hdf5name, 'd1' ) #,
                   #where=['A>.5'], columns=['A','B'])
    #plt.plot( df['t'] , df['hightarif'] ,'.')

    print("i... DFrame ok;    LENGTH:",len(df))
    print("i... columns      :", list(df.columns.values) )
    print("_"*70,"info")
    timekey = "t" # normally  't', but I allow for time TIME....
    if not 't' in df.keys():
        if 'time' in df.keys():
            timekey = "time"
        if 'TIME' in df.keys():
            timekey = "TIME"
    if timekey in df.keys():
        df = df.sort_values(by=[timekey], ascending=1)
    else:
        print("X... NO TIME KEY present, continuing")
    print("D... fulltext print (-f):", fulltext)
    if fulltext:
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', -1)
    print(df)
    if return_none:
        print("D...    you   asked  to   return   NONE.... returning NONE")
        return None
    else:
        return df






#===============================================================

def read_infl_credentials(config="~/.influx_userpassdb"):
    """ READ and RETURN Influxdb  Credentials
    """
    ips=[]
    ips1=[]
    ips2=[]
    try:
        with open( os.path.expanduser("~/.myservice_discover8086") ) as f:
            ips1=f.readlines()
    except:
        print("X... NO FILE ~/.myservice_discover8086 with automatic IPs")

    try:
        with open( os.path.expanduser("~/.myservice_permanent8086") ) as f:
            ips2=f.readlines()
    except:
        print("X... NO FILE ~/.myservice_permanent8086 with permanent IPs")


    ips=ips1+ips2
    ips=[ i.strip() for i in ips]
    with open(os.path.expanduser( config ) ) as f:
        creds=f.readlines()
    creds=[ i.strip() for i in creds ]
    return creds






#================================================================

def df2infl( hdf5name,  MEASUREMENT, h5key="", IP="127.0.0.1" ):
    """translate DF to INFLUXDB. Database is in credentials. df2infl file meas -IP=www.cz
    """
    print("D...  df to infl, IP=",IP)
    creds=read_infl_credentials()
    df=read_h5( hdf5name ,h5key, return_none=False )

    if len(IP)<7:
        print("D... IP too short......... quit")
        quit()
    if IP[0].isdigit(): #
        print("D... IP numbers......... ")
        client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=False, timeout=3)
    else:
        print("D... IP text, i do ssl......... ")
        client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=True, verify_ssl=False,timeout=8)

    cols=list(df.columns.values)
    MYHOSTNAME=socket.gethostname()
    print("D....................MYHOST=",MYHOSTNAME )
    #
    ##============= for each line repeat this=============
    #
    for x in range(len(df)-1,-1,-1):
        json_body = [ {"measurement":MYHOSTNAME+"_"+MEASUREMENT} ]
        json_body[0]["fields"]={}
        for i in cols:
            val=df.loc[x][i]
            if i=="t":
                i="time"
                print( val )
                #------either
                #val=val.strftime("%Y-%m-%dT%H:%M:%SZ")
                #or---------
                try:
                    val=time.strptime( str(val) ,"%Y-%m-%d %H:%M:%S.%f")
                except:
                    val=time.strptime( str(val) ,"%Y-%m-%d %H:%M:%S")
                val = int( time.mktime( val )*1e+9 )
                print( val )
                #json_body[0]["time"]={}
                json_body[0]["time"]= val

                from numbers import Integral
                ising= isinstance(val, Integral)
                print( "D.. is instatnce IOntegral",ising)
                if not ising:
                    quit()
            else:
                json_body[0]["fields"][i]=val
            #    ={"prague_temp":1,"prague_humi":2}
        print("D... json to ",IP,"...", json_body )
        client.write_points(json_body)
        #client.write(json_body , protocol=u"json")





#=============================================================
#=============================================================
#=============================================================
if __name__=="__main__":
    print("D... in main of project/module:  tdb_io/h5toinfl ")
    print("D... version :", __version__ )
    print("D................................................")
    print("D...  ")
    print("D...  ")

    Fire( {
      'read_h5': read_h5,
      'df2infl': df2infl,
#      'help': help
  } )
