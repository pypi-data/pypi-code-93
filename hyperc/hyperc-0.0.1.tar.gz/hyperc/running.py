import time
import pathlib
import hyperc.settings
import os
import copy
import logging
import random, string
log = logging.getLogger("hyperc")

class RunningPlanner:
    def __init__(
            self, name, proc=None, work_dir=None, run_dir=None, runscripts=None, translator=None, run_timeout=0,
            stdin=None, parent=None):
        """
        runscripts is a dict of list
        """
        self.lonely = False
        self.main_pid = -1
        self.proc = proc
        self.stdin = stdin
        self.work_dir = work_dir
        self.run_dir = run_dir
        self.run_timeout = run_timeout
        if run_timeout > 0:
            self.stop_time = time.time() + run_timeout
        else:
            self.stop_time = None
        self.name = name
        if runscripts is None:
            self.runscripts = {}
        else:
            assert isinstance(runscripts,dict)
            self.runscripts = runscripts
        self.translator = translator
        self.dir_created = False

    def create_dirs(self):
        if self.work_dir is not None:
            pathlib.Path(self.work_dir).mkdir(parents=True, exist_ok=True)
            if self.run_dir is None:
                self.run_dir = os.path.join(self.work_dir, self.name)
        if self.dir_created:
            return
        self.dir_created = True
        if self.run_dir is not None:
            try:
                pathlib.Path(self.run_dir).mkdir(parents=True)
            except FileExistsError:
                self.run_dir = self.run_dir + '_' + ''.join(random.choices(string.ascii_letters + string.digits, k=5))
                pathlib.Path(self.run_dir).mkdir(parents=True)
    
    def format(self):
        if self.translator is not None:
            for idx, part in enumerate(self.translator):
                self.translator[idx] = part.format(work_dir=self.work_dir, run_dir=self.run_dir)
        if self.runscripts is not None:
            for name in self.runscripts:
                for idx, part in enumerate(self.runscripts[name]):
                    self.runscripts[name][idx] = part.format(work_dir=self.work_dir, run_dir=self.run_dir)
        if self.stdin is not None:
            self.stdin = self.stdin.format(run_dir=self.run_dir, work_dir=self.work_dir)

    def reset_timer(self):
        if self.run_timeout > self.max_time:
           self.run_timeout = self.max_time
        if self.run_timeout > 0:
            self.stop_time = time.time() + self.run_timeout
        else:
            self.stop_time = None

    def check_timeout(self):
        if self.stop_time is not None:
            if time.time() > self.stop_time:
                return True
        return False
    
    def kill(self):
        try:
            import signal, psutil, platform, os
        except:
            log.error("Could not init process control")
            return


        if platform.system() == "Linux":
            try:
                pidg = os.getpgid(self.main_pid)
                os.killpg(pidg, signal.SIGTERM)
            except:
                log.error("CANT KILL")
        else:
            parent = psutil.Process(self.main_pid)
            children = parent.children(recursive=True)
            for child in children:
                log.error(f"kill pid {child.pid}")
                try:
                    child.kill()
                except Exception as ex:
                    log.error(ex)

            gone, still_alive = psutil.wait_procs(children, timeout=5)
            try:
                parent.kill()
                parent.wait(5)
            except Exception as ex:
                log.error(ex)
        if platform.system() == "Windows":
            # dead end
            try:
                os.system("TASKKILL /F /IM  /A downward.exe")
            except:
                log.error("Can't call TASKKILL")
        if hyperc.settings.HYPERC_DELETE_STDOUT == "1":
            try:
                os.remove(os.path.join(self.run_dir, "stdout.log"))
            except:
                pass
        if hyperc.settings.STORE_SAS == '0':
            for sas_file in [os.path.join(self.run_dir, 'output.sas'), os.path.join(self.work_dir, 'output.sas'), os.path.join(self.run_dir, 'rnd.sas'), os.path.join(self.work_dir, 'rnd.sas')]:
                try:
                    os.remove(sas_file)
                except:
                    pass

    def __str__(self):
        stdin = ""
        if self.stdin is not None:
            stdin = f'stdin - {self.stdin}'
        if self.translator is None:
            translator = "None"
        else:
            translator = " ".join(self.translator)
        if self.runscripts is None:
            runscripts = "None"
        else:
            runscripts = "\n".join([" ".join(runscript) for runscript in self.runscripts.values()])
        return "translator\n{translator}\runscripts\n{runscripts}\n{stdin}\n".format(
            translator=translator, runscripts=runscripts, stdin=stdin)


