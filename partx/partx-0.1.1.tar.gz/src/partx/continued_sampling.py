import numpy as np
import copy
import random
from random import choice
import numpy as np
from itertools import product
from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.models import LinearColorMapper, BasicTicker, ColorBar
from bokeh.palettes import Category10
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern as M, RBF as R, ConstantKernel as C 
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
import scipy as sp
import numpy.matlib as mtlb
from numpy import linalg as la
from scipy.optimize import minimize
import pandas as pd
from sklearn.linear_model import LogisticRegression as LR
#import statsmodels.api as sm
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import joblib
import shutil
from typing import Tuple, Union, List, Callable, Sequence, Optional
from warnings import catch_warnings, simplefilter, filterwarnings
from numpy import arange
from numpy import vstack
from numpy import argmax
from numpy import asarray
from numpy.random import normal
from numpy.random import random
from scipy.stats import norm

    
import pathlib

from .models import SamplingMethod, PartitioningResult


import logging
from logging import getLogger, INFO, root


from pathos.multiprocessing import ProcessingPool as Pool

import time
import pickle

logging.basicConfig(level=logging.INFO)
logger = getLogger("partX")
verbose = True

test_function = None



def sl(sub_u: list, i_dim: int):  #get the region that we want to do partition
    '''
    Returns the desired partition region

    Parameters:
        sub_u (list): M * i_dim * 2 matrix that has the upper and lower bounds
        i_dim: the dimension of the subregion
    Returns:
        [np.ndarray, np.ndarray]: tuple of MxNx1 that are the separated upper and lower bounds
    '''
    sub_u1 = np.array(sub_u)
    assert sub_u1.shape[1] == i_dim, 'sub_u matrix must be i_dim dimensional'
    assert sub_u1.shape[2] == 2, 'sub_u matrix must be an M * i_dim * 2'
    assert np.apply_along_axis(lambda x: x[1] > x[0], 2, sub_u1).all(), 'sub_u Z-pairs must be in increasing order'
    sl_coordinate_lower = sub_u1[:, :, 0]  # Return first Z-value
    sl_coordinate_upper = sub_u1[:, :, 1]  # Return second Z-value

    return sl_coordinate_lower, sl_coordinate_upper

# def fun_reg_branching(sl_coordinate_lower: np.array, sl_coordinate_upper: np.array, i_dim: int, i_B: int, sub_r, sub_u: list) -> list:
#     '''
#     Partitioning Algorithm
#     Parameters:
#         [np.ndarray, np.ndarray]: tuple of MxNx1 that are the separated upper and lower bounds
#         i_dim(int):dimension
#         sub_u(list): defined region
        
#     Returns:
#         sub_r(list): sub-regions
#     '''
#     assert sl_coordinate_lower.ndim == 2, 'sl_coordinate_lower matrix must be 2 dimensional'
#     assert sl_coordinate_upper.ndim == 2, 'sl_coordinate_upper matrix must be 2 dimensional'
#     sl_coordinate_upper = sl_coordinate_upper.tolist()
#     sl_coordinate_lower = sl_coordinate_lower.tolist()
#     for j in range(len(sub_u)):
#         m = (np.array(sl_coordinate_upper[j])-np.array(sl_coordinate_lower[j])).tolist()
#         f_value = choice(m)
#         i_index = m.index(f_value)
#         for i in range(0, i_B):
#             l_coordinate_lower = copy.deepcopy(sl_coordinate_lower)
#             l_coordinate_upper = copy.deepcopy(sl_coordinate_upper)
#             l_coordinate_lower[j][i_index] = float((sl_coordinate_upper[j][i_index] - sl_coordinate_lower[j][i_index]) * i) / i_B + sl_coordinate_lower[j][i_index]
#             l_coordinate_upper[j][i_index] = float((sl_coordinate_upper[j][i_index] - sl_coordinate_lower[j][i_index]) * (i + 1)) / i_B + sl_coordinate_lower[j][i_index]
#             a = [[0]*2 for i in range(0, i_dim)]
#             for i in range(0, i_dim):
#                 a[i][0] = l_coordinate_lower[j][i]
#                 a[i][1] = l_coordinate_upper[j][i]
#             sub_r.append(a)

#     return sub_r

def tell_sample(X_all, Y_all, sub_r,i_dim,z,s_p,Y_p ):##########################
    if z!=0:
        for i in range(len(sub_r)):
            for m in range(len(X_all)):
                TELL = 1
                for j in range(i_dim):
                      if TELL ==1:
                        if X_all[m][j] < sub_r[i][j][1] and X_all[m][j] > sub_r[i][j][0]:
                            TELL = 1
                        else:
                            TELL = 0
                #print(TELL)
                if TELL == 1:
                    s_p[i].append(X_all[m])
                    Y_p[i].append(Y_all[m])
        return s_p, Y_p  
    
def sample_rate(L_est,classified, sub_r):#####################
    '''
   DECIDE sampling rate

    Parameters:
        L_est: sampling rate
        classified(list): # of classified region 
    Returns:
        L(list): re-ratio sampling rate

    '''
    L_con = []
    ratio_L = []
    L=[0]
    sub_rc = []
    for k in range(len(classified)):
        L_con.append(L_est[classified[k]])
        sub_rc.append(sub_r[classified[k]])
    for i in range(len(L_con)):
        ratio_L.append(L_con[i]/sum(L_con))
    a=0
    for m in range(len(ratio_L)):
        a+=ratio_L[m]
        L.append(a)
    return L, sub_rc, ratio_L

