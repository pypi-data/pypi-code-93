# -*- coding: utf-8 -*-

from ctypes import c_uint8, c_uint16, c_uint32, c_int16, c_float, Structure
from struct import pack, unpack
from os.path import getsize
from sys import argv
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import re, os
import datetime as dt
from datetime import timezone
import numpy as np
import csv
from spacepy.time import Ticktock
from spacepy.coordinates import Coords
from scipy import interpolate
import pytz
import shutil as sh
from . import backend as be


###############################################################################
#CuPID House Style

plt.rcParams['axes.grid'] = True
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Verdana']
red = '#CA054D'
blue = '#0091AD'
green = '#9CE7C8'
black = '#003049'
colormap = 'inferno'
filepath = os.getenv('DROPBOXBU')

###############################################################################

def plot_xrbr(filename):

    xrdata = be.read_xrbr_sci(filename)
    times = np.transpose([d.time for d in xrdata])
    x0r, x1r, y0r, y1r = np.transpose([d.channels for d in xrdata])
    #####
    ADC_Vrange = 4.5
    VperC = ADC_Vrange/65536.
    x0 = x0r * VperC
    x1 = x1r * VperC
    y0 = y0r * VperC
    y1 = y1r * VperC
    nbins = 100
    lo_thold = 2.1#16019.
    hi_thold = 3.3#62622.
    offset = 1
    # offsetx0 = 1#14563.
    # offsetx1 = 1#14563.
    # offsety0 = 1#14563.
    # offsety1 = 1#14563.
    #
    mask_x0 = np.where((x0 < hi_thold) & (x0 > lo_thold))
    mask_x1 = np.where((x1 < hi_thold) & (x1 > lo_thold))
    mask_y0 = np.where((y0 < hi_thold) & (y0 > lo_thold))
    mask_y1 = np.where((y1 < hi_thold) & (y1 > lo_thold))

    mask_x = np.intersect1d(mask_x0,mask_x1)
    mask_y = np.intersect1d(mask_y0,mask_y1)

    pass_mask = np.intersect1d(mask_x,mask_y)

    x0pass = (x0[pass_mask]) - offset
    x1pass = (x1[pass_mask]) - offset
    y0pass = (y0[pass_mask]) - offset
    y1pass = (y1[pass_mask]) - offset

    tvalid = times[pass_mask]

    # NOMINAL CALCULATION OF MCP POSITION
    x =(x0pass/(x0pass+x1pass))
    y =(y0pass/(y0pass+y1pass))
    # ALIGNMENT CORRECTION DEVELOPED BY C. O'Brien
    x_offset = 0.5006
    y_offset = 0.5061
    M_inv = np.array([[1.0275, -0.14678],[-0.13380, 1.0293]])
    x_shift = x - x_offset
    y_shift = y - y_offset
    x = (x_shift * M_inv[0,0] + y_shift * M_inv[0,1]) + 0.5
    y = (x_shift * M_inv[1,0] + y_shift * M_inv[1,1]) + 0.5
    #THE -0.5 IS INTHERE TO SHIFT IT TO 0,0
    #THE *10 IS A NORMALIZATION FACTOR LIKE SIEGMUND et. al. 1986
    x = (x-0.5)*7*nbins
    y = (y-0.5)*7*nbins

    XCenterPlus = np.where(y > -1)
    XCenterMinus = np.where(y < 1)
    XMask = np.intersect1d(XCenterPlus,XCenterMinus)
    XCenter = x[XMask]

    YCenterPlus = np.where(x > -1)
    YCenterMinus = np.where(x < 1)
    YMask = np.intersect1d(YCenterPlus,YCenterMinus)
    YCenter = y[YMask]

    left, width = 0.15, 0.55
    bottom, height = 0.15, 0.55
    spacing = 0.03

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom + height + spacing, width, 0.2]
    rect_histy = [left + width + spacing, bottom, 0.2, height]
