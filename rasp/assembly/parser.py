#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.assembly.ast import AssemblyProgram, Declaration, Operation


class AssemblyParser:


    @staticmethod
    def read_file(assembly_file):
        parser = AssemblyParser()
        with open(assembly_file, "r") as source:
            return parser.parse(source.read())


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
