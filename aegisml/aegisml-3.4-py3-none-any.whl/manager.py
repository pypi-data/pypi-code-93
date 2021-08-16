'''
global variables:
root_path
meta_path
trainset
validset
testset

'''
import random
import math
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from .dataset import KucisDataset

def setQuantity(n, ratio):
    quantity = [math.floor(i*n) for i in ratio]
    remain = n - sum(quantity)
    quantity[0] += remain
    if sum(quantity) != n:
        raise Exception('Error_setQuantity_sum')
    else:
        return quantity
            
def setPath(path):
    global root_path
    global meta_path
    root_path = path + 'kucis_dataset/'
    meta_path = root_path + 'metadata.csv'

def splitDataset(ratio, random_seed = 777):
    if len(ratio) != 3 or sum(ratio) != 1:
        raise Exception('sum of the list is not 1.0 or length is not 3')

    global root_path
    global meta_path
    global trainset
    global validset
    global testset
    
    metadata = pd.read_csv(meta_path, encoding='latin1')
    random.seed(random_seed)
    total = len(metadata)
    train_list = list()
    valid_list = list()
    test_list  = list()
    malware_lists = list()
    
    for i in range(9):
        malware_lists.append(list(metadata[metadata.Class == i+1]['Id']))
        random.shuffle(malware_lists[i])
        
    for i, names in enumerate(malware_lists):
        q = setQuantity(len(names), ratio)
        train_list.append(malware_lists[i][:q[0]])
        valid_list.append(malware_lists[i][q[0]:q[0]+q[1]])
        test_list.append(malware_lists[i][q[0]+q[1]:q[0]+q[1]+q[2]])
    
    QTrain = [len(i) for i in train_list]
    QValid = [len(i) for i in valid_list]
    QTest = [len(i) for i in test_list]
    
    if sum(QTrain) + sum(QValid) + sum(QTest) != total:
        raise Exception()
    
    trainset = KucisDataset('train/', train_list, root_path)
    validset = KucisDataset('valid/', valid_list, root_path)
    testset = KucisDataset('test/', test_list, root_path)
    
    str0 = 'Total:{0}\n'.format(total)
    str1 = 'Proportions of Dataset:{0:5}, {1}, {2}\n'.format(ratio[0], ratio[1], ratio[2])
    str2 = 'Quantity of Trainset :{0:5}, {1}\n'.format(sum(QTrain), [len(i) for i in train_list])
    str3 = 'Quantity of Vaildset :{0:5}, {1}\n'.format(sum(QValid), [len(i) for i in valid_list])
    str4 = 'Quantity of Testset  :{0:5}, {1}'.format(sum(QTest), [len(i) for i in test_list])
    print(f'{str0}{str1}{str2}{str3}{str4}')
    
def makeImages(method):
    global trainset
    global validset
    global testset
    trainset.makeImages(method)
    validset.makeImages(method)
    testset.makeImages(method)
    
def showImage(method):
    if method == 'SO':
        mPath = 'Stream_Order/'
    elif method == 'IC':
        mPath = 'Incremental_Coordinate/'
    try:
        path = root_path + random.choice(['test/', 'train/', 'valid/']) + mPath
    except NameError as e:
        print(e,':aegisml.manager.setPath()가 설정되지 않았습니다.')
        return
        
    os.listdir(path)
    image = np.load(path + random.choice(os.listdir(path)))
    plt.imshow(image, cmap='Greys', interpolation='nearest')
    plt.show()
