import collections
import copy
import flips.util as util
import inspect
import itertools
import numpy as np
import scipy.sparse as sp
import scipy.integrate as integ
from tqdm.notebook import tqdm
from tqdm import tqdm as tqdm_txt

class non_local:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        
class scheme:
    def __init__(self, solver, **kwargs):
        o = util.defaults(kwargs, {'L':1000, 'num_lumps':101, 'lump':10, 'diffusion':1, 'min_burst':1e-14})
        self.solver = solver
        self.crn = solver.crn
        nodes = self.dict_value(o.num_lumps, util.isint, '"num_lumps" should either be a positive integer or a mapping (e.g. dictionary) indexed by every species and with positive integers')
        self.num_cont_nodes = tuple([nodes[s] for s in self.crn.species])
        self.num_nodes = tuple([nodes[s] for s in self.crn.species] + self.crn.discrete_truncs)
        self.nm = np.prod(self.num_nodes)
        if not util.isnumber(o.lump) or o.lump<=0:
            raise Exception('Parameter "lump" should be a positive number, probably greater than 1')
        self.dx = o.lump / o.L
        if not util.isnumber(o.L) or o.L<=0:
            raise Exception('Parameter "L" should be a positive number')
        self.L = o.L
        if not util.isnumber(o.min_burst):
            raise Exception('Parameter "min_burst" should be a number')
        self.min_burst = o.min_burst
        if not util.isnumber(o.diffusion):
            raise Exception('Parameter "diffusion" should be a number')
        self.diffusion = o.diffusion
        
    def dict_value(self, val, istest, msg):
        try:
            if istest(val) and val > 0:
                return {s:val for s in self.crn.species}
            elif (isinstance(val, collections.Mapping) and 
                  len(val) == self.crn.num_species and
                  sorted(val.keys()) == sorted(self.crn.species) and
                  all(map(lambda v:istest(v) and v > 0, val.values()))):
                return val
            else:
                raise Exception()
        except Exception:
            raise Exception(msg)
    
    def isvalidij(self, ij):
        return (ij >= 0).all() and (self.num_nodes > ij).all()
    
    def ij2i(self, ij):
        return np.ravel_multi_index(ij, self.num_nodes)
        
    def i2ij(self, i):
        return np.unravel_index(i, self.num_nodes)
    
    def ij2xarg(self, ij):
        x = {self.crn.species[i]:ij[i]*self.dx for i in range(self.crn.num_species)}
        m = {self.crn.discrete_species[i]:ij[self.crn.num_species+i] for i in range(self.crn.num_discrete_species)}
        return {**x, **m}
        
    def get_zero_initial_conditions(self):
        return np.zeros(self.num_nodes)
    
    def set_initial_conditions(self, ics):
        # allow shortcuts where we will just put all the probability mass in the corner
        if isinstance(ics, str):
            if ics == 'uniform':
                ics = 1
            elif ics == 'zero':
                ics = 0
            elif ics == 'full':
                ics = -1
            
        if util.isint(ics):
            if ics == 0:
                ics = np.zeros(self.num_nodes)
                ics[tuple(np.array(self.num_nodes)*0)] = 1
            elif ics == -1:
                ics = np.zeros(self.num_nodes)
                ics[tuple(np.array(self.num_nodes)-1)] = 1
            elif ics == 1:
                ics = np.ones(self.num_nodes)
            else:
                raise Exception('Unknown default initial condition')
        elif np.array(ics).shape != self.num_nodes:
            raise Exception('Expecting initial conditions array size = continuum species * states (continuum & discrete)')

        ics = np.array(ics)
        ics = self.normalise(ics)
        self.solver.p = ics.reshape((self.nm,))
        self.solver.p_save = [(0, ics)]
        self.solver.T = 0
        
    def normalise(self, ics):
        if ics.shape != self.num_nodes:
            raise Exception('Expecting initial conditions array size = continuum species * states (continuum & discrete)')
        elif ics.min() < 0 or ics.sum() == 0:
            raise Exception('Expecting non-negative initial conditions, not all zero')
        return ics / ics.sum() / (self.L * self.dx)**self.crn.num_species

    def build(self):
        pass
    
    def solve(self, T, t_evals=[], save=100):
        pass