# Runnable templates
DOWNWARD_TRANSLATOR = hyperc.settings.DOWNWARD_FOLDER + "/builds/release/bin/translate/translate.py"
DOWNWARD_SEARCH = hyperc.settings.DOWNWARD_FOLDER + '/builds/release/bin/downward'

downward_translator = RunningPlanner(name="downward_translator",
                                     run_timeout=hyperc.settings.SOLVER_MAX_TIME, stdin=False)

downward_translator.translator = [
    hyperc.settings.PYTHON,
    DOWNWARD_TRANSLATOR,
    '{work_dir}/domain.pddl',
    '{work_dir}/problem.pddl',
    '--sas-file',
    '{run_dir}/output.sas',
    '--total-queue-pushes',
    hyperc.settings.DOWNWARD_TOTAL_PUSHES
]


default_ff = RunningPlanner(name="ff", run_timeout=15)
default_ff.runscripts['out'] = [
    os.path.join(hyperc.settings.DOWNWARD_FOLDER, 'builds/release/bin/ff'),
    '-o', '{work_dir}/domain.pddl',
    '-f', '{work_dir}/problem.pddl',
    '-P', '{run_dir}/out.plan'
]

runscript_template = [
    hyperc.settings.PYTHON,
    hyperc.settings.DOWNWARD_SCRIPT,
    '--plan-file', '{run_dir}/out.plan',
    '--sas-file', '{run_dir}/output.sas',
    '{work_dir}/domain.pddl',
    '{work_dir}/problem.pddl',
]

lmcount_alt5 = RunningPlanner(name="FastDownward-lmcount-alt5", run_timeout=hyperc.settings.SOLVER_MAX_TIME, stdin=True)

lmcount_alt5.translator = [
    hyperc.settings.PYTHON,
    DOWNWARD_TRANSLATOR,
    '{work_dir}/domain.pddl',
    '{work_dir}/problem.pddl',
    '--sas-file',
    '{run_dir}/output.sas',
    '--total-queue-pushes',
    hyperc.settings.DOWNWARD_TOTAL_PUSHES
]

lmcount_alt5.stdin = '{run_dir}/output.sas'
#ff evaluator only
lmcount_alt5.runscripts = {
    'ff+lmcount': [
        DOWNWARD_SEARCH,
        '--loglevel' , hyperc.settings.HYPERC_SOLVER_LOGLEVEL,
        '--evaluator', 'hff=ff()',
        '--evaluator', 'hlm=lmcount(lm_rhw(reasonable_orders=true),transform=no_transform())',
        '--search',
        "lazy(alt([single(hff),single(hff,pref_only=true),single(hlm),single(hlm,pref_only=true),type_based([hff,g()])],boost=1000),"
                    "preferred=[hff,hlm],"
                    "cost_type=one,"
                    "reopen_closed=false,"
                    "randomize_successors=true,"
                    "preferred_successors_first=false,"
                    "bound=infinity)",
        "--internal-plan-file", "{run_dir}/out.plan"
    ]
}

lmcount_gen1 = RunningPlanner(name="FastDownward-lmcount-gen1", run_timeout=hyperc.settings.SOLVER_MAX_TIME, stdin=True)

lmcount_gen1.translator = [
    hyperc.settings.PYTHON,
    DOWNWARD_TRANSLATOR,
    '{work_dir}/domain.pddl',
    '{work_dir}/problem.pddl',
    '--sas-file',
    '{run_dir}/output.sas',
    '--total-queue-pushes',
    hyperc.settings.DOWNWARD_TOTAL_PUSHES
]

