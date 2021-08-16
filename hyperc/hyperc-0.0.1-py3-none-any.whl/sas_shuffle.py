import sys
from random import shuffle

SAS_STF_BEG = """begin_version
3
end_version
begin_metric
0
end_metric
"""

class SASFile:
    def __init__(self):
        self.version = 3
        self.metric = 0
        self.variable_count = 0
        self.variables = []
        self.mutex_count = 0
        self.mutexes = []
        self.state = []
        self.goal = []
        self.operators_count = 0
        self.operators = []
        self.axioms_count = 0
        self.axioms = []

    def load_sas(self, fd):
        # skip version, metric
        for _ in range(6): fd.readline()
        # get variable count
        self.variable_count = int(fd.readline().strip())
        for _ in range(self.variable_count):
            vline = fd.readline().strip()
            assert vline.strip() == "begin_variable"
            var_lines = [vline]
            while vline.strip() != "end_variable":
                vline = fd.readline().strip()
                var_lines.append(vline)
            self.variables.append(var_lines)
        self.mutex_count = int(fd.readline().strip())
        for _ in range(self.mutex_count):
            vline = fd.readline().strip()
            assert vline.strip() == "begin_mutex_group"
            var_lines = [vline]
            while vline.strip() != "end_mutex_group":
                vline = fd.readline()[:-1]
                var_lines.append(vline)
            self.mutexes.append(var_lines)
        # now state
        state_line = fd.readline().strip()
        assert state_line.strip() == "begin_state", "State section inconsistency"
        self.state.append(state_line)
        while state_line.strip() != "end_state":
            state_line = fd.readline().strip()
            self.state.append(state_line)
        # goal
        goal_line = fd.readline().strip()
        assert goal_line.strip() == "begin_goal", "Goal section inconsistency"
        self.goal.append(goal_line)
        while goal_line.strip() != "end_goal":
            goal_line = fd.readline().strip()
            self.goal.append(goal_line)
        # operators
        self.operators_count = int(fd.readline().strip())
        for _ in range(self.operators_count):
            vline = fd.readline().strip()
            assert vline.strip() == "begin_operator"
            var_lines = [vline]
            while vline.strip() != "end_operator":
                vline = fd.readline().strip()
                var_lines.append(vline)
            self.operators.append(var_lines)
        # assume no axioms
        assert len(self.operators) == self.operators_count
        assert len(self.variables) == self.variable_count
        assert len(self.mutexes) == self.mutex_count
    
    def shuffle_operators(self):
        shuffle(self.operators)
    
    def gen_sasfile(self):
        sasfile = SAS_STF_BEG
        sasfile += "%s\n" % self.variable_count # append variables count
        # append all variables
        sasfile += "\n".join(['\n'.join(x) for x in self.variables])
        sasfile += "\n%s\n" % self.mutex_count
        sasfile += "\n".join(['\n'.join(x) for x in self.mutexes])
        sasfile += "\n"
        sasfile += "\n".join(self.state)
        sasfile += "\n"
        sasfile += "\n".join(self.goal)
        sasfile += "\n%s\n" % self.operators_count
        sasfile += "\n".join(['\n'.join(x) for x in self.operators])
        # append no axioms
        sasfile += "\n0\n"
        return sasfile
    

def main():
    sf = SASFile()
    fd = open(sys.argv[1])
    sf.load_sas(fd)
    if len(sys.argv) == 3:
        sf.shuffle_operators()
    of = open(sys.argv[2], "w+")
    of.write(sf.gen_sasfile())
    of.close()

if __name__ == '__main__':
    main()