class stepper:
    def __init__(self):
        return
    
    def step(scheme, p, dt):
        pass
    
    def get_stepper(o):
        if o.stepper not in steppers.keys():
            raise Exception('Unknown time stepper. Available options are: ' + ', '.join(steppers.keys()))
        return steppers[o.stepper](o)

class stepper_RK(stepper):
    def __init__(self, o):
        o = util.defaults(o, {'step_order': 2})
        if not (util.isint(o.step_order) and 1 <= o.step_order <= 3):
            raise Exception('RK stepper requires an integer order from 1 to 3')
    
        etas = [[0], # forward Euler
                [0, .5],
                [0, 3/4, 1/3]][o.step_order-1]
        cs = [[1],
              [0, 1],
              [0, 1, 1/2]][o.step_order-1]
        
        self.iters = [(etas[i],cs[i]) for i in range(len(etas))]
        
    def step(self, scheme, p, t, dt):
        p0 = p
        for (eta,c) in self.iters:
            p = eta * p0 + (1-eta) * (p + dt * scheme(p, t + c * dt))
        return p
    
    def CFL(self):
        return 1

# TODO: initiate the multilevel stepper with RK
class stepper_multilevel(stepper):
    def __init__(self, o):
        o = util.defaults(o, {'step_order':2, 'step_level':3})
        ss = [[2,3],[3,5]]
        if not (util.isint(o.step_order) and 2 <= o.step_order <= 3):
            raise Exception('Multilevel stepper requires an integer "step_order" from 1 to 3')
        if not (util.isint(o.step_level) and ss[o.step_order-2][0] <= o.step_level <= ss[o.step_order-2][1]):
            raise Exception('Multilevel stepper of order {} requires an integer "step_level" from {} to {}'.format(o.step_order,ss[o.step_order-2][0],ss[o.step_order-2][1]))
            
        s = o.step_level - 2
        offsets = [2,3]
        self.eta = [[3/4, 8/9],
                    [16/27, 25/32, 108/125]][o.step_order-2][s-offsets[o.step_order-2]]
        self.cs = [[(2,0), (3/2,0)],
                    [(3,12/11), (2,10/7), (5/3,30/17)]][o.step_order-2][s-offsets[o.step_order-2]]
        self.ps = collections.deque(maxlen = s+1)
        self.s = s
        self.cfl = min([c for c in self.cs if c>0])
        
    def step(self, scheme, p, t, dt):
        p0 = p
        Cp0 = scheme(p, t)
        # on the first step, fill the queue
        for i in range(self.s+1 - len(self.ps) + 1):
            self.ps.append((p0, Cp0))
        ps, Cps = self.ps[0]
        return self.eta * (p0 + self.cs[0] * dt * Cp0) + (1-self.eta) * (ps + self.cs[1] * dt * Cps)
    
    def CFL(self):
        return self.cfl
            
steppers = {'RK':stepper_RK, 'multilevel':stepper_multilevel}
        
