import os
import os.path
import sys
from sys import platform
import numpy as np
from sklearn.utils.validation import check_array
from sklearn.metrics.cluster import adjusted_rand_score
from sklearn.metrics.cluster import normalized_mutual_info_score
from sklearn.metrics.cluster import adjusted_mutual_info_score
from sklearn.metrics.cluster import homogeneity_score
from sklearn.metrics.cluster import silhouette_score
from . import TUlti as tulti
import timeit
from . import TDef
import csv
from csv import writer
import random
from .cvi import *
from .fuzzy_cluster_validity_indices import *
from sklearn.utils import check_random_state
import random

class FuzzyClusteringAlgorithm:
    ALGORITHM_LIST = ['kModes','kRepresentatives']
    def __init__(self, X, y,n_init=-1,k=-1,n_iter=-1,dbname='dbname',alpha=1.1,random_state=None):
        self.random_state  = check_random_state(random_state)
        self.seed = -1
        self.alpha = alpha
        self.measurename = 'None'
        self.dicts = [];self.dicts2 = []
        self.iter=-1
        self.dbname = dbname
        self.time_lsh=-1
        self.X = X
        self.y = y
        self.n = len(self.X)
        self.d = len(self.X[0])
        self.k = k if k > 0 else len(np.unique(y))
        self.n_init = n_init
        self.n_iter = n_iter
        if n_init == -1: self.n_init = TDef.n_init 
        if n_iter ==-1 : self.n_iter = TDef.n_iter 
        self.scorebest = -2
        self.power = float(1 / (self.alpha - 1))
        self.power2 =  float(1 / (TDef.beta - 1))

        #self.threshold_measure = 132000000
        self.threshold_measure = 100000000
        
        if TDef.seed == -1:
            random.seed(None)
            self.seed = random.randint(0,100000)
        else: self.seed = TDef.seed
        random.seed(self.seed)
    
       
    def SetupMeasure(self, classname):
        self.measurename = classname
        module = __import__(classname, globals(), locals(), ['object'])
        class_ = getattr(module, classname)
        self.measure = class_()
        self.measure.setUp(self.X, self.y)
    def SetupLSH(self, hbits=-1,k=-1,measure='DILCA' ):
        asd=123
    def overlap_distance(self,a, b):
        return np.sum(a != b)
    def Overlap(self,x,y):
        n = len(x)
        sum =0
        for i in range(n):
            if x[i] != y[i]: sum +=1
        return sum
    def DoCluster(self):
        print("Do something")
        return -1
    def _labels_cost(self,X, centroids, dissim, membship=None):
        X = check_array(X)
        n_points = X.shape[0]
        cost = 0.
        labels = np.empty(n_points, dtype=np.uint16)
        for ipoint, curpoint in enumerate(X):
            diss = self.ComputeDistances(centroids, curpoint)
            clust = np.argmin(diss)
            labels[ipoint] = clust
            cost += diss[clust]
        return labels, cost
    def _labels_cost_Overlap(self,X, centroids, dissim, membship=None):
        X = check_array(X)
        n_points = X.shape[0]
        cost = 0.
        labels = np.empty(n_points, dtype=np.uint16)
        for ipoint, curpoint in enumerate(X):
            diss = self.ComputeDistances_Overlap(centroids, curpoint)
            clust = np.argmin(diss)
            labels[ipoint] = clust
            cost += diss[clust]
        return labels, cost
    def ComputeDistances(self, X, mode):
        return [ self.measure.calculate(i, mode ) for i in X ]
    def ComputeDistances_Overlap(self, X, mode):
        return [ self.Overlap(i, mode ) for i in X ]
    def ComputeUfromlabels(self,labels):
        self.u = np.zeros((self.n, self.k))
        for i in range(self.n):
            self.u[i][labels[i]]=1
    def CalcScore(self, verbose=True):
        if TDef.is_skip_eval: return
        self.AddVariableToPrint("name",self.name)
        self.AddVariableToPrint("name_full",self.name_full)
        self.AddVariableToPrint("desc",self.desc)
        self.timetest = timeit.default_timer()
        #print("TIME1:",timeit.default_timer()-self.timetest,'tich=',self.n*self.k*self.d ); self.timetest = timeit.default_timer()
        starttime = timeit.default_timer()
        s="";
        if self.n*self.k*self.d <= 1000000000: 
            self.purity_score = tulti.CheckCLusteringPurityByHeuristic(self.y, self.labels)
        else: self.purity_score =-2
        #print("TIME2:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        s+= str(timeit.default_timer()-starttime)+"|";  starttime = timeit.default_timer()
        self.NMI_score = normalized_mutual_info_score(self.y,self.labels) #tulti.CheckClusteringNMI(self.y, self.labels)
        s+= str(timeit.default_timer()-starttime)+"|";  starttime = timeit.default_timer()
        #print("TIME3:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        self.ARI_score = adjusted_rand_score(self.labels,self.y) # tulti.CheckClusteringARI(self.y, self.labels)
        s+= str(timeit.default_timer()-starttime)+"|";  starttime = timeit.default_timer()
        self.AMI_score = adjusted_mutual_info_score(self.labels,self.y)
        s+= str(timeit.default_timer()-starttime)+"|";  starttime = timeit.default_timer()
        self.HOMO_score = homogeneity_score(self.labels,self.y)
        s+= str(timeit.default_timer()-starttime)+"|";  starttime = timeit.default_timer()
        #print("TIME4:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        if self.n*self.k*self.d <= self.threshold_measure:
            try: 
                self.SILHOUETTE_score = silhouette_score(self.X, self.labels, metric= self.Overlap)
            except:
                self.SILHOUETTE_score=-1
        else: self.SILHOUETTE_score=-2
        #print("TIME5:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        s+= str(timeit.default_timer()-starttime)+"|";  starttime = timeit.default_timer()
        if self.n*self.k*self.d <= self.threshold_measure: 
            self.Ac_score, self.Pr_score,self.Rc_score =  tulti.AcPrRc(self.y, self.labels)
        else: self.Ac_score =  self.Pr_score = self.Rc_score = -2  
        #print("TIME6:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        s+= str(timeit.default_timer()-starttime)+"|";  starttime = timeit.default_timer()
        self.AddVariableToPrint("Scoringtime",s )

        if verbose: print("Purity:", "%.2f" % self.purity_score,"NMI:", "%.2f" %self.NMI_score,"ARI:", "%.2f" %self.ARI_score,"Sil: ", "%.2f" %self.SILHOUETTE_score,"Acc:", "%.2f" %self.Ac_score,
                          "Recall:", "%.2f" %self.Rc_score,"Precision:", "%.2f" %self.Pr_score)
        #print("TIME22:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        return (self.purity_score,self.NMI_score,self.ARI_score,self.AMI_score,self.HOMO_score,self.SILHOUETTE_score,self.time_score, self.time_lsh,
                self.Ac_score, self.Pr_score, self.Rc_score)
        
    def CalcFuzzyScore(self):
        if TDef.is_skip_eval: return
        #print("TIME33:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        self.fuzzy_pc = pc(self.X, self.u.T,self.centroids, self.alpha )
        #print("TIME331:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        self.fuzzy_npc = npc(self.X, self.u.T,self.centroids, self.alpha )
        #print("TIME332:",timeit.default_timer()-self.timetest,'tich=',self.n*self.k*self.d); self.timetest = timeit.default_timer()
        if self.n*self.k*self.d <= self.threshold_measure:
            self.fuzzy_fhv = fhv(self.X, self.u.T,self.centroids, self.alpha, self.minus_X_to_v )
            self.fuzzy_fs = fs(self.X, self.u.T,self.centroids, self.alpha ,self.squared_distances, self.squared_distances_V)
            self.fuzzy_xb = xb(self.X, self.u.T,self.centroids, self.alpha ,self.squared_distances, self.squared_distances_V)
            self.fuzzy_bh = bh(self.X, self.u.T,self.centroids, self.alpha ,self.squared_distances, self.squared_distances_V)
            self.fuzzy_bws = bws(self.X, self.u.T,self.centroids, self.alpha,self.minus_X_to_v )
        else: self.fuzzy_fs = -2; self.fuzzy_xb=-2; self.fuzzy_bh=-2;self.fuzzy_fhv=-2;self.fuzzy_bws=-2
        #print("TIME333:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        
        self.fuzzy_fpc = self._fp_coeff(self.u)

        #print("TIME34:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()

        if self.n*self.k*self.d <= self.threshold_measure: 
            self.fuzzy_sil_ = FuzzySil(self.X,self.u)
            self.fuzzy_mysil = MyFuzzySil(self.X,self.u,self.labels)
        else:
            self.fuzzy_sil_ = -2
            self.fuzzy_mysil = -2
        #print("TIME35:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        _,_,self.fuzzy_mpo = MPO(self.u)
        #print("TIME351:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        self.fuzzy_npe = NPE(self.u)
        #print("TIME352:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        self.fuzzy_pe = PE(self.u)
        #print("TIME353:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        self.fuzzy_peb = PEB(self.u)

        #print("TIME36:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
        print("Fuzzy scores PC:" +"%.2f" %self.fuzzy_pc,"NPC:" +"%.2f" %self.fuzzy_npc
             ,"FHV↓:" +"%.2f" %self.fuzzy_fhv,"FS↓:" +"%.2f" %self.fuzzy_fs
             ,"XB↓:" +"%.2f" %self.fuzzy_xb,"BH↓:" +"%.2f" %self.fuzzy_bh,"BWS:" +"%.2f" %self.fuzzy_bws,
             "FPC:" +"%.2f" %self.fuzzy_fpc, "SIL_R:" +"%.2f" %self.fuzzy_sil_, "FSIL:" +"%.2f" %self.fuzzy_mysil, "MPO:" +"%.2f" %self.fuzzy_mpo,
             "NPE:" +"%.2f" %self.fuzzy_npe, "PE:" +"%.2f" %self.fuzzy_pe, "PEB:" +"%.2f" %self.fuzzy_peb)

        if TDef.is_auto_save:
            self.WriteResultToCSV()
        #print("TIME44:",timeit.default_timer()-self.timetest); self.timetest = timeit.default_timer()
    def append_list_as_row(self,file_name, list_of_elem):
        with open(file_name, 'a+', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(list_of_elem)
    def AddVariableToPrint(self,name,val):
        self.dicts2.append((name,val ))

    def WriteResultToCSV(self,file=''):
        if not os.path.exists(TDef.folder):
            os.makedirs(TDef.folder)
        if file=='':
            file = TDef.folder+ '/' + self.name + TDef.fname + ".csv" 
        
        self.dbname = self.dbname.replace("_c","").replace(".csv","").capitalize()
        self.dicts.append(('dbname',self.dbname ))
        self.dicts.append(('n',self.n ))
        self.dicts.append(('d',self.d ))
        self.dicts.append(('k',self.k ))
        self.dicts.append(('seed',self.seed ))
        self.dicts.append(('range','-1' ))
        self.dicts.append(('sigma_ratio',-1 ))
        self.dicts.append(('Measure',  self.measurename))
        self.dicts.append(('n_init',self.n_init ))
        self.dicts.append(('n_iter',self.n_iter ))
        self.dicts.append(('iter',self.iter ))
        self.dicts.append(('Purity',self.purity_score ))
        self.dicts.append(('NMI',self.NMI_score ))
        self.dicts.append(('ARI',self.ARI_score ))
        self.dicts.append(('AMI',self.AMI_score ))
        self.dicts.append(('Homogeneity',self.HOMO_score ))
        self.dicts.append(('Silhouette',self.SILHOUETTE_score ))
        self.dicts.append(('Accuracy',self.Ac_score ))
        self.dicts.append(('Precision',self.Pr_score ))
        self.dicts.append(('Recall',self.Rc_score ))
        self.dicts.append(('Time',self.time_score ))
        self.dicts.append(('LSH_time',self.time_lsh ))
        self.dicts.append(('Score',self.scorebest ))
        
        self.dicts.append(('PC',self.fuzzy_pc ))
        self.dicts.append(('NPC',self.fuzzy_npc ))
        self.dicts.append(('FHV',self.fuzzy_fhv ))
        self.dicts.append(('FS',self.fuzzy_fs ))
        self.dicts.append(('XB',self.fuzzy_xb ))
        self.dicts.append(('BH',self.fuzzy_bh ))
        self.dicts.append(('BWS',self.fuzzy_bws ))
        self.dicts.append(('FPC',self.fuzzy_fpc ))
        self.dicts.append(('FSilhouette_R',self.fuzzy_sil_ ))
        self.dicts.append(('FSilhouette',self.fuzzy_mysil ))
        self.dicts.append(('MPO',self.fuzzy_mpo ))
        self.dicts.append(('NPE',self.fuzzy_npe ))
        self.dicts.append(('PE',self.fuzzy_pe ))
        self.dicts.append(('PEB',self.fuzzy_peb ))



        dicts = self.dicts+self.dicts2;
        try:
            if os.path.isfile(file)==False:
                colnames = [i[0] for i in dicts]
                self.append_list_as_row(file,colnames)
            vals = [i[1] for i in dicts]
            self.append_list_as_row(file,vals)
        except Exception  as ex:
            print('Cannot write to file ', file ,'', ex);
            self.WriteResultToCSV(file + str(random.randint(0,1000000)) + '.csv')
    def _fp_coeff(self,u):
        n = u.shape[1]
        return np.trace(u.dot(u.T)) / float(n)

    def ComputeRepresentatives(self,u):
        weightsums = [[[0.0 for i in range(self.D[j])] for j in range(self.d) ] for kk in range(self.k)]
        weightsums_total = [[0.0  for j in range(self.d) ] for kk in range(self.k)]
        representatives =( [[[0.0 for i in range(self.D[j])] for j in range(self.d)] for ki in range(self.k)])
        um = u ** self.alpha
        for ki in range(self.k):
            for di in range(self.d):
                weightsums_total[ki][di]=0
                for ai in range(self.D[di]):
                    weightsums[ki][di][ai] =0.0
        
        for i,x in enumerate (self.X):
            for di,xi in enumerate(x):
                for ki in range(self.k):
                    weightsums[ki][di][xi] += um[i,ki]
                    weightsums_total[ki][di]+= um[i,ki]
        for ki in range(self.k):
            for di in range(self.d):
                for vj in range(self.D[di]):
                    representatives[ki][di][vj] = weightsums[ki][di][vj]/weightsums_total[ki][di]
        return representatives
    def ResetWeightsums(self):
        for kk in range(self.k): 
            for j in range(self.d):
                self.weightsums_total[kk][j]=0
                for i in range(self.D[j]):
                    self.weightsums[kk][j][i]=0
    def Compute_dismatrix(self, X,KIS):
        dist_matrix = np.empty((self.n,self.k))
        for i in range(self.n):
            for ki in range(self.k):
                dist_matrix[i][ki] = self.OverlapKrepresentatives(X[i],KIS[ki])
        return dist_matrix
    def Compute_dismatrix_res(self, KIS):
        dist_matrix = np.zeros((self.k,self.k))
        for i in range(self.k-1):
            for j in range(i+1,self.k):
                dist_matrix[i][j] =dist_matrix[j][i]= self.Overlap_Between_Krepresentatives(KIS[i],KIS[j])
        return dist_matrix
    def OverlapKrepresentatives(self,point,representative):
        sum=0;
        for i in range (self.d):
            for vj in range(self.D[i]):
                if point[i] != vj:
                    sum+= representative[i][vj]
        return sum
    def Overlap_Between_Krepresentatives(self,r1,r2):
        sum=0
        for k in range(self.d):
            sum+= np.linalg.norm(np.array(r1[k]) - np.array(r2[k]))
        return sum
    def DistanceRepresentativeToRepresentative(self, r1,r2):
        sum =0
        for k in range(self.d):
            sum+= np.linalg.norm(np.array(r1[k]) - np.array(r2[k]))
        return sum
    def ComputeMemberships_Modes(self,modes):
        
        u =np.zeros((self.n,self.k));
        distall =np.zeros((self.n,self.k));
        distall_sum =np.zeros((self.n));
        for i in range(self.n):
            for ki in range(self.k):
                tmp = self.Overlap(self.X[i],modes[ki] )
                if tmp==0: tmp=0.0001
                distall[i][ki] = 1/(tmp**self.power)
                if(distall[i][ki]==0): distall[i][ki] = 000.00001
                distall_sum[i]+=distall[i][ki] 
            for ki in range(self.k):
                u[i][ki] = distall[i][ki]/distall_sum[i]
        self.cost_modes = np.sum(u**self.power*distall)
        return u
    #def Compute_dismatrix_modes(self,modes):

    def ComputeLabels_modes(self,solution):
        dist_matrix=scipy.spatial.distance.cdist(self.X, solution, self.Overlap)
        return np.argmin(dist_matrix,1)
    def ComputeMemberships(self, kiss):
        distall_tmp = np.zeros((self.n,self.k))
        distall = np.zeros((self.n,self.k))
        for i in range(self.n):
            for ki in range(self.k):
                tmp = self.OverlapKrepresentatives(self.X[i],kiss[ki] )
                distall_tmp[i][ki] = tmp
                distall[i][ki] = tmp**power
        denominator_ = distall.reshape((self.X.shape[0], 1, -1)).repeat(distall.shape[-1], axis=1)
        denominator_ = distall[:, :, np.newaxis] / denominator_ 
        self.u = 1 / denominator_.sum(2)
        return np.sum(self.u**self.alpha*distall_tmp)

    def CheckLabels(self):
        #if self.k>2: return
        uniques = np.unique(self.labels)
        if len(uniques) == self.k: return
        print("Waring: empty cluser!!")
        for i in range(self.k):
            if i not in uniques:
                self.labels[random.randint(0,self.n-1)] = i;
                break
        self.CheckLabels()
    def EncodeCategoricalFeatures(self):
        D = [len(np.unique(self.X[:,i])) for i in range(self.d) ]
        d2 = sum(D)
        X2 = np.empty((self.n,d2))
        current_di=0
        current_index=0
        for di in range(d2):
            for ni in range(self.n):
                if self.X[ni,current_di] == current_index:
                    X2[ni,di]=1
                else : X2[ni,di]=0
            current_index+=1
            if current_index==D[current_di]:
                current_di+=1
                current_index=0
        self.X=X2
        self.d = d2
    def minus_X_to_v_mode(self, X,v):
        d = X.shape[1]
        m = np.zeros( (X.shape[0],d) )
        for i,xi in enumerate(X):
            for di in range(d):
                m[i][di] =  xi[di] - v[di]
        return m;
    def minus_X_to_v_vector(self, X,v):
        return X-v;
    def minus_X_to_v_rep(self, X,v):
        d = X.shape[1]
        m = np.ones( (X.shape[0],d) )
        for i,xi in enumerate(X):
            for di in range(d):
                m[i][di] = 1 - v[di][xi[di]]
        return m;

    def squared_distances_rep(self, x,v):
        m = np.zeros((self.n,self.k))
        for i in range(self.n):
            for j in range(self.k):
                m[i][j] = self.OverlapKrepresentatives (x[i],v[j])**2
        return m

        return scipy.spatial.distance.cdist(x, v,self.Distance2)**2
    def squared_distances_V_rep(self, v1,v2):
        m = np.zeros((self.k,self.k))
        for i in range(self.k):
            for j in range(self.k):
                m[i][j] = self.DistanceRepresentativeToRepresentative(v1[i],v2[j])**2
        return m
    def squared_distances_vector(self, x,v):
        return scipy.spatial.distance.cdist(x, v)**2
    def squared_distances_V_vector(self, v1,v2):
        return scipy.spatial.distance.cdist(v1, v2)**2
    def squared_distances_mode(self, x,v):
        return scipy.spatial.distance.cdist(x, v,overlap_distance)**2
    def squared_distances_V_mode(self, v1,v2):
        return scipy.spatial.distance.cdist(v1, v2,overlap_distance)**2




