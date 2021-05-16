#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


class InstructionSet:

    @staticmethod
    def default():
        return InstructionSet([
            Print, Read, Load, Store, Halt, JumpIfPositive, Add, Subtract
        ])

    def __init__(self, instructions):
        self._instructions = { each.CODE: each for each in instructions }

    def find_opcode(self, mnemonic):
        for code, instruction in self._instructions.items():
            if instruction.MNEMONIC == mnemonic:
                return instruction.CODE
        raise RuntimeError("Unknown operation")

    def find_mnemonic(self, opcode):
        if opcode not in self._instructions:
            return Halt.MNEMONIC
        return self._instructions[opcode].MNEMONIC

    def read_from(self, machine):
        address = machine.cpu.instruction_pointer
        code = machine.memory.read(address)
        if code not in self._instructions:
            return Halt()
        instruction = self._instructions[code]
        return instruction.read_from(machine.memory, address)



class Instruction:

    def __init__(self, address, size=2):
        self._address = address
        self._size = size

    @property
    def size(self):
        return self._size

    def cpu_cost(self):
        return 1;

    def load_at(self, memory, address):
        memory.write(address, self.CODE)
        memory.write(address+1, self._address)

    def __eq__(self, other):
        if not isinstance(other, Instruction):
            return False
        return self.CODE == other.CODE \
            and self._address == other._address

    def send_to(self, machine):
        machine.cpu.tick(self.cpu_cost())
        self._execute(machine)

    def _execute(self, machine):
        pass

    def __str__(self):
        return f"{self.MNEMONIC} {self._address}"


class Print(Instruction):

    CODE = 1
    MNEMONIC = "print"

    @staticmethod
    def read_from(memory, address):
        operand = memory.read(address+1)
        return Print(operand)

    def __init__(self, address):
        super().__init__(address)

    def _execute(self, machine):
        value = machine.memory.read(self._address)
        machine.output_device.write(value)
        machine.cpu.instruction_pointer += self.size


class Read(Instruction):

    CODE = 2
    MNEMONIC = "read"

    @staticmethod
    def read_from(memory, address):
        operand = memory.read(address+1)
        return Read(operand)

    def __init__(self, address):
        super().__init__(address)

    def _execute(self, machine):
        value = machine.input_device.read()
        machine.memory.write(self._address, value)
        machine.cpu.instruction_pointer += self.size


class Add(Instruction):

    CODE = 3
    MNEMONIC = "add"

    @staticmethod
    def read_from(memory, address):
        operand = memory.read(address+1)
        return Add(operand)

    def __init__(self, address):
        super().__init__(address)

    def _execute(self, machine):
        operand = machine.memory.read(self._address)
        machine.cpu.accumulator += operand
        machine.cpu.instruction_pointer += self.size


class Store(Instruction):

    CODE = 4
    MNEMONIC = "store"

    @staticmethod
    def read_from(memory, address):
        operand = memory.read(address+1)
        return Store(operand)

    def __init__(self, address):
        super().__init__(address)

    def _execute(self, machine):
        machine.memory.write(self._address, machine.cpu.accumulator)
        machine.cpu.instruction_pointer += self.size


class Subtract(Instruction):

    CODE = 5
    MNEMONIC = "subtract"

    @staticmethod
    def read_from(memory, address):
        operand = memory.read(address+1)
        return Subtract(operand)

    def __init__(self, address):
        super().__init__(address)

    def _execute(self, machine):
        operand = machine.memory.read(self._address)
        machine.cpu.accumulator -= operand;
        machine.cpu.instruction_pointer += self.size


class JumpIfPositive(Instruction):

    CODE = 6
    MNEMONIC = "jump"

    @staticmethod
    def read_from(memory, address):
        operand = memory.read(address+1)
        return JumpIfPositive(operand)

    def __init__(self, address):
        super().__init__(address)

    def _execute(self, machine):
        if machine.cpu.accumulator >= 0:
            machine.cpu.instruction_pointer = self._address
        else:
            machine.cpu.instruction_pointer += self.size


class Halt(Instruction):

    CODE = 7
    MNEMONIC = "halt"

    @staticmethod
    def read_from(memory, address):
        return Halt()

    def __init__(self):
        super().__init__(-1)

    def _execute(self, machine):
        machine.halt()
        machine.cpu.instruction_pointer += self.size


class Load(Instruction):

    CODE = 8
    MNEMONIC = "load"

    @staticmethod
    def read_from(memory, address):
        operand = memory.read(address+1)
        return Load(operand)

    def __init__(self, constant):
        super().__init__(constant)

    def _execute(self, machine):
        machine.cpu.accumulator = self._address
        machine.cpu.instruction_pointer += self.size
