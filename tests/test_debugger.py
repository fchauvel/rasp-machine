#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.debugger import Break, Debugger, Quit, SetAccumulator, SetMemory, \
    SetInstructionPointer, ShowCPU, ShowMemory, ShowSource, Step
from rasp.machine import Load, RASP

from unittest import TestCase



class DebuggerTest(TestCase):

    def setUp(self):

        self.machine = RASP()
        self.machine.memory.load_program(
            Load(2),
            Load(3),
            Load(4),
            Load(5))
        self.debugger = Debugger(self.machine)

    def test_set_accumulator(self):
        self.debugger.set_accumulator(2)
        self.assertEqual(2, self.machine.cpu.accumulator)

    def test_set_instruction_pointer(self):
        self.debugger.set_instruction_pointer(2)
        self.assertEqual(2, self.machine.cpu.instruction_pointer)

    def test_set_memory(self):
        self.debugger.set_memory(10, 2)
        self.assertEqual(2, self.machine.memory.read(10))

    def test_set_breakpoint(self):
        self.debugger.set_breakpoint(4)
        self.debugger.resume()
        self.assertEqual(4, self.machine.cpu.instruction_pointer)


class CommandParserTest(TestCase):


    def verify(self, expectation, text):
        command = Debugger.parse_command(text)
        self.assertEqual(expectation, command)

    def test_set_ip(self):
        self.verify(SetInstructionPointer(25),
                    "set ip 25")

    def test_set_acc(self):
        self.verify(SetAccumulator(25),
                    "set acc 25")

    def test_set_memory(self):
        self.verify(SetMemory(25, -10),
                    "set mem 25 -10")

    def test_break(self):
        self.verify(Break(24),
                    "break 24")

    def test_step(self):
        self.verify(Step(), "step")

    def test_quit(self):
        self.verify(Quit(), "quit")

    def test_show_memory(self):
        self.verify(ShowMemory(10, 30),
                    "show mem 10 30")

    def test_show_cpu(self):
        self.verify(ShowCPU(), "show cpu")

    def test_show_source(self):
        self.verify(ShowSource(), "show source")

    def test_show_source_with_start(self):
        self.verify(ShowSource(start=12),
                    "show source 12")

    def test_show_source_with_start_and_end(self):
        self.verify(ShowSource(12, 20),
                    "show source 12 20")
