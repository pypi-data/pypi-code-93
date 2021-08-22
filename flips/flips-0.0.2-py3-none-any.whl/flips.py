from ipywidgets import widgets, interactive
import itertools
import matplotlib.pyplot as plt
import numpy as np
import pickle
import flips.util as util
import flips.rctn as rct
import flips.scheme as scm

class solver:
    
    methods = {'first order':scm.explicit_first_order,
               'LUD':scm.explicit_LUD,
               'third order':scm.explicit_third_order,
               'KT':scm.explicit_KT}
    
    def __init__(self, reactions=[], discrete_truncs={}, discrete_reactions=[], verbose=0, scheme='KT', **kwargs):
        self.verbose = verbose
        self.crn = rct.crn(reactions, discrete_truncs, discrete_reactions)
        self.write(1, 'Parsed reactions. Discovered continuum species: ' + ', '.join(self.crn.species) +
                       ', and ' + ('no ' if len(self.crn.discrete_species)==0 else '') + 'discrete species' + (': ' + ', '.join(self.crn.discrete_species) if len(self.crn.discrete_species)>0 else ''))
        
        if scheme not in self.methods.keys():
            raise Exception('Unknown solver, available solvers are: ' + ', '.join(self.methods.keys()))
        self.scheme = self.methods[scheme](self, **kwargs)

    def get_zero_initial_conditions(self):
        return self.scheme.get_zero_initial_conditions()
    
    def set_initial_conditions(self, *args):
        self.scheme.set_initial_conditions(*args)
        
    def solve(self, *args, **kwargs):
        self.scheme.solve(*args, **kwargs)
        
    #############################################################################################################
    ###############################      Returning the results     ##############################################
    #############################################################################################################
    
    def get_species(self):
        return self.crn.species + self.crn.discrete_species
    
    def S2ij(self, S):
        species = self.crn.species + self.crn.discrete_species
        for s in species:
            if s not in S:
                raise Exception(f'The argument S must be a dictionary with an index for each species {species}, \'{s}\' is currently missing')
        return tuple([S[k] for k in species])
    
    def get_prob_dens(self, i, S):
        return self.p_save[i][1][self.S2ij(S)]
    
    def get_saved_times(self):
        return [v[0] for v in self.p_save]
    
    def set_ics_value(self, ics, S, v):
        ics[self.S2ij(S)] = v
    
    def get_p(self, margins, state):
        return self.format_p((self.T, self.p), margins, state)
        
    def format_p(self, frame, margins, states):
        t,p = frame
        # take the marginals by summing the other indices
        if len(margins) == 1:
            i = self.s2i(margins[0])
            n = self.scheme.num_nodes[i]
            Xs = np.linspace(0, n*self.scheme.dx*self.scheme.L, n)
            pp = self.moment(p, margins, states, 0)
        elif len(margins) == 2:
            i = [self.s2i(margins[0]), self.s2i(margins[1])]
            n = [self.scheme.num_nodes[i[0]], self.scheme.num_nodes[i[1]]]
            Xs = np.meshgrid(np.linspace(0, n[0]*self.scheme.dx*self.scheme.L, n[0]),
                             np.linspace(0, n[1]*self.scheme.dx*self.scheme.L, n[1]))
            pp = np.zeros(np.flip(n)) # flip because meshgrid has matrix-like access, so y-axis first, then x-axis
            inds = [range(nn) for nn in self.scheme.num_cont_nodes] + states
            for k in itertools.product(*[range(nn) for nn in n]):
                inds[i[0]] = [k[0]]
                inds[i[1]] = [k[1]]
                pp[tuple(np.flip(k))] = sum([p[ind] for ind in itertools.product(*inds)])
            pp *= (self.scheme.L*self.scheme.dx)**(self.crn.num_species-2)
        return t, Xs, pp
    
    def moment(self, p, margins, states, order):
        i = self.s2i(margins[0])
        n = self.scheme.num_nodes[i]
        Xs = np.linspace(0, n*self.scheme.dx*self.scheme.L, n)
        pp = np.zeros(n)
        inds = [range(n) for n in self.scheme.num_cont_nodes] + states
        for k in range(n):
            inds[i] = [k]
            pp[k] = Xs[k]**order * sum([p[ind] for ind in itertools.product(*inds)])
        return pp * (self.scheme.L*self.scheme.dx)**(self.crn.num_species-1)
    
    def get_mean(self, margins, state):
        ts = [p[0] for p in self.p_save]
        ps = [sum(self.moment(p[1], margins, state, 1)) for p in self.p_save]
        return ts, ps
    
    def get_sigma(self, margins, state):
        ts = [p[0] for p in self.p_save]
        ps = [np.sqrt(sum(self.moment(p[1], margins, state, 2)) - sum(self.moment(p[1], margins, state, 1))**2) for p in self.p_save]
        return ts, ps
    
    def parse_margins(self, margins):
        if isinstance(margins, str):
            margins = [margins]

        if margins is None:
            margins = self.crn.species

        if self.crn.num_species == 1:
            if margins != self.crn.species:
                raise Exception('Marginal unknown')
            margins = self.crn.species
        elif self.crn.num_species == 2:
            if margins == []:
                margins = self.crn.species
            elif any([m not in self.crn.species for m in margins]):
                raise Exception('Marginal unknown')
        elif len(margins) > 2 or any([m not in self.crn.species for m in margins]):
            raise Exception('No more than two marginals from among the continuum species')
        return margins
    
    def parse_state(self, state):
        if not(state is None or tuple(state) in self.crn.discrete_states_prod):
            raise Exception('The state must be an iterable with each entry in the range from 0 to the number of states-1, or to marginalise over all states, pass None')
        return [[s] for s in list(state)] if state is not None else [range(n) for n in self.crn.discrete_truncs]
    
    def s2i(self, s):
        return self.crn.species.index(s)
        
    def plott(self, p, title, margins, state, ylim):
        plt.title(title + '$(' + margins[0] + ')$' + self.state_str(state))
        plt.xlabel('$t$')
        plt.plot(p[0], p[1])
        
    def plot1D(self, p, margins, state, ylim, marker, normalise):
        plt.title('$t$ = {:.3f}'.format(p[0]) + self.state_str(state))
        plt.xlabel(margins[0])
        if ylim is not None:
            if util.isnumber(ylim):
                plt.ylim(top=ylim)
            else:
                plt.ylim(bottom=ylim[0], top=ylim[1])
        plt.ylabel('$P(' + margins[0] + ')$', rotation=0, labelpad=20)
        p2 = p[2] if not normalise else p[2] / np.sum(p[2]) / self.scheme.dx / self.scheme.L
        plt.plot(p[1], p2, marker=marker)
        
    def plot2D(self, p, margins, state, ylim, marker, normalise):
        plt.title('$t$ = {:.3f}'.format(p[0]) + self.state_str(state))
        plt.xlabel(margins[0])
        plt.ylabel(margins[1], rotation=0)
        ylim = ylim if ylim is not None else p[2].max()
        plot = plt.contourf(p[1][0], p[1][1], p[2], np.linspace(0, ylim, 10), cmap='Blues')
        nm = plot.legend_elements()[0]
        lbl = ['$[{:.2e}, {:.2e}]$'.format(plot.levels[i], plot.levels[i+1]) for i in range(len(plot.levels)-1)]
        plt.legend(nm, lbl, bbox_to_anchor=(1, 1.05), loc='upper left')
    
    def state_str(self, state):
        return ', disc. st. = ' + str(tuple([s[0] for s in state])) if np.prod([len(s) for s in state]) < np.prod(self.crn.discrete_truncs) else ', (all states)' if self.crn.num_discrete_species > 0 else ''
        
    def plot_p(self, margins=None, state=None, ylim=None, marker=None, normalise=False):
        self.check_solved()
        margins, state = self.parse_margins(margins), self.parse_state(state)
        [self.plot1D,self.plot2D][len(margins)-1](self.get_p(margins, state), margins, state, ylim, marker, normalise)

    def time_plot_p(self, margins=None, state=None, ylim=None, marker=None, normalise=False, hook=lambda i:None):
        self.check_solved()
        margins, state = self.parse_margins(margins), self.parse_state(state)
        # cache the frames so that they aren't calculated each time
        pp = [self.format_p(self.p_save[i], margins, state) for i in range(len(self.p_save))]
        fn = lambda i:[self.plot1D,self.plot2D][len(margins)-1](pp[i], margins, state, ylim, marker, normalise)
        return interactive(lambda i:(fn(i),hook(i)), i=widgets.IntSlider(min=0, max=len(self.p_save)-1, value=0))
    
    def plot_mean(self, margins=None, state=None, ylim=None):
        self.check_solved()
        margins, state = self.parse_margins(margins), self.parse_state(state)
        if len(margins) != 1:
            raise Exception('Mean can only be plotted for one species')
        self.plott(self.get_mean(margins, state), 'mean', margins, state, ylim)
    
    def plot_sigma(self, margins=None, state=None, ylim=None):
        self.check_solved()
        margins, state = self.parse_margins(margins), self.parse_state(state)
        if len(margins) != 1:
            raise Exception('Variance can only be plotted for one species')
        self.plott(self.get_sigma(margins, state), '$\sigma$', margins, state, ylim)
    
    def check_solved(self):
        if not hasattr(self, 'T'):
            raise Exception('Initial conditions need to be set and the solve method called for useful output')
    
    def write(self, level, msg):
        if self.verbose >= level:
            print(msg)
            
    def set_write_level(self, v):
        self.verbose = v
        
    # save final frame
    def save_frame(self, fname):
        self.saver(fname, self.p)
        
    # save all frames
    def save(self, fname):
        self.saver(fname, self.p_save)
        
    def saver(self, fname, data):
        f = open(fname+'.dat', 'wb')
        pickle.dump(data, f)
        f.close()
            
    def load(fname):
        f = open(fname+'.dat', 'rb')
        p = pickle.load(f)
        f.close()
        return p
        
class burst(scm.non_local):
    def __init__(self, a, b):
        super().__init__(a,b)
        self.add = scm.explicit.add_burst
        
class fragment(scm.non_local):
    def __init__(self, a, C):
        super().__init__(a,C)
        self.add = scm.explicit.add_fragment
        
class fragment_delta(scm.non_local):
    def __init__(self, a, c):
        super().__init__(a,c)
        self.add = scm.explicit.add_fragment_delta
        
def static_rate(fn):
    fn.t = False
    return fn
    
def Hill(spec,n=1,K=1,coeff=1,shift=0):
    if n > 0:
        Hill_rate = lambda S,L,t: shift + coeff * (S[spec]/K)**n / (1 + (S[spec]/K)**n)
    else:
        n = -n
        Hill_rate = lambda S,L,t: shift + coeff / (1 + (K * S[spec])**n)
    Hill_rate.t = False
    return Hill_rate

def MichaelisMenten(spec,vmax,km):
    return Hill(spec,n=1,coeff=vmax,k=km)