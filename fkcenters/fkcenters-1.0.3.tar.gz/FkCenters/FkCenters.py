import os
import os.path
import sys
from sys import platform
sys.path.append(os.path.join(os.getcwd(), "Measures"))
sys.path.append(os.path.join(os.getcwd(), "LSH"))
sys.path.append(os.path.join(os.getcwd(), "../"))
sys.path.append(os.path.join(os.getcwd(), "../Dataset"))
sys.path.append(os.path.join(os.getcwd(), "../Measures"))
sys.path.append(os.path.join(os.getcwd(), "../LSH"))
sys.path.append(os.path.join(os.getcwd(), "./ClusteringAlgorithms"))

import numpy as np
import pandas as pd
#from kmodes_lib import KModes

from collections import defaultdict
from sklearn.utils import check_random_state
from sklearn.utils.validation import check_array
import timeit
from kmodes.util import get_max_value_key, encode_features, get_unique_rows, \
    decode_centroids, pandas_to_numpy

from .FuzzyClusteringAlgorithm import FuzzyClusteringAlgorithm
from sklearn.metrics.cluster import adjusted_rand_score
from sklearn.metrics.cluster import normalized_mutual_info_score
from sklearn.metrics.cluster import adjusted_mutual_info_score
from sklearn.metrics.cluster import homogeneity_score
import random
from . import TDef
from . import TUlti as tulti


