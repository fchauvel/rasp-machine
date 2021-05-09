#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#



from rasp.assembler import Assembler, AssemblyParser, AssemblyProgram, Declaration, \
    Operation
from rasp.machine import Add, Halt, Load, Print, Read, Store

from unittest import TestCase



class AssemblyCodeParsingTests(TestCase):


    def test_single_declaration(self):
        parser = AssemblyParser()

        program = parser.parse("segment: data\n"
                               "   my_variable 1  123\n"
                               "   another 2 0\n" )

        expected = AssemblyProgram(
            data=[
                Declaration("my_variable", 1, 123),
                Declaration("another", 2, 0)
            ],
            code=[]
        )
        self.assertEqual(expected, program)


    def test_single_code_segment(self):
        parser = AssemblyParser()

        program = parser.parse("segment: code\n"
                               "   load 0\n"
                               "   add 25\n" )

        expected = AssemblyProgram(
            data=[],
            code=[
                Operation("load", 0),
                Operation("add", 25)
            ]
        )
        self.assertEqual(expected, program)

    def test_single_negative_integers(self):
        parser = AssemblyParser()

        program = parser.parse("segment: code\n"
                               "          load  -12\n")

        expected = AssemblyProgram(
            data=[],
            code=[
                Operation("load", -12)
            ]
        )
        self.assertEqual(expected, program)


    def test_single_code_segment_with_label(self):
        parser = AssemblyParser()

        program = parser.parse("segment: code\n"
                               "          load  0\n"
                               "   start: add   25\n" )

        expected = AssemblyProgram(
            data=[],
            code=[
                Operation("load", 0),
                Operation("add", 25, "start")
            ]
        )
        self.assertEqual(expected, program)


    def test_single_code_segment_with_reference(self):
        parser = AssemblyParser()

        program = parser.parse("segment: code\n"
                               "          load  variable\n"
                               "   start: add   25\n" )

        expected = AssemblyProgram(
            data=[],
            code=[
                Operation("load", "variable"),
                Operation("add", 25, "start")
            ]
        )
        self.assertEqual(expected, program)


    def test_both_code_and_data_segment(self):
        parser = AssemblyParser()

        program = parser.parse("segment: data\n"
                               "   variable 1 123\n"
                               "   another 2 0\n"
                               "\n"
                               ";; Here comes the code segment\n"
                               "segment: code\n"
                               "          load  variable ;; load variable\n"
                               "   start: add   25\n" )

        expected = AssemblyProgram(
            data=[
                Declaration("variable", 1, 123),
                Declaration("another", 2, 0)
            ],
            code=[
                Operation("load", "variable"),
                Operation("add", 25, "start")
            ]
        )
        self.assertEqual(expected, program)



class AssemblerTests(TestCase):

    def setUp(self):
        self.assembler = Assembler()


    def test_using_declared_variable(self):
        program = AssemblyProgram(
            data=[
                Declaration("my_variable", 1, 23)
            ],
            code=[
                Operation("add", "my_variable")
            ]
        )

        layout = self.assembler.assemble(program)

        self.assertEqual(2 * 1 + 1, len(layout))
        self.assertEqual(2 * 1, layout[1])


    def test_using_undeclared_variable(self):
        program = AssemblyProgram(
            data=[
                Declaration("my_variable", 1, 23)
            ],
            code=[
                Operation("add", "undeclared_variable")
            ]
        )

        with self.assertRaises(RuntimeError):
            self.assembler.assemble(program)


    def test_using_unknown_mnemonic(self):
        program = AssemblyProgram(
            data=[
                Declaration("my_variable", 1, 23)
            ],
            code=[
                Operation("unknown", "my_variable")
            ]
        )

        with self.assertRaises(RuntimeError):
            self.assembler.assemble(program)

    def test_jumping_to_a_unknown_label(self):
        program = AssemblyProgram(
            data=[],
            code=[
                Operation("jump", "nowehere"),
                Operation("load", 0),
                Operation("add", 10, label="destination")
            ]
        )

        with self.assertRaises(RuntimeError):
            layout = self.assembler.assemble(program)

    def test_jumping_to_label(self):
        program = AssemblyProgram(
            data=[],
            code=[
                Operation("jump", "destination"),
                Operation("load", 0),
                Operation("add", 10, label="destination")
            ]
        )

        layout = self.assembler.assemble(program)

        self.assertEqual(2 * 3, len(layout))
        self.assertEqual(4, layout[1])


    def test_without_label(self):
        program = AssemblyProgram(
            data=[],
            code=[
                Operation("read", 10),
                Operation("load", 0)
            ]
        )

        layout = self.assembler.assemble(program)

        self.assertEqual(2 * 2, len(layout))
        self.assertEqual(Read.CODE, layout[0])
        self.assertEqual(10, layout[1])
        self.assertEqual(Load.CODE, layout[2])
        self.assertEqual(0, layout[3])



class EndToEndTests(TestCase):

    def test_parse_assemble_dump(self):
        assembly_code = ("segment: data\n"
                         "    value 1 10\n"
                         "    result 2 20\n"
                         "segment: code\n"
                         "    start:   load   0\n"
                         "             read   value\n"
                         "             add    value\n"
                         "             read   value\n"
                         "             add    value\n"
                         "             store  result\n"
                         "             print  result\n"
                         "             halt   0\n")


        parser = AssemblyParser()
        program = parser.parse(assembly_code)

        assembler = Assembler()
        layout = assembler.assemble(program)

        expected = [ Load.CODE, 0,
                     Read.CODE, 16,
                     Add.CODE, 16,
                     Read.CODE, 16,
                     Add.CODE, 16,
                     Store.CODE, 17,
                     Print.CODE, 17,
                     Halt.CODE, 0,
                     10, 20, 20]
        self.assertEqual(expected, layout)
