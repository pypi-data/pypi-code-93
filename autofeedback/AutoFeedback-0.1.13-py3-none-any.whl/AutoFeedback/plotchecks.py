from AutoFeedback.varchecks import check_value
import matplotlib.pyplot as plt

def grab_figure(modname='main'):
    fighand=None
    try:
        plt.ion() #make any show commands non-blocking
        if modname == 'main':
            mod=__import__(modname)
        fighand=plt.gca()
        #plt.close() # close any open figures
    except:
        import sys
        sys.exit()
    return fighand

def extract_plot_elements(fighand,lines=True,patches=False,axislabels=False,axes=False,legend=False): 
    line_data, patch_data, axes_data, axis_labels, legend_data = None,None,None,None,[None]

    if lines: line_data = fighand.get_lines()

    if patches: patch_data = fighand.patches
 
    if axes: axes_data = [*fighand.get_xlim(), *fighand.get_ylim()]

    if axislabels: labels=[fighand.get_xlabel(), fighand.get_ylabel(), fighand.get_title()]

    if legend: 
        try:
            legend_data = [x.get_text() for x in fighand.get_legend().get_texts()]
        except:
            legend_data = []

    return line_data, patch_data, axes_data ,labels, legend_data

def check_linestyle(line,expected):
    style=line.get_linestyle()
    return (style in expected)

def check_marker(line,expected):
    style=line.get_marker()
    return (style in expected)

def check_colour(line,expected):
    color=line.get_color()
    return (color in expected)

def check_linedata(line,expline,no_diagnose=False):
    x,y=zip(*line.get_xydata())
    return expline.check_linedata(x,y,no_diagnose)

def check_patchdata(patch,exppatch):
    x, y = [], []
    for p in patch :
        xd, yd = p.get_xy()
        yd = p.get_height()
        x.append( xd + 0.5*p.get_width() )
        y.append( yd )
    return exppatch.check_linedata(x,y) 

def check_legend(legend_data,expected):
    return(legend_data and check_value(legend_data,expected)) 

def check_axes(l1,l2):
    return(check_value(l1,l2))

def reorder(a,b):
    from itertools import permutations,zip_longest
    for perm in permutations(b):
        if (all ([check_linedata(x,y,no_diagnose=True) for x,y in zip(perm,a)])):
            return (perm)
    return b

def e_string(error,label):
    if label:
        return error+'("'+label+'")'
    else:
        return error+"('')"
        
def check_plot(explines,exppatch=None,explabels=None,expaxes=None,explegend=False,output=False,check_partial=False,modname='main'):
    from AutoFeedback.plot_error_messages import print_error_message
    from itertools import zip_longest
    try:
        fighand = grab_figure(modname)
        lines, patch, axes,labels, legends= extract_plot_elements(fighand,
                                                                  lines=(len(explines)>0),\
                                                                  patches=exppatch,\
                                                                  axes=bool(expaxes),\
                                                                  axislabels=bool(explabels),\
                                                                  legend=explegend)
        
        explegends=[l.label for l in explines if l.label is not None]
        expline=""
        if not check_partial : 
            if explines : assert (len(lines)==len(explines)), "datasets"
            if explegend : assert (len(legends)==len(explegends)), "legend"
      
        if (explines):
            lines=reorder(explines,lines)

            for line,expline,legend in zip_longest(lines,explines,legends):
                if expline:
                    assert (check_linedata(line,expline)), e_string("data",expline.label)
                    if expline.linestyle:
                        assert(check_linestyle(line,expline.linestyle)), e_string("linestyle",expline.label)
                    if expline.marker: assert(check_marker(line,expline.marker)), e_string("marker",expline.label)
                    if expline.colour   : assert(check_colour(line,expline.colour)), e_string("colour",expline.label)
                    if expline.label and explegend :
                        if line.get_label()[0] != "_":
                            assert(check_legend(line.get_label(),expline.label)), "legend"
                        else:
                            assert(check_legend(legend,expline.label)), "legend"
                    if output: print_error_message(e_string("partial",expline.label),expline)
        if (exppatch):
            expline=exppatch
            assert(check_patchdata(patch,exppatch)), e_string("data","") 
            if output: print_error_message(e_string("partial",""),exppatch)
        if not explines and not exppatch :
            assert(False), "data"
        if explabels        : assert(check_axes(labels,explabels)), "labels"
        if expaxes          : assert(check_axes(axes,expaxes)),"axes"
        if output: print_error_message("success",expline)
        return(True)
    except AssertionError as error:
        if output: print_error_message (error,expline)
        return(False)