lmcount_gen1.stdin = '{run_dir}/output.sas'
#ff evaluator only
lmcount_gen1.runscripts = {
    'ff+lmcount': [
        DOWNWARD_SEARCH,
        '--loglevel', hyperc.settings.HYPERC_SOLVER_LOGLEVEL,
        '--evaluator', 'hff=ff()',
        '--evaluator', 'hlm=lmcount(lm_rhw(reasonable_orders=true),transform=no_transform())',
        "--search", "lazy(alt([type_based([hlm, weight(g(), 296)]), type_based([goalcount(transform=no_transform(), cache_estimates=true), g()])], boost=8300), preferred=[], reopen_closed=false, randomize_successors=true, preferred_successors_first=true, bound=infinity)",
        "--internal-plan-file", "{run_dir}/out.plan"
    ]
}

lmcount_alt5_simple = RunningPlanner(name="FastDownward-lmcount-alt5-simple", run_timeout=hyperc.settings.SOLVER_MAX_TIME, stdin=True)
lmcount_alt5_simple.translator = [
    hyperc.settings.PYTHON,
    DOWNWARD_TRANSLATOR,
    '{work_dir}/domain.pddl',
    '{work_dir}/problem.pddl',
    '--sas-file', '{run_dir}/output.sas',
    '--total-queue-pushes', hyperc.settings.DOWNWARD_TOTAL_PUSHES,
    '--keep-unreachable-facts',
    '--skip-variable-reordering',
    '--keep-unimportant-variables',
    '--invariant-generation-max-time', '300',
    '--invariant-generation-max-candidates', '0',
    ]

lmcount_alt5_simple.stdin = '{run_dir}/output.sas'
lmcount_alt5_simple.runscripts = {
    'ff+lmcount': [
        DOWNWARD_SEARCH,
        '--loglevel' , hyperc.settings.HYPERC_SOLVER_LOGLEVEL,
        '--evaluator', 'hff=ff()',
        '--evaluator', 'hlm=lmcount(lm_rhw(reasonable_orders=true),transform=no_transform())',
        '--search',
        "lazy(alt([single(hff),single(hff,pref_only=true),single(hlm),single(hlm,pref_only=true),type_based([hff,g()])],boost=1000),"
        "preferred=[hff,hlm],"
        "cost_type=one,"
        "reopen_closed=false,"
        "randomize_successors=true,"
        "preferred_successors_first=false,"
        "bound=infinity)",
        "--internal-plan-file", "{run_dir}/out.plan"
    ]
}

alt_lazy_ff_cea = RunningPlanner(name="FastDownward-alt_lazy_ff_cea", run_timeout=hyperc.settings.SOLVER_MAX_TIME)
alt_lazy_ff_cea.runscripts = {'out': [
        hyperc.settings.PYTHON,
    hyperc.settings.DOWNWARD_SCRIPT,
    '--plan-file', '{run_dir}/out.plan',
    '--sas-file', '{run_dir}/output.sas',
    '{work_dir}/domain.pddl',
    '{work_dir}/problem.pddl',
    '--translate-options',
    '--total-queue-pushes', hyperc.settings.DOWNWARD_TOTAL_PUSHES,
    '--keep-unreachable-facts',
    '--skip-variable-reordering',
    '--keep-unimportant-variables',
    '--invariant-generation-max-time', '300',
    '--invariant-generation-max-candidates', '0',
    '--search-options',
    '--evaluator', 'hff=ff(transform=no_transform())',
    '--evaluator', 'hcea=cea(transform=no_transform())',
    '--search',
    "lazy_greedy("
            "[hff,hcea]"
            "preferred=[hff,hcea],"
            "cost_type=normal,"
            "bound=infinity)"
]}

