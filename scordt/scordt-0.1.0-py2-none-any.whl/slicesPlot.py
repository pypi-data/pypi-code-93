import matplotlib.pyplot as plt
import numpy as np

import scordt.arc as arc

# Plot slices of the angular distribution z by z

def plot_angular_slices(cellsPolar, cells, f1):
    ncells = []
    r = []
    rMean = []
    rStd = []
    theta = []
    diameter = []
    diamMean = []
    diamStd = []
    z = []
    cellsPolar = cellsPolar.sort_values(['z'])
    cellsPolar['z'] = cellsPolar['z'].apply(lambda x: round(x, 1))
    # Select all values in slice = nnn
    # for i in range(int(min(cellsPolar['z']))-1, int(max(cellsPolar['z']))):
    num = 0
    for i in cellsPolar['z']:
        num += 1
        l = cellsPolar.loc[cellsPolar['z'] == i]
        # print("New part... --------------")
        if len(l) != 0:
            z.append(i)
            # Plot number of cells as a function of AP
            ncells.append(len(l))
            # Plot r as a function of AP
            r.append(list(l['r']))
            rMean.append(np.mean(r[-1]))
            rStd.append(np.std(r[-1]))
            # Plot theta as a function of AP
            theta.append(list(l['theta']))
            # Plot area of cells as a function of AP
            diamID = list(l['id'])
            # diamEle = []
            # for id in diamID:
            #     diamEle.append(float(cells.loc[cells['id'] == id]['diameter']))
            # diameter.append(diamEle)
            # diamMean.append(np.mean(diamEle))
            # diamStd.append(np.std(diamEle))

            plt.clf()
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='polar')
            ax.set_theta_offset(3*np.pi/2)
            c = ax.scatter(list(l['theta']), list(l['r']), alpha=0.75)
            ax = plt.gca()
            plt.text(0.95, 0, "AP = "+str(round(i, 1)),
                    transform=ax.transAxes, fontweight="bold")

            ax.fill_between(np.linspace(np.pi/2, 3 * np.pi/2, 100), 0, 120, color="gray", alpha=0.1, zorder=0)
            ax.fill_between(np.linspace(- np.pi/2, np.pi/2, 100), 0, 120, color="green", alpha=0.1, zorder=0)

            ax.set_rmax(120)

            ax.annotate('Dorsal',
                        xy=(np.pi/2, 80),  # theta, radius
                        xytext=(0.55, 0.95),    # fraction, fraction
                        textcoords='figure fraction',
                        # arrowprops=dict(facecolor='black', shrink=0.05),
                        horizontalalignment='left',
                        verticalalignment='bottom',
                        fontweight='bold',
                        )
            ax.annotate('Ventral',
                        xy=(0, 0),  # theta, radius
                        xytext=(0.55, 0.05),    # fraction, fraction
                        textcoords='figure fraction',
                        # arrowprops=dict(facecolor='black', shrink=0.05),
                        horizontalalignment='left',
                        verticalalignment='top',
                        fontweight='bold',
                        )

            plt.tight_layout()
            plt.savefig("slicesOfAngularDist/"+str(num)+".png", dpi=400)

            # print("Z: ", z)
            # print("Number of cells: ", ncells)
            # print("R: ", r)
            # print("Theta:", theta)
            # print("Diameter:", diameter)
            # break
        # print("----------")
    # plot all:
    # create a function that given x gives position in new axis:
    def apaxis(x):
        return arc.arc_len(f1, [min(z), x], 1000)
    ## Plot cell number
    # z = list(map(apaxis, z))
    print(z)

    plt.clf()
    plt.title("Number of cells vs AP axis")
    plt.scatter(z, ncells)
    plt.xlabel(r"AP axis [$ \mu m $]")
    plt.ylabel("Number of cells")
    plt.savefig("apPlots/ncells.png", dpi=400)
    ## Plot r
    plt.clf()
    plt.title("Distance from center of AP axis")
    plt.scatter(z, rMean, alpha=0.75)
    plt.errorbar(z, rMean, yerr=rStd, alpha=0.75, fmt='none')
    plt.xlabel(r"AP axis [$ \mu m $]")
    plt.ylabel(r"Radius [$ \mu m $]")
    plt.savefig("apPlots/radius.png", dpi=400)
    ## Plot theta
    plt.clf()
    # plt.title("Angle from AP axis")
    # plt.scatter(z, theta)
    # plt.xlabel(r"AP axis [$ \mu m $]")
    # plt.ylabel("Angle")
    # plt.savefig("apPlots/theta.png", dpi=400)
    # ## Plot diameter
    # plt.clf()
    # plt.title("Diameter of cells vs AP axis")
    # plt.scatter(z, diamMean, alpha=0.75)
    # plt.errorbar(z, diamMean, diamStd, alpha=0.75, fmt='none')
    # plt.xlabel(r"AP axis [$ \mu m $]")
    # plt.ylabel(r"Diameter [$ \mu m $]")
    # plt.savefig("apPlots/diameter.png", dpi=400)
