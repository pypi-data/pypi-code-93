#!/usr/bin/env python3
# -fire CLI
from fire import Fire
from tdb_io.version import __version__




from pymongo import MongoClient
import pymongo # to get ASCENDING
import datetime
import time

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()



#  from monary import Monary #  10x faster BUT CANNOT FIND mongoc.h
import numpy
import numpy as np
import pandas as pd

import argparse
import os
import json

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#================== I import from myself........:)
#import influx

DEBUG=1  # will change in MAIN  args
ACTUAL_CREDENTIALS={}
#=================================================

print("D...  project/module:  tdb_io/mongo :", __version__ )
#print("i... module tdb_io/mongo is loaded")


#=================================================

def read_mongo_credentials( configfile="~/.mymongo.local" , silent=False):
    """Reads filename with credentials:  ~/.mymongo.local   Returns: output DICT with credentials
    """
    cfgfile=os.path.expanduser( configfile )
    if DEBUG:print("D... reading credentials", cfgfile)
    if not silent:print("i... reading ", cfgfile , end="\n" )
    cdict={}
    if os.path.isfile( cfgfile ):
        with open( cfgfile ,'r') as f:
            cdict=json.load( f )
        if not silent:print( ' ... HOST=',cdict['host'], end="\n" )
    else:
        if not silent:print(" !... NO FILE FOUND")
        if not silent:print("""
X...   try to create some JSON file like:
____________________________________________
{
"host":"127.0.0.1",
"username":"user",
"password":"xxx",
"authSource":"admin"
}
____________________________________________
        """)
        quit()
    print("i... credentioals ..                             [OK]")
    return cdict  # returns credentials============



#=================================================


def test_read_mongo_credentials():
    print("D... test function ... run pytest")
    r=read_mongo_credentials()
    assert  len(r["host"])>0
    assert  len(r["username"])>0
    assert  len(r["password"])>0
    assert  len(r["authSource"])>0





#=================================================


# from reading file, gives an extra question, returns client
#   ~/.mymongo.local   assumed   TEST and DATA

def get_mongo_database( database , initialconfig="~/.mymongo.local" , silent=False, return_none=True  ):
    """
    Return: client_to_database / needs databasename
    """
    global ACTUAL_CREDENTIALS
    if database=="":
        print("X... no database given, try test, data, mysql ...")
        return None
    print(ACTUAL_CREDENTIALS)
    if  len(ACTUAL_CREDENTIALS)==0:
        print("W... no actual credentials, reading the file",initialconfig)
        ACTUAL_CREDENTIALS=read_mongo_credentials( initialconfig ,silent=silent)
    print("D...",ACTUAL_CREDENTIALS)
    if DEBUG:print("D... has read credentials")
    if DEBUG: print( "D... ", ACTUAL_CREDENTIALS)
    if ACTUAL_CREDENTIALS['host']=="":
        print("X.... host not defined in cfg, bad cfg file...") # rare case
        quit()
    client = MongoClient( ACTUAL_CREDENTIALS['host'],
                     username=ACTUAL_CREDENTIALS['username'],
                     password=ACTUAL_CREDENTIALS['password'],
                     authSource=ACTUAL_CREDENTIALS['authSource'],
#                    authMechanism='SCRAM-SHA-1', # !!! later versions
                     serverSelectionTimeoutMS=1000,
                     connect=False
     )
   #  { "host":"127.0.0.1",
   # "username":"ojr",
   # "password":"aaaa",
   # "authSource":"data"
   #     }

    ###---- ONE EXTRA question == slowdown, but no messing later
    q=False
    if DEBUG:print("D... extra slowingdown question on ismaster")
    try:
        if DEBUG:print("D... asking admin: ismaster: ... ")
        result = client.admin.command("ismaster")
        if DEBUG:print("D... client is                                   [OK]")

    except:
    #except errors.ConnectionFailure:
        print("!... Connection failed <- ismaster check")
        q=True
    if q:
        try:
             errors
        except:
            print("!... `errors` object not found ... mongo database doesnt exist?")
            print("!...  may authSource is not 'auth' but 'data' ? ")
            print("!... quitting");quit()
    #not authorizes!!!  print( client.database_names() )
    print("D... NAMES==",    client.database_names() )
    if return_none:
        print("D...    you   asked  to   return   NONE.... returning NONE")
        return None
    else:
        return client[ database ]
    print("D...  get_mongo_database ...........             [OK]")





