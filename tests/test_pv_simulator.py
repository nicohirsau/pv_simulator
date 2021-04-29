#!/usr/bin/env python

"""Tests for `pv_simulator` package."""


import unittest
from click.testing import CliRunner

from pv_simulator import pv_simulator
from pv_simulator import cli


class TestPv_simulator(unittest.TestCase):
    """Tests for `pv_simulator` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'pv_simulator.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