def continue_sampling(L, sub_rc, N_cont, i_dim, rng):##############
    '''
    Continue Sample Classified region N times

    Parameters:
        sub_rc (list): Sample space
        N_cont (int): Number of samples
        i_dim(int): dimension of the region
        L_est: sampling rate
    Returns:
        np.ndarray: Matrix of sampled points

    '''
    # a = np.random.uniform(0,1,N_cont)
    a = rng.uniform(0, 1, N_cont)
    n_sub = [0 for m in range(len(L)-1)]
    for i in range(len(a)):
        for j in range(len(L)):
            if a[i] > L[j] and a[i] < L[j+1]:
                n_sub[j]+=1 
    sample_c=[[] for j in range(len(sub_rc))]
    for k in range(len(sub_rc)):
        sample_c[k] = [[0]*n_sub[k]]*i_dim
    for m in range(len(sub_rc)):
         for n in range(0,i_dim):
            sample_c[m][n]=rng.uniform(sub_rc[m][n][0],sub_rc[m][n][1],n_sub[m]).tolist()
    return sample_c

def sam_c(sub_rc, n_sub, sample_c, s_p, sub_r, i_dim):###########
    X_all_c =[]
    s_c=[[] for i in range(len(sub_rc))]
    for k in range(len(sub_rc)):
        s_c[k] = [[0]*i_dim]*n_sub[k]
    for j in range(len(sub_rc)):
        for i in range(n_sub[j]):
            s_c[j][i] =  ([x[i] for x in sample_c[j]])
        s_c[j] = s_c[j] + s_p[len(sub_r)+j]
        X_all_c += s_c[j]
   # s_c = np.array(s_c)
    return s_c,X_all_c 

def g_c(s_c,Y_c,test_function, Y_p,sub_r):###############
    Y_all_c = []
    for k in range(0,len(s_c)):
        Y_c.append([])
        for i in range(len(s_c[k])-len(Y_p[len(sub_r)+k])):
            current = test_function(s_c[k][i]) 
            Y_c[k].append(current)
        if len(Y_p[len(sub_r)+k])!=0:
            Y_c[k]+=Y_p[len(sub_r)+k]
        Y_all_c += Y_c[k]
    return Y_c,Y_all_c

def sample_g(sub_r: list, n: int, i_dim:int, rng) -> list:#########
    '''
    Sample sub_r n times

    Parameters:
        sub_r (list): Sample space
        n (int): Number of samples
        i_dim(int): dimension of the region
    Returns:
        np.ndarray: Matrix of sampled points

    '''
    sub_r1 = np.array(sub_r)
    assert sub_r1.shape[1] == i_dim, 'sub_r matrix must be 3-dimensional'
    assert sub_r1.shape[2] == 2, 'sub_r matrix must be MxNx2'
    assert np.apply_along_axis(lambda x: x[1] > x[0], 2, sub_r1).all(), 'sub_r Z-pairs must be in increasing order'

    return np.apply_along_axis(lambda x: rng.uniform(x[0], x[1], n), 2, sub_r1).tolist()


def sam(sub_r: list,  n: int, sample: np.array, s: list,s_p:list) -> list:###############
    '''
    modify the points 

    Parameters:
        sub_r (list): Sample space
        n (int): Number of samples

    Returns:
        np.array: Matrix of sampled points

    '''
    X_all =[]
    for j in range(len(sub_r)):
        for i in range(n):
            s[j][i] =  ([x[i] for x in sample[j]])
        s[j] = s[j] + s_p[j]
        X_all += s[j]
    #s = np.array(s)
    return s, X_all


def g(s: np.array, Y, test_function,Y_p:list) -> list:  #True values
    '''
    calculate robustness values

    Parameters:
        s (np.array): Sample points
        test_fucntion (function)

    Returns:
        list: Matrix of robustness values

    '''
    Y_all = []
    for k in range(0,len(s)):
        Y.append([])
        for i in range(len(s[k])-len(Y_p[k])):
            current = test_function(np.array(s[k][i])) 
            Y[k].append(current)
        if len(Y_p[k])!=0:
            Y[k]+=Y_p[k]
        Y_all += Y[k]
    return Y,Y_all


def vol(sub_u:list,i_dim: int) -> int:    #calculate the volume of undefined area
    '''
    calculate defined regions‘ volume
    Parameters:
        sub_u(list) :defined regions
        i_dim(int) : dimension of these regions
    

    Returns:
        int: the volume of that regions

    '''
    v = 0
    for i in range(len(sub_u)):
        a = []
        for j in range(i_dim):
            a.append ((sub_u[i][j][1] - sub_u[i][j][0]))
        #print(a)
        v += np.prod(a)# * (sub_u[i][2][1] - sub_u[i][2][0])* (sub_u[i][3][1] - sub_u[i][3][0])* (sub_u[i][4][1] - sub_u[i][4][0])
    
    #print(v)
    return v

def surrogate(model, X):
    '''
    predict for the Predicted values of BO
    Parameters:
        model
        X(np.array)
    

    Returns:
        predicted values

    '''
	# catch any warning generated when making a prediction
    with catch_warnings():
        # ignore generated warnings
        simplefilter("ignore")
        return model.predict(X, return_std=True)
    
def acquisition(X: np.array, Xsamples: np.array, model):
    '''
    calculate the best surrogate score found so far
    Parameters:
        model; the GP models
        X(np.array): sample points 
        Xsample(np.array): new sample points for BO
    

    Returns:
        sample probabiility of each sample points

    '''
    # calculate the best surrogate score found so far
    yhat, _ = surrogate(model, X)
    best = min(yhat)
    # calculate mean and stdev via surrogate function
    mu, std = surrogate(model, Xsamples)
    #mu = mu[:, 0]
    # calculate the probability of improvement
    probs = norm.cdf((mu - best) / (std+1E-9))
    return probs

