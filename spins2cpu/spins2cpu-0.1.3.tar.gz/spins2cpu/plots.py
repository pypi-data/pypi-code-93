import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

def plot(arr):
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['font.family'] = 'Times New Roman'
    n, m = arr.shape
    l = (m - 2) // 2
    for i in range(1, l+1):
        plt.plot(arr[:,0],arr[:,i],linewidth=1,linestyle=':',label="spin%s"%(i-1),marker='o',markersize=2)
    plt.xlabel('Temperature (K)')
    plt.ylabel('magnetism')
    plt.xlim(arr[0,0], arr[-1,0])
    plt.grid(axis="x", ls='--', lw=0.5)
    plt.minorticks_on()
    plt.legend(loc='upper right', frameon=False, prop={'style':'italic','size':'small'})
    plt.savefig("magnetism.png", dpi=750, transparent=True, bbox_inches='tight')

    plt.clf()
    plt.xlabel('Temperature (K)')
    plt.ylabel('susceptibility')
    plt.xlim(arr[0,0], arr[-1,0])
    plt.grid(axis="x", ls='--', lw=0.5)
    plt.minorticks_on()
    for i in range(l+1, m-1):
        plt.plot(arr[:,0],arr[:,i],linewidth=1,linestyle=':',label='susceptibility%s'%(i-l-1),marker='o',markersize=2)
    plt.legend(loc='upper left', frameon=False, prop={'style':'italic','size':'small'})
    plt.savefig("susceptibility.png", dpi=750, transparent=True, bbox_inches='tight')

    plt.clf()
    plt.xlabel('Temperature (K)')
    plt.ylabel('specific heat')
    plt.xlim(arr[0,0], arr[-1,0])
    plt.grid(axis="x", ls='--', lw=0.5)
    plt.minorticks_on()
    plt.plot(arr[:,0],arr[:,-1],linewidth=1,linestyle=':',label='specific heat',marker='o',markersize=2)
    plt.legend(loc='upper left', frameon=False, prop={'style':'italic','size':'small'})
    plt.savefig("specific_heat.png", dpi=750, transparent=True, bbox_inches='tight')

def main(file):
    f = open(file,"r")
    lines = f.readlines()
    f.close()

    j = False
    arr = []
    for i in lines:
        if j:
            if len(i.split()) > 0 and i.split()[0][0].isdigit():
                arr.append(i)
            else:
                j = False
        else:
            k = i.split()
            if k[0] == 'Temperature':
                j = True

    if arr:
        arr = np.array([i.split()[0:-1] for i in arr]).astype(float)
        plot(arr)
    else:
        print('No data!')
