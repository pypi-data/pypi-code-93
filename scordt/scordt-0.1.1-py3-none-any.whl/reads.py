import pandas as pd
import numpy as np
import os
import sys
import time

from scipy.interpolate import interp1d

import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

# from scordt.slicesPlot import plot_angular_slices
import scordt.arc2 as arc
from scordt.func import *


def format2(cellsOri, elipseOri):
    # cellsFile = "data/"+str(fil)

    # cellsOri = pd.read_excel(cellsFile, sheet_name=0, skiprows=3)
    # elipseOri = pd.read_excel(cellsFile, sheet_name=1, skiprows=0)

    cells = pd.DataFrame()
    ellip = pd.DataFrame()
    newCoords = pd.DataFrame()

    cells['x'] = cellsOri['Position X']
    cells['y'] = cellsOri['Position Y']
    cells['z'] = cellsOri['Position Z']
    # cells['diameter'] = cellsOri['Column13'][3:]
    cells['id'] = cellsOri['ID']


    ellip['y'] = elipseOri['XM'][0:]
    ellip['x'] = elipseOri['YM'][0:]
    ellip['z'] = elipseOri['Slice'][0:]

    return cells, ellip

def format(cellsOri, elipseOri):
    # cellsFile = "../data/"+sys.argv[1]
    # cellsFile = str(fil)

    # cellsOri = pd.read_excel(cellsFile, sheet_name=0, engine="openpyxl")
    # elipseOri = pd.read_excel(cellsFile, sheet_name=1, engine="openpyxl")

    cells = pd.DataFrame()
    ellip = pd.DataFrame()
    newCoords = pd.DataFrame()

    cells['x'] = cellsOri['Column1'][4:]
    cells['y'] = cellsOri['Column2'][4:]
    cells['z'] = cellsOri['Column3'][4:]
    # cells['diameter'] = cellsOri['Column13'][3:]
    cells['id'] = cellsOri['Column8'][4:]

    ellip['y'] = elipseOri['XM'][0:]
    ellip['x'] = elipseOri['YM'][0:]
    ellip['z'] = elipseOri['Slice'][0:]

    return cells, ellip

