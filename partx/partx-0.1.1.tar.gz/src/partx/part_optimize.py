import numpy as np
import copy
import random
from random import choice
import numpy as np
from itertools import product
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
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import joblib
from typing import Tuple, Union, List, Callable, Optional, Sequence
from warnings import catch_warnings, simplefilter, filterwarnings
from numpy import arange, vstack, argmax, asarray
from numpy.random import normal, random
from scipy.stats import norm
import pathlib
import logging
from logging import getLogger, INFO, root
from .models import SamplingMethod, PartitioningOptions, PartitioningResult, PartXBehavior


logging.basicConfig(level=logging.INFO)
logger = getLogger("partX")
verbose = True

test_function = None

def _partition_region(sub_u: list, region_dimension: int):  #get the region that we want to do partition
    '''
    Returns the desired partition region

    Parameters:
        sub_u (list): M * region_dimension * 2 matrix that has the upper and lower bounds
        region_dimension: the dimension of the subregion
    Returns:
        [np.ndarray, np.ndarray]: tuple of MxNx1 that are the separated upper and lower bounds
    '''
    sub_u1 = np.array(sub_u)
    assert sub_u1.shape[1] == region_dimension, 'sub_u matrix must be region_dimension dimensional'
    assert sub_u1.shape[2] == 2, 'sub_u matrix must be an M * region_dimension * 2'
    assert np.apply_along_axis(lambda x: x[1] > x[0], 2, sub_u1).all(), 'sub_u Z-pairs must be in increasing order'
    sl_coordinate_lower = sub_u1[:, :, 0]  # Return first Z-value
    sl_coordinate_upper = sub_u1[:, :, 1]  # Return second Z-value

    return sl_coordinate_lower, sl_coordinate_upper

def _tell_sample(X_all, Y_all, sub_r,region_dimension,z,s_p,Y_p ):##########################
    if z!=0:
        for i in range(len(sub_r)):
            for m in range(len(X_all)):
                TELL = 1
                for j in range(region_dimension):
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
    
def _compute_sampling_rate(L_est,classified, sub_r):#####################
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

def _continue_sampling(L, sub_rc, N_cont, region_dimension):##############
    '''
    Continue Sample Classified region N times

    Parameters:
        sub_rc (list): Sample space
        N_cont (int): Number of samples
        region_dimension(int): dimension of the region
        L_est: sampling rate
    Returns:
        np.ndarray: Matrix of sampled points

    '''
    a = np.random.uniform(0,1,N_cont)
    n_sub = [0 for m in range(len(L)-1)]
    for i in range(len(a)):
        for j in range(len(L)):
            if a[i] > L[j] and a[i] < L[j+1]:
                n_sub[j]+=1 
    sample_c=[[] for j in range(len(sub_rc))]
    for k in range(len(sub_rc)):
        sample_c[k] = [[0]*n_sub[k]]*region_dimension
    for m in range(len(sub_rc)):
         for n in range(0,region_dimension):
            sample_c[m][n]=np.random.uniform(sub_rc[m][n][0],sub_rc[m][n][1],n_sub[m]).tolist()
    return sample_c

def _sample_c(sub_rc, n_sub, sample_c, s_p, sub_r):###########
    X_all_c =[]
    s_c=[[] for i in range(len(sub_rc))]
    for k in range(len(sub_rc)):
        s_c[k] = [[0]*region_dimension]*n_sub[k]
    for j in range(len(sub_rc)):
        for i in range(n_sub[j]):
            s_c[j][i] =  ([x[i] for x in sample_c[j]])
        s_c[j] = s_c[j] + s_p[len(sub_r)+j]
        X_all_c += s_c[j]
   # s_c = np.array(s_c)
    return s_c,X_all_c 

def _compute_robustness_c(s_c,Y_c,test_function, Y_p,sub_r):###############
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

