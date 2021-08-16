
import sys
import operator
import math
import random

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

import subprocess
import time
from logzero import logger
import logzero

EVALUATED_INF = 99999999
LOGFILE = f"./experiment_{int(time.time())}.log" 
log = logzero.setup_logger(logfile=LOGFILE, level=50, fileLoglevel=10)
print("See log at", LOGFILE)
log.level = 10
# log_format = '%(message)s'
# formatter = logzero.LogFormatter(fmt=log_format)
# logzero.setup_default_logger(formatter=formatter)

# logzero.logfile(f"./experiment_{int(time.time())}.log")

BIN="/home/grandrew/sandbox/hyperc/venv_hcinstalled/lib/python3.8/site-packages/downward_ch/builds/release/bin/downward"
STD_PAR="--loglevel debug --internal-plan-file out.plan"

EVALUATORS="--evaluator 'hff=ff()' --evaluator 'hlm=lmcount(lm_rhw(reasonable_orders=true),pref=true,transform=no_transform())'"

TIMEOUT = 60
SASFILE = "./output.sas"

class SmallInt:
    pass

class Search:
    pass

class ExitList:
    pass # TODO: is it needed?

class Evaluator:
    pass

class OpenList:
    pass

class Preferred:
    pass

class Pruning:
    pass

class AtomSelectionStrategy:
    pass

def eager(OL, reopen_closed, preferred, pruning):
    f"eager({OL}, reopen_closed={reopen_closed}, preferred={preferred}, pruning={pruning}, cost_type=NORMAL, bound=infinity, max_time=infinity, verbosity=normal)"
# These are equivalent to above:
# def eager_greedy2(H1, H2, preferred, boost, pruning):
    # f"eager_greedy([{H1}, {H2}]], preferred={preferred}, boost={boost}, pruning={pruning}, cost_type=NORMAL, bound=infinity, max_time=infinity, verbosity=normal)"
# def eager_greedy3(H1, H2, H3, preferred, boost, pruning):
    # f"eager_greedy([{H1}, {H2}, {H3}]], preferred={preferred}, boost={boost}, pruning={pruning}, cost_type=NORMAL, bound=infinity, max_time=infinity, verbosity=normal)"
def ehc(H1):
    return f"ehc({H1}, preferred_usage=PRUNE_BY_PREFERRED, preferred=[], cost_type=NORMAL, bound=infinity, max_time=infinity, verbosity=normal)"

def lazy(OL, preferred: Preferred, randomize_successors: bool, preferred_successors_first: bool):
    return f"lazy({OL}, preferred={preferred}, reopen_closed=false, randomize_successors={randomize_successors}, preferred_successors_first={preferred_successors_first}, bound=infinity)"

def pruning_null():
    return f"null()"

def pruning_atom_centric_stubborn_sets(use_sibling_shortcut: bool, atom_selection_strategy: AtomSelectionStrategy, min_required_pruning_ratio: float, expansions_before_checking_pruning_ratio: int):
    return f"atom_centric_stubborn_sets(use_sibling_shortcut={use_sibling_shortcut}, atom_selection_strategy={atom_selection_strategy}, min_required_pruning_ratio={min_required_pruning_ratio}, expansions_before_checking_pruning_ratio={expansions_before_checking_pruning_ratio})"

def pruning_stubborn_sets_ec(min_required_pruning_ratio: float, expansions_before_checking_pruning_ratio: int):
    return f"stubborn_sets_ec(min_required_pruning_ratio={min_required_pruning_ratio}, expansions_before_checking_pruning_ratio={expansions_before_checking_pruning_ratio})"

def pruning_stubborn_sets_simple(min_required_pruning_ratio: float, expansions_before_checking_pruning_ratio: int):
    return f"stubborn_sets_simple(min_required_pruning_ratio={min_required_pruning_ratio}, expansions_before_checking_pruning_ratio={expansions_before_checking_pruning_ratio})"

def preferred0():
    return f"[]"
def preferred1(H1):
    return f"[{H1}]"
def preferred2(H1, H2):
    return f"[{H1}, {H2}]"

def tiebreaking2(H1, H2, pref_only, unsafe_pruning):
    return f"tiebreaking([{H1}, {H2}], pref_only={pref_only}, unsafe_pruning={unsafe_pruning})"
def tiebreaking3(H1, H2, H3, pref_only, unsafe_pruning):
    return f"tiebreaking([{H1}, {H2}, {H3}], pref_only={pref_only}, unsafe_pruning={unsafe_pruning})"
def pareto2(H1, H2, pref_only, state_uniform_selection):
    return f"pareto([{H1}, {H2}], pref_only={pref_only}, state_uniform_selection={state_uniform_selection}, random_seed=-1)"
