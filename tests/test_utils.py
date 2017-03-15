# -*- coding: utf-8 -*-

from unittest import TestCase
from datetime import datetime, timedelta
from cronwrapper.cronwrap import total_seconds, Lock


class TestUtils(TestCase):

    def test_total_seconds(self):
        before = datetime.now()
        after = datetime.now() + timedelta(hours=2)
        delta = after - before
        self.assertEquals(round(total_seconds(delta), 3), 7200)

    def test_lock(self):
        lock = Lock("foo")
        self.assertTrue(lock.acquire())
        lock.release()
        lock = Lock("foo")
        self.assertTrue(lock.acquire())
        lock.release()
