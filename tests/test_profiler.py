#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.instructions import Print, Halt, Read, Load, Add, Subtract, JumpIfPositive, Store
from rasp.machine import RASP, Profiler

from tests.fakes import FakeInputDevice, FakeOutputDevice

from unittest import TestCase


class TheProfileShould(TestCase):

    def setUp(self):
        self.user = FakeInputDevice()
        self.journal = FakeOutputDevice()
        self.machine = RASP(self.user,
                            self.journal)
        self.profiler = Profiler()
        self.machine.memory.attach(self.profiler)
        self.machine.cpu.attach(self.profiler)

        self.machine.memory.load_program(
            Load(5),             # 01.
            Store(50),           # 02. max := 5
            Load(0),             # 03.
            Store(51),           # 04. counter := 0
            Load(0),             # 05. while counter < max
            Add(51),             # 06.
            Subtract(50),        # 07.
            JumpIfPositive(28),  # 08. do:
            Print(51),           # 09.    print counter
            Load(1),             # 10.
            Add(51),             # 11.
            Store(51),           # 12.   counter += 1
            Load(0),             # 13.
            JumpIfPositive(8),   # 14. done
            Halt()               # 15.
        )

    def test_totals(self):
        self.machine.run()

        self.assertEqual(15 * 2 + 2, self.profiler.used_memory)
        self.assertEqual(4 + 6 * 4 + 5 * 6 + 1 , self.profiler.cycle_count)


    def test_instructions_coverage(self):

        self.machine.run()

        expected = [ (0, 1), (2, 1), (4, 1), (6, 1), (8, 6), (10, 6),
                     (12, 6), (14, 6), (16, 5), (18, 5), (20, 5),
                     (22,5), (24, 5), (26, 5), (28, 1) ]

        self.assertEqual(expected, self.profiler.instruction_coverage)


    def test_memory_coverage(self):

        self.machine.run()

        # addr, read, write
        expected = [
            (0, 1, 1), (1, 1, 1), (2, 1, 1), (3, 1, 1), (4, 1, 1), (5, 1, 1), (6, 1, 1),
            (7, 1, 1), (8, 6, 1), (9, 6, 1), (10, 6, 1),
            (11, 6, 1), (12, 6, 1), (13, 6, 1), (14, 6, 1), (15, 6, 1), (16, 5, 1),
            (17, 5, 1), (18, 5, 1), (19, 5, 1), (20, 5, 1), (21, 5, 1), (22, 5, 1),
            (23, 5, 1), (24, 5, 1), (25, 5, 1), (26, 5, 1), (27, 5, 1), (28, 1, 1),
            (29, 0, 1), (50, 6, 1), (51, 16, 6)
        ]

        self.assertEqual(expected, self.profiler.memory_coverage)
