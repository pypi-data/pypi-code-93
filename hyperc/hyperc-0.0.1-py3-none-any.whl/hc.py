# Command-line hypercomputation tool for XTJ format

# Out: - time to solve
#      - whether it was able to solve
# Status, Time, Reason, Path to solve folder

import hyperc.xtj
import hyperc.exceptions
import sys
import time
import json
import os
import argparse

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "xtj_file", metavar="<file.xtj>", help="path to xtj file")
    argparser.add_argument(
        "--out-file", dest="xtj_file_output", metavar="<out.xtj>", default="out.xtj", help="path to xtj file")
    argparser.add_argument(
        "--tmp", dest="tmp", default="./.hc_cache",
        help="path to the tmp dir")
    argparser.add_argument(
        "--goal", dest="goal", default=None,
        help="Goal name (first if not defined)")
    argparser.add_argument(
        "--input", dest="input", default=None,
        help="Input name (first if not defined)")


    try:
        args = argparser.parse_args()
    except:
        argparser.print_help()
        sys.exit(0)

    os.makedirs(args.tmp, exist_ok=True)
    x = hyperc.xtj.XTJ(open(args.xtj_file), work_dir=args.tmp)
    start = time.time()
    status = "[ OK ]"
    err = "Solved"
    meta = {}
    try:
        x.solve(metadata=meta)
    except hyperc.exceptions.SchedulingError as e:
        status = "[FAIL]"
        err = e
    json.dump(x.merge_result().json_data, open(args.xtj_file_output, "w+"))
    print(f"{status}, {str('%.2f' % (time.time()-start)).rjust(7, '0')}, seconds, {err}, {meta['work_dir']}, Evaluations, {meta['stats']['evaluations']}")


if __name__ == "__main__":
    main()
