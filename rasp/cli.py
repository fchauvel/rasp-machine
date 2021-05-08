#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


import logging

from rasp.assembler import Assembler, AssemblyParser
from rasp.loader import Loader
from rasp.machine import RASP, Profiler

from pathlib import Path

from sys import argv



def assemble(assembly_file):
    parser = AssemblyParser()
    with open(assembly_file, "r") as source:
        program = parser.parse(source.read())

    assembler = Assembler()
    layout = assembler.assemble(program)

    executable = Path(assembly_file).stem + ".rx"
    with open(executable, "w") as output:
        output.write(" ".join(str(each) for each in layout))



def execute(executable_file):
    load = Loader()
    machine = RASP()
    profiler = Profiler()
    machine.cpu.attach(profiler)
    machine.memory.attach(profiler)
    with open(executable_file, "r") as code:
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