################################################################################
# GENERATE THE LINEAR SCALE PLOT
    lin_fig = plt.figure(figsize=(10, 10))

    ax = lin_fig.add_axes(rect_scatter)
    ax_histx = lin_fig.add_axes(rect_histx, sharex=ax)
    ax_histy = lin_fig.add_axes(rect_histy, sharey=ax)
    cax = lin_fig.add_axes([0.2, 0.08, 0.45, 0.01])

    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histy.tick_params(axis="y", labelleft=False)
    #['viridis', 'plasma', 'inferno', 'magma']
    binedges = np.linspace(-nbins/2,nbins/2,nbins+1)
    h2, xedges, yedges, im= ax.hist2d(x,y,bins=binedges,cmap='inferno')
    cb = lin_fig.colorbar(im,cax=cax,orientation='horizontal')
    ax.set_xlim((-nbins/2,nbins/2))
    ax.set_ylim((-nbins/2,nbins/2))
    #ARROWS FOR CUPID COORDINATES
    ArrSize = nbins/20
    ArrLoc = 39/100
    ZeroLoc = ArrLoc*nbins
    LabLoc = ZeroLoc-ArrSize-ArrSize/5
    ax.arrow(ZeroLoc,-ZeroLoc,0,ArrSize,color = 'r')
    ax.text(ZeroLoc,-LabLoc, 'CuPID +X',color='r',fontsize='small',horizontalalignment='center')
    ax.arrow(ZeroLoc,-ZeroLoc,-ArrSize,0,color = 'r')
    ax.text(LabLoc,-ZeroLoc, 'CuPID +Y',color='r',rotation = 90,fontsize='small',horizontalalignment='center', )
    ax.set_xlabel('X Position Bin')
    ax.set_ylabel('Y Position Bin')
    ax.set_title('2D Histogram of MCP')
    cb.set_label('Counts (total)')
    ax.axvline(0,color="r",alpha=0.5)
    ax.axhline(0,color="b",alpha=0.5)

    fmax = np.amax(h2)
    indfmax = np.where(h2 == fmax)
    hmax = fmax/2
    minmatrix = abs(h2-hmax)
    indhmax = np.where(minmatrix == np.amin(minmatrix))

    ax_histx.hist(XCenter, bins=binedges,color='b')#the X axis histogram at y = .5
    ax_histx.set_title('1D Histogram at Y = 1/2')
    ax_histx.set_ylabel('Counts (total)')
    ax_histy.hist(YCenter, bins=binedges, orientation='horizontal',color='r')
    ax_histy.set_title('1D Histogram at X = 1/2')
    ax_histy.set_xlabel('Counts (total)')
    lowstring = 'Low: '
    highstring = 'High: '
    BinNumber = '#Bins = '
    lin_fig.text(0.83, 0.9, 'CuPID X-ray', fontsize=16, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.87, 'Experiment:', fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.85, filename, fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.83,  lowstring+ (str(lo_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.81,  highstring+ (str(hi_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.text(0.83, 0.79,  BinNumber+(str(nbins)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    lin_fig.savefig(filename+'_linscale_corrected_'+str(nbins)+'bins.png')
    plt.close()
################################################################################
# GENERATE THE LOG SCALE PLOT
    log_fig = plt.figure(figsize=(10, 10))

    ax = log_fig.add_axes(rect_scatter)
    ax_histx = log_fig.add_axes(rect_histx, sharex=ax)
    ax_histy = log_fig.add_axes(rect_histy, sharey=ax)
    cax = log_fig.add_axes([0.2, 0.08, 0.45, 0.01])

    ax_histx.tick_params(axis="x", labelbottom=False)
    ax_histy.tick_params(axis="y", labelleft=False)
    #['viridis', 'plasma', 'inferno', 'magma']
    binedges = np.linspace(-nbins/2,nbins/2,nbins+1)
    h2, xedges, yedges, im= ax.hist2d(x,y,bins=binedges,cmap='inferno',norm=LogNorm(vmin=1,vmax=10*(1+np.floor(np.amax(h2)/10))))
    cb = log_fig.colorbar(im,cax=cax,orientation='horizontal')
    ax.set_xlim((-nbins/2,nbins/2))
    ax.set_ylim((-nbins/2,nbins/2))
    #ARROWS FOR CUPID COORDINATES
    ArrSize = nbins/20
    ArrLoc = 39/100
    ZeroLoc = ArrLoc*nbins
    LabLoc = ZeroLoc-ArrSize-ArrSize/5
    ax.arrow(ZeroLoc,-ZeroLoc,0,ArrSize,color = 'r')
    ax.text(ZeroLoc,-LabLoc, 'CuPID +X',color='r',fontsize='small',horizontalalignment='center')
    ax.arrow(ZeroLoc,-ZeroLoc,-ArrSize,0,color = 'r')
    ax.text(LabLoc,-ZeroLoc, 'CuPID +Y',color='r',rotation = 90,fontsize='small',horizontalalignment='center', )
    ax.set_xlabel('X Position Bin')
    ax.set_ylabel('Y Position Bin')
    ax.set_title('2D Histogram of MCP')
    cb.set_label('Counts (total)')
    ax.axvline(0,color="r",alpha=0.5)
    ax.axhline(0,color="b",alpha=0.5)

    fmax = np.amax(h2)
    indfmax = np.where(h2 == fmax)
    hmax = fmax/2
    minmatrix = abs(h2-hmax)
    indhmax = np.where(minmatrix == np.amin(minmatrix))

    ax_histx.hist(XCenter, bins=binedges,color='b')#the X axis histogram at y = .5
    ax_histx.set_yscale('log')
    ax_histx.set_title('1D Histogram at Y = 1/2')
    ax_histx.set_ylabel('Counts (total)')
    ax_histy.hist(YCenter, bins=binedges, orientation='horizontal',color='r')
    ax_histy.set_xscale('log')
    ax_histy.set_title('1D Histogram at X = 1/2')
    ax_histy.set_xlabel('Counts (total)')
    lowstring = 'Low: '
    highstring = 'High: '
    BinNumber = '#Bins = '
    log_fig.text(0.83, 0.9, 'CuPID X-ray', fontsize=16, horizontalalignment='center',verticalalignment='center')
    log_fig.text(0.83, 0.87, 'Experiment:', fontsize=12, horizontalalignment='center',verticalalignment='center')
    log_fig.text(0.83, 0.85, filename, fontsize=12, horizontalalignment='center',verticalalignment='center')
    log_fig.text(0.83, 0.83,  lowstring+ (str(lo_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    log_fig.text(0.83, 0.81,  highstring+ (str(hi_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    log_fig.text(0.83, 0.79,  BinNumber+(str(nbins)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    log_fig.savefig(filename+'_logscale_corrected_'+str(nbins)+'bins.png')
    plt.close()

def plot_xrfs(filename):
    xrfs_data = be.read_xrfs(filename)
    times = np.transpose([d.time for d in xrfs_data])
    x = np.transpose([d.x for d in xrfs_data])/50000.
    y = np.transpose([d.y for d in xrfs_data])/50000.
    print("xmax = " + str(np.amax(x)) + " , y = " + str(np.amax(y)))
    nbins = 100

    binedges = np.linspace(0,1,nbins+1)
    h,xedges,yedges,im = plt.hist2d(x,y,bins=binedges)
    cb = plt.colorbar(im)
    cb.set_label('Counts (total)')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.xlim([0,1])
    plt.ylim([0,1])
    plt.suptitle('XRFS valid counts generated ' + dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' from ' + filename)
    plt.savefig(filename+'_linhist.jpg')
    plt.close()

    binedges = np.linspace(0,1,101)
    h,xedges,yedges,im = plt.hist2d(x,y,bins=binedges,norm=LogNorm(vmin=1,vmax=10*(1+np.floor(np.amax(h)/10))))
    cb = plt.colorbar(im)
    cb.set_label('Counts (total)')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.xlim([0,1])
    plt.ylim([0,1])
    plt.suptitle('XRFS valid counts generated ' + dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' from ' + filename)
    plt.savefig(filename+'_loghist.jpg')
    plt.close()

def burst_plot(start_date, minutes, data_path = '../../../L2a/', cr_cadence = 1, pdf = False):
    """
    Combined x-ray countrate, x-ray position, two-channel dosi countrate, mags magnetometer plot
    utility.

    ### Parameters

    * start_date : string
        >String start date in YYYYMMDDHHMM format.
    * minutes : int
        >Duration of plot in minutes.
    * data_path : string, optional
        >String path to L2a data directory. The default is '../../../L2a/'.
    * cr_cadence : int, optionalo
        >Seconds over which to calculate x-ray countrate. The default is 1.
    * pdf : bool, optional
        >If true, writes a pdf version of plot in addition to the png version. The default is False.

    ### Returns

    * None.

    """
    start_time = dt.datetime.strptime(start_date, '%Y%m%d%H%M') #Grab time range in datetime
    stop_time = start_time + dt.timedelta(minutes = minutes)
    start_time = pytz.utc.localize(start_time)
    stop_time = pytz.utc.localize(stop_time)
    #Generate the strings that will be used to reference the data files (15 minute and daily)
    if (start_date[10:12] == '00')|(start_date[10:12] == '15')|(start_date[10:12] == '30')|(start_date[10:12] == '45'):
        minstr = start_date #This happens if we only need to load one file (i.e. falls perfectly on a 15 minute time range)
    else: #And these happen if we have to load two files, i.e. if we're overlapping two time ranges
        if (int(start_date[10:12])//15 == 0):
            minstr=[start_date[:10]+'00',start_date[:10]+'15']
        if(int(start_date[10:12])//15 == 1):
            minstr=[start_date[:10]+'15',start_date[:10]+'30']
        if(int(start_date[10:12])//15 == 2):
            minstr=[start_date[:10]+'30',start_date[:10]+'45']
        if(int(start_date[10:12])//15 == 3):
            date1 = dt.datetime(start_time.year, start_time.month,start_time.day,start_time.hour,45)
            date2 = date1+dt.timedelta(minutes=15)
            minstr=[date1.strftime('%Y%m%d%H%M'),date1.strftime('%Y%m%d%H%M')]
    date1 = dt.datetime(start_time.year, start_time.month,start_time.day)
    date2 = dt.datetime(stop_time.year, stop_time.month,stop_time.day)
    daystr = np.unique([date1.strftime('%Y%m%d'),date2.strftime('%Y%m%d')]) #Same as above if statements but for days (easier)
    
    home_dir = os.getcwd()
    os.chdir(data_path) #Step into 2a directory
    os.chdir('xrfs')
    xrfs=[]
    for string in minstr:
        try:
            xrfs = np.concatenate((xrfs, np.loadtxt(string+'_xrfs_2a.csv',delimiter = ',')),axis=0) #load in all the xrfs we need
        except OSError:
            continue
    os.chdir('../dsfs')
    dsfs_ARate = []
    dsfs_BRate = []
    for string in minstr:
        try:
            dsfs_ARate = np.concatenate((dsfs_ARate, np.loadtxt(string+'_dsfs_ARate_2a.csv',delimiter = ',')),axis=0) #load in all the dsfs we need
            dsfs_BRate = np.concatenate((dsfs_BRate, np.loadtxt(string+'_dsfs_BRate_2a.csv',delimiter = ',')),axis=0)
        except OSError:
            continue
    
    os.chdir('../mags')
    mags = []
    for string in daystr:
        try:
            mags = np.concatenate((mags, np.loadtxt(string+'_mags_2a.csv',delimiter = ',')),axis=0) #load in all the mags we need
        except OSError:
            continue
    os.chdir(home_dir)
    #Calculate X-Ray Countrate
    cr_arr = np.zeros(int(stop_time.timestamp()-start_time.timestamp())//cr_cadence)
    cr_times = np.arange(start_time.timestamp(),stop_time.timestamp(),cr_cadence)
    xr_times = xrfs[:,0]
    for i in np.arange(len(cr_arr)):
        cr_arr[i] = len(xr_times[(xr_times < start_time.timestamp()+i*cr_cadence)&(xr_times > start_time.timestamp()+(i-1)*cr_cadence)])/cr_cadence
    
    fig_l, axes_l = plt.subplots(nrows=4, ncols=1, sharex=True)
    fig_l.subplots_adjust(hspace=0)
    
    for i in np.arange(0,4):
            if i == 0:
                axes_l[i].plot(cr_times,cr_arr,color=red)
                axes_l[i].set_ylabel(r'$CR_{XRFS}$')
                title = 'CuPID Burst '+start_time.strftime('%b %d, %Y')+' ('+str(minutes)+' minutes)'
                axes_l[i].set_title(title)
            if i == 1:
                axes_l[i].plot(cr_times,np.zeros(len(cr_arr)),color=black)
                axes_l[i].set_ylabel(r'$BG$')
                axes_l[i].set_yticks([0])
            if i == 2:
                if (len(dsfs_ARate) != 0) & (len(dsfs_BRate) != 0):
                    axes_l[i].plot(dsfs_ARate[:,0],dsfs_ARate[:,1],color=red)
                    axes_l[i].plot(dsfs_BRate[:,0],dsfs_BRate[:,1],color=blue)
                    axes_l[i].legend(['A','B'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
                axes_l[i].set_ylabel(r'$CR_{DSFS}$')
            if i == 3:
                if (len(mags) != 0):
                    axes_l[i].plot(mags[:,0],mags[:,1],color=red)
                    axes_l[i].plot(mags[:,0],mags[:,2],color=blue)
                    axes_l[i].plot(mags[:,0],mags[:,3],color=green)
                    axes_l[i].legend(['X','Y','Z'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
                axes_l[i].set_ylabel('B')
    axes_l[-1].set_xlabel('UTC (HH:MM:SS)')
    axes_l[-1].set_xlim(start_time.timestamp(),stop_time.timestamp())
    axes_l[-1].set_xticks(np.linspace(start_time.timestamp(),stop_time.timestamp(),4))
    ticktimes = [dt.datetime.fromtimestamp(stamp, tz=dt.timezone.utc) for stamp in np.linspace(start_time.timestamp(),stop_time.timestamp(),4)]
    labels = [date.strftime('%H:%M:%S') for date in ticktimes]
    axes_l[-1].set_xticklabels(labels)
    
    #Make a histogram to the right of the plot with the same size as the 4 bars
    h = np.sum([ax.get_position().height for ax in axes_l])
    axes_r = plt.axes([axes_l[-1].get_position().x0+1.3*axes_l[-1].get_position().width,axes_l[-1].get_position().y0,axes_l[-1].get_position().width,h])
    axes_cb = plt.axes([axes_r.get_position().x0+axes_r.get_position().width,axes_r.get_position().y0,0.02,axes_r.get_position().height])
    bin_width = 0.5 #width of bins in degrees
    RA_bins = np.arange(int(np.min(xrfs[:,1])),int(np.max(xrfs[:,1])),bin_width)
    Dec_bins = np.arange(int(np.min(xrfs[:,2])),int(np.max(xrfs[:,2])),bin_width)
    h2, RA_edges, Dec_edges, image = axes_r.hist2d(xrfs[:,1],xrfs[:,2],bins=[RA_bins,Dec_bins], cmap='inferno')
    cbar = fig_l.colorbar(image,cax=axes_cb,orientation='vertical')
    axes_r.set_xlabel('RA [deg]')
    axes_r.set_ylabel('Dec [deg]')
    cbar.set_label('Counts')
    
    plot_name = 'burst_{date}_{mins}mins'.format(date=start_date,mins=str(minutes))
    if pdf:
        plt.savefig(plot_name+'.pdf', bbox_inches='tight')
    plt.savefig(plot_name+'.png', bbox_inches='tight')
    plt.close()

def plot_dsfs(filename):
    dosidata = be.read_dsfs(filename)
    times = [d.pkt_count for d in dosidata]
    amed = [d.dosa_med for d in dosidata]
    alow = [d.dosa_low[0] for d in dosidata]
    five = [d.five_mon for d in dosidata]
    threethree = [d.three_mon for d in dosidata]
    tmon = [d.t_mon for d in dosidata]
    tmon2 = [(i * -0.7798)+100.81 for i in tmon]

    bmed = [d.dosb_med for d in dosidata]
    blow = [d.dosb_low[0] for d in dosidata]

    Label1 = 'DosA Low'
    Label2 = 'DosA Med'
    Label3 = 'DosB Low'
    Label4 = 'DosB Med'
    Label5 = 'DosA Rate'
    Label6 = 'DosB Rate'
    Label7 = 'Dosi Temp'
    Label8 = '5V Monitor'
    Label9 = '3.3V Monitor'

    LegendLabs = ('Dosi A', 'Dosi B','5V Monitor', '3.3V Monitor', 'Dosi Temp')

    fig1 = plt.figure()
    fig1.set_size_inches(8,10)
    ax1=fig1.add_subplot(311, label="1")
    ax2=fig1.add_subplot(312, label="2")
    ax3=fig1.add_subplot(313, label="3")

    A, = ax1.plot(times,[i*0.0196 for i in alow], 'r', Linewidth = 2, label=Label1)
    B, = ax1.plot(times,[i*0.0196 for i in blow], 'b', Linewidth = 2, label=Label3)
    ax1.set_ylabel('Voltage out [V]')
    ax1.set_title('Low Count Voltage')
    ax1.set_xticklabels([])
    ax1.set_xlim([np.min(times),np.max(times)])
    ax1.grid(True)

    ax2.plot(times,[i*0.0196 for i in amed], 'r-', Linewidth = 2, label=Label2)
    ax2.plot(times,[i*0.0196 for i in bmed], 'b-', Linewidth = 2, label=Label4)
    ax2.set_ylabel('Voltage out [V]')
    ax2.set_title('Medium Count Voltage')
    ax2.set_xlim([0,len(times)/10])
    ax2.set_xticklabels([])
    ax2.grid(True)

    # ax3.plot(Time,A_rate, 'r', Linewidth = 2, label=Label5)
    # ax3.plot(Time,B_rate, 'b', Linewidth = 2, label=Label6)
    # ax3.set_ylabel('Count Rate [C/s]')
    # ax3.set_title('Count Rate')
    # ax3.set_xlim([0,len(Time)/10])
    # ax3.set_xticklabels([])
    # ax3.grid(True)

    FiveLn, = ax3.plot(times,[i*0.0196*2 for i in five], 'k', Linewidth = 2, linestyle='dashed', label=Label8)
    ThreeLn, = ax3.plot(times,[i*0.0196 for i in threethree], 'k', Linewidth = 2, label=Label9)
    ax3R = ax3.twinx()
    TempLn, = ax3R.plot(times,tmon2, 'g', Linewidth = 2, label=Label7)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Voltage [V]')
    ax3.set_title('Voltage and Temp Monitor')
    ax3.set_ylim([2,6])
    ax3.set_xlim([0,len(times)/10])
    degree_sign= u'\N{DEGREE SIGN}'
    ax3R.set_ylabel('Dosi Temp ['+degree_sign+'C]', color = 'green')
    ax3R.tick_params(axis='y', labelcolor='green')
    ax3R.set_ylim([0,70])

    Title = fig1.suptitle('Dosimeter Test Data ', fontsize = 'xx-large')
    Title.set_y(0.94)
    plt.legend((A,B,FiveLn, ThreeLn, TempLn), LegendLabs, bbox_to_anchor=(1.02, -0.26), ncol = 5)
    plt.grid(True)
    plt.savefig(filename+'_DosimeterPlot.png',bbox_inches=None, pad_inches=0.3)

def plot_cxdh(filename):
    cxdhdata = be.read_cxdh(filename)
    times = np.transpose([(d.time_payld) for d in cxdhdata])
    datatimes = np.linspace(times[0],times[-1],times.size*6)
    therms = np.transpose([d.thermistors[:] for d in cxdhdata])
    p_x = np.transpose(d.p_x for d in cxdhdata)
    p_y = np.transpose(d.p_y for d in cxdhdata)
    p_z = np.transpose(d.p_z for d in cxdhdata)
    #p_r = np.sqrt(p_x*p_x + p_y*p_y + p_z*p_z)
    counts = [d.counts_xray[:] for d in cxdhdata]
    counts = np.concatenate(counts)
    filter = np.where(counts>0)[0]
    counts_filt = counts[filter]
    times_xray = np.repeat(times - times[0],6)
    times_filt = times_xray[filter]
    dosi_shape = np.size([d.dosa_low for d in cxdhdata])

    dosa_low = np.reshape([d.dosa_low[:] for d in cxdhdata],newshape=dosi_shape,order='C')
    dosa_med = np.reshape([d.dosa_med[:] for d in cxdhdata],newshape=dosi_shape,order='C')
    dosb_low = np.reshape([d.dosb_low[:] for d in cxdhdata],newshape=dosi_shape,order='C')
    dosb_med = np.reshape([d.dosb_med[:] for d in cxdhdata],newshape=dosi_shape,order='C')

    dositimes = datatimes - times[0]

    f, (ax0,ax1,ax2,ax3) = plt.subplots(4,1,sharex=True)
    f.subplots_adjust(hspace=0)
    f.suptitle('CXDS plot generated ' + dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' from ' + filename)
    ax0.plot(times_filt,counts_filt)
    ax1.plot(dositimes[filter],dosa_low[filter],'r',label='DosALow')
    ax1.plot(dositimes[filter],dosa_med[filter],'b',label='DosAMed')
    ax2.plot(dositimes[filter],dosb_low[filter],'r',label='DosBLow')
    ax2.plot(dositimes[filter],dosb_med[filter],'b',label='DosBMed')

    for i in range(10):
        templabel = 'T'+str(i)
        tmpplot,  = ax3.plot(times-times[0],therms[i,:])
        tmpplot.set_label(templabel)


    ax0.set_xlim([0,10*np.ceil((datatimes[-1] - times[0])/10)])
    ax0.set_ylabel('Valid X-Rays')
    ax1.legend()
    ax1.set_ylabel('Dosimeter A')
    ax2.legend()
    ax2.set_ylabel('Dosimeter B')
    ax0.set_ylim(0,65535)
    ax2.set_ylim(0,255)
    ax1.set_ylim(0,255)
    ax3.set_ylim(0,255)
    ax3.set_ylabel('Temperatures')
    ax3.legend(ncol=5,fontsize='small')
    plt.savefig(filename+'_survey.png')

def summary_plot(start_date, hours, HK = False, data_path = '../../L2a', pdf=False):
    '''
    Plotting function to create a summary plot of given length and start time.
    Uses processed L2a CXDH data.
    Planned functionality: passing list of keywords to determine contents of
    plots.

    ### Parameters

    * start_date : str
        >YYYYMMDDHHMM string for plot start date.
    
    * hours : int
        >Duration of plot in hours.  
    
    * HK : bool, optional
        >Include housekeeping data (to make Data Acquision Plots). The default is False.
        
    * data_path : str, optional
        >String path to L2a data. The default is '../../L2a'.
        
    * pdf : bool, optional
        >If true, writes a pdf version of plot in addition to the png version. The default is False.

    ### Returns

    * None.

    '''

    start_time = dt.datetime.strptime(start_date, '%Y%m%d%H%M')
    stop_time = start_time + dt.timedelta(hours=hours)
    home_dir = os.getcwd()
    os.chdir(data_path+'/cxdh')
    cxdh = np.asarray([])
    try:
        cxdh = np.loadtxt(start_time.strftime('%Y%m%d')+'_cxdh_2a.csv', delimiter=',')
    except OSError:
        os.chdir(home_dir)
        return
    for i in np.arange((stop_time-start_time).days):
        try:
            cxdh = np.concatenate((cxdh,np.loadtxt((start_time+dt.timedelta(days=int(i))).strftime('%Y%m%d')+'_cxdh_2a.csv', delimiter=',')),axis=0)
        except OSError:
            os.chdir(home_dir)
            return
            
    #Initialize empty arrays to read data into
    time = np.zeros(len(cxdh),dtype=dt.datetime)
    time_exp = np.zeros(len(cxdh)*6,dtype=dt.datetime)
    xrbr_log = np.zeros(len(cxdh))
    xrfs_log = np.zeros(len(cxdh))
    dsfs_log = np.zeros(len(cxdh))
    mags_log = np.zeros(len(cxdh))
    therm = np.zeros((len(cxdh),14))
    batt_v = np.zeros(len(cxdh))
    pos_GSE = np.zeros((len(cxdh),3))
    mlat = np.zeros(len(cxdh))
    mlong = np.zeros(len(cxdh))
    b_field = np.zeros((len(cxdh),3))
    xray_cnt = np.zeros(len(cxdh)*6)
    dosi_cnt = np.zeros((len(cxdh)*6,2)) #0 is a, 1 is b on second index
    
    #Read in CXDH data
    for i in np.arange(len(cxdh)):
        time[i] = dt.datetime.utcfromtimestamp(cxdh[i,2]) #Assume it comes as UNIX time
        xrbr_log[i] = cxdh[i,3]
        xrfs_log[i] = cxdh[i,4]
        dsfs_log[i] = cxdh[i,5]
        mags_log[i] = cxdh[i,29]
        therm[i,:] = cxdh[i,7:21] #temps in degrees C
        batt_v[i] = cxdh[i,21]
        pos_GSE[i,:] = [cxdh[i,30],cxdh[i,31],cxdh[i,32]] #Position in GSE (Re)
        b_field[i,:] = [32 * g_mag[0]*(cxdh[i,33] - o_mag[0]),32 * g_mag[1]*(cxdh[i,34] - o_mag[1]),32 * g_mag[2]*(cxdh[i,35] - o_mag[2])]
        for j in np.arange(6):
            time_exp[6*i+j] = time[i]+ dt.timedelta(seconds=(j / 8640)) #Inferred 10s cadence
            xray_cnt[6*i+j] = cxdh[i,40+j]
            if (j==0):
                if (i==0):
                    dosi_cnt[0,:] = [0,0]
                else:
                    dosi_cnt[6*i+j,:] = [(cxdh[i,46+j] + 256 * cxdh[i,52+j] - cxdh[i-1,51] - 256 * cxdh[i-1,57])/10, (cxdh[i,58+j] + 256 * cxdh[i,64+j] - cxdh[i-1,63] - 256 * cxdh[i-1,69])/10]
            else:
                dosi_cnt[6*i+j,:] = [(cxdh[i,46+j] + 256 * cxdh[i,52+j] - cxdh[i,46+j-1] - 256 * cxdh[i,52+j-1])/10, (cxdh[i,58+j] + 256 * cxdh[i,64+j] - cxdh[i,58+j-1] - 256 * cxdh[i,64+j-1])/10]

        #COORDINATE CONVERSIONS
        pos = Coords(pos_GSE[i,:], 'GSE', 'car', units = ['Re','Re','Re'], ticks = Ticktock(adacs_time[i],'UTC'))
        pos_MAG = pos.convert('MAG','sph')
        mlat[i] = pos_MAG.lati
        mlong[i] = pos_MAG.long
    time_mask = ((time >= start_time)&(time <= stop_time))
    time_exp_mask = ((time_exp >= start_time)&(time_exp <= stop_time))
    time = time[time_mask]
    time_exp = time_exp[time_mask]
    xrbr_log = xrbr_log[time_mask]
    xrfs_log = xrfs_log[time_mask]
    dsfs_log = dsfs_log[time_mask]
    mags_log = mags_log[time_mask]
    therm = therm[time_mask]
    batt_v = batt_v[time_mask]
    pos_GSE = pos_GSE[time_mask]
    mlat = mlat[time_mask]
    mlong = mlong[time_mask]
    b_field = b_field[time_mask]
    xray_cnt = xray_cnt[time_exp_mask]
    dosi_cnt = dosi_cnt[time_exp_mask]
    
    #INITIALIZE FIGURE
    rows = 7 if HK else 5
    fig, axes = plt.subplots(nrows=rows, ncols=1, sharex=True)
    fig.subplots_adjust(hspace=0)
    
    for i in np.arange(0,rows):
        if i == 0:
            axes[i].plot(time_exp,xray_cnt,color=black)
            axes[i].set_ylabel(r'$CR_{XRAY}$')
            title = 'DAP '+start_date+' '+str(hours)+' hours' if HK else 'Summary '+start_date+' '+str(hours)+' hours'
            axes[i].set_title(title)
            bottom,top = axes[i].get_ylim()
            y1 = (top-bottom)*0.2 + bottom
            y2 = (top-bottom)*0.8 + bottom
            axes[i].text(start_date+dt.timedelta(seconds=360),y1,xrbr_log[0],color=red)
            axes[i].text(start_date+dt.timedelta(seconds=360),y2,xrfs_log[0],color=blue)
            for j in np.arange(1,len(time)):
                if (xrbr_log[j]!=xrbr_log[j-1]):
                    axes[i].vline(x=time[j],color=red,alpha=0.5)
                    axes[i].text(time[j]+dt.timedelta(seconds=360),y1,xrbr_log[j],color=red)
                if (xrfs_log[j]!=xrfs_log[j-1]):
                    axes[i].vline(x=time[j],color=blue,alpha=0.5)
                    axes[i].text(time[j]+dt.timedelta(seconds=360),y2,xrfs_log[j],color=blue)
        if i == 1:
            axes[i].plot(time_exp,dosi_cnt[:,0],color=red)
            axes[i].plot(time_exp,dosi_cnt[:,1],color=blue)
            axes[i].legend(['A','B'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
            axes[i].set_ylabel(r'$CR_{DSFS}$')
            bottom,top = axes[i].get_ylim()
            y = (top-bottom)*0.8 + bottom
            axes[i].text(start_date+dt.timedelta(seconds=360),y,dsfs_log[0],color=black)
            for j in np.arange(1,len(time)):
                if (dsfs_log[j]!=dsfs_log[j-1]):
                    axes[i].vline(x=time[j],color=black,alpha=0.5)
                    axes[i].text(time[j]+dt.timedelta(seconds=360),y,dsfs_log[j],color=black)
        if i == 2:
            axes[i].plot(time,b_field[:,0],color=red)
            axes[i].plot(time,b_field[:,1],color=blue)
            axes[i].plot(time,b_field[:,2],color=green)
            axes[i].legend(['X','Y','Z'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
            axes[i].set_ylabel('B')
            bottom,top = axes[i].get_ylim()
            y = (top-bottom)*0.8 + bottom
            axes[i].text(start_date+dt.timedelta(seconds=360),y,mags_log[0],color=black)
            for j in np.arange(1,len(time)):
                if (mags_log[j]!=mags_log[j-1]):
                    axes[i].vline(x=time[j],color=black,alpha=0.5)
                    axes[i].text(time[j]+dt.timedelta(seconds=360),y,mags_log[j],color=black)
        if i == 3:
            axes[i].plot(time,mlat,color=black)
            axes[i].hlines([60,90],start_time,stop_time,colors = red, linestyles='dashed',alpha = 0.3)
            axes[i].set_ylabel('MLAT')
        if i == 4:
            axes[i].plot(time,mlong,color=black)
            axes[i].set_ylabel('MLONG')
        if i == 5:
            axes[i].plot(time,batt_v,color=black)
            axes[i].set_ylabel(r'$V_{batt}$')
        if i == 6:
            axes[i].plot(time,therm[:,13],color=black)
            axes[i].set_ylabel(r'$T_{board}$')
            axes[i].set_ylim(-150,150)
            axes[i].hlines([100,-100],start_time,stop_time,colors = red, linestyles='dashed',alpha = 0.3)
    axes[-1].set_xlabel('Time (UTC)')
    axes[-1].set_xlim(start_time,stop_time)
    tick_locs = [start_time + i * (stop_time-start_time)/8 for i in np.arange(9)]
    axes[-1].set_xticks(tick_locs)
    ticktimes = [dt.datetime.fromtimestamp(stamp, tz=dt.timezone.utc) for stamp in np.linspace(start_time.timestamp(),stop_time.timestamp(),9)]
    labels = [date.strftime('%H%M') for date in ticktimes]
    axes[-1].set_xticklabels(labels)
    
    os.chdir(home_dir)
    plot_name = 'DAP_{date}_{hours}hours'.format(date=start_date,hours=str(hours)) if HK else 'summary_{date}_{hours}hours'.format(date=start_date,hours=str(hours))
    if pdf:
        plt.savefig(plot_name+'.pdf', bbox_inches='tight')
    plt.savefig(plot_name+'.png')
    plt.close()

def burst_plot(start_date, minutes, data_path = '../../../L2a/', cr_cadence = 1, pdf = False):
    """
    Combined x-ray countrate, x-ray position, two-channel dosi countrate, mags magnetometer plot
    utility.

    ### Parameters
    
    * start_date : string
        >String start date in YYYYMMDDHHMM format.
    * minutes : int
        >Duration of plot in minutes.
    * data_path : string, optional
        >String path to L2a data directory. The default is `'../../../L2a/'`.
    * cr_cadence : int, optionalo
        >Seconds over which to calculate x-ray countrate. The default is 1.
    * pdf : bool, optional
        >If `True`, writes a pdf version of plot in addition to the png version. The default is `False`.

    ### Returns

    * None.

    """
    start_time = dt.datetime.strptime(start_date, '%Y%m%d%H%M') #Grab time range in datetime
    stop_time = start_time + dt.timedelta(minutes = minutes)
    start_time = pytz.utc.localize(start_time)
    stop_time = pytz.utc.localize(stop_time)
    #Generate the strings that will be used to reference the data files (15 minute and daily)
    if (start_date[10:12] == '00')|(start_date[10:12] == '15')|(start_date[10:12] == '30')|(start_date[10:12] == '45'):
        minstr = start_date #This happens if we only need to load one file (i.e. falls perfectly on a 15 minute time range)
    else: #And these happen if we have to load two files, i.e. if we're overlapping two time ranges
        if (int(start_date[10:12])//15 == 0):
            minstr=[start_date[:10]+'00',start_date[:10]+'15']
        if(int(start_date[10:12])//15 == 1):
            minstr=[start_date[:10]+'15',start_date[:10]+'30']
        if(int(start_date[10:12])//15 == 2):
            minstr=[start_date[:10]+'30',start_date[:10]+'45']
        if(int(start_date[10:12])//15 == 3):
            date1 = dt.datetime(start_time.year, start_time.month,start_time.day,start_time.hour,45)
            date2 = date1+dt.timedelta(minutes=15)
            minstr=[date1.strftime('%Y%m%d%H%M'),date1.strftime('%Y%m%d%H%M')]
    date1 = dt.datetime(start_time.year, start_time.month,start_time.day)
    date2 = dt.datetime(stop_time.year, stop_time.month,stop_time.day)
    daystr = np.unique([date1.strftime('%Y%m%d'),date2.strftime('%Y%m%d')]) #Same as above if statements but for days (easier)
    
    home_dir = os.getcwd()
    os.chdir(data_path) #Step into 2a directory
    os.chdir('xrfs')
    xrfs=[]
    for string in minstr:
        try:
            xrfs = np.concatenate((xrfs, np.loadtxt(string+'_xrfs_2a.csv',delimiter = ',')),axis=0) #load in all the xrfs we need
        except OSError:
            continue
    os.chdir('../dsfs')
    dsfs_ARate = []
    dsfs_BRate = []
    for string in minstr:
        try:
            dsfs_ARate = np.concatenate((dsfs_ARate, np.loadtxt(string+'_dsfs_ARate_2a.csv',delimiter = ',')),axis=0) #load in all the dsfs we need
            dsfs_BRate = np.concatenate((dsfs_BRate, np.loadtxt(string+'_dsfs_BRate_2a.csv',delimiter = ',')),axis=0)
        except OSError:
            continue
    
    os.chdir('../mags')
    mags = []
    for string in daystr:
        try:
            mags = np.concatenate((mags, np.loadtxt(string+'_mags_2a.csv',delimiter = ',')),axis=0) #load in all the mags we need
        except OSError:
            continue
    os.chdir(home_dir)
    #Calculate X-Ray Countrate
    cr_arr = np.zeros(int(stop_time.timestamp()-start_time.timestamp())//cr_cadence)
    cr_times = np.arange(start_time.timestamp(),stop_time.timestamp(),cr_cadence)
    xr_times = xrfs[:,0]
    for i in np.arange(len(cr_arr)):
        cr_arr[i] = len(xr_times[(xr_times < start_time.timestamp()+i*cr_cadence)&(xr_times > start_time.timestamp()+(i-1)*cr_cadence)])/cr_cadence
    
    fig_l, axes_l = plt.subplots(nrows=4, ncols=1, sharex=True)
    fig_l.subplots_adjust(hspace=0)
    
    for i in np.arange(0,4):
            if i == 0:
                axes_l[i].plot(cr_times,cr_arr,color=red)
                axes_l[i].set_ylabel(r'$CR_{XRFS}$')
                title = 'CuPID Burst '+start_time.strftime('%b %d, %Y')+' ('+str(minutes)+' minutes)'
                axes_l[i].set_title(title)
            if i == 1:
                axes_l[i].plot(cr_times,np.zeros(len(cr_arr)),color=black)
                axes_l[i].set_ylabel(r'$BG$')
                axes_l[i].set_yticks([0])
            if i == 2:
                if (len(dsfs_ARate) != 0) & (len(dsfs_BRate) != 0):
                    axes_l[i].plot(dsfs_ARate[:,0],dsfs_ARate[:,1],color=red)
                    axes_l[i].plot(dsfs_BRate[:,0],dsfs_BRate[:,1],color=blue)
                    axes_l[i].legend(['A','B'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
                axes_l[i].set_ylabel(r'$CR_{DSFS}$')
            if i == 3:
                if (len(mags) != 0):
                    axes_l[i].plot(mags[:,0],mags[:,1],color=red)
                    axes_l[i].plot(mags[:,0],mags[:,2],color=blue)
                    axes_l[i].plot(mags[:,0],mags[:,3],color=green)
                    axes_l[i].legend(['X','Y','Z'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
                axes_l[i].set_ylabel('B')
    axes_l[-1].set_xlabel('UTC (HH:MM:SS)')
    axes_l[-1].set_xlim(start_time.timestamp(),stop_time.timestamp())
    axes_l[-1].set_xticks(np.linspace(start_time.timestamp(),stop_time.timestamp(),4))
    ticktimes = [dt.datetime.fromtimestamp(stamp, tz=dt.timezone.utc) for stamp in np.linspace(start_time.timestamp(),stop_time.timestamp(),4)]
    labels = [date.strftime('%H:%M:%S') for date in ticktimes]
    axes_l[-1].set_xticklabels(labels)
    
    #Make a histogram to the right of the plot with the same size as the 4 bars
    h = np.sum([ax.get_position().height for ax in axes_l])
    axes_r = plt.axes([axes_l[-1].get_position().x0+1.3*axes_l[-1].get_position().width,axes_l[-1].get_position().y0,axes_l[-1].get_position().width,h])
    axes_cb = plt.axes([axes_r.get_position().x0+axes_r.get_position().width,axes_r.get_position().y0,0.02,axes_r.get_position().height])
    bin_width = 0.5 #width of bins in degrees
    RA_bins = np.arange(int(np.min(xrfs[:,1])),int(np.max(xrfs[:,1])),bin_width)
    Dec_bins = np.arange(int(np.min(xrfs[:,2])),int(np.max(xrfs[:,2])),bin_width)
    h2, RA_edges, Dec_edges, image = axes_r.hist2d(xrfs[:,1],xrfs[:,2],bins=[RA_bins,Dec_bins], cmap='inferno')
    cbar = fig_l.colorbar(image,cax=axes_cb,orientation='vertical')
    axes_r.set_xlabel('RA [deg]')
    axes_r.set_ylabel('Dec [deg]')
    cbar.set_label('Counts')
    
    plot_name = 'burst_{date}_{mins}mins'.format(date=start_date,mins=str(minutes))
    if pdf:
        plt.savefig(plot_name+'.pdf', bbox_inches='tight')
    plt.savefig(plot_name+'.png', bbox_inches='tight')
    plt.close()
