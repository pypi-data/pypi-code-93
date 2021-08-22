import collections
import functools
import inspect
import itertools
import math
import numpy as np
import warnings
import flips
import flips.util as util
import flips.scheme as scm
    
class reaction:
    
    def __init__(self, reactants, products, species, discrete_species, discrete_prod):
        self.reactants = reactants
        self.products = products
        self.rates = {state:0 for state in discrete_prod}
        self.e = np.array([self.get_product(s)-self.get_reactant(s) for s in species + discrete_species])
    
    def get_disp(self):
        return self.e
        
    def get_reactant(self, s):
        return self.reactants[s] if s in self.reactants else 0
    
    def get_reactants(self):
        return self.reactants.keys()
    
    def get_num_reactants(self):
        return sum(list(self.reactants.values()))
    
    def get_product(self, s):
        return self.products[s] if s in self.products else 0
    
    def get_type(self):
        return self.type
    
    def get_rate(self, state):
        return self.rates[state]
    
    def set_rate(self, state, rate):
        self.rates[state] = rate
        
class crn:
    
    def __init__(self, reactions, discrete_truncs, discrete_reactions):
        self.species = self.parse_species_prs(reactions)
    #        for r in reactions:
    #            if sum(list(r[0].values())) >= 3:
    #                raise Exception('Trimolecular reaction (or higher) negligible')
        self.discrete_species = self.parse_species_prs(discrete_reactions, False)
        self.species = [s for s in self.species if s not in self.discrete_species]
        self.num_species = len(self.species)
        self.num_discrete_species = len(self.discrete_species)
        
        if not isinstance(discrete_truncs, collections.Mapping) or any([not util.isint(s) or s<=0 for s in discrete_truncs.values()]):
            raise Exception('Parameter "discrete_truncs" should be a dictionary indexed by discrete species and with positive integer values describing each maximum discrete state value')
        trunc_species = list(discrete_truncs.keys())
        trunc_species.sort()
        if trunc_species != self.discrete_species:
            raise Exception('Not all discrete species detected have prescribed truncations')            
        self.discrete_truncs = [discrete_truncs[k] for k in self.discrete_species]
        
        self.discrete_states_prod = [el for el in itertools.product(*[range(n) for n in self.discrete_truncs])]
        
        self.reactions = [reaction(r[0], r[1], self.species, self.discrete_species, self.discrete_states_prod) for r in reactions]
        self.discrete_reactions = [reaction(r[0], r[1], self.species, self.discrete_species, self.discrete_states_prod) for r in discrete_reactions]
        
        #if len(self.species) == 0:
        #    raise Exception('No continnuum species found')

        for rctn in self.reactions:
            if sum([abs(rctn.get_product(s)-rctn.get_reactant(s)) for s in self.species]) == 0:
                raise Exception('Degenerate continuum reaction found, please remove')
            if sum([abs(rctn.get_product(s)-rctn.get_reactant(s)) for s in self.discrete_species]) > 0:
                raise Exception('Discrete species must not be created/destroyed in the continuum reactions')
        for rctn in self.discrete_reactions:
            if sum([abs(rctn.get_product(s)-rctn.get_reactant(s)) for s in self.discrete_species]) == 0:
                raise Exception('Degenerate discrete reaction found, please remove')
            if sum([abs(rctn.get_product(s)-rctn.get_reactant(s)) for s in self.species]) > 0:
                raise Exception('Continuum species must not be created/destroyed in the discrete reactions')

        self.clean_rates(self.reactions, [r[2] for r in reactions])
        self.clean_rates(self.discrete_reactions, [r[2] for r in discrete_reactions], allow_bursts=False, ma_continuum=False)
        # remove rates that transition beyond the discrete state space [0,max-1]
        for r in self.discrete_reactions:
            for i in range(self.num_discrete_species):
                diff = r.get_product(self.discrete_species[i]) - r.get_reactant(self.discrete_species[i])
                i_states = range(self.discrete_truncs[i] - diff, self.discrete_truncs[i]) if diff > 0 else range(-diff)
                for state in itertools.product(*[range(self.discrete_truncs[j]) if j != i else i_states for j in range(self.num_discrete_species)]):
                    r.set_rate(state, 0)
        
    def parse_species_prs(self, rctns, continuum=True):
        species = set()
        for rctn in rctns:
            self.test_rctn(rctn, continuum)
            for i in range(2):
                species |= set(rctn[i].keys())
        species = list(species)
        species.sort()
        return species
    
    def test_rctn(self, rctn, continuum=True):
        if len(rctn) != 3:
            raise Exception('Each reaction should be of length 3: [reactants, products, reaction rate]')
        for i in range(2):
            if not isinstance(rctn[i], collections.Mapping):
                raise Exception('Reactants and products should be passed as (possibly empty) dictionaries')
            for s,v in rctn[i].items():
                if not isinstance(s, str) or len(s)==0:
                    raise Exception('Each species (dictionary index) must be a nonempty string')
                if not util.isint(v) or v<0:
                    raise Exception('Each species quantity (dictionary value) must be a positive integer')
        if continuum and functools.reduce(math.gcd, list(rctn[0].values())+list(rctn[1].values())) > 1:
            warnings.warn('A reaction with a GCD (of reactants and products) larger than one has been detected. This is probably better modelled in the continuum by dividing the reactants and products by the GCD (and using an appropriate rate function).')
    
    def dstate2dict(self, j):
        return {s:j[i] for i,s in enumerate(self.discrete_species)}
        
    def clean_rates(self, rctns_p, rates, allow_bursts=True, ma_continuum=True):
        for i in range(len(rctns_p)):
            self.test_rate(rates[i], allow_bursts)
            
            call = (callable(rates[i]) and len(inspect.signature(rates[i]).parameters) == 1)
            rates[i] = {j:rates[i](self.dstate2dict(j)) if call else rates[i] for j in self.discrete_states_prod}
            for j in self.discrete_states_prod:
                rate = rates[i][j]
                if rctns_p[i].get_num_reactants() > 0 and isinstance(rate, flips.burst):
                    raise Exception('Bursts can only occur with no reactants')
                if isinstance(rate, scm.non_local) and not isinstance(rate, flips.burst):
                    if rctns_p[i].get_num_reactants() != 1 or rctns_p[i].get_product(list(rctns_p[i].get_reactants())[0]) != 2:
                        raise Exception('Fragmentation must be denoted by a reaction of the form [{"species":1}, {"species":2}, flips.fragment(...)]')
                rctns_p[i].set_rate(j, self.wrap_rate(rctns_p[i], rate, ma_continuum))
    
    def test_rate(self, rate, allow_bursts=True):
        if callable(rate) and len(inspect.signature(rate).parameters) == 1:
            for j in self.discrete_states_prod:
                self.test_rate_inner(rate(self.dstate2dict(j)), allow_bursts)
        else:
            self.test_rate_inner(rate, allow_bursts)
            
    def test_rate_inner(self, rate, allow_bursts=True):
        allow_negative_rr = True
        if util.isnumber(rate):
            if rate < 0 and not allow_negative_rr:
                raise Exception('Scalar reaction rate should be non-negative')
        # do not allow nesting burst instances as rates
        elif isinstance(rate, scm.non_local) and allow_bursts:
            self.test_rate_inner(rate.a, False)
            if not isinstance(rate, flips.fragment):
                self.test_rate_inner(rate.b, False)
            else:
                self.test_cumulative(rate.b)
        elif callable(rate):
            try:
                test_species = {s:0 for s in self.species+self.discrete_species}
                test_size = 1000
                test_t = 0
                r = rate(test_species, test_size, test_t)
                assert(util.isnumber(r) and (r >= 0 or allow_negative_rr))
            except Exception:
                raise Exception('Callable reaction rate threw an exception or a returned something other than a non-negative number')
        else:
            raise Exception('Reaction rate should be a positive number or a callable (e.g. flips.Hill(...), lambda S,L,t:...)')
    
    def test_cumulative(self, rate, nest=True):
        if callable(rate) and len(inspect.signature(rate).parameters) == 3: # state/time dependent cumulative density, test for one set of inputs
            if nest:
                try:
                    test_species = {**{s:1 for s in self.species}, **{s:0 for s in self.discrete_species}}
                    test_size = 1000
                    test_t = 0
                    r = rate(test_species, test_size, test_t)
                    self.test_cumulative(r, False)
                except Exception:
                    raise Exception('Cumulative density function threw an exception')
            else:
                raise Exception('Cumulative density expected')
        if not callable(rate):
            raise Exception('Cumulative density is expected to be a callable function on the domain [0,1]')
        rs = [rate(x) for x in np.linspace(0,1,20)]
        if not (rs[0] == 0 and rs[-1] == 1 and all([0<=r<=1 for r in rs]) and all([d >= 0 for d in np.diff(rs)])):
            raise Exception('Cumulative density function expected as second parameter of fragmentation operator, that is a function f satisfying f(0) = 0, f(1) = 1, and f is non-decreasing')
        
    def wrap_rate(self, rctn_p, rate, ma_continuum=True, ma_default=True):
        if util.isnumber(rate):
            return 0 if rate == 0 else self.mass_action(rctn_p, rate, ma_continuum) if ma_default else self.constant_rate(rate)
        elif isinstance(rate, scm.non_local):
            return 0 if rate.a == 0 or rate.b == 0 else rate.__class__(self.wrap_rate(rctn_p, rate.a, ma_default=False), self.wrap_rate(rctn_p, rate.b, ma_default=False))
        elif callable(rate) and len(inspect.signature(rate).parameters) == 1: # fragment cumulative density
            rate_fn = lambda S,L,t:rate
            rate_fn.t = False
            return rate_fn
        else:
            return rate
    
    def constant_rate(self, rate):
        def rate_fn(S,L,t):
            return rate
        rate_fn.t = False
        return rate_fn
    
    def mass_action(self, rctn_p, rate, continuum=True):
        def mass_action_fn(S, L, t):
            # analytically, we expect the reaction rates to transform from discrete to continuous cases with
            # a factor of 1/L as follows:
            # 0 --a--> X becomes a/L
            # X --aX--> 0 becomes aX/L
            # X --aX--> Y becomes aX/L = ax
            # 2X --aX(X-1)/2L--> Z becomes aX(X-1)/2L^2 = ax(x-1/L)/2
            # X + Y --aXY/L--> Z becomes axy
            if not continuum: L = 1
            ma_rate = rate if sum([rctn_p.get_reactant(s) for s in rctn_p.get_reactants() if s in self.species]) > 0 else rate/L
            for rctnt in rctn_p.get_reactants():
                k = rctn_p.get_reactant(rctnt)
                # for discrete species in continuum reactions, there is no characteristic size to divide by
                localL = L if rctnt in self.species else 1
                ma_rate *= np.prod([S[rctnt]-i/localL for i in range(k)]) / math.factorial(k)
            return ma_rate
        mass_action_fn.t = False
        return mass_action_fn