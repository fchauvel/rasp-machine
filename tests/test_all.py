#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.machine import RASP, Print, Halt, Read, Load, Add, Subtract, JumpIfPositive, Store, \
    Profiler, Parser

from tests.fakes import FakeInputDevice, FakeOutputDevice

from unittest import TestCase


class TestRASP(TestCase):

    def setUp(self):
        self.user = FakeInputDevice()
        self.journal = FakeOutputDevice()
        self.machine = RASP(self.user,
                            self.journal)

    def test_profiler(self):
        profiler = Profiler()
        self.machine.memory.attach(profiler)
        self.machine.cpu.attach(profiler)

        self.machine.memory.load_program(
            Load(45),
            JumpIfPositive(4*2),
            Print(50),
            Store(50),
            Print(50),
            Halt()
        )
        self.machine.memory.write(50, 25)

        self.machine.run()

        self.assertEqual(1, len(self.journal.values))
        self.assertEqual(6 * 2 + 1, profiler.used_memory)
        self.assertEqual(4, profiler.cycle_count)

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



class TestParser(TestCase):

    def setUp(self):
        self.parser = Parser()

    def test_parse_print(self):
        program = self.parser.parse("PRINT 23")

        self.assertEqual(1, len(program))
        self.assertEqual(Print(23), program[0])

    def test_parse_load(self):
        parser = Parser()

        program = self.parser.parse("LOAD 100\n"
                               "PRINT 34\n")

        self.assertEqual(2, len(program))
        self.assertEqual(Load(100), program[0])

    def test_parse_command_with_comment(self):
        program = self.parser.parse("LOAD 100 ; this is a dummy comment!\n"
                                    "PRINT 34\n")

        self.assertEqual(2, len(program))
        self.assertEqual(Load(100), program[0])

    def test_parse_commented_line(self):
        program = self.parser.parse("LOAD 100 ; this is a dummy comment!\n"
                                    "PRINT 34\n"
                                    ";;LOAD 50\n ; this line is out")

        self.assertEqual(2, len(program))
        self.assertEqual(Load(100), program[0])

    def test_parse_jump(self):
        program = self.parser.parse("JUMP 100\n"
                                    "PRINT 34\n")

        self.assertEqual(2, len(program))
        self.assertEqual(JumpIfPositive(100), program[0])

    def test_parse_halt(self):
        program = self.parser.parse("HALT\n"
                                    "PRINT 34\n")

        self.assertEqual(2, len(program))
        self.assertEqual(Halt(), program[0])


    def test_parse_store(self):
        program = self.parser.parse("STORE 234\n"
                                    "PRINT 34\n")

        self.assertEqual(2, len(program))
        self.assertEqual(Store(234), program[0])

    def test_parse_add(self):
        program = self.parser.parse("ADD 234\n"
                                    "PRINT 34\n")

        self.assertEqual(2, len(program))
        self.assertEqual(Add(234), program[0])

    def test_parse_subtract(self):
        program = self.parser.parse("SUBTRACT 234\n"
                                    "PRINT 34\n")

        self.assertEqual(2, len(program))
        self.assertEqual(Subtract(234), program[0])

    def test_parse_read(self):
        program = self.parser.parse("READ 234\n"
                                    "PRINT 34\n")

        self.assertEqual(2, len(program))
        self.assertEqual(Read(234), program[0])

    def test_parse_lowercase(self):
        program = self.parser.parse("read 234\n"
                                    "print 34\n")

        self.assertEqual(2, len(program))
        self.assertEqual(Read(234), program[0])