def create(cells, ellip, ampPlane = 0):
    # print(path_to_file)
    print("Running test version !")
    print("Running test version !")
    print("Running test version !")
    ampPlane = int(ampPlane)
    cells, ellip = format(cells, ellip)
    print("Executing...")
    # Going from cells to ellipse coordinate by rotation:
    x = []
    y = []
    z = []


    # Interpolate ellipses
    mine = min(ellip['z'])
    maxe = max(ellip['z'])

    if ampPlane < mine:
        ampPlane = mine
        print("Amputation before ellipse, using minimum as first ...")

    xfull = np.linspace(mine, maxe, num=40, endpoint=True)
    ellip['z'] = pd.to_numeric(ellip['z'], errors='coerce')

    # pd.to_numeric(cells['x'], errors='coerce')
    # pd.to_numeric(cells['y'], errors='coerce')
    # pd.to_numeric(cells['z'], errors='coerce')
    cells['x'] = cells['x'].astype(float)
    cells['y'] = cells['y'].astype(float)
    cells['z'] = cells['z'].astype(float)


    mid = 50

    # ez = list(ellip['z'][:mid]) + list(ellip['z'][mid+35:])
    # ey = list(ellip['y'][:mid]) + list(ellip['y'][mid+35:])
    # ex = list(ellip['x'][:mid]) + list(ellip['x'][mid+35:])

    ez = ellip['z']
    ey = ellip['y']
    ex = ellip['x']


    f1 = interp1d(ez, ey, kind='cubic')
    f2 = interp1d(ez, ex, kind='cubic')

    ###DEBUG:
    # print("DEBUG")
    # # l = cells.loc[cells['x'] == i]
    # # cells = cells[cells.x > mine]
    # print(cells['x'].max())
    # fig = plt.figure()
    # plt.plot(xfull, f1(xfull), color="green")
    # plt.scatter(cells['x'] , cells['y'], color="red", alpha=0.6)
    # plt.xlabel("Slice")
    # plt.ylabel("XM")
    # plt.savefig("res/eliPos/"+str(fil)[0:3]+"_xm.png", dpi=300)
    # plt.clf()
    # plt.plot(xfull, f2(xfull), color="green")
    # plt.xlabel("Slice")
    # plt.ylabel("YM")
    # plt.scatter(cells['x'] , cells['z'], color="red", alpha=0.6)
    # plt.savefig("res/eliPos/"+str(fil)[0:3]+"_ym.png", dpi=300)
    #
    # ##
    # plt.clf()
    # fig = plt.figure()
    # ax = plt.axes(projection='3d')
    # ax.plot3D(ellip['x'], ellip['y'], ellip['z'], 'gray')
    # ax.scatter3D(cells['z'], cells['y'], cells['x'])
    # ax.scatter3D(ellip['x'], ellip['y'], ellip['z'], 'green')
    # # ax.scatter3D(ellip['x'].iloc[0], ellip['y'].iloc[0], mine)
    # ax.set_xlabel("YM (Top - Bottom)")
    # ax.set_ylabel("XM (Dorsal - Ventral)")
    # ax.set_zlabel("Slice (Posterior - Anterior)")
    #
    # # ax.set_xlim(0, 50)
    # plt.savefig("res/eliPos3D/"+str(fil)[0:3]+".png", dpi=400)
    #
    # for ii in range(0,360,1):
    #     ax.view_init(elev=10., azim=ii)
    #     plt.savefig("res/eliPos3D/"+str(fil)[0:3]+"/movie%d.png" % ii)
    # # plt.show()
    # print("END DEBUG")
    #####
    # exit()


    # Put all cells in the new coordinate system
    frame = (ellip['x'].iloc[0], ellip['y'].iloc[0], mine)
    print("Frame of reference: ", frame)
    newR = []
    newTh = []
    newZ = []
    newID = []
    for i in range(4, len(cells)):
        if float(cells['x'][i]) >= float(mine) and float(cells['x'][i]) <= float(maxe):
            xy = (float(cells['z'][i]), float(cells['y'][i]))
            # z position of the cell is given by the x
            z = float(cells['x'][i])
            newX = float(cells['y'][i]) - f1(z)
            newY = float(cells['z'][i]) - f2(z)

            r = np.sqrt(newX**2 + newY**2)

            th = np.arctan2(newY, newX)
            if th < 0:
                th += 2 * np.pi

            newR.append(r)
            newTh.append(th)
            newZ.append(z)
            newID.append(int(cells['id'][i]))
            newCoords = (r, th, z)
            if newCoords[0] < 3:
                print("Resta x: ", f1(z))
                print("Resta y: ", f2(z))
                print(i, (xy[0], xy[1], z), "--->", newCoords)
                print("---------------")
        else:
            pass
            # print("ID: ", i, " above or below interpolation range")

    cellsPolar = pd.DataFrame()

    cellsPolar['r'] = newR
    cellsPolar['theta'] = newTh
    cellsPolar['z'] = newZ
    cellsPolar['id'] = newID


    # create a function that given x gives position in new axis:
    def apaxis(x, ampPlane):
        # length = arc.arc_len(f1, [min(cellsPolar['z']), x], 1000)
        length = arc.arc_len(f1, [ampPlane, x], 1000)
        if float(x) < ampPlane:
            return -1*length
        else:
            return length

    time1 = time.time()
    arrAp = list(map(lambda p: apaxis(p, ampPlane), newZ))
    time2 = time.time()
    print("Map took: ", time2 - time1, " seconds")

    cellsPolar['z'] = arrAp

    return cellsPolar, cells, (f1, f2), ellip