def opt_acquisition(X: np.array, y: np.array, model,n_b:int ,i_dim:int, sub_r:list, rng):
    '''
    get the sample points
    Parameters:
        X(np.array): sample points 
        y(np.array): corresponding rebustness values
        model: the GP models 
        n_b(int): the number of sample points to construct the robustness values
        i_dim(int): dimesion
        sub_r(list): subregions
    

    Returns:
         min_bo(np.array): the new sample points by BO

    '''
    # random search, generate random samples
    samplebo = [[[0]*(n_b)] for m in range(i_dim)]
    for k in range(i_dim):
        samplebo[k] = rng.uniform(sub_r[k][0],sub_r[k][1],n_b)
    sbo = [[[0]*i_dim] for p in range(n_b)]
    for l in range(n_b):
        sbo[l] = ([x[l] for x in samplebo])
    # calculate the acquisition function for each sample
    scores = acquisition(X, sbo, model)
    # locate the index of the largest scores
    ix = argmax(scores)
    min_bo = np.array(sbo)[ix]
    return min_bo

def Bayesian_optimization(s:np.array , Y:list, n_bo: int, i_dim:int, sub_r:list,test_function,n_b:int, rng):
    '''
    calculate the best surrogate score found so far
    Parameters:
        s(np.array): sample points
        Y(list): robustness values
        n_bo(int): number of Bayesian Optimization sampling
        i_dim(int): dimension
        sub_r(list): subregions
        test_function: the test function
        n_b(int): number of points to construct GPs in BO (default = 100)
    

    Returns:
        S_BO(np.array): updated sample points
        Y(list): corresponding updated robuseness values

    '''
    s_bo = []
    s_bo_all = []
    Y_all = []
    for i in range(len(s)):
        X = s[i]
        for j in range(n_bo):
            model = GaussianProcessRegressor()
            model.fit(X, Y[i])
            #print('1')
            # select the next point to sample
            min_bo = opt_acquisition(X, Y[i], model,n_b,i_dim, sub_r[i], rng)
            # sample the point
            actual = test_function(min_bo)
            # add the data to the dataset
            X = vstack((X, [min_bo]))
            X = list(X)
            Y[i].append(actual)
        s_bo.append(X)
        s_bo_all += X
        Y_all+=Y[i]
    #s_bo = np.array(s_bo)
    return s_bo,Y,s_bo_all, Y_all


def model_construction(s: np.array, Y: list, v_s: int, sub_r: list, lower, upper, level: list, z: int, q: int, i_dim: int, fal_num:int, n_model:int,alpha:float, number_a:list, partition_list: list, root_path, rng) -> Tuple[np.array,np.array]:   ##Gaussian process 
    '''
    construct Gaussian processes and confidence intervals

    Parameters:
        s (np.array): Sample points
        Y (list): robustness values
        v_s (int): volume of sub_u
        sub_r(list): partitioned subregions
        z(int): # of repliction 
        q(int): # of iteration
        i_dim(int): # of dimension
        level(list): the quantiles (example:[0.5,0.6])
        fal_num(int): # of points to construct the falsification volume
        n_model: # of points to construct thr lower/ upper bounds 
        alphs(float): mis-coverage level
        list_star(list): subregion number
    Returns:
        model_lower(np.array): lower bounds of confidence intervals of each subregions
        model_upper(np.array): lower bounds of confidence intervals of each subregions
        models: all GP models corresponding sub-regions
    '''
    level_quantile = [[0]*len(level) for i in range(len(s))]
    L_est = []#############
    for i in range(len(sub_r)):
        X = np.array(s[i])#########
        y = Y[i]
        kernel = R([1]*i_dim) * M([1]*i_dim) #input kernel for GPs 
        gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=i_dim)
        #gp = GaussianProcessRegressor()
        gp.fit(X, y) #fit sample points to Grussian Process
        #print(q)
        #print(z)
        name =  root_path + '/models/'+'trainmodel' +str(0)+ str(q+1) +str(0)+ str(partition_list[i]) +str(0)+str(number_a[i])+'.m'  #save the models # modify your name here
        joblib.dump(gp, name) 
        #model = joblib.load(name)
        n_s = int(fal_num*vol([sub_r[i]],i_dim)/v_s) # assign corresponding number of points to subregions
        n_ss = n_s + n_model
        samplegp = [[[0]*(n_ss)] for m in range(i_dim)]
        for k in range(i_dim):
            samplegp[k] = rng.uniform(sub_r[i][k][0],sub_r[i][k][1],n_ss)
            #np.apply_along_axis(lambda x: np.random.uniform(x[0], x[1], n), 2, sub_r)
        sgp = [[[0]*i_dim] for p in range(n_ss)]
        for l in range(n_ss):
            sgp[l] = ([x[l] for x in samplegp])
        y_pred_st, sigma_st = gp.predict(sgp, return_std=True)   ##predict new sample points
        cdfn = []############
        #print(sigma_st)
        for e in range(len(y_pred_st)):###############
            cdfn.append(norm.cdf(0,loc=y_pred_st[e], scale=sigma_st[e]**2))#############
        f0 = sum(cdfn)#############
        L_est.append(f0*vol([sub_r[i]], i_dim))###################
        idxs = rng.integers(0, n_s + n_model, n_model)
        y_pred = y_pred_st[idxs]
        y_sigma = sigma_st[idxs]
        for o in range(len(level)):
            level_quantile[i][o] = stats.norm.interval(level[o],y_pred_st,sigma_st)[0]
        i_s = np.argmin(y_pred, axis=0)      #find maximum and minimum values of predicted values
        i_ss = np.argmax(y_pred, axis=0) 
        #conf_intveral_1 = stats.norm.interval(1-alpha, loc=y_pred[i_s], scale=y_sigma[i_s])
        #a = list(conf_intveral_1)
        #lower.append(a[0])
        #conf_intveral_2 = stats.norm.interval(1-alpha, loc=y_pred[i_ss], scale=y_sigma[i_ss])
        #b = list(conf_intveral_2)
        #upper.append(b[1])
        sigma_s = max(y_sigma)
        v_min = y_pred[i_s]-1.96*sigma_s   ##try to build the confidence interval
        v_max = y_pred[i_ss] + 1.96*sigma_s
        lower.append(v_min)
        upper.append(v_max)
    model_lower = np.array(lower)
    model_upper = np.array(upper)
    return model_lower, model_upper,level_quantile, L_est ###########
              
