#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nihonshu - Customized Wine binary for OS X (Ja)
#
# Copyright (C) 2013 mattintosh4, https://github.com/mattintosh4/nihonshu
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
#
import os
import sys

PREFIX      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WINE        = os.path.join(PREFIX, "libexec/wine")
WINEDEBUG   = "" #+ "+loaddll"


if len(sys.argv) < 2 or sys.argv[1] in ["--help", "--version"]:
    os.execv(WINE, sys.argv)


os.environ.setdefault("LANG", "ja_JP.UTF-8")
os.environ.setdefault("WINEDEBUG", WINEDEBUG)


wineprefix  = os.environ.get("WINEPREFIX", os.path.expanduser("~/.wine"))
wineprefix  = os.path.join(wineprefix, "drive_c")
wineprefix  = os.path.exists(wineprefix)
with_opt    = sys.argv[1] in ["--skip-init", "--suppress-init", "--force-init"]
if not wineprefix or with_opt:
    import init_wine
    init_wine.PREFIX    = PREFIX
    init_wine.WINE      = WINE
    init_wine.PLUGINDIR = os.path.join(PREFIX, "share/wine/plugin")
    init_wine.main()


print >> sys.stderr, "\033[4;32m" + " ".join(sys.argv[1:]) + "\033[m"


os.execv(WINE, sys.argv)
