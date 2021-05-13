#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.machine import InstructionSet



class Declaration:

    def __init__(self, label, size=1, initial_value=0, location=None):
        self.label = label
        self.reserved_size = size
        self.initial_value = initial_value
        self.location = location

    def __eq__(self, other):
        if not isinstance(other, Declaration):
            return False
        return self.label == other.label \
            and self.reserved_size == other.reserved_size \
            and self.initial_value == other.initial_value

    def __str__(self):
        return f"{self.label} {self.reserved_size} {self.initial_value}"

    def __repr__(self):
        return f"Declaration({self.label} {self.reserved_size} {self.initial_value})"


class Operation:

    def __init__(self, mnemonic, operand, label=None, location=None):
        self.mnemonic = mnemonic
        self.operand = operand
        self.label = label
        self.location = location

    def __eq__(self, other):
        if not isinstance(other, Operation):
            return False
        print(type(self.mnemonic), type(other.mnemonic))
        print(type(self.operand), type(other.operand))
        print(self.label, other.label)
        result = self.mnemonic == other.mnemonic \
            and self.operand == other.operand \
            and self.label == other.label
        print(result)
        return result

    def __repr__(self):
        return f"Operation({self.mnemonic}, {self.operand}, {self.label})"


class AssemblyProgram:

    def __init__(self, data, code):
        self.code = code
        self.data = data

    @property
    def size(self):
        return 2 * len(self.code) + sum(variable.reserved_size
                                        for variable in self.data)

    def __eq__(self, other):
        if not isinstance(other, AssemblyProgram):
            return False
        return self.data == other.data \
            and self.code == other.code

    def __repr__(self):
        return repr(self.__dict__)


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


class AssemblyParser:

    def __init__(self):
        pass


    def parse(self, text):
        import pyparsing as pp

        comments = pp.Suppress(";") + pp.restOfLine()

        identifier = pp.Word(pp.alphas, pp.alphanums + '_')

        integer = pp.Combine(pp.Optional(pp.Char("-+")) + pp.Word(pp.nums))\
                    .setParseAction(lambda t: int(t[0]))

        declaration = (
            identifier + integer + integer
        ).setParseAction(self._build_declaration)

        data_segment = (
            pp.Suppress("segment") + pp.Suppress(":") + pp.Literal("data") \
            + pp.Group(pp.OneOrMore(declaration))
        )

        mnemonic = pp.oneOf(("halt", "load", "store", "jump", "read",
                             "print", "add", "subtract"))

        operation = (
            pp.Optional(identifier + pp.Suppress(":")) + (mnemonic + (identifier | integer))
        ).setParseAction(self._build_operation)

        code_segment = (
            pp.Suppress("segment") + pp.Suppress(":") + pp.Literal("code")  \
            + pp.Group(pp.OneOrMore(operation))
        )

        program = (
            data_segment + code_segment | data_segment | code_segment
        ).setParseAction(self._build_program)

        program.ignore(comments)

        return program.parseString(text)[0]


    def _build_declaration(self, source, position, tokens):
        line_number = len(source[0:position+1].splitlines())
        return Declaration(tokens[0], tokens[1], tokens[2], location=line_number)


    def _build_operation(self, source, position, tokens):
        line_number = len(source[0:position+1].splitlines())
        if len(tokens) == 3:
            return Operation(tokens[1], tokens[2], tokens[0], location=line_number)
        else:
            return Operation(tokens[0], tokens[1], location=line_number)


    def _build_program(self, tokens):
        data = []
        code = []
        for index in range(len(tokens)):
            if tokens[index] == "data":
                data = tokens[index+1].asList()
            elif tokens[index] == "code":
                code = tokens[index+1].asList()
        return AssemblyProgram(data=data,
                               code=code)
