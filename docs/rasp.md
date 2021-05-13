# What Are RASP Machines?

A random access stored procedure machine (RASP) is an abstract machine,
used to in complexity theory. As opposed to Turing machines, the RASP
architecture resembles a modern computer: It has a CPU, a memory and I/O
devices. It is actually a minimal Von Neumann architecture!

I am not sure who came up with this machine first, but I followed the
description provided by S. Cook and A. Reckhow in their 1973 article:

 * Cook, Stephen A., and Robert A. Reckhow. "Time bounded random
   access machines." Journal of Computer and System Sciences 7, no. 4
   (1973):
   354&ndash;375. [DOI](https://doi.org/10.1016/S0022-0000(73)80029-7)

This article also describes RAM machines, where data and instructions
follow two separate paths (i.e., instructions are immutable). RAM
instantiate the Harvard architecture instead of the Von Neumann
architecture.

## Architecture

A RASP machine has the following three components:

* A central processing unit (CPU), which carries out arithmetic
  operations. This CPU has the following registers:
  
  * *IP*, which points to the location (in memory) of the next
    instruction to execute. Initially, the IP is set to zero.
  
  * *ACC*, which holds a single and unbounded integer
    value. Initially, ACC is set to zero.
  
* A memory, made of an *infinite* number of cells, where each cell contains
  a single *unbounded* integer value. Each cells is initially set to zero.
  
* I/O devices that allows the user and the RASP machine to exchange
  integer values.

### The Instruction Set

RASP programs are made of the following 7 instructions. Each
instruction requires two memory cells, one for the operation code
and one for its operand. Operands are either an address (i.e., an
unsigned integer) or a constant (i.e., a signed integer).

| Op. Code | Syntax         | Description                                                             | Semantic                  |
|----------|----------------|-------------------------------------------------------------------------|---------------------------|
| 1        | `READ <addr>`  | Read a integer from the I/O device                                      | memory[addr] := i/o       |
| 2        | `PRINT <addr>` | Send the value stored in memory at <addr> and send it to the I/O device | i/O := memory[addr]       |
| 3        | `ADD <addr>`   | Add the value stored in memory at <addr> to the ACC register.           | ACC := ACC + memory[addr] |
| 4        | `SUB <addr>`   | Subtract the value stored in memory at <addr> from the ACC register.    | ACC := ACC - memory[addr] |
| 5        | `LOAD <val>`   | Load the given value into the ACC register                              | ACC := val                |
| 6        | `JUMP <addr>`  | Set Register IP to <addr> if an only if ACC >= 0                        | IP := addr                |
| 7        | `STORE <addr>` | Store the value of the ACC register in memory at the given address      | mem[addr] := ACC          |
| 0        | `HALT <val>`   | Terminate the execution of the program.                                 |                           |


### Sample Program

Below is a simple program which reads two numbers from the I/O
devices, add them, and returns the result to the I/O device. This
program contains 8 instructions, so it takes 16 memory cells (the
so-called code segment, from Address 0 to 15), plus one memory cell to
store the user input (the data segment, Cell 16).

```asm
    read  16
    load  0
    add   16
    read  16
    add   16
    store 16
    print 16
    halt  0
```

To execute this program, we must convert each instruction into a pair
of integer, using the operation code shown in the table above. This gives:

```
1 16 5 0 3 16 1 16 3 16 7 16 2 16 0 0 0
```
