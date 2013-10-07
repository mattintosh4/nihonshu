on main(input)
    do shell script "WINEDEBUG=-all /usr/local/wine/bin/wine 7zFM.exe " & input & " &>/dev/null &"
end main

on run
    main("")
end run

on open argv
    repeat with f in argv
        main(quoted form of POSIX path of f)
    end repeat
end open
