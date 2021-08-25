import math
import sys
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.pyplot import imshow
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.display import display, HTML

def ju_init():
    display(HTML("<style>.container {width:95% !important;}</style>"))
    display(HTML("<style>div.output pre {font-family:Sans-Serif;font-size:10pt;color:black;font-weight:400;letter-spacing:1px;}</style>"))
    InteractiveShell.ast_node_interactivity = "all"
    pd.set_option('max_rows', 1000)
    pd.options.display.max_columns = 1000
    pd.options.display.float_format = '{:,.2f}'.format

def in_ipynb():
    try:
        ret = get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
    except: return False
    return True

jupyter_stdout = sys.stdout
def disablePrint(): sys.stdout = open(os.devnull, 'w')
def enablePrint(): sys.stdout = jupyter_stdout
    
def force_print(*args):
    _stdout = sys.stdout
    enablePrint()
    print(*args)
    sys.stdout = _stdout

def imshow(im, title):
    if type(im)==np.ndarray and im.shape[0]==1: im = im[0]
    plt.imshow(im)
    plt.title(title)
    plt.show()
    plt.pause(0.001)
    
def imgrid(x, y):
    if len(x.shape) not in [3,4]: Exception('x dims must be 3 ou 4')
    if len(x.shape)==3: x = x[None,:,:,:]
    n = x.shape[0]
    nr = math.floor(math.sqrt(n))
    nc = n // nr
    fig, axs = plt.subplots(nr, nc, figsize=(15,8))
    if type(axs)!=np.ndarray: axs = [[axs]]
    elif len(axs.shape)==1: axs = [axs]
    for i in range(n):
        r,c = i//nc,i%nc
        ax = axs[r][c]
        ax.imshow(x[i])
        ax.set_title(y[i])
    fig.tight_layout()
    plt.show()
    plt.pause(0.001)

def plot_signal(x, ch=0, title=None):
    plt.plot(x[ch])
    if title: plt.title(title)
    plt.show()
    plt.pause(0.001)
    
def plot_signal_grid(x):
    n = x.shape[0]
    nr = math.floor(math.sqrt(n))
    nc = n // nr
    fig, axs = plt.subplots(nr, nc, figsize=(15,8))
    for i in range(n):
        r,c = i//nc,i%nc
        axs[r][c].plot(x[i])
        axs[r][c].set_title(f'Channel {i}')
    fig.tight_layout()
    plt.show()
    plt.pause(0.001)