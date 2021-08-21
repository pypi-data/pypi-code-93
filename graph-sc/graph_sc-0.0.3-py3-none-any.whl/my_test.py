import h5py
import matplotlib.pyplot as plt
import numpy as np
import pkg_resources

import graph_sc.models as models
import graph_sc.train as train

device = train.get_device(use_cpu=True)
print(f"Running on device: {device}")


DATA_PATH = pkg_resources.resource_filename("graph_sc", "data/")
data_mat = h5py.File(f"{DATA_PATH}/worm_neuron_cell.h5", "r")

Y = np.array(data_mat["Y"])
X = np.array(data_mat["X"])
n_clusters = len(np.unique(Y))
scores = train.fit(X, Y, n_clusters, cluster_methods=["KMeans"])
print(scores.keys())

from sklearn.decomposition import PCA

print("Plotting...")
embeddings = scores["features"]
pca = PCA(2).fit_transform(embeddings)
plt.figure(figsize=(12, 4))
plt.subplot(121)
plt.title("Ground truth")
plt.scatter(pca[:, 0], pca[:, 1], c=Y, s=4)

plt.subplot(122)
plt.title("K-Means pred")
plt.scatter(pca[:, 0], pca[:, 1], c=scores["kmeans_pred"], s=4)
