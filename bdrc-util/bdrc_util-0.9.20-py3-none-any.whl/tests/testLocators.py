import csv
import unittest
from collections import Counter
from typing import Callable

from archive_ops import *


def works_to_list(file_path: str) -> []:
    """
    Creates a 2 dim array list from a csv file in file_path.
    :param file_path:
    :return: list of list of row values. list[0] is the header
    """

    out_rows = []
    with open(file_path, newline='\n') as csv_data:
        data_dict = csv.DictReader(csv_data)
        for row in data_dict:
            out_rows.append(row)

    return out_rows


def counters_to_list(bucket_work_counts: Counter, bucket_sizes: Counter, bucket_file_counts: Counter) -> []:
    """
    Transforms counters into dicts
    :param bucket_work_counts: number of works in this bucket
    :param bucket_sizes: total bytes in this bucket
    :param bucket_file_counts: total files in this bucket
    :return: list of
    """
    return list(
        map(lambda x: [x, bucket_work_counts[x], bucket_sizes[x], bucket_file_counts[x]], bucket_work_counts.keys()))


def hist_buckets(data_list: [], algo: Callable) -> []:
    """
    Get count of works in each bucket from the list of works
    :param data_list: list of dict objects, with keys bucket,count,file_size (at least)
    :type data_list: []
    :param algo: bucketing function
    :type algo: object
    :return: tuple of counters of buckets, bucket sizes, bucket file counts which represents the
    operation of algo
    """
    buckets = Counter()
    bucket_sizes = Counter()
    bucket_file_count = Counter()

    for aWork in data_list:
        w_root, w_bucket = algo(aWork['bucket'])
        buckets[w_bucket] += 1
        bucket_sizes[w_bucket] += int(aWork['size'])
        bucket_file_count[w_bucket] += int(aWork['file_count'])

    return counters_to_list(buckets, bucket_sizes, bucket_file_count)


def b2(w): return locators.r_divmod_50_b_2(w)


def md5_b2(w): return locators.r_divmod_50_b_md5_2(w)


class MyTestCase(unittest.TestCase):

    fs_root: str = "/Path/TestRoot"
    s3_root: str = "s3://Path/TestRoot"

    def test_shell_gt_bucket_lim(self):
        test_target0: str = "W1FPL51"
        expected: str = "/Path/TestRoot1/51/W1FPL51"
        self.assertEqual(expected, locators.r_divmod_50_b_2(self.fs_root, test_target0))

        expected: str = "s3://Path/TestRoot1/51/W1FPL51"
        self.assertEqual(expected, locators.r_divmod_50_b_2(self.s3_root, test_target0))

    def test_shell_lt_bucket_lim(self):
        test_target0: str = "W1FPL49"
        expected: str = "/Path/TestRoot0/49/W1FPL49"
        self.assertEqual(expected, locators.r_divmod_50_b_2(self.fs_root, test_target0))
        expected: str = "s3://Path/TestRoot0/49/W1FPL49"
        self.assertEqual(expected, locators.r_divmod_50_b_2(self.s3_root, test_target0))

    def test_non_numeric_shell(self):
        test_target0: str = "W1FPL"
        expected: str = "/Path/TestRoot0/00/W1FPL"
        self.assertEqual(expected, locators.r_divmod_50_b_2(self.fs_root, test_target0))
        expected: str = "s3://Path/TestRoot0/00/W1FPL"
        self.assertEqual(expected, locators.r_divmod_50_b_2(self.s3_root, test_target0))

    def test_null(self):
        test_target0: str = "Zaphod"
        expected: str = "/Path/TestRoot/Zaphod"
        self.assertEqual(expected, locators.r_null(self.fs_root, test_target0))
        expected: str = "s3://Path/TestRoot/Zaphod"
        self.assertEqual(expected, locators.r_null(self.s3_root, test_target0))

    def test_s3(self):
        test_target0: str = "Zaphod"
        expected: str = "/Path/TestRoot/f5/Zaphod"
        self.assertEqual(expected, locators.r_s3(self.fs_root, test_target0))
        expected: str = "s3://Path/TestRoot/f5/Zaphod"
        self.assertEqual(expected, locators.r_s3(self.s3_root, test_target0))

    @staticmethod
    def write_hashes(buckets: Counter, bucket_sizes: Counter, bucket_file_counts: Counter):
        with open('bucket_dist.csv', 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(['bucket', 'count', 'size', 'file_count'])
            for bb in buckets.keys():
                writer.writerow([bb, buckets[bb], bucket_sizes[bb], bucket_file_counts[bb]])


if __name__ == '__main__':
    unittest.main()
