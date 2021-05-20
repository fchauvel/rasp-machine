#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


import logging

from rasp import About
from rasp.assembly.parser import AssemblyParser
from rasp.assembler import Assembler, ProgramMap
from rasp.debug.controller import DebugController
from rasp.debug.core import Debugger
from rasp.debug.view import DebugView
from rasp.executable import Loader
from rasp.machine import RASP, Profiler

from pyparsing import ParseException
from pathlib import Path

from sys import argv



class Presenter:

    def syntax_error(self, error):
        print(f"Syntax Error.")

    def source_code_loaded_from(self, source):
        print(f"Assembly code loaded from '{source}'.")

    def missing_source_code(self):
        print("Warning: Unable to locate the assembly source code.")
        print(" - Assembly symbols and line number will not be available.")

    def executable_created(self, executable_file):
        print(f"Machine code written in '{executable_file}'.")

    def executable_not_found(self, executable_file):
        print(f"Error: Could not open '{executable_file}'")

    def execution_failed(self, executable_file):
        print(f"Error: Could not read '{executable_file}'")
        print(f" - Use 'rasp assemble source.asm' to get an RASP executable file.")

    def source_not_found(self, source_file):
        print(f"Error: Could not open assembly file '{source_file}'")

    def version(self):
        print(f"{About.NAME} {About.VERSION} -- {About.DESCRIPTION}")
        print(f"{About.COPYRIGHT}")
        print(f"{About.LICENSE} license")



class Controller:

    ASSEMBLE = 1
    DEBUG = 2
    EXECUTE = 3
    VERSION = 4

    def __init__(self):
        self._present = Presenter()
        self._assembler = Assembler()
        self._load = Loader()
        self._assembly = AssemblyParser


    def assemble(self, assembly_file, include_debug, output_file):
        try:
            program = self._assembly.read_file(assembly_file)

        except ParseException as error:
            self._present.syntax_error(error)

        except FileNotFoundError as error:
            self._present.source_not_found(assembly_file)

        try:
            executable = self._assembler.assemble(program, include_debug)
            output = Path(assembly_file).with_suffix(".rx")
            if output_file:
                output = Path(output_file)
            self._load.save_as(executable, output)
            self._present.executable_created(str(output))

        except FileNotFoundError as error:
            self._present.executable_not_found(str(output))



    def debug(self, executable_file, source_file=None):
        source_code = self._load_source_code(executable_file, source_file)
        try:
            view = DebugView()
            machine = RASP(input_device=view, output_device=view)
            debug_infos = self._load.from_file(machine.memory, executable_file)
            debugger = Debugger(machine, view, debug_infos, source_code)
            session = DebugController(debugger, view)
            session.start()

        except FileNotFoundError as error:
            self._present.executable_not_found(executable_file)


    def _load_source_code(self, executable_file, source_file):
        source = Path(executable_file).with_suffix(".asm")
        if source_file:
            source = Path(source_file)

        try:
            assembly_file = source
            with open(assembly_file, "r") as assembly:
                self._present.source_code_loaded_from(str(source))
                return  assembly.read()

        except FileNotFoundError as error:
            self._present.missing_source_code()


    def execute(self, executable_file, use_profiler=False):
        machine = RASP()
        if use_profiler:
            profiler = Profiler()
            machine.cpu.attach(profiler)
            machine.memory.attach(profiler)

        try:
            with open(executable_file, "r") as code:
                self._load.from_stream(machine.memory, code)
                machine.run()
                if use_profiler:
                    data_file = Path(executable_file).with_suffix(".perf")
                    profiler.save_results_as(data_file)
                return 0

        except FileNotFoundError as error:
            self._present.executable_not_found(executable_file)
            logger.error(error)

        except Exception as error:
            self._present.execution_failed(executable_file)
            logger.error(error)


    def version(self):
        self._present.version()



def parse_arguments(command_line):
    from argparse import ArgumentParser

    parser = ArgumentParser(
        prog=About.CLI_PROGRAM,
        description=About.DESCRIPTION)

    subparsers = parser.add_subparsers(title="Available commands")
    assembler = subparsers.add_parser("assemble",
                                      help="assemble RASP programs into an executable")
    assembler.add_argument("--debug", "-d",
                           help="Inline debugging information into the executable",
                           action="store_true")
    assembler.add_argument("--output", "-o",
                           metavar="EXE_FILE",
                           help="Name of the executable file to generate")
    assembler.add_argument("assembly_file",
                           metavar="FILE",
                           help="The RASP assembly file to compile to machine code")
    assembler.set_defaults(command=Controller.ASSEMBLE)

    debugger = subparsers.add_parser("debug",
                                     help='starts the interactive debugger')
    debugger.add_argument("--asm-source", "-s",
                          metavar="ASM_FILE",
                          help="Assembly source code associated with the executable")
    debugger.add_argument("executable_file",
                           metavar="FILE",
                           help="The RASP executable file to compile to debug")
    debugger.set_defaults(command=Controller.DEBUG)

    runner = subparsers.add_parser("execute",
                                   help='execute the given RASP executable file')
    runner.add_argument("--use-profiler", "-p",
                           help="Profile the CPU & memory usage of the program",
                           action="store_true")
    runner.add_argument("executable_file",
                           metavar="FILE",
                           help="The RASP executable file to compile to debug")
    runner.set_defaults(command=Controller.EXECUTE)

    about = subparsers.add_parser("version",
                                  help="show version, license and other details")
    about.set_defaults(command=Controller.VERSION)

    return parser.parse_args(command_line)


def main():
    from sys import argv

    logging.basicConfig(filename='rasp.log', level=logging.INFO)

    rasp = Controller()
    arguments = parse_arguments(argv[1:])

    if arguments.command == Controller.ASSEMBLE:
        rasp.assemble(arguments.assembly_file,
                      arguments.debug,
                      arguments.output)

    elif arguments.command == Controller.EXECUTE:
        rasp.execute(arguments.executable_file,
                     arguments.use_profiler)

    elif arguments.command == Controller.DEBUG:
        rasp.debug(arguments.executable_file,
                   arguments.asm_source)

    elif arguments.command == Controller.VERSION:
        rasp.version()