class explicit(scheme):
    
    def __init__(self, solver, **kwargs):
        super().__init__(solver, **kwargs)
        self.init(**kwargs)
        self.build()
        
    def init(self, **kwargs):
        o = util.defaults(kwargs, {'dt':None, 'min_dt':1e-12, 'stepper':'RK', 'step_order':1, 'step_frac':0.5})
        
        self.stepper = stepper.get_stepper(o)
        
        self.dt = o.dt
        if o.dt is not None:
            if not util.isnumber(o.dt) or o.dt <= 0:
                raise Exception('Time step "dt" must be a positive number')
        else:
            if not util.isnumber(o.step_frac) or o.step_frac <= 0:
                raise Exception('Parameter "step_frac" should be a number, probably in (0,1]')
            self.step_frac = o.step_frac
            if not util.isnumber(o.min_dt) or o.min_dt < 0:
                raise Exception('Parameter "min_dt" should be a non-negative number')
            self.min_dt = o.min_dt
                        
    def build(self):
        self.solver.write(1, 'Building the time-independent part of the scheme')
        self.inv2L = self.diffusion / (2 * self.L)
        self.ijprod = [el for el in itertools.product(*[range(n) for n in self.num_cont_nodes])]
        
        t, t_updates, self.reactions, self.reactions_semi_t, self.reactions_t, self.bursts, self.bursts_semi_t, self.bursts_t = self.separate_time_bursts(self.crn.reactions)
        discrete_t, discrete_t_updates, self.discrete_reactions, self.discrete_reactions_semi_t, self.discrete_reactions_t, _, _, _ = self.separate_time_bursts(self.crn.discrete_reactions)
        self.t = t or discrete_t
        self.t_updates = list(set(t_updates + discrete_t_updates))
        self.t_updates.sort()
        
        self.build_iterable()
        
    def separate_time_bursts(self, rctns):
        # separate the time-dependent rates from the independent and semi-independent (piecewise constant) ones
        # so we only calculate the static ones once, and the semi-independent ones only at the known switching points
        # and the bursts, so we can process them all quickly
        rctns_t = copy.deepcopy(rctns)
        rctns_semi_t = copy.deepcopy(rctns)
        rctns_bursts = copy.deepcopy(rctns)
        rctns_bursts_t = copy.deepcopy(rctns)
        rctns_bursts_semi_t = copy.deepcopy(rctns)
        t = False # is there any time-dependence
        t_updates = []
        def set_zero(lsts,i,j):
            for lst in lsts:
                lst[i].set_rate(j, 0)
        for i in range(len(rctns)):
            for j in self.crn.discrete_states_prod:
                rate = rctns[i].get_rate(j)
                if isinstance(rate, non_local):
                    set_zero([rctns,rctns_t,rctns_semi_t],i,j)
                    # if the rate or burst size is zero, then remove the reaction altogether
                    if rate.a == 0 or rate.b == 0:
                        set_zero([rctns_bursts,rctns_bursts_semi_t,rctns_bursts_t],i,j)
                    # either both bursting rates and sizes are time-independent
                    elif hasattr(rate.a, 't') and rate.a.t == False and hasattr(rate.b, 't') and rate.b.t == False:
                        set_zero([rctns_bursts_t,rctns_bursts_semi_t],i,j)
                    # or they're both time-semi-dependent
                    elif hasattr(rate.a, 't') and util.islistts(rate.a.t) and hasattr(rate.b, 't') and util.islistts(rate.b.t):
                        t_updates += rate.a.t + rate.b.t
                        set_zero([rctns_bursts,rctns_bursts_t],i,j)
                    # otherwise the reaction is considered time-dependent
                    else:
                        t = True
                        set_zero([rctns_bursts,rctns_bursts_semi_t],i,j)
                else:
                    set_zero([rctns_bursts,rctns_bursts_semi_t,rctns_bursts_t],i,j)
                    if rate == 0:
                        set_zero([rctns,rctns_t,rctns_semi_t],i,j)
                    elif hasattr(rate, 't') and rate.t == False:
                        set_zero([rctns_semi_t,rctns_t],i,j)
                    elif hasattr(rate, 't') and util.islistts(rate.t):
                        t_updates += rate.t
                        set_zero([rctns,rctns_t],i,j)
                    else:
                        t = True
                        set_zero([rctns,rctns_semi_t],i,j)
        return t, t_updates, rctns, rctns_semi_t, rctns_t, rctns_bursts, rctns_bursts_semi_t, rctns_bursts_t
    
    def build_scheme_part(self, scheme, reactions, add_fn, t):
        for rctn in reactions:
            e = rctn.get_disp()
            norm_e = np.linalg.norm(e)
            for m in self.crn.discrete_states_prod:
                rate = rctn.get_rate(m)
                if rate == 0:
                    continue
                for ij_ in self.ijprod:
                    ij = ij_ + m
                    i = self.ij2i(ij)
                    add_fn(scheme, rate, ij, i, e, norm_e, self.dx, t)

    def add_reaction(self, scheme, rate, ij, i, e, norm_e, dx, t):
        ratex = rate(self.ij2xarg(ij), self.L, t)
        # phi_(j+e) if it's in the domain
        ije = ij + e
        if self.isvalidij(ije):
            scheme[i,self.ij2i(ije)] += self.inv2L / dx * rate(self.ij2xarg(ije), self.L, t) / dx
            scheme[i,i] += - (1 + self.inv2L / dx) * ratex / dx
        # phi_j if it's in the domain (includes terms of j-e)
        ije = ij - e
        if self.isvalidij(ije):
            scheme[i,self.ij2i(ije)] += (1 + self.inv2L / dx) * rate(self.ij2xarg(ije), self.L, t) / dx
            scheme[i,i] += - self.inv2L / dx * ratex / dx

    def add_nonlocal(self, scheme, rate, ij, i, e, norm_e, dx, t):
        rate.add(self, scheme, rate, ij, i, e, norm_e, dx, t)
        
    def add_burst(self, scheme, rate, ij, i, e, norm_e, dx, t):
        arg = self.ij2xarg(ij)
        ratea = rate.a(arg, self.L, t)
        b = rate.b(arg, self.L, t) / self.L # from the evaluation below, we need to assure that b>1
        
        ratexk = ratea * b * (1-np.exp(-norm_e*dx / b))**2 / (norm_e*dx)
        prod = np.exp(-norm_e*dx / b)
        # number of jumps that can be made staying within the domain
        domain = int(np.floor(min([(self.num_nodes[ii]-1 - ij[ii]) / e[ii] for ii in e.nonzero()[0]])))
        # no need to add entries to the sparsity matrix when the coefficients are too small
        # so guarantee that: ratexk*prod**(k-1) > min_burst
        min_burst = int(np.ceil(1 + np.log(self.min_burst/ratexk) / np.log(prod)))
        ije = ij
        for k in range(1,min(domain, min_burst)):
            ije += e
            scheme[i,i] += -ratexk
            scheme[self.ij2i(ije),i] += ratexk
            ratexk *= prod

    def add_fragment(self, scheme, rate, ij, i, e, norm_e, dx, t):
        arg = self.ij2xarg(ij)
        a = rate.a(arg, self.L, t)
        C = rate.b(arg, self.L, t) # cumulative probability of finding a single daughter of certain size
        ii = ij[e.nonzero()[0][0]] # assumes e is one-dimensional
        for k in range(1,ii+1):
            jj = ii-k
            p = integ.quad(lambda x:C((jj+.5) / (ii-.5+x))-C(max([0, (jj-.5) / (ii-.5+x)])),0,1)[0]
            if p > self.min_burst:
                scheme[i,i] += -a*p
                scheme[self.ij2i(ij-k*e),i] += 2*a*p # there are two daughters

    def add_fragment_delta(self, scheme, rate, ij, i, e, norm_e, dx, t):
        arg = self.ij2xarg(ij)
        a = rate.a(arg, self.L, t)
        c = rate.b(arg, self.L, t) # fraction of smallest size
        ii = ij[e.nonzero()[0][0]] # assumes e is one-dimensional
        for k in range(1,ii+1):
            jj = ii-k-1
            p = min([1, max([0, (jj+.5)/c - ii+.5])]) - min([1, max([0, (jj-.5)/c - ii+.5])])
            if p > self.min_burst:
                scheme[i,i] += -a*p
                scheme[self.ij2i(ij-k*e),i] += 2*a*p # there are two daughters
            
    def add_discrete(self, scheme, rate, ij, i, e, norm_e, dx, t):
        ratex = rate(self.ij2xarg(ij), self.L, t)
        # for the discrete reactions, we have to impose both the + and the -, but we have already checked validity
        scheme[i,i] += -ratex
        scheme[self.ij2i(ij+e),i] += ratex
        
    # if save is a number, then it saves that number of points equispaced on the time interval [0,T]
    # in addition to any t_evals
    # if save is a list of times, then it saves at those times (in addition to t_evals)
    def solve(self, T, t_evals=[], save=100, bar='tqdm', leave=False):
        if not hasattr(self.solver, 'p'):
            raise Exception('Must set initial conditions before running simulation')
            
        if util.isnumber(T):
            Tnum = T
            Tfn = lambda p,t: t>=T
        else:
            Tnum = np.inf
            if not callable(T) or len(inspect.signature(T).parameters) != 2:
                raise Exception('Terminal event should be a function taking parameters p,t')
            Tfn = T
        
        save_list = util.islistts(save, lo=self.solver.T, hi=Tnum)
        if not (util.isint(save) and save >= 2 or save_list):
            raise Exception(f'Parameter "save" should be a positive integer >= 2 (representing the number of frames to save), or a list of times on the interval [t,T] where t is the time solved to (t={self.solver.T} in this case)')
        if not util.islistts(t_evals, lo=self.solver.T, hi=Tnum):
            raise Exception(f'Parameter "t_evals" should be an iterable of numbers in the interval [t,T] where t is the time solved to (t={self.solver.T:.3e} in this case). Be careful of floating point imprecision: check that the smallest and largest values really are within the interval.')
        
        if Tnum == np.inf and not save_list:
            raise Exception('When using an event as a terminal condition, you must pass a list of times at which the solution will be saved (for all the times before the event occurs)')
        
        if bar:
            bars = {'tqdm':tqdm, 'console':tqdm_txt}
            if not bar in bars.keys():
                raise Exception('Parameter "bar_type" unrecognised, options are None or the strings ' + ', '.join([f'"{k}"' for k in bars.keys()]))
            bar = bars[bar]
        
        t_updates = [t for t in self.t_updates if self.solver.T < t <= Tnum]
        
        t_saves = list(t_evals) + [Tnum]
        t_saves += list(save) if save_list else np.linspace(self.solver.T, Tnum, save).tolist()[1:]
        t_saves = list(set(t_saves))
        t_saves.sort()
        if t_saves[0] == self.solver.T:
            t_saves = t_saves[1:]
            
        self.t_evals = list(set(t_updates + t_saves))
        self.t_evals.sort()
        self.t_evals_i = 0
        self.t_updates_b = [t in t_updates for t in self.t_evals]
        self.t_saves_b = [t in t_saves for t in self.t_evals]
        
        # automatic on the first run, but necessary if the user does solve(t) and then solve(t+something)
        self.solver.p = self.solver.p.reshape((self.nm,1))
        
        if bar:pbar = bar(total=Tnum-self.solver.T if Tnum<np.inf else 0, unit='sim. time unit', leave=leave, bar_format='{l_bar}{bar} {n:.3f}/{total:.3f} [{elapsed}<{remaining} {rate_fmt}{postfix}]')
        to_terminate = Tfn(self.solver.p.reshape(self.num_nodes), self.solver.T)
        while not to_terminate:
            newT, dt, to_save, to_update = self.time_step(self.get_max_dt(self.solver.T))
            
            if bar:pbar.update(dt)
            # renewal bcs
            # self.solver.p = self.solver.p.multiply(non_bcs_mask) + integral_bcs in the bcs_mask form
            self.solver.p = self.stepper.step(self.scheme, self.solver.p, self.solver.T, dt)
            self.solver.T = newT
            
            to_terminate = Tfn(self.solver.p.reshape(self.num_nodes), self.solver.T)
            if to_update:
                self.scheme_update(self.solver.T)
            if to_save or to_terminate:
                self.solver.p_save += [(self.solver.T, self.solver.p.reshape(self.num_nodes))]
        if bar:
            pbar.n = pbar.total # needed because poor design with floating point updates https://github.com/tqdm/tqdm/issues/849
            pbar.close()
        
        self.solver.p = self.solver.p.reshape(self.num_nodes)
    
    def time_step(self, max_dt):
        if self.dt is not None:
            dt = self.dt
        else:
            dt = self.step_frac * max_dt
            if dt < self.min_dt:
                raise Exception('Calculated time step lower than "min_dt" threshold')
        if self.solver.T + dt >= self.t_evals[self.t_evals_i]:
            dt = self.t_evals[self.t_evals_i] - self.solver.T
            newT = self.t_evals[self.t_evals_i] # exact, not adding the dt, so that equality testing works
            to_save = self.t_saves_b[self.t_evals_i]
            to_update = self.t_updates_b[self.t_evals_i]
            self.t_evals_i += 1
        else:
            newT = self.solver.T + dt
            to_update = to_save = False
        return newT, dt, to_save, to_update
    
    def diagnostic_monotonic(self, scheme):
        if scheme.min() < 0:
            self.solver.write(1, 'Warning: base_scheme not monotonic')
            self.solver.write(2, 'monotonicity: scheme.min() = {:.3e}, #elements < 0 = {}       (should both be zero)'.format(scheme.min(), (scheme<0).sum()))
            self.solver.write(3, scheme)
    
    def diagnostic_conservative(self, scheme):
        ones = np.matrix([1] * self.nm)
        res = ones * scheme - ones
        if np.linalg.norm(res) > 1e-9:
            self.solver.write(1, 'Warning: scheme not conservative')
            self.solver.write(2, 'conservation: |1^T scheme - 1^T| = {:.3e}, #elements > 1e-10 = {}       (should both be zero)'.format(np.linalg.norm(res), (np.abs(res)>1e-10).sum()))
            self.solver.write(3, res)
    
