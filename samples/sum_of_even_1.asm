;; Sum all the even number until the given limit

segment: data
        limit           1       0
        sum             1       0
        modulo          1       0
        counter         1       0

segment: code
        read    limit
loop:   load    0
        add     counter
        subtract limit
        jump    done            ; If counter >= limit, goto done

        load    0
        subtract counter
        store   modulo          ; modulo = -counter
mod:    load    0
        add     modulo
        jump    end_mod         ; if modulo >= 0, then goto end_mod
        load    2               ; else
        add     modulo          ;
        store   modulo          ;     modulo += 2
        load    0
        jump    mod             ;     goto mod

end_mod: load   -1
        add     modulo
        jump    next            ; if modulo-1 > 0, then goto next
        load    0               ; else:
        add     counter
        add     sum
        store   sum             ;    sum += counter

next:   load    1
        add     counter
        store   counter         ; counter += 1
        load    0
        jump    loop            ; goto loop

done:   print   sum
        halt
