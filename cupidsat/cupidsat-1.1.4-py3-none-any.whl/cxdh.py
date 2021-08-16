import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from . import backend as be

l1_cols = ['sync', 'time_payld', 'time_adacs', 'xrbr_log_no', 'xrfs_log_no','dsfs_log_no', 'hkhi_log_no','radio_temp [C]', 'gps_temp [C]', 'dosi_temp [C]', 'pld_hv_bd_temp [C]',
           'pld_fpga_temp [C]', 'pos_x_temp [C]', 'neg_x_temp [C]', 'pos_y_temp [C]','neg_y_temp [C]', 'pos_z_temp [C]', 'neg_z_temp [C]','cntr_temp [C]', 'zync_temp [C]', 
           'board_temp [C]','v_batt [V]', 'v_spnl [V]', 'i_batt [A]', 'i_spnl [A]', 'i_epssw1 [A]', 'i_epssw2 [A]','angle_to_go', 'n_xray_cull_thresh', 'mags_log_no', 'p_x_eci [Re]', 
           'p_y_eci [Re]', 'p_z_eci [Re]', 'Bfield_meas1 [nT]', 'Bfield_meas2 [nT]', 'Bfield_meas3 [nT]','Qbi_1', 'Qbi_2', 'Qbi_3','Qbi_4','counts_xray_1', 'counts_xray_2', 'counts_xray_3',
           'counts_xray_4', 'counts_xray_5', 'counts_xray_6','dosalow_1', 'dosalow_2', 'dosalow_3','dosalow_4', 'dosalow_5', 'dosalow_6','dosamed_1', 'dosamed_2', 'dosamed_3','dosamed_4', 
           'dosamed_5', 'dosamed_6', 'dosblow_1', 'dosblow_2', 'dosblow_3','dosblow_4', 'dosblow_5', 'dosblow_6','dosbmed_1', 'dosbmed_2', 'dosbmed_3','dosbmed_4', 'dosbmed_5', 'dosbmed_6']

l2_cols = ['sync', 'time_payld', 'time_utc', 'xrbr_log_no', 'xrfs_log_no','dsfs_log_no', 'hkhi_log_no','radio_temp [C]', 'gps_temp [C]', 'dosi_temp [C]', 'pld_hv_bd_temp [C]',
           'pld_fpga_temp [C]', 'pos_x_temp [C]', 'neg_x_temp [C]', 'pos_y_temp [C]','neg_y_temp [C]', 'pos_z_temp [C]', 'neg_z_temp [C]','cntr_temp [C]', 'zync_temp [C]', 
           'board_temp [C]','v_batt [V]', 'v_spnl [V]', 'i_batt [A]', 'i_spnl [A]', 'i_epssw1 [A]', 'i_epssw2 [A]','angle_to_go', 'n_xray_cull_thresh', 'mags_log_no', 'p_x_gse [Re]', 
           'p_y_gse [Re]', 'p_z_gse [Re]', 'B_x [nT]', 'B_y [nT]', 'B_z [nT]','Qbi1', 'Qbi2', 'Qbi3', 'Qbi4','counts_xray_1', 'counts_xray_2', 'counts_xray_3',
           'counts_xray_4', 'counts_xray_5', 'counts_xray_6','dosalow_1', 'dosalow_2', 'dosalow_3','dosalow_4', 'dosalow_5', 'dosalow_6','dosamed_1', 'dosamed_2', 'dosamed_3','dosamed_4', 
           'dosamed_5', 'dosamed_6', 'dosblow_1', 'dosblow_2', 'dosblow_3','dosblow_4', 'dosblow_5', 'dosblow_6','dosbmed_1', 'dosbmed_2', 'dosbmed_3','dosbmed_4', 'dosbmed_5', 'dosbmed_6']

