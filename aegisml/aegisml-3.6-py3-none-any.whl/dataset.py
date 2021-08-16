import torch
import torch.nn.functional as F
from torch.utils.data import Dataset
import numpy as np
import os
import tqdm

class KucisDataset(Dataset):
    def __init__(self, dsType, malware_lists, path):
        self.dsType = dsType
        self.malware_lists = malware_lists
        self.path = path
        self.images = list()

    def __len__(self):
        return sum([len(i) for i in self.malware_lists])

    def __getitem__(self, idx): 
        return 0
    
    def makeImages(self, method, regulation=2.0, dim=1):
        if method == 'SO':
            self.Stream_Order()
        elif method == 'IC':
            self.Incremental_Coordinate(regulation, dim)
        
    def Stream_Order(self):
        j = ''.join
        s = np.save
        t = torch.tensor
        fl = math.floor
        q = math.sqrt
        dsPath = j([self.path, self.dsType, 'Stream_Order/'])
        lawPath = j([self.path, 'law_data/'])
        
        os.makedirs(dsPath, exist_ok=True)
        fnames = sum(self.malware_lists, [])
        for name in tqdm(fnames):
            with open(j([lawPath, name, '.bytes']), 'rb') as f:
                data = list(f.read())
            length = fl(q(len(data)))
            s(j([dsPath, name]), t(data[:length*length]).reshape(length, length).numpy().astype(dtype='uint8'))
        
    def Incremental_Coordinate(self, regulation, dim):
        j = ''.join
        s = np.save
        Fn = F.normalize
        dsPath = j([self.path, self.dsType, 'Incremental_Coordinate/'])
        lawPath = j([self.path, 'law_data/'])
        
        os.makedirs(dsPath, exist_ok=True)
        fnames = sum(self.malware_lists, [])
        for name in tqdm(fnames):
            with open(j([lawPath, name, '.bytes']), 'rb') as f:
                data = list(f.read())
                
            if len(data)%2:
                data = data[:-1]
            
            imgMap = [[0 for x in range(256)] for y in range(256)]
            
            dataIter = iter(data)
            nextd = dataIter.__next__
            for i in dataIter:
                imgMap[i][nextd()] += 1
            
            s(j([dsPath, name]), Fn(torch.FloatTensor(imgMap), p=regulation, dim=dim).numpy())
