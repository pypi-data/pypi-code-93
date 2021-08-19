import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
sns.set_color_codes(palette='deep')

def plotmultiple(colnames,df,fz,plttype,orient='h',hue=None):
    """
    colnames= list of name of columns of dataframe you want plot for eg. ['sex','region']
    df=pd.DataFrame object
    fz=tuple of size of figure eg. (10,20) 
    plttype=type of plot required eg. 'count','box','swarm','hist'
    in case other than given plottype passed, boxplot will be plotted.
    orient='v'or'h'
    hue=categorical variable by which plot should be categorised eg. hue='sex'
    """
    plt.ioff()
    n=len(colnames)
    b=int(n/2)
    c=1
    plt.figure(figsize=fz)
    for i in colnames:
        plt.subplot(n,b,c)
        if(plttype=='count'):
            if(hue!=None):
                sns.countplot(df[hue],df[i],orient=orient)
            else:
                sns.countplot(df[i],orient=orient)
        elif(plttype=='box'):
            if(hue!=None):
                sns.boxplot(df[hue],df[i],orient=orient)
            else:
                sns.boxplot(df[i],orient=orient)
        elif(plttype=='swarm'):
            if(hue!=None):
                sns.swarmplot(df[hue],df[i],orient=orient)
            else:
                sns.swarmplot(df[i],orient=orient)
        elif(plttype=='hist'):
            if(hue!=None):
                sns.distplot(df[hue],df[i],orient=orient)
            else:
                sns.distplot(df[i],orient=orient)
        else:
            sns.boxplot(df[i],orient=orient)
        c=c+1
    plt.tight_layout()
    plt.show()