def region_classify(lower: list, upper:list , sub_r:list, theta_undefined, theta_plus, theta_minus, tpn, tmn, tun):  
    '''
    classify the regions

    Parameters:
        lower(np.array): lower bounds of confidence intervals of each subregions
        upper(np.array): lower bounds of confidence intervals of each subregions
        sub_r(list): partitioned subregions

       
    Returns:
        theta_plus, theta_minus, theta_undefined: classified regions
        tpn, tmn, tun: number of classified region 
    '''
    for i in range(0,len(lower)):
        if lower[i]>0:
            theta_plus.append(sub_r[i])
            tpn.append(i)
        elif upper[i]<0:
            theta_minus.append(sub_r[i])
            tmn.append(i)
        else:
            theta_undefined.append(sub_r[i])
            tun.append(i)                                     
    return theta_plus, theta_minus, theta_undefined,tpn, tmn, tun
                                     
def find_min(Y_subm,num,s: np.array,Y: list,i_dim:int) -> list:    #the minimum robustness values
    '''
    find minimum robustness values

    Parameters:
        s (np.array): Sample points
        Y(list): robustness values
        i_dim(int): the dimension of subregion

    Returns:
         num(list): the number of minmum points and corresponding robustness values
         Y_subm(list): the minmum points

    '''
    Y_subm = [[] for i in range(len(s))]
    num = [[0]*i_dim for i in range(len(s))]
    for k in range(0,len(s)):
        Y_subm[k] = min(Y[k])
        inum = list(Y[k]).index(Y_subm[k])
        num[k][0] = k
        num[k][1] = inum
    return num,Y_subm

def part_percent(level:list, sub_r:list, v_s,level_quantile, p_quantile,i_dim: int):
    '''
    calculate falsification volume for each sub_regions

    Parameters:
        level(list): the quantile set
        sub_r(list): the subregions
        v_s: volume of the whole region
        level_quantile: the predicted values to calculate fal_volume
        i_dim(int): the dimension
    Returns:
        p_quantile(list): fal_volume for subregions
    '''
    for i in range(len(level)):
        for j in range(len(sub_r)):
            a_s = [x for x in level_quantile[j][i] if x < 0]
            p_quantile[i]. append((len(a_s)/len(level_quantile[j][i]))*(vol([sub_r[j]],i_dim)/v_s))
    return p_quantile

def part_listc(i_dim, part_num, iteration):
    l = []
    k = []
    for i in range(part_num, i_dim):
        l.append(i)
    for j in range(i_dim):
        k.append(j)
    part_index = k*round((iteration-part_num)/i_dim)
    part_list = l + part_index
    return part_list

def fun_reg_branching(sl_coordinate_lower: np.ndarray, sl_coordinate_upper: np.ndarray, i_dim: int, i_B: int, sub_r, sub_u: list, part_list:list, z: int,list_subr:list, partition_list) -> list:#########
    '''
    Partitioning Algorithm
    Parameters:
        [np.ndarray, np.ndarray]: tuple of MxNx1 that are the separated upper and lower bounds
        i_dim(int):dimension
        sub_u(list): defined region
        part_list(list): the list to instruct the partition
        iteration(int): which itertion
        
        
    Returns:
        sub_r(list): sub-regions
    '''
    assert sl_coordinate_lower.ndim == 2, 'sl_coordinate_lower matrix must be 2 dimensional'
    assert sl_coordinate_upper.ndim == 2, 'sl_coordinate_upper matrix must be 2 dimensional'
    sl_coordinate_upper = sl_coordinate_upper.tolist()
    sl_coordinate_lower = sl_coordinate_lower.tolist()
    list_star = [[] for i in range(2*len(sub_u))]
    for j in range(len(sub_u)):
        m = (np.array(sl_coordinate_upper[j]) - np.array(sl_coordinate_lower[j])).tolist()
        #f_value = choice(m)
        #i_index = m.index(f_value)
        i_index = part_list[partition_list[j]]
        for i in range(0, i_B):
            l_coordinate_lower = copy.deepcopy(sl_coordinate_lower)
            l_coordinate_upper = copy.deepcopy(sl_coordinate_upper)
            l_coordinate_lower[j][i_index] = float((sl_coordinate_upper[j][i_index] - sl_coordinate_lower[j][i_index]) * i) / i_B + sl_coordinate_lower[j][i_index]
            l_coordinate_upper[j][i_index] = float((sl_coordinate_upper[j][i_index] - sl_coordinate_lower[j][i_index]) * (i + 1)) / i_B + sl_coordinate_lower[j][i_index]
            a = [[0]*2 for i in range(0, i_dim)]
            for i in range(0, i_dim):
                a[i][0] = l_coordinate_lower[j][i]
                a[i][1] = l_coordinate_upper[j][i]
            sub_r.append(a)
            if list_subr != []:
                list_star[2*j] = 2*(list_subr[j]) -1
                list_star[2*j+1] = 2*(list_subr[j])
            else:
                list_star = []
                

    return sub_r,list_star

def tell_partition(sub_r,i_dim,v_s):##################
    partition_list = []
    for m in range(len(sub_r)):
        partition_list.append(int(math.log(int(v_s/vol([sub_r[m]],i_dim)), 2)))
    return partition_list


def budget_control(sub_r, i_dim, v_s):###############
    bc_rate = []
    rate_bc = []
    Rate_bc=[0]
    for i in range(len(sub_r)):
        bc_rate.append(vol([sub_r[i]],i_dim)/v_s)
    for j in range(len(bc_rate)):
        rate_bc.append(bc_rate[j]/sum(bc_rate))
    a = 0
    for k in range(len(rate_bc)):
        a+=rate_bc[k]
        Rate_bc.append(a)
    return Rate_bc

