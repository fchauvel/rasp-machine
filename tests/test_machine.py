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


class TestRASP(TestCase):

    def setUp(self):
        self.user = FakeInputDevice()
        self.journal = FakeOutputDevice()
        self.machine = RASP(self.user,
                            self.journal)

    def test_print_an_address(self):
        self.machine.memory.load_program(
            Print(10))
        self.machine.memory.write(10, 25)

        self.machine.run()

        self.assertEqual(25, self.journal.values[-1])

    def test_read_a_value(self):
        self.machine.memory.load_program(
            Read(10),
            Print(10))
        self.user.inputs = [34]

        self.machine.run()

        self.assertEqual(34, self.journal.values[-1])

    def test_add_two_values(self):
        self.machine.memory.load_program(
            Read(50),
            Read(51),
            Add(50),
            Add(51),
            Store(52),
            Print(52))
        self.user.inputs = [34, 27]

        self.machine.run()

        self.assertEqual(34 + 27, self.journal.values[-1])

    def test_add_three_values(self):
        self.machine.memory.load_program(
            Read(50),
            Read(51),
            Read(52),
            Add(50),
            Add(51),
            Add(52),
            Store(53),
            Print(53))
        self.user.inputs = [34, 27, 11]

        self.machine.run()

        self.assertEqual(34 + 27 + 11, self.journal.values[-1])


    def test_subtract_two_values(self):
        self.machine.memory.load_program(
            Read(50),
            Read(51),
            Add(50),
            Subtract(51),
            Store(52),
            Print(52))

        self.user.inputs = [34, 27]

        self.machine.run()

        self.assertEqual(34 - 27, self.journal.values[-1])


    def test_jump_if_positive(self):
        self.machine.memory.load_program(
            Read(50),
            Read(51),
            Add(50),
            JumpIfPositive(2*5),
            Print(50),
            Print(51))
        self.user.inputs = [34, 27]

        self.machine.run()

        self.assertEqual(1, len(self.journal.values))


    def test_halt(self):
        self.machine.memory.load_program(
            Read(50),
            Read(51),
            Halt(),
            Print(50),
            Print(51))
        self.user.inputs = [34, 27]

        self.machine.run()

        self.assertEqual(0, len(self.journal.values))


    def test_load(self):
        self.machine.memory.load_program(
            Load(122),
            Store(51),
            Print(51))

        self.user.inputs = [34, 27]

        self.machine.run()

        self.assertEqual(122, self.journal.values[0])