def _sample_subregion_n_times(sub_r: list, n: int, region_dimension:int) -> list:#########
    '''
    Sample sub_r n times

    Parameters:
        sub_r (list): Sample space
        n (int): Number of samples
        region_dimension(int): dimension of the region
    Returns:
        np.ndarray: Matrix of sampled points

    '''
    sub_r1 = np.array(sub_r)
    assert sub_r1.shape[1] == region_dimension, 'sub_r matrix must be 3-dimensional'
    assert sub_r1.shape[2] == 2, 'sub_r matrix must be MxNx2'
    assert np.apply_along_axis(lambda x: x[1] > x[0], 2, sub_r1).all(), 'sub_r Z-pairs must be in increasing order'

    return np.apply_along_axis(lambda x: np.random.uniform(x[0], x[1], n), 2, sub_r1).tolist()


def _modify_points(sub_r: list,  n: int, sample: np.array, s: list,s_p:list) -> list:###############
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


def _compute_robustness(s: np.array, Y, test_function,Y_p:list) -> list:  #True values
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
            # print("Current", s[k][i], type(s[k][i]))
            current = test_function(np.array(s[k][i])) 
            Y[k].append(current)
        if len(Y_p[k])!=0:
            Y[k]+=Y_p[k]
        Y_all += Y[k]
    return Y,Y_all


def _vol(sub_u:list,region_dimension: int) -> int:    #calculate the volume of undefined area
    '''
    calculate defined regions‘ volume
    Parameters:
        sub_u(list) :defined regions
        region_dimension(int) : dimension of these regions
    

    Returns:
        int: the volume of that regions

    '''
    v = 0
    for i in range(len(sub_u)):
        a = []
        for j in range(region_dimension):
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

def opt_acquisition(X: np.array, y: np.array, model,n_b:int ,region_dimension:int, sub_r:list):
    '''
    get the sample points
    Parameters:
        X(np.array): sample points 
        y(np.array): corresponding rebustness values
        model: the GP models 
        n_b(int): the number of sample points to construct the robustness values
        region_dimension(int): dimesion
        sub_r(list): subregions
    

    Returns:
         min_bo(np.array): the new sample points by BO

    '''
    # random search, generate random samples
    samplebo = [[[0]*(n_b)] for m in range(region_dimension)]
    for k in range(region_dimension):
        samplebo[k] = np.random.uniform(sub_r[k][0],sub_r[k][1],n_b)
    sbo = [[[0]*region_dimension] for p in range(n_b)]
    for l in range(n_b):
        sbo[l] = ([x[l] for x in samplebo])
    # calculate the acquisition function for each sample
    scores = acquisition(X, sbo, model)
    # locate the index of the largest scores
    ix = argmax(scores)
    min_bo = np.array(sbo)[ix]
    return min_bo

