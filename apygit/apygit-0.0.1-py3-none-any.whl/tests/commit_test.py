#!/usr/bin/env python3

import logging
import six
import time
import unittest

import repo_test


class MetaClass(type):
    def __dir__(cls):
        return cls.__dict__.keys()

@six.add_metaclass(MetaClass)
class TestClient(repo_test.TestClient):

    def test_Commit__init__(self):
        commits = self.repo.commits()
        assert len(commits) == 2, commits

    def test_commit_compare(self):
        commits_1 = self.repo.commits()
        commits_2 = self.repo.commits()
        assert commits_1[0] != commits_1[1]
        assert commits_1[0] != commits_2[1]
        assert commits_2[0] != commits_1[1]
        assert commits_2[0] != commits_2[1]
        assert commits_1[0] == commits_2[0]
        assert commits_1[1] == commits_2[1]
        assert "initial commit" in commits_1[1].log, commits_1[1].log
        time.sleep(1)
        self.create_commit(99)
        self.push()
        commits_3 = self.repo.commits()
        assert len(commits_3) == 3, commits_3
        assert "initial commit" in commits_3[2].log, commits_1[2].log
        assert "1: oneline" in commits_3[1].log, commits_1[1].log
        assert "99: oneline" in commits_3[0].log, commits_1[0].log
        assert commits_1[0] == commits_3[1]
        assert commits_1[1] == commits_3[2]
        assert commits_1[0] < commits_3[0]
        assert commits_1[1] < commits_3[0]
        assert hash(commits_3[0]) != hash(commits_3[1])
        assert hash(commits_3[0]) != hash(commits_3[2])
        assert hash(commits_3[1]) != hash(commits_3[2])
        assert hash(commits_1[0]) == hash(commits_3[1])
        assert hash(commits_1[1]) == hash(commits_3[2])
        assert commits_1[0].log == commits_3[1].log
        assert commits_1[1].log == commits_3[2].log



if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="count", default=0)

    args = parser.parse_args()

    if args.verbose >= 2:
        level = logging.DEBUG
        format = "%(asctime)-15s  %(levelname)5s  %(filename)s:%(lineno)d  %(message)s"
        logging.basicConfig(stream=sys.stderr, level=level, format=format)

    unittest.main()
