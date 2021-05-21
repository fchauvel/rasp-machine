;;; Compute the sum of the first n even integer, where n is defined as
;;; a constant

segment:        data
        limit           1       0
        remainder       1       0
        half            1       0
        result          1       0
        counter         1       0

segment:        code
        ;; Divide the limit by two
                read            limit
                load            0
                subtract        limit
                store           remainder       ; remainder = -limit
        div:    load            0
                add             remainder
                jump            mul             ; if remainder >= 0, goto mul
                load            2               ; else
                add             remainder
                store           remainder       ;   remainder += 2
                load            1
                add             half
                store           half            ;   half += 1
                load            0
                jump            div             ;   goto div
        ;; result = half * (half - 1)
        mul:    load            0
                add             counter
                subtract        half
                jump            done            ; if counter >= half, goto done
                load            1               ; else
                add             result
                add             half
                store           result          ;   result += (half + 1)
                load            1
                add             counter
                store           counter         ;   counter += 1
                load            0
                jump            mul             ;   goto mul
        done:   print           result
                halt            0
