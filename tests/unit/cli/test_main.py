"""
Tests for the main.py file.
"""
import os
import sys
import tempfile
import unittest
from argparse import ArgumentParser
from unittest.mock import patch

import pytest

from TTiP.cli import main


# pylint: disable=attribute-defined-outside-init
class TestGetArgParser(unittest.TestCase):
    """
    Class for testing the get_argparser method.
    """

    def setUp(self):
        """
        Create an argparser to test.
        """
        self.ap = main.get_argparser()

    def test_returntype(self):
        """
        Test that get_argparser returns an ArgumentParser
        """
        self.assertIsInstance(self.ap, ArgumentParser)

    def test_parsing_debug_off(self):
        """
        Test returned parser with default debug option.
        """
        args = self.ap.parse_args(['test'])
        self.assertEqual(args.debug, False)

    def test_parsing_debug_on(self):
        """
        Test returned parser with debug arg.
        """
        args = self.ap.parse_args(['-d', 'test'])
        self.assertEqual(args.debug, True)

    def test_parsing_config(self):
        """
        Test returned parser with config file.
        """
        args = self.ap.parse_args(['test'])
        self.assertEqual(args.config, 'test')

    def test_multiple_config(self):
        """
        Test returned parser with 2 config files.
        """
        with self.assertRaises(SystemExit):
            _ = self.ap.parse_args(['test', 'test2'])


class TestRun(unittest.TestCase):
    """
    Class for testing the run method.
    Note this will not test the results, that will be done in regression tests.
    """

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, capsys):
        """
        Utility function for allowing checking the logs using pytest.

        Args:
            caplog (pytest fixture): The pytest fixture to copy to self.
        """
        self._capsys = capsys

    def setUp(self):
        """
        Set up a temp directory and cd into it to keep workspace clean.
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.problems_dir = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, 'mock_problems')

        self.wd = os.getcwd()
        os.chdir(self.temp_dir.name)

        self.args = ()
        self.kwargs = {}

    def tearDown(self):
        """
        cd back to original working directory and cleanup the temp directory.
        """
        os.chdir(self.wd)
        self.temp_dir.cleanup()

    def capture_args(self, *args, **kwargs):
        """
        Capture arguments from a mocked out function.
        """
        self.args = args
        self.kwargs = kwargs

    def test_generates_files(self):
        """
        Test that run generates the expected files for a given config file.
        """
        with patch.object(main.Solver, 'solve', self.capture_args):
            main.run(os.path.join(self.problems_dir,
                                  'be_box_nosource_steady.ini'))

        self.assertDictEqual(
            {'file_path': './mock_results/be_box_nosource_steady.pvd'},
            self.kwargs)

    def test_logging_debug_off(self):
        """
        Test that the logging output is only reporting info with debug off.
        """
        with patch.object(main.Solver, 'solve', self.capture_args):
            main.run(os.path.join(self.problems_dir,
                                  'be_box_nosource_steady.ini'))
        out, _ = self._capsys.readouterr()
        self.assertNotIn('Building', out)
        self.assertIn('Running', out)
        self.assertIn('Success', out)

    def test_logging_debug_on(self):
        """
        Test that the logging output is reporting all messages with debug on.
        """
        with patch.object(main.Solver, 'solve', self.capture_args):
            main.run(os.path.join(self.problems_dir,
                                  'be_box_nosource_steady.ini'),
                     debug=True)
        out, _ = self._capsys.readouterr()
        self.assertIn('Building', out)
        self.assertIn('Running', out)
        self.assertIn('Success', out)


class TestMain(unittest.TestCase):
    """
    Class for testing the main method.
    """

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, capsys):
        """
        Utility function for allowing checking the logs using pytest.

        Args:
            caplog (pytest fixture): The pytest fixture to copy to self.
        """
        self._capsys = capsys

    def test_no_args(self):
        """
        Test that main returns help with no args and exits.
        """
        testargs = ['prog']
        with patch.object(sys, 'argv', testargs):
            with self.assertRaises(SystemExit):
                main.main()
        out, _ = self._capsys.readouterr()
        self.assertIn('usage', out)

    def test_with_args(self):
        """
        Test that main passes the correct args into run.
        """
        testargs = ['prog', '-d', 'some_conf.ini']
        with patch.object(sys, 'argv', testargs):
            with patch.object(main, 'run', self.stash_args):
                main.main()
        self.assertEqual(len(self.stashed_args), 2)
        self.assertIn(True, self.stashed_args)
        self.assertIn('some_conf.ini', self.stashed_args)

    def stash_args(self, *args, **kwargs):
        """
        Utility function to store args in self.
        Used to replace a function in main.
        """
        self.stashed_args = list(args) + list(kwargs.values())
