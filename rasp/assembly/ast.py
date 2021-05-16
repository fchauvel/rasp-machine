#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#




class Declaration:

    def __init__(self, label, size=1, initial_value=0, location=None):
        self.label = label
        self.reserved_size = size
        self.initial_value = initial_value
        self.location = location

    def __eq__(self, other):
        if not isinstance(other, Declaration):
            return False
        return self.label == other.label \
            and self.reserved_size == other.reserved_size \
            and self.initial_value == other.initial_value

    def __str__(self):
        return f"{self.label} {self.reserved_size} {self.initial_value}"

    def __repr__(self):
        return f"Declaration({self.label} {self.reserved_size} {self.initial_value})"


class Operation:

    def __init__(self, mnemonic, operand, label=None, location=None):
        self.mnemonic = mnemonic
        self.operand = operand
        self.label = label
        self.location = location

    def __eq__(self, other):
        if not isinstance(other, Operation):
            return False
        print(type(self.mnemonic), type(other.mnemonic))
        print(type(self.operand), type(other.operand))
        print(self.label, other.label)
        result = self.mnemonic == other.mnemonic \
            and self.operand == other.operand \
            and self.label == other.label
        print(result)
        return result

    def __repr__(self):
        return f"Operation({self.mnemonic}, {self.operand}, {self.label})"


class AssemblyProgram:

    def __init__(self, data, code):
        self.code = code
        self.data = data

    @property
    def size(self):
        return 2 * len(self.code) + sum(variable.reserved_size
                                        for variable in self.data)

    def __eq__(self, other):
        if not isinstance(other, AssemblyProgram):
            return False
        return self.data == other.data \
            and self.code == other.code

    def __repr__(self):
        return repr(self.__dict__)
