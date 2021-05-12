import logging


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


class Parser:

    def __init__(self):
        self._factory = {
            "PRINT": lambda address: Print(address),
            "LOAD": lambda constant: Load(constant),
            "JUMP": lambda address: JumpIfPositive(address),
            "HALT": lambda argument: Halt(),
            "STORE": lambda address: Store(address),
            "ADD": lambda address: Add(address),
            "SUBTRACT": lambda address: Subtract(address),
            "READ": lambda address: Read(address)
        }


    def parse(self, text):
        program = []
        for each_line in text.split("\n"):
            if not each_line:
                continue
            content = each_line.split(";", 1)
            if content[0].strip():
                parts = content[0].split()
                operation = parts[0]
                argument = 0
                if len(parts) == 2:
                    argument = int(parts[1])
                if operation.upper() in self._factory:
                    instruction = self._factory[operation.upper()](argument)
                    program.append(instruction)
                else:
                    raise RuntimeError(f"Unknown operation '{operation}'")

        return program