eager_ff_cg = RunningPlanner(name="FastDownward-eager_ff_cg", run_timeout=hyperc.settings.SOLVER_MAX_TIME)
eager_ff_cg.runscripts = {'out': [
        hyperc.settings.PYTHON,
    hyperc.settings.DOWNWARD_SCRIPT,
    '--plan-file', '{run_dir}/out.plan',
    '--sas-file', '{run_dir}/output.sas',
    '{work_dir}/domain.pddl',
    '{work_dir}/problem.pddl',
    '--translate-options',
    '--total-queue-pushes', hyperc.settings.DOWNWARD_TOTAL_PUSHES,
    '--keep-unreachable-facts',
    '--skip-variable-reordering',
    '--keep-unimportant-variables',
    '--invariant-generation-max-time', '300',
    '--invariant-generation-max-candidates', '0',
    '--search-options',
    '--evaluator', 'hff=ff(transform=no_transform())',
    '--evaluator', 'hcg=cg(transform=no_transform())',
    '--search',
    "eager_greedy("
            "[hff,hcg]"
            "preferred=[hff,hcg],"
            "cost_type=normal,"
            "bound=infinity)"
  
]}

alt_lazy_cea_cg = RunningPlanner(name="FastDownward-alt_lazy_cea_cg", run_timeout=hyperc.settings.SOLVER_MAX_TIME)
alt_lazy_cea_cg.runscripts = {'out': [
        hyperc.settings.PYTHON,
    hyperc.settings.DOWNWARD_SCRIPT,
    '--plan-file', '{run_dir}/out.plan',
    '--sas-file', '{run_dir}/output.sas',
    '{work_dir}/domain.pddl',
    '{work_dir}/problem.pddl',
    '--translate-options',
    '--total-queue-pushes', hyperc.settings.DOWNWARD_TOTAL_PUSHES,
    '--keep-unreachable-facts',
    '--skip-variable-reordering',
    '--keep-unimportant-variables',
    '--invariant-generation-max-time', '300',
    '--invariant-generation-max-candidates', '0',
    '--search-options',
    '--evaluator', 'hcea=cea(transform=no_transform())',
    '--evaluator', 'hcg=cg(transform=no_transform())',
    '--search',
    "eager_greedy("
            "[hcea,hcg]"
            "preferred=[hcea,hcg],"
            "cost_type=normal,"
            "bound=infinity)"
  
]}

downward_default = RunningPlanner(name="downward_default", run_timeout=hyperc.settings.SOLVER_MAX_TIME)
downward_default.runscripts = {'out': [
    hyperc.settings.PYTHON,
    hyperc.settings.DOWNWARD_SCRIPT,
    '--plan-file', '{run_dir}/out.plan',
    '--sas-file', '{run_dir}/output.sas',
    '{work_dir}/domain.pddl',
    '{work_dir}/problem.pddl',
    '--translate-options',
    '--total-queue-pushes', hyperc.settings.DOWNWARD_TOTAL_PUSHES,
    '--search-options',
    '--evaluator', 'hff=ff()',
    '--search', "lazy(single(hff,pref_only=true),preferred=[hff],cost_type=normal,reopen_closed=false,randomize_successors=false,preferred_successors_first=false,bound=infinity)"
]}

double_search = RunningPlanner(name="double_search_ff+lmcount", run_timeout=hyperc.settings.SOLVER_MAX_TIME, stdin=True)

double_search.translator = [DOWNWARD_TRANSLATOR, '{work_dir}/domain.pddl', '{work_dir}/problem.pddl', '--sas-file', '{run_dir}/output.sas',
                            '--total-queue-pushes', hyperc.settings.DOWNWARD_TOTAL_PUSHES]

double_search.stdin = '{run_dir}/../output.sas'
#ff evaluator only
double_search.runscripts={"ff_only": [
    DOWNWARD_SEARCH,
    '--evaluator', 'hff=ff()', "--search",
    'lazy(single(hff,pref_only=true),preferred=[hff],cost_type=normal,reopen_closed=false,randomize_successors=false,preferred_successors_first=false,bound=infinity)',
    "--internal-plan-file", "{run_dir}/out.plan"],  # < {run_dir}/../output.sas

#lmcount + ff
'ff+lmcount': [
    DOWNWARD_SEARCH,
    '--evaluator', '"hff=ff()"', '--evaluator', 'hlm=lmcount(lm_rhw(reasonable_orders=true),transform=no_transform())',
    '--search', 'lazy(alt([single(hff),single(hff,pref_only=true),single(hlm),single(hlm,pref_only=true),type_based([hff,g()])],boost=1000),preferred=[hff,hlm],cost_type=one,reopen_closed=false,randomize_successors=true,preferred_successors_first=false,bound=infinity)',
    "--internal-plan-file", "{run_dir}/out.plan"]  # < {run_dir}/../output.sas
}


