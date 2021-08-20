import collections
import json
import math
import statistics

from retriever_research.profiler.profiler import Profiler


UNIT_MAP = dict(
    cpu_avg="%",
    free_mem="GB",
    net_sent="Gbit/s",
    net_recv="Gbit/s",
    disk_read="MB/s",
    disk_write="MB/s",
    disk_iops="#",
    proc_mem="MB",
    proc_count="#",
)

def humanize_float(num): return "{0:,.4f}".format(num)
h=humanize_float


def summarize_profile(profiler: Profiler):
    # TODO: don't take profiler as input
    # TODO: Pull start and end time from profile file
    if profiler.start_time and profiler.end_time:
        print(f"Duration: {h(profiler.end_time - profiler.start_time)} sec")

    profiles = collections.defaultdict(lambda: [])
    with open(profiler.file_loc, 'r') as f:
        for line in f:
            profile_event = json.loads(line)
            for measurement_name, measurement_val in profile_event.items():
                if measurement_name == "timestamp" or measurement_name == "per_cpu":
                    continue
                profiles[measurement_name].append(measurement_val)

    for measurement_name, timeseries in profiles.items():
        avg_val = statistics.mean(timeseries)
        max_val = max(timeseries)
        min_val = min(timeseries)
        median_val = statistics.median(timeseries)

        print("------------------------")
        print(f"Profile Summary - {measurement_name} ({UNIT_MAP[measurement_name]})")
        # print(f"Num Datapoints={len(timeseries)}")
        print(f"avg: {h(avg_val)}")
        print(f"max: {h(max_val)}")
        print(f"min: {h(min_val)}")
        print(f"median: {h(median_val)}")
        print(f"first: {h(timeseries[0])}")
        # print(f"p90: {h(calculate_percentile(timeseries, 90))}")
        # print(f"p80: {h(calculate_percentile(timeseries, 80))}")
        # # print(f"p70: {h(calculate_percentile(timeseries, 70))}")
        # print(f"p60: {h(calculate_percentile(timeseries, 60))}")
        # print(f"median: {h(median_val)}")
        # print(f"p40: {h(calculate_percentile(timeseries, 40))}")
        # # print(f"p30: {h(calculate_percentile(timeseries, 30))}")
        # print(f"p20: {h(calculate_percentile(timeseries, 20))}")
        # print(f"p10: {h(calculate_percentile(timeseries, 10))}")
        print()


def calculate_percentile(timeseries, percentile):
    n = len(timeseries)
    p = n * percentile / 100
    if p.is_integer():
        return sorted(timeseries)[int(p)]
    else:
        return sorted(timeseries)[int(math.ceil(p)) - 1]


if __name__ == '__main__':
    prof = Profiler(interval=0.1)
    prof.start()

    from retriever_research.retriever import Retriever
    ret = Retriever()
    # ret.launch(s3_bucket="quilt-ml", s3_prefix="cv/coco2017/annotations/captions_", s3_region="us-east-1")
    ret.launch(s3_bucket="quilt-ml", s3_prefix="cv/coco2017/annotations/captions_train2017.json", s3_region="us-east-1", download_loc="./downloads/")
    # ret.launch(s3_bucket="quilt-ml", s3_prefix="cv/coco2017/train2017/000000000025.jpg", s3_region="us-east-1")
    ret.get_output()

    prof.end()
    summarize_profile(prof)