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
from subprocess import check_call

LANG       = "ja_JP.UTF-8"
#WINEDEBUG  = "+loaddll"

################################################################################

PREFIX      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WINE        = os.path.join(PREFIX, "libexec", "wine")
PLUGINDIR   = os.path.join(PREFIX, "share/wine", "plugin")

if sys.argv[1] in ["--help", "--version"]:
    os.execv(WINE, sys.argv)

if "LANG"       in globals(): os.environ.setdefault("LANG",       LANG)
if "WINEDEBUG"  in globals(): os.environ.setdefault("WINEDEBUG",  WINEDEBUG)

if "WINEPREFIX" in os.environ:
    WINEPREFIX = os.getenv("WINEPREFIX")
else:
    WINEPREFIX = os.path.expanduser("~/.wine")

if (
    not os.path.exists(os.path.join(WINEPREFIX, "drive_c"))
    or
    sys.argv[1] == "--force-init"
):
    check_call([WINE, "wineboot.exe", "--init"])
    if sys.argv[1] == "--skip-init": sys.exit()

    import init_wine
    init_wine.PREFIX    = PREFIX
    init_wine.WINE      = WINE
    init_wine.PLUGINDIR = PLUGINDIR

    init_wine.load_inf()
    if sys.argv[1] == "--suppress-init": sys.exit()
    init_wine.main()
    if sys.argv[1] == "--force-init": sys.exit()

print >> sys.stderr, "\033[4;32m%s\033[m" % " ".join(sys.argv[1:])

os.execv(WINE, sys.argv)
