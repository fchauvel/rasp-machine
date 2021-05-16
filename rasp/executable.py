#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.assembler import ProgramMap

from io import StringIO


class Loader:

    NO_LABEL = "?"


    def from_file(self, memory, file_name):
        with open(file_name, "r") as file_stream:
            return self.from_stream(memory, file_stream)


    def from_text(self, memory, text):
        return self.from_stream(memory, StringIO(text))

    def from_stream(self, memory, stream):
        content = stream.read().split()
        code_length = int(content[0])
        address = 0
        for any_cell in content[1:code_length+1]:
            if any_cell:
                try:
                    memory.write(address, int(any_cell))
                    address += 1
                except ValueError as error:
                    raise RuntimeError(f"Unable to read Cell {address}: "
                                       f"Expected an integer, but found {any_cell}")

        index = code_length + 1
        if len(content) <= code_length + 1:
            return None
        return self._read_debug_infos(content[code_length+1:])


    def _read_debug_infos(self, content):
        debug_infos = ProgramMap()
        count = int(content[0])
        index = 1
        while index < len(content):
            line_number = int(content[index])
            memory_address = int(content[index + 1])
            label = content[index + 2]
            if label == self.NO_LABEL:
                label = None
            debug_infos.record(line_number, memory_address, label)
            index += 3
        return debug_infos


    @staticmethod
    def save_as(data, file_name):
        with open(file_name, "w") as rx_file:
                rx_file.write(" ".join(str(each) for each in data))