search_32_alt5 = RunningPlanner(name="search_32_alt5", run_timeout=hyperc.settings.SOLVER_MAX_TIME, stdin=True)

search_32_alt5.translator = [
    hyperc.settings.PYTHON, 
    DOWNWARD_TRANSLATOR, 
    '{work_dir}/domain.pddl', 
    '{work_dir}/problem.pddl', 
    '--sas-file', 
    '{run_dir}/output.sas',
    '--total-queue-pushes', 
    hyperc.settings.DOWNWARD_TOTAL_PUSHES
]


search_32_alt5.stdin = '{run_dir}/../output.sas'
#ff evaluator only
search_32_alt5.runscripts={
    'ff+lmcount'+str(i): [
        DOWNWARD_SEARCH,
        '--loglevel' , hyperc.settings.HYPERC_SOLVER_LOGLEVEL,
        '--evaluator', 'hff=ff()',
        '--evaluator', 'hlm=lmcount(lm_rhw(reasonable_orders=true),transform=no_transform())',
        '--search',
        "lazy(alt([single(hff),single(hff,pref_only=true),single(hlm),single(hlm,pref_only=true),type_based([hff,g()])],boost=1000),"
                    "preferred=[hff,hlm],"
                    "cost_type=one,"
                    "reopen_closed=false,"
                    "randomize_successors=true,"
                    "preferred_successors_first=false,"
                    "bound=infinity)",
        "--internal-plan-file", "{run_dir}/out.plan"
    ] for i in range(32)
}

search_all_alt5 = RunningPlanner(name="search_all_alt5", run_timeout=hyperc.settings.SOLVER_MAX_TIME, stdin=True)
search_all_alt5.translator = [hyperc.settings.PYTHON,DOWNWARD_TRANSLATOR,'{work_dir}/domain.pddl','{work_dir}/problem.pddl','--sas-file','{run_dir}/output.sas','--total-queue-pushes',hyperc.settings.DOWNWARD_TOTAL_PUSHES]
search_all_alt5.stdin = '{run_dir}/../output.sas'

cpu_amount = os.cpu_count()
if cpu_amount is None:
    cpu_amount = hyperc.settings.HYPERC_MAX_PROC_COUNTER
search_all_alt5.runscripts = {'ff+lmcount_'+str(i): [DOWNWARD_SEARCH, '--loglevel' , hyperc.settings.HYPERC_SOLVER_LOGLEVEL, '--evaluator', 'hff=ff()','--evaluator', 'hlm=lmcount(lm_rhw(reasonable_orders=true),transform=no_transform())','--search',"lazy(alt([single(hff),single(hff,pref_only=true),single(hlm),single(hlm,pref_only=true),type_based([hff,g()])],boost=1000),preferred=[hff,hlm],cost_type=one,reopen_closed=false,randomize_successors=true,preferred_successors_first=false,bound=infinity)","--internal-plan-file", "{run_dir}/out.plan"] for i in range(cpu_amount)}

eager_lmcount_stubborn = RunningPlanner(name="FastDownward-lmcount_alt5_stubborn",
                                        run_timeout=hyperc.settings.SOLVER_MAX_TIME)
eager_lmcount_stubborn.runscripts = {'out': [
    hyperc.settings.PYTHON,
    hyperc.settings.DOWNWARD_SCRIPT,
    '--plan-file', '{run_dir}/out.plan',
    '--sas-file', '{run_dir}/output.sas',
    '{work_dir}/domain.pddl',
    '{work_dir}/problem.pddl',
    '--translate-options',
    '--total-queue-pushes', hyperc.settings.DOWNWARD_TOTAL_PUSHES,
    '--search-options',
    '--evaluator', 'hff=ff()',
    '--evaluator', 'hlm=lmcount(lm_rhw(reasonable_orders=true),transform=no_transform())',
    '--search',
    'eager(alt([single(hff),single(hff,pref_only=true),single(hlm),single(hlm,pref_only=true),type_based([hff,g()])],boost=1000),cost_type=one,preferred=[hff,hlm],reopen_closed=false,pruning=stubborn_sets_simple(min_required_pruning_ratio=0.2,expansions_before_checking_pruning_ratio=1000))'
]}