class explicit_first_order(explicit):
    
    def __init__(self, solver, **kwargs):
        super().__init__(solver, **kwargs)
        
    def build_iterable(self):
        self.base_scheme = self.build_scheme(sp.lil_matrix((self.nm,) * 2), self.reactions, self.discrete_reactions, self.bursts).tocsr()
        
        if self.t:
            if self.dt is not None:
                self.solver.write(1, 'Given dt = {:.3e}'.format(self.dt))
            self.base_scheme_diag = self.base_scheme.diagonal()

            self.scheme = lambda p,t: (self.base_scheme + self.t_scheme(t)) * p
            self.get_max_dt = lambda t: -1 / (self.base_scheme_diag + self.t_scheme(t).diagonal()).min()
        else:
            self.base_max_dt = -1 / self.base_scheme.diagonal().min()
            if self.dt is None:
                # split the construction into two parts and use the first part to calculate the diagonal components
                # so that we can determine the maximum timestep to remain montonic
                self.dt = self.step_frac * self.base_max_dt
                self.solver.write(1, 'Calculated dt = {:.3e}'.format(self.dt))
            else:
                self.solver.write(1, 'Calculated max_dt = {:.3e}, using user-given dt = {:.3e}'.format(self.base_max_dt, self.dt))
            self.scheme = lambda p,_: self.base_scheme * p
            self.get_max_dt = lambda t: 0
        
        self.diagnostics()

    def t_scheme(self, t):
        return self.build_scheme(sp.lil_matrix((self.nm,) * 2), self.reactions_t, self.discrete_reactions_t, self.bursts_t, t)
                
    def build_scheme(self, scheme, reactions, discrete_reactions, burst_reactions, t=0):
        self.build_scheme_part(scheme, reactions, self.add_reaction, t)
        self.build_scheme_part(scheme, discrete_reactions, self.add_discrete, t)
        self.build_scheme_part(scheme, burst_reactions, self.add_nonlocal, t)
        return scheme
    
    def diagnostics(self, t=0, p=None):
        if self.t:
            dt = self.get_max_dt(t)
            scheme = self.base_scheme + self.build_scheme(sp.lil_matrix((self.nm,) * 2), self.reactions_t, self.discrete_reactions_t, self.bursts_t, t) * dt
        else:
            scheme = self.base_scheme
        
        self.solver.write(1, 'scheme.nnz = {} = n^{:.2f} = ({:.2f})n       (for n = {})'.format(scheme.nnz, np.log(scheme.nnz)/np.log(self.nm), scheme.nnz/self.nm, self.nm))
                
        self.diagnostic_monotonic(scheme)
        self.diagnostic_conservative(scheme)
    
