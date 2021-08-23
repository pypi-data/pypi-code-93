#!/usr/bin/env python3

import logging
import os
import shutil
import subprocess
import tempfile
import unittest

import pygit


TEMP_PATH = os.environ.get("PYGIT_TEST_TEMP_PATH", "/tmp")
NO_DELETE = os.environ.get("PYGIT_TEST_NO_DELETE", "") != ""


class TestBase(unittest.TestCase):

    valid_commit_message = "oneline\n\ndetailed description\n"

    def create_git_repo(self, name, path):
        pygit.repo.execute(["init", "--bare", name], cwd=TEMP_PATH)
        with open(os.path.join(path, "description"), "w") as f:
            f.write(name.replace(".git", ""))
        self.server = pygit.Repository(path)

    def create_git_client(self, server_path, name, path):
        # create client (clone server)
        pygit.repo.execute(["clone", server_path, path], cwd=TEMP_PATH,
            stderr=subprocess.STDOUT)  # 2>&1 so we don't see warning about empty repo
        # make an initial commit (store client repo handle)
        self.client = pygit.Repository(path)  # do all test operations in the client
        # make sure to setup a valid email addr
        self.client.execute(["config", "user.email", "noreply@gmail.com"])
        filename = os.path.join(path, "README.md")
        with open(filename, "w") as f:
            f.write("initial commit\n")
        self.client.execute(["add", filename])
        self.client.execute(["commit", "-am", "initial commit"])
        self.client.execute(["push", "origin", "main"], stderr=subprocess.STDOUT)

        # tag the first commit with the "init" tag; all our repos have this tag
        commits = self.client.execute(["rev-list", "--all"], stderr=subprocess.STDOUT)
        commit = commits.split("\n")[-1]  # first commit
        self.client.execute(["tag", "-m", "initial commit", "init", commit],
            stderr=subprocess.STDOUT)
        self.client.execute(["push", "origin", "--tags"], stderr=subprocess.STDOUT)

    def delete_git_repos(self):
        if os.path.exists(self.server_path):
            shutil.rmtree(self.server_path, True)
        if os.path.exists(self.client_path):
            shutil.rmtree(self.client_path, True)


    def setUp(self):
        self.server_name = "git-test-server.git"
        self.server_path = os.path.join(TEMP_PATH, self.server_name)
        self.client_name = "git-test-client"
        self.client_path = os.path.join(TEMP_PATH, self.client_name)
        self.delete_git_repos()
        self.create_git_repo(self.server_name, self.server_path)
        self.create_git_client(self.server_path, self.client_name, self.client_path)
        self.create_commit(1)

    def tearDown(self):
        if not NO_DELETE:
            self.delete_git_repos()

    def commit(self, msg, amend=False, commit_date=None, push=True):
        """ Commit and push to the server """
        f = tempfile.NamedTemporaryFile(delete=False, mode='w+')
        f.write(msg)
        f.close()
        if commit_date:
            os.environ["GIT_COMMITTER_DATE"] = commit_date.isoformat()
        self.client.execute(["add", "."])
        cmd = ["commit", "-aF", f.name]
        if amend:
            cmd = ["commit", "--amend", "-aF", f.name]
        self.client.execute(cmd)
        os.unlink(f.name)
        if commit_date:
            del os.environ["GIT_COMMITTER_DATE"]
        if push:
            return self.push()

    def get_commit(self, branch="HEAD"):
        """ create commit object based on sha1 (not branch name) """
        commits = self.client.commits(branch)
        self.assertTrue(len(commits) > 0)
        return self.client.commit(commits[0].sha1)

    def create_commit(self, xid):
        """ create a new commit """
        # modify a file
        filename = os.path.join(self.client_path, "junk%d" % xid)
        with open(filename, "w") as f:
            f.write("this is a test (%d)" % xid)
        # commit
        self.commit("%d: %s" % (xid, self.valid_commit_message))
        # get HEAD commit (i.e., the thing we just committed)
        commit = self.get_commit()
        return commit

    def push(self):
        return self.client.execute(['push', 'origin'], stderr=subprocess.STDOUT)



class TestServer(TestBase):

    def setUp(self):
        super().setUp()
        self.repo = self.server
        self.repo_path = self.server_path

    def test_execute(self):
        out = self.repo.execute(["log"])
        logging.debug(out)

    def test_execute_error(self):
        with self.assertRaises(subprocess.CalledProcessError):
            out = self.repo.execute(["log2"], stderr=subprocess.STDOUT)

    def test_Respository__init__(self):
        with self.assertRaises(Exception):
            logging.debug(self.repo.status())
        assert self.repo.is_bare
        abs_rootdir = os.path.realpath(self.repo.rootdir)
        abs_repo_path = os.path.realpath(self.repo_path)
        assert abs_rootdir == abs_repo_path, (abs_rootdir, abs_repo_path)
        with self.assertRaises(Exception):
            self.repo.is_dirty
        commits = self.repo.commits()
        assert len(commits) == 2, commits

    def test_revision_single(self):
        commits = self.repo.commits("HEAD^..HEAD")
        assert len(commits) == 1, commits
        commits = self.repo.commits("HEAD^", "HEAD")
        assert len(commits) == 1, commits

    def test_revision_multiple(self):
        self.create_commit(2)
        commits = self.repo.commits("HEAD~2..HEAD")
        assert len(commits) == 2, commits
        commits = self.repo.commits("HEAD~2", "HEAD")
        assert len(commits) == 2, commits

    def test_commit(self):
        created = self.create_commit(2)
        commits = self.repo.commits("HEAD^", "HEAD")
        assert len(commits) == 1, commits
        fetched = commits[0]
        assert created == fetched, (created, fetched)


class TestClient(TestServer):

    def setUp(self):
        super().setUp()
        self.repo = self.client
        self.repo_path = self.client_path

    def test_Respository__init__(self):
        out = self.repo.status()
        logging.debug(out)
        assert not self.repo.is_bare
        abs_rootdir = os.path.realpath(self.repo.rootdir)
        abs_repo_path = os.path.realpath(self.repo_path)
        assert abs_rootdir == abs_repo_path, (abs_rootdir, abs_repo_path)
        assert not self.repo.is_dirty
        commits = self.repo.commits()
        assert len(commits) == 2, commits

    def test_Respository_is_dirty(self):
        out = self.repo.status()
        logging.debug(out)
        assert not self.repo.is_dirty
        self.create_commit(99)
        commits = self.repo.commits()
        assert len(commits) == 3, commits
        assert not self.repo.is_dirty
        self.repo.execute(["reset", "HEAD^"])
        commits = self.repo.commits()
        assert len(commits) == 2, commits
        assert self.repo.is_dirty


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
