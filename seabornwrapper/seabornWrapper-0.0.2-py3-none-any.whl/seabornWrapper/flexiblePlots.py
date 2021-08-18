import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

def custom_plot(data, x=None, y=None, hue=None,
                     plt_dims=(15,5),
                     ylim=None,
                     ylabel=None,
                     yfontsize=None,
                     xlim=None,
                     xlabel=None,
                     xfontsize=None,
                     titleText=None,
                     titleFontsize=None,
                     legendTitle=None,
                     legendLabels=None,
                     legendFontsize=None,
                     legendLoc=None,
                     allfontscale=None,
                     add_labels=True,
                     label_font=10,
                     color_palette=None,
                     n_colors=2,
                     text_color='black',
                     n_round=1,
                     outside_legend=True,
                     int_vals=False,
                     pct_vals=None,
                     plot_type='bar'):
 
   
    #create fig, ax to modify plot, add plot size here
    fig, ax = plt.subplots(figsize=plt_dims)
   
    #get current axis
    ax = plt.gca()
   
    #add color palette
    if color_palette is not None:
        sns.set_palette(color_palette, n_colors=n_colors)
   
    #create actual plot
    if plot_type=='bar':
        out_plt = sns.barplot(data=data, x=x, y=y, hue=hue, ax=ax, ci=False)
    elif plot_type=='line':
        out_plt = sns.lineplot(data=data, x=x, y=y, hue=hue, ax=ax, ci=False)
   
    #add labels if specified
    if add_labels:
        # Iterate through the list of axes' patches to add labels
        for i, p in enumerate(ax.patches):
            if int_vals and pct_vals is not None:
                val = str(int(round(p.get_height(), n_round))) + f'\n {pct_vals[i]}%'
            elif int_vals:
                val = int(round(p.get_height(), n_round))
            else:
                val = round(p.get_height(), n_round)
               
            ax.text(p.get_x() + p.get_width()/2., p.get_height(), val,
                    fontsize=label_font, color=text_color, ha='center', va='bottom')
   
    #modify title
    if titleText is not None:
        ax.set_title(titleText)
    if titleFontsize is not None:
        for ax in plt.gcf().axes:
            l = ax.get_title()
            ax.set_title(l, fontsize=titleFontsize)
   
    #modify x axis
    if xlim is not None:
        ax.set(xlim=xlim)
    if xlabel is not None:
        ax.set(xlabel=xlabel)
    if xfontsize is not None:
        for ax in plt.gcf().axes:
            l = ax.get_xlabel()
            ax.set_xlabel(l, fontsize=xfontsize)
   
    #modify y axis
    if ylim is not None:
        ax.set(ylim=ylim)
    if ylabel is not None:
        ax.set(ylabel=ylabel)
    if yfontsize is not None:
        for ax in plt.gcf().axes:
            l = ax.get_ylabel()
            ax.set_ylabel(l, fontsize=yfontsize)
           
    #modify legend
    leg = ax.get_legend()
    if legendLoc is not None:
        plt.legend(loc=legendLoc)
    if legendTitle is not None:
        leg.set_title(legendTitle)
    if legendLabels is not None:
        for t, l in zip(leg.texts, legendLabels):
            t.set_text(l)
   
    #allfontsize overwrites previous fontsize parameters       
    if allfontscale is not None:
        sns.set(font_scale=allfontscale)
   
    #more legend attributes
    if legendFontsize is not None:
        plt.setp(ax.get_legend().get_title(), fontsize=legendFontsize)
        plt.setp(ax.get_legend().get_texts(), fontsize=legendFontsize)
       
    if outside_legend:
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)
