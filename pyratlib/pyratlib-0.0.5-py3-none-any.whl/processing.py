import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def Trajectory (data, bodyPartTraj, bodyPartBox, cmapType = 'viridis', figureTitle = None, 
              hSize=6, wSize =8,fontsize=15, invertY = True, saveName=None, figformat =".eps"):
    """
    Plots the trajectory of the determined body part.

    Parameters
    ----------
    data : pandas DataFrame
        The input.
    bodyPartTraj : str
        Body part you want to plot the tracking.
    bodyPartBox : str
        The body part you want to use to estimate the limits of the environment, 
        usually the base of the tail is the most suitable for this determination.
    cmapType : str, optional
        matplotlib colormap.
    figureTitle : str, optional
        Figure title.
    hSize : int, optional
        Determine the figure height size (x).
    wSize : int, optional
        Determine the figure width size (y).
    fontsize : int, optional
        Determine of all font sizes.
    invertY : bool, optional
        Determine if de Y axis will be inverted (used for DLC output).
    saveName : str, optional
        Determine the save name of the plot.        
    figformat : str, optional
        Determines the type of file that will be saved. Used as base the ".eps", 
        which may be another supported by matplotlib..  

    Returns
    -------
    out : plot
        The output of the function is the figure with the tracking plot of the 
        selected body part.


    See Also
    --------
    For more information and usage examples: https://github.com/pyratlib/pyrat

    Notes
    -----
    This function was developed based on DLC outputs and is able to support 
    matplotlib configurations."""
    values = (data.iloc[2:,1:].values).astype(np.float)
    lista1 = (data.iloc[0][1:].values +" - " + data.iloc[1][1:].values).tolist()

    x = values[:,lista1.index(bodyPartTraj+" - x")]
    y = values[:,lista1.index(bodyPartTraj+" - y")]

    cmap = plt.get_cmap(cmapType)

    c = np.linspace(0, x.size/30, x.size)
    esquerda = values[:,lista1.index(bodyPartBox+" - x")].min()
    direita = values[:,lista1.index(bodyPartBox+" - x")].max()
    baixo = values[:,lista1.index(bodyPartBox+" - y")].min()
    cima = values[:,lista1.index(bodyPartBox+" - y")].max()

    plt.rcParams["font.family"] = "Arial"
    plt.figure(figsize=(wSize, hSize), dpi=80)
    plt.title(figureTitle, fontsize=fontsize)
    plt.scatter(x, y, c=c, cmap=cmap, s=3)
    plt.plot([esquerda,esquerda] , [baixo,cima],"r")
    plt.plot([esquerda,direita]  , [cima,cima],"r")
    plt.plot([direita,direita]   , [cima,baixo],"r")
    plt.plot([direita,esquerda]  , [baixo,baixo],"r")
    #ax1.set_ylim(480,0)
    #ax1.set_xlim(0,640)
    cb = plt.colorbar()
    #plt.xticks(rotation=45)
    #plt.yticks(rotation=90)

    if invertY == True:
        plt.gca().invert_yaxis()
    cb.set_label('Time (s)',fontsize=fontsize)
    cb.ax.tick_params(labelsize=fontsize*0.8)
    plt.xlabel("X (px)",fontsize=fontsize)
    plt.ylabel("Y (px)",fontsize=fontsize)
    plt.xticks(fontsize = fontsize*0.8)
    plt.yticks(fontsize = fontsize*0.8)
    if saveName != None:
        plt.savefig(saveName+figformat)
    plt.show()


def Heatmap(data, bodyPart, cmapType = 'viridis', figureTitle = None, hSize=6, wSize =8,
            bins = 40, vmax= 1000, fontsize=15, invertY = True, saveName=None, figformat = ".eps"):
    """
    Plots the trajectory heatmap of the determined body part.

    Parameters
    ----------
    data : pandas DataFrame
        The input.
    bodyPart : str
        Body part you want to plot the heatmap.
    cmapType : str, optional
        matplotlib colormap.
    figureTitle : str, optional
        Figure title.
    hSize : int, optional
        Determine the figure height size (x).
    wSize : int, optional
        Determine the figure width size (y).
    bins : int, optional
        Determine the heatmap resolution, the higher the value, the higher the 
        resolution.
    vmax : int, optional
        Determine the heatmap scale.
    fontsize : int, optional
        Determine of all font sizes.
    invertY : bool, optional
        Determine if de Y axis will be inverted (used for DLC output).
    saveName : str, optional
        Determine the save name of the plot.        
    figformat : str, optional
        Determines the type of file that will be saved. Used as base the ".eps", 
        which may be another supported by matplotlib..  

    Returns
    -------
    out : plot
        The output of the function is the figure with the tracking plot of the 
        selected body part.


    See Also
    --------
    For more information and usage examples: https://github.com/pyratlib/pyrat

    Notes
    -----
    This function was developed based on DLC outputs and is able to support 
    matplotlib configurations."""
    values = (data.iloc[2:,1:].values).astype(np.float)
    lista1 = (data.iloc[0][1:].values +" - " + data.iloc[1][1:].values).tolist()

    x = values[:,lista1.index(bodyPart+" - x")]
    y = values[:,lista1.index(bodyPart+" - y")]

    plt.figure(figsize=(wSize, hSize), dpi=80)

    plt.hist2d(x,y, bins = bins, vmax = vmax,cmap=plt.get_cmap(cmapType))

    cb = plt.colorbar()

    plt.title(figureTitle, fontsize=fontsize)
    cb.ax.tick_params(labelsize=fontsize*0.8)
    plt.xlabel("X (px)",fontsize=fontsize)
    plt.ylabel("Y (px)",fontsize=fontsize)
    plt.xticks(fontsize = fontsize*0.8)
    plt.yticks(fontsize = fontsize*0.8)
    if invertY == True:
        plt.gca().invert_yaxis()

    if saveName != None:
        plt.savefig(saveName+figformat)
    plt.show()