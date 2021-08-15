from ailever.investment import __fmlops_bs__ as fmlops_bs
from ..__base_structures import BaseManagement

import datetime
from pytz import timezone
import re


class ForecastingModelRegistryManager(BaseManagement):
    def __init__(self):
        self.__core = fmlops_bs.core['FMR'] 
        self.__framework = None
        self.latest_specifications_in_local_system = dict()
        self.latest_specifications_in_remote_system = dict()
        r"""
        * management policy
        1. self.__framework : it's about a specific framework defined for training a model through fmlops_forecasters/[framework]/*.py.
        2. argument framework : it's about a framework for UI(user interface) Design.
           2.1 forecaster.model_registry('listdir', framework='torch')
           2.2 forecaster.model_registry('remove')
           2.3 forecaster.model_registry('clearall')
            ...
            ...

        * model nomenclature
        model[id]_[framework]_[architecture]_[ticker]_[training_data_period_start]_[training_data_period_end]_[packet_size]_[perdiction_range]_v[version]_[rep]_[message]_[time]
        example) model1_torch_lstm_are_20210324_20210324_365_100_v1_ailever_TargetingMarketCapital_2021_08_10
           - self.id : [id]
           - self.framework : [framework]
           - self.architecture : [architecture]
           - self.ticker : [ticker]
           - self.training_data_period_start : [training_data_period_start]
            ...
            ...
        """
        
    def __iter__(self):
        return self

    def __next__(self):
        if self.country == 'united_states':
            today = datetime.datetime.now(timezone('US/Eastern'))
        if self.country == 'korea':
            today = datetime.datetime.now(timezone('Asia/Seoul'))

        self.id += 1
        self.time = today.strftime(format='%Y%m%d-%H%M%S')

        id = self.id # [1]
        framework = self.framework # [2]
        architecture = self.architecture # [3]
        ticker = self.ticker # [4]
        training_data_period_start = self.training_data_period_start # [5]
        training_data_period_end = self.training_data_period_end # [6]
        packet_size = self.packet_size # [7]
        prediction_interval = self.prediction_interval # [8]
        version = self.version # [9]
        rep = self.rep # [10]
        message = self.message # [11]
        time = self.time # [12]

        name = f'model{id}_{framework}_{architecture}_{ticker}_{training_data_period_start}_{training_data_period_end}_{packet_size}_{prediction_interval}_v{version}_{rep}_{message}_{time}'
        return name
 
    def __local_system_model_management(self, framework:str=None):
        if framework:
            self.__framework = framework
        else:
            assert hasattr(self, '_ForecastingModelRegistryManager__framework'), '__framework must be defined through self.loading_connection from the UI_Transformation function on fmlops_forecasters/[framework]/*.py' 

        if self.__framework == 'torch':
            model_saving_names = self.__core.listfiles(format='pt')
        elif self.__framework == 'tensorflow':
            model_saving_names = self.__core.listfiles(format='ckpt')
        elif self.__framework == 'sklearn':
            model_saving_names = self.__core.listfiles(format='joblib')
        elif self.__framework == 'statsmodels':
            model_saving_names = self.__core.listfiles(format='pkl')
        else:
            assert False, 'The framework is not yet supported.'


        self.model = dict()
        for model_saving_name in model_saving_names:
            pattern = '(.+)_'*12
            re_obj = re.search(pattern[:-1], model_saving_name)
            
            # saving information
            id = int(re_obj.group(1)[5:])
            self.model[id] = {'model_saving_name': model_saving_name,
                              'framework': re_obj.group(2),
                              'architecture': re_obj.group(3),
                              'ticker': re_obj.group(4),
                              'start': re_obj.group(5),
                              'end': re_obj.group(6),
                              'packet_size': re_obj.group(7),
                              'prediction_interval': re_obj.group(8),
                              'version': re_obj.group(9)[1:],
                              'rep': re_obj.group(10),
                              'message': re_obj.group(11),
                              'time': re_obj.group(12),
                              }

    def __remote_system_model_management(self, framework:str=None):
        pass

    def _local_filesystem_user_interfaces(self, framework:str=None):
        if framework == 'torch':
            model_saving_names = self.__core.listfiles(format='pt')
        elif framework == 'tensorflow':
            model_saving_names = self.__core.listfiles(format='ckpt')
        elif framework == 'sklearn':
            model_saving_names = self.__core.listfiles(format='joblib')
        elif framework == 'statsmodels':
            model_saving_names = self.__core.listfiles(format='pkl')
        else:
            model_saving_names = self.__core.listfiles(format=None)

        self.model = dict()
        for model_saving_name in model_saving_names:
            pattern = '(.+)_'*12
            re_obj = re.search(pattern[:-1], model_saving_name)
            
            # saving information
            id = int(re_obj.group(1)[5:])
            self.model[id] = {'model_saving_name': model_saving_name,
                              'framework': re_obj.group(2),
                              'architecture': re_obj.group(3),
                              'ticker': re_obj.group(4),
                              'start': re_obj.group(5),
                              'end': re_obj.group(6),
                              'packet_size': re_obj.group(7),
                              'prediction_interval': re_obj.group(8),
                              'version': re_obj.group(9)[1:],
                              'rep': re_obj.group(10),
                              'message': re_obj.group(11),
                              'time': re_obj.group(12),
                              }

    def _remote_filesystem_user_interfaces(self):
        pass

    def _local_search(self, entity:str):
        self.__local_system_model_management()
        if not self.model:
            if entity=='latest_id':
                return 0
            elif entity=='latest_version':
                return 1
        else:
            latest_id = max(self.model.keys())
            latest_version = self.model[latest_id]['version']
            if entity=='latest_id':
                return latest_id
            elif entity=='latest_version':
                return latest_version

    def _remote_search(self, entity:str):
        pass

    def local_finder(self, entity:str, target:str, framework:str=None):
        self._local_filesystem_user_interfaces(framework=framework)
        if entity == 'id':
            id = int(target)
            if id in self.model.keys():
                model_saving_infomation = self.model[id]
                return model_saving_infomation # dict
            else:
                model_saving_infomation = dict()
                return model_saving_information # dict

        elif entity == 'ticker':
            target = str(target)
            model_saving_informations = list(filter(lambda x: x[entity] == target, self.model.values()))
            model_saving_informations = list(filter(lambda x: x[entity] == target, self.model.values()))
            return model_saving_informations # list of dicts

    def remote_finder(self, entity:str, target:str, framework:str=None):
        if entity=='id':
            return dict()
        elif entity=='ticker':
            return [{}]

    def remove(self, name:str, framework:str=None):
        self.__core.remove(name=name)

    def clearall(self, framework:str=None):
        self._local_filesystem_user_interfaces(framework=framework)
        for id in self.model.keys():
            file = self.model[id]['model_saving_name']
            self.__core.remove(name=file)

    def listfiles(self, framework:str=None):
        self._local_filesystem_user_interfaces(framework=framework)
        model_saving_names = list(map(lambda x: x['model_saving_name'], self.model.values()))
        return model_saving_names

    def listdir(self, framework:str=None):
        return self.__core.listdir(format=None)

    # It's a pair with storing_connection
    def local_loading_connection(self, specification, usage='train'):
        self.__local_system_model_management(framework=specification['framework'])
        if not self.model.keys():
            specification['loading_model_name_from_local_model_registry'] = None
            return specification
        else:
            # ID exsistance in specification
            if 'id' in specification.keys():
                id = int(specification['id'])
                if id in self.model.keys():
                    specification['loading_model_name_from_local_model_registry'] = self.model[id]['model_saving_name']
                    return specification
            else:
                specification['loading_model_name_from_local_model_registry'] = None
                return specification
    
    # It's a pair with loading_connection
    def local_storing_connection(self, specification, usage='train'):
        self.country = specification['country']
        self.id = self._local_search(entity='latest_id')                           # [1] : model1
        self.framework = specification['framework']                                # [2] : torch
        self.architecture = specification['architecture']                          # [3] : lstm00
        self.ticker = specification['ticker']                                      # [4] : ARE
        self.training_data_period_start = specification['start']                   # [5] : '20200101'
        self.training_data_period_end = specification['end']                       # [6] : '20210801'
        self.packet_size = specification['packet_size']                            # [7] : 365
        self.prediction_interval = specification['prediction_interval']            # [8] : 100
        self.version = self._local_search(entity='latest_version')                 # [9] : 1
        self.rep = specification['rep']                                            # [10] : ailever
        self.message = specification['message']                                    # [11] 'TargetingMarketCaptial'
        
        specification['saving_name_in_local_model_registry'] = next(self)
        specification['saving_path'] = self.__core.path
        self.latest_specifications_in_local_system[specification['ticker']] = specification
        return specification

    def remote_loading_connection(self, specification, usage='train'):
        return specification

    def remote_storing_connection(self, specification, usage='train'):
        return specification
