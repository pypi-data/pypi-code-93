import matplotlib.pyplot as plt
import numpy as np

import scordt.reads as reads
import io

def ncellvstheta(d):
    rang = np.arange(0, 360,  10)
    d['theta'] = d['theta'] * 180 / np.pi
    hist = np.histogram(d['theta'], bins = rang, density=True)
    plt.clf()
    plt.plot(hist[1][:-1], hist[0])
    plt.xlabel("Angle")
    plt.ylabel("Frequency [a.u]")
    plt.tight_layout()
    plt.savefig("ncellvsangle.png", dpi=300)

def rvstheta(d):
    plt.clf()
    d['theta'] = d['theta'] * 180 / np.pi
    plt.scatter(d['theta'], d['r'])
    plt.xlabel("Angle")
    plt.ylabel(r"Radius from center [$\mu m $]")
    plt.tight_layout()
    plt.savefig("rvstheta.png", dpi=300)

def all_points_polar(cellsPolar, rmax=120):
    plt.clf()
    fig = plt.figure()
    plt.set_cmap('coolwarm')
    ax = fig.add_subplot(111, projection='polar')
    c = ax.scatter(cellsPolar['theta'], cellsPolar['r'], c=cellsPolar['z'] , alpha=0.75)
    ax.set_theta_offset(3*np.pi/2)
    ax = plt.gca()
    cbar = plt.colorbar(c)
    cbar.ax.set_ylabel(r'AP position [$\mu m$]', rotation=270, labelpad=15)
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


    ax.fill_between(np.linspace(np.pi/2, 3 * np.pi/2, 100), 0, 120, color="gray", alpha=0.1, zorder=0)
    ax.fill_between(np.linspace(- np.pi/2, np.pi/2, 100), 0, 120, color="green", alpha=0.1, zorder=0)
    ax.set_rmax(rmax)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    return buf

def r_histogram(cellsPolar, rmax=120):
    # Histograms of R distribution
    plt.clf()
    plt.title("Radius distribution")
    plt.hist(cellsPolar['r'], bins=20)
    plt.xlabel(r"Radius from AP axis [$\mu m $]")
    plt.ylabel("Frequency count")
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    return buf

def plot_3d(cells, ellip, path):
    plt.clf()
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot3D(ellip['x'], ellip['y'], ellip['z'], 'gray')
    ax.scatter3D(cells['z'], cells['y'], cells['x'])
    # ax.scatter3D(ellip['x'].iloc[0], ellip['y'].iloc[0], mine)
    ax.set_xlabel("YM")
    ax.set_ylabel("XM")
    ax.set_zlabel("Slice")

    ax.set_xlim(0, 50)
    plt.savefig(path, dpi=400)