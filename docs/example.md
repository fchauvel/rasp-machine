# How to Write RASP Programs?

RASP machine read integers ... and writing long series of integers
quickly gets annoying. To mitigate that, RASP comes with mini assembly
language, and assembler and a debugger that help write program more
efficiently.

Let us consider a program that multiply two numbers (remember that the
original instruction set only offers add and subtract).

```rasm
;; Read two numbers on from the input device, multiply them and return
;; the result on the output device.

segment: data
                left    1       0       ; the left operand
                right   1       0       ; the right operand
                counter 1       0       ; counter
                result  1       0       ; the result

segment: code
                read            left    ; left
                read            right   ; right
        loop:   load            0       ;
                add             counter
                subtract        right   ;
                jump            done    ; if counter - right >= 0, goto done
                load            0
                add             result
                add             left
                store           result  ; result += left
                load            1
                add             counter
                store           counter ; counter += 1
                load            0
                jump            loop    ; goto loop
        done:   print           result
                halt            -1
```

This code cannot be directly run on the RASP machine. To do so, we
need to produce an "executable", that is a sequence of integer that
we can then load into memory. Provided we save the code above in a
file named `multiplication.asm`, we can assemble it into such a "RASP
executable" file using:

```shell-session
$ rasp assemble samples/multiplication.asm
```

This yields a file named `multiplication.rx` that contains a sequence
of integer that we can now load into our RASP machine and run.

```
2 32 2 33 8 0 3 34 5 33 6 30 8 0 3 35 3 32 4 35 8 1 3 34 4 34 8 0 6 4 1 35 0 0 0 0
```

To run this file, we simply invoke `rasp execute` as follows:
```console
$ rasp execute multiplication.rx
rasp? 10
rasp? 20
200
---
Time: 268 cycle(s)
Memory: 36 cell(s)
```
