# RASP Machines

[![last release on PyPI](https://img.shields.io/pypi/v/RASP-machine.svg)](https://pypi.python.org/pypi/RASP-Machine)
[![License](https://img.shields.io/pypi/l/RASP-Machine.svg)](https://en.wikipedia.org/wiki/MIT_License)
[![Build status](https://img.shields.io/github/workflow/status/fchauvel/rasp-machine/test-package-publish)](https://github.com/fchauvel/rasp-achine/actions)
[![Code coverage](https://img.shields.io/codecov/c/github/fchauvel/rasp-machine/main.svg)](https://codecov.io/gh/fchauvel/rasp-machine)
[![Code quality](https://img.shields.io/codacy/grade/132a989754b14fb085d76d7a63f10bc4.svg)](https://www.codacy.com/app/fchauvel/rasp-machine/dashboard)
[![Downloads](https://img.shields.io/pypi/dm/rasp-machine.svg)](https://pypistats.org/packages/rasp-machine)

This is a small Python&nbsp;3 emulator for the random access stored
procedure machine (RASP) designed by Cook & Reckhow in 1973 below. I
developed this as a companion tool for a course in algorithms & data
structures, where it helps (I hope) to with understanding computation
models, growth orders and the applicability of the Big-O notation.

* Cook, Stephen A., and Robert A. Reckhow. "Time bounded random access
  machines." Journal of Computer and System Sciences 7, no. 4 (1973):
  354&ndash;375. [DOI](https://doi.org/10.1016/S0022-0000(73)80029-7)

In a nutshell, the RASP machine is a mini computer with eight
instructions, two registers (an accumulator and instruction pointer),
and an I/O device. As a computation model, it closely resembles an
actual computer, as opposed to a Turing machine for instance.

## How to install RASP?

The simplest way to install the latest version is to use PyPI as
follows:

```shell
  $ pip install rasp-machine
```

Please, refer to the [documentation](https://fchauvel.github.io/rasp-machine)
for a more comprehensive help!

## How to use the RASP machine?

### A Simple Program: Adding Two Integers

Let us consider a tiny program for the rasp machine. To simplify
writing programs, RASP provides a simple assembly language, as shown
below, with the code needed to read two integers from the I/O device
and to print their sum back onto it.

```
segment: data
    left     1       0
    right    1       0
    result   1       0

segment: code
    read     left      ;; left = user_input()
    read     right     ;; right = user_input()
    load     0
    add      left
    add      right
    store    result    ;; result = left + right
    print    result
    halt     -1
```

Provided we save the code above into a file named `addition.asm`, we
can get the associated machine code, using the following command
```shell-session
$ rasp assemble addition.asm
Machine code saved in 'addition.rx'
```

Note that the option `--debug` will yield machine code that contains
debugging information, useful when using the debugger.

### Debugging & Executing RASP

Now we have the machine code, we can execute it using the following commands:

```shell-session
$ rasp execute addition.rx
rasp? 10
rasp? 20
30
```

Note that you can extract some performance measure (CPU cycle, read,
writes, etc.) using the `--use-profiler` option.

Should there be any problem with the execution, we can start the
associated debugger with the command:
```shell-session
$ rasp debug addition.rx
RASP-Machine 0.1.0
 ┼ debug >
```