class explicit_LUD(explicit_first_order):
    
    def __init__(self, solver, **kwargs):
        super().__init__(solver, **kwargs)

    def add_reaction(self, scheme, rate, ij, i, e, norm_e, dx, t):
        ratex = rate(self.ij2xarg(ij), self.L, t)
        # phi_(j+e) if it's in the domain
        if self.isvalidij(ij + 2*e):
            scheme[i,self.ij2i(ij + 2*e)] += (.5) * rate(self.ij2xarg(ij + 2*e), self.L, t) / dx
            scheme[i,self.ij2i(ij + e)] += (-1.5 + self.inv2L / dx) * rate(self.ij2xarg(ij + e), self.L, t) / dx
            scheme[i,i] += - (self.inv2L / dx) * ratex / dx
        # phi_j if it's in the domain (includes terms of j-e)
        if self.isvalidij(ij - e) and self.isvalidij(ij + e):
            scheme[i,self.ij2i(ij + e)] += (-.5) * rate(self.ij2xarg(ij + e), self.L, t) / dx
            scheme[i,i] += (1.5 - self.inv2L / dx) * ratex / dx
            scheme[i,self.ij2i(ij - e)] += (self.inv2L / dx) * rate(self.ij2xarg(ij - e), self.L, t) / dx
                
