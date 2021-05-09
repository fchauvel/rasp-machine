#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.debugger import Break, Debugger, Quit, SetAccumulator, SetMemory, \
    SetInstructionPointer, ShowCPU, ShowMemory, Step
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

    def test_set_ip(self):
        command = Debugger.parse_command("set ip 25")
        self.assertEqual(SetInstructionPointer(25), command)

    def test_set_acc(self):
        command = Debugger.parse_command("set acc 25")
        self.assertEqual(SetAccumulator(25), command)

    def test_set_memory(self):
        command = Debugger.parse_command("set mem 25 -10")
        self.assertEqual(SetMemory(25, -10), command)

    def test_break(self):
        command = Debugger.parse_command("break 24")
        self.assertEqual(Break(24), command)

    def test_step(self):
        command = Debugger.parse_command("step")
        self.assertEqual(Step(), command)

    def test_quit(self):
        command = Debugger.parse_command("quit")
        self.assertEqual(Quit(), command)

    def test_show_memory(self):
        command = Debugger.parse_command("show mem 10 30")
        self.assertEqual(ShowMemory(10, 30), command)

    def test_show_cpu(self):
        command = Debugger.parse_command("show cpu")
        self.assertEqual(ShowCPU(), command)
