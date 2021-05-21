;; Sum all the even number until the given limit

segment: data
        limit           1       0
        sum             1       0
        remainder       1       0
        each_integer    1       0

segment: code
        read    limit
loop:   load    -1
        add     each_integer
        subtract limit
        jump    done            ; If each_integer >= limit, goto done
        load    0
        subtract each_integer
        store   remainder       ; remainder = -limit
mod:    load    0
        add     remainder
        jump    end_mod         ; if remainder <= 0, then goto end_mod
        load    2               ; else
        add     remainder       ;
        store   remainder       ;     remainder += 2
        load    0
        jump    mod             ;     goto mod

end_mod: load   -1
        add     remainder
        jump    next            ; if remainder != 0, then goto next
        load    0               ; else:
        add     each_integer
        add     sum
        store   sum             ;    sum += each_integer

next:   load    1
        add     each_integer
        store   each_integer         ; each_integer += 1
        load    0
        jump    loop            ; goto loop

done:   print   sum
        halt
