import scipy.cluster.hierarchy as shc
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn import metrics

cluster = AgglomerativeClustering(n_clusters=4, affinity='euclidean', linkage='ward')

def result_metrics(X, labels):
    print('Silhouette Coefficient score')
    sil_score = metrics.silhouette_score(X, labels, metric='euclidean')
    print(sil_score)
    print('Calinski-Harabasz index')
    cal_index = metrics.calinski_harabasz_score(X, labels)
    print(cal_index)
    print('Davies-Bouldin index')
    dav_index = metrics.davies_bouldin_score(X, labels)
    print(dav_index)
    return sil_score, cal_index, dav_index