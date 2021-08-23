import ctypes
from itertools import chain
import sys
import os
import numpy as np
import pandas as pd
from numpy import double
from numpy.ctypeslib import ndpointer
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from rpy2.robjects.packages import importr
from ctypes import *
phiMethods = ["extremes","range"]


def phi_control(y, phi_parms=None, method=phiMethods,
                extr_type=None, control_pts=None, asym=True):
    # call = todo call <- match.call() why this line
    if (phi_parms is not None):
        method = phi_parms["method"]
        extr_type = phi_parms["extr_type"]
        control_pts = phi_parms["control_pts"]

    # todo method <- match.arg(method, phiMethods) why this line?
    if method == "range":
        # todo create phi_range and control the parameters
        control_pts = phi_range(y,control_pts=control_pts)
    else:
        # create phi_extreme and control the parameters
        control_pts = phi_extremes(y, extr_type=extr_type,asym=asym)
        method = "extremes"
    phiP = {"method": method, "npts": control_pts["npts"], "control_pts": control_pts["control_pts"]}

    return phiP
def minmax(val_list):
    min_val = min(val_list)
    max_val = max(val_list)

    return (min_val, max_val)

def phi_extremes(y, extr_type="both", coef=1.5, asym=True):
    from sklearn.model_selection import train_test_split
    from rpy2.robjects.packages import importr
    # todo
    # extr.type <- match.arg(extr.type) probably delete this line
    control_pts = []
    npts = None
    if asym:

        y = y.to_list()
        from rpy2 import robjects as ro
        robustbase = importr("robustbase")
        extr = robustbase.adjboxStats(ro.FloatVector(y), coef=coef)
        r = minmax(y)
        if extr_type is None : extr_type = "both"
        if extr_type in ("both", "low"):
            ## adjL

            control_pts.append((extr[3][0], 1, 0))
        else:

            ## min

            control_pts.append( (r[0], 0, 0))

        ## median


        control_pts.append((extr[0][2], 0, 0))

        if (extr_type in ("both", "high")):

            ## adjH
            control_pts.append( (extr[3][1], 1, 0))
        else:
            ## max
            control_pts.append( (r[1], 0, 0))

        # if control_pts is a dataframe I can use this for row number, again rearrange according to datatype
        npts = len(control_pts)

    else:

        y = y.to_list()
        from rpy2 import robjects as ro
       # boxplot = importr("boxplot.stats")
        boxplot = ro.r['boxplot.stats']
        extr = boxplot(ro.FloatVector(y), coef=1.5)
        print(extr)
        print("any(x>extr[0][1] for x in extr[3]):",any(x>extr[0][1] for x in extr[3]))
        print("extr_type in (both, high)  :" ,extr_type in ("both", "high") )
        #extr = robustbase.adjboxStats(ro.FloatVector(y), coef=1.5)
        r = minmax(y)

        if (extr_type in ("both", "low")) & (any(x<extr[0][1] for x in extr[3])):

            ## adjL
            control_pts.append( (extr[0][0], 1, 0))
        else:
            ## min
            control_pts.append( (r[0], 0, 0))

        ## median
        control_pts.append( (extr[0][2], 0, 0))

        if (extr_type in ("both", "high") )& (any(x>extr[0][4] for x in extr[3])):

            ## adjH
            control_pts.append( (extr[0][4], 1, 0))
        else:
            ## max
            control_pts.append( (r[1], 0, 0))

            # if control_pts is a dataframe I can use this for row number, again rearrange according to datatype
            npts = len(control_pts)

    # return list(npts = npts,control_pts = as.numeric(control_pts.T)) deleted as.numeric part if doesnt work check again
    numpy_array = np.array(control_pts)
    transpose = numpy_array.T
    transpose_list = transpose.tolist()
    latten_list = list(chain.from_iterable(control_pts))
    return {"npts": npts, "control_pts": latten_list}

