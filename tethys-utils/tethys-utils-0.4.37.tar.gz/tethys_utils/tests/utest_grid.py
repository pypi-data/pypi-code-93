# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 09:25:41 2019

@author: michaelek
"""
import os
import yaml
# import pytest
import pandas as pd

pd.options.display.max_columns = 10


###############################################
### Parameters

base_dir = os.path.realpath(os.path.dirname(__file__))

with open(os.path.join(base_dir, 'parameters.yml')) as param:
    param = yaml.safe_load(param)

source = param['source'].copy()
remote = param['remote']
public_url = source['public_url']
processing_code = source['processing_code']

datasets = source['datasets']
parameter = datasets[0]['parameter']

########################################
### Tests


self = Grid(datasets, remote, processing_code, public_url)

self.load_data(data, parameter, height=2)

block_test = self.determine_grid_block_size(starting_x_size=20, starting_y_size=20, increment=10, min_size=800, max_size=1100)

x_size = block_test['x_size']
y_size = block_test['y_size']



































