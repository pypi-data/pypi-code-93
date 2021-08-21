#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  7 09:29:29 2021

@author: mike
"""
import numpy as np
import xarray as xr
import pandas as pd
import os
import glob
from tethys_utils.processing import write_pkl_zstd, process_datasets, prepare_results, assign_station_id, make_run_date_key
from tethys_utils.s3 import process_run_date, update_results_s3, put_remote_dataset, put_remote_agg_stations, put_remote_agg_datasets, s3_connection
from shapely.geometry import shape, mapping, Point, box
import copy
import rasterio
import concurrent.futures
from tethys_utils.grid import Grid


###########################################
### Parameters


############################################
### Functions


def parse_images(path_str):
    """

    """
    f2 = glob.glob(path_str)
    f3 = {f: os.path.getsize(f) for f in f2}
    max1 = max(f3.values())
    max_f = [f for f in f3 if f3[f] == max1][0]

    return f3, max_f


def process_image(image, parameter, x_name='x', y_name='y', band=1):
    """

    """
    xr1 = xr.open_rasterio(image)
    xr1 = xr1.rename({x_name: 'lon', y_name: 'lat'}).sel(band=band).drop('band')
    xr1.name = parameter

    return xr1


############################################
### Class


class Raster(object):
    """

    """
    ## Initial import and assignment function
    def __init__(self, path_str, time, height, x_name='x', y_name='y', band=1, dataset_list=None, remote=None, processing_code=None, public_url=None, run_date=None):
        f_dict, max_f = parse_images(path_str)

        # Run checks
        src = rasterio.open(max_f)
        crs = src.crs.to_epsg()

        if crs != 4326:
            raise ValueError('Raster CRS is in epsg: ' + str(crs) + ', but should be 4326')

        src.close()

        # Set attrs
        setattr(self, 'x_name', x_name)
        setattr(self, 'y_name', y_name)
        setattr(self, 'max_image', max_f)
        setattr(self, 'images', f_dict)
        setattr(self, 'band', band)
        setattr(self, 'time', time)
        setattr(self, 'height', height)

        if isinstance(dataset_list, list):
            grid = Grid(dataset_list, remote, processing_code, public_url, run_date)
            setattr(self, 'update_aggregates', self.grid.update_aggregates)

        else:
            grid = Grid()

        setattr(self, 'grid', grid)

        pass


    def open_big_one(self):
        """

        """
        xr1 = xr.open_rasterio(self.max_image)

        return xr1


    def determine_grid_block_size(self, starting_x_size=100, starting_y_size=100, increment=100, min_size=800, max_size=1100):
        """

        """
        parameter = self.grid.datasets[0]['parameter']
        xr1 = process_image(self.max_image, parameter, x_name=self.x_name, y_name=self.y_name, band=1)
        self.grid.load_data(xr1.to_dataset(), parameter, self.time, self.height)
        size_dict = self.grid.determine_grid_block_size(starting_x_size, starting_y_size, increment, min_size, max_size)

        setattr(self, 'grid_size_dict', size_dict)

        res = xr1.attrs['res'][0]
        setattr(self, 'grid_res', res)

        return size_dict


    def save_results(self, x_size, y_size, threads=30):
        """

        """
        ## Iterate through the images
        images = list(self.images.keys())
        images.sort()

        for tif in images:
            print(tif)

            parameter = self.grid.datasets[0]['parameter']
            xr1 = process_image(self.max_image, parameter, x_name=self.x_name, y_name=self.y_name, band=1)
            self.grid.load_data(xr1.to_dataset(), parameter, self.time, self.height)

            self.grid.save_results(x_size, y_size, threads=threads)










