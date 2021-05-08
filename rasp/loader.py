#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from io import StringIO


class Loader:


    def from_text(self, memory, text):
        self.from_stream(memory, StringIO(text))

    def from_stream(self, memory, stream):
        address = 0
        for any_cell in stream.read().split():
            if any_cell:
                try:
                    memory.write(address, int(any_cell))
                    address += 1
                except ValueError as error:
                    raise RuntimeError(f"Unable to read Cell {address}: "
                                       f"Expected an integer, but found {any_cell}")
