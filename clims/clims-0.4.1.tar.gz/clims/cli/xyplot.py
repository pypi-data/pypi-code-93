import matplotlib.pyplot as plt
import click
import numpy as np

@click.command()
@click.argument("xyfiles", nargs=-1)
def xyplot(xyfiles):
    """
    Simple X-Y plot of data files with first column represent X axis and second and
    following columns represent Y data.
    """ 
    for i, xyfile in enumerate(xyfiles):
        x, *ys = np.loadtxt(xyfile).T
        for j, y in enumerate(ys):
            label = f'File[{i}]: y[{j}]'
            plt.plot(x,y,label=label)
    plt.legend()
    plt.show()