def _bayesian_optimization(s:np.array , Y:list, n_bo: int, region_dimension:int, sub_r:list,test_function,n_b:int):
    '''
    calculate the best surrogate score found so far
    Parameters:
        s(np.array): sample points
        Y(list): robustness values
        n_bo(int): number of Bayesian Optimization sampling
        region_dimension(int): dimension
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
            min_bo = opt_acquisition(X, Y[i], model,n_b,region_dimension, sub_r[i])
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


def _model_construction(s: np.array, Y: list, v_s: int, sub_r: list, lower, upper, level: list, z: int, q: int, region_dimension: int, fal_num:int, n_model:int,miscoverage_level:float, list_star:list, root_path) -> Tuple[np.array,np.array]:   ##Gaussian process 
    '''
    construct Gaussian processes and confidence intervals

    Parameters:
        s (np.array): Sample points
        Y (list): robustness values
        v_s (int): volume of sub_u
        sub_r(list): partitioned subregions
        z(int): # of repliction 
        q(int): # of iteration
        region_dimension(int): # of dimension
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
    for i in range(len(s)):
        X = np.array(s[i])#########
        y = Y[i]
        kernel = R([1]*region_dimension) * M([1]*region_dimension) #input kernel for GPs 
        gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=9)
        gp.fit(X, y) #fit sample points to Grussian Process
        name =  root_path + '/models/'+'trainmodel' +str(0)+ str(q+1) +str(0)+ str(z+1) +str(0)+ str(i+1)+'.m'  #save the models # modify your name here
        joblib.dump(gp, name) 
        #model = joblib.load(name)
        n_s = int(fal_num*_vol([sub_r[i]],region_dimension)/v_s) # assign corresponding number of points to subregions
        n_ss = n_s + n_model
        samplegp = [[[0]*(n_ss)] for m in range(region_dimension)]
        for k in range(region_dimension):
            samplegp[k] = np.random.uniform(sub_r[i][k][0],sub_r[i][k][1],n_ss)
            #np.apply_along_axis(lambda x: np.random.uniform(x[0], x[1], n), 2, sub_r)
        sgp = [[[0]*region_dimension] for p in range(n_ss)]
        for l in range(n_ss):
            sgp[l] = ([x[l] for x in samplegp])
        y_pred_st, sigma_st = gp.predict(sgp, return_std=True)   ##predict new sample points
        cdfn = []############
        #print(sigma_st)
        for q in range(len(y_pred_st)):###############
            cdfn.append(norm.cdf(0,loc=y_pred_st[q], scale=sigma_st[q]**2))#############
        f0 = sum(cdfn)#############
        L_est.append(f0*_vol([sub_r[i]], region_dimension))###################
        idxs = np.random.randint(0, n_s + n_model, n_model)
        y_pred = y_pred_st[idxs]
        y_sigma = sigma_st[idxs]
        for o in range(len(level)):
            level_quantile[i][o] = stats.norm.interval(level[o],y_pred_st,sigma_st)[0]
        i_s = np.argmin(y_pred, axis=0)      #find maximum and minimum values of predicted values
        i_ss = np.argmax(y_pred, axis=0) 
        #conf_intveral_1 = stats.norm.interval(1-miscoverage_level
        #, loc=y_pred[i_s], scale=y_sigma[i_s])
        #a = list(conf_intveral_1)
        #lower.append(a[0])
        #conf_intveral_2 = stats.norm.interval(1-miscoverage_level
        #, loc=y_pred[i_ss], scale=y_sigma[i_ss])
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
              
def _region_classify(lower: list, upper:list , sub_r:list, theta_undefined, theta_plus, theta_minus, tpn, tmn, tun):  
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
                                     
def _find_min(Y_subm,num,s: np.array,Y: list,region_dimension:int) -> list:    #the minimum robustness values
    '''
    find minimum robustness values

    Parameters:
        s (np.array): Sample points
        Y(list): robustness values
        region_dimension(int): the dimension of subregion

    Returns:
         num(list): the number of minmum points and corresponding robustness values
         Y_subm(list): the minmum points

    '''
    Y_subm = [[] for i in range(len(s))]
    num = [[0]*region_dimension for i in range(len(s))]
    for k in range(0,len(s)):
        Y_subm[k] = min(Y[k])
        inum = list(Y[k]).index(Y_subm[k])
        num[k][0] = k
        num[k][1] = inum
    return num,Y_subm

def _part_percent(level:list, sub_r:list, v_s, level_quantile, p_quantile, region_dimension: int):
    '''
    calculate falsification volume for each sub_regions

    Parameters:
        level(list): the quantile set
        sub_r(list): the subregions
        v_s: volume of the whole region
        level_quantile: the predicted values to calculate fal_volume
        region_dimension(int): the dimension
    Returns:
        p_quantile(list): fal_volume for subregions
    '''
    for i in range(len(level)):
        for j in range(len(sub_r)):
            a_s = [x for x in level_quantile[j][i] if x < 0]
            p_quantile[i]. append((len(a_s)/len(level_quantile[j][i]))*(_vol([sub_r[j]],region_dimension)/v_s))
    return p_quantile

def _part_listc(region_dimension, part_num, iteration):
    l = []
    k = []
    for i in range(part_num, region_dimension):
        l.append(i)
    for j in range(region_dimension):
        k.append(j)
    part_index = k*round((iteration-part_num)/region_dimension)
    part_list = l + part_index
    return part_list

