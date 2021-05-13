#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


import logging

from rasp.debugger import Debugger
from rasp.assembler import Assembler, AssemblyParser, ProgramMap
from rasp.loader import Loader
from rasp.machine import RASP, Profiler

from pathlib import Path

from sys import argv


class CLI:

    def show_memory(self, view):
        self._format(f"   \u2514\u2500 Memory:")
        for index, (address, value, is_current, is_breakpoint, mnemonic) in enumerate(view):
            marker = "\u251C" if index < len(view) - 1 else "\u2514"
            break_point = "(b)" if is_breakpoint else "   "
            current = ">>>" if is_current else "   "
            self._format(f"       {marker}\u2500 {current} {break_point} {address:>5}: {value:>5} {mnemonic:<20}")

    def show_breakpoints(self, infos):
        self._format(f"   \u2514\u2500 Breakpoints:")
        for address, is_current, value, mnemonic in infos:
            current = ">>>" if is_current else "   "
            self._format(f"       \u2514\u2500 {current} {address:>5}: {value:>5} {mnemonic:<20}")

    def show_cpu(self, view):
        self._format(f"   \u2514\u2500 CPU:")
        self._format(f"       \u251C\u2500 ACC: {view[0]:>6}")
        self._format(f"       \u2514\u2500  IP: {view[1]:0>6} ~ {view[2]}")

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


def assemble(assembly_file):
    parser = AssemblyParser()
    with open(assembly_file, "r") as source:
        program = parser.parse(source.read())

    assembler = Assembler()
    layout = assembler.assemble(program)

    executable = Path(assembly_file).with_suffix(".rx")
    with open(executable, "w") as output:
        output.write(" ".join(str(each) for each in layout))


def debug(executable_file):

    assembly_file = Path(executable_file).with_suffix(".asm")
    with open(assembly_file, "r") as assembly:
        source_code = assembly.read()

    with open(executable_file, "r") as code:
        cli = CLI()
        machine = RASP(input_device=cli, output_device=cli)
        profiler = Profiler()
        machine.cpu.attach(profiler)
        machine.memory.attach(profiler)
        debug_infos = Loader().from_stream(machine.memory, code)

        debugger = Debugger(machine, cli, debug_infos, source_code)
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



def execute(executable_file):
    machine = RASP()
    profiler = Profiler()
    machine.cpu.attach(profiler)
    machine.memory.attach(profiler)
    with open(executable_file, "r") as code:
        load = Loader()
        load.from_stream(machine.memory, code)
        machine.run()
    print("---")
    print(f"Time: {profiler.cycle_count} cycle(s)")
    print(f"Memory: {profiler.used_memory} cell(s)")


def main():
    from sys import argv

    logging.basicConfig(filename='rasp.log', level=logging.INFO)

    command = argv[1]
    if command == "assemble":
        assemble(argv[2])
    elif command == "execute":
        execute(argv[2])
    elif command == "debug":
        debug(argv[2])
