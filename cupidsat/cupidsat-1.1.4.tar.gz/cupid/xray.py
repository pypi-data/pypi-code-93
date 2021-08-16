import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from . import backend as be

def data(trange=['2021-01-01/00:00','2021-01-02/00:00'], filename=None, lognumbers=[], level='1', logtype='XRFS', numpy=False):
    """
    Read x-ray telescope data from TFTP server or local file into `pandas` dataframe or numpy array.

    ### Parameters
    * trange : string array-like, optional
        >Time range of x-ray telescope data to download from the TFTP server. Format 'YYYY-MM-DD/HH:MM' in UTC.
        Default `['2021-01-01/00:00','2021-01-02/00:00']`.
    * filename : str, optional
        >Name of XRBR or XRFS logfile to read. Only specify if you have a local CuPID binary file you want to read.
        Overrides `trange` if specified. Default `None`.
    * lognumbers : int, array-like, optional
        >Lognumber(s) of XRBR or XRFS logfiles being read. Only specify if you have a local CuPID binary file you want to read and sync to UTC time.
        Default `[]`.
    * level : str, optional
        >Data processing level of x-ray telescope data to download. Only specify if data is to be downloaded. Options:
        >
        >     '1' : Level 1 data (time in onboard payload time, no background subtraction, no nonlinearity correction)
        >
        >     '2a': Level 2a data (time in UTC, no background subtraction, MCP nonlinearity correction)
        >
        >     '2b': Level 2b data (time in UTC, background subtraction, MCP nonlinearity correction)
        >
        >If time sync fails for manually processed file when level 2a/b specified, returned data uses the mission elapsed time of the telescope in seconds to tag photon arrivals.
        >Default `'2a'`.
    * logtype : str, optional
        >Whether to process/download x-ray burst ('XRBR') or x-ray fast survey ('XRFS') data. Only specify if you have a local CuPID binary file 
        you want to read *or* specified level one data in `level` argument. Default `'XRFS'`.
    * numpy : bool, optional
        >If `True`, returns numpy array of x-ray telescope data. If `False`, returns `pandas` DataFrame of x-ray telescope data. Default `False`.

    ### Returns
    * xray : float array-like
        >Dataframe (if not `numpy`) or numpy array (if `numpy`) of x-ray telescope data. Contents are as follows:
        >
        >Level 2a/b XRFS files have three contents: `['time_utc','RA','Dec']`. RA and Dec are right ascension and declination of each photon in degrees. time_utc is UNIX timestamp of photon arrival in UTC. 
        >
        >Level 1 XRFS files have three contents: `['time_payld','x','y']`. x and y are the x and y position of the photon on the MCP in voltage space. time_payld is the mission elapsed time of photon arrival in seconds.
        >
        >Level 2a/b XRBR files have five contents: `['time_utc','x0','x1','y0','y1']`. x0 and x1 are the x voltages on the anode board, and y0 and y1 are the y voltages on the anode board. time_utc is UNIX timestamp of photon arrival in UTC.
        >
        >Level 1 XRBR files have five contents: `['time_payld','x0','x1','y0','y1']`. x0 and x1 are the x voltages on the anode board, and y0 and y1 are the y voltages on the anode board. time_payld is the mission elapsed time of photon arrival in seconds.

    ### Examples
    Read in data from cusp encounter on January 3rd, 2022 from 12:30 to 13:00
    ```python
        from cupid import xray
        xraydata = xray.data(trange=['2022-01-03/12:30','2022-01-03/13:00'])
    ```
    Since we bring down every photon, we can bin photons when calculating countrate however we want. Let's look at the countrate in a 5 second cadence during this cusp encounter:
    ```python
        import numpy as np
        import matplotlib.pyplot as plt
        bins = np.arange(xraydata['time'][0],xraydata['time'][len(a)-1],5) #Five second wide bins covering the whole time range
        plt.hist(xraydata['time'],bins=bins)
    ```
    We can also define whatever resolution we want for our images (within reason, the lower limit is ~0.25 degrees) or even use creative binning schemes to extract information.
    Let's use large pixel widths in Dec and small pixel widths in RA to better illustrate the patches of reconnection in this event:
    ```python
        RAbins = np.arange(np.min(xraydata['RA']),np.max(xradatay['RA']),0.25) #1/4 degree bins in RA (resolution limit)
        Decbins = np.arange(np.min(xraydata['Dec']),np.max(xraydata['Dec']),4) #4 degree bins in Dec
        plt.hist2d(x=xraydata['RA'],y=xray['Dec'],bins=[RAbins,Decbins],cmap = 'inferno') #Make a 2d histogram using our bins
        plt.gca().set_aspect('equal') #Make the plot isotropic to avoid smearing
    ```
    This is great for making custom plots, but if you want to plot quickly and easily it may be better to use `cupid.xray.plot`.

    """
    if filename is None: #If filename is not specified
        if (logtype=='XRFS'):
            raise NameError("TFTP Download not implemented in current release. Please specify filename argument.")
        if (logtype=='XRBR'):
            raise NameError("TFTP Download not implemented in current release. Please specify filename argument.")
        else:
            raise NameError("Logtype must be either 'XRBR' or 'XRFS'")
    else: #You specified a filename to open
        if (logtype=='XRFS'):
            xray = be.read_xrfs(filename)
            if ((level == '1')|(level==1)):
                xray = be.makeL1(xray)
                xray = pd.DataFrame(xray,columns=['time_payld','x','y'])
            if ((level=='2a')|(level==2)):
                xray = be.makeL1(xray)
                xray = be.makeL2a(xray,lognumbers)
                xray = pd.DataFrame(xray,columns=['time_utc','RA','Dec'])
            if (level=='2b'):
                xray = be.makeL1(xray)
                xray = be.makeL2a(xray,lognumbers)
                print('Background subtraction not implemented in current release.')
                xray = pd.DataFrame(xray,columns=['time_utc','RA','Dec'])
            return(xray)
        elif (logtype=='XRBR'):
            xray = be.read_xrbr_sci(filename)
            if ((level == '1')|(level==1)):
                xray = be.makeL1(xray)
                xray = pd.DataFrame(xray,columns=['time_payld','x0','x1','y0','y1'])
            if ((level=='2a')|(level==2)):
                xray = be.makeL1(xray)
                xray = be.makeL2a(xray,lognumbers)
                xray = pd.DataFrame(xray,columns=['time_utc','x0','x1','y0','y1'])
            if (level=='2b'):
                xray = be.makeL1(xray)
                xray = be.makeL2a(xray,lognumbers)
                print('Background subtraction not implemented in current release.')
                xray = pd.DataFrame(xray,columns=['time_utc','x0','x1','y0','y1'])
            return(xray)
        else:
            raise NameError("Logtype must be either 'XRBR' or 'XRFS'")
            
