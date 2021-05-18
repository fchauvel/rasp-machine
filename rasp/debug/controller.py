#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#



from rasp.debug.view import DebugView
from rasp.debug.core import Debugger
from rasp.machine import RASP

import pyparsing as pp



class DebugController:


    def __init__(self, debugger, view):
        self._debugger = debugger
        self._view = view


    def start(self):
        self._view.show_opening()
        while True:
            user_input = self._view.request_input()
            try:
                command = self._parse_command(user_input)
            except Exception:
                self._view.invalid_command(user_input)
                continue
            if command.is_quit():
                break
            command.send_to(self._debugger, self._view)
        self._view.show_closing()


    @staticmethod
    def _parse_command(text):
        identifier = pp.Word(pp.alphas, pp.alphanums + '_')

        integer = pp.Combine(
            pp.Optional(pp.Char("-+")) + pp.Word(pp.nums)
        ).setParseAction(lambda tokens: int(tokens[0]))

        address = (
            pp.Word(pp.nums)
        ).setParseAction(lambda tokens: int(tokens[0]))

        set_ip = (
            pp.Suppress("set") + pp.Suppress("ip")  +  address
        ).setParseAction(lambda tokens: SetInstructionPointer(tokens[0]))

        set_acc = (
            pp.Suppress("set") + pp.Suppress("acc") + integer
        ).setParseAction(lambda tokens: SetAccumulator(tokens[0]))

        set_mem = (
            pp.Suppress("set") + pp.Suppress("memory") + address + integer
        ).setParseAction(lambda tokens: SetMemory(tokens[0], tokens[1]))

        break_at = (
            pp.Suppress("break") + pp.Suppress("at") + pp.oneOf(["line", "address"]) + address
        ).setParseAction(lambda tokens: Break(tokens[1], tokens[0] == "line"))

        clear = (
            pp.Suppress("clear") + pp.oneOf(["line", "address"]) + address
        ).setParseAction(lambda tokens: Clear(tokens[1], tokens[0] == "line"))

        step = (
            pp.Suppress("step") + pp.Optional(integer)
        ).setParseAction(lambda tokens: Step(*tokens))

        run = (
            pp.Suppress("run") | pp.Suppress("continue")
        ).setParseAction(lambda tokens: Run())

        stop = (
            pp.Suppress("quit") | pp.Suppress("exit")
        ).setParseAction(lambda tokens: Quit())

        show_mem = (
            pp.Suppress("show") + pp.Suppress("memory") + address + address
        ).setParseAction(lambda tokens: ShowMemory(tokens[0], tokens[1]))

        show_breakpoints = (
            pp.Suppress("show") + pp.Suppress("breakpoints")
        ).setParseAction(lambda tokens: ShowBreakpoints())

        show_cpu = (
            pp.Suppress("show") + pp.Suppress("cpu")
        ).setParseAction(lambda tokens: ShowCPU())

        show_source = (
            pp.Suppress("show") + pp.Suppress("source") + pp.Optional(integer) + pp.Optional(integer)
        ).setParseAction(lambda tokens: ShowSource(*tokens))

        show_symbol = (
            pp.Suppress("show") + identifier
        ).setParseAction(lambda tokens: ShowSymbol(tokens[0]))

        help_me = (
            pp.Suppress("help")
        ).setParseAction(lambda tokens: Help())

        command = (
            set_ip | set_acc | set_mem \
            | help_me \
            | break_at | clear | step | stop | run \
            | show_mem | show_cpu | show_source | show_breakpoints | show_symbol

        )

        return command.parseString(text)[0]


class Command:

    def send_to(self, debugger, view):
        pass

    def is_quit(self):
        return False


class Help(Command):

    def __init__(self):
        super().__init__()

    def send_to(self, debugger, view):
        view.show_help()

    def __eq__(self, other):
        return isinstance(_other, Help)


