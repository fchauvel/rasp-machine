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
        value = self._cells[address]
        for each_observer in self._observers:
            each_observer.on_read(address, value)
        return value


class CPU:

    def __init__(self, accumulator=0, instruction_pointer=0):
        self.accumulator = accumulator
        self.instruction_pointer = instruction_pointer
        self._observers = []

    def attach(self, profiler):
        self._observers.append(profiler)

    def tick(self, count):
        for each_observer in self._observers:
            each_observer.on_new_cpu_cycle(count, self.instruction_pointer)

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
        self._memory = {}

    @property
    def used_memory(self):
        return sum(min(1, each[2])for each in self._memory.values())

    @property
    def cycle_count(self):
        return sum(each[3] for each in self._memory.values())

    def on_read(self, address, value):
        self._record(address, +1, 0, 0)

    def on_write(self, address, value):
        self._record(address, 0, +1, 0)

    def on_new_cpu_cycle(self, count=1, ip=0):
        self._record(ip, 0, 0, +1)

    def _record(self, address, new_reads, new_writes, new_executions):
        if not address in self._memory:
            self._memory[address] = (address, 0, 0, 0)
        address, reads, writes, executions = self._memory[address]
        self._memory[address] = (address,
                                 reads + new_reads,
                                 writes + new_writes,
                                 executions + new_executions)
    @property
    def instruction_coverage(self):
        results = [ (address, executions)
                    for address, reads, writes, executions in self._memory.values()
                    if executions > 0]
        return sorted(results, key=lambda i: i[0])

    @property
    def memory_coverage(self):
        results = [ (address, reads, writes)
                    for address, reads, writes, executions in self._memory.values() ]
        return sorted(results, key=lambda i: i[0])


    def save_results_as(self, file_name):
        with open(file_name, "w") as destination:
            destination.write("address, reads, writes, executions\n")
            for address, reads, writes, runs in self._as_table():
                destination.write(f"{address},{reads},{writes},{runs}\n")

    def _as_table(self):
        return sorted(self._memory.values(), key=lambda t: t[0])
