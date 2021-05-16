#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


import logging


from rasp.instructions import InstructionSet



class Memory:

    def __init__(self, capacity=1000):
        self._cells = [0 for each in range(capacity)]
        self._observers = []

    def attach(self, profiler):
        self._observers.append(profiler)

    def load_program(self, *instructions):
        for index, each_instruction in enumerate(instructions):
            each_instruction.load_at(self, index*2)

    def write(self, address, value):
        self._cells[address] = value
        for each_observer in self._observers:
            each_observer.on_write(address, value)

    def read(self, address):
        return self._cells[address]


class CPU:

    def __init__(self, accumulator=0, instruction_pointer=0):
        self.accumulator = accumulator
        self.instruction_pointer = instruction_pointer
        self._observers = []

    def attach(self, profiler):
        self._observers.append(profiler)

    def tick(self, count):
        for each_observer in self._observers:
            each_observer.on_new_cpu_cycle(count)

    def __str__(self):
        return f"[ACC={self.accumulator} IP={self.instruction_pointer}]"


class InputDevice:

    def read(self):
        print("rasp? ", end="")
        user_input = input()
        return int(user_input)


class OutputDevice:

    def write(self, value):
        print(value)





class RASP:

    def __init__(self, input_device=None, output_device=None):
        self.memory = Memory()
        self.cpu = CPU()
        self.input_device = input_device or InputDevice()
        self.output_device = output_device or OutputDevice()
        self.instructions = InstructionSet.default()
        self._is_running = True

    def run(self):
        self._is_running = True
        while self._is_running:
            self.run_one_cycle()

    def run_one_cycle(self):
        instruction = self.instructions.read_from(self)
        logging.debug(f"{instruction} {self.cpu}")
        instruction.send_to(self)

    @property
    def next_instruction(self):
        return self.instructions.read_from(self)

    def halt(self):
        self._is_running = False

    @property
    def is_stopped(self):
        return not self._is_running


class Profiler:

    def __init__(self):
        self._used_memory_cells = set();
        self._cpu_cycle = 0

    @property
    def used_memory(self):
        return len(self._used_memory_cells);

    def on_write(self, address, value):
        self._used_memory_cells.add(address)

    def on_new_cpu_cycle(self, count=1):
        self._cpu_cycle += count

    @property
    def cycle_count(self):
        return self._cpu_cycle
