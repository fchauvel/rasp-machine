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

from pathlib import Path

from sys import argv


class Controller:

    ASSEMBLE = 1
    DEBUG = 2
    EXECUTE = 3
    VERSION = 4

    def __init__(self):
        self._assembler = Assembler()
        self._load = Loader()
        self._assembly = AssemblyParser

    def assemble(self, assembly_file):
        program = self._assembly.read_file(assembly_file)

        executable = self._assembler.assemble(program)

        self._load.save_as(executable,
                           Path(assembly_file).with_suffix(".rx"))


    def debug(self, executable_file):
        assembly_file = Path(executable_file).with_suffix(".asm")
        with open(assembly_file, "r") as assembly:
            assembly_code = assembly.read()

        view = DebugView()
        machine = RASP(input_device=view, output_device=view)
        debug_infos = self._load.from_file(machine.memory, executable_file)
        debugger = Debugger(machine, view, debug_infos, assembly_code)
        session = DebugController(debugger, view)
        session.start()


    def execute(self, executable_file):
        machine = RASP()
        profiler = Profiler()
        machine.cpu.attach(profiler)
        machine.memory.attach(profiler)
        with open(executable_file, "r") as code:
            self._load.from_stream(machine.memory, code)
            machine.run()
        print("---")
        print(f"Time: {profiler.cycle_count} cycle(s)")
        print(f"Memory: {profiler.used_memory} cell(s)")


    def version(self):
        print(f"{About.NAME} {About.VERSION} -- {About.DESCRIPTION}")
        print(f"{About.COPYRIGHT}")
        print(f"{About.LICENSE} license")



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
    assembler.add_argument("assembly_file",
                           metavar="FILE",
                           help="The RASP assembly file to compile to machine code")
    assembler.set_defaults(command=Controller.ASSEMBLE)

    debugger = subparsers.add_parser("debug",
                                     help='starts the interactive debugger')

    debugger.add_argument("executable_file",
                           metavar="FILE",
                           help="The RASP executable file to compile to debug")
    debugger.set_defaults(command=Controller.DEBUG)

    runner = subparsers.add_parser("execute",
                                   help='execute the given RASP executable file')
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
        rasp.assemble(arguments.assembly_file)

    elif arguments.command == Controller.EXECUTE:
        rasp.execute(arguments.executable_file)

    elif arguments.command == Controller.DEBUG:
        rasp.debug(arguments.executable_file)

    elif arguments.command == Controller.VERSION:
        rasp.version()
