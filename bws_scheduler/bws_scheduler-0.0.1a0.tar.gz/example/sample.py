from bws_scheduler import Scheduler, Task

sched = Scheduler()

@sched.add("00:0:05")
def task_interval(state, task):
    """
    docstring
    """
    state["num"] = state.get("num", 0) + 1
    print("num: %s" % state["num"])


if __name__ == "__main__":
    sched.run()
