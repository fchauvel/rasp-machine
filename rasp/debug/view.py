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
        print(f"{About.COPYRIGHT}")
        print()


    def request_input(self):
        print(" \u253C debug > ", end="")
        return input()

    def show_closing(self):
        print("That's all folks!")


    def show_memory(self, view):
        self._format(f"   \u2514\u2500 Memory:")
        for index, (address, value, is_current, is_breakpoint, mnemonic) in enumerate(view):
            marker = "\u251C" if index < len(view) - 1 else "\u2514"
            break_point = "(b)" if is_breakpoint else "   "
            current = ">>>" if is_current else "   "
            self._format(f"       {marker}\u2500 {current} {break_point} {address:>5}: {value:>5} {mnemonic:<20}")

    def show_breakpoints(self, infos):
        items = []
        for address, is_current, value, mnemonic in infos:
            current = ">>>" if is_current else "   "
            items.append(f"{current} {address:>5}: {value:>5} {mnemonic:<20}")
        self._format_list("Breakpoints", items)
#
    def _format_list(self, title, items):
        if not items:
            self._format(f"   \u2514\u2500 {title}: None")
        else:
            self._format(f"   \u2514\u2500 {title}:")
            for index, item in enumerate(items):
                if index < len(items) - 1:
                    self._format(f"       \u251C\u2500 {item}")
                else:
                    self._format(f"       \u2514\u2500 {item}")


    def show_cpu(self, view):
        self._format_list("CPU:", [
            f"ACC: {view[0]:>6}",
            f" IP: {view[1]:0>6} ~ {view[2]}"
        ])

    def show_source(self, code_fragment):
        self._format(f"   \u2514\u2500 Assembly Code:")
        for line_number, is_current, is_breakpoint, code in code_fragment:
            current = ">>>" if is_current else "   "
            bp = "(b)" if is_breakpoint else "   "
            self._format(f"       \u251C\u2500 {line_number:0>3}: {current} {bp} {code}")

    def no_source_code(self):
        self._format(f"   \u2514\u2500 Assembly code is not available.")
        self._format(f"       \u2514\u2500 Did you assemble with the '--debug' flag?")

    def show_instruction(self, instruction):
        self._format(f"   \u2514\u2500 RUN: {instruction}")

    def invalid_command(self, command):
        self._format(f"   \u2514\u2500 Invalid command '{command}'.")

    def _format(self, text, end="\n"):
        print(" \u2502" + text, end=end)

    def report_error(self, error):
        self._format(f"   \u2514\u2500 Error: {str(error)}.")

    def read(self):
        self._format(f"      \u2514\u2500 Input? ", end="")
        user_input = input()
        return int(user_input)

    def write(self, value):
        self._format(f"   \u2514\u2500 Output: {value}")
