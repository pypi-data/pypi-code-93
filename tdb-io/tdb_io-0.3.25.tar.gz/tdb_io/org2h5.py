#!/usr/bin/env python3

from fire import Fire
import pandas as pd
import os
import datetime as dt



def orgme(filename):
    with open(filename) as f:
        r = f.readlines()
    # print(r)

    onn = False
    title = ""
    for i in r:
        if onn:
            if i.find("|-")==0:
                continue
            # avoid  before first | and after last|
            tbl = i.split("|")[1:-1]
            tbl = [ j.strip() for j in tbl] # clean it
            tbl = [ "" if j =="NaN" else j  for j in tbl ] # clean it
            print("",tbl)
            df.loc[len(df)] =  tbl
            #print(df)

        if (onn == False) and (i[0] == "|"):
            onn = True
            title = i.split("|")[1:-1]
            title = [j.strip() for j in title]
            cols = len(title)
            df = pd.DataFrame( {}, columns=title)
            print(title)
            print(df)

    print(df)
    for i in df.columns:
        if (i == 't') or (i == 'time') or (i == 'TIME') :
            df[i] = pd.to_datetime(df[i])
        else:
            df[i] = pd.to_numeric(df[i])


    print(df.dtypes)

    now = dt.datetime.now()
    newfile = os.path.splitext( filename )[0] +"_"+ now.strftime("%Y%m%d_%H%M%S")+ ".h5"

    if os.path.isfile(newfile):
        print("X... file already exists....", newfile)
    else:
        print("D... creating", newfile)
        df.to_hdf(newfile, "T"+now.strftime("%Y%m%d_%H%M%S") )


if __name__=="__main__":
    Fire(orgme)