eager_ff_stubborn_sets = RunningPlanner(name="FastDownward-eager_ff_simple_stubborn_sets",
                                        run_timeout=hyperc.settings.SOLVER_MAX_TIME)
eager_ff_stubborn_sets.runscripts = {'out': [
    hyperc.settings.PYTHON,
    hyperc.settings.DOWNWARD_SCRIPT,
    '--plan-file', '{run_dir}/out.plan',
    '--sas-file', '{run_dir}/output.sas',
    '{work_dir}/domain.pddl',
    '{work_dir}/problem.pddl',
    '--translate-options',
    '--total-queue-pushes', hyperc.settings.DOWNWARD_TOTAL_PUSHES,
    '--search-options',
    '--evaluator', 'hff=ff()',
    '--search', 'eager(single(hff,pref_only=true),preferred=[hff],'
    'pruning=stubborn_sets_simple(min_required_pruning_ratio=0.2,expansions_before_checking_pruning_ratio=1000))'
]}


maplan_search = RunningPlanner(name="maplan_search", run_timeout=hyperc.settings.SOLVER_MAX_TIME)
maplan_search.translator = [hyperc.settings.DOWNWARD_FOLDER + '/maplan/third-party/translate/translate.py', '--proto', '--output', '{run_dir}/problem.proto', '{work_dir}/domain.pddl', '{work_dir}/problem.pddl']
maplan_search.runscripts = {
'lm-cut+astar':
[hyperc.settings.DOWNWARD_FOLDER+'/maplan/bin/search', '-p', '{work_dir}/problem.proto', '-H', 'lm-cut', '-s', 'astar', '-o', '{run_dir}/out.plan']}

