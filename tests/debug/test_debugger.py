#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#



from rasp.assembler import ProgramMap
from rasp.debug.controller import Break, Quit, SetAccumulator, SetMemory, \
    SetInstructionPointer, ShowCPU, ShowMemory, ShowSource, Step
from rasp.debug.core import Debugger
from rasp.instructions import Add, Halt, Load, Print, Read, Store
from rasp.machine import RASP


from tests.fakes import FakeInputDevice

from unittest import TestCase
from unittest.mock import MagicMock



class DebuggerTest(TestCase):

    def setUp(self):
        self.instructions = [
            Load(2),
            Load(3),
            Load(4),
            Load(5),
            Halt()
        ]

        self.machine = RASP()
        self.machine.memory.load_program(*self.instructions)
        self.cli = MagicMock()
        self.debugger = Debugger(self.machine, self.cli)

    def test_set_accumulator(self):
        self.debugger.set_accumulator(2)
        self.assertEqual(2, self.machine.cpu.accumulator)

    def test_set_instruction_pointer(self):
        self.debugger.set_instruction_pointer(2)
        self.assertEqual(2, self.machine.cpu.instruction_pointer)

    def test_set_memory(self):
        self.debugger.set_memory(10, 2)
        self.assertEqual(2, self.machine.memory.read(10))

    def test_run_until_breakpoint(self):
        self.debugger.set_breakpoint(4)
        self.debugger.run()
        self.assertEqual(4, self.machine.cpu.instruction_pointer)

    def test_run_until_end(self):
        self.debugger.run()
        self.assertEqual(10, self.machine.cpu.instruction_pointer)

    def test_run_from_breakpoint(self):
        self.debugger.set_breakpoint(0)
        self.debugger.set_breakpoint(4)
        self.debugger.run()
        self.assertEqual(4, self.machine.cpu.instruction_pointer)

    def test_view_memory(self):
        self.debugger.show_memory(2, 4)

        expected = [
            # address, value, is_ip, is_bp, mnemonic
            (2, 8, False, False, 'load'),
            (3, 3, False, False, 'add'),
            (4, 8, False, False, 'load')
        ]
        self.cli.show_memory.assert_called_once_with(expected)


    def test_view_memory_with_ip(self):
        self.debugger.show_memory(0, 2)

        expected = [
            # address, value, is_ip, is_bp, mnemonic
            (0, 8, True, False, 'load'),
            (1, 2, False, False, 'read'),
            (2, 8, False, False, 'load')
        ]
        self.cli.show_memory.assert_called_once_with(expected)

    def test_view_memory_with_breakpoint(self):
        self.debugger.set_breakpoint(3)

        self.debugger.show_memory(2, 4)

        expected = [
            # address, value, is_ip, is_bp, mnemonic
            (2, 8, False, False, 'load'),
            (3, 3, False, True, 'add'),
            (4, 8, False, False, 'load')
        ]
        self.cli.show_memory.assert_called_once_with(expected)

    def test_view_breakpoints(self):
        self.debugger.set_breakpoint(3)
        self.debugger.set_breakpoint(6)

        self.debugger.show_breakpoints()

        expected = [
            (3, False, 3, 'add'),
            (6, False, 8, 'load')
        ]
        self.cli.show_breakpoints.assert_called_once_with(expected)

    def test_clear_breakpoint(self):
        self.debugger.set_breakpoint(4)
        self.debugger.set_breakpoint(6)

        self.debugger.clear_breakpoint(4)

        self.debugger.show_breakpoints()
        self.cli.show_breakpoints.assert_called_once_with([
            (6, False, 8, 'load')
        ])




class WithSourceCode(TestCase):


    def setUp(self):
        program = ("segment: data\n"
                   "           value 1 0 \n"
                   "segment: code\n"
                   "   start:  read  value\n"
                   "           load  0\n"
                   "           add   value\n"
                   "           read  value\n"
                   "           add   value\n"
                   "           store value\n"
                   "           print value\n"
                   "           halt  0\n")
        debug_infos = ProgramMap.from_table([
            (4, 0, "start"),
            (5, 2, None),
            (6, 4, None),
            (7, 6, None),
            (8, 8, None),
            (9, 10, None),
            (10, 12, None),
            (11, 14, None),
            (2, 16, "value")
        ])

        self.instructions = [
            Read(16),
            Load(0),
            Add(16),
            Read(16),
            Add(16),
            Store(16),
            Print(16),
            Halt()
        ]

        self.machine = RASP(input_device=FakeInputDevice([20, 30]))
        self.machine.memory.load_program(*self.instructions)
        self.cli = MagicMock()
        self.debugger = Debugger(self.machine, self.cli, debug_infos, program)


    def test_execute_a_single_step(self):
        self.assertEqual(0, self.machine.cpu.instruction_pointer)
        self.debugger.step()
        self.assertEqual(2, self.machine.cpu.instruction_pointer)

    def test_execute_multiple_step(self):
        self.assertEqual(0, self.machine.cpu.instruction_pointer)
        self.debugger.step(3)
        self.assertEqual(2*3, self.machine.cpu.instruction_pointer)

    def test_clear_breakpoint(self):
        self.debugger.set_breakpoint_at_line(4)
        self.debugger.set_breakpoint_at_line(6)

        self.debugger.clear_breakpoint_at_line(4)

        self.debugger.show_breakpoints()
        self.cli.show_breakpoints.assert_called_once_with([
            (4, False, 3, 'add')
        ])

    def test_view_source(self):
        self.debugger.show_source(1, 10)

        # line_no, is_current, is_breakpoint, source code
        expected = [
            (1, False, False, "segment: data"),
            (2, False, False, "           value 1 0 "),
            (3, False, False, "segment: code"),
            (4, True,  False, "   start:  read  value"),
            (5, False, False, "           load  0"),
            (6, False, False, "           add   value"),
            (7, False, False, "           read  value"),
            (8, False, False, "           add   value"),
            (9, False, False, "           store value"),
            (10, False, False, "           print value")
        ]

        self.cli.show_source.assert_called_once_with(expected)

    def test_view_source_with_breakpoint(self):
        self.debugger.set_breakpoint(4)
        self.debugger.show_source(1, 10)

        # line_no, is_current, is_breakpoint, source code
        expected = [
            (1, False, False, "segment: data"),
            (2, False, False, "           value 1 0 "),
            (3, False, False, "segment: code"),
            (4, True,  False, "   start:  read  value"),
            (5, False, False, "           load  0"),
            (6, False, True, "           add   value"),
            (7, False, False, "           read  value"),
            (8, False, False, "           add   value"),
            (9, False, False, "           store value"),
            (10, False, False, "           print value")
        ]

        self.cli.show_source.assert_called_once_with(expected)


    def test_view_source_with_breakpoint_at_line(self):
        self.debugger.set_breakpoint_at_line(8)
        self.debugger.show_source(1, 10)

        # line_no, is_current, is_breakpoint, source code
        expected = [
            (1, False, False, "segment: data"),
            (2, False, False, "           value 1 0 "),
            (3, False, False, "segment: code"),
            (4, True,  False, "   start:  read  value"),
            (5, False, False, "           load  0"),
            (6, False, False, "           add   value"),
            (7, False, False, "           read  value"),
            (8, False, True, "           add   value"),
            (9, False, False, "           store value"),
            (10, False, False, "           print value")
        ]

        self.cli.show_source.assert_called_once_with(expected)
