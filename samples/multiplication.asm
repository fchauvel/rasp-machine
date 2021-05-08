;; Read two numbers on from the input device, multiply them and return
;; the result on the output device.

segment: data
                left    1       0       ; the left operand 501
                right   1       0       ; the right operand 502
                counter 1       0       ; counter 503
                result  1       0       ; the result 5+4

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