class explicit_third_order(explicit_first_order):
    
    def __init__(self, solver, **kwargs):
        super().__init__(solver, **kwargs)

    def add_reaction(self, scheme, rate, ij, i, e, norm_e, dx, t):
        ratex = rate(self.ij2xarg(ij), self.L, t)
        # phi_(j+e) if it's in the domain
        if self.isvalidij(ij + 2*e):
            scheme[i,self.ij2i(ij + 2*e)] += (1/6) * rate(self.ij2xarg(ij + 2*e), self.L, t) / dx
            scheme[i,self.ij2i(ij + e)] += (-5/6 + self.inv2L / dx) * rate(self.ij2xarg(ij + e), self.L, t) / dx
            scheme[i,i] += - (2/6 + self.inv2L / dx) * ratex / dx            
        # phi_j if it's in the domain (includes terms of j-2e)        
        if self.isvalidij(ij - e) and self.isvalidij(ij + e):
            scheme[i,self.ij2i(ij + e)] += (-1/6) * rate(self.ij2xarg(ij + e), self.L, t) / dx
            scheme[i,self.ij2i(ij - e)] += (2/6 + self.inv2L / dx) * rate(self.ij2xarg(ij - e), self.L, t) / dx
            scheme[i,i] += (5/6 - self.inv2L / dx) * ratex / dx

