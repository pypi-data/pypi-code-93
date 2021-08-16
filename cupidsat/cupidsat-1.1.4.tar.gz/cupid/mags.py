import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from . import backend as be

mags_l1_cols = ['sync','time','bx00','bx01','bx02','bx03','bx04','bx05','bx06','bx07','bx08','bx09','bx10','bx11',
                'by00','by01','by02','by03','by04','by05','by06','by07','by08','by09','by10','by11',
                'bz00','bz01','bz02','bz03','bz04','bz05','bz06','bz07','bz08','bz09','bz10','bz11']

mags_l2_cols = ['sync','time_utc','bx00','bx01','bx02','bx03','bx04','bx05','bx06','bx07','bx08','bx09','bx10','bx11',
                'by00','by01','by02','by03','by04','by05','by06','by07','by08','by09','by10','by11',
                'bz00','bz01','bz02','bz03','bz04','bz05','bz06','bz07','bz08','bz09','bz10','bz11']

mags_l1_cols_lin = ['time','B_x','B_y','B_z']

mags_l2_cols_lin = ['time_utc','B_x','B_y','B_z']

def data(trange=['2021-01-01/00:00','2021-01-02/00:00'], filename=None, lognumbers=[], level='1', linear=True,numpy=False):
    """
    Read magnetometer data from TFTP server or local file into `pandas` dataframe or `numpy` array.

    ### Parameters
    * trange : string array-like, optional
        >Time range of magnetometer data to download from the TFTP server. Format 'YYYY-MM-DD/HH:MM' in UTC.
        Default `['2021-01-01/00:00','2021-01-02/00:00']`.
    * filename : str, optional
        >Name of MAGS logfile to read. Only specify if you have a local CuPID binary file you want to read.
        Overrides `trange` if specified. Default `None`.
    * lognumbers : int, array-like, optional
        >Lognumber(s) of MAGS logfiles being read. Only specify if you have a local CuPID binary file you want to read and sync to UTC time.
        Default `[]`.
    * level : str, optional
        >Data processing level of magnetometer data to download. Only specify if data is to be downloaded or you have paths to your own L2a CXDH data. Options:
        >
        >     '1' : Level 1 data (time in onboard payload time, no low-pass filter)
        >
        >     '2': Level 2 data (time in UTC, low-pass noise filter)
        >
        >If time sync fails for manually processed file when level 2 specified, returned data uses GPS time in seconds to tag magnetometer measurements.
        >Default `'2'`.
    * linear : bool, optional
        >If `True`, the returned array is unraveled into four columns, time and three magnetic field components (either CuPID x,y,z). Default `True`.
    * numpy : bool, optional
        >If `True`, returns numpy array of magnetometer data. If `False`, returns `pandas` DataFrame of magnetometer data. Default `False`.

    ### Returns
    * mags : float array-like
        >Dataframe (if not `numpy`) or numpy array (if `numpy`) of magnetometer data. If `linear`, the columns are 'time'/'time_utc' (GPS time or UTC time depending on data level), and 'B_x'/'B_y'/'B_z' which are magnetometer measurements in nT. If not `linear`, there are twelve entries for each channel per row, each 5s apart.

    ### Examples
    Read in data from field aligned current crossing on January 3rd, 2022 from 12:30 to 13:00, and unravel the data for convenience.
    ```python
        from cupid import mags
        from cupid import backend
        magsdata = mags.data(trange=['2022-01-03/12:30','2022-01-03/13:00'],linear=True)
    ```
    Plot the three magnetic field components during this event.
    ```python
        import matplotlib.pyplot as plt
        plt.plot(magsdata['time_utc'],magsdata['B_x'],color=backend.red)
        plt.plot(magsdata['time_utc'],magsdata['B_y'],color=backend.green)
        plt.plot(magsdata['time_utc'],magsdata['B_z'],color=backend.blue)
        plt.legend(['X','Y','Z'])
    ```
    This is great for making custom plots, but if you want to plot quickly and easily it may be better to use `cupid.mags.plot`.

    """
    if filename is None: #If filename is not specified
        raise NameError("TFTP Download not implemented in current release. Please specify filename argument.")
    else:
        mags = be.read_mags(filename)
        if ((level == '1')|(level==1)):
            mags = be.makeL1(mags)
            if linear:
                time = np.zeros(len(mags)*12)
                for i in range(len(time)):
                    time[i] = mags[i//12,1]+5*(i%12)
                temp = np.zeros((len(time),4))
                temp[:,0] = time
                temp[:,1] = mags[:,2:14].ravel()
                temp[:,2] = mags[:,14:26].ravel()
                temp[:,2] = mags[:,26:38].ravel()
                mags = temp
                mags = pd.DataFrame(mags,columns=mags_l1_cols_lin)
            else:
                mags = pd.DataFrame(mags,columns=mags_l1_cols)
        if ((level=='2a')|(level=='2b')|(level=='2')|(level==2)):
            mags = be.makeL1(mags)
            mags = be.makeL2a(mags,lognumbers)
            mags = pd.DataFrame(mags,columns=l2_cols)
            if linear:
                time = np.zeros(len(mags)*12)
                for i in range(len(time)):
                    time[i] = mags[i//12]+5*(i%12)
                mags = np.asarray([time,mags[:,2:14].ravel(),mags[:,14:26].ravel(),mags[:,26:38].ravel()])
                mags = pd.DataFrame(mags,columns=mags_l2_cols_lin)
            else:
                mags = pd.DataFrame(mags,columns=mags_l2_cols)
        if numpy:
            return mags.to_numpy()
        else:
            return mags

def plot(trange=['2021-01-01/00:00','2021-01-02/00:00'], filename=None, lognumbers=[], level='1', mags = None, title=None):
    """
    Plot magnetometer data for given time range, file, or existing DataFrame.

    ### Parameters
    * trange : string array-like, optional
        >Time range of magnetometer data to download from the TFTP server. Format 'YYYY-MM-DD/HH:MM' in UTC.
        Default `['2021-01-01/00:00','2021-01-02/00:00']`.
    * filename : str, optional
        >Name of MAGS logfile to read. Only specify if you have a local CuPID binary file you want to read.
        Overrides `trange` if specified. Default `None`.
    * lognumbers : int, array-like, optional
        >Lognumber(s) of MAGS logfiles being read. Only specify if you have a local CuPID binary file you want to read and sync to UTC time.
        Default `[]`.
    * level : str, optional
        >Data processing level of magnetometer data to download. Only specify if data is to be downloaded or you have paths to your own L2a CXDH data. Options:
        >
        >     '1' : Level 1 data (time in onboard payload time, no low-pass filter)
        >
        >     '2': Level 2 data (time in UTC, low-pass noise filter)
        >
        >If time sync fails for manually processed file when level 2 specified, returned data uses GPS time in seconds to tag magnetometer measurements.
        >Default `'2'`.
    * mags : DataFrame, optional
        >DataFrame of magnetometer data as read with `cupid.mags.data()`. Can be supplied instead of logfile or time range. Must be linear (`linear=True` set in `cupid.mags.data()`). Default `None`.
    * title : str, optional
        >If specified, adds title to plot of counts or countrates. Default `None`.

    ### Returns
    * mags : float array-like
        >Dataframe of magnetometer data.

    ### Examples
    Plot the magnetic field measured during field aligned current crossing on January 3rd, 2022 from 12:30 to 13:00
    ```python
        from cupid import mags
        magsdata = mags.plot(trange=['2022-01-03/12:30','2022-01-03/13:00'])
    ```
    If we have a binary logfile we want to look at, we can specify the path to the logfile.
    ```python
        magsdata = mags.plot(filename='mags-26')
    ```
    """
    if (mags is None):
        mags = data(trange=trange, filename=filename, lognumbers=lognumbers, level=level)
    if ((level == '1')|(level==1)):
        t = mags['time']
        label = 'GPS Time'
    if ((level=='2a')|(level=='2b')|(level=='2')|(level==2)):
        t = mags['time_utc']
        label = 'Time (UTC)'
    plt.plot(t,mags['B_x'],color=be.red)
    plt.plot(t,mags['B_y'],color=be.green)
    plt.plot(t,mags['B_z'],color=be.blue)
    plt.xlabel(label)
    plt.ylabel('Magnetic Field (nT)')
    plt.legend(['X','Y','Z'])
    if title is None:
        plt.title('CuPID Magnetometer '+trange[0]+' to '+trange[1])
    else:
        plt.title(title)
    plt.show()
    return mags