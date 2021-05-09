#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.machine import InstructionSet



class Declaration(object):

    def __init__(self, label, size=1, initial_value=0):
        self.label = label
        self.reserved_size = size
        self.initial_value = initial_value

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

    def __init__(self, mnemonic, operand, label=None):
        self.mnemonic = mnemonic
        self.operand = operand
        self.label = label

    @property
    def is_labelled(self):
        return self.label is not None

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

    def __eq__(self, other):
        if not isinstance(other, AssemblyProgram):
            return False
        return self.data == other.data \
            and self.code == other.code

    def __repr__(self):
        return repr(self.__dict__)


class Symbol:

    def __init__(self, label, address):
        self.label = label
        self.address = address


class Assembler:

    def __init__(self, instructions=None):
        self._instructions = instructions or InstructionSet.default()
        self._symbol_table = {}

    def assemble(self, program):
        layout = []

        self._generate_symbol_table(program)

        for each_operation in program.code:
            opcode = self._instructions.find_opcode(each_operation.mnemonic)
            operand = each_operation.operand
            if type(operand) == str:
                operand = self._find_address(program, operand)
            layout += [opcode, operand]

        for each_declaration in program.data:
            layout += [each_declaration.initial_value
                       for i in range(each_declaration.reserved_size)]

        return layout

    def _generate_symbol_table(self, program):
        self._symbol_table = {}

        offset = 0
        for index, instruction in enumerate(program.code):
            if instruction.is_labelled:
                label = instruction.label
                if label in self._symbol_table:
                    raise RuntimeError(f"Duplicated label '{label}'")
                self._symbol_table[label] = Symbol(label, address=2*index)
            offset += 2

        for each_declaration in program.data:
            label = each_declaration.label
            if each_declaration.label in self._symbol_table:
                raise RuntimeError(f"Duplicated variable name '{label}'.")
            self._symbol_table[label] = Symbol(label, offset)
            offset += each_declaration.reserved_size


    def _find_address(self, program, symbol):
        if symbol not in self._symbol_table:
            message = (
                f"Error: Unknown symbol '{symbol}'!\n"
                f"Candidates are: {self._symbol_table.keys()}\n"
            )
            raise RuntimeError(message)
        return self._symbol_table[symbol].address


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


    def _build_declaration(self, tokens):
        return Declaration(tokens[0], tokens[1], tokens[2])

    def _build_operation(self, tokens):
        if len(tokens) == 3:
            return Operation(tokens[1], tokens[2], tokens[0])
        else:
            return Operation(tokens[0], tokens[1])

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
