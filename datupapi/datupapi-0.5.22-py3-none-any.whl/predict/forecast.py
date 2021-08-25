import boto3
import os
import pandas as pd
import time

from datupapi.configure.config import Config


class Forecast(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path


    def create_forecast_deepar(self, forecast_name, predictor_arn):
        """
        Return a JSON response for AWS Forecast's create_forecast API calling

        :param forecast_name: Forecast's name to uniquely identify.
        :param predictor_arn: ARNs that identifies the predictor that produced backtesting.
        :return response: API's response

        >>> response = create_forecast(forecast_name='my_forecast', predictor_arn='arn:aws:forecast:us-east-1:account-id:predictor/my_predictor')
        >>> response = 'arn:aws:forecast:us-east-1:147018152776:forecast/my_forecast'
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        try:
            response = client.create_forecast(
                ForecastName=forecast_name,
                PredictorArn=predictor_arn,
                ForecastTypes=self.forecast_types
            )
        except client.exceptions.ResourceAlreadyExistsException as err:
            self.logger.exception(f'The forecast already exists. Please forecast name: {err}')
            return False
        except client.exceptions.ResourceNotFoundException as err:
            self.logger.exception(f'The forecast is not found. Please forecast name: {err}')
            return False
        except client.exceptions.ResourceInUseException as err:
            self.logger.exception(f'Predictor creation in progress. Please wait some minutes: {err}')
            return False
        return response['ForecastArn']


    def create_forecast_export_deepar(self, export_job, forecast_arn, export_path):
        """
        Return a JSON response for AWS Forecast's create_forecast API calling

        :param export_job: Forecast export job's name to uniquely identify.
        :param forecast_arn: ARNs that identifies the forecast.
        :param export_path: S3 bucket's path to export the forecast. Do not include bucket's name.
        :return response: API's response

        >>> response = create_forecast_export_deepar(export_job='my_export', forecast_arn='arn:aws:forecast:us-east-1:account-id:forecast/my_forecast', export_path='path/to/export')
        >>> response = 'arn:aws:forecast:us-east-1:147018152776:forecast-export/my_forecast_export'
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        try:
            response = client.create_forecast_export_job(
                ForecastExportJobName=export_job,
                ForecastArn=forecast_arn,
                Destination={
                    'S3Config': {
                        'Path': os.path.join('s3://', self.datalake, export_path),
                        'RoleArn': self.forecast_role
                    }
                }
            )
        except client.exceptions.ResourceAlreadyExistsException as err:
            self.logger.exception(f'The forecast export already exists. Please forecast export name: {err}')
            return False
        except client.exceptions.ResourceNotFoundException as err:
            self.logger.exception(f'The forecast export is not found. Please forecast export name: {err}')
            return False
        except client.exceptions.ResourceInUseException as err:
            self.logger.exception(f'Forecast creation in progress. Please wait some minutes: {err}')
            return False
        return response['ForecastExportJobArn']


    def list_forecasts_deepar(self):
        """
        Return a JSON response for AWS Forecast's list_forecasts API calling

        :return response: API's response

        >>> response = list_forecasts_deepar()
        >>> response = {'ForecastArn': 'arn:aws:forecast:us-east-1:147018152776:forecast/my_forecast'}
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        response = client.list_forecasts(
            MaxResults=100,
            Filters=[
                {
                    "Condition": "IS_NOT",
                    "Key": "Status",
                    "Value": "ACTIVE"
                }
            ]
        )
        return response['Forecasts']


    def list_forecast_export_deepar(self):
        """
        Return a JSON response for AWS Forecast's list_forecast_export_jobs API calling

        :return response: API's response

        >>> response = list_forecast_export_deepar()
        >>> response = {'ForecastExportJobArn': 'arn:aws:forecast:us-east-1:147018152776:forecast-export-job/my_export'}
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        response = client.list_forecast_export_jobs(
            MaxResults=100,
            Filters=[
                {
                    "Condition": "IS_NOT",
                    "Key": "Status",
                    "Value": "ACTIVE"
                }
            ]
        )
        return response['ForecastExportJobs']


    def delete_forecast_deepar(self, arn_forecast):
        """
        Delete the specified forecast resource

        :param arn_forecast: ARNs that identifies the forecast.
        :return None:

        >>> delete_forecast_deepar(arn_forecast='arn:aws:forecast:us-east-1:147018152776:forecast/my_forecast')
        >>> None
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        response = client.delete_forecast(ForecastArn=arn_forecast)
        time.sleep(300)
        return None


    def check_status(self, arn_target, check_type):
        """
        Return a True or False flag to determine whether the status in progress

        :param arn_target: ARN to check with the API calling to resources in progress
        :param check_type: Type of status check, either import or predictor
        :return False: Determine the status check is done

        >>> check_status(arn_target='arn:aws:forecast:us-east-1:147018152776:forecast/my_forecast', check_type='forecast')
        >>> False
        """
        in_progress = True
        if check_type == 'forecast':
            while in_progress:
               in_progress = any(arn['ForecastArn'] == arn_target for arn in self.list_forecasts_deepar())
               time.sleep(300)
        elif check_type == 'export':
            while in_progress:
               in_progress = any(arn['ForecastExportJobArn'] == arn_target for arn in self.list_forecast_export_deepar())
               time.sleep(300)
        else:
            self.logger.debug(f'Invalid check type option. Choose from import or predictor')
        return in_progress