def _fun_reg_branching(sl_coordinate_lower: np.ndarray, sl_coordinate_upper: np.ndarray, region_dimension: int, num_partition: int, sub_r, sub_u: list, part_list:list, z: int,list_subr) -> list:
    '''
    Partitioning Algorithm
    Parameters:
        [np.ndarray, np.ndarray]: tuple of MxNx1 that are the separated upper and lower bounds
        region_dimension(int):dimension
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
        i_index = part_list[z]
        for i in range(0, num_partition):
            l_coordinate_lower = copy.deepcopy(sl_coordinate_lower)
            l_coordinate_upper = copy.deepcopy(sl_coordinate_upper)
            l_coordinate_lower[j][i_index] = float((sl_coordinate_upper[j][i_index] - sl_coordinate_lower[j][i_index]) * i) / num_partition + sl_coordinate_lower[j][i_index]
            l_coordinate_upper[j][i_index] = float((sl_coordinate_upper[j][i_index] - sl_coordinate_lower[j][i_index]) * (i + 1)) / num_partition + sl_coordinate_lower[j][i_index]
            a = [[0]*2 for i in range(0, region_dimension)]
            for i in range(0, region_dimension):
                a[i][0] = l_coordinate_lower[j][i]
                a[i][1] = l_coordinate_upper[j][i]
            sub_r.append(a)
            #list_star[2*j] = 2*(list_subr[j]) -1
            #list_star[2*j+1] = 2*(list_subr[j])
                

    return sub_r,list_star

def _part_classify(subregion: list, region_dimension: int, num_partition: int, miscoverage_level: float, 
                   test_function: Callable[[], float], num_sampling:int, level:list, replication:int, iteration: int, 
                   min_volume:float, max_budget:int, fal_num: float, n_model: int,
                   n_bo: int, n_b: int, sample_method: SamplingMethod, part_num:int, 
                   continue_sampling_budget:int, root_path:str):
    
    '''
    algorithm

    Parameters:
        sub_u(list): region
        region_dimension(int): dimension of the region
        num_partition: # of partition (default = 2)
        miscoverage_level
    (float): miscoverage level
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
    v_s = _vol(subregion,region_dimension)
    region = subregion
    #print(v_s)
    S=[]
    # count = i
    t_fal = []
    X_minf = []
    Y_minf = []
    number_subregion = []
    part_list = _part_listc(region_dimension, part_num, iteration)
    fal_con = []#########
    for q in range(replication):  #CHANGE FOR MORE REPLICATION
        sub_u = region
        print("runtime:",q+1)
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
        v_min = [_vol(sub_u,region_dimension)]
        d1 = 0
        d2 = 0
        list_subr = [1]
        sub_rc = []###########
        falsification_con = [[] for k in range(len(level))]##########
        sample_c = []#######
        X_all_c = []
        for z in range(iteration):  ##change for iteration
            v = _vol(sub_u,region_dimension)
            if min(v_min) > min_volume*v_s and D < max_budget: #0.01: #v(sub_u)
                sl_coordinate_lower, sl_coordinate_upper = _partition_region(sub_u,region_dimension)
                sub_r = []
                sub_r, list_star = _fun_reg_branching(sl_coordinate_lower, sl_coordinate_upper, region_dimension, num_partition, sub_r , sub_u, part_list,z,list_subr)
                s_p = [[] for i in range(len(sub_r)+len(sub_rc))]
                Y_p = [[] for i in range(len(sub_r)+len(sub_rc))]
                sub_r1 = sub_r + sub_rc#########
                if z!=0: #################
                    s_p, Y_p = _tell_sample(X_all, Y_all, sub_r1,region_dimension,z,s_p,Y_p)######################
               
                sample = _sample_subregion_n_times(sub_r, num_sampling, region_dimension)
                s=[[[0] * region_dimension] * num_sampling for i in range(len(sub_r))]###########
                s,X_all = _modify_points(sub_r, num_sampling, sample, s,s_p)
                Y = []
                Y,Y_all = _compute_robustness(s, Y, test_function,Y_p)
                #print(Y_all)
                if sample_method == SamplingMethod.BAYESIAN: 
                    s_bo, Y,s_bo_all, Y_all = _bayesian_optimization(s , Y, n_bo,region_dimension,sub_r,test_function,n_b)
                    s = s_bo
                    X_all = s_bo_all
                if sub_rc !=[]:
                    n_sub = [0 for m in range(len(L)-1)]
                    s_c,X_all_c = _sample_c(sub_rc, n_sub, sample_c,s_p, sub_r)
                    Y_c = []
                    Y_c, Y_all_c = _compute_robustness_c(s_c, Y_c, test_function, Y_p, sub_r)
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
                num = [[0]*region_dimension for i in range(len(s))]
                num_min = []
                num, Y_subm = _find_min(Y_subm,num,s,Y,region_dimension)
                kf = Y_subm.index(min(Y_subm))
                num_min.append(num[kf])
                X_min.append(s[num_min[0][0]][num_min[0][1]])
                Y_min.append(min(Y_subm))
                lower=[]
                upper=[]
                if sub_rc !=[]:
                     D += (len(sub_r) * (num_sampling + n_bo) + continue_sampling_budget)
                else: 
                     D += len(sub_r) * (num_sampling + n_bo)    
                sub_r = sub_r1
                model_lower, model_upper,level_quantile, L_est = _model_construction(s, Y, v_s, sub_r, lower, upper, level, z, q, region_dimension, fal_num, n_model,miscoverage_level,list_star, root_path)
                #print(L_est)
                p_quantile = [[] for i in range(len(level))]
                p_quantile = _part_percent(level, sub_r, v_s,level_quantile, p_quantile,region_dimension)
                #print(p_quantile)
                theta_undefined=[]
                theta_plus=[]
                theta_minus = []
                tpn = []
                tmn = []
                tun = []
                theta_plus, theta_minus, theta_undefined, tpn, tmn, tun = _region_classify(lower, upper , sub_r, theta_undefined, theta_plus, theta_minus, tpn, tmn, tun)
                tp =[]
                theta_d = []
                v_min = []
                theta = theta_undefined+theta_plus+theta_minus
                classified = tmn+tpn##############
                L=[0]
                ratio_L = []
                if len(classified)!=0:########
                    L, sub_rc, ratio_L = _compute_sampling_rate(L_est, classified, sub_r)############
                    sample_c = _continue_sampling(L, sub_rc, continue_sampling_budget, region_dimension)###########
                    #print(sample_c)
                else: #######
                    sub_rc = []##########
                   
                if len(theta_undefined) != 0:
                    for i in range(len(theta)):
                        v_min.append(_vol([theta[i]],region_dimension))
                if len(theta_undefined) == 0:
                    v_min.append(0)
                if min(v_min) < min_volume*v_s or D >= max_budget:
                    tp = tpn+tmn+tun
                if min(v_min) > min_volume*v_s and D < max_budget:
                    tp = tpn+tmn
                Z = []
                Q = []
                list_region = []
                for i in range(len(tp)):
                    if len(tp)!=0:
                        theta_d.append(sub_r[tp[i]])
                        #list_region.append(list_star[tp[i]])
                        for j in range(len(level)):
                            p_fal[j].append(p_quantile[j][tp[i]])
                #number_sub.append(list_region)
                #####for m in range(len(list_region)):
                    ####shutil.move('/Users/candicetsao/Desktop/sin_gp/models/'+'trainmodel'+str(0)+str(q+1)+str(0)+str(z+1) + str(0)+str(list_region[m])+'.m', '/Users/candicetsao/Desktop/sin_gp/all_gp_result')     
                number = []########
                number_p = []
                Z_p = []######
                Q_p = []#######
                for l in range(len(s)):###########
                    number.append(l+1)###########
                    for o in range(len(s[l])):
                        number_p.append(l+1)
                        Z_p.append(z+1)
                        Q_p.append(q+1)
                Z = [z+1]*len(sub_r)##########
                Q = [q+1]*len(sub_r)######## 
                Z_c = [z+1]*len(sub_rc)##########
                Q_c = [q+1]*len(sub_rc)######## 
                number_c = []######
                for p in range(len(sub_rc)):#######
                    number_c.append(p+1+len(sub_r)-len(sub_rc))####
                subregion = pd.DataFrame({'subregion': sub_r,'replication': Q,'deepth': Z,'number':number})
                subregion.to_csv(root_path + '/subregions'+ str(q+1)+ '.csv', mode='a', header=False)
                points = pd.DataFrame({'X': X_all,'Y': Y_all, 'replication': Q_p,'deepth': Z_p, 'nunmber': number_p})
                points.to_csv(root_path + '/points'+str(q+1)+'.csv', mode = 'a', index=False,sep=',',header =False)
                #list_subr = [x for x in list_star if x not in list_region]
                if sub_rc !=[]:
                    prob_metric = pd.DataFrame({'I':ratio_L,'subregion': sub_rc, 'replication': Q_c,'deepth': Z_c, 'nunmber': number_c})
                    prob_metric.to_csv(root_path + '/prob_metric'+str(q+1)+'.csv', mode = 'a', index=False,sep=',',header =False)
                
                for i in range(len(level)):
                    fal_iter[i].append(sum(p_quantile[i]))
                #print(fal_iter)
                if len(theta_plus)!= 0:
                     d1 = _vol(theta_plus,region_dimension)
                if len(theta_minus)!= 0:
                    d2 = _vol(theta_minus,region_dimension)
                d = d1 + d2
                V.append(d / v_s)
                TP.append(d1 / v_s)
                TM.append(d2 / v_s)
                budgets.append(len(sub_r))
                if theta_undefined !=[]:
                    sub_u = theta_undefined
                else:
                    sub_u = sub_r
            else:
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
    
    return TPV,TMV,TUV, S, H, evl, p_iter, number_subregion,fal_con

