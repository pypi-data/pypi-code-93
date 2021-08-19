import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
sns.set_color_codes(palette='deep')

def plotmultiple(colnames,df,fz,plttype):
    """
    colnames= list of name of columns of dataframe you want plot for eg. ['sex','region']
    df=pd.DataFrame object
    fz=tuple of size of figure eg. (10,20) 
    plttype=type of plot required eg. 'count','box','swarm','hist'
    in case other than given plottype passed, boxplot will be plotted.
    """
    plt.ioff()
    n=len(colnames)
    b=1
    c=1
    plt.figure(figsize=fz)
    for i in colnames:
        plt.subplot(n,b,c)
        if(plttype=='count'):
            sns.countplot(df[i])
        elif(plttype=='box'):
            sns.boxplot(df[i])
        elif(plttype=='swarm'):
            sns.swarmplot(df[i])
        elif(plttype=='hist'):
            sns.distplot(df[i])
        else:
            sns.boxplot(df[i])
        c=c+1
    plt.show()