class explicit_KT(explicit):
    
    def __init__(self, solver, **kwargs):
        super().__init__(solver, **kwargs)
        
    def init(self, **kwargs):
        super().init(**kwargs)
        
        o = util.defaults(kwargs, {'theta':1})
        if not util.isnumber(o.theta):
            raise Exception('The KT scheme requires a number parameter "theta", probably in [1,2]')
        self.theta = o.theta
    
    def scheme_update(self, t):
        semi_scheme, semi_flux_bases = self.build_frame(self.reactions_semi_t, self.discrete_reactions_semi_t, self.bursts_semi_t, t)
        self.base_scheme = self.static_base_scheme + semi_scheme
        self.flux_bases = self.static_flux_bases + semi_flux_bases
        
        # This is slightly stronger than what's in the paper because we don't actually need the union bound
        # dt <= 1/(||h + (sum_i r_i)/(Omega dx^2)|| + 4|I| max_i ||r_i||/dx)
        # where norms ||.|| are over space, and the rates are all for the current time
        ris = [f[2].diagonal() for f in self.flux_bases]
        max_norm_ri = np.max([np.abs(r).max() for r in ris]) if len(ris)>0 else 0
        I = len(self.crn.reactions)
        h = self.base_scheme.diagonal()
        sum_ris = np.sum(ris, axis=0)

        self.max_dt = 1/(np.max(np.abs(h + sum_ris*self.diffusion/(self.L*self.dx**2))) + 4*I*max_norm_ri/self.dx) / self.stepper.CFL()
        
    def build_iterable(self):
        self.static_base_scheme, self.static_flux_bases = self.build_frame(self.reactions, self.discrete_reactions, self.bursts, 0)
        self.scheme_update(0)
        
        if self.t:
            def time_scheme(p, t):
                t_scheme, t_flux_bases = self.build_frame(self.reactions_t, self.discrete_reactions_t, self.bursts_t, t)
                return (self.base_scheme + t_scheme) * p + np.sum([self.fluxes(f,p) for f in self.flux_bases + t_flux_bases], 0)
            self.scheme = time_scheme
            cfl = self.stepper.CFL()
            self.get_max_dt = lambda t: self.dx / (np.sum([f[2] for f in self.flux_bases + self.build_frame(self.reactions_t, self.discrete_reactions_t, self.bursts_t, t)[1]], 0)).max() / 8 / cfl
        else:
            def static_scheme(p, t):
                return self.base_scheme * p + np.sum([self.fluxes(f,p) for f in self.flux_bases], 0)
            self.scheme = static_scheme
            self.get_max_dt = lambda t: self.max_dt
            
    def minmod_(self, a, b):
        return np.multiply(((np.sign(a)+np.sign(b))/2).astype(int), np.minimum(np.abs(a), np.abs(b)))

    def minmod(self, a, b, theta):
        return self.minmod_(self.minmod_(theta * a, theta * b), (a+b)/2)
    
    def fluxes(self, f, p):
        shift_m, d_p, rates, diff, de = f
        dp = d_p * p
        dp = self.minmod(dp, shift_m * dp, self.theta)
