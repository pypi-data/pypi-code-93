import os
import shutil

class ConceptualHierarchy:
    def __init__(self, name:str=None):
        self.__level = 0
        self.__name = name if name else None

    def __str__(self):
        return self.__name

    def hierarchy(self, name:str=None): 
        instance = super().__new__(type(self))
        instance.__init__(name=name)
        return instance

    def _rename(self, name:str):
        self.__name = name

    @property
    def name(self):
        return self.__name

class BasePolicyHierarchy:
    def __init__(self, name:str=None):
        self.__path = ''
        self.__parent_name = ''
        self.__ascendants = list()
        self.__level = 0
        self.__name = name if name else None

    def __str__(self):
        return self.__name

    def hierarchy(self, name:str=None): 
        instance = super().__new__(type(self))
        instance.__init__(name=name)
        return instance

    def compiling(self, mkdir:bool=False):
        if mkdir:
            path = str(self)
            if not os.path.isdir(path):
                os.mkdir(path)

        children = self._compiling(self, mkdir=mkdir)
        while children:
            _children = list()
            for child in children:
                _children.extend(self._compiling(child, mkdir))
            children = _children

    @staticmethod
    def _compiling(parent, mkdir:bool=False):
        selected_objs = filter(lambda x: isinstance(x[1], type(parent)), vars(parent).items())
        children = list(map(lambda child: vars(parent)[child[0]], selected_objs))
        for child_obj in children:
            child_obj.parent_name = parent.name
            child_obj.ascendants = (parent.ascendants, parent.name)
            child_obj.path = child_obj.ascendants + [child_obj.name]
            child_obj.level = parent.level + 1
            if mkdir:
                path = child_obj.path
                if not os.path.isdir(path):
                    os.mkdir(path)
        return children

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, bases:list):
        self.__path = os.path.join(*bases)

    @property
    def parent_name(self):
        return self.__parent_name

    @parent_name.setter
    def parent_name(self, name:str):
        self.__parent_name = name

    @property
    def ascendants(self):
        return self.__ascendants

    @ascendants.setter
    def ascendants(self, ascendants:tuple):
        self.__ascendants.extend(ascendants[0])
        self.__ascendants.append(ascendants[1])

    def _rename(self, name:str):
        self.__name = name

    def listdir(self, format:str=None):
        self._listdir = os.listdir(self.__path)
        if format:
            assert isinstance(format, str), 'The format argements must be object of string-type.'
            self._listdir = list(filter(lambda x: x[-len(format):]==format, self._listdir))
        return self._listdir

    def listfiles(self, format:str=None):
        self._listfiles = [file for file in os.listdir(self.__path) if os.path.isfile(os.path.join(self.__path, file))]
        if format:
            assert isinstance(format, str), 'The format argements must be object of string-type.'
            self._listfiles = list(filter(lambda x: x[-len(format):]==format, self._listfiles))
        return self._listfiles

    def remove(self, name:str):
        path = os.path.join(self.__path, name)
        if os.path.isfile(path):
            os.remove(path)

    def rmdir(self, name:str):
        path = os.path.join(self.__path, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
    
    def mkdir(self, name:str):
        path = os.path.join(self.__path, name)
        if not os.path.isdir(path):
            os.mkdir(path)

    @property
    def name(self):
        return self.__name

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, level:int):
        self.__level = level


