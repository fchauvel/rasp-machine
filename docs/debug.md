# How to Debug?

Writing assembly code, especially when we are learning, is not
necessarily straightforward. To ease the development, RASP provide a
simple debugger that let you run your programs step by step,
scrutinizing the memory and the CPU as you need.

## Enabling Debugging

By default, the RASP assembler only generates the memory layout to be
loaded in the RASP machine. That excludes any debugging information,
but does not precludes debugging. It only prevents the debugger from
mapping memory address back to the assembly source file and its
labels.

To enable this mapping (from memory addresses to assembly code), you
must assemble using the `--debug` flag so that the resulting
executable file also includes debugging information.

```shell-session
$ rasp assemble --debug multiplication.asm
```

With this alternative executable (also named `multiplication.rx`), you
can now lauch the debugger using:

```shell-session
$ rasp debug multiplication.rx 
 ┼ debug > show cpu
 │   └─ CPU:
 │       ├─ ACC:      0
 │       └─  IP: 000000 ~ read 34
 ┼ debug > show 
 │   └─ Memory:
 │       ├─    4:     8 - load      
 │       └─    5:     0 - halt      
 ┼ debug > quit
```

## Execution

 * `step [number]?`. Execute the given `number` of instruction,
   provided that none is marked as a breakpoint and that the program
   does not terminate. If `number` is not specified, it executes only
   the next instruction.
 
 * `run`. Execute instructions until the next breakpoint or the end of
   the program.
   
 * `reset`. Reload the current program in memory. All changes to the
   memory (to both code and data segment) are lost.
 
 * `quit`. Quit the current debugger session. All state is discarded.


## Assembly Source File

* `show source [from-line]? [to-line]?` Show the assembly source code
  from the line number given as `from-line` to the line number given
  as `to-line` (both are included). If `to-line` is omitted, it shows
  10 lines from the given `from-line` number. If both `from-line`and
  `to-line`are omitted, it shows 10 lines around the current location
  (i.e., the current value IP).

## CPU

 * `show cpu` Show the current state of the CPU, that is its ACC and
   IP registers.
   
 * `set acc <value>` Set the ACC register to the given value.
 
 * `set ip <value>` Set the IP register to the given value.

## Memory

 * `show memory <from-address> <to-address>`. Show the content of the
   memory for the given range of address (both ends are included).
 
 * `show <symbol>`. Show the memory associated with the given symbol.
 

 * `break at [a:XXX|l:XXX]`. Set a breakpoint, either at a given
   address (using `a:XXX`) or at a line of the assembly source code
   (using `l:XXX`).
   
 * `show breaks` list all the break points defined so far.

