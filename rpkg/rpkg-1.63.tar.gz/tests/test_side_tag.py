# -*- coding: utf-8 -*-

import logging
import os

import koji
import mock
import pyrpkg.cli
import six
from six.moves import StringIO, configparser

from utils import CommandTestCase

if six.PY2:
    ConfigParser = configparser.SafeConfigParser
else:
    # The SafeConfigParser class has been renamed to ConfigParser in Python 3.2.
    ConfigParser = configparser.ConfigParser


class BaseCase(CommandTestCase):
    def new_cli(self, args):
        config = ConfigParser()
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        config.read(os.path.join(fixtures_dir, "rpkg.conf"))

        client = pyrpkg.cli.cliClient(config, name="rpkg")
        client.setupLogging(pyrpkg.log)
        pyrpkg.log.setLevel(logging.CRITICAL)
        client.do_imports()
        cmd = ["rpkg", "--path", self.cloned_repo_path] + args
        with mock.patch("sys.argv", new=cmd):
            client.parse_cmdline()

        client.cmd._kojisession = mock.Mock()

        return client


class RequestSideTagTestCase(BaseCase):
    def test_guess_base_tag(self):
        cli = self.new_cli(["request-side-tag"])
        cli.cmd._kojisession.getBuildTarget.return_value = {"build_tag_name": "base"}
        cli.cmd._kojisession.createSideTag.return_value = {"name": "side", "id": 123}
        with mock.patch("sys.stdout", new_callable=StringIO) as mock_out:
            cli.request_side_tag()

        output = mock_out.getvalue()
        self.assertIn("Side tag 'side' (id 123) created.", output)
        self.assertIn("Use 'rpkg build --target=side' to use it.", output)

        self.assertEqual(
            cli.cmd._kojisession.createSideTag.call_args_list, [mock.call("base")]
        )
        self.assertEqual(
            cli.cmd._kojisession.getBuildTarget.call_args_list,
            [mock.call(cli.cmd.target)],
        )

    def test_explicit_base_tag(self):
        cli = self.new_cli(["request-side-tag", "--base-tag=f30-build"])
        cli.cmd._kojisession.createSideTag.return_value = {"name": "side", "id": 123}
        with mock.patch("sys.stdout", new_callable=StringIO) as mock_out:
            cli.request_side_tag()

        output = mock_out.getvalue()
        self.assertIn("Side tag 'side' (id 123) created.", output)
        self.assertIn("Use 'rpkg build --target=side' to use it.", output)

        self.assertEqual(
            cli.cmd._kojisession.createSideTag.call_args_list, [mock.call("f30-build")]
        )

    def test_failure(self):
        def raise_error(*args, **kwargs):
            raise koji.GenericError("a problem")

        cli = self.new_cli(["request-side-tag", "--base-tag=foobar"])
        cli.cmd._kojisession.createSideTag.side_effect = raise_error

        with self.assertRaises(Exception) as ctx:
            cli.request_side_tag()

        self.assertIn("a problem", str(ctx.exception))

    def test_suffix(self):
        cli = self.new_cli(
            ["request-side-tag", "--base-tag=f30-build", "--suffix=stack-gate"]
        )
        cli.cmd._kojisession.createSideTag.return_value = {"name": "side", "id": 123}
        with mock.patch("sys.stdout", new_callable=StringIO) as mock_out:
            cli.request_side_tag()

        output = mock_out.getvalue()
        self.assertIn("Side tag 'side' (id 123) created.", output)
        self.assertIn("Use 'rpkg build --target=side' to use it.", output)

        self.assertEqual(
            cli.cmd._kojisession.createSideTag.call_args_list,
            [mock.call("f30-build", suffix="stack-gate")],
        )


class ListSideTagTestCase(BaseCase):
    def test_list_all(self):
        cli = self.new_cli(["list-side-tags"])
        cli.cmd._kojisession.listSideTags.return_value = [
            dict(name="f31-build-side-456", id=1, user_name="packager10", user_id="10"),
            dict(name="f30-build-side-1", id=2, user_name="packager11", user_id="11"),
        ]
        with mock.patch("sys.stdout", new_callable=StringIO) as mock_out:
            cli.list_side_tags()

        self.assertEqual(
            cli.cmd._kojisession.listSideTags.call_args_list,
            [mock.call(basetag=None, user=None)],
        )

        self.assertEqual(
            mock_out.getvalue(),
            "f30-build-side-1\t(id 2)\t(user packager11|11)\n"
            "f31-build-side-456\t(id 1)\t(user packager10|10)\n",
        )

    def list_for_base_tag(self):
        cli = self.new_cli(["list-side-tags", "--base-tag=f30-build"])
        cli.cmd._kojisession.listSideTags.return_value = [
            dict(name="f30-build-side-456", id=1)
        ]
        cli.list_side_tags()

        self.assertEqual(
            cli.cmd._kojisession.listSideTags.call_args_list,
            [mock.call(basetag="f30-build", user=None)],
        )

    def list_mine(self):
        cli = self.new_cli(["list-side-tags", "--mine"])
        cli.user = "devel"
        cli.cmd._kojisession.listSideTags.return_value = [
            dict(name="f30-build-side-456", id=1)
        ]
        cli.list_side_tags()

        self.assertEqual(
            cli.cmd._kojisession.listSideTags.call_args_list,
            [mock.call(basetag=None, user="devel")],
        )

    def list_for_user(self):
        cli = self.new_cli(["list-side-tags", "--user=jdoe"])
        cli.cmd._kojisession.listSideTags.return_value = [
            dict(name="f30-build-side-456", id=1)
        ]
        cli.list_side_tags()

        self.assertEqual(
            cli.cmd._kojisession.listSideTags.call_args_list,
            [mock.call(basetag=None, user="jdoe")],
        )


class RemoveSideTagTestCase(BaseCase):
    def test_success_remove(self):
        cli = self.new_cli(["remove-side-tag", "f30-build-side-123"])
        cli.remove_side_tag()
        self.assertEqual(
            cli.cmd._kojisession.removeSideTag.call_args_list,
            [mock.call("f30-build-side-123")],
        )

    def test_fail_to_remove(self):
        def raise_error(*args, **kwargs):
            raise koji.GenericError("a problem")

        cli = self.new_cli(["remove-side-tag", "f30-build-side-123"])
        cli.cmd._kojisession.removeSideTag.side_effect = raise_error
        with self.assertRaises(Exception) as ctx:
            cli.remove_side_tag()

        self.assertIn("a problem", str(ctx.exception))
