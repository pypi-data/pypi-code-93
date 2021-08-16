from js import document
from collections import defaultdict
import time

DIRTY_FRAMES = set()

FRAME = 0
TOTAL_FRAMES = 6

FRAME_ACCESS_TIME = defaultdict(lambda: 0)

# def get_iframe_status():
#     return document.getElementById("ffframe").contentWindow.Module.calledRun

# def reset(finish):
#     document.getElementById("ffframe").contentWindow.location.reload()
#     document.getElementById("ffframe").contentWindow.onload = finish

def reset():
    global DIRTY_FRAMES
    global FRAME
    DIRTY_FRAMES.add(FRAME)
    dframe = FRAME
    def undirty(evt):
        global DIRTY_FRAMES
        # print("Undirty! %s" % dframe)
        try:
            DIRTY_FRAMES.remove(dframe)
        except KeyError:
            pass
    document.getElementById(f"ffframe{FRAME}").contentWindow.dirty = True
    document.getElementById(f"ffframe{FRAME}").addEventListener("load", undirty, True)
    document.getElementById(f"ffframe{FRAME}").contentWindow.location.reload()
    # print(f"Resetting frame {FRAME}")

def select_frame():
    global FRAME
    global DIRTY_FRAMES
    global FRAME_ACCESS_TIME 
    FRAME = -1
    for i in range(TOTAL_FRAMES):
        if not hasattr(document.getElementById("ffframe%s" % i).contentWindow, "dirty") and \
            not i in DIRTY_FRAMES and time.time() - FRAME_ACCESS_TIME[i] > 3: 
            FRAME = i
            break
    if FRAME == -1:
        raise EnvironmentError("WASM Vritual Machine busy; please wait.")
    FRAME_ACCESS_TIME[FRAME] = time.time()
    # print("Selected frame %s" % FRAME)

def write_file(path, sdata):
    # print("Writing in frame %s" % FRAME)
    document.getElementById(f"ffframe{FRAME}").contentWindow.FS.writeFile(path, sdata)

def read_file(path):
    # print("Reading in frame %s" % FRAME)
    return document.getElementById(f"ffframe{FRAME}").contentWindow.FS.readFile(path, {"encoding": "utf8"})

def write_problem_file(sdata):
    write_file("/problem.pddl", sdata)

def write_domain_file(sdata):
    write_file("/domain.pddl", sdata)

def run_ff_solver():
    "we assume that files have already been written with above functions"
    # print("Solving in frame %s" % FRAME)
    document.getElementById(f"ffframe{FRAME}").contentWindow.callMain(
        ["-o", "/domain.pddl", "-f", "/problem.pddl", "-P", "/out.plan"])

def read_plan():
    path = "/out.plan"
    if not document.getElementById(f"ffframe{FRAME}").contentWindow.FS.analyzePath(path).path:
        return "NoSolution"
    if "goal can be simplified to FALSE" in document.getElementById(f"ffframe{FRAME}").contentWindow.ss:
        return "NoSolutionProven"
    return read_file(path)
