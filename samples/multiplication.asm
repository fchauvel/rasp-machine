;; Read two numbers on from the input device, multiply them and return
;; the result on the output device.

segment: data
                left    1       12       ; the left operand
                right   1       5      ; the right operand
                counter 1       0       ; counter
                result  1       0       ; the result

segment: code
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