class SetInstructionPointer(Command):

    def __init__(self, address):
        super().__init__()
        self._address = address

    def send_to(self, debugger, view):
        debugger.set_instruction_pointer(self._address)

    def __eq__(self, other):
        if not isinstance(other, SetInstructionPointer):
            return False
        return self._address == other._address


class SetAccumulator(Command):

    def __init__(self, value):
        super().__init__()
        self._value = value

    def send_to(self, debugger, view):
        debugger.set_accumulator(self._value)

    def __eq__(self, other):
        if not isinstance(other, SetAccumulator):
            return False
        return self._value == other._value


class SetMemory(Command):

    def __init__(self, address, value):
        super().__init__()
        self._address = address
        self._value = value

    def send_to(self, debugger, view):
        debugger.set_memory(self._address, self._value)

    def __eq__(self, other):
        if not isinstance(other, SetMemory):
            return False
        return self._address == other._address \
            and self._value == other._value


class Break(Command):

    def __init__(self, address, is_line_number=False):
        super().__init__()
        self._address = address
        self._is_line_number = is_line_number

    def send_to(self, debugger, view):
        if self._is_line_number:
            debugger.set_breakpoint_at_line(self._address)
        else:
            debugger.set_breakpoint(self._address)

    def __eq__(self, other):
        if not isinstance(other, Break):
            return False
        return self._address == other._address \
            and self._is_line_number == other._is_line_number


class Clear(Command):

    def __init__(self, address, is_line_number=False):
        self._address = address
        self._is_line_number = is_line_number

    def send_to(self, debugger, view):
        if self._is_line_number:
            debugger.clear_breakpoint_at_line(self._address)
        else:
            debugger.clear_breakpoint(self._address)

    def __eq__(self, other):
        if not isinstance(other, Clear):
            return False
        return self._address == other._address \
            and self._is_line_number == other._is_line_number


class ShowMemory(Command):

    def __init__(self, start, end):
        self._start = start
        self._end = end

    def send_to(self, debugger, view):
        debugger.show_memory(self._start, self._end)

    def __eq__(self, other):
        if not isinstance(other, ShowMemory):
            return False
        return self._start == other._start \
        and self._end == self._end


class ShowSource(Command):

    def __init__(self, start=None, end=None):
        self._start = start
        self._end = end

    def send_to(self, debugger, view):
        debugger.show_source(self._start, self._end)

    def __eq__(self, other):
        if not isinstance(other, ShowSource):
            return False
        return self._start == other._start \
            and self._end == other._end


class ShowSymbol(Command):

    def __init__(self, symbol):
        super().__init__()
        self._symbol = symbol

    def send_to(self, debugger, view):
        debugger.show_symbol(self._symbol)

    def __eq__(self, other):
        if not isinstance(other, ShowSymbol):
            return False
        return self._symbol == other._symbol


class ShowBreakpoints(Command):

    def __init__(self):
        super().__init__()

    def send_to(self, debugger, view):
        debugger.show_breakpoints()

    def __eq__(self, other):
        return isinstance(other, ShowBreakpoints)


class ShowCPU(Command):

    def __init__(self):
        super().__init__()

    def send_to(self, debugger, view):
        debugger.show_cpu()

    def __eq__(self, other):
        return isinstance(other, ShowCPU)


class Step(Command):

    def __init__(self, step_count=None):
        super().__init__()
        self._step_count = step_count or 1

    def send_to(self, debugger, view):
        debugger.step(self._step_count)

    def __eq__(self, other):
        return isinstance(other, Step)


class Quit(Command):

    def __init__(self):
        super().__init__()

    def send_to(self, debugger, view):
        pass

    def is_quit(self):
        return True

    def __eq__(self, other):
        return isinstance(other, Quit)


class Run(Command):

    def __init__(self):
        super().__init__()

    def send_to(self, debugger, view):
        debugger.run()

    def __eq__(self, other):
        return isinstance(other, Run)
