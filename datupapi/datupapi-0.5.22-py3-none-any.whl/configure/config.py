import logging
import os
import yaml

from datetime import date, datetime, timedelta


class Config():

    LOCAL_PATH = '/tmp'

    def __init__(self, config_file=None, logfile=None):
        try:
            #Initialize config parameters
            with open(config_file) as file:
                params = yaml.full_load(file)
            self.access_key = params.get('aws_access_key')
            self.secret_key = params.get('aws_secret_key')
            self.region = params.get('aws_region')
            self.tenant_id = params.get('tenant_id')
            self.datalake = params.get('datalake')
            self.sql_database = params.get('sql_database')
            self.config_path = params.get('config_path')
            self.response_path = params.get('response_path')
            self.forecast_role = params.get('forecast_role')
            # Initialize Prepare training parameters
            self.dataset_orig_cols = params.get('prepare')[0].get('dataset_orig_cols')
            self.items_metadata = params.get('prepare')[1].get('items_metadata')
            # Initialize DeepAR training parameters
            self.dataset_frequency = params.get('deepar_training')[0].get('dataset_frequency')
            self.forecast_horizon = params.get('deepar_training')[1].get('forecast_horizon')
            self.forecast_types = params.get('deepar_training')[2].get('forecast_types')
            self.input_window = params.get('deepar_training')[3].get('input_window')
            self.epochs = params.get('deepar_training')[4].get('epochs')
            self.neurons = params.get('deepar_training')[5].get('neurons')
            self.hidden_layers = params.get('deepar_training')[6].get('hidden_layers')
            self.backtests = params.get('deepar_training')[7].get('backtests')
            self.backtest_horizon = params.get('deepar_training')[8].get('backtest_horizon')
            self.use_location = params.get('deepar_training')[9].get('use_location')
            self.use_automl = params.get('deepar_training')[10].get('use_automl')
            self.dataset_import_path = params.get('deepar_training')[11].get('dataset_import_path')
            self.backtest_export_path = params.get('deepar_training')[12].get('backtest_export_path')
            # Initialize Attention model training parameters
            self.models_export_path = params.get('attup_training')[0].get('models_export_path')
            self.n_backtests = params.get('attup_training')[1].get('n_backtests')
            self.n_steps_out = params.get('attup_training')[2].get('n_steps_out')
            self.n_steps_in = params.get('attup_training')[3].get('n_steps_in')
            self.location = params.get('attup_training')[4].get('location')
            self.save_last_epoch = params.get('attup_training')[5].get('save_last_epoch')
            self.normalization = params.get('attup_training')[6].get('normalization')
            self.lr = params.get('attup_training')[7].get('lr')
            self.units = params.get('attup_training')[8].get('units')
            self.batch_size = params.get('attup_training')[9].get('batch_size')
            self.epochs = params.get('attup_training')[10].get('epochs')
            self.dropout = params.get('attup_training')[11].get('dropout')
            self.dropout_train = params.get('attup_training')[12].get('dropout_train')
            self.n_iter = params.get('attup_training')[13].get('n_iter')
            self.momentum = params.get('attup_training')[14].get('momentum')
            self.lrS = params.get('attup_training')[15].get('lrS')
            self.sku_impct = params.get('attup_training')[16].get('sku_impct')
            # Initialize DeepAR prediction parameters
            self.forecast_export_path = params.get('deepar_prediction')[0].get('forecast_export_path')
            # Initialize Transform parameters
            self.abc_threshold = params.get('transform')[0].get('abc_threshold')
            self.fsn_threshold = params.get('transform')[1].get('fsn_threshold')
            self.xyz_threshold = params.get('transform')[2].get('xyz_threshold')
            self.export_item_ranking = params.get('transform')[3].get('export_item_ranking')
            self.backtest_ids = params.get('transform')[4].get('backtest_ids')
            self.error_ids = params.get('transform')[5].get('error_ids')
            self.upsample_frequency = params.get('transform')[6].get('upsample_frequency')
            self.results_path = params.get('transform')[7].get('results_path')
            self.multiforecast_path = params.get('transform')[8].get('multiforecast_path')
            self.sftp_export = params.get('transform')[9].get('sftp_export')
            # Initialize logger
            self.logfile = logfile + '_' + datetime.today().strftime("%Y%m%d-%H%M%S") + '.log'
            self.logger = logging.getLogger('__name__')
            self.logger.setLevel(logging.DEBUG)
            self.file_handler = logging.FileHandler(os.path.join(Config.LOCAL_PATH, self.logfile))
            self.file_format = logging.Formatter('%(asctime)s|%(levelname)s|%(name)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            self.file_handler.setLevel(logging.DEBUG)
            self.file_handler.setFormatter(self.file_format)
            self.logger.addHandler(self.file_handler)
        except FileNotFoundError as err:
            self.logger.exception(f'Config file not found. Please check entered path: {err}')
            raise
        finally:
            file.close()