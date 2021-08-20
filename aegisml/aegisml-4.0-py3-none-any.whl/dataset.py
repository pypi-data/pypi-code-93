import torch
import torch.nn.functional as F
from torch.utils.data import Dataset
import numpy as np
import pandas as pd
import os
from tqdm import tqdm
import matplotlib.pyplot as plt

class KucisDataset(Dataset):
    def __init__(self, dsType, malware_lists, path):
        self.dsType = dsType
        self.filenames = sum(malware_lists, [])
        self.path = path
        self.metadata = pd.read_csv(''.join([path, 'metadata.csv']), encoding='latin1')
        
    def __len__(self):
        return len(self.filenames)
        
    def __getitem__(self, idx):
        name = self.filenames[idx]
        x = torch.from_numpy(np.load(''.join([self.path, self.dsType, 'Incremental_Coordinate/', name, '.npy'])))
        try:
            y = int(self.metadata[self.metadata['Id'] == name]['Class'])
        except AttributeError as e:
            print(e,':aegisml.manager.splitDataset()이 실행되지 않은 것 같습니다.')
        return x, y
        
    def makeImages(self, regulation, dim, show=False):
        if show:
            self.Incremental_Coordinate_Show(regulation, dim)
        else:
            self.Incremental_Coordinate(regulation, dim)
        
    def Incremental_Coordinate(self, regulation, dim):
        join = ''.join
        save = np.save
        normalize = F.normalize
        dsPath = join([self.path, self.dsType, 'Incremental_Coordinate/'])
        lawPath = join([self.path, 'law_data/'])
        tofloat = torch.FloatTensor
        os.makedirs(dsPath, exist_ok=True)
        
        for name in tqdm(self.filenames):
            with open(join([lawPath, name, '.bytes']), 'rb') as f:
                data = list(f.read())
            
            if len(data) & 1:
                data = data[:-1]

            img = [[0 for x in range(256)] for y in range(256)]
            
            dataIter = iter(data)
            nextd = dataIter.__next__
            for i in dataIter:
                img[i][nextd()] += 1
            
            save(join([dsPath, name]), normalize(tofloat(img), p=regulation, dim=dim).numpy())
    
    def Incremental_Coordinate_Show(self, regulation, dim):
        join = ''.join
        save = np.save
        normalize = F.normalize
        dsPath = join([self.path, self.dsType, 'Incremental_Coordinate/'])
        lawPath = join([self.path, 'law_data/'])
        tofloat = torch.FloatTensor
        os.makedirs(dsPath, exist_ok=True)
        
        imshow = plt.imshow
        show = plt.show
        
        for name in tqdm(self.filenames):
            with open(join([lawPath, name, '.bytes']), 'rb') as f:
                data = list(f.read())
            
            if len(data) & 1:
                data = data[:-1]

            img = [[0 for x in range(256)] for y in range(256)]
            
            dataIter = iter(data)
            nextd = dataIter.__next__
            for i in dataIter:
                img[i][nextd()] += 1
            
            imshow(normalize(tofloat(img), p=regulation, dim=dim), cmap='Greys', interpolation='nearest')
            show()
