#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  7 09:29:29 2021

@author: mike
"""
import numpy as np
import xarray as xr
import pandas as pd
from tethys_utils.processing import write_pkl_zstd, prepare_results, assign_ds_ids
from tethys_utils.s3 import process_run_date, update_results_s3, put_remote_dataset, put_remote_agg_stations, put_remote_agg_datasets, s3_connection
# from tethys_utils.titan import Titan
# from shapely.geometry import shape, mapping, Point, box
# import copy
# import rasterio
import concurrent.futures


###########################################
### Parameters


############################################
### Functions


def _split_grid(arr, x_size, y_size, x_name='lon', y_name='lat'):
    """
    Function to split an n-dimensional dataset along the x and y dimensions. Optionally, add time and height dimensions if the array does not aready contain them.

    Parameters
    ----------
    arr : DataArray
        An xarray DataArray with at least x and y dimensions. It can have any number of dimensions, though it probably does not make much sense to have greater than 4 dimensions.
    x_size : int
        The size or length of the smaller grids in the x dimension.
    y_size : int
        The size or length of the smaller grids in the y dimension.
    x_name : str
        The x dimension name.
    y_name : str
        The y dimension name.

    Returns
    -------
    List of DataArrays
        The result contains none of the original attributes.
    """
    ## Get the dimension data
    dims = arr.dims

    # Get other array info
    x_index = dims.index(x_name)
    y_index = dims.index(y_name)
    data_name = arr.name

    arr_shape = arr.shape

    m = arr_shape[x_index]
    n = arr_shape[y_index]
    dtype = arr.dtype

    ## Build the new regular array to be queried
    y_diff = arr[y_name].diff(y_name, 1).median().values
    x_diff = arr[x_name].diff(x_name, 1).median().values

    bpx = ((m-1)//x_size + 1) # blocks per x
    bpy = ((n-1)//y_size + 1) # blocks per y
    M = x_size * bpx
    N = y_size * bpy

    x_y = list(arr_shape)
    x_y[x_index] = M
    x_y[y_index] = N

    sel1 = tuple(slice(0, s) for s in arr_shape)

    A = np.nan * np.ones(x_y)
    A[sel1] = arr

    # x array
    x_start = arr[x_name][0].values
    x_int = M * x_diff
    x_end = x_start + x_int
    xs = np.arange(x_start, x_end, x_diff)

    # y array
    y_start = arr[y_name][0].values
    y_int = N * y_diff
    y_end = y_start + y_int
    ys = np.arange(y_start, y_end, y_diff)

    # Coords
    coords = []
    new_dims = []
    for d in dims:
        name = d
        if d == x_name:
            c = xs
        elif d == y_name:
            c = ys
        else:
            c = arr[d]
        coords.extend([c])
        new_dims.extend([name])

    # New DataArray
    A1 = xr.DataArray(A, coords=coords, dims=new_dims, name=data_name)

    block_list = []
    previous_x = 0
    for x_block in range(bpy):
        previous_x = x_block * x_size
        previous_y = 0
        for y_block in range(bpx):
            previous_y = y_block * y_size
            x_slice = slice(previous_x, previous_x+x_size)
            y_slice = slice(previous_y, previous_y+y_size)

            sel2 = list(sel1)
            sel2[x_index] = x_slice
            sel2[y_index] = y_slice

            block = A1[tuple(sel2)]

            # remove nans
            block = block.dropna(y_name, 'all')
            block = block.dropna(x_name, 'all')

            ## append
            if block.size:
                block_list.append(block.astype(dtype))

    return block_list


############################################
### Class


class Grid(object):
    """

    """
    ## Initial import and assignment function
    def __init__(self, dataset_list=None, remote=None, processing_code=None, public_url=None, run_date=None):
        """

        """
        if isinstance(dataset_list, list):
            self.process_datasets(dataset_list, remote, processing_code, public_url, run_date)

        pass


    def process_datasets(self, dataset_list, remote, processing_code, public_url=None, run_date=None):
        """

        """
        ### Create dataset_ids
        datasets = assign_ds_ids(dataset_list)

        ## Checks
        grid_bool = all([d['spatial_distribution'] == 'grid' for d in datasets])
        if not grid_bool:
            raise ValueError('All values of spatial_distribution in the datasets should be grid.')

        grouping_len = len(np.unique([d['grouping'] for d in datasets]))
        if grouping_len > 1:
            raise ValueError('All values of grouping in the datasets must be the same.')

        grouping = datasets[0]['grouping']

        ### Determine the last run date and process the old data if old enough
        run_date_dict = process_run_date(processing_code, datasets, remote, run_date)
        max_run_date_key = max(list(run_date_dict.values()))

        ## Create the data_dict
        # data_dict = {d['dataset_id']: [] for d in datasets}

        ## Save objects
        setattr(self, 's3_remote', remote)
        setattr(self, 'public_url', public_url)
        setattr(self, 'datasets', datasets)
        setattr(self, 'run_date_dict', run_date_dict)
        setattr(self, 'max_run_date_key', max_run_date_key)
        setattr(self, 'processing_code', processing_code)
        setattr(self, 'grouping', grouping)

        pass


    def load_data(self, data, parameter, time=None, height=None):
        """
        Load an xr.Dataset into the class and perform checks.

        Parameters
        ----------
        data : xr.Dataset
            The data
        parameter : str
            The parameter name.
        time : str, pd.Timestamp, or None
            If time is not already in the data as a dimension (if this is a raster), then this values will be added to the data.
        height : int, float, or None
            If height is not already in the data as a dimension, then this values will be added to the data.

        """
        if hasattr(self, 'data'):
            delattr(self, 'data')

        arr = data.copy()

        ## Get the dimension data
        dims = arr.dims

        # Check and add dimensions if necessary
        if not 'lon' in dims:
            raise ValueError('lon must be a dimension.')
        if not 'lat' in dims:
            raise ValueError('lat must be a dimension.')

        if not 'time' in dims:
            if not isinstance(time, (str, pd.Timestamp)):
                raise ValueError("If time is not part of the array's dimensions, then a string or Timestamp must be passed to time.")
            else:
                print('time will be added to the data.')
                time1 = pd.Timestamp(time)
                arr = arr.assign_coords({'time': time1})
                arr = arr.expand_dims('time')

        if not 'height' in dims:
            if not isinstance(height, (int, float)):
                raise ValueError("If height is not part of the array's dimensions, then a int or float must be passed to height.")
            else:
                print('height will be added to the data.')
                arr = arr.assign_coords({'height': height})
                arr = arr.expand_dims('height')

        setattr(self, 'data', arr)
        setattr(self, 'parameter', parameter)

        pass


    def determine_grid_block_size(self, starting_x_size=10, starting_y_size=10, increment=10, min_size=800, max_size=1100):
        """
        Function to determine the appropriate grid size for splitting.

        Parameters
        ----------
        arr : DataArray
            An xarray DataArray with at least x and y dimensions. It can have any number of dimensions, though it probably does not make much sense to have greater than 4 dimensions.
        starting_x_size : int
            The initial size or length of the smaller grids in the x dimension.
        starting_y_size : int
            The initial size or length of the smaller grids in the y dimension.
        increment : int
            The incremental grid size to be added iteratively to the starting sizes.
        min_size : int
            The minimum acceptable object size in KB.
        max_size : int
            The maximum acceptable object size in KB.
        x_name : str
            The x dimension name.
        y_name : str
            The y dimension name.

        Returns
        -------
        dict
            Of the optimised grid size results.
        """
        encoding = {'lon': {'dtype': 'int32', '_FillValue': -999999, 'scale_factor': 1e-07},
 'lat': {'dtype': 'int32', '_FillValue': -999999, 'scale_factor': 1e-07},
 'altitude': {'dtype': 'int32', '_FillValue': -9999, 'scale_factor': 0.001},
 'time': {'_FillValue': -99999999, 'units': 'days since 1970-01-01 00:00:00'}}

        encoding.update(self.datasets[0]['properties']['encoding'])

        max_obj_size = 0
        x_size = starting_x_size
        y_size = starting_y_size

        while True:
            block_list = _split_grid(self.data[self.parameter], x_size=x_size, y_size=y_size)
            block_list2 = [a.to_dataset() for a in block_list]

            for block in block_list2:
                for k, v in encoding.items():
                    if k in block:
                        block[k].encoding = v

            obj_sizes = [len(write_pkl_zstd(nc.to_netcdf())) for nc in block_list2]
            max_obj_size = max(obj_sizes)

            if max_obj_size < min_size*1000:
                x_size = x_size + increment
                y_size = y_size + increment
            else:
                break

        if max_obj_size > max_size*1000:
            print('max_object_size:', str(max_obj_size))
            raise ValueError('max object size is greater than the allotted size. Reduce the increment value and start again.')

        obj_dict = {'x_size': x_size, 'y_size': y_size, 'max_obj_size': max_obj_size, 'min_obj_size': min(obj_sizes), 'sum_obj_size': sum(obj_sizes), 'len_obj': len(obj_sizes)}

        setattr(self, 'grid_size_dict', obj_dict)

        return obj_dict


    def save_results(self, x_size=None, y_size=None, threads=30):
        """

        """
        ## Create the data_dict
        data_dict = {d['dataset_id']: [] for d in self.datasets}

        ## Process data
        print('Processing data...')

        if self.grouping == 'blocks':
            if not (isinstance(x_size, int) and isinstance(y_size, int)):
                raise TypeError('x_size and y_size must be ints.')

            block_list = _split_grid(self.data[self.parameter], x_size=x_size, y_size=y_size)
            # TODO: add in option to save ancilliary variables

            for block in block_list:
                prepare_results(data_dict, self.datasets, block.to_dataset(), self.max_run_date_key)
        else:
            data1 = self.data.stack(geometry=['lon', 'lat'])
            g2 = data1.groupby('geometry', squeeze=False)

            for index, g in g2:
                res1 = g.unstack('geometry')
                prepare_results(data_dict, self.datasets, res1, self.max_run_date_key)

        ## Update to S3
        print('Updating data on S3')
        update_results_s3(self.processing_code, data_dict, self.run_date_dict, self.s3_remote, threads, self.public_url)

        print('Processing and saving data has been successful!')


    def update_aggregates(self, threads=60):
        """

        """
        ## Update the datasets and station jsons
        print('Aggregating dataset and station data.')
        s3 = s3_connection(self.s3_remote['connection_config'], threads)

        for ds in self.datasets:
            ds_new = put_remote_dataset(s3, self.s3_remote['bucket'], ds)
            ds_stations = put_remote_agg_stations(s3, self.s3_remote['bucket'], ds['dataset_id'], threads)

        # Aggregate all datasets for the bucket
        ds_all = put_remote_agg_datasets(s3, self.s3_remote['bucket'], threads)

        print('Updating the aggregates has been successful!')

















