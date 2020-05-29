"""
Tests for the gen_conf.py file.
"""

import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from TTiP.cli.gen_conf import gen_conf


class TestGenConf(TestCase):
    """
    Tests for the gen_conf method.
    """

    def setUp(self):
        """
        Create a new temporary directory to test the creation of files within.
        """
        self.dir = TemporaryDirectory()

        self.old_dir = os.getcwd()
        os.chdir(self.dir.name)

    def tearDown(self):
        os.chdir(self.old_dir)
        self.dir.cleanup()

    def test_empty_dir(self):
        """
        Test that the function creates a new file if the dir is empty.
        """
        gen_conf()
        self.assertTrue(os.path.exists('new_conf.ini'))

    def test_non_empty_dir(self):
        """
        Test that calling multiple times in a row creates expected files.
        """
        gen_conf()
        self.assertTrue(os.path.exists('new_conf.ini'))

        gen_conf()
        self.assertTrue(os.path.exists('new_conf1.ini'))
        gen_conf()
        self.assertTrue(os.path.exists('new_conf2.ini'))

        os.remove('new_conf1.ini')
        gen_conf()
        self.assertTrue(os.path.exists('new_conf1.ini'))
