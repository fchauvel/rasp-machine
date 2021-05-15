#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp.machine import InputDevice, OutputDevice


class FakeInputDevice(InputDevice):

    def __init__(self, inputs=None):
        self.inputs = inputs or [0]
        self._index = 0
        super().__init__()

    def read(self):
        value =  self.inputs[self._index]
        self._index = (self._index + 1) % len(self.inputs)
        return int(value)


class FakeOutputDevice(OutputDevice):

    def __init__(self):
        self.values = []

    @property
    def size(self):
        return len(self.values)

    def write(self, value):
        self.values.append(value)