def part_optimize_with_continous_sampling(
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
    global verbose
    
    if verbose:
        logger.setLevel(INFO)
        
    # if seed is None:
    #     np.random.seed(np.random.randint(0, 100))
    # else:
    #     np.random.seed(seed)
    
    subregion = [subregion]
    subregion_file = pathlib.Path(subregion_file)
    workspace_directory = subregion_file.parents[0]
    models_directory = workspace_directory.joinpath('models')
    all_gp_result_directory = workspace_directory.joinpath('all_gp_result')
    models_directory.mkdir(exist_ok=True)
    all_gp_result_directory.mkdir(exist_ok=True)
    tpv, tmv, tuv, s, h, evl, p_iter, number_subregion, fal_con = _part_classify(
        subregion=subregion,
        region_dimension=region_dimension,
        num_partition=num_partition,
        miscoverage_level=confidence_level,
        test_function=func,
        num_sampling=num_sampling,
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
        continue_sampling_budget=continue_sampling_budget,
        root_path=str(workspace_directory.resolve()))

    subregion = pd.read_csv(subregion_file)

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
        history=None,
        seed=None)

# Example :: 


# sub_u =[[[-5,5],[-5,5]]]#[[[0,20],[0,20]]] #parameter space  
# region_dimension = 2 #dimension
# num_partition = 2     #parts want to partition, default = 2
# miscoverage_level = 0.05  #miscoverage level
# level = [0.5,0.75,0.9,0.95]


# def test_function(X):  ##CHANGE
#     return (X[0]**2+X[1] - 11)**2+(X[1]**2+X[0] - 7)**2-40 

# TPV,TMV,TUV, S, H, evl, p_iter, number_subregion,fal_con  = _part_classify(sub_u, region_dimension, num_partition, miscoverage_level, test_function, 20,level, 1, 100 ,0.001 ,30000, 15000,20,0,100,'BO Sampling',1,100)

