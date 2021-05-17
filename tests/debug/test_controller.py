#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.debug.controller import Break, DebugController, Quit, SetAccumulator, SetMemory, \
    SetInstructionPointer, ShowCPU, ShowMemory, ShowSource, Step

from unittest import TestCase



class CommandParserTest(TestCase):


    def verify(self, expectation, text):
        command = DebugController._parse_command(text)
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
                    "break at address 24")

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
