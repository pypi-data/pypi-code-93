##################################################################################################
# Based on https://gitlab.cern.ch/atlas-physics/stat/tools/StatisticsTools
# Author: Alkaid Cheng
# Email: chi.lung.cheng@cern.ch
##################################################################################################
import os
import sys
import math
import logging
import fnmatch
from typing import List, Optional, Union, Dict

import ROOT

import quickstats
from quickstats.components.numerics import is_integer
from quickstats.utils.root_utils import load_macro
from quickstats.utils.io import VerbosePrint

_PRINT_ = VerbosePrint("INFO")

class ExtendedModel(object):
    
    _DEFAULT_NAMES_ = {
        'conditional_globs': 'conditionalGlobs_{mu}',
        'conditional_nuis': 'conditionalNuis_{mu}',
        'nominal_globs': 'nominalGlobs',
        'nominal_nuis': 'nominalNuis',
        'temp_globs': 'tmpGlobs',
        'temp_nuis': 'tmpNuis',
        'weight': 'weightVar',
        'dataset_args': 'obsAndWeight',
        'asimov': 'asimovData_{mu}',
        'channel_asimov': 'combAsimovData{index}',
        'nll_snapshot': '{nll_name}_{mu}'
    }
    
    def __init__(self, fname:str, ws_name:Optional[str]=None, mc_name:Optional[str]=None,
                 data_name:str="combData", snapshot_name:Optional[str]=None,
                 binned_likelihood:bool=True, tag_as_measurement:str="pdf_",
                 fix_cache:bool=True, fix_multi:bool=True, interpolation_code:int=-1,
                 load_extension:bool=True, verbosity:Union[int, str]="INFO"):
        self.fname = fname
        self.ws_name = ws_name
        self.mc_name = mc_name
        self.data_name = data_name
        self.snapshot_name = snapshot_name
        self.binned_likelihood = binned_likelihood
        self.tag_as_measurement = tag_as_measurement
        self.fix_cache = fix_cache
        self.fix_multi = fix_multi
        self.interpolation_code = interpolation_code
        _PRINT_.verbosity = verbosity
        if load_extension:
            self.load_extension()
        self.initialize()
  
    @property
    def file(self):
        return self._file
    @property
    def workspace(self):
        return self._workspace
    @property
    def model_config(self):
        return self._model_config
    @property
    def pdf(self):
        return self._pdf
    @property
    def data(self):
        return self._data
    @property
    def nuisance_parameters(self):
        return self._nuisance_parameters
    @property
    def global_observables(self):
        return self._global_observables
    @property
    def pois(self):
        return self._pois
    @property
    def observables(self):
        return self._observables        
    
    @staticmethod
    def load_extension():
        try:
            if not hasattr(ROOT, 'RooTwoSidedCBShape'):
                result = load_macro('RooTwoSidedCBShape')
                if hasattr(ROOT, 'RooTwoSidedCBShape'):
                    _PRINT_.info('INFO: Loaded extension module "RooTwoSidedCBShape"')
        except Exception as e:
            print(e)
            
    @staticmethod
    def load_RooFitObjects():
        load_macro('RooFitObjects')
        
    @staticmethod
    def modify_interp_codes(ws, interp_code, classes=None):
        if classes is None:
            classes = [ROOT.RooStats.HistFactory.FlexibleInterpVar, ROOT.PiecewiseInterpolation]
        for component in ws.components():
            for cls in classes:
                if (component.IsA() == cls.Class()):
                    component.setAllInterpCodes(interp_code)
                    class_name = cls.Class_Name().split('::')[-1]
                    _PRINT_.info('INFO: {} {} interpolation code set to {}'.format(component.GetName(),
                                                                            class_name,
                                                                            interp_code))
        return None

    @staticmethod
    def activate_binned_likelihood(ws):
        _PRINT_.info('INFO: Activating binned likelihood evaluation')
        for component in ws.components():
            if (component.IsA() == ROOT.RooRealSumPdf.Class()):
                component.setAttribute('BinnedLikelihood')
                _PRINT_.info('INFO: Activated binned likelihood attribute for {}'.format(component.GetName()))
        return None
                          
    @staticmethod
    def set_measurement(ws, condition):
        _PRINT_.info('INFO: Activating measurements to reduce memory consumption')
        for component in ws.components():
            name = component.GetName()
            if ((component.IsA() == ROOT.RooAddPdf.Class()) and condition(name)):
                component.setAttribute('MAIN_MEASUREMENT')
                _PRINT_.info('INFO: Activated main measurement attribute for {}'.format(name))
        return None
    
    @staticmethod
    def deactivate_lv2_const_optimization(ws, condition):
        _PRINT_.info('INFO: Deactivating level 2 constant term optimization for specified pdfs')
        for component in ws.components():
            name = component.GetName()
            if (component.InheritsFrom(ROOT.RooAbsPdf.Class()) and condition(name)):
                component.setAttribute("NOCacheAndTrack")
                _PRINT_.info('INFO: Deactivated level 2 constant term optimization for {}'.format(name))
            
    def initialize(self):
        if not os.path.exists(self.fname):
            raise FileNotFoundError('workspace file {} does not exist'.format(self.fname))
        _PRINT_.info('INFO: Opening file "{}"'.format(self.fname))
        file = ROOT.TFile(self.fname) 
        if (not file):
            raise RuntimeError("Something went wrong while loading the root file: {}".format(self.fname))
        # load workspace
        if self.ws_name is None:
            ws_names = [i.GetName() for i in file.GetListOfKeys() if i.GetClassName() == 'RooWorkspace']
            if not ws_names:
                raise RuntimeError("No workspaces found in the root file: {}".format(self.fname))
            if len(ws_names) > 1:
                _PRINT_.warning("WARNING: Found multiple workspace instances from the root file: {}. Available workspaces"
                      " are \"{}\". Will choose the first one by default".format(self.fname, ','.join(ws_names)))
            self.ws_name = ws_names[0]

        ws = file.Get(self.ws_name)
        if not ws:
            raise RuntimeError('failed to load workspace "{}"'.format(self.ws_name))
        _PRINT_.info('INFO: Loaded workspace "{}"'.format(self.ws_name))
        # load model config
        if self.mc_name is None:
            mc_names = [i.GetName() for i in ws.allGenericObjects() if 'ModelConfig' in i.ClassName()]
            if not mc_names:
                raise RuntimeError("no ModelConfig object found in the workspace: {}".format(ws_name))
            if len(mc_names) > 1:
                _PRINT_.warning("WARNING: Found multiple ModelConfig instances from the workspace: {}. "
                      "Available ModelConfigs are \"{}\". "
                      "Will choose the first one by default".format(ws_name, ','.join(mc_names)))
            self.mc_name = mc_names[0]
        model_config = ws.obj(self.mc_name)
        if not model_config:
            raise RuntimeError('failed to load model config "{}"'.format(self.mc_name))
        _PRINT_.info('INFO: Loaded model config "{}"'.format(self.mc_name))
            
        # modify interpolation code
        if self.interpolation_code != -1:
            self.modify_interp_codes(ws, self.interpolation_code,
                                     classes=[ROOT.RooStats.HistFactory.FlexibleInterpVar, ROOT.PiecewiseInterpolation])
        
        # activate binned likelihood
        if self.binned_likelihood:
            self.activate_binned_likelihood(ws)
        
        # set main measurement
        if self.tag_as_measurement:
            self.set_measurement(ws, condition=lambda name: name.startswith(self.tag_as_measurement))
                          
        # deactivate level 2 constant term optimization
            self.deactivate_lv2_const_optimization(ws, 
                condition=lambda name: (name.endswith('_mm') and 'mumu_atlas' in name))

        # load pdf
        pdf = model_config.GetPdf()
        if not pdf:
            raise RuntimeError('Failed to load pdf')
        _PRINT_.info('INFO: Loaded model pdf "{}" from model config'.format(pdf.GetName()))
             
        # load dataset
        data = ws.data(self.data_name)
        if not data:
            raise RuntimeError('Failed to load dataset')
        _PRINT_.info('INFO: Loaded dataset "{}" from workspace'.format(data.GetName()))
                
        # load nuisance parameters
        nuisance_parameters = model_config.GetNuisanceParameters()
        if not nuisance_parameters:
            raise RuntimeError('Failed to load nuisance parameters')
        _PRINT_.info('INFO: Loaded nuisance parameters from model config')
                
        # Load global observables
        global_observables = model_config.GetGlobalObservables()
        if not global_observables:
            raise RuntimeError('Failed to load global observables')          
        _PRINT_.info('INFO: Loaded global observables from model config')                  
    
        # Load POIs
        pois = model_config.GetParametersOfInterest()
        if not pois:
            raise RuntimeError('Failed to load parameters of interest')
        _PRINT_.info('INFO: Loaded parameters of interest from model config')
                                  
        # Load observables
        observables = model_config.GetObservables()
        if not observables:
            raise RuntimeError('Failed to load observables')     
        _PRINT_.info('INFO: Loaded observables from model config')
        
        self._file                = file
        self._workspace           = ws
        self._model_config        = model_config
        self._pdf                 = pdf
        self._data                = data
        self._nuisance_parameters = nuisance_parameters
        self._global_observables  = global_observables
        self._pois                = pois
        self._observables         = observables
                          
        # Load snapshots
        if (self.snapshot_name) and self.workspace.getSnapshot(self.snapshot_name):
            self._workspace.loadSnapshot(self.snapshot_name)
            _PRINT_.info('INFO: Loaded snapshot "{}"'.format(self.snapshot_name))
        return None
                
    @staticmethod
    def _fix_parameters(source:"ROOT.RooArgSet", param_expr=None, param_str='parameter'):
        '''
            source: parameters instance
            param_expr: 
        '''            
        param_dict = ExtendedModel.parse_param_expr(param_expr)
        return ExtendedModel._set_parameters(source, param_dict, mode='fix', param_str=param_str)           
    
    @staticmethod
    def _profile_parameters(source:"ROOT.RooArgSet", param_expr=None, param_str='parameter'):
        '''
            source: parameters instance
            param_expr: 
        '''                          
        param_dict = ExtendedModel.parse_param_expr(param_expr)
        return ExtendedModel._set_parameters(source, param_dict, mode='free', param_str=param_str)   
    
    def fix_parameters(self, param_expr=None):
        return self._fix_parameters(self.workspace.allVars(), param_expr=param_expr,
                                    param_str='parameter')
    
    def profile_parameters(self, param_expr=None):
        profiled_parameters = self._profile_parameters(self.workspace.allVars(), param_expr=param_expr,
                                                       param_str='parameter') 
        if not profiled_parameters:
            _PRINT_.info('Info: No parameters are profiled.')
        return profiled_parameters 
    
    def fix_nuisance_parameters(self, param_expr=None):
        return self._fix_parameters(self.nuisance_parameters, param_expr=param_expr,
                                    param_str='nuisance parameter')
                          
    def fix_parameters_of_interest(self, param_expr=None):
        return self._fix_parameters(self.pois, param_expr=param_expr, param_str='parameter of interest')

    def profile_parameters_of_interest(self, param_expr=None):
        return self._profile_parameters(self.pois, param_expr=param_expr, param_str='parameter of interest')
    
    @staticmethod
    def _set_parameters(source:"ROOT.RooArgSet", param_dict, mode=None, param_str='parameter'):
        set_parameters = []
        available_parameters = [param.GetName() for param in source]
        for name in param_dict:
            selected_params = [param for param in available_parameters if fnmatch.fnmatch(param, name)]
            if not selected_params:
                _PRINT_.warning('WARNING: Parameter "{}" does not exist. No modification will be made.'.format(name))
            for param_name in selected_params:
                ExtendedModel._set_parameter(source[param_name], param_dict[name], mode=mode, param_str=param_str)
                set_parameters.append(source[param_name])

        return set_parameters
    
    @staticmethod
    def _set_parameter(param, value, mode=None, param_str='parameter'):
        name = param.GetName()
        old_value = param.getVal()
        new_value = old_value
        if isinstance(value, (float, int)):
            new_value = value
        elif isinstance(value, (list, tuple)):
            if len(value) == 3:
                new_value = value[0]
                v_min, v_max = value[1], value[2]
            elif len(value) == 2:
                v_min, v_max = value[0], value[1]
            else:
                raise ValueError('invalid expression for profiling parameter: {}'.format(value))
            # set range
            if (v_min is not None) and (v_max is not None):
                if (new_value < v_min) or (new_value > v_max):
                    new_value = (v_min + v_max)/2
                param.setRange(v_min, v_max)
                _PRINT_.info('INFO: Set {} "{}" range to ({},{})'.format(param_str, name, v_min, v_max))
            elif (v_min is not None):
                if (new_value < v_min):
                    new_value = v_min
                # lower bound is zero, if original value is negative, will flip to positive value
                if (v_min == 0) and (old_value < 0):
                    new_value = abs(old_value)
                param.setMin(v_min)
                _PRINT_.info('INFO: Set {} "{}" min value to ({},{})'.format(param_str, name, v_min))
            elif (v_max is not None):
                if (new_value > v_max):
                    new_value = v_max
                # upper bound is zero, if original value is positive, will flip to negative value
                if (v_max == 0) and (old_value > 0):
                    new_value = -abs(old_value)                    
                param.setMax(v_max)
                _PRINT_.info('INFO: Set {} "{}" max value to ({},{})'.format(param_str, name, v_max))
        if new_value != old_value:
            param.setVal(new_value)              
            _PRINT_.info('INFO: Set {} "{}" value to {}'.format(param_str, name, new_value))
        if mode=='fix':
            param.setConstant(1)
            _PRINT_.info('INFO: Fixed {} "{}" at value {}'.format(param_str, name, param.getVal()))
        elif mode=='free':
            param.setConstant(0)
            _PRINT_.info('INFO: "{}" = [{}, {}]'.format(name, param.getMin(), param.getMax()))
        return None

    @staticmethod
    def set_parameter_defaults(source:"ROOT.RooArgSet", value=None, error=None, constant=None,
                               remove_range=None, target:List[str]=None):

        for param in source:
            if (not target) or (param.GetName() in target):
                if remove_range:
                    param.removeRange()            
                if value is not None:
                    param.setVal(value)
                if error is not None:
                    param.setError(error)
                if constant is not None:
                    param.setConstant(constant)
        return None
    
    @staticmethod
    def parse_param_expr(param_expr):
        param_dict = {}
        # if parameter expression is not empty string or None
        if param_expr: 
            if isinstance(param_expr, str):
                param_dict = ExtendedModel.parse_param_str(param_expr)
            elif isinstance(param_expr, dict):
                param_dict = param_dict
            else:
                raise ValueError('invalid format for parameter expression: {}'.format(param_expr))
        elif param_expr is None:
        # if param_expr is None, all parameters will be parsed as None by default
            param_dict = {param.GetName():None for param in source}
        return param_dict

    @staticmethod
    def parse_param_str(param_str):
        '''
        Example: "param_1,param_2=0.5,param_3=-1,param_4=1,param_5=0:100,param_6=:100,param_7=0:"
        '''
        param_str = param_str.replace(' ', '')
        param_list = param_str.split(',')
        param_dict = {}
        for param_expr in param_list:
            expr = param_expr.split('=')
            # case only parameter name is given
            if len(expr) == 1:
                param_dict[expr[0]] = None
            # case both parameter name and value is given
            elif len(expr) == 2:
                param_name = expr[0]
                param_value = expr[1]
                # range like expression
                if ':' in param_value:
                    param_range = param_value.split(':')
                    if len(param_range) != 2:
                        raise ValueError('invalid parameter range: {}'.format(param_value))
                    param_min = float(param_range[0]) if param_range[0].isnumeric() else None
                    param_max = float(param_range[1]) if param_range[1].isnumeric() else None
                    param_dict[param_name] = [param_min, param_max]
                elif is_integer(param_value):
                    param_dict[param_name] = int(param_value)
                else:
                    param_dict[param_name] = float(param_value)
            else:
                raise ValueError('invalid parameter expression: {}'.format(param))
        return param_dict
    
    @staticmethod
    def find_unique_prod_components(root_pdf, components, recursion_count=0):
        if (recursion_count > 50):
            raise RuntimeError('find_unique_prod_components detected infinite loop')
        pdf_list = root_pdf.pdfList()
        if pdf_list.getSize() == 1:
            components.add(pdf_list)
            #print('ProdPdf {} is fundamental'.format(pdf_list.at(0).GetName()))
        else:
            for pdf in pdf_list:
                if pdf.ClassName() != 'RooProdPdf':
                    #print('Pdf {} is no RooProdPdf. Adding it.')
                    components.add(pdf)
                    continue
                find_unique_prod_components(pdf, components, recursion_count+1)
                
    @staticmethod 
    def _unfold_constraints(source:ROOT.RooArgSet, obs:ROOT.RooArgSet, nuis:ROOT.RooArgSet, 
                           result:ROOT.RooArgSet=None, recursion:int=0, threshold:int=50):
        if recursion > threshold:
            raise RuntimeError("failed to find unfold constraints: recusion limit exceeded")
        if result is None:
            result = ROOT.RooArgSet()
        for pdf in source:
            class_name = pdf.ClassName()
            if class_name not in ["RooGaussian", "RooLognormal", "RooGamma", "RooPoisson", "RooBifurGauss"]:
                constraint_set = pdf.getAllConstraints(obs.Clone(), nuis.Clone(), ROOT.kFALSE)
                ExtendedModel._unfold_constraints(constraint_set, obs, nuis, result=result, recursion=recursion+1)
            else:
                result.add(pdf)
        return result
    
    def unfold_constraints(self, threshold:int=50):
        source = self.get_all_constraints()
        return self._unfold_constraints(source, self.observables, self.nuisance_parameters, threshold=threshold)
    
    @staticmethod
    def _pair_constraints(constraint_set:ROOT.RooArgSet, globs:ROOT.RooArgSet, nuis:ROOT.RooArgSet):
        nuis_list = []
        glob_list = []
        pdf_list = []
        for pdf in constraint_set:
            target_np   = None
            target_glob = None
            components = pdf.getComponents()
            components.remove(pdf)
            if components.getSize():
                for c1 in components:
                    for c2 in components:
                        if c1 == c2:
                            continue
                        if c2.dependsOn(c1):
                            components.remove(c1)
                if (components.getSize() > 1):
                    raise RuntimeError("failed to isolate proper nuisance parameter")
                elif (components.getSize() == 1):
                    target_np = components.first()
            else:
                for np in nuis:
                    if pdf.dependsOn(np):
                        target_np = np
                        break
            if not target_np:
                _PRINT_.warning('WARNING: Could not find nuisance parameter for the constrain: {}'.format(pdf.GetName()))
                continue
            for glob in globs:
                if pdf.dependsOn(glob):
                    target_glob = glob
                    break
            if not target_glob:
                _PRINT_.warning('WARNING: Could not find global observable for the constrain: {}'.format(pdf.GetName()))
                continue
            nuis_list.append(target_np)
            glob_list.append(target_glob)
            pdf_list.append(pdf)
        return nuis_list, glob_list, pdf_list
    
    def pair_nuis_and_glob_obs(self):
        constraint_set = self.unfold_constraints()
        nuis_list, glob_list, _ = self._pair_constraints(constraint_set, self.global_observables, self.nuisance_parameters)
        return nuis_list, glob_list

    def pair_constraints(self, to_str=False):
        constraint_set = self.unfold_constraints()
        nuis_list, glob_list, pdf_list = self._pair_constraints(constraint_set, self.global_observables, self.nuisance_parameters)
        if to_str:
            nuis_names = [i.GetName() for i in nuis_list]
            glob_names = [i.GetName() for i in glob_list]
            pdf_names  = [i.GetName() for i in pdf_list]
            size = len(nuis_names)
            return [(pdf_names[i], nuis_names[i], glob_names[i]) for i in range(size)]
        return nuis_list, glob_list, pdf_list 
    
    def get_all_constraints(self):
        all_constraints = ROOT.RooArgSet()
        cache_name = "CACHE_CONSTR_OF_PDF_{}_FOR_OBS_{}".format(self.pdf.GetName(), 
                     ROOT.RooNameSet(self.data.get()).content())                 
        constr = self.workspace.set(cache_name)
        if constr:
            # retrieve constrains from cache     
            all_constraints.add(constr)
        else:
            # load information needed to determine attributes from ModelConfig 
            obs = self.observables.Clone()
            nuis = self.nuisance_parameters.Clone()
            all_constraints = self.pdf.getAllConstraints(obs, nuis, ROOT.kFALSE)
            
        # take care of the case where we have a product of constraint terms
        temp_all_constraints = ROOT.RooArgSet(all_constraints.GetName())
        for constraint in all_constraints:
            if constraint.IsA() == ROOT.RooProdPdf.Class():
                buffer = ROOT.RooArgSet()
                ExtendedModel.find_unique_prod_components(constraint, buffer)
                temp_all_constraints.add(buffer)
            else:
                temp_all_constraints.add(constraint)
        return temp_all_constraints
    
    def inspect_constrained_nuisance_parameter(self, nuis, constraints):
        nuis_name = nuis.GetName()
        _PRINT_.info('INFO: On nuisance parameter {}'.format(nuis_name))
        nuip_nom = 0.0
        prefit_variation = 1.0
        found_constraint = ROOT.kFALSE
        found_gaussian_constraint = ROOT.kFALSE
        constraint_type = None
        for constraint in constraints:
            constr_name = constraint.GetName()
            if constraint.dependsOn(nuis):
                found_constraint = ROOT.kTRUE
                constraint_type = 'unknown'
                # Loop over global observables to match nuisance parameter and
                # global observable in case of a constrained nuisance parameter
                found_global_observable = ROOT.kFALSE
                for glob_obs in self.global_observables:
                    if constraint.dependsOn(glob_obs):
                        found_global_observable = ROOT.kTRUE
                        # find constraint width in case of a Gaussian
                        if constraint.IsA() == ROOT.RooGaussian.Class():
                            found_gaussian_constraint = ROOT.kTRUE
                            constraint_type = 'gaus'
                            old_sigma_value = 1.0
                            found_sigma = ROOT.kFALSE
                            for server in constraint.servers():
                                if (server != glob_obs) and (server != nuis):
                                    old_sigma_value = server.getVal()
                                    found_sigma = ROOT.kTRUE
                            if math.isclose(old_sigma_value, 1.0, abs_tol=0.001):
                                old_sigma_value = 1.0
                            if not found_sigma:
                                _PRINT_.info('INFO: Sigma for pdf {} not found. Uisng 1.0.'.format(constr_name))
                            else:
                                _PRINT_.info('INFO: Uisng {} for sigma of pdf {}'.format(old_sigma_value, constr_name))

                            prefit_variation = old_sigma_value
                        elif constraint.IsA() == ROOT.RooPoisson.Class():
                            constraint_type = 'pois'
                            tau = glob_obs.getVal()
                            _PRINT_.info('INFO: Found tau {} of pdf'.format(constr_name))
                            prefit_variation = 1. / math.sqrt(tau)
                            _PRINT_.info('INFO: Prefit variation is {}'.format(prefit_variation))
                            nuip_nom = 1.0
                            _PRINT_.info("INFO: Assume that {} is nominal value of the nuisance parameter".format(nuip_nom))
        return prefit_variation, constraint_type, nuip_nom
        
    def set_initial_errors(self, source:Optional["ROOT.RooArgSet"]=None):
        if not source:
            source = self.nuisance_parameters
    
        all_constraints = self.get_all_constraints()
        for nuis in source:
            nuis_name = nuis.GetName()
            prefit_variation, constraint_type, _ = self.inspect_constrained_nuisance_parameter(nuis, all_constraints)
            if constraint_type=='gaus':
                _PRINT_.info('INFO: Changing error of {} from {} to {}'.format(nuis_name, nuis.getError(), prefit_variation))
                nuis.setError(prefit_variation)
                nuis.removeRange()    
        return None
    
    def get_poi(self, poi_name:str, strict:bool=False):
        poi = self.workspace.var(poi_name)
        if not poi:
            raise RuntimeError('workspace does not contain the variable "{}"'.format(poi_name))
        if strict and (poi not in list(self.pois)):
            raise RuntimeError('workspace variable "{}" is not part of the POIs'.format(poi_name))
        return poi
    
    def _load_obs_and_weight(self, obs_and_weight:Optional[Union["ROOT.RooArgSet",str]]=None, 
                             weight_var:Optional[Union["ROOT.RooRealVar",str]]=None):
        # get the weight variable
        if weight_var is None:
            weight_name = self._DEFAULT_NAMES_['weight']
            weight_var = self.workspace.var(weight_name)
            if not weight_var:
                weight_var = ROOT.RooRealVar(weight_name, weight_name, 1)
                getattr(self.workspace, "import")(weight_var)
        elif isinstance(weight_var, str):
            weight_var = self.workspace.var(weight_var)
            if not weight_var:
                raise RuntimeError('weight variable "{}" not found in workspace'.format(weight_var))
        elif not isinstance(weight_var, ROOT.RooRealVar):
            raise ValueError('weight variable must be of RooRealVar type')
                
        # get the obs_and_weight arg set
        if obs_and_weight is None:
            default_name = self._DEFAULT_NAMES_['dataset_args']
            obs_and_weight = self.workspace.set(default_name)
            if not obs_and_weight:
                obs_and_weight = ROOT.RooArgSet()
                obs_and_weight.add(self.observables)            
                obs_and_weight.add(weight_var)
                self.workspace.defineSet(default_name, obs_and_weight)
        elif isinstance(obs_and_weight, str):
            obs_and_weight = self.workspace.set(obs_and_weight)
            if not obs_and_weight:
                raise RuntimeError('named set "{}" not found in workspace'.format(obs_and_weight))
        elif not isinstance(obs_and_weight, ROOT.RooArgSet):
            raise ValueError('the argument "obs_and_weight" must be of RooArgSet type')
        return obs_and_weight, weight_var
    
    @staticmethod
    def get_object_map(object_dict:Dict, object_name:str):
        ExtendedModel.load_RooFitObjects()
        if object_name not in ["RooDataSet", "RooAbsPdf"]:
            raise ValueError("unsupported object `{}`".format(object_name))
        object_map = ROOT.std.map(f"string, {object_name}*")()
        object_map.keepalive = list()
        for c, d in object_dict.items():
            object_map.keepalive.append(d)
            object_map.insert(object_map.begin(), ROOT.std.pair(f"const string, {object_name}*")(c, d))
        return object_map
    
    @staticmethod
    def get_dataset_map(dataset_dict:Dict):
        ExtendedModel.load_RooFitObjects()
        dsmap = ROOT.std.map('string, RooDataSet*')()
        dsmap.keepalive = list()
        for c, d in dataset_dict.items():
            dsmap.keepalive.append(d)
            dsmap.insert(dsmap.begin(), ROOT.std.pair("const string, RooDataSet*")(c, d))
        return dsmap
    
    @staticmethod
    def get_pdf_map(pdf_dict:Dict):
        ExtendedModel.load_RooFitObjects()
        pdfmap = ROOT.std.map('string, RooAbsPdf*')()
        pdfmap.keepalive = list()
        for c, d in pdf_dict.items():
            pdfmap.keepalive.append(d)
            pdfmap.insert(pdfmap.begin(), ROOT.std.pair("const string, RooAbsPdf*")(c, d))
        return pdfmap    
    
    def generate_asimov_from_pdf(self, name:str="asimovData", pdf:Optional["ROOT.RooAbsPdf"]=None,
                                 obs_and_weight:Optional[Union["ROOT.RooArgSet",str]]=None, 
                                 weight_var:Optional[Union["ROOT.RooRealVar",str]]=None,
                                 extra_args=None):
        
        pdf = pdf if pdf is not None else self.pdf
        if isinstance(pdf, ROOT.RooSimultaneous):
            raise ValueError("this method should not be called from a simultaneous pdf")
        
        obs_and_weight, weight_var = self._load_obs_and_weight(obs_and_weight, weight_var)
        
        # get the combined arg set for the asimov dataset
        arg_set = ROOT.RooArgSet()
        arg_set.add(obs_and_weight)
        if extra_args is not None:
            if isinstance(extra_args, list):
                for arg in extra_args:
                    arg_set.add(arg)
            else:
                arg_set.add(extra_args)
                
        asimov_data = ROOT.RooDataSet(name, name, arg_set, ROOT.RooFit.WeightVar(weight_var))
        
        # generate observables defined by the pdf associated with this state
        obs = pdf.getObservables(self.observables)        
        target_obs = obs.first()
        expected_events = pdf.expectedEvents(obs)
        #print("INFO: Generating Asimov for pdf {}".format(pdf.GetName()))
        for i in range(target_obs.numBins()):
            target_obs.setBin(i)
            norm = pdf.getVal(obs)*target_obs.getBinWidth(i)
            n_events = norm*expected_events
            if n_events <= 0:
                _PRINT_.warning("WARNING: Detected bin with zero expected events ({})! Please check"
                      "your inputs. Obs = {}, bin = {}".format(n_events, target_obs.GetName(), i))
            elif (n_events > 0) and (n_events < 1e18):
                asimov_data.add(self.observables, n_events)

        if (asimov_data.sumEntries() != asimov_data.sumEntries()):
            raise RuntimeError("asimov data sum entries is nan")
        return asimov_data

    def generate_asimov(self, poi_name:str, poi_val:float, poi_profile:Optional[float]=None,
                        do_conditional:bool=False, do_import:bool=True, dataset:Optional["ROOT.RooDataSet"]=None,
                        minimizer_options:Optional[Dict]=None, nll_options:Optional[Dict]=None,
                        object_names:Optional[Dict]=None):
        # define simplified ws variable names
        ws = self.workspace
        globs = self.global_observables
        nuis  = self.nuisance_parameters
        
        # define names used for various objects
        names = self._DEFAULT_NAMES_
        if object_names is not None:
            names.update(object_names)
        tmp_glob_name = names['temp_globs']
        tmp_nuis_name = names['temp_nuis'] 
        nom_glob_name = names['nominal_globs']
        nom_nuis_name = names['nominal_nuis']
        con_glob_name = names['conditional_globs']
        con_nuis_name = names['conditional_nuis']
        asimov_data_name = names['asimov'].format(mu=poi_val)
        channel_asimov_data_name = names['channel_asimov']
        
        poi = self.get_poi(poi_name)
        if not nuis:
            nuis = ROOT.RooArgSet()
        nuis_list, glob_list = self.pair_nuis_and_glob_obs()

        ws.saveSnapshot(tmp_glob_name, globs)
        ws.saveSnapshot(tmp_nuis_name, nuis)
        if not ws.getSnapshot(nom_glob_name):
            _PRINT_.info('INFO: Saving snapshot "{}"'.format(nom_glob_name))
            ws.saveSnapshot(nom_glob_name, globs)
        if not ws.getSnapshot(nom_nuis_name):
            _PRINT_.info('INFO: Saving snapshot "{}"'.format(nom_nuis_name))
            ws.saveSnapshot(nom_nuis_name, nuis)

        if do_conditional and (poi_profile is not None):
            from quickstats.components import ExtendedMinimizer
            if dataset is None:
                dataset = self.data
            minimizer = ExtendedMinimizer("Minimizer", self.pdf, dataset)
            if minimizer_options is None:
                minimizer_options = minimizer._DEFAULT_MINIMIZER_OPTION_
            if nll_options is None:
                nll_options = minimizer._DEFAULT_NLL_OPTION_
            minimizer.configure(**minimizer_options)
            minimizer.configure_nll(self.nuisance_parameters, self.global_observables,
                                    **nll_options)
            poi.setVal(poi_profile)
            poi.setConstant(1)
            minimizer.minimize()
        poi.setVal(poi_val)
        poi.setConstant(0)

        for np, glob in zip(nuis_list, glob_list):
            glob.setVal(np.getVal())

        if do_conditional and (poi_profile is not None):
            ws.saveSnapshot(con_glob_name.format(mu=poi_profile), globs)
            ws.saveSnapshot(con_nuis_name.format(mu=poi_profile), nuis)
        else:
            ws.saveSnapshot(con_glob_name.format(mu=poi_val), globs)
            ws.saveSnapshot(con_nuis_name.format(mu=poi_val), nuis)
            
        if not do_conditional:
            ws.loadSnapshot(nom_glob_name)
            ws.loadSnapshot(nom_nuis_name)    
        poi.setVal(poi_val)
        
        sim_pdf = self.pdf
        if not isinstance(sim_pdf, ROOT.RooSimultaneous):
            asimov_data = self.generate_asimov_from_pdf(asimov_data_name, sim_pdf)
        else:
            asimov_data_map = {}
            channel_cat = sim_pdf.indexCat()
            n_cat = len(channel_cat)
            for i in range(n_cat):
                channel_cat.setIndex(i)
                label = channel_cat.getLabel()
                pdf_cat = sim_pdf.getPdf(label)
                name = channel_asimov_data_name.format(index=i)
                asimov_data_map[label] = self.generate_asimov_from_pdf(name, pdf_cat, extra_args=channel_cat)

            obs_and_weight, weight_var = self._load_obs_and_weight()
            dataset_map = ExtendedModel.get_dataset_map(asimov_data_map)
            asimov_data = ROOT.RooDataSet(asimov_data_name, asimov_data_name, 
                                          ROOT.RooArgSet(obs_and_weight, channel_cat),
                                          ROOT.RooFit.Index(channel_cat),
                                          ROOT.RooFit.Import(dataset_map),
                                          ROOT.RooFit.WeightVar(weight_var))
        if do_import:
            getattr(ws, "import")(asimov_data)
        ws.loadSnapshot(nom_glob_name)
        return asimov_data
    
    @staticmethod
    def to_dataframe(args):
        import pandas as pd
        data = [{'Name':i.GetName(), 'Value':i.getVal(), "Constant":i.isConstant(), "Min":i.getMin(), "Max":i.getMax()} for i in args]
        df = pd.DataFrame(data)
        return df
    
    @staticmethod
    def load_ws(fname:str, ws_name:Optional[str]=None, mc_name:Optional[str]=None):
        if not os.path.exists(fname):
            raise FileNotFoundError('workspace file {} does not exist'.format(fname))
        file = ROOT.TFile(fname)
        if (not file):
            raise RuntimeError("Something went wrong while loading the root file: {}".format(fname))        
        # load workspace
        if ws_name is None:
            ws_names = [i.GetName() for i in file.GetListOfKeys() if i.GetClassName() == 'RooWorkspace']
            if not ws_names:
                raise RuntimeError("No workspaces found in the root file: {}".format(fname))
            if len(ws_names) > 1:
                _PRINT_.warning("WARNING: Found multiple workspace instances from the root file: {}. Available workspaces"
                      " are \"{}\". Will choose the first one by default".format(fname, ','.join(ws_names)))
            ws_name = ws_names[0]
        ws = file.Get(ws_name)
        if not ws:
            raise RuntimeError('Failed to load workspace: "{}"'.format(ws_name))
        # load model config
        if mc_name is None:
            mc_names = [i.GetName() for i in ws.allGenericObjects() if 'ModelConfig' in i.ClassName()]
            if not mc_names:
                raise RuntimeError("no ModelConfig object found in the workspace: {}".format(ws_name))
            if len(mc_names) > 1:
                _PRINT_.warning("WARNING: Found multiple ModelConfig instances from the workspace: {}. "
                      "Available ModelConfigs are \"{}\". "
                      "Will choose the first one by default".format(ws_name, ','.join(mc_names)))
            mc_name = mc_names[0]     
        mc = ws.obj(mc_name)
        if not mc:
            raise RuntimeError('Failed to load model config "{}"'.format(mc_name))
        return file, ws, mc
    
    @staticmethod
    def get_nuisance_parameter_names(fname:str, ws_name:Optional[str]=None, mc_name:Optional[str]=None):
        ExtendedModel.load_extension()
        file, ws, mc = ExtendedModel.load_ws(fname, ws_name, mc_name)
        nuisance_parameters = mc.GetNuisanceParameters()
        if not nuisance_parameters:
            raise RuntimeError('Failed to load nuisance parameters')
        return [nuis.GetName() for nuis in nuisance_parameters]
    
    @staticmethod
    def get_poi_names(fname:str, ws_name:Optional[str]=None, mc_name:Optional[str]=None):
        ExtendedModel.load_extension()
        file, ws, mc = ExtendedModel.load_ws(fname, ws_name, mc_name)
        pois = mc.GetParametersOfInterest()
        if not pois:
            raise RuntimeError('Failed to load parameters of interest')        
        return [poi.GetName() for poi in pois]

    @staticmethod
    def get_dataset_names(fname:str, ws_name:Optional[str]=None, mc_name:Optional[str]=None):
        ExtendedModel.load_extension()
        file, ws, mc = ExtendedModel.load_ws(fname, ws_name, mc_name)
        datasets = ws.allData()
        if not datasets:
            raise RuntimeError('Failed to load datasets')
        return [dataset.GetName() for dataset in datasets]