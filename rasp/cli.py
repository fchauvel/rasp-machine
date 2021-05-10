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
        for index, (address, value, mnemonic) in enumerate(view):
            marker = "\u251C" if index < len(view) - 1 else "\u2514"
            self._format(f"       {marker}\u2500{address:>5}: {value:>5} - {mnemonic:<20}")

    def show_cpu(self, view):
        self._format(f"   \u2514\u2500 CPU:")
        self._format(f"       \u251C\u2500 ACC: {view[0]:>6}")
        self._format(f"       \u2514\u2500  IP: {view[1]:0>6} ~ {view[2]}")


    def show_instruction(self, instruction):
        self._format(f"   \u2514\u2500 RUN: {instruction}")

    def _format(self, text):
        print(" \u2502" + text)


def assemble(assembly_file):
    parser = AssemblyParser()
    with open(assembly_file, "r") as source:
        program = parser.parse(source.read())

    assembler = Assembler()
    layout = assembler.assemble(program)

    executable = Path(assembly_file).stem + ".rx"
    with open(executable, "w") as output:
        output.write(" ".join(str(each) for each in layout))


def debug(executable_file):
    machine = RASP()
    profiler = Profiler()
    machine.cpu.attach(profiler)
    machine.memory.attach(profiler)

    with open(executable_file, "r") as code:
        debug_infos = Loader().from_stream(machine.memory, code)
        debugger = Debugger(machine, CLI(), debug_infos)
        while True:
            print(" \u253C debug > ", end="")
            user_input = input()
            command = Debugger.parse_command(user_input)
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
