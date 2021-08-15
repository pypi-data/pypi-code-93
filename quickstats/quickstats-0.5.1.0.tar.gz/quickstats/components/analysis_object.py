from typing import Optional, Union

from quickstats.components import ExtendedModel, ExtendedMinimizer
import ROOT

class AnalysisObject(object):
    def __init__(self, filename:Optional[str]=None, data_name:str='combData', binned_likelihood:bool=True,
                 fix_param:str='', profile_param:str='', ws_name:Optional[str]=None, 
                 mc_name:Optional[str]=None, snapshot_name:Optional[str]=None,
                 minimizer_type:str='Minuit2', minimizer_algo:str='Migrad', precision:float=0.001, 
                 eps:float=1.0, strategy:int=0, print_level:int=1, timer:bool=True,
                 num_cpu:int=1, offset:bool=True, optimize:int=2, eigen:bool=False,
                 fix_cache:bool=True, fix_multi:bool=True, max_calls:int=-1, 
                 max_iters:int=-1, constrain_nuis:bool=True, **kwargs):
        
        self.model = None
        self.minimizer = None
        
        if filename is not None:
            self.setup_model(filename, data_name, binned_likelihood, ws_name, mc_name, 
                             snapshot_name, fix_cache, fix_multi)
            self.setup_parameters(fix_param, profile_param)
            self.setup_minimizer(minimizer_type, minimizer_algo, precision, eps, strategy, num_cpu,
                                 offset, optimize, eigen, max_calls, max_iters, print_level,
                                 timer, constrain_nuis)
        
    def setup_model(self, filename, data_name='combData', binned_likelihood:bool=True, 
                    ws_name:Optional[str]=None, mc_name:Optional[str]=None, 
                    snapshot_name:Optional[str]=None, fix_cache:bool=True, fix_multi:bool=True):
        
        model = ExtendedModel(fname=filename, ws_name=ws_name, mc_name=mc_name, data_name=data_name, 
                              snapshot_name=snapshot_name, binned_likelihood=binned_likelihood,
                              fix_cache=fix_cache, fix_multi=fix_multi)
        self.model = model
    
    def setup_parameters(self, fix_param:str='', profile_param:str=''):
        if not self.model:
            raise RuntimeError('uninitialized analysis object')
        if fix_param:
            self.model.fix_parameters(fix_param)
        if profile_param:
            self.model.profile_parameters(profile_param)
            
    def setup_minimizer(self, minimizer_type:str='Minuit2', minimizer_algo:str='Migrad', 
                        precision:float=0.001, eps:float=1.0, strategy:int=0, 
                        num_cpu:int=1, offset:bool=True, optimize:bool=True, eigen:bool=False,
                        max_calls:int=-1, max_iters:int=-1, print_level:int=-1, timer:bool=True,
                        constrain_nuis:bool=True):
        
        minimizer = ExtendedMinimizer("minimizer", self.model.pdf, self.model.data)
        
        nll_commands = [ROOT.RooFit.NumCPU(num_cpu, 3), 
                        ROOT.RooFit.Offset(offset)]
        if (constrain_nuis and self.model.nuisance_parameters):
            nll_commands.append(ROOT.RooFit.Constrain(self.model.nuisance_parameters))
            nll_commands.append(ROOT.RooFit.GlobalObservables(self.model.global_observables))
            nll_commands.append(ROOT.RooFit.ConditionalObservables(self.model.model_config.GetConditionalObservables()))
            #nll_commands.append(ROOT.RooFit.ExternalConstraints(ROOT.RooArgSet()))
        
        minimize_options = {
            'minimizer_type'   : minimizer_type,
            'minimizer_algo'   : minimizer_algo,
            'default_strategy' : strategy,
            'opt_const'        : optimize,
            'precision'        : precision,
            'eps'              : eps,
            'eigen'            : eigen,
            'max_calls'        : max_calls,
            'max_iters'        : max_iters,
            'print_level'      : print_level,
            'timer'            : timer
        }

        minimizer.configure(nll_commands=nll_commands, **minimize_options)
        
        self.minimizer = minimizer