class FkCenters(FuzzyClusteringAlgorithm):
    def SetupMeasure(self, classname):
        if classname=="Overlap":
            from .Overlap import Overlap
            class_ = Overlap
        #module = __import__(classname, globals(), locals(), ['object'])
        #class_ = getattr(module, classname)
        self.measure = class_()
        self.measure.setUp(self.X, self.y)
    
    def DistanceRepresentativestoAPoints(self,representatives, point):
        return [self.Distance(c, point) for c in centers]

    def CalcDistMatrix(self):
        for i in range(self.n):
            for j in range(self.k):
                 tmp=self.Distance(self.centers[j],self.X[i],j)
                 self.dist_matrix[i][j] = tmp
    def UpdateLabelsFirst(self):
        self.CalcDistMatrix()
        for i in range(self.n):
            min_id = np.argmin(self.dist_matrix[i])
            self.labels[i] = min_id
            self.representatives_sum[min_id]+=1
            for ii, val in enumerate(self.X[i]):
                self.representatives_count[min_id][ii][val]+=1
    def MoveAPoint(self,i,from_id,to_id):
        if self.representatives_sum[from_id] >1:
            self.labels[i] = to_id
            self.representatives_sum[to_id]+=1
            self.representatives_sum[from_id]-=1
            for ii, val in enumerate(self.X[i]):
                self.representatives_count[to_id][ii][val]+=1
                self.representatives_count[from_id][ii][val]-=1
            return 1
        return 0
    def UpdateLabels(self):
        cost=0
        move=0
        self.CalcDistMatrix()
        for i in range(self.n):
            min_id = np.argmin(self.dist_matrix[i])
            cost+= self.dist_matrix[i][min_id]
            last_id = self.labels[i]
            if min_id!= last_id:
                move+=self.MoveAPoint(i,last_id,min_id)
        return cost,move
    def Distance2_(self,point,representative ):
        return self.Distance(representative,point)
    def Distance(self,representative, point):
        sum=0;
        for i in range (self.d):
            sum = sum + representative[i][point[i]]
        return (self.d - sum)/self.d
    def Distance3_(self,representative,point,ki):
        sum=0;
        for i in range (self.d):
            for vj in range(self.D[i]):
                if point[i] == vj:
                    tmp=  self.W[ki][i]* (1-representative[i][vj])**2
                else: tmp= self.W[ki][i]*(0-representative[i][vj])**2
                sum+= tmp
        return sum**0.5
    def UpdateLambdasFuzzy(self):
        #Fuzzy krepresentatives
        um = self.u ** self.alpha
        for ki in range(self.k):
            for di in range(self.d):
                self.weightsums_total[ki][di]=0
                for ai in range(self.D[di]):
                    self.weightsums[ki][di][ai] =0.0
        for i,x in enumerate (self.X):
            for di,xi in enumerate(x):
                for ki in range(self.k):
                    if um[i,ki] ==0: um[i,ki] = 0.000001
                    self.weightsums[ki][di][xi] += um[i,ki]
                    self.weightsums_total[ki][di]+= um[i,ki]
        for ki in range(self.k):
            for di in range(self.d):
                for vj in range(self.D[di]):
                    self.representatives_only[ki][di][vj] = self.weightsums[ki][di][vj]/self.weightsums_total[ki][di]
        for ki in range(self.k):
            tmp = np.sum(self.weightsums_total[ki])
            if tmp==0: tmp = 0.0000001
            tmp = 1/tmp
            numerator=0
            denominator=0
            for di in range(self.d):
                numerator_child=0
                for vj in range(self.D[di]):
                    numerator_child+= self.representatives_only[ki][di][vj]**2
                numerator+= 1 - numerator_child
                denominator+= numerator_child - 1/ self.D[di]
                
            self.lambdas[ki] = min(0.99, tmp*numerator/denominator)
        if TDef.verbose>=2:    
            print("Lambdas:",self.lambdas)
        
    def UpdateCentersFuzzy(self):
        for ki in range(self.k):
            for di in range(self.d):
                right = 1 - (self.lambdas[ki]**2) /self.D[di];
                tmp= self.lambdas[ki]**2-1
                tmp2=0
                for vj in range(self.D[di]):
                    tmp2 = self.representatives_only[ki][di][vj]**2
                right = right+tmp*tmp2
                tmp/=-self.beta
                self.W[ki][di] = 10**tmp
        #Test normalize W
        row_sums = self.W.sum(axis=1)
        self.W = self.W / row_sums[:, np.newaxis]
        #Now update centers
        for ki in range(self.k):
             for di in range(self.d):
                    for vj in range(self.D[di]):
                        self.centers[ki][di][vj] = self.lambdas[ki]/self.D[di]  + (1-self.lambdas[ki])*self.representatives_only[ki][di][vj]
                        #self.centers[ki][di][vj] = self.representatives_only[ki][di][vj]
        asd=123
    def UpdateMemberships(self):
        self.u =  np.zeros((self.n,self.k))
        distall_sum = np.zeros((self.n))
        for i in range(self.n):
            for ki in range(self.k):
                self.distall_tmp[i][ki] = self.Distance(self.centers[ki] ,self.X[i])
                if  self.distall_tmp[i][ki]<=0:  self.distall_tmp[i][ki]= 0.001  #Unclear error
                tmp = self.distall_tmp[i][ki]**self.power
                self.distall[i][ki] = 1/(tmp)
                distall_sum[i] += self.distall[i][ki]
            for ki in range(self.k):
                self.u[i][ki] =self.distall[i][ki]/ distall_sum[i]
        return np.sum(self.u**self.alpha*self.distall_tmp)
    
    def NormalizeCenters(self):
        for ki in range(self.k):
            for i in range(self.d):
                sum_ = 0
                for j in range(self.D[i]): sum_ = sum_ + self.centers[ki][i][j]
                for j in range(self.D[i]): self.centers[ki][i][j] = self.centers[ki][i][j]/sum_;
        asd=123
    def DoCluster(self, plabels=np.zeros(0)):
        self.name = "F$k$Centers" 
        self.name_full = "Fuzzy$k$Centers"
        self.desc ='nmtoan91'
        self.minus_X_to_v = self.minus_X_to_v_rep
        self.squared_distances_V= self.squared_distances_V_rep
        self.squared_distances = self.squared_distances_rep
        #Init varibles
        X = self.X
        self.k = k = n_clusters = self.k
        self.n = n = self.X.shape[0];
        self.d = d = X.shape[1]
        self.D = D = [len(np.unique(X[:,i])) for i in range(d) ]
        self.beta = 0.5
        all_labels = []
        all_costs = []
        start_time = timeit.default_timer()
        self.dist_matrix = np.zeros((self.n, self.k))
        self.weightsums = [[[0.0 for i in range(self.D[j])] for j in range(self.d) ] for kk in range(self.k)]
        self.weightsums_total = [[0.0  for j in range(self.d) ] for kk in range(self.k)]
        self.distall =np.zeros((self.n,self.k)); self.distall_tmp =np.zeros((self.n,self.k));
        results = []
        for init_no in range(self.n_init):
            start_time2 =  timeit.default_timer()
            if TDef.verbose >=1: print ('FkCenters Init ' + str(init_no))
            self.random_state = check_random_state(None)
            self.lambdas = np.zeros(self.k)
            self.W = np.ones((self.k, self.d))/d
            self.centers = [[[random.uniform(0,1) for i in range(D[j])] for j in range(d)] for ki in range(k)]
            self.representatives_only = [[[random.uniform(0,1) for i in range(D[j])] for j in range(d)] for ki in range(k)]

            self.centers = [[[random.uniform(0.1,1) for i in range(self.D[j])] for j in range(self.d)] for ki in range(self.k)]
            self.NormalizeCenters()
            self.UpdateMemberships()
            last_cost = float('inf')

            for i in range(self.n_iter):
                self.itr=i
                start_time_iter =  timeit.default_timer()
                self.UpdateLambdasFuzzy()
                self.UpdateCentersFuzzy()
                cost=self.UpdateMemberships()
                if(last_cost==cost): break; 
                last_cost=cost
                if TDef.verbose >=2: print ('Iter ' + str(i)," Cost:", "%.2f"%cost," Timelapse:", "%.2f"%(timeit.default_timer()-start_time_iter) )
            re = self.centers, self.u, last_cost, self.itr, timeit.default_timer() - start_time2
            results.append(re)
        all_centers, all_u, all_costs, all_n_iters, all_time = zip(*results)
        best = np.argmin(all_costs)
        self.iter= all_n_iters[best]; self.u= all_u[best]; self.cost = all_costs[best]
        self.time_score = (timeit.default_timer() - start_time)/ self.n_init
        self.labels  = self.u.argmax(axis=1)
        self.CheckLabels()
        self.centroids = all_centers[best]
        return self.labels
    
if __name__ == "__main__":
    TDef.InitParameters(sys.argv)
    MeasureManager.CURRENT_DATASET = 'soybean_small.csv' 
    MeasureManager.CURRENT_MEASURE = 'Overlap'
    if TDef.data!='': MeasureManager.CURRENT_DATASET = TDef.data
    if TDef.measure!='': MeasureManager.CURRENT_MEASURE = TDef.measure
    if TDef.test_type == 'syn':
        DB = tulti.LoadSynthesisData(TDef.n,  TDef.d, TDef.k)
        MeasureManager.CURRENT_DATASET= DB['name']
    else:
        DB = tulti.LoadRealData(MeasureManager.CURRENT_DATASET)

    print("\n\n############## FkCenters ###################")
    
    algo = FkCenters(DB['DB'],DB['labels_'] ,dbname=MeasureManager.CURRENT_DATASET ,k=TDef.k, alpha=TDef.alpha)
    algo.SetupMeasure(MeasureManager.CURRENT_MEASURE)
    #for i in range(1000):
    #    a = random.randint(0,1000)
    #    random.seed(a)
    #    print("seed",a)
    #    TDef.verbose =0
    algo.DoCluster()
    algo.CalcScore()
    algo.CalcFuzzyScore()
