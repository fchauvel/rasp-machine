#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.machine import Memory
from rasp.loader import Loader

from unittest import TestCase



class TestLoader(TestCase):

    def test_valid_content(self):
        load = Loader()
        memory = Memory()

        load.from_text(memory, "12 13 14")

        self.assertEqual(12, memory.read(0))
        self.assertEqual(13, memory.read(1))
        self.assertEqual(14, memory.read(2))

    def test_invalid_content(self):
        load = Loader()
        memory = Memory()

        with self.assertRaises(RuntimeError):
            load.from_text(memory, "12 XX 14")