#        dp_p = shift_p * dp
#        p_p2 = shift_p * (p - dp_p / 2)
        p_m2 = p + dp / 2
#        fs = rates * (p_p2 + p_m2)
#        a = rates
#        H_p2 = fs / 2 - a / 2 * (p_p2 - p_m2)
        H_p2 = rates * p_m2
        P_p2 = diff * p
        return - (H_p2 - shift_m * H_p2) / de + (P_p2 - shift_m * P_p2) / de
    
    def build_frame(self, reactions, discrete_reactions, bursts, t=0):
        scheme = sp.lil_matrix((self.nm,) * 2)
        self.build_scheme_part(scheme, discrete_reactions, self.add_discrete, t)
        self.build_scheme_part(scheme, bursts, self.add_nonlocal, t)
        scheme = scheme.tocsr()
                
        flux_bases = []
        for rctn in reactions:
            shift_m = sp.lil_matrix((self.nm,) * 2)
            d_p = sp.lil_matrix((self.nm,) * 2)
            rates = sp.lil_matrix((self.nm,) * 2)
            diff_flux = sp.lil_matrix((self.nm,) * 2)
            self.build_scheme_part(shift_m, [rctn], self.add_shift_m, t)
            self.build_scheme_part(d_p, [rctn], self.add_d_p_trunc, t)
            self.build_scheme_part(rates, [rctn], self.add_rates, t)
            self.build_scheme_part(diff_flux, [rctn], self.add_diff_flux, t)
            
            flux_bases += [[b.tocsr() for b in [shift_m, d_p, rates, diff_flux]] +
                            [np.linalg.norm(rctn.get_disp())*self.dx]]
        
        return scheme, flux_bases
    
    # an alternative way to evaluate the (u_x) terms at the boundary
    def add_d_p_trunc(self, scheme, rate, ij, i, e, norm_e, dx, t):
        if self.isvalidij(ij + e):
            scheme[i,self.ij2i(ij + e)] += 1
            scheme[i,i] += -1
            
    def add_d_p(self, scheme, rate, ij, i, e, norm_e, dx, t):
        if self.isvalidij(ij + e):
            scheme[i,self.ij2i(ij + e)] += 1
        scheme[i,i] += -1
            
    def add_shift_m(self, scheme, rate, ij, i, e, norm_e, dx, t):
        if self.isvalidij(ij - e):
            scheme[i,self.ij2i(ij - e)] += 1
            
    def add_rates(self, scheme, rate, ij, i, e, norm_e, dx, t):
        if self.isvalidij(ij + e):
            x1 = self.ij2xarg(ij)
            x2 = self.ij2xarg(ij + e)
            x = {k:(x1[k]+x2[k])/2 for k in x1.keys()}
            scheme[i,i] += rate(x, self.L, t)
        
    def add_diff_flux(self, scheme, rate, ij, i, e, norm_e, dx, t):
        if self.isvalidij(ij + e):
            scheme[i,self.ij2i(ij + e)] += self.inv2L * rate(self.ij2xarg(ij + e), self.L, t) / dx
            scheme[i,i] += - self.inv2L * rate(self.ij2xarg(ij), self.L, t) / dx
    
    def diagnostics(self, t=0, p=None):
        if p is None:
            p = self.normalise(np.array([[np.random.rand() for r in range(self.nm)]]).transpose())[:,0]
            
        scheme = self.base_scheme + np.sum([self.fluxes(f, p) for f in self.flux_bases], 0)
                
        self.diagnostic_conservative(scheme)