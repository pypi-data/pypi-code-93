import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

def format_axis_ticks(ax, x_axis=True, y_axis=True, major_length=16, minor_length=8):
    if x_axis:
        if ax.get_xaxis().get_scale() != 'log':
            ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.tick_params(axis="x", which="major", direction='in', length=major_length)
        ax.tick_params(axis="x", which="minor", direction='in', length=minor_length)        
    if y_axis:
        if ax.get_yaxis().get_scale() != 'log':
            ax.yaxis.set_minor_locator(AutoMinorLocator())        
        ax.tick_params(axis="y", which="major", direction='in', length=major_length)
        ax.tick_params(axis="y", which="minor", direction='in', length=minor_length) 

def centralize_axis(ax, which='x'):
    if which == 'x':
        limits = ax.get_xlim()
        xmax = np.max(np.abs(limits))
        ax.set_xlim(-xmax, xmax)
    elif which == 'y':
        limits = ax.get_ylim()
        ymax = np.max(np.abs(limits))
        ax.set_ylim(-ymax, ymax)
        
def parse_transform(obj:str):
    if not obj:
        transform = None
    elif obj == 'figure':
        transform = plt.gcf().transFigure
    elif obj == 'axis':
        transform = plt.gca().transAxes
    elif obj == 'data':
        transform = plt.gca().transData
    return transform

def get_box_dimension(box):
    axis = plt.gca()
    plt.gcf().canvas.draw()
    bb = box.get_window_extent()
    points  = bb.transformed(axis.transAxes.inverted()).get_points().transpose()
    xmin = np.min(points[0])
    xmax = np.max(points[0])
    ymin = np.min(points[1])
    ymax = np.max(points[1])
    return xmin, xmax, ymin, ymax

def draw_sigma_bands(axis, ymax, height=1.0):
    # +- 2 sigma band
    axis.add_patch(Rectangle((-2, -height/2), 2*2, ymax + height/2, fill=True, color='yellow'))
    # +- 1 sigma band
    axis.add_patch(Rectangle((-1, -height/2), 1*2, ymax + height/2, fill=True, color='lime'))
    
def draw_sigma_lines(axis, ymax, height=1.0, **styles):
    y = [-height/2, ymax*height - height/2]
    axis.add_line(Line2D([-1, -1], y, **styles))
    axis.add_line(Line2D([+1, +1], y, **styles))
    axis.add_line(Line2D([0, 0], y, **styles)) 
    
def draw_hatches(axis, ymax, height=1.0, **styles):
    x_min    = axis.get_xlim()[0]
    x_max    = axis.get_xlim()[1]
    x_range  = x_max - x_min
    y_values = np.arange(0, height*ymax, 2*height) - height/2
    for y in y_values:
        axis.add_patch(Rectangle((x_min, y), x_range, 1, **styles, zorder=-1))

def draw_text(axis, x, y, s, **styles):
    text = axis.text(x, y, s, **styles)
    xmin, xmax, ymin, ymax = get_box_dimension(text)
    return xmin, xmax, ymin, ymax

def draw_ATLAS_label(axis, x=0.05, y=0.95, fontsize=25, extra='Internal', 
                     transform_x='axis', transform_y='axis', 
                     vertical_align='top', horizontal_align='left'):
    current_axis = plt.gca()
    plt.sca(axis)
    if vertical_align not in ['top', 'bottom']:
        raise ValueError('only "top" or "bottom" vertical alignment is allowed')
    if horizontal_align not in ['left', 'right']:
        raise ValueError('only "left" or "right" horizontal alignment is allowed') 
    transform = transforms.blended_transform_factory(parse_transform(transform_x), 
                                                     parse_transform(transform_y))
    text_atlas = axis.text(x, y, 'ATLAS', fontsize=fontsize, transform=transform,
                           horizontalalignment=horizontal_align,
                           verticalalignment=vertical_align,
                           fontproperties={"weight":"bold", "style":"italic"})
    xmin, xmax, ymin, ymax = get_box_dimension(text_atlas)
    text_width = xmax - xmin
    dx = text_width/15
    text_extra = axis.text(xmax + dx, ymin, extra, fontsize=fontsize, transform=axis.transAxes,
                           horizontalalignment='left', verticalalignment='bottom')
    plt.sca(current_axis)
    _, xmax, _, ymax = get_box_dimension(text_atlas)
    return xmin, xmax, ymin, ymax