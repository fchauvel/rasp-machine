#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.instructions import Load
from rasp.machine import RASP


class Debugger:

    def __init__(self, machine, view, program_map=None, assembly_code=None):
        self._machine = machine
        self._ui = view
        self._map = program_map
        self._assembly_code = assembly_code.splitlines() if assembly_code else None
        self._breakpoints = set()

    def set_instruction_pointer(self, address):
        self._machine.cpu.instruction_pointer = address

    def set_accumulator(self, value):
        self._machine.cpu.accumulator = value

    def set_memory(self, address, value):
        self._machine.memory.write(address, value)

    def show_breakpoints(self):
        infos = []
        for any_address in self._breakpoints:
            value = self._machine.memory.read(any_address)
            mnemonic = self._machine.instructions.find_mnemonic(value)
            infos.append((
                any_address,
                any_address == self._machine.cpu.instruction_pointer,
                value,
                mnemonic
            ))
        self._ui.show_breakpoints(infos)

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
            is_ip = address == self._machine.cpu.instruction_pointer
            is_bp = address in self._breakpoints
            view.append((address, value, is_ip, is_bp, opcode))
            address += 1
        self._ui.show_memory(view)

    def show_source(self, start, end):
        if not self._assembly_code:
            ui.no_source_code()

        else:
            current_location = self._map.find_source(self._machine.cpu.instruction_pointer)
            if start is None and end is None:
                start = max(1, current_location - 5)
                end = start + 10
            elif end is None:
                end = start + 10

            fragment = []
            for each_line in range(start, end+1):
                is_current = each_line == current_location

                is_breakpoint = False
                try:
                    address = self._map.find_address_by_line(each_line)
                    is_breakpoint = address in self._breakpoints
                except RuntimeError:
                    pass
                fragment.append(
                    (each_line, is_current, is_breakpoint, self._assembly_code[each_line-1])
                )

            self._ui.show_source(fragment)


    def show_symbol(self, symbol):
        try:
            address = self._map.find_address(symbol)
            self.show_memory(address, address+1)

        except RuntimeError as error:
            self._ui.report_error(error)

    def run(self):
        while True:
            self._execute_one_instruction()
            if self._machine.is_stopped or self._at_break_point:
                break
        self.show_cpu()

    def _execute_one_instruction(self):
        instruction = self._machine.next_instruction
        print(str(instruction))
        self._ui.show_instruction(str(instruction))
        self._machine.run_one_cycle()

    def step(self, step_count=1):
        for each_step in range(step_count):
            self._execute_one_instruction()
            self.show_cpu()
            if self._at_break_point or self._machine.is_stopped:
                break
        current_line_number = self._map.find_source(self._machine.cpu.instruction_pointer)
        self.show_source(current_line_number-1, current_line_number+1)

    @property
    def _at_break_point(self):
        return self._machine.cpu.instruction_pointer in self._breakpoints

    def set_breakpoint(self, address):
        self._breakpoints.add(address)


    def set_breakpoint_at_line(self, line_number):
        if not self._assembly_code:
            self._ui.report_error("Error: Assembly code is not available.")
        address = self._map.find_address_by_line(line_number)
        self.set_breakpoint(address)

    def clear_breakpoint(self, address):
        self._breakpoints.remove(address)


    def clear_breakpoint_at_line(self, line_number):
        if not self._assembly_code:
            self._ui.report_error("Error: Assembly code is not available")
        address = self._map.find_address_by_line(line_number)
        self.clear_breakpoint(address)
