#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-ANN.
# @File         : ANN
# @Time         : 2019-12-04 20:05
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :


import faiss
import numpy as np


class ANN(object):
    """Flat支持: https://github.com/Jie-Yuan/faiss_note/blob/master/4.Faiss%20indexes%20%E8%BF%9B%E9%98%B6%E6%93%8D%E4%BD%9C.ipynb
    恢复原数据
    从index中移除向量
    搜索距离范围内的向量
    拆分/合并index

    cpu_index.make_direct_map()
    cpu_index.reconstruct(0)
    ann.index.reconstruct
    ann.index.reconstruct_c
    ann.index.reconstruct_n
    ann.index.reconstruct_n_c
    ann.index.search_and_reconstruct
    ann.index.search_and_reconstruct_c


    数据集的大小
    在高效检索的index中，聚类是其中的基础操作，数据量的大小主要影响聚类过程。

    如果小于1M， 使用"...,IVFx,..."
    N是数据集中向量个数，x一般取值[4sqrt(N),16sqrt(N)],需要30x ～ 256x个向量的数据集去训练。

    如果在1M-10M，使用"...,IMI2x10,..."
    使用k-means将训练集聚类为2^10个类，但是执行过程是在数据集的两半部分独立执行，即聚类中心有2^(2*10)个。

    如果在10M-100M，使用"...,IMI2x12,..."

    一个簇至少39个样本：一般2的N次方，我们一般用2**14或者更小一点 >> topk
    经验公式 2 ** (np.log2(n) // 2 + 2)
    """

    def __init__(self):
        self.nogpu_index_factory = {'HNSW', 'SQ'}

    def train(self, data, index_factory='Flat', metric=None, noramlize=False):
        """

        :param data:
        :param index_factory: 'IVF1024,Flat'
            https://www.cnblogs.com/houkai/p/9316172.html
            https://blog.csdn.net/xiaoxu2050/article/details/84982478
            https://github.com/facebookresearch/faiss/wiki/Faiss-indexes
            https://github.com/liqima/faiss_note/blob/master/4.Faiss%20indexes%20IO%E5%92%8Cindex%20factory.ipynb
        :param metric:
            faiss.METRIC_BrayCurtis
            faiss.METRIC_Canberra
            faiss.METRIC_INNER_PRODUCT: L2之后内积≈cosine
            faiss.METRIC_JensenShannon
            faiss.METRIC_L1
            faiss.METRIC_L2
            faiss.METRIC_Linf
            faiss.METRIC_Lp
        :return:
        """
        if noramlize:
            data = self.noramlize(data)
        assert data.dtype == 'float32', "TODO: np.array([]).astype('float32')"
        dim = data.shape[1]
        args = [dim, index_factory, metric] if metric else [dim, index_factory]

        self.index = faiss.index_factory(*args)

        if faiss.get_num_gpus() > 0:
            if any(index_factory.__contains__(i) for i in self.nogpu_index_factory):
                pass
                print(f"Donot Support GPU: {index_factory}")
            else:
                # gpu_index_flat = faiss.index_cpu_to_gpu(res, 0, index_flat)
                self.index = faiss.index_cpu_to_all_gpus(self.index)

        print("Train ...")
        self.index.train(data)
        self.index.add(data)

        print(f"Ntotal: {self.index.ntotal}")

    def search(self, data, topK=10, nprobe=1, k_factor=1):
        """

        :param data:
        :param topK:
        :param nprobe: nprobe参数始终是调整速度和结果精度之间权衡的一种方式。
        :param k_factor:
        :return:
        """
        self.index.k_factor = k_factor  # 搜索阶段会首先选取 k_factor*topK，重排序
        self.index.nprobe = nprobe  # default nprobe is 1, try a few more
        return self.index.search(data, topK)

    def write_index(self, file_name="index_file.index"):
        # faiss.index_cpu_to_all_gpus(index)
        if faiss.get_num_gpus() > 0:
            index = faiss.index_gpu_to_cpu(self.index)  # gpu版本？
            faiss.write_index(index, str(file_name))
        else:
            faiss.write_index(self.index, str(file_name))

    def read_index(self, file_name="index_file.index"):
        index = faiss.read_index(str(file_name))
        # if faiss.get_num_gpus() > 0:
        #     index = faiss.index_cpu_to_gpu()
        # index_new = faiss.clone_index(index) # 复制索引
        return index

    def noramlize(self, x):
        if len(x.shape) > 1:
            return x / np.clip(x ** 2, 1e-12, None).sum(axis=1).reshape((-1, 1) + x.shape[2:]) ** 0.5
        else:
            return x / np.clip(x ** 2, 1e-12, None).sum() ** 0.5


if __name__ == '__main__':
    import numpy as np

    data = np.random.random((1000, 128)).astype('float32')

    ann = ANN()
    ann.train(data, noramlize=True)

    dis, idx = ann.search(data[:10])

    # print(dis)
    print(idx)

    ann.write_index()