def data(trange=['2021-01-01/00:00','2021-01-02/00:00'], filename=None, level='1',numpy=False):
    """
    Read combined x-ray, dosi, and housekeeping (CXDH) data from TFTP server or local file into `pandas` dataframe or `numpy` array.

    ### Parameters
    * trange : string array-like, optional
        >Time range of CXDH data to download from the TFTP server. Format 'YYYY-MM-DD/HH:MM' in UTC.
        Default `['2021-01-01/00:00','2021-01-02/00:00']`.
    * filename : str, optional
        >Name of CXDH logfile to read. Only specify if you have a local CuPID binary file you want to read.
        Overrides `trange` if specified. Default `None`.
    * level : str, optional
        >Data processing level of CXDH data to download. Only specify if data is to be downloaded or you have paths to your own L2 CXDH data. Options:
        >
        >     '1' : Level 1 data (time in GPS time, position in Earth Centered Inertial coordinates, pointing in quaternion, magnetic field in body coordinates w/o gain and bias calibration)
        >
        >     '2': Level 2 data (time in UTC, position in Geocentric Solar Ecliptic coordinates, pointing in RA/Dec, magnetic field in lat/lon/norm coordinates)
        >
        >Default `'1'`.
    * numpy : bool, optional
        >If `True`, returns numpy array of CXDH data. If `False`, returns `pandas` DataFrame of CXDH data. Default `False`.

    ### Returns
    * cxdh : float array-like
        >Dataframe (if not `numpy`) or numpy array (if `numpy`) of CXDH data.

    ### Examples
    Read in data from cusp encounter on January 3rd, 2022 from 12:30 to 13:00
    ```python
        from cupid import cxdh
        from cupid import backend
        cxdhdata = cxdh.data(trange=['2022-01-03/12:30','2022-01-03/13:00'])
    ```
    Plot spacecraft position during this event.
    ```python
        import matplotlib.pyplot as plt
        plt.plot(cxdhdata['time_utc'],cxdhdata['p_x_gse [Re]'],color=backend.red)
        plt.plot(cxdhdata['time_utc'],cxdhdata['p_y_gse [Re]'],color=backend.green)
        plt.plot(cxdhdata['time_utc'],cxdhdata['p_z_gse [Re]'],color=backend.blue)
        plt.legend(['X','Y','Z'])
    ```
    This is great for making custom plots, but if you want to plot quickly and easily it may be better to use `cupid.cxdh.plot`.

    """
    if filename is None: #If filename is not specified
        raise NameError("TFTP Download not implemented in current release. Please specify filename argument.")
    else:
        cxdh = be.read_cxdh(filename)
        if ((level == '1')|(level==1)):
            cxdh = be.makeL1(cxdh)
            cxdh = pd.DataFrame(cxdh,columns=l1_cols)
        if ((level=='2a')|(level=='2b')|(level=='2')|(level==2)):
            cxdh = be.makeL1(cxdh)
            cxdh = be.makeL2a(cxdh,[])
            cxdh = pd.DataFrame(cxdh,columns=l2_cols)
        if numpy:
            return cxdh.to_numpy()
        else:
            return cxdh