def sam_bc(sub_rc, n_sub, sample_c, s, i_dim):###########
    s_c=[[] for i in range(len(sub_rc))]
    for k in range(len(sub_rc)):
        s_c[k] = [[0]*i_dim]*n_sub[k]
    for j in range(len(sub_rc)):
        for i in range(n_sub[j]):
            s_c[j][i] =  ([x[i] for x in sample_c[j]])
        #print(len(s_c[j]))
        #s_c[j] += s[j]
        #X_all_c += s_c[j]
   # s_c = np.array(s_c)
    return s_c

def g_bc(s_c,Y_c,test_function, Y):###############
    Y_all_c = []
    for k in range(0,len(s_c)):
        Y_c.append([])
        for i in range(len(s_c[k])):
            current = test_function(s_c[k][i]) 
            Y_c[k].append(current)
        #print(len(Y_c[k]))
        Y_c[k]+=Y[k]
        Y_all_c += Y_c[k]
    return Y_c,Y_all_c


def replicate(data):
    global test_function
    start_time = time.time()
    q, sub_u, i_dim, i_B, alpha, n, level, iteration, min_volume, max_budget, fal_num, n_model, n_bo, n_b, sample_method, part_num, N_cont, root_path, seed = data

    rng = np.random.default_rng(seed)

    P = []
    K = []
    TPP = []
    TMP = []
    TMV = []
    TPV = []
    TUV = []
    H = []
    evl = []
    p_iter=[]
    v_s = vol(sub_u,i_dim)
    region = sub_u
    #print(v_s)
    S=[]
    # count = i
    t_fal = []
    X_minf = []
    Y_minf = []
    number_subregion = []
    part_list = part_listc(i_dim, part_num, iteration)
    fal_con = []#########

    sub_u = region
    theta_plus=[]
    theta_minus=[]
    V=[]
    TP=[]
    TM=[]
    budgets = []
    D=0
    p_fal = [[] for j in range(len(level))]
    fal_iter = [[] for j in range(len(level))]
    z=0
    Y_min = []
    X_min = []
    True_fal = []
    number_sub = []
    v_min = [vol(sub_u,i_dim)]
    d1 = 0
    d2 = 0
    list_subr = [1]
    #TP_iter = []
    #TM_iter = []
    #TU_iter = []
    sub_rc = []###########
    falsification_con = [[] for k in range(len(level))]##########
    sample_c = []#######
    X_all_c = []
    partition_list = [0]#########
    list_region = []
    for z in range(iteration):  ##change for iteration
        print("PartX: Replication {}, Iteration {}".format(q + 1, z))
        v = vol(sub_u,i_dim)
        if min(v_min) > min_volume*v_s and D + i_B*(n_bo+n)*len(sub_u) + N_cont < max_budget: ##########
            if sub_u != []:
                sl_coordinate_lower, sl_coordinate_upper = sl(sub_u,i_dim)
                sub_r = []
                sub_r, list_star = fun_reg_branching(sl_coordinate_lower, sl_coordinate_upper, i_dim, i_B, sub_r , sub_u, part_list,z,list_subr, partition_list)
            else:
                sub_r = []
                list_star = []

            s_p = [[] for i in range(len(sub_r)+len(sub_rc))]
            Y_p = [[] for i in range(len(sub_r)+len(sub_rc))]
            sub_r1 = sub_r + sub_rc#########
            if z!=0: #################
                s_p, Y_p = tell_sample(X_all, Y_all, sub_r1,i_dim,z,s_p,Y_p)######################
            
            if sub_u != []:
                sample = sample_g(sub_r, n,i_dim, rng)
                #print(sample)
                s=[[[0]*i_dim]*n for i in range(len(sub_r))]###########
                s,X_all = sam(sub_r, n, sample, s,s_p)
                #print(X_all)
                Y = []
                Y,Y_all = g(s, Y, test_function,Y_p)
                #print(Y_all)
                if sample_method == SamplingMethod.BAYESIAN: 
                    s_bo, Y,s_bo_all, Y_all = Bayesian_optimization(s , Y, n_bo,i_dim,sub_r,test_function,n_b, rng)
                    s = s_bo
                    X_all = s_bo_all
            else:
                X_all = []
                Y_all = []
                s = []
                Y = []

            if sub_rc !=[]:
                n_sub = [0 for m in range(len(L)-1)]
                s_c,X_all_c = sam_c(sub_rc, n_sub, sample_c,s_p, sub_r, i_dim)
                Y_c = []
                Y_c, Y_all_c = g_c(s_c, Y_c, test_function, Y_p, sub_r)
                X_all += X_all_c
                Y_all += Y_all_c
                s += s_c
                Y += Y_c
            #sub_all = []
            #number_all = []
            #for p in range(len(s)):
                #sub_all.append([sub_r1[p]]*len(s[p]))
                #number_all.append(list_star[p]*len(s[p]))
    
            tf = [x for x in Y_all if x < 0]
            if tf != []:
                True_fal.append(len(tf)/len(Y_all))
            else: 
                True_fal.append(0)
            #print(true_fal)
            
            Y_subm = [[] for i in range(len(s))]
            num = [[0]*i_dim for i in range(len(s))]
            num_min = []
            num, Y_subm = find_min(Y_subm,num,s,Y,i_dim)
            kf = Y_subm.index(min(Y_subm))
            num_min.append(num[kf])
            X_min.append(s[num_min[0][0]][num_min[0][1]])
            Y_min.append(min(Y_subm))
            lower=[]
            upper=[]
            if sub_rc !=[]:
                    D += len(sub_r) * (n+n_bo)+N_cont
            else: 
                    D += len(sub_r) * (n+n_bo)    
            sub_r = sub_r1
            number_a = list_star+list_region
            partition_list = tell_partition(sub_r, i_dim, v_s)
            model_lower, model_upper,level_quantile, L_est = model_construction(s, Y, v_s, sub_r, lower, upper, level, z, q, i_dim, fal_num, n_model,alpha,number_a, partition_list, root_path, rng)
            #print(L_est)
            p_quantile = [[] for i in range(len(level))]
            p_quantile = part_percent(level, sub_r, v_s,level_quantile, p_quantile,i_dim)
            #print(p_quantile)
            theta_undefined=[]
            theta_plus=[]
            theta_minus = []
            tpn = []
            tmn = []
            tun = []
            theta_plus, theta_minus, theta_undefined, tpn, tmn, tun = region_classify(lower, upper , sub_r, theta_undefined, theta_plus, theta_minus, tpn, tmn, tun)
            tp =[]
            theta_d = []
            v_min = []
            theta = theta_undefined+theta_plus+theta_minus
            classified = tmn+tpn##############
            global classification
            classification = [[0] for i in range(len(sub_r))]
            if len(tpn)!=0:
                for w in range(len(tpn)):
                    classification[tpn[w]] = 'theta plus'
            if len(tmn)!=0:        
                for e in range(len(tmn)):
                    classification[tmn[e]] = 'theta mius'
            if len(tun)!=0:
                for r in range(len(tun)):
                    classification[tun[r]] = 'theta undefined'   
            L=[0]
            ratio_L = []
            if len(classified)!=0:########
                L, sub_rc, ratio_L = sample_rate(L_est, classified, sub_r)############
                sample_c = continue_sampling(L, sub_rc, N_cont, i_dim, rng)###########
                #print(sample_c)
            else: #######
                sub_rc = []##########

            # sub_a = theta_undefined + sub_rc########
            # partition_list = tell_partition(sub_a,i_dim, v_s)#########
            for i in range(len(theta)):
                v_min.append(vol([theta[i]],i_dim))
            if min(v_min) < min_volume*v_s:#########
                tp = tpn+tmn+tun
                
            if min(v_min) > min_volume*v_s:###########
                tp = tpn+tmn
            list_subr = []    
            if tun!=[]:
                for b in range(len(tun)):
                    list_subr.append(number_a[tun[b]])
            Z = []
            Q = []
            list_region = []
            if classified!=[]:
                for i in range(len(classified)):##################
                    theta_d.append(sub_r[classified[i]])
                    list_region.append(number_a[classified[i]])
                    for j in range(len(level)):
                        p_fal[j].append(p_quantile[j][classified[i]])
            #number_sub.append(list_region)
            
            number_p = []
            Z_p = []######
            Q_p = []#######
            for l in range(len(s)):###########
                #rint(len(s[l]))
                for o in range(len(s[l])):
                    Z_p.append(partition_list[l])
                    Q_p.append(q+1)
                    number_p.append(number_a[l])
            Z = [z+1]*len(sub_r)##########
            Q = [q+1]*len(sub_r)######## 
            p_list = []
            for w in range(len(partition_list)):
                p_list.append(partition_list[w])
                
            subregion = pd.DataFrame({'subregion': sub_r,'replication': Q,'deepth': p_list,'number':number_a,'clssification':classification})
            subregion.to_csv(root_path + '/subregions'+str(q+1)+'.csv', mode='a', header=False)
            
            points = pd.DataFrame({'X': X_all,'Y': Y_all, 'replication': Q_p,'deepth': Z_p, 'nunmber': number_p})
            points.to_csv(root_path + '/points'+str(q+1)+'.csv', mode = 'a', index=False,sep=',',header =False)
            #list_subr = [x for x in list_star if x not in list_region]
            if sub_rc !=[]:
                prob_metric = pd.DataFrame({'L':L_est,'subregion': sub_r, 'replication': Q,'deepth': p_list,'number':number_a,'clssification':classification})
                prob_metric.to_csv(root_path + '/prob_metric'+str(q+1)+'.csv', mode = 'a', index=False,sep=',',header =False)
            
            for i in range(len(level)):
                fal_iter[i].append(sum(p_quantile[i]))
            #print(fal_iter)
            if len(theta_plus)!= 0:
                    d1 = vol(theta_plus,i_dim)
            if len(theta_minus)!= 0:
                d2 = vol(theta_minus,i_dim)
            d = d1 + d2
            #print(d)
            V.append(d/v_s)
            TP.append(d1/v_s)
            TM.append(d2/v_s)
            budgets.append(len(sub_r))