def plot(trange=['2021-01-01/00:00','2021-01-02/00:00'], filename=None, lognumbers=[], xray=None, level='1', logtype='XRFS', correction=True,
        linscale=False, bins = None, equal=True, expansion=7.0, arrows=False, hist1D=True, bltext=True
        ):
    """
    Plot x-ray telescope data for given time range, file, or existing DataFrame.

    ### Parameters
    * trange : string array-like, optional
        >Time range of x-ray telescope data to download from the TFTP server. Format 'YYYY-MM-DD/HH:MM' in UTC.
        Default `['2021-01-01/00:00','2021-01-02/00:00']`.
    * filename : str
        >Name of XRBR or XRFS logfile to read. Only specify if you have a local CuPID binary file you want to read.
        Overrides `trange` if specified. Default `None`.
    * xray : DataFrame, optional
    * lognumbers : int, array-like, optional
        >Lognumber(s) of XRBR or XRFS logfiles being read. Only specify if you have a local CuPID binary file you want to read and sync to UTC time.
        Default `[]`.
    * level : str, optional
        >Data processing level of x-ray telescope data to download. Only specify if data is to be downloaded. Options:
        >
        >     '1' : Level 1 data (time in onboard payload time, no background subtraction, no nonlinearity correction)
        >
        >     '2a': Level 2a data (time in UTC, no background subtraction, MCP nonlinearity correction)
        >
        >     '2b': Level 2b data (time in UTC, background subtraction, MCP nonlinearity correction)
        >
        >If time sync fails for manually processed file when level 2a/b specified, returned data uses the mission elapsed time of the telescope in seconds to tag photon arrivals.
        >Default `'2a'`.
    * logtype : str, optional
        >Whether to process/download x-ray burst ('XRBR') or x-ray fast survey ('XRFS') data. Only specify if you have a local CuPID binary file 
        you want to read *or* specified level one data in `level` argument. Default `'XRFS'`.
    * correction : bool, optional
        >If `True`, applies nonlinearity correction to data. Default `True`.
    * linscale : bool, optional
        >If `True`, renders histogram in linear scale. If `False`, renders figure in log scale. Default `True`.
    * bins : None or int or [int, int] or array-like or [array, array], optional
        >The bins passed to matplotlib.pyplot.hist2d. The bin specification:
        >
        >     If int, the number of bins for the two dimensions (nx=ny=bins).
        >
        >
        >     If `[int, int]`, the number of bins in each dimension (nx, ny = bins).
        >
        >
        >     If array-like, the bin edges for the two dimensions (x_edges=y_edges=bins).
        >
        >
        >     If [array, array], the bin edges in each dimension (x_edges, y_edges = bins).
        >
        >Default is 0.25 degree wide bins in each axis when plotting L2a/b data, and 100 bins in each axis when plotting L1 data.
    * equal : bool, optional
        >If `True`, renders histogram isotropically (equal aspect ratio in x and y). If `False`, renders figure with matplotlib default, which can smear images. Default is `True`.
    * expansion : float, optional
        >Factor that data is expanded by when viewing raw MCP positions (only used when `level=1`). Can be thought of as a normalization factor. Default is `7.0`.
    * arrows : bool, optional
        >If `True`, renders CuPID orientation arrows on figure. Default `False`.
    * hist1D : bool, optional
        >If `True`, renders 1D marginal histograms for each axis. Default `True`.
    * bltext : bool, optional
        >If `True`, adds text useful for beamline experiments. If `False`, adds text useful for science on-orbit. Default `True` (CHANGE TO FALSE IN PRODUCTION RELEASE).

    ### Returns
    * xray : float array-like
        >Dataframe (if not `numpy`) or numpy array (if `numpy`) of x-ray telescope data. Contents are as follows:
        >
        >Level 2a/b XRFS files have three contents: `['time_utc','RA','Dec']`. RA and Dec are right ascension and declination of each photon in degrees. time_utc is UNIX timestamp of photon arrival in UTC. 
        >
        >Level 1 XRFS files have three contents: `['time_payld','x','y']`. x and y are the x and y position of the photon on the MCP in voltage space. time_payld is the mission elapsed time of photon arrival in seconds.
        >
        >Level 2a/b XRBR files have five contents: `['time_utc','x0','x1','y0','y1']`. x0 and x1 are the x voltages on the anode board, and y0 and y1 are the y voltages on the anode board. time_utc is UNIX timestamp of photon arrival in UTC.
        >
        >Level 1 XRBR files have five contents: `['time_payld','x0','x1','y0','y1']`. x0 and x1 are the x voltages on the anode board, and y0 and y1 are the y voltages on the anode board. time_payld is the mission elapsed time of photon arrival in seconds.
    * fig : matplotlib.pyplot.figure object
        >figure object in which the axes are rendered.

    ### Examples
    Plot x-ray data from cusp encounter on January 3rd, 2022 from 12:30 to 13:00.
    ```python
        from cupid import xray
        xray.plot(trange=['2022-01-03/12:30','2022-01-03/13:00'])
    ```
    If we want to make it use similar bins to the ones used in the `cupid.xray.data` example, we can specify the number of bins in each axis. Here we use plenty of RA bins and only a few Dec bins.
    ```python
        xray.plot(trange=['2022-01-03/12:30','2022-01-03/13:00'],bins=[100,5])
    ```
    If we have some calibration image we want to look at, we can specify a binary file by path.
    ```python
        xray.plot(filename='/calibration_images/xrbr_calibration',bltext=True)
    ```
    """
    if xray is None: #If you didnt't feed it a pandas DataFrame or numpy array of xray data
        xray = data(trange=trange,filename=filename,lognumbers=lognumbers,level=level,logtype=logtype)
    if bins is None:
        if (((level=='2a')|(level=='2b')|(level==2))&(logtype=='XRFS')):
            RAbins = np.arange(np.min(xraydata['RA']),np.max(xradatay['RA']),0.25) #1/4 degree bins in RA
            Decbins = np.arange(np.min(xraydata['Dec']),np.max(xraydata['Dec']),0.25) #1/4 degree bins in Dec
            bins = [RAbins,Decbins]
        else:
            bins = np.linspace(-1,1,100)
    if (logtype=='XRBR'):
        x0 = xray['x0'].to_numpy()
        x1 = xray['x1'].to_numpy()
        y0 = xray['y0'].to_numpy()
        y1 = xray['y1'].to_numpy()
        mask_x0 = np.where((x0 < be.hi_thold) & (x0 > be.lo_thold)) #Mask out voltages that are outside threshholds
        mask_x1 = np.where((x1 < be.hi_thold) & (x1 > be.lo_thold))
        mask_y0 = np.where((y0 < be.hi_thold) & (y0 > be.lo_thold))
        mask_y1 = np.where((y1 < be.hi_thold) & (y1 > be.lo_thold))
        mask_x = np.intersect1d(mask_x0,mask_x1)
        mask_y = np.intersect1d(mask_y0,mask_y1)
        pass_mask = np.intersect1d(mask_x,mask_y)
        x0p = (x0[pass_mask]) - be.offset #Remove voltage offsets
        x1p = (x1[pass_mask]) - be.offset
        y0p = (y0[pass_mask]) - be.offset
        y1p = (y1[pass_mask]) - be.offset
        x =(x0p/(x0p+x1p))-0.5 #Calculate MCP position
        y =(y0p/(y0p+y1p))-0.5
        if correction:
            x,y = be.nonlin_correction(x,y) #Apply nonlinearity correction
        x *= expansion #Apply normalization factor
        y *= expansion
    elif (logtype=='XRFS'):
        if ((level == '1')|(level==1)):
            x = xray['x'].to_numpy()
            y = xray['y'].to_numpy()
            if correction:
                x,y = be.nonlin_correction(x,y) #Apply nonlinearity correction
            x *= expansion #Apply normalization factor
            y *= expansion
        if ((level=='2a')|(level=='2b')|(level==2)):
            x = xray['RA'].to_numpy()
            y = xray['Dec'].to_numpy()
    else:
        raise NameError("Logtype must be either 'XRBR' or 'XRFS'")
    fig = plt.figure(figsize=(10, 10)) #Make the figure
    if linscale:
        h2, xedges, yedges, im= plt.hist2d(x,y,bins=bins,cmap=be.colormap) #Make the linear 2d histogram
    else:
        h2, xedges, yedges, im= plt.hist2d(x,y,bins=bins,cmap=be.colormap,norm=LogNorm()) #Make the log 2d histogram
    ax = plt.gca() #Get the axes of the histogram to put other stuff relative to it
    if equal:
        ax.set_aspect('equal')
    ax.set_title('2D Histogram')
    if (((level=='2a')|(level=='2b')|(level==2))&(logtype=='XRFS')):
        ax.set_xlabel('RA')
        ax.set_ylabel('Dec')
    else:
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
    hist_pos = ax.get_position()
    height = 0.03
    spacing = 0.08
    cax = fig.add_axes([hist_pos.x0,hist_pos.y0-spacing,hist_pos.width,height])
    cb = plt.colorbar(im,cax=cax,orientation='horizontal')
    cb.set_label('Counts (total)')
    if arrows: #Arrows for CuPID coordinates
        ArrSize = hist_pos.width/20.
        ArrLoc = 39./100.
        ZeroLoc = ArrLoc*nbins
        LabLoc = ZeroLoc-ArrSize-ArrSize/5
        ax.arrow(ZeroLoc,-ZeroLoc,0,ArrSize,color = be.green)
        ax.text(ZeroLoc,-LabLoc, 'CuPID +X',color=be.green,fontsize='small',horizontalalignment='center')
        ax.arrow(ZeroLoc,-ZeroLoc,-ArrSize,0,color = be.green)
        ax.text(LabLoc,-ZeroLoc, 'CuPID +Y',color=be.green,rotation = 90,fontsize='small',horizontalalignment='center', )
    if hist1D: #Add 1D hists to top and bottom
        height = 0.1
        spacing = 0.07
        if (((level=='2a')|(level=='2b')|(level==2))&(logtype=='XRFS')):
            xlabel = 'RA'
            ylabel = 'Dec'
        else:
            xlabel = 'X'
            ylabel = 'Y'
        ax_histx = fig.add_axes([hist_pos.x0,hist_pos.y0+hist_pos.height+spacing,hist_pos.width,height],sharex=ax)
        ax_histy = fig.add_axes([hist_pos.x0+hist_pos.width+spacing,hist_pos.y0,height,hist_pos.height])
        ax_histx.bar(xedges[:-1],np.sum(h2,axis=0),color=be.blue)
        ax_histx.set_title('1D Histogram over '+xlabel)
        ax_histx.set_ylabel('Counts (total)')
        ax_histy.barh(yedges[:-1],np.sum(h2,axis=1),color=be.red)
        ax_histy.set_title('1D Histogram over '+ylabel)
        ax_histy.set_xlabel('Counts (total)')
    x_spacing = 0.12
    y_spacing = 0.01
    text = 0.03
    text_x = hist_pos.x0+hist_pos.width+x_spacing
    text_y = hist_pos.x0+hist_pos.height+y_spacing
    if bltext:
        fig.text(text_x, text_y+6*text, 'CuPID X-ray', fontsize=16, horizontalalignment='center',verticalalignment='center')
        fig.text(text_x, text_y+5*text, 'Experiment:', fontsize=12, horizontalalignment='center',verticalalignment='center')
        fig.text(text_x, text_y+4*text, filename, fontsize=12, horizontalalignment='center',verticalalignment='center')
        fig.text(text_x, text_y+3*text,  'Low Threshold: '+ (str(lo_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
        fig.text(text_x, text_y+2*text,  'High Threshold: '+ (str(hi_thold)), fontsize=12, horizontalalignment='center',verticalalignment='center')
    else:
        fig.text(text_x, text_y+5*text, 'CuPID X-ray Image', fontsize=16, horizontalalignment='center',verticalalignment='center')
        fig.text(text_x, text_y+4*text, trange[0], fontsize=12, horizontalalignment='center',verticalalignment='center')
        fig.text(text_x, text_y+3*text, 'to', fontsize=12, horizontalalignment='center',verticalalignment='center')
        fig.text(text_x, text_y+2*text, trange[1], fontsize=12, horizontalalignment='center',verticalalignment='center')
    plt.show()
    return xray, fig