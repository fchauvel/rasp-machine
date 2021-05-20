#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#

from io import StringIO

from rasp.cli import Controller, ErrorCodes

from unittest import TestCase


class UiTests(TestCase):

    TEST_PROGRAM = "samples/multiplication.asm"
    TEST_BINARY = "samples/multiplication.rx"

    def setUp(self):
        self.output = StringIO()
        self.cli = Controller(self.output)


    def check_status(self, expected_status, command):
        try:
            status = self.cli.run(command.split())

        except:
            self.fail("Must not throw any exception!")

        self.assertEqual(expected_status, status)
        self.assertNotIn("TraceBack", self.output.getvalue())

    def test_version(self):
        self.check_status(ErrorCodes.OK,
                          "rasp version")

    def test_assemble(self):
        self.check_status(ErrorCodes.OK,
                          f"rasp assemble {self.TEST_PROGRAM}")

    def test_assemble_missing_file(self):
        self.check_status(ErrorCodes.SOURCE_NOT_FOUND,
                          f"rasp assemble this_is/not_there.asm")

    def test_assemble_with_debug(self):
        self.check_status(ErrorCodes.OK,
                          f"rasp assemble --debug {self.TEST_PROGRAM}")

    def test_assemble_with_output(self):
        self.check_status(ErrorCodes.OK,
                          f"rasp assemble --output test.rx {self.TEST_PROGRAM}")

    def test_execute(self):
        self.check_status(ErrorCodes.OK,
                          f"rasp assemble {self.TEST_PROGRAM}")
        self.check_status(ErrorCodes.OK, f"rasp execute {self.TEST_BINARY}")

    def test_execute_with_profiler(self):
        self.check_status(ErrorCodes.OK,
                          f"rasp assemble {self.TEST_PROGRAM}")
        self.check_status(ErrorCodes.OK,
                          f"rasp execute --use-profiler {self.TEST_BINARY}")

    def test_execute_with_a_missing_file(self):
        self.check_status(ErrorCodes.EXECUTABLE_NOT_FOUND,
                          f"rasp execute --use-profiler not_there.rx")