def pareto3(H1, H2, H3, pref_only, state_uniform_selection):
    return f"pareto([{H1}, {H2}, {H3}], pref_only={pref_only}, state_uniform_selection={state_uniform_selection}, random_seed=-1)"

def alt2(H1, H2, boost: int):
    ol = [H1, H2]
    ol = [x for x in ol if x is not None]
    sol = ", ".join(ol)
    return f"alt([{sol}], boost={boost})"
def alt3(H1, H2, H3, boost: int):
    ol = [H1, H2, H3]
    ol = [x for x in ol if x is not None]
    sol = ", ".join(ol)
    return f"alt([{sol}], boost={boost})"
def alt4(H1, H2, H3, H4, boost: int):
    ol = [H1, H2, H3, H4]
    ol = [x for x in ol if x is not None]
    sol = ", ".join(ol)
    return f"alt([{sol}], boost={boost})"
def alt5(H1, H2, H3, H4, H5, boost: int):
    ol = [H1, H2, H3, H4, H5]
    ol = [x for x in ol if x is not None]
    sol = ", ".join(ol)
    return f"alt([{sol}], boost={boost})"

def type_based_2(H1, H2):
    return f"type_based([{H1}, {H2}])"
def type_based_3(H1, H2, H3):
    return f"type_based([{H1}, {H2}, {H3}])"

def epsilon_greedy(H1, pref_only, epsilon):
    return f"epsion_greedy({H1}, pref_only={str(pref_only).lower()}, epsilon={str(epsilon)[:3]})"

def single(H1: Evaluator, pref_only: bool):
    return f"single({H1}, pref_only={str(pref_only).lower()})"

def sum2(H1, H2):
    return f"sum([{H1}, {H2}])"
def sum3(H1, H2, H3):
    return f"sum([{H1}, {H2}, {H3}])"

def weight(H1, w: int):
    if type(w) == bool:
        w = 1
    return f"weight({H1}, {w})"

def max2(H1, H2):
    return f"max({H1}, {H2})"
def max3(H1, H2, H3):
    return f"max({H1}, {H2}, {H3})"

def small_weight(H1, w: SmallInt):
    if type(w) == bool:
        w = 1
    return f"weight({H1}, {w})"

def const_b(val):
    return f"const(value={val})"
def const_sm(val):
    return f"const(value={val})"

def g():
    return "g()"

def hff():
    return "hff"

def hlm():
    return "hlm"

def hadd():
    return "add()"

def hcea():
    return "cea()"

def hcg():
    return "cg()"

def hblind():
    return "blind(transform=no_transform(), cache_estimates=true)"

def goalcount():
    return "goalcount(transform=no_transform(), cache_estimates=true)"

def hm(m: int):
    return f"hm(m={m}, transform=no_transform(), cache_estimates=true)"

def hmax():
    return "hmax(transform=no_transform(), cache_estimates=true)"

def lmcut():
    return "lmcut(transform=no_transform(), cache_estimates=true)"

def true():
    return "true"
def false():
    return "false"

class BigInt:
    pass

class Bool(object):
    pass


class NumberPrimitive:
    def __init__(self, name, val):
        self.__name__ = name
        self.val = val
    def __call__(self):
        return self.val

# print(type_based_2(weight(g(), 2), sum2(g(), hff())))
# sys.exit()

