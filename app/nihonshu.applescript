on main(argv)
    repeat with f in argv
        do shell script "WINEDEBUG=-all /usr/local/wine/bin/wine start /unix " & quoted form of POSIX path of f & " &>/dev/null &"
    end repeat
end main

on run
    main((choose file with multiple selections allowed) as list)
end run

on open argv
    main(argv)
end open
