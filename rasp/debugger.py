#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.machine import Load, RASP


class DebugUI:

    pass

class Debugger:


    def __init__(self, machine, ui=None, program_map=None):
        self._machine = machine
        self._ui = ui or DebugUI()
        self._map = program_map
        self._breakpoints = set()

    def set_instruction_pointer(self, address):
        self._machine.cpu.instruction_pointer = address

    def set_accumulator(self, value):
        self._machine.cpu.accumulator = value

    def set_memory(self, address, value):
        self._machine.memory.write(address, value)

    def show_cpu(self):
        view = ( self._machine.cpu.accumulator,
                 self._machine.cpu.instruction_pointer,
                 str(self._machine.next_instruction) )

        self._ui.show_cpu(view)

    def show_memory(self, start, end):
        view = []
        address = start
        while address <= end:
            value = self._machine.memory.read(address)
            opcode = self._machine.instructions.find_mnemonic(value)
            view.append((address, value, opcode))
            address += 1
        self._ui.show_memory(view)

    def show_symbol(self, symbol):
        try:
            address = self._map.find_address(symbol)
            self.show_memory(address, address+1)

        except RuntimeError as error:
            ui.report_error(error)

    def resume(self):
        while self._machine.cpu.instruction_pointer not in self._breakpoints:
            self._machine.run_one_cycle()

    def step(self):
        instruction = self._machine.next_instruction
        self._ui.show_instruction(str(instruction))
        self._machine.run_one_cycle()
        self.show_cpu()

    def set_breakpoint(self, address):
        self._breakpoints.add(address)


    @staticmethod
    def parse_command(text):
        import pyparsing as pp

        identifier = pp.Word(pp.alphas, pp.alphanums + '_')

        integer = pp.Combine(
            pp.Optional(pp.Char("-+")) + pp.Word(pp.nums)
        ).setParseAction(lambda tokens: int(tokens[0]))

        address = (
            pp.Word(pp.nums)
        ).setParseAction(lambda tokens: int(tokens[0]))

        set_ip = (
            pp.Suppress("set") + pp.Suppress("ip") + address
        ).setParseAction(lambda tokens: SetInstructionPointer(tokens[0]))

        set_acc = (
            pp.Suppress("set") + pp.Suppress("acc") + integer
        ).setParseAction(lambda tokens: SetAccumulator(tokens[0]))

        set_mem = (
            pp.Suppress("set") + pp.Suppress("mem") + address + integer
        ).setParseAction(lambda tokens: SetMemory(tokens[0], tokens[1]))

        break_at = (
            pp.Suppress("break") + address
        ).setParseAction(lambda tokens: Break(tokens[0]))

        step = (
            pp.Suppress("step")
        ).setParseAction(lambda tokens: Step())

        stop = (
            pp.Suppress("quit") | pp.Suppress("exit")
        ).setParseAction(lambda tokens: Quit())

        show_mem = (
            pp.Suppress("show") + pp.Suppress("mem") + address + address
        ).setParseAction(lambda tokens: ShowMemory(tokens[0], tokens[1]))

        show_cpu = (
            pp.Suppress("show") + pp.Suppress("cpu")
        ).setParseAction(lambda tokens: ShowCPU())

        show_symbol = (
            pp.Suppress("show") + identifier
        ).setParseAction(lambda tokens: ShowSymbol(tokens[0]))

        command = (
            set_ip | set_acc | set_mem \
            | break_at | step | stop \
            | show_mem | show_cpu | show_symbol
        )

        return command.parseString(text)[0]


class Command:

    def send_to(self, debugger):
        pass

    def is_quit(self):
        return False


class SetInstructionPointer(Command):

    def __init__(self, address):
        super().__init__()
        self._address = address

    def send_to(self, debugger):
        debugger.set_instruction_pointer(self._address)

    def __eq__(self, other):
        if not isinstance(other, SetInstructionPointer):
            return False
        return self._address == other._address


class SetAccumulator(Command):

    def __init__(self, value):
        super().__init__()
        self._value = value

    def send_to(self, debugger):
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

    def send_to(self, debugger):
        debugger.set_memory(self._address, self._value)

    def __eq__(self, other):
        if not isinstance(other, SetMemory):
            return False
        return self._address == other._address \
            and self._value == other._value


class Break(Command):

    def __init__(self, address):
        super().__init__()
        self._address = address

    def send_to(self, debugger):
        debugger.set_breakpoint(self._address)

    def __eq__(self, other):
        if not isinstance(other, Break):
            return False
        return self._address == other._address


class ShowMemory(Command):

    def __init__(self, start, end):
        self._start = start
        self._end = end

    def send_to(self, debugger):
        debugger.show_memory(self._start, self._end)

    def __eq__(self, other):
        if not isinstance(other, ShowMemory):
            return False
        return self._start == other._start \
        and self._end == self._end


class ShowSymbol(Command):

    def __init__(self, symbol):
        super().__init__()
        self._symbol = symbol

    def send_to(self, debugger):
        debugger.show_symbol(self._symbol)

    def __eq__(self, other):
        if not isinstance(other, ShowSymbol):
            return False
        return self._symbol == other._symbol


class ShowCPU(Command):

    def __init__(self):
        super().__init__()

    def send_to(self, debugger):
        debugger.show_cpu()

    def __eq__(self, other):
        return isinstance(other, ShowCPU)


class Step(Command):

    def __init__(self):
        super().__init__()

    def send_to(self, debugger):
        debugger.step()

    def __eq__(self, other):
        return isinstance(other, Step)


class Quit(Command):

    def __init__(self):
        super().__init__()

    def send_to(self, debugger):
        pass

    def is_quit(self):
        return True

    def __eq__(self, other):
        return isinstance(other, Quit)
