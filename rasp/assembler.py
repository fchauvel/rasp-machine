#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.assembly.ast import AssemblyProgram, Declaration, Operation
from rasp.machine import InstructionSet


class ProgramMap:

    @staticmethod
    def read_from(stream):
        program_map = ProgramMap()
        content = stream.read().splitlines()
        print(content)
        for each_line in content:
            parts = each_line.split()
            print("DBG", parts)
            if len(parts) == 3:
                program_map.record(int(parts[0]), int(parts[1]), parts[2])
            else:
                program_map.record(int(parts[0]), int(parts[1]))
        return program_map

    @staticmethod
    def create_from(program):
        program_map = ProgramMap()
        address = 0
        for each_instruction in program.code:
            program_map.record(each_instruction.location,
                               address,
                               each_instruction.label)
            address += 2
        for each_declaration in program.data:
            program_map.record(each_declaration.location,
                               address,
                               each_declaration.label)
            address += each_declaration.reserved_size
        return program_map

    @staticmethod
    def from_table(symbol_table):
        program_map = ProgramMap()
        for source, address, symbol in symbol_table:
            program_map.record(source, address, symbol)
        return program_map


    def __init__(self):
        self._addresses = {}
        self._symbols = {}

    def record(self, source, address, symbol=None):
        entry = (source, address, symbol)
        if address in self._addresses:
            raise RuntimeError(f"Duplicated address {address}!")
        self._addresses[address] = entry
        if symbol:
            if symbol in self._symbols:
                raise RuntimeError(f"Duplicated symbol {symbol}.")
            self._symbols[symbol] = entry

    def find_address_by_line(self, line_number):
        for line, address, symbol in self._addresses.values():
            if line == line_number:
                 return address
        raise RuntimeError(f"Invalid line number {line_number}")

    def find_address(self, symbol):
        if symbol not in self._symbols:
            raise RuntimeError(f"Unknown symbol '{symbol}'")
        return self._symbols[symbol][1]

    def find_source(self, address):
        if address not in self._addresses:
            raise RuntimeError(f"Unknown address '{address}'")
        return self._addresses[address][0]

    def as_table(self):
        table = [each for each in self._addresses.values()]
        return sorted(table, key=lambda entry: entry[1])


class Assembler:

    def __init__(self, instructions=None):
        self._instructions = instructions or InstructionSet.default()

    def assemble(self, program, debug=True):
        layout = []
        program_map = ProgramMap.create_from(program)

        layout.append(program.size)
        for each_operation in program.code:
            opcode = self._instructions.find_opcode(each_operation.mnemonic)
            operand = each_operation.operand
            if type(operand) == str:
                operand = program_map.find_address(operand)
            layout += [opcode, operand]

        for each_declaration in program.data:
            layout += [each_declaration.initial_value
                       for i in range(each_declaration.reserved_size)]

        if debug:
            debug_infos = program_map.as_table()
            layout.append(3 * len(debug_infos))
            for source, address, label in debug_infos:
                layout += [source, address, label or "?"]

        return layout