# ff_cg_lazy_greedy = RunningPlanner(name="ff_cg_lazy_greedy",)
    #         runscript.extend([
    #             '--search-options',
    #             '--evaluator', 'hff=ff(transform=no_transform())',
    #             '--evaluator', 'hcg=cg(transform=no_transform())',
    #             '--search', ("lazy_greedy("
    #                          "[hff,hcg]"
    #                          "preferred=[hff,hcg],"
    #                          "cost_type=normal,"
    #                          "reopen_closed=false,"
    #                          "randomize_successors=true,"
    #                          "preferred_successors_first=false,"
    #                          "bound=infinity,max_time={max_time})".format(max_time=max_time))
    #         ])
    #     elif search_config == "alt_eager_ff_cea_cg":
    #         runscript.extend([
    #             '--search-options',
    #             '--evaluator', 'hff=ff(transform=no_transform())',
    #             '--evaluator', 'hcea=cea(transform=no_transform())',
    #             '--evaluator', 'hcg=cg(transform=no_transform())',
    #             '--search', ("eager_greedy("
    #                          "[hff,hcea,hcg]"
    #                          "preferred=[hff,hcea,hcg],"
    #                          "cost_type=normal,"
    #                          "bound=infinity,max_time={max_time})".format(max_time=max_time))
    #         ])
    #     elif search_config == "alt_lazy_ff_cea":
    #         runscript.extend([
    #             '--search-options',
    #             '--evaluator', 'hff=ff(transform=no_transform())',
    #             '--evaluator', 'hcea=cea(transform=no_transform())',
    #             '--search', ("lazy_greedy("
    #                          "[hff,hcea]"
    #                          "preferred=[hff,hcea],"
    #                          "cost_type=normal,"
    #                          "bound=infinity,max_time={max_time})".format(max_time=max_time))
    #         ])
    #     elif search_config == "alt_lazy_cea_ff":
    #         runscript.extend([
    #             '--search-options',
    #             '--evaluator', 'hff=ff(transform=no_transform())',
    #             '--evaluator', 'hcea=cea(transform=no_transform())',
    #             '--search', ("lazy_greedy("
    #                          "[hcea,hff]"
    #                          "preferred=[hcea,hff],"
    #                          "cost_type=normal,"
    #                          "bound=infinity,max_time={max_time})".format(max_time=max_time))
    #         ])
    #     elif search_config == "alt_lazy_ff_cea_opt":
    #         runscript.extend([
    #             '--keep-unreachable-facts',
    #             '--skip-variable-reordering',
    #             '--keep-unimportant-variables',
    #             '--invariant-generation-max-time', '300',
    #             '--invariant-generation-max-candidates', '0',
    #             '--search-options',
    #             '--evaluator', 'hff=ff(transform=no_transform())',
    #             '--evaluator', 'hcea=cea(transform=no_transform())',
    #             '--search', ("lazy_greedy("
    #                          "[hff,hcea]"
    #                          "preferred=[hff,hcea],"
    #                          "cost_type=normal,"
    #                          "reopen_closed=false,"
    #                          "randomize_successors=true,"
    #                          "preferred_successors_first=false,"
    #                          "bound=infinity,max_time={max_time})".format(max_time=max_time))
    #         ])
    #     elif search_config == "alt_lazy_ff_cea_opt2":
    #         runscript.extend([
    #             '--keep-unreachable-facts',
    #             '--skip-variable-reordering',
    #             '--keep-unimportant-variables',
    #             '--invariant-generation-max-time', '300',
    #             '--invariant-generation-max-candidates', '0',
    #             '--search-options',
    #             '--evaluator', 'hff=ff(transform=no_transform())',
    #             '--evaluator', 'hcea=cea(transform=no_transform())',
    #             '--search', ("lazy_greedy("
    #                          "[hff,hcea]"
    #                          "preferred=[hff,hcea],"
    #                          "cost_type=one,"
    #                          "reopen_closed=false,"
    #                          "randomize_successors=true,"
    #                          "preferred_successors_first=false,"
    #                          "bound=infinity,max_time={max_time})".format(max_time=max_time))
    #         ])
    #     elif search_config == "alt_lazy_ff_cea":
    #         runscript.extend([
    #             '--search-options',
    #             '--evaluator', 'hff=ff(transform=no_transform())',
    #             '--evaluator', 'hcea=cea(transform=no_transform())',
    #             '--search', ("lazy_greedy("
    #                          "[hff,hcea]"
    #                          "preferred=[hff,hcea],"
    #                          "cost_type=normal,"
    #                          "bound=infinity,max_time={max_time})".format(max_time=max_time))
    #         ])

    #     elif search_config == "eager_ff_cg":
    #         runscript.extend([
    #             '--search-options',
    #             '--evaluator', 'hff=ff(transform=no_transform())',
    #             '--evaluator', 'hcg=cg(transform=no_transform())',
    #             '--search', ("eager_greedy("
    #                          "[hff,hcg]"
    #                          "preferred=[hff,hcg],"
    #                          "cost_type=normal,"
    #                          "bound=infinity,max_time={max_time})".format(max_time=max_time))
    #         ])
    #     elif search_config == "alt_lazy_cea_cg":
    #         runscript.extend([
    #             '--search-options',
    #             '--evaluator', 'hcea=cea(transform=no_transform())',
    #             '--evaluator', 'hcg=cg(transform=no_transform())',
    #             '--search', ("eager_greedy("
    #                          "[hcea,hcg]"
    #                          "preferred=[hcea,hcg],"
    #                          "cost_type=normal,"
    #                          "bound=infinity,max_time={max_time})".format(max_time=max_time))
    #         ])
    #     elif search_config == "alt_eager_ff_add":
    #         runscript.extend([
    #             '--search-options',
    #             '--evaluator', 'hff=ff(transform=no_transform())',
    #             '--evaluator', 'hadd=add(transform=no_transform())',
    #             '--search', ("eager_greedy("
    #                          "[hff,hadd]"
    #                          "preferred=[hff,hadd],"
    #                          "cost_type=normal,"
    #                          "bound=infinity,max_time={max_time})".format(max_time=max_time))
    #         ])