#             print(S)
            if theta_undefined !=[]:
                sub_u = theta_undefined
            else:
                sub_u = []
        else:##########################
            Rate_bc = budget_control(sub_r, i_dim, v_s)
            
            sample_c = continue_sampling(Rate_bc, sub_r, max_budget-D, i_dim, rng)
            n_sub = [0 for m in range(len(Rate_bc)-1)]
            s_c = sam_bc(sub_r, n_sub, sample_c,s, i_dim)
            #print(len(X_all_c))
            Y_c = []
            Y_c, Y_all_c = g_bc(s_c, Y_c, test_function, Y)
            # print(len(Y_all_c))
            X_all_c =[]
            for u in range(len(s_c)):
                s_c[u] += s[u]
                X_all_c += s_c[u]
                
            X_all = X_all_c
            Y_all = Y_all_c
            lower=[]
            upper=[]
            lower, upper,level_quantile, L_est = model_construction(s_c, Y_c, v_s, sub_r, lower, upper, level, z, q, i_dim, fal_num, n_model,alpha,number_a, partition_list, root_path, rng)
            p_quantile = [[] for i in range(len(level))]
            p_quantile = part_percent(level, sub_r, v_s,level_quantile, p_quantile,i_dim)
            theta_undefined=[]
            theta_plus=[]
            theta_minus = []
            tpn = []
            tmn = []
            tun = []
            theta_plus, theta_minus, theta_undefined, tpn, tmn, tun = region_classify(lower, upper , sub_r, theta_undefined, theta_plus, theta_minus, tpn, tmn, tun)
            theta = theta_undefined+theta_plus+theta_minus
            classification = [[] for i in range(len(sub_r))]
            if len(tpn)!=0:
                for w in range(len(tpn)):
                    classification[tpn[w]].append('theta plus')
            if len(tmn)!=0:        
                for e in range(len(tmn)):
                    classification[tmn[e]].append('theta mius')
            if len(tun)!=0:
                for r in range(len(tun)):
                    classification[tun[r]].append('theta undefined')
            classified = tmn+tpn##############
            Z_p = []######
            Q_p = []#######
            number_p = []
            for l in range(len(s_c)):###########
                for o in range(len(s_c[l])):
                    Z_p.append(partition_list[l])
                    Q_p.append(q+1)
                    number_p.append(number_a[l])
            #print(number_a)
            p_list = []
            for w in range(len(partition_list)):
                p_list.append(partition_list[w])
            subregion = pd.DataFrame({'subregion': sub_r,'replication': Q,'deepth': p_list,'number':number_a,'clssification':classification})
            subregion.to_csv(root_path + '/subregions'+str(q+1)+'.csv', mode='a', header=False)
            subregion.to_csv(root_path + '/subregions.csv', mode='a', header=False)
            points = pd.DataFrame({'X': X_all,'Y': Y_all, 'replication': Q_p,'deepth': Z_p, 'nunmber': number_p})
            points.to_csv(root_path + '/points'+str(q+1)+'.csv', mode = 'a', index=False,sep=',',header =False)
            #list_subr = [x for x in list_star if x not in list_region]
            if sub_rc !=[]:
                prob_metric = pd.DataFrame({'I':L_est,'subregion': sub_r, 'replication': Q,'deepth': p_list,'number':number_a,'clssification':classification})
                prob_metric.to_csv(root_path + '/prob_metric_final'+str(q+1)+'.csv', mode = 'a', index=False,sep=',',header =False)
            if len(theta_plus)!= 0:
                    d1 = vol(theta_plus,i_dim)
            if len(theta_minus)!= 0:
                d2 = vol(theta_minus,i_dim)
            d = d1 + d2
            
            
            V.append(d/v_s)
            TP.append(d1/v_s)
            TM.append(d2/v_s)
            for t in range(len(p_quantile)):###########
                falsification_con[t].append(sum(p_quantile[t]))###########
            fal_v = [[] for i in range(len(level))]
            for i in range(len(level)):
                fal_v[i]= sum(p_fal[i])
            TMV.append(theta_minus)
            TPV.append(theta_plus)
            TUV.append(theta_undefined)
            S.append(D)
            P.append(z)
            K.append(V)
            TPP.append(TP)
            TMP.append(TM)
            H.append(fal_v)
            evl.append(budgets)
            p_iter.append(fal_iter)
            dk = Y_min.index(min(Y_min))
            t_fal.append(True_fal)
            X_minf.append(X_min[dk])
            Y_minf.append(min(Y_min))
            number_subregion.append(number_sub)
            fal_con.append(falsification_con)###############
            break

    replication_time = time.time() - start_time
    return [P, K, TPP, TMP, TPV, TMV, TUV, H, S, evl, p_iter, Y_minf, X_minf, t_fal, number_subregion, fal_con, replication_time]

