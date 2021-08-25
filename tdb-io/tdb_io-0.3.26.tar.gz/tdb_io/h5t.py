#!/usr/bin/env python3


#from pymongo import MongoClient
import pymongo # to get ASCENDING
import datetime
import time

#
# /home/milous/.local/lib/python3.6/site-packages/pandas/plotting/_matplotlib/converter.py:103: FutureWarning: Using an implicitly registered datetime converter for a matplotlib plotting method. The converter was registered by pandas on import. Future versions of pandas will require you to explicitly register matplotlib converters.
#
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

from fire import Fire

def get_date_from_mark( atime ,string=False ): # 1d 1h 1w
    """ enter  string number+time_unit like 5m 30m 1h 3d 5w
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




def main(hdf5name,
         key="",
         plot="",
         #values="",
         DERIVATIVE="",
         INTEGRAL=False,
         last="",
         background="white",
         points_off=False,
         lines_off=False,
         writejpg=False,
         silent = False, # no graph
         hdf5=""):

    """
    1/ plot  a,b,c:d,e,f
    2/ -D 1y ... derivatives addressed by d_a,d_b
       always plot byt histogram bars

    3/ -w can be a.jpg,  a.txt, .... ?a.org?
    """

    print("D... received ARGUMENTS:")
    print("hfname={} key={} plot={} DER={} INT={} last={} backg={} points={} lines={} writejpg={} silent={}".format(
        hdf5name,
        key,
        plot,
#        key,
        DERIVATIVE,
        INTEGRAL,
        last,
        background,
        points_off,
        lines_off,
        writejpg,
        silent, # no graph
        hdf5)
    )

    if 1==1:
        #
        with pd.HDFStore(hdf5name) as hdf:
            keysavailable=hdf.keys()
            print("i... keys         :",  keysavailable)
            if len(keysavailable)==1:
                # overriding key
                key=keysavailable[0]
                print("D... only one key available, key overriden....")
            keyok=False
            for i in hdf.keys():
                if i==key:keyok=True
            if keyok:
                keyname= key
            else:
                print("D... no key",key)
                sys.exit(0)
            print("i... selected key :",  keyname )
            df = hdf.get(key)
            #df=pd.read_hdf( hdf5name, keyname )



        cols = df.columns.tolist()
        timecol_DT_format = True

        # this works with datetime, but what if there are seconds?
        timecol = 't'
        if not timecol in cols:
            if 'time' in cols:
                timecol = 'time'
            elif 'TIME' in cols:
                timecol = 'TIME'
            else:
                if len(plot)>1:
                    timecol = plot[0]
                    if len(plot)==2:
                        print("#... single", plot)
                        plot = plot[1]
                    else:
                        plot = plot[1:]
                    print("D... timecol not TIME; but =",  timecol, " plot=",plot)
                    timecol_DT_format=False # means float


        # TIME SORT HERE
        if len(last)>0:
            start = get_date_from_mark(last)
            df = df[df[timecol]>start]
            df.reset_index(drop=True, inplace=True)


        #print(df)
        #df=pd.DataFrame( licursor )
        #del df["_id"]               # DELETE _id, dont mess with it
        #  nicer display: make 't'  be the 1st column ==================

        if timecol in cols:
            # PUT time to the first (left-right) place for nice print
            while cols[0]!=timecol:
                cols=cols[-1:]+cols[:-1]

            # also check the FORMAT
            print("D... TIME FORMAT", df[timecol][0], type(df[timecol][0]) )
            if type(df[timecol][0])==numpy.float64:
                timecol_DT_format=False # means float
            if type(df[timecol][0])==str:
                # print("STR")
                df[timecol] = pd.to_datetime(df[timecol])
                print("X... TIME FORMAT CONVERTED FROM STRING ",  type(df[timecol][0]) )

                timecol_DT_format=False # means float
        else:
            print("D...  NO TIME variable.... 't' expected")



        df=df[cols]
        ##############################
        #---------- PRINTOUT - FINAL ===========================================
        #
        print( df )
        #       print full table:
        #            with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #                print(df)
        #  WRITE TXT -f a.txt

        # printing to txt file?
        if isinstance(writejpg,bool):
            print("D...  WRITEJPG is BOOL, just show", writejpg)
            #writejpg=""
        else:
            if ( len(writejpg)>0) and( writejpg.find(".txt")>=len(writejpg)-5 ):
                # TRICK TO PRINT TO txt FILE:
                #df.to_csv(args.writejpg, sep="\t", index=False)
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    with open( writejpg,"w") as f:
                        f.write('''---
documentclass: extarticle
fontsize: 8pt
geometry: [top=0.5cm, bottom=0.5cm, left=1.5cm, right=1cm]
---
''')
                        outlines=df.__str__().split("\n")
                        for i in outlines:
                            f.write( "    "+i+"\n" ) # I NEED MAGIC OF 4 spaces and after
                            #      -f markdown+hard_line_breaks is not necessary, courier works...
                        print("D... table in file", writejpg)
                        print("        pandoc    ",writejpg,"  -o o.pdf")

        #
        #############################


        # for ii in  values:     # PRINT THE LAST VALUE of the column
        #     print("D... ",ii," of ", values.split(","))
        #     print( df[ii].iloc[0] , " ... ", df[ii].iloc[-1]) # 1st in dataframe by time

        if DERIVATIVE != "":
            factor=0
            # correspodning value over time period
            multiple=(DERIVATIVE[:-1]) # should be 1
            print("D...  time normalization=", multiple)
            multiple=float( multiple ) # should be 1
            if DERIVATIVE[-1]=="S": factor=1
            if DERIVATIVE[-1]=="M": factor=60
            if DERIVATIVE[-1]=="H": factor=3600
            if DERIVATIVE[-1]=="d": factor=3600*24
            if DERIVATIVE[-1]=="m": factor=3600*24*30
            if DERIVATIVE[-1]=="y": factor=3600*24*365
            if DERIVATIVE[-1]=="w": factor=3600*24*7
            print("D...  derivating all now ......................",factor,multiple)
            factor=factor*multiple
            for i in cols: #  there is t here!!!!
                #df['d_'+i]=df[i].diff()/df['t'].diff().dt.total_seconds()*factor
                df['d_'+i]=-df[i].diff( periods=-1 ) # create DIFF
            for i in cols: #  there is t here!!!!
                if i!=timecol:                           # MAKE RATE norm on TIME & FACTOR
                    df['d_'+i]=df['d_'+i]/df['d_'+timecol].dt.total_seconds()*factor
            df['d_'+timecol]=-df[timecol].diff( periods=-1 )
            df['t2']=df[timecol]-df[timecol].diff( periods=-1 )/2 # in the midle of period


            #print(df)
        ###########################   PLOT  ##############
        #  idea:  t1,t2,t3 h1,h2,h3   would make two axes best
        #
        #
        if plot:
            #if DEBUG:
            plot = str(plot)
            plot = plot.replace("'","")
            plot = plot.replace(" ","")
            plot = plot.replace("(","")
            plot = plot.replace(")","")

            # NEW TST 2 axes===========  a,b,c:d,e,f TWO SCALES
            PLOLIST1=[]
            PLOLIST2=[]

            # print("D... PLOT PARAMETER(s):  type:",type(plot),"len:", len(plot)," =", plot )
            if isinstance(plot,str) and (plot.find(",")>0 or plot.find(":")>0):
                print("D... list in form of str present")
                if plot.find(":")>0:
                    PLOLIST1=plot.split(":")[0].split(",")
                    PLOLIST2=plot.split(":")[1].split(",")
                else:
                    PLOLIST1=plot.split(",")

            elif isinstance(plot,tuple):
                # tuple not happen now
                print("D... (plot) tuple present, creating list")
                plot = [ x for x in plot]
                PLOLIST1=plot
            else: # will be str anyways
                # single word
                print("D... (plot) not tuple, creating list")
                plot=[plot]
                PLOLIST1=plot

            print("D... plot list1",plot)
            print("D... axes 1 vs 2 : ", PLOLIST1 ,"vs.", PLOLIST2 )


            #================ prepare two axes lists


            fig=plt.figure( )
            fig.patch.set_facecolor( background )
            #fig=plt.figure(  figsize=(5, 4), dpi=100 )
            host = fig.add_subplot(111)
            numero=0  # COUNTER yax1 yax2
            markcols     =['b.-','r.-','g.-','c.-','m.-','y.-', 'tab:orange',  'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive']
            # lines off
            if lines_off:
                markcols=['b.','r.','g.','c.','m.','y.', 'tab:orange',  'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive']
            if points_off:
                markcols=['b-','r-','g-','c-','m-','y-', 'tab:orange',  'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive']
            markcol2=['b.','r.','g.','c.','m.','y.', 'tab:orange',  'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive']
            plot_lns=[]   # legend is organized here
            ###########
            # axis 1
            #
            # here is INTEGRAL, so i put DERIVATE also? ------ but DRV should be in pandas...
            ###########
            preleg=""
            if len(DERIVATIVE)>0:
                preleg="[ Norm="+DERIVATIVE+"]  "

            restlabels=[] # y2 will have al the labels on yaxis
            for i in PLOLIST1[:len(markcols)-2]:
            #for i in args.plot[:len(markcols)-2]:
                if numero>=0:
                    #print(i)
                    #print(df[i])
                    #print(np.isnan( df[i] ) )
                    logic_array = ~(np.isnan( df[i] )) # BIG TRICK - void NaN

                    # I plot normally OR derivative "t2"
                    if DERIVATIVE and i.find("d_")>=0:
                        # I transform from np to LISTS: bar cannot plot np well.
                        # binb width from d_t * 0.9; colors game
                        print("D... axis 1; derivative done in pandas; drawing vs. 't2'")
                        aaa=[ x for x in df.t2[logic_array]  ]
                        daa=[ -x.total_seconds()/24/3600*0.9 for x in df["d_"+timecol][logic_array]  ]
                        bbb=[ float(x) for x  in  df[i][logic_array] ]
                        #print(  aaa )
                        #print( daa )
                        #print( bbb )
                        p1=host.bar( aaa , bbb , width=daa  , label=i ,edgecolor=markcol2[numero][0] ,color=markcol2[numero][0] ,alpha=0.2)
                        p1,=host.plot( df.t2[logic_array] , df[i][logic_array] , markcol2[numero] , label=i+preleg)

                    else:
                        print("D... classical plotting here option. No DER no INTEG. lines_off==", lines_off)
                        p1,=host.plot( df[timecol][logic_array] , df[i][logic_array] , markcols[numero] , label=i)
                        print("D... plotted")

                    if INTEGRAL:
                        print("D...  ploting integral axis 1")
                        ## EXPERIMENT  INTEGRATE
                        Ingral=integratepd( df[timecol][logic_array] , df[i][logic_array]   )
                        print( 'Integral ==',Ingral.iloc[-1]," to ",Ingral.iloc[0])
                        p1a,=host.plot( df[timecol][logic_array][:-1] , Ingral , markcols[numero][0]+':' )
                        ## EXPERIMENT  INTEGRATE

                    ####p1,=host.bar( df.t , df[i]  )
                    restlabels.append( i )
                    plot_lns.append( p1 )
                    host.set_ylabel(i)

                    #PRELEG not here anymore
                    #host.set_ylabel( preleg +";".join(restlabels)[:50]  ) #, color=markcols[numero][0]
                    host.set_ylabel( ";".join(restlabels)[:50]  ) #, color=markcols[numero][0]
                numero=numero+1

            plt.gca().grid() # I put grid here to be aligned with y-values (left)
            ###########
            # axis 2
            ###########
            restlabels=[] # y2 will have al the labels on yaxis
            numero2=0
            for i in PLOLIST2[:len(markcols)-2]:
            #for i in plot[:len(markcols)-2]:
                if numero2==0:
                     ax2=host.twinx()
                     logic_array = ~(np.isnan( df[i] ))


                     # I plot normally OR derivative "t2"
                     if DERIVATIVE and i.find("d_")>=0:
                         # I transform from np to LISTS: bar cannot plot np well.
                         # binb width from d_t * 0.9; colors game
                         print("D... axis 1; derivative done in pandas; drawing vs. 't2'")
                         aaa=[ x for x in df.t2[logic_array]  ]
                         daa=[ -x.total_seconds()/24/3600*0.9 for x in df["d_"+timecol][logic_array]  ]
                         bbb=[ float(x) for x  in  df[i][logic_array] ]
                         #print(  aaa )
                         #print( daa )
                         #print( bbb )
                         p1=ax2.bar( aaa , bbb , width=daa  , label=i ,edgecolor=markcol2[numero][0] ,color=markcol2[numero][0] ,alpha=0.2)
                         p1,=ax2.plot( df.t2[logic_array] , df[i][logic_array] , markcol2[numero] , label=i+preleg)

                     else:
                         p1,=ax2.plot( df[timecol][logic_array] , df[i][logic_array] , markcols[numero] , label=i)


                     #p1,=ax2.plot( df.t[logic_array] , df[i][logic_array] , markcols[numero] , label=i)
                     if INTEGRAL:
                        print("D...  axis 2 CANNOT HAVE INTEGRAL !")

                     restlabels.append( i )
                     ax2.set_ylabel(  i , color=markcols[numero][0] )
                     print("D... ValueForAxis: set_ylabel   color=",markcols[numero][0])
#                     ax2.tick_params( i , colors=markcols[numero][0] )
#                     print("D... ValueForAxis: tick_params   color=",markcols[numero][0])
                     # aligning right yticks with left side
                     #
                     #ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(host.get_yticks()) ) )

                     plot_lns.append( p1 )
                if numero2>=1:
                     logic_array = ~(np.isnan( df[i] ))
                     p1,=ax2.plot( df[timecol][logic_array] , df[i][logic_array] , markcols[numero] , label=i)
                     restlabels.append( i )
                     ax2.set_ylabel(  ";".join(restlabels)[:50]  ) #, color=markcols[numero][0]
                     plot_lns.append( p1 )
                numero=numero+1
                numero2=numero2+1

            host.legend( handles=plot_lns, loc='best' )
                #plt.plot( df.t , df[i] ,'.' , label=i)# worked good
            ###plt.plot( df.t , df.b, 'g-.d' )
            ###plt.plot( df.t , df.c, 'r-..' )
            print("D... xdate")
            plt.gcf().autofmt_xdate()   # rotates
            print("D... xdate done")

            #print( "DDD .............. t     ", df.t )
            #print( "DDD .............. t[]   ", df.t[0] )  # last
            #print( "DDD .............. len   ", len(df.t) )  # last
            #print( "DDD .............. t[len] ", df.t[ len(df.t)-1 ] )  #
            #print( "DDD ..............       ",  (df.t[0] - df.t[ len(df.t)-1 ]).total_seconds()   )
            if timecol_DT_format == True: # datetime format - should work for electro
                print("D... DTformat true")
                if  (df[timecol][0] - df[timecol][ len(df[timecol])-1 ]).total_seconds() <3600*24*3:  # Three days  3 days
                    myFmt = mdates.DateFormatter('%y-%m-%d %H:%M') #
                else:
                    myFmt = mdates.DateFormatter('%Y-%m-%d') #
                    ####myFmt = mdates.DateFormatter('%H:%M') #
                plt.gca().xaxis.set_major_formatter(myFmt)
            #----------- if format FLOAT SECONDS nupmy 64: i just print

            #plt.gca().grid() # move after host==ax1 before ax2
            #plt.legend( loc='upper left' )
            fig.tight_layout()
            #============================== PICTURE SHOULD BE OK NOW
            plt.text(0,1, datetime.datetime.now().strftime("%Y/%m/%d_%H:%M"),transform=plt.gca().transAxes, fontsize=8,   verticalalignment='bottom')


            # draw jpg must come before the display?yes.
            if isinstance(writejpg,str) and( writejpg.find(".txt")<0):
                print("D... --writejpg is",writejpg," creating jpg")
                plt.savefig( writejpg  , bbox_inches='tight', facecolor=background  )
                #plt.savefig( writejpg , bbox_inches='tight' )

            if writejpg: # IF -w ==  boolean -w  === I ONLY DISPLAY
                print("D... --writejpg is",writejpg, " and I display it")
                plt.show()
            else:
                print("i... use  '-w' to show graph, '-w filename' to show and save jpg/txt")
                #else:
            #fig.patch.set_facecolor( background )



        if hdf5 != "":
            hdf = pd.HDFStore( hdf5 )
            name=DATABASE+"_"+COLLECTION+"_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            hdf.put( name  , df, format='table', data_columns=True)
            ks= hdf.keys()
            for i in ks:
                print( "  ", i, hdf[i].shape)
    ###################### WRITE SECTION #################
    else:
        if timecol in insdict:  # key in dict
            #if DEBUG:
            print("D...  time insertion detected...")
            val=prepare_write_no_time( insdict )
        else:
            #if DEBUG:
            print("D... automatic time...")
            val=prepare_write( insdict )
        result=collection.insert_one( val )
        print("result ID of write:", result.inserted_id )

if __name__=="__main__":
    Fire(main)
