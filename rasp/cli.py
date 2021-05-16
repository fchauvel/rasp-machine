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
from rasp.debugger import Debugger
from rasp.assembly.parser import AssemblyParser
from rasp.assembler import Assembler, ProgramMap
from rasp.executable import Loader
from rasp.machine import RASP, Profiler

from pathlib import Path

from sys import argv


class CLI:

    def show_opening(self):
        print(f"{About.NAME} {About.VERSION}")
        print(f"{About.COPYRIGHT}")
        print()


    def show_closing(self):
        print("That's all folks!")


    def show_memory(self, view):
        self._format(f"   \u2514\u2500 Memory:")
        for index, (address, value, is_current, is_breakpoint, mnemonic) in enumerate(view):
            marker = "\u251C" if index < len(view) - 1 else "\u2514"
            break_point = "(b)" if is_breakpoint else "   "
            current = ">>>" if is_current else "   "
            self._format(f"       {marker}\u2500 {current} {break_point} {address:>5}: {value:>5} {mnemonic:<20}")

    def show_breakpoints(self, infos):
        items = []
        for address, is_current, value, mnemonic in infos:
            current = ">>>" if is_current else "   "
            items.append(f"{current} {address:>5}: {value:>5} {mnemonic:<20}")
        self._format_list("Breakpoints", items)
#
    def _format_list(self, title, items):
        if not items:
            self._format(f"   \u2514\u2500 {title}: None")
        else:
            self._format(f"   \u2514\u2500 {title}:")
            for index, item in enumerate(items):
                if index < len(items) - 1:
                    self._format(f"       \u251C\u2500 {item}")
                else:
                    self._format(f"       \u2514\u2500 {item}")


    def show_cpu(self, view):
        self._format_list("CPU:", [
            f"ACC: {view[0]:>6}",
            f" IP: {view[1]:0>6} ~ {view[2]}"
        ])

    def show_source(self, code_fragment):
        self._format(f"   \u2514\u2500 Assembly Code:")
        for line_number, is_current, is_breakpoint, code in code_fragment:
            current = ">>>" if is_current else "   "
            bp = "(b)" if is_breakpoint else "   "
            self._format(f"       \u251C\u2500 {line_number:0>3}: {current} {bp} {code}")

    def no_source_code(self):
        self._format(f"   \u2514\u2500 Assembly code is not available.")
        self._format(f"       \u2514\u2500 Did you assemble with the '--debug' flag?")

    def show_instruction(self, instruction):
        self._format(f"   \u2514\u2500 RUN: {instruction}")

    def invalid_command(self, command):
        self._format(f"   \u2514\u2500 Invalid command '{command}'.")

    def _format(self, text, end="\n"):
        print(" \u2502" + text, end=end)

    def report_error(self, error):
        self._format(f"   \u2514\u2500 Error: {str(error)}.")

    def read(self):
        self._format(f"      \u2514\u2500 Input? ", end="")
        user_input = input()
        return int(user_input)

    def write(self, value):
        self._format(f"   \u2514\u2500 Output: {value}")


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
            source_code = assembly.read()

        cli = CLI()
        machine = RASP(input_device=cli, output_device=cli)
        profiler = Profiler()
        machine.cpu.attach(profiler)
        machine.memory.attach(profiler)
        debug_infos = self._load.from_file(machine.memory, executable_file)

        debugger = Debugger(machine, cli, debug_infos, source_code)
        cli.show_opening()
        while True:
            print(" \u253C debug > ", end="")
            user_input = input()
            try:
                command = Debugger.parse_command(user_input)
            except Exception:
                cli.invalid_command(user_input)
                continue
            if command.is_quit():
                break
            command.send_to(debugger)
        cli.show_closing()


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
