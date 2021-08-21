import pathlib
from retriever_research.profiler.event import ProfileEvent
import zlib

try:
    import ujson as json
except ImportError:
    import json


# Interface to the 20min.profile file.
# - Can we load the whole thing into memory?
# - Should we use a pure approach?
# - Should we sit on top of an open fileobj?
# - Will this only be for replays or will this also be able to handle live files?
#
# Should have a different interface for viewing old profiles and for streaming current data. Old data should generate videos
# Streaming should use live UX like tkinter, awesome unicode usage, jupyter dynamic graphs, tsdb + streaming graph, streamlit?
class Profile:
    def __init__(self, inp):
        self.events = []
        for line in inp:
            self.events.append(ProfileEvent.from_json(line))

        # self.events = []
        # for line in inp:
        #     self.events.append(line)




    # def create_static_graphs(self):
    #     import matplotlib.pyplot as plt
    #
    #     fig, axs = plt.subplots(9, 1)
    #     ts = [e.timestamp for e in self.events]
    #     axs[0].plot(ts, [e.cpu_avg for e in self.events])
    #     axs[1].plot(ts, [e.free_mem for e in self.events])
    #     axs[2].plot(ts, [e.net_sent for e in self.events])
    #     axs[3].plot(ts, [e.net_recv for e in self.events])
    #     axs[4].plot(ts, [e.disk_read for e in self.events])
    #     axs[5].plot(ts, [e.disk_write for e in self.events])
    #     axs[6].plot(ts, [e.disk_iops for e in self.events])
    #     axs[7].plot(ts, [e.proc_mem for e in self.events])
    #     axs[8].plot(ts, [e.proc_count for e in self.events])
    #     axs[0].grid(True)
    #
    #     fig.set_size_inches(15, 20)
    #     fig.savefig('test2png.png', dpi=100)


    def create_static_graphs(self):
        import matplotlib.pyplot as plt

        with plt.style.context("ggplot"):
            fig, axs = plt.subplots(3, 1)
            ts = [e.timestamp for e in self.events]
            dur_secs = (ts[-1] - ts[0]).total_seconds()
            dur_mins = dur_secs / 60
            axs[0].plot(ts, [e.cpu_avg for e in self.events])
            axs[0].title.set_text('Avg CPU %')
            axs[1].plot(ts, [e.free_mem for e in self.events])
            axs[1].title.set_text('Free Memory (GB)')
            axs[2].plot(ts, [e.net_recv for e in self.events])
            axs[2].title.set_text('Network Throughput, Received (Gbit/s)')
            axs[0].grid(True)

        x_inches_per_minute = 6
        fig.set_size_inches(dur_mins * x_inches_per_minute,5)
        fig.tight_layout()
        fig.savefig('test2png.png', dpi=200)
        plt.show()





if __name__ == '__main__':
    from retriever_research.profiler.collectors import ProcInfoCollector

    print(f"Starting mem: {ProcInfoCollector.sample()[0]} MB")
    with open("example_profiles/cocoval.profile", 'r') as f:
        p = Profile(inp=f)
    print(f"End mem: {ProcInfoCollector.sample()[0]} MB")

    # When 20min.profile is 3.7MB, this python process uses about 14MB. Not good at scale
    # We can reduce this to about 5MB if we store each event as a string instead of as ProfilerEvents (likely at the cost of latency later)
    # We can reduce this down to 4 MB if we compress each str (individually) with zlib. Not worth

    p.create_static_graphs()