def _part_classify(sub_u: list, i_dim: int, i_B: int, alpha: float, test_function: Callable[[], float], n:int,level:list,replication:int, iteration: int,min_volume:float,max_budget:int, fal_num: float,n_model: int,n_bo:int, n_b:int, sample_method,part_num:int, N_cont:int, root_path, start_seed):######
    '''
    algorithm

    Parameters:
        sub_u(list): region
        i_dim(int): dimension of the region
        i_B: # of partition (default = 2)
        alpha(float): miscoverage level
        test_function: the callable function 
        n(int): the number of uniform sampling for each subregions
        level(list): the list of quantile of falsification volume (ex: [0.5,0.7])
        replication(int): number of replication
        iteration(int): number of iteration for each replication (default = 100)
        min_volume(float): stop condition of the volume (default = 0.001)
        max_budget(int): number of max budget for one replication
        fal_num (int): the number of sample points to calculate the falsification volume
        n_model(int): number of sample points to do the GP prediction to construct the CI
        n_bo(int): number of Bayesian Optimization sampling
        n_b(int): number of points to construct GPs in BO (default = 100)
        sample_method(str): 'BO sampling' or 'uniform sampling'
        part_num: number of way to start partitioning
        N_cont(int): continue sampling budget for each iteration
        
    Returns:
        iteration(list): iteration numbers to finish one replication
        percentage of defined region(list): percentage of volume of theta_plus+theta_minus over the volume of whole region for each iteration
        percentage of theta_plus (list): percentage of volume of theta_plus over the volume of whole region for each iteration
        percentage of theta_minus(list): percentage of volume of theta_minus over the volume of whole region for each iteration
        theta_plus(list): theta_plus( the regions satisfy trajectory)
        theta_minus(list): theta_minus( the regions violate trajectory)
        theta_undefined(list): the regions remain to be defined
        falsidication volumes(list): the falsification volume for each quantile
        budgets(list): overall budget for one replication
        budgets for each iteration(list): budget of each iteration for one replication
        falsification volume for each iteration(list): the falsification volume for each quantile of each iteration
        The minimum robustness value(list): minimum robustness value of one repliacation
        The minimum robustness value corresponding point(list): the corresponding sanple point
        percentage of falsifying points of robustness values(list): for each iteration, the percentage of negative robustness values
    
    '''
    inputs = []
    for q in range(replication):
        seed = start_seed + q
        data = (q, sub_u, i_dim, i_B, alpha, n, level, iteration, min_volume, max_budget, fal_num, n_model, n_bo, n_b, sample_method, part_num, N_cont, root_path, seed)
        
        inputs.append(data)

    pool = Pool()
    results = list(pool.map(replicate, inputs))

    P = []
    K = []
    TPP = []
    TMP = []
    TPV = []
    TMV = []
    TUV = []
    H = []
    S = []
    evl = []
    p_iter = []
    Y_minf = []
    X_minf = []
    t_fal = []
    number_subregion = []
    fal_con = []

    for index, result in enumerate(results):
        __P, __K, __TPP, __TMP, __TPV, __TMV, __TUV, __H, __S, __evl, __p_iter, __Y_minf, __X_minf, __t_fal, __number_subregion, __fal_con, _replication_time = result

        P.extend(__P)
        K.extend(__K)
        TPP.extend(__TPP)
        TMP.extend(__TMP)
        TPV.extend(__TPV)
        TMV.extend(__TMV)
        TUV.extend(__TUV)
        H.extend(__H)
        S.extend(__S)
        evl.extend(__evl)
        p_iter.extend(__p_iter)
        Y_minf.extend(__Y_minf)
        X_minf.extend(__X_minf)
        t_fal.extend(__t_fal)
        number_subregion.extend(__number_subregion)
        fal_con.extend(__fal_con)

        result_dict = {
            'iterations': __P,
            'percent_defined_region': __K, 
            'percent_theta_plus': __TPP,
            'percent_theta_minus': __TMP,
            'theta_plus': __TPV,
            'theta_minus': __TMV,
            'theta_undefined': __TUV,
            'falsification_volumes': __H,
            'budgets': __S,
            'evl': __evl,
            'p_iter': __p_iter,
            'Y_minf': __Y_minf,
            'X_minf': __X_minf,
            't_fal': __t_fal,
            'number_subregion': number_subregion,
            'fal_con': fal_con,
            'replication_time': _replication_time
        }

        pickle_path = pathlib.Path(root_path).joinpath('replication_result_{}.pkl'.format(index))
        f = open(pickle_path, 'wb')
        pickle.dump(result_dict, f)
        f.close()

    
    if verbose:
        print('iteration:',P)   # replication time
        #print(S)   # budgets for each time
        print('percentage of defined region:',K)    # Volume of theta_plus+theta_minus
        print("---------------------------------------")
        print('percentage of theta_plus:',TPP)  #Volume of theta_plus
        print("---------------------------------------")
        print('percentage of theta_minus:',TMP)   #Volume of theta_minus
        print("---------------------------------------")
        print('theta_plus:',TPV)
        print("---------------------------------------")
        print('theta_minus:',TMV)
        print("---------------------------------------")
        print('theta_undefined:',TUV)
        print("---------------------------------------")
        print('falsification volumes:', H)
        print("---------------------------------------")
        print("budgets:", S)
        print("---------------------------------------")
        print("budgets for each iteration:", evl)
        print("---------------------------------------")
        print("falsification volume for each iteration:", p_iter)
        print("---------------------------------------")
        print("The minimum robustness value:", Y_minf)
        print("---------------------------------------")
        print("The minimum robustness value corresponding point:", X_minf)
        print("---------------------------------------")
        print("percentage of falsifying points of robustness values:",t_fal)
        print("---------------------------------------")
        print("number of defined region:",number_subregion)
        print("---------------------------------------")
        print("falsification of continue sampling:",fal_con)    
    
    return TPV,TMV,TUV, S, H, evl, p_iter, number_subregion,fal_con###########



