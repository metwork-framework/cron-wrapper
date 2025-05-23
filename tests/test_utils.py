# -*- coding: utf-8 -*-

from unittest import TestCase
import subprocess


class Test(TestCase):

    def test_execute1(self):
        cmd = "cronwrap --lock --load-env --low --timeout=10 sleep 1"
        output = subprocess.check_output(cmd, shell=True)
        self.assertEqual(output, b"")

    def test_execute2(self):
        cmd = "cronwrap --lock --load-env --low --timeout=1 sleep 2"
        try:
            subprocess.check_output(cmd, shell=True)
            raise Exception("CalledProcessError not raised")
        except subprocess.CalledProcessError as e:
            self.assertEqual(e.returncode, 12)
            return