def phi_range(y, control_pts) :

  ## if it comes from pre-set env
  # just trying to check is the control_pts emoty or not rewrite according to datatype
  if type(control_pts) is dict :
      control_pts = np.reshape(np.array(control_pts["control_pts"]),(control_pts["npts"],int(len(control_pts["control_pts"])/control_pts["npts"])))

  if (type(control_pts) is not np.ndarray) or (control_pts is None) or (np.shape(control_pts)[1] > 3) or (np.shape(control_pts)[1] < 2):
       sys.exit('The control.pts must be given as a matrix in the form: \n < x, y, m > or, alternatively, < x, y >')

  npts = len(control_pts)
  dx = control_pts[1:,0] - control_pts[0:(npts-1),0]


  if(None  in dx) or (0 in dx ) :
    sys.exit("'x' must be *strictly* increasing (non - NA)")

  if (any(x>1 for x in control_pts[:,1]))  or  any(x<0 for x in control_pts[:,1]) :
    sys.exit("phi relevance function maps values only in [0,1]")


  control_pts = control_pts[np.argsort(control_pts[:, 0])]

  if(np.shape(control_pts)[1] == 2) :
    ## based on "monoH.FC" method
    dx = control_pts[1:,0] - control_pts[0:(npts-1),0]
    dy = control_pts[1:,1] - control_pts[0:(npts-1),1]
    Sx = dy / dx
    m = (Sx[1:] + Sx[0:(npts-2),])/2
    m = np.reshape(m,(len(m),1))
    m = np.insert(m,(0,len(m)),0,axis=0)
    control_pts = np.append(control_pts,m,axis=1)


  r = minmax(y)
  npts = np.shape(control_pts)[0]
  latten_list = list(chain.from_iterable(control_pts))

  return {"npts": npts, "control_pts": latten_list}
def phi2double(phi_parms):
    # need to know what phi.parms  has exactly, I guess just one item like range or extreme
    # so the value returns from that match(phi.parms$method,phiMethods) - 1 is 0 or NA . I need to confirm to right this part
    phi_parms_double = []
    if phi_parms["method"] == "extremes":
        phi_parms_double.append(0)
    elif phi_parms["method"] == "range":
        phi_parms_double.append(1)

    phi_parms_double.append(double(phi_parms["npts"]))
    phi_parms_double = np.append(phi_parms_double, phi_parms["control_pts"])

    return phi_parms_double
def phi(y, phi_parms=None, only_phi=True):
   if phi_parms is None:
       phi_parms = phi_control(y)
   n = len(y)
   path = os.path.abspath(os.curdir)
   if sys.platform == "win32":
       phi_c = cdll.LoadLibrary(path + r"\src\phi.dll")
   elif  sys.platform == "darwin":
       phi_c = cdll.LoadLibrary(path + r"\src\phi_mac.so")
   elif  sys.platform == "linux":
       phi_c = cdll.LoadLibrary(path + r"\src\phi_linux.so")

   try:
       py2phi = phi_c.py2phi
       py2phi.restype = None
       py2phi.argtypes = [ctypes.c_size_t,
                          ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
                          ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
                          ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]

       y_phi_all = np.empty((3 * n))
       py2phi(n, y.values, phi2double(phi_parms), y_phi_all)
       phis = {"y_phi": y_phi_all[0:n], "yd_phi": y_phi_all[n:2 * n], "ydd_phi": y_phi_all[2 * n:3 * n]}

       plt.plot(y, y_phi_all[0:n], '.')
       plt.show()
       if (only_phi):
           return phis["y_phi"]
       else:
           return phis
   except:
       print('OS %s not recognized, Only win32, macos or linux' % (sys.platform))



df = pd.read_csv('./data/dfs_fixed.cvs')
x = df["value"]
x = x.to_list()
train_data, test_data = train_test_split(df, test_size=0.2, random_state=7)
y = df["value"]
phit = phi_control(y,extr_type="high")
print(phit)
phi(y, phi_parms=phit)
'''

phi_parms = {"method" : "range" , "npts" : 2 , "control_pts": [0,0,3,3,3]}
print(phi2double(phi_parms))
df = pd.read_csv('data/accel_data.cvs')
x = df["acceleration"]
x = x.to_list()
train_data, test_data = train_test_split(df, test_size=0.2, random_state=7)
y = df["acceleration"]
control_pts = { "npts" : 2 , "control_pts":(10,0,0,15,1,0)}
de = phi_control(y, method="range",control_pts=control_pts)
print(de)
ph = phi_control(y,extr_type="both")
de = phi_control(y, method="range",control_pts=np.reshape(np.array((10,0,1,1,15,0,0,1)),(4,2)))
#control_pts = phi_extremes(y, extr_type = "high")

print(ph)
'''
