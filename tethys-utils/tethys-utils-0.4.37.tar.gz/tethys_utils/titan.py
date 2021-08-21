#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 13:39:58 2021

@author: mike
"""
import tethys_utils as tu
from tethysts.utils import s3_connection
# import boto3
# import botocore
import requests
# import ray

##############################################
### Parameters


###############################################
### Class


class Titan(object):
    """

    """

    def __init__(self):
        """

        """

        pass


    def init_results_dict(self):
        """

        """
        results_dict = {d: [] for d in self.datasets}
        setattr(self, 'results_dict', results_dict)


    def load_dataset_metadata(self, datasets):
        """

        """
        # TODO : add in more dataset checks
        dataset_list = tu.processing.process_datasets(datasets)

        ds_dict = {ds['dataset_id']: ds for ds in dataset_list}

        setattr(self, 'dataset_list', dataset_list)
        setattr(self, 'datasets', ds_dict)

        self.init_results_dict()

        return dataset_list


    def load_connection_params(self, connection_config, bucket, public_url=None):
        """

        """
        ## Test S3 connection
        s3 = s3_connection(connection_config)

        try:
            head1 = s3.head_bucket(Bucket=bucket)
        except Exception as err:
            response_code = err.response['Error']['Code']
            if response_code == '403':
                raise requests.exceptions.ConnectionError('403 error. The connection_config is probably wrong.')
            elif response_code == '404':
                raise requests.exceptions.ConnectionError('404 error. The bucket was not found.')

        ## Save parameters
        setattr(self, 'connection_config', connection_config)
        setattr(self, 'bucket', bucket)


    def load_run_date(self, processing_code, run_date=None):
        """

        """
        remote = {'connection_config': self.connection_config, 'bucket': self.bucket}

        run_date_dict = tu.s3.process_run_date(processing_code, self.dataset_list, remote, run_date)
        max_run_date_key = max(list(run_date_dict.values()))

        setattr(self, 'processing_code', processing_code)
        setattr(self, 'run_date_dict', run_date_dict)
        setattr(self, 'max_run_date_key', max_run_date_key)


    def load_result(self, dataset_id, result, sum_closed='right', other_closed='left', discrete=True, other_attrs=None, other_encoding=None, run_date=None):
        """

        """
        ## result checks
        if len(result.squeeze().dims) > 0:
            dataset = self.datasets[dataset_id]

            if isinstance(run_date, str):
                run_date_key = tu.misc.make_run_date_key(run_date)
            else:
                run_date_key = self.max_run_date_key

            out1 = tu.processing.prepare_results_v02(dataset, result, run_date_key, sum_closed=sum_closed, other_closed=other_closed, discrete=discrete, other_attrs=other_attrs, other_encoding=other_encoding)

            if out1 is not None:
                self.results_dict[dataset_id].append(out1)
        else:
            print('results only have one value per dimension.')


    def update_results(self, threads=30):
        """

        """
        remote = {'connection_config': self.connection_config, 'bucket': self.bucket}

        tu.s3.update_results_s3(self.processing_code, self.results_dict, self.run_date_dict, remote, threads=threads, public_url=self.public_url)

        self.results_dict = {}


    def update_aggregates(self, threads=60):
        """

        """
        ## Update the datasets and station jsons
        print('Aggregating dataset and station data.')
        s3 = s3_connection(self.s3_remote['connection_config'], threads)

        for ds in self.datasets:
            ds_new = tu.s3.put_remote_dataset(s3, self.s3_remote['bucket'], ds)
            ds_stations = tu.s3put_remote_agg_stations(s3, self.s3_remote['bucket'], ds['dataset_id'], threads)

        # Aggregate all datasets for the bucket
        ds_all = tu.s3.put_remote_agg_datasets(s3, self.s3_remote['bucket'], threads)

        print('Updating the aggregates has been successful!')













################################
### Testing


   # def init_ray(self, num_cpus=1, include_dashboard=False, configure_logging=False, **kwargs):
    #     """

    #     """
    #     if ray.is_initialized():
    #         ray.shutdown()

    #     ray.init(num_cpus=num_cpus, include_dashboard=include_dashboard, configure_logging=configure_logging, **kwargs)

    #     @ray.remote
    #     def _load_result(dataset, result, run_date_key, other_attrs, discrete, other_closed, sum_closed, other_encoding):
    #         """

    #         """
    #         out1 = tu.processing.prepare_results_v02(dataset, result, run_date_key, sum_closed=sum_closed, other_closed=other_closed, discrete=discrete, other_attrs=other_attrs, other_encoding=other_encoding)

    #         return out1

    #     self._load_result = _load_result
    #     self._obj_refs = []


    # def shutdown_ray(self):
    #     ray.shutdown()


    # def load_results(self, results, sum_closed='right', other_closed='left', discrete=True, other_attrs=None, other_encoding=None, run_date=None):
    #     """

    #     """
    #     ## Dataset checks
    #     # ds_ids = list(results.keys())

    #     if isinstance(run_date, str):
    #         run_date_key = tu.misc.make_run_date_key(run_date)
    #     else:
    #         run_date_key = self.max_run_date_key

    #     r1 = [self._load_result.remote(self.datasets[r['dataset_id']], r['result'], run_date_key, other_attrs, discrete, other_closed, sum_closed, other_encoding) for r in results]
    #     # r2 = ray.get(r1)

    #     self._obj_refs.extend(r1)