def part_optimize_with_continued_sampling(
    subregion_file: str,
    subregion: np.ndarray,
    region_dimension: int,
    num_partition: int,
    confidence_level: float,
    func: Callable[[np.ndarray], float],
    num_sampling: int,
    levels: Sequence[float],
    replications: int,
    iterations: int,
    min_volume: float,
    budget: int,
    fal_num: int,
    n_model: int,
    n_bo: int,
    n_b: int,
    sample_method: SamplingMethod,
    part_num: int,
    continue_sampling_budget: int,
    seed: Optional[int] = None):
    
    filterwarnings("ignore")
    global verbose, test_function

    test_function = func
    
    if verbose:
        logger.setLevel(INFO)
        
    # if seed is None:
    #     np.random.seed(np.random.randint(0, 100))
    # else:
    #     np.random.seed(seed)
    
    subregion = [subregion]
    subregion_file = pathlib.Path(subregion_file)
    workspace_directory = subregion_file.parents[0]
    workspace_directory.mkdir(exist_ok=True)
    models_directory = workspace_directory.joinpath('models')
    all_gp_result_directory = workspace_directory.joinpath('all_gp_result')
    models_directory.mkdir(exist_ok=True)
    all_gp_result_directory.mkdir(exist_ok=True)
    tpv, tmv, tuv, s, h, evl, p_iter, number_subregion, fal_con = _part_classify(
        sub_u=subregion,
        i_dim=region_dimension,
        i_B=num_partition,
        alpha=confidence_level,
        test_function=func,
        n=num_sampling,
        level=levels,
        replication=replications,
        iteration=iterations,
        min_volume=min_volume,
        max_budget=budget,
        fal_num=fal_num,
        n_model=n_model,
        n_bo=n_bo,
        n_b=n_b,
        sample_method=sample_method,
        part_num=part_num,
        N_cont=continue_sampling_budget,
        root_path=str(workspace_directory.resolve()),
        start_seed=seed)

    # subregion = pd.read_csv(subregion_file)

    return PartitioningResult(
        theta_plus=tpv,
        theta_minus=tmv,
        theta_undefined=tuv,
        evl=evl,
        budgets=s,
        falsification_volumes=h,
        p_iter=p_iter,
        number_subregion=number_subregion,
        fal_con=fal_con,
        fal_ems=None,
        runs=[],
        seed=None,
        options=None,
        time_taken=0)



