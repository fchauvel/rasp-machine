#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.machine import Memory
from rasp.executable import Loader

from unittest import TestCase


class TestLoader(TestCase):

    def setUp(self):
        self._load = Loader()
        self.memory = Memory()

    def load(self, text):
        return self._load.from_text(self.memory, text)

    def verify_memory_is(self, *cells):
        for address, value in enumerate(cells):
            self.assertEqual(value, self.memory.read(address))

    def test_only_memory_layout(self):
        debug_infos = self.load("3 12 13 14")

        self.verify_memory_is(12, 13, 14)
        self.assertIsNone(debug_infos)

    def test_debug_infos_with_label(self):
        debug_infos = self.load("1 23 1 10 0 label")

        self.assertEqual(23, self.memory.read(0))
        self.assertIsNotNone(debug_infos)
        self.assertEqual(0, debug_infos.find_address("label"))

    def test_debug_infos_without_label(self):
        debug_infos = self.load("1 23 1 10 0 ?")

        self.assertEqual(23, self.memory.read(0))
        self.assertIsNotNone(debug_infos)
        self.assertEqual(10, debug_infos.find_source(0))

    def test_invalid_content(self):
        with self.assertRaises(RuntimeError):
            self._load.from_text(self.memory, "2 XX 14")
