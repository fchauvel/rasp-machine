#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#



from pathlib import Path

from rasp.assembly.parser import AssemblyParser
from rasp.assembler import Assembler
from rasp.executable import Loader
from rasp.machine import RASP

from tests.fakes import FakeInputDevice, FakeOutputDevice

from unittest import TestCase, TestSuite, main



class Scenario:

    def __init__(self, name, program, tests, is_skipped=False):
        self.name = name
        self._binary_code = self._compile(program)
        self._tests = tests
        self.is_skipped = is_skipped


    def prepare_run(self):
        runners = []
        for each_test in self._tests:
            runner = each_test.prepare_run(self._binary_code)
            runners.append((each_test.name, runner))
        return runners

    @staticmethod
    def _compile(assembly_code):
        program = AssemblyParser().parse(assembly_code)
        binary = Assembler().assemble(program)
        return " ".join(str(each) for each in binary)



class Test:

    def __init__(self, name, inputs, expected_outputs):
        self._inputs = inputs
        self._expected_outputs = expected_outputs
        self.name = name

    def prepare_run(self, binary_code):
        def runner(this):
            machine = RASP(input_device=FakeInputDevice(self._inputs),
                       output_device=FakeOutputDevice())

            Loader().from_text(machine.memory, binary_code)
            machine.run()
            this.assertEqual(self._expected_outputs, machine.output_device.values)
        return runner


class YAMLKeys:
    SCENARIO = "scenario"
    INPUTS = "inputs"
    OUTPUTS = "outputs"
    NAME = "name"
    DESCRIPTION = "description"
    TESTS = "tests"
    PROGRAM = "program"


class Library:

    def __init__(self, directory):
        self._home = Path(directory)

    def all(self):
        scenarios = []
        for each_file in self._find_all_scenarios():
            each_data = self._parse(each_file)
            each_scenario = self._build(each_data)
            scenarios.append(each_scenario)
        return scenarios

    def _find_all_scenarios(self):
        yaml_files = []
        for any_file in self._home.iterdir():
            if any_file.suffix in [".yaml", ".yml"]:
                yaml_files.append(any_file)
        return yaml_files

    def _parse(self, yaml_file):
        from yaml import safe_load
        return safe_load(yaml_file.read_text())

    def _build(self, dictionary):
        tests = []
        for each_test in dictionary[YAMLKeys.SCENARIO][YAMLKeys.TESTS]:
            name = each_test[YAMLKeys.NAME]
            tests.append(Test(name,
                              list(map(int, each_test[YAMLKeys.INPUTS])),
                              list(map(int, each_test[YAMLKeys.OUTPUTS]))))
        return Scenario(dictionary[YAMLKeys.SCENARIO][YAMLKeys.NAME],
                        dictionary[YAMLKeys.SCENARIO][YAMLKeys.PROGRAM],
                        tests)


class Generator:

    def __init__(self, repository):
        self._scenarios = repository

    def all_test_cases(self):
        test_cases = []
        for each_scenario in self._scenarios.all():
            test_case = self._create_test_case_class(each_scenario)
            test_cases.append(test_case)
        return test_cases


    def _create_test_case_class(self, scenario):
        methods = {}
        for name, runner in scenario.prepare_run():
            methods["test " + name] = runner
        return type(scenario.name, (TestCase,), methods)



def load_tests(loader, tests, pattern):
    repository = Library("tests/acceptance")
    generate = Generator(repository)
    suite = TestSuite()
    for each_test_case in generate.all_test_cases():
        tests = loader.loadTestsFromTestCase(each_test_case)
        suite.addTests(tests)
    return suite


if __name__ == "__main__":
    main()