# Define new functions
def protectedDiv(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1
# , preferred: Preferred, randomize_successors: bool, preferred_successors_first: bool 
# pset = gp.PrimitiveSetTyped("MAIN", [Preferred, bool, bool], float)
# TODO: use search engine as input parameter for search too
# pset = gp.PrimitiveSetTyped("MAIN", [], OpenList)
pset = gp.PrimitiveSetTyped("MAIN", [], Search)
pset.addPrimitive(lazy, [ExitList, Preferred, Bool, Bool], Search)
# pset.addPrimitive(ehc, [Evaluator], Search)
# pset.addPrimitive(eager, [OpenList, Bool, Preferred, Pruning], Search)
pset.addPrimitive(preferred0, [], Preferred)
# pset.addPrimitive(preferred1, [Evaluator], Preferred)
# pset.addPrimitive(preferred2, [Evaluator, Evaluator], Preferred)
pset.addPrimitive(alt2, [OpenList, OpenList, int], ExitList)
pset.addPrimitive(alt3, [OpenList, OpenList, OpenList, int], ExitList)
pset.addPrimitive(alt4, [OpenList, OpenList, OpenList, OpenList, int], ExitList)
pset.addPrimitive(alt5, [OpenList, OpenList, OpenList, OpenList, OpenList, int], ExitList)
pset.addPrimitive(pareto2, [Evaluator, Evaluator, Bool, Bool], OpenList)
pset.addPrimitive(pareto3, [Evaluator, Evaluator, Evaluator, Bool, Bool], OpenList)
pset.addPrimitive(tiebreaking2, [Evaluator, Evaluator, Bool, Bool], OpenList)
pset.addPrimitive(tiebreaking3, [Evaluator, Evaluator, Evaluator, Bool, Bool], OpenList)
pset.addPrimitive(type_based_2, [Evaluator, Evaluator], OpenList)
pset.addPrimitive(type_based_3, [Evaluator, Evaluator, Evaluator], OpenList)
pset.addPrimitive(epsilon_greedy, [Evaluator, Bool, float], OpenList)
pset.addPrimitive(single, [Evaluator, Bool], OpenList)
pset.addPrimitive(sum2, [Evaluator, Evaluator], Evaluator)
pset.addPrimitive(sum3, [Evaluator, Evaluator, Evaluator], Evaluator)
pset.addPrimitive(weight, [Evaluator, int], Evaluator)
pset.addPrimitive(small_weight, [Evaluator, SmallInt], Evaluator)
pset.addPrimitive(g, [], Evaluator)
pset.addPrimitive(hadd, [], Evaluator)
pset.addPrimitive(hcea, [], Evaluator)
pset.addPrimitive(hadd, [], Evaluator)
pset.addPrimitive(hcg, [], Evaluator)
pset.addPrimitive(hff, [], Evaluator)
pset.addPrimitive(hlm, [], Evaluator)
pset.addPrimitive(hblind, [], Evaluator)
pset.addPrimitive(goalcount, [], Evaluator)
# pset.addPrimitive(hm, [SmallInt], Evaluator)
pset.addPrimitive(hmax, [], Evaluator)
pset.addPrimitive(lmcut, [], Evaluator)
pset.addPrimitive(const_b, [int], Evaluator)
pset.addPrimitive(const_sm, [SmallInt], Evaluator)
pset.addPrimitive(true, [], Bool)
pset.addPrimitive(false, [], Bool)
# Pruning
pset.addPrimitive(pruning_null, [], Pruning)
pset.addPrimitive(pruning_atom_centric_stubborn_sets, [Bool, AtomSelectionStrategy, float, int], Pruning)
pset.addPrimitive(pruning_stubborn_sets_ec, [float, int], Pruning)
pset.addPrimitive(pruning_stubborn_sets_simple, [float, int], Pruning)
pset.addTerminal("null()", Pruning)
# AtomSelectionStrategy
pset.addTerminal("fast_downward", AtomSelectionStrategy)
pset.addTerminal("quick_skip", AtomSelectionStrategy)
pset.addTerminal("static_small", AtomSelectionStrategy)
pset.addTerminal("dynamic_small", AtomSelectionStrategy)
pset.addPrimitive(NumberPrimitive("p_fast_downward", "fast_downward"), [], AtomSelectionStrategy)
pset.addPrimitive(NumberPrimitive("p_quick_skip", "quick_skip"), [], AtomSelectionStrategy)
pset.addPrimitive(NumberPrimitive("p_static_small", "static_small"), [], AtomSelectionStrategy)
pset.addPrimitive(NumberPrimitive("p_dynamic_small", "dynamic_small"), [], AtomSelectionStrategy)


pset.addTerminal("", ExitList)
pset.addTerminal("", Search)
pset.addTerminal("[]", Preferred)
pset.addTerminal("[hlm,hff]", Preferred)
pset.addTerminal("[hlm]", Preferred)
pset.addTerminal("[hff]", Preferred)
pset.addTerminal("[cg]", Preferred)
pset.addTerminal("[cg,hff]", Preferred)
pset.addTerminal("[add]", Preferred)
pset.addTerminal(None, OpenList)
pset.addTerminal(True, Bool)
pset.addTerminal(False, Bool)
pset.addTerminal("hff", Evaluator)
pset.addTerminal("hlm", Evaluator)
for i in range(8):
    pset.addTerminal(float(f"0.{i}"), float)
    floatX = NumberPrimitive(f"float0_{i}", float(f"0.{i}"))
    pset.addPrimitive(floatX, [], float)
for i in range(1, 100):
    intX = NumberPrimitive(f"int{i}", i*100)
    pset.addPrimitive(intX, [], int)
    if i > 1 and i < 20:
        pset.addTerminal(i, SmallInt)
        smallintX = NumberPrimitive(f"smallint{i}", i)
        pset.addPrimitive(smallintX, [], SmallInt)

pset.addEphemeralConstant("rand_5000", lambda: random.randint(0, 1000), int)
# pset.addEphemeralConstant("rand_01_08", lambda: random.uniform(0.1,0.8), float)

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=12)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)