#=================================================
#                "~/.mymongo.local"
def tell_mongo_collections( database , initialconfig="~/.mymongo.local" ):
    """
    lists collections in the database . NEEDS:  databasename /test/data/
    """
    dbase=get_mongo_database( database ,initialconfig, silent=True, return_none=False)
    if DEBUG:print("i... dbase obtained. Searching collections names:", database )
    collection = dbase.collection_names(include_system_collections=False)
    #print( "{:10s}   {}".format( database,sorted(collection) ) )
    print( "\n=== {:10s} ==========================".format( database ) )
    print(   " collection name      | number of records".format( database ) )
    print(   "_________________________________________" )
    for i in sorted(collection):
        print("{:>19s}  ".format(i) , end="" )
        a=[]
        la=dbase[ i ].count()
        #la=list(a)
        print("   {:9d}".format(  la )   )
    #print("D.... returning collection")
    return collection





#=================================================

def get_date_from_mark( atime ,string=False ): # 1d 1h 1w
    """ Returns START time. NEEDS: number+time_unit ... 5m 30m 1h 3d 5w
        returns START time
              Either  timedelta
              Or      string (if mongodb t is string)
    """
    unit=1
    if atime[-1]=='S': unit=1
    if atime[-1]=='M': unit=60
    if atime[-1]=='H': unit=60*60
    if atime[-1]=='d': unit=60*60*24
    if atime[-1]=='m': unit=60*60*24*30
    if atime[-1]=='y': unit=3600*24*365
    if atime[-1]=='w': unit=60*60*24*7
    val=atime[:-1]
    ret=float(val) * unit
    print( "D... time distance:  value=",val," unit=", unit ," ... seconds=", ret )
    start=datetime.datetime.now() - datetime.timedelta( seconds= ret)
    print("D... fetching from DATE: ",start)
    if string:
        start=start.strftime("%Y-%m-%d %H:%M:%S")
    return start







#==================================================================

def mongo2h5( DATABASE="", COLLECTION="",  nlimit=int(1e+9), tfrom="100y",  initialconfig="~/.mymongo.local", write_h5=True):
    """
    Creates h5 FILE. NEEDS: database collection ( test,test )
    """
    #
    if DATABASE=="":
            get_mongo_database( DATABASE )
            print("________________ list of databases _______")
            quit()
    #
    #
    if COLLECTION=="":
            #get_mongo_database( DATABASE )
            tell_mongo_collections( DATABASE )
            print("________________ list of collections _______")
            quit()
    #
    db=get_mongo_database( DATABASE , initialconfig , return_none=False)
    collection=db[ COLLECTION ]
    # i have db and collection
    # i sort by time  t
    collection.ensure_index(  [ ("t", pymongo.ASCENDING) ]   )
    READ_CONDITION={}
    start=get_date_from_mark( "100y", string=False ) # 1d 1h 1w
    READ_CONDITION['t']={'$gte': start}
    print("D.... READ_CONDITION", READ_CONDITION," nlimit=", nlimit)
    #start
    #     READ_CONDITION['t']={'$gte': start}
    #==== ii in arg.values ===
    #
    #READ_CONDITION[ ]={'$ne':None }
    #
    cursor=collection.find(  READ_CONDITION  ).sort([('t',-1)]).limit( nlimit )
    licursor=list(cursor)
    if len(licursor)==0:
        print("X... NO DATA")
        quit()
    print("D...  creating DataFrame")
    df=pd.DataFrame( licursor )
    print("D...  deleting _id")
    del df["_id"]               # DELETE _id, dont mess with it
    cols = df.columns.tolist()
    #---------------put 't' in front
    print("D...  reorganizing DataFrame")
    if 't' in cols:
        while cols[0]!='t':
            cols=cols[-1:]+cols[:-1]
    else:
        if DEBUG:print("D...  NO TIME variable.... 't' expected")
    df=df[cols]
    print(df)
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #    print(df)
    if not write_h5: return
    name=DATABASE+"_"+COLLECTION+"_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    hdf = pd.HDFStore( name+".h5" )
    hdf.put( name  , df,  format='table',  data_columns=True)
    ks= hdf.keys()
    for i in ks:
        print( "  ", i, hdf[i].shape)









#=================================================


