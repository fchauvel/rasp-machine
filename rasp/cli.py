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
from rasp.assembler import Assembler, AssemblyParser
from rasp.loader import Loader
from rasp.machine import RASP, Profiler

from pathlib import Path

from sys import argv


class CLI:

    def show_memory(self, view):
        headers = ("address:", "as value", "as instruction")

        print(f"{headers[0]:>10} {headers[1]:>10} {headers[2]:>20}")
        for address, value, mnemonic in view:
            print(f"{address:>10}: {value:>10} {mnemonic:>20}")


    def show_cpu(self, view):
        self._format(f"- CPU:")
        self._format(f"   - ACC: {view[0]:>6}")
        self._format(f"   -  IP: {view[1]:0>6} ~ {view[2]}")


    def show_instruction(self, instruction):
        self._format(f"- RUN: {instruction}")

    def _format(self, text):
        print(" | " + text)


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
    debugger = Debugger(machine, CLI())
    with open(executable_file, "r") as code:
        load = Loader()
        load.from_stream(machine.memory, code)
        while True:
            print(" + debug > ", end="")
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
