#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ecs_dns` package."""

import pytest
from click.testing import CliRunner

from ecs_dns import _cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()

    # test no args
    result = runner.invoke(_cli.main)
    assert result.exit_code == 0
    assert "ecs_dns._cli.main" in result.output

    # test help command
    help_result = runner.invoke(_cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