#################################
# # done = False
# # while not done:
# #     try:
# #         expr = gp.genHalfAndHalf(pset, min_=1, max_=5)
# #         #expr = gp.genFull(pset, min_=1, max_=5)
# #     except IndexError:
# #         done = True
# #         # continue
# expr = gp.genFull(pset, min_=1, max_=5, type_=Search)
# # expr = gp.genHalfAndHalf(pset, min_=1, max_=5)
# tree = gp.PrimitiveTree(expr)
# # print(str(tree))
# func = toolbox.compile(expr=tree)
# print(func)
# sys.exit()
#################################

def evalSymbReg(individual, points):
    # Transform the tree expression in a callable function
    # print(individual)
    func = toolbox.compile(expr=individual)
    search_config_length = len(str(func))
    runscript = f'timeout {TIMEOUT} {BIN} {STD_PAR} {EVALUATORS} --search "{func}" < {SASFILE}'
    # print(runscript)
    start_time = time.time()
    proc = subprocess.run(runscript, shell=True, bufsize=1, universal_newlines=True, start_new_session=True, capture_output=True)
    # print(proc.stdout)
    evaluated_states = EVALUATED_INF 
    l_stdout = proc.stdout.split("\n")
    search_log_length = len(l_stdout)
    search_g_length = len([l for l in l_stdout if "g=" in l])
    search_plan = [int(l.strip().split()[2]) for l in l_stdout if "step(s)" in l]
    search_plan_len = 0
    if search_plan:
        search_plan_len = max(search_plan)
    if proc.returncode == 0: 
        for l in l_stdout:
            if "Evaluated" in l:
                evaluated_states_out = int(l.split()[1])
                if evaluated_states_out > 1:
                    evaluated_states = evaluated_states_out
    dt = time.time() - start_time
    if evaluated_states < EVALUATED_INF:
        total_score = evaluated_states + search_config_length + search_log_length
    else: 
        total_score = evaluated_states - search_g_length * 1000 - search_plan_len
    ret_str = f"{total_score};{search_log_length};{search_g_length};{search_plan_length};{dt};{runscript}"
    #if dt < TIMEOUT and proc.returncode == 0: log.debug(ret_str)
    log.debug(ret_str)
    # return dt,
    return total_score,

toolbox.register("evaluate", evalSymbReg, points=[x/10. for x in range(-10,10)])
toolbox.register("select", tools.selTournament, tournsize=4)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=12)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))


import multiprocessing

def inf_filtered(arr, func):
    arr = numpy.array(arr)
    # result = [x for x in arr if x[0] < EVALUATED_INF]
    result = arr[arr < EVALUATED_INF]
    min_arr = numpy.min(arr)
    if len(result) == 0:
        result = [ EVALUATED_INF ]
    else:
        result = []
        if min_arr > EVALUATED_INF - 10000000:
            for x in arr:
                x = EVALUATED_INF - x
                result.append(x)
        else:
            result = arr
            
    return func(result)

last_time = time.time()
last_tdiff = 0
def time_diff(ind):
    global last_time
    global last_tdiff 
    if time.time() - last_time < 3.0:
        return last_tdiff
    last_tdiff = time.time() - last_time
    last_time = time.time()
    return last_tdiff


def main(sasfile, timeout):
    global SASFILE
    global TIMEOUT 

    SASFILE = sasfile
    TIMEOUT = timeout

    #random.seed(318)
    pool = multiprocessing.Pool(40)
    toolbox.register("map", pool.map)

    pop = toolbox.population(n=900) # 100->12/15 
    hof = tools.HallOfFame(1)
    
    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_time = tools.Statistics(time_diff)
    # stats_size = tools.Statistics(len)
    #mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats = tools.MultiStatistics(fitness=stats_fit, runtime=stats_time)
    # mstats.register("avg", lambda x: inf_filtered(x, numpy.mean))
    # mstats.register("std", lambda x: inf_filtered(x, numpy.std))
    mstats.register("min", lambda x: inf_filtered(x, numpy.min))
    mstats.register("max", lambda x: inf_filtered(x, numpy.max))
    # from scoop import futures
    # toolbox.register("map", futures.map)

    pop, log = algorithms.eaSimple(pop, toolbox, 0.5, 0.1, 40, stats=mstats, halloffame=hof, verbose=True)
    # pop, log = algorithms.eaMuCommaLambda(pop, toolbox, 1000, 30000, 0.5, 0.1, 40, halloffame=hof, stats=mstats, verbose=True)
    # print(log)
    pool.close()
    for h in hof:
        tree = gp.PrimitiveTree(h)
        print(str(tree))
        func = toolbox.compile(expr=tree)
        print(func)
    return pop, log, hof

if __name__ == "__main__":
    # print(main())
    import sys
    if len(sys.argv) < 3:
        print("USAGE", sys.argv[0], "<file.sas> <timeout>")
        sys.exit(1)
    pop = main(sys.argv[1], int(sys.argv[2]))