#  create DICT with floats from programmed arguments
#def prepare_write( **kwargs ):  # a=1,b=2....
def prepare_write_no_time( kwargs , silent=True):      # DICT
    """
    INTERNAL: help for prepare_write_no_time  ['t'] is in input
    """
    tnew=datetime.datetime.strptime(kwargs['t'],"%Y-%m-%d %H:%M:%S")
    val={"t":tnew }
    for k in kwargs.keys():
        if not silent:print("    k:w=",k,":",kwargs[k] )
        if kwargs[k] is None:
            val[ k ] = None
        elif k!="t":
            val[ k ] = float( kwargs[k] )

    if not silent:print("FINAL",val)
    return val







#=================================================

######   NORMAL -  WITH AUTOMATIC TIME ########
def prepare_write( kwargs ):      # DICT
    """
    INTERNAL: help for prepare_wite - gets current time
    """
    val={ "t":datetime.datetime.now()
    }
    for k in kwargs.keys():
        print("    k:w=",k,":",kwargs[k] )
        if kwargs[k] is None:
            val[ k ] = None
        else:
            val[ k ] = float( kwargs[k] )
    print("FINAL",val)
    return val







#=================================================

def mongowrite( DATABASE="test", COLLECTION="test",
                values="",
                initialconfig="~/.mymongo.local" , influx_too=False ):
    """
    Writes into MONGO  database (test) collection (test) values (a=1,b=2)
    """
    #
    if DATABASE=="":
            get_mongo_database( DATABASE )
            print("________________ list of databases _______")
            quit()
    #
    #
    if COLLECTION=="":
            #get_mongo_database( DATABASE )
            tell_mongo_collections( DATABASE )
            print("________________ list of collections _______")
            quit()
    #
    #
    #
    db=get_mongo_database( DATABASE , initialconfig , return_none=False)
    collection=db[ COLLECTION ]
    #
    #
    #========= prepare insert values ---------------- make THEM DICT
    INSERTDICT={}
    if DEBUG: print("D...   preapring write - general")
    #insertvals=",".join(values)
    if len(values)==0:
        print("D....  no values given ... calling mongo2h5")
        mongo2h5( DATABASE, COLLECTION, nlimit=100000, write_h5=False)
        quit()

    #
    #
    #
    #
    #=================== WRITe TO INFLUX ================
    if not influx_too:
        influx.influxwrite( DATABASE, COLLECTION, values)
    #
    #
    #
    insertvals=values.split(",")
    print("D... insert pairs:", insertvals)
    for i in insertvals:
        print("D... insert pair:",i)
        key=i.split("=")[0]
        val=i.split("=")[1]
        INSERTDICT[key]=val
    if DEBUG:print("D... INSERT DICT:", INSERTDICT )
    #_____________________________________________________
    #
    #
    #    ###################### WRITE SECTION #################
    if "t" in INSERTDICT:  # key in dict
        if DEBUG:print("D...  time insertion detected...")
        val=prepare_write_no_time( INSERTDICT )
    else:
        if DEBUG:print("D... automatic time...")
        val=prepare_write( INSERTDICT )
    print("i... INSERTING to {} / {} <=".format(DATABASE,COLLECTION), INSERTDICT)
    result=collection.insert_one( val )
    print("result ID of write:", result.inserted_id )







#=================================================
def help( arg="" ):
    """help - not used
    """
    print("H... help")
    if len(arg)>0:
        Fire(arg)
#=================================================





#=============================================================
#=============================================================
#=============================================================
if __name__=="__main__":
    print("D................................................")
    print("D...    database (test,data) - collections - values?")
    print("D...  ./mongo.py  read_mongo_credentials       ")
    print("D...  ./mongo.py  get_mongo_database test      ")
    print("D...  ./mongo.py  tell_mongo_collections test  ")
    print("D...  ./mongo.py  mongo2h5 test home_electro")
    print("D...  ")
    print("D...  ./mongo.py  mongowrite ")
    print("D...  ./mongo.py  mongowrite test test test=5")
    print("D... ./mongo.py  mongo2h5 test test ")
    print("D...  ")

    Fire( {
      'read_mongo_credentials': read_mongo_credentials,
      'get_mongo_database': get_mongo_database,
      'tell_mongo_collections': tell_mongo_collections,
#      'get_date_from_mark': get_date_from_mark,
      'mongo2h5':mongo2h5 ,
#      'prepare_write_no_time':prepare_write_no_time ,
#      'prepare_write':prepare_write ,
      'mongowrite':mongowrite ,
#      'help': help
  } )