def initialization_policy(local_environment:dict=None, remote_environment:dict=None):

    r"""
    Usage:
        >>> from ailever.investment import __fmlops_bs__ as fmlops_bs
        >>> fmlops_bs.local_system.root.model_registry.listdir()  # files in directory
        >>> fmlops_bs.local_system.root.model_registry.remove()   # delete file
        >>> fmlops_bs.local_system.root.model_registry.rmdir()    # delete folder
        >>> fmlops_bs.local_system.root.model_registry.path
        >>> fmlops_bs.local_system.root.model_registry.name
    """

    # Financial MLOps Basic Structure(Default)
    fmlops_bs = ConceptualHierarchy('FMLOps_BasicStructure')
    fmlops_bs.local_system = fmlops_bs.hierarchy('local_system')

    fmlops = BasePolicyHierarchy('.fmlops')
    fmlops_bs.local_system.root = fmlops
    fmlops_bs.local_system.root.feature_store = fmlops.hierarchy('feature_store')
    fmlops_bs.local_system.root.source_repository = fmlops.hierarchy('source_repository')
    fmlops_bs.local_system.root.model_registry = fmlops.hierarchy('model_registry')
    fmlops_bs.local_system.root.analysis_report_repository = fmlops.hierarchy('analysis_report_repository')
    fmlops_bs.local_system.root.investment_outcome_repository = fmlops.hierarchy('investment_outcome_repository')
    fmlops_bs.local_system.root.metadata_store = fmlops.hierarchy('metadata_store')

    fmlops_bs.local_system.root.model_registry.forecasting_model_registry = fmlops.hierarchy('forecasting_model_registry')
    fmlops_bs.local_system.root.model_registry.strategy_model_registry = fmlops.hierarchy('strategy_model_registry')
    fmlops_bs.local_system.root.analysis_report_repository.fundamental_analysis_result = fmlops.hierarchy('fundamental_analysis_result')
    fmlops_bs.local_system.root.analysis_report_repository.technical_analysis_result = fmlops.hierarchy('technical_analysis_result')
    fmlops_bs.local_system.root.analysis_report_repository.model_prediction_result = fmlops.hierarchy('model_prediction_result')
    fmlops_bs.local_system.root.analysis_report_repository.sector_analysis_result = fmlops.hierarchy('sector_analysis_result')
    fmlops_bs.local_system.root.investment_outcome_repository.optimized_portfolio_registry = fmlops.hierarchy('optimized_portfolio_registry')
    fmlops_bs.local_system.root.investment_outcome_repository.backtesting_repository = fmlops.hierarchy('backtesting_repository')
    fmlops_bs.local_system.root.metadata_store.monitoring_source = fmlops.hierarchy('monitoring_source')
    fmlops_bs.local_system.root.metadata_store.data_management = fmlops.hierarchy('data_management')
    fmlops_bs.local_system.root.metadata_store.model_management = fmlops.hierarchy('model_management')
    fmlops_bs.local_system.root.metadata_store.model_specification = fmlops.hierarchy('model_specification')


    if local_environment:
        assert isinstance(local_environment, dict), 'The local_environment information must be supported by wtih dictionary data-type.'
        
        # just for renaming
        fmlops_bs.local_system.root._rename(local_environment['root'])
        fmlops_bs.local_system.root.feature_store._rename(local_environment['feature_store'])
        fmlops_bs.local_system.root.source_repository._rename(local_environment['source_repository'])
        fmlops_bs.local_system.root.model_registry._rename(local_environment['model_registry'])
        fmlops_bs.local_system.root.analysis_report_repository._rename(local_environment['analysis_report_repository'])
        fmlops_bs.local_system.root.investment_outcome_repository._rename(local_environment['investment_outcome_repository'])
        fmlops_bs.local_system.root.metadata_store._rename(local_environment['metadata_store'])

    fmlops.compiling(mkdir=True)

    r"""

- [FMLOPS] .fmlops
  |-- [FS] feature_store [Semi-Automation]
  |-- [SR] source_repository [Semi-Automation]
  |-- [MR] model_registry [Automation]
      |-- [FMR] forecasting_model_registry [Automation]
      |-- [SMR] strategy_model_registry [Heuristic Semi-Automation]
  |-- [ARR] analysis_report_repository [Heuristic Semi-Automation]
      |-- [FAR] fundamental_analysis_result
      |-- [TAR] technical_analysis_result
      |-- [MPR] model_prediction_result
      |-- [SAR] sector_analysis_result
  |-- [IOR] investment_outcome_repository [Automation]
      |-- [OPR] optimized_portfolio_registry
      |-- [BR] backtesting_repository
  |-- [MS] metadata_store [Automation]
      |-- [MS1] monitoring_source [Automation]
      |-- [DM] data_management
      |-- [MM] model_management
      |-- [MS2] model_specification

    """

    fmlops_bs.local_base_dir_core = dict()
    fmlops_bs.local_base_dir_core['FMLOPS'] = fmlops_bs.local_system.root
    fmlops_bs.local_base_dir_core['FS'] = fmlops_bs.local_system.root.feature_store
    fmlops_bs.local_base_dir_core['SR'] = fmlops_bs.local_system.root.source_repository
    fmlops_bs.local_base_dir_core['MR'] = fmlops_bs.local_system.root.model_registry
    fmlops_bs.local_base_dir_core['FMR'] = fmlops_bs.local_system.root.model_registry.forecasting_model_registry
    fmlops_bs.local_base_dir_core['SMR'] = fmlops_bs.local_system.root.model_registry.strategy_model_registry
    fmlops_bs.local_base_dir_core['ARR'] = fmlops_bs.local_system.root.analysis_report_repository
    fmlops_bs.local_base_dir_core['RAR'] = fmlops_bs.local_system.root.analysis_report_repository.fundamental_analysis_result
    fmlops_bs.local_base_dir_core['TAR'] = fmlops_bs.local_system.root.analysis_report_repository.technical_analysis_result
    fmlops_bs.local_base_dir_core['MPR'] = fmlops_bs.local_system.root.analysis_report_repository.model_prediction_result
    fmlops_bs.local_base_dir_core['SAR'] = fmlops_bs.local_system.root.analysis_report_repository.sector_analysis_result
    fmlops_bs.local_base_dir_core['IOR'] = fmlops_bs.local_system.root.investment_outcome_repository
    fmlops_bs.local_base_dir_core['OPR'] = fmlops_bs.local_system.root.investment_outcome_repository.optimized_portfolio_registry
    fmlops_bs.local_base_dir_core['BR'] = fmlops_bs.local_system.root.investment_outcome_repository.backtesting_repository
    fmlops_bs.local_base_dir_core['MS'] = fmlops_bs.local_system.root.metadata_store
    fmlops_bs.local_base_dir_core['MS1'] = fmlops_bs.local_system.root.metadata_store.monitoring_source
    fmlops_bs.local_base_dir_core['DM'] = fmlops_bs.local_system.root.metadata_store.data_management
    fmlops_bs.local_base_dir_core['MM'] = fmlops_bs.local_system.root.metadata_store.model_management
    fmlops_bs.local_base_dir_core['MS2'] = fmlops_bs.local_system.root.metadata_store.model_specification

    return fmlops_bs



