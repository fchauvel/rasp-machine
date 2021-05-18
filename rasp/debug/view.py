#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp import About


class DebugView:

    def show_opening(self):
        print(f"{About.NAME} {About.VERSION}")
        print()

    def show_help(self):
        items = [
            "break at address <address>",
            "break at line <line_number>",
            "clear address <address>",
            "clear line <line_number>",
            "continue",
            "exit",
            "set acc <value>",
            "set ip <value>",
            "set memory <address> <value>",
            "show breakpoints",
            "show cpu",
            "show memory <from:address> <to:address>?",
            "show source <from:line> <to:line>?",
            "show <symbol>",
            "step <count:value>?",
            "quit",
            "run"
        ]

        self._format_list("Available commands", items)

    def request_input(self):
        print(" \u253C debug > ", end="")
        return input()

    def show_closing(self):
        print("That's all folks!")


    def show_memory(self, memory_fragment):
        items = []
        for address, value, is_current, is_breakpoint, mnemonic in memory_fragment:
            current = ">>>" if is_current else "   "
            bp = "(b)" if is_breakpoint else "   "
            item = f"{address:0>3}: {current} {bp} {value:>5} {mnemonic:<20}"
            items.append(item)
        self._format_list("Memory", items)

    def show_breakpoints(self, infos):
        items = []
        for address, is_current, value, mnemonic in infos:
            current = ">>>" if is_current else "   "
            items.append(f"{current} {address:>5}: {value:>5} {mnemonic:<20}")
        self._format_list("Breakpoints", items)

    def show_cpu(self, view):
        self._format_list("CPU:", [
            f"ACC: {view[0]:>6}",
            f" IP: {view[1]:0>6} ~ {view[2]}"
        ])

    def show_source(self, code_fragment):
        items = []
        for line_number, is_current, is_breakpoint, code in code_fragment:
            current = ">>>" if is_current else "   "
            bp = "(b)" if is_breakpoint else "   "
            item = f"{line_number:0>3}: {current} {bp} {code}"
            items.append(item)
        self._format_list("Assembly Code", items)

    def no_source_code(self):
        self._format_list("Error", ["Assembly code is not available.",
                                    f"Did you assemble with the '--debug' flag?"])

    def show_instruction(self, instruction):
        self._format_message(f"RUN: {instruction}")

    def invalid_command(self, command):
        self._format_message(f"Invalid command '{command}'. Use 'help' to the availble ones.")

    def report_error(self, error):
        self._format_message(f"Error: {str(error)}.")

    def read(self):
        self._format(f"      \u2514\u2500 Input? ", end="")
        user_input = input()
        return int(user_input)

    def write(self, value):
        self._format_message(f"Output: {value}")

    def _format_list(self, title, items):
        if not items:
            self._format_message(f"{title}: None")
        else:
            self._format(f"   \u2514\u2500 {title}:")
            for index, item in enumerate(items):
                if index < len(items) - 1:
                    self._format(f"       \u251C\u2500 {item}")
                else:
                    self._format(f"       \u2514\u2500 {item}")

    def _format_message(self, message):
        self._format(f"   \u2514\u2500 {message}")

    def _format(self, text, end="\n"):
        print(" \u2502" + text, end=end)
