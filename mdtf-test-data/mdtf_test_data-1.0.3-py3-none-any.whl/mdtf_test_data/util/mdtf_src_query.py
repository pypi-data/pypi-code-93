#!/usr/bin/env python

import sys
from mdtf_test_data.synthetic.synthetic_data import dataset_stats

if __name__ == "__main__":
    filename = sys.argv[1]
    var = sys.argv[2] if len(sys.argv) >= 3 else None
    limit = sys.argv[3] if len(sys.argv) >= 4 else None

    dataset_stats(filename, var, limit)