def plot(trange=['2021-01-01/00:00','2021-01-02/00:00'], filename=None, level='1', cxdh = None, title=None, keys=None):
    """
    Plot combined x-ray, dosi, and housekeeping (CXDH) data for given time range, file, or existing DataFrame.

    ### Parameters
    * trange : string array-like, optional
        >Time range of CXDH data to download from the TFTP server. Format 'YYYY-MM-DD/HH:MM' in UTC.
        Default `['2021-01-01/00:00','2021-01-02/00:00']`.
    * filename : str, optional
        >Name of CXDH logfile to read. Only specify if you have a local CuPID binary file you want to read.
        Overrides `trange` if specified. Default `None`.
    * level : str, optional
        >Data processing level of CXDH data to download. Only specify if data is to be downloaded or you have paths to your own L2 CXDH data. Options:
        >
        >     '1' : Level 1 data (time in GPS time, position in Earth Centered Inertial coordinates, pointing in quaternion, magnetic field in body coordinates w/o gain and bias calibration)
        >
        >     '2': Level 2 data (time in UTC, position in Geocentric Solar Ecliptic coordinates, pointing in RA/Dec, magnetic field in lat/lon/norm coordinates)
        >
        >Default `'1'`.
    * cxdh : DataFrame, optional
        >DataFrame of CXDH data as read with `cupid.cxdh.data()`. Can be supplied instead of logfile or time range. Default `None`.
    * title : str, optional
        >If specified, adds title to plot. Default `None`.
    * keys : str, array-like
        >Keys of CXDH data to plot. Assumed iterable, so if only one key is passed it must be passed in a list (`['key']`). Options are:
        >
        >     'xray' : X-Ray countrate.
        >
        >     'dosi' : Dosimeter channel A and B countrate.
        >
        >     'mags' : Three channel magnetometer measurements.
        >
        >     'lognumbers' : If included, lognumbers are plotted on top of relevant plots (xray, dosi, mags).
        >
        >     'position' : Spacecraft position (ECI if level 1, GSE if level 2).
        >
        >     'pointing' : Spacecraft pointing (Quaternion if level 1, RA/Dec if level 2).
        >
        >     'temps' : Temperatures (all over top each other, with safety bounds plotted)
        >
        >     'EPS' : Currents and voltages.
        >

    ### Returns
    * cxdh : float array-like
        >Dataframe of CXDH data.

    ### Examples
    Plot the spacecraft position during cusp encounter on January 3rd, 2022 from 12:30 to 13:00
    ```python
        from cupid import cxdh
        cxdhdata = cxdh.plot(trange=['2022-01-03/12:30','2022-01-03/13:00'],keys=['position'])
    ```
    If we have a binary logfile we want to look at, we can specify the path to the logfile.
    ```python
        cxdhdata = cxdh.plot(filename='cxdh-26')
    ```
    """
    if (cxdh is None):
        cxdh = data(trange=trange, filename=filename, level=level)
    if ((level == '1')|(level==1)):
        t = cxdh['time_adacs']
        xlabel = 'GPS Time'
    if ((level=='2a')|(level=='2b')|(level=='2')|(level==2)):
        t = cxdh['time_utc']
        xlabel = 'Time (UTC)'
    if (keys is None):
        keys = ['xray','dosi','mags','position']
    t_exp = np.zeros(len(t)*6)
    for i in range(len(t_exp)):
        t_exp[i] = t[i//10]+(i%10)
    rows = 0
    for key in keys:
        if (key=='xray'):
            rows += 1
        if (key=='dosi'):
            rows += 1
        if (key=='mags'):
            rows += 1
        if (key=='position'):
            rows += 1
        if (key=='pointing'):
            rows += 1
        if (key=='temps'):
            rows += 1
        if (key=='EPS'):
            rows += 2
    fig, axes = plt.subplots(nrows=rows, ncols=1, sharex=True)
    fig.subplots_adjust(hspace=0)
    ind = 0
    if title is None:
        axes[0].set_title('CuPID CXDH '+trange[0]+' to '+trange[1])
    else:
        axes[0].set_title(title)
    axes[-1].set_xlabel(xlabel)
    for key in keys:
        if (key=='xray'):
            xray = cxdh[['counts_xray_1', 'counts_xray_2', 'counts_xray_3','counts_xray_4', 'counts_xray_5', 'counts_xray_6']].to_numpy().ravel()
            cr = np.zeros(len(xray))
            for i in range(1,len(cr)):
                cr[i] = (xray[i]-xray[i-1])/10
            axes[ind].plot(t_exp,cr,color=be.black)
            axes[ind].set_ylabel(r'$CR_{XRAY}$')
            if (np.isin('lognumbers',keys)):
                bottom,top = axes[i].get_ylim()
                y1 = (top-bottom)*0.2 + bottom
                y2 = (top-bottom)*0.8 + bottom
                axes[ind].text(t[0]+360,y1,int(xrbr_log[0]),color=be.blue)
                axes[ind].text(t[0]+360,y2,int(xrfs_log[0]),color=be.red)
                for j in np.arange(1,len(t)):
                    if (cxdh['xrbr_log_no'][j]!=cxdh['xrbr_log_no'][j-1]):
                        axes[ind].axvline(x=t[j],color=be.blue,alpha=0.5)
                        axes[ind].text(t[j]+360,y1,int(cxdh['xrbr_log_no'][j]),color=be.blue)
                    if (cxdh['xrfs_log_no'][j]!=cxdh['xrfs_log_no'][j-1]):
                        axes[ind].axvline(x=t[j],color=be.red,alpha=0.5)
                        axes[ind].text(t[j]+360,y2,int(cxdh['xrfs_log_no'][j]),color=be.red)
            ind += 1
        if (key=='dosi'):
            dosi_a_lo = cxdh[['dosalow_1', 'dosalow_2', 'dosalow_3','dosalow_4', 'dosalow_5', 'dosalow_6']].to_numpy().ravel()
            dosi_b_lo = cxdh[['dosblow_1', 'dosblow_2', 'dosblow_3','dosblow_4', 'dosblow_5', 'dosblow_6']].to_numpy().ravel()
            dosi_a_me = cxdh[['dosamed_1', 'dosamed_2', 'dosamed_3','dosamed_4', 'dosamed_5', 'dosamed_6']].to_numpy().ravel()
            dosi_b_me = cxdh[['dosbmed_1', 'dosbmed_2', 'dosbmed_3','dosbmed_4', 'dosbmed_5', 'dosbmed_6']].to_numpy().ravel()
            dosi_a = dosi_a_lo + (dosi_a_me * 256)
            dosi_b = dosi_b_lo + (dosi_b_me * 256)
            cr_a = np.zeros(len(dosi_a))
            cr_b = np.zeros(len(dosi_b))
            for i in range(1,len(cr_a)):
                cr_a[i] = (dosi_a[i]-dosi_a[i-1])/10
                cr_b[i] = (dosi_b[i]-dosi_b[i-1])/10
            axes[ind].plot(t_exp,cr_a,color=be.red)
            axes[ind].plot(t_exp,cr_a,color=be.blue)
            axes[ind].legend(['A','B'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
            axes[ind].set_ylabel(r'$CR_{DSFS}$')
            if (np.isin('lognumbers',keys)):
                bottom,top = axes[ind].get_ylim()
                y = (top-bottom)*0.8 + bottom
                axes[ind].text(t[0]+360,y,int(cxdh['dsfs_log_no'][0]),color=be.black)
                for j in np.arange(1,len(t)):
                    if (cxdh['dsfs_log_no'][j]!=cxdh['dsfs_log_no'][j-1]):
                        axes[ind].axvline(x=t[j],color=be.black,alpha=0.5)
                        axes[ind].text(t[j]+360,y,int(cxdh['dsfs_log_no'][j]),color=be.black)
            ind += 1
        if (key=='mags'):
            if ((level == '1')|(level==1)):
                b = cxdh[['Bfield_meas1 [nT]', 'Bfield_meas2 [nT]', 'Bfield_meas3 [nT]']].to_numpy()
                legend = ['X','Y','Z']
            if ((level=='2a')|(level=='2b')|(level=='2')|(level==2)):
                b = cxdh[['B_lat [nT]', 'B_lon [nT]', 'B_norm [nT]']].to_numpy()
                legend = ['Lat','Lon','Norm']
            axes[ind].plot(t,b[:,0],color=be.red)
            axes[ind].plot(t,b[:,1],color=be.blue)
            axes[ind].plot(t,b[:,2],color=be.green)
            axes[ind].legend(legend,loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
            axes[ind].set_ylabel('B (nT)')
            if (np.isin('lognumbers',keys)):
                bottom,top = axes[ind].get_ylim()
                y = (top-bottom)*0.8 + bottom
                axes[ind].text(t[0]+360,y,int(cxdh['mags_log_no'][0]),color=be.black)
                for j in np.arange(1,len(time)):
                    if (mags_log[j]!=mags_log[j-1]):
                        axes[ind].axvline(x=t[j],color=be.black,alpha=0.5)
                        axes[ind].text(t[j]+360,y,int(cxdh['mags_log_no'][j]),color=be.black)
            ind += 1
        if (key=='position'):
            if ((level == '1')|(level==1)):
                axes[ind].plot(t,cxdh['p_x_eci [Re]'],color=be.red)
                axes[ind].plot(t,cxdh['p_y_eci [Re]'],color=be.green)
                axes[ind].plot(t,cxdh['p_z_eci [Re]'],color=be.blue)
                axes[ind].legend(['ECI X','ECI Y','ECI Z'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
            if ((level=='2a')|(level=='2b')|(level=='2')|(level==2)):
                axes[ind].plot(t,cxdh['p_x_gse [Re]'],color=be.red)
                axes[ind].plot(t,cxdh['p_y_gse [Re]'],color=be.green)
                axes[ind].plot(t,cxdh['p_z_gse [Re]'],color=be.blue)
                axes[ind].legend(['GSE X','GSE Y','GSE Z'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
            axes[ind].set_ylabel(r'Position $R_{E}$')
            ind += 1
        if (key=='pointing'):
            if ((level == '1')|(level==1)):
                axes[ind].plot(t,cxdh['Qbi_1'],color=be.red)
                axes[ind].plot(t,cxdh['Qbi_2'],color=be.green)
                axes[ind].plot(t,cxdh['Qbi_3'],color=be.blue)
                axes[ind].plot(t,cxdh['Qbi_4'],color=be.black)
                axes[ind].legend(['Qbi 1','Qbi 2','Qbi 3','Qbi 4'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
            if ((level=='2a')|(level=='2b')|(level=='2')|(level==2)):
                axes[ind].plot(t,cxdh['RA'],color=be.red)
                axes[ind].plot(t,cxdh['Dec'],color=be.blue)
                axes[ind].legend(['RA','Dec'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
            ind += 1
        if (key=='temps'):
            temps = ['radio_temp [C]', 'gps_temp [C]', 'dosi_temp [C]', 'pld_hv_bd_temp [C]','pld_fpga_temp [C]',
                     'pos_x_temp [C]', 'neg_x_temp [C]', 'pos_y_temp [C]','neg_y_temp [C]', 'pos_z_temp [C]', 
                     'neg_z_temp [C]','cntr_temp [C]', 'zync_temp [C]','board_temp [C]']
            for temp in temps:
                axes[ind].plot(t,cxdh[temp],color=be.black,alpha=0.2)
            axes[ind].set_ylabel('T (K)')
            axes[ind].hlines([75,-20],t[0],t[-1],colors = be.red, linestyles='dashed',alpha = 0.3)
            ind += 1
        if (key=='EPS'):
            'v_batt [V]', 'v_spnl [V]', 'i_batt [A]', 'i_spnl [A]', 'i_epssw1 [A]', 'i_epssw2 [A]'
            axes[ind].plot(t,cxdh['v_batt [V]'],color=be.black)
            axes[ind].plot(t,cxdh['v_spnl [V]'],color=be.red)
            axes[ind].set_ylabel('V')
            axes[ind].legend(['Battery','Solar Panel'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
            ind += 1
            axes[ind].plot(t,cxdh['i_batt [A]'],color=be.black)
            axes[ind].plot(t,cxdh['i_spnl [A]'],color=be.red)
            axes[ind].plot(t,cxdh['i_epssw1 [A]'],color=be.green)
            axes[ind].plot(t,cxdh['i_epssw2 [A]'],color=be.blue)
            axes[ind].set_ylabel('A')
            axes[ind].legend(['Battery','Solar Panel','EPSS1','EPSS2'],loc='center left',bbox_to_anchor=(1,0.5),frameon=False)
            ind += 1
    plt.show()
    return cxdh