#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nihonshu - Custom Wine Binary for OS X (Ja)
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

WINEPREFIX = os.path.expanduser("~/.wine")
#WINEDEBUG  = "+loaddll"
LANG       = "ja_JP.UTF-8"

################################################################################

PREFIX      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WINE        = os.path.join(PREFIX, "libexec", "wine")
PLUGINDIR   = os.path.join(PREFIX, 'share/wine/plugin')

if sys.argv[1] in ["--help", "--version"]:
    os.execv(WINE, sys.argv)

if "WINEPREFIX" in globals(): os.environ.setdefault("WINEPREFIX", WINEPREFIX)
if "WINEDEBUG"  in globals(): os.environ.setdefault("WINEDEBUG",  WINEDEBUG)
if "LANG"       in globals(): os.environ.setdefault("LANG",       LANG)

if "WINEPREFIX" in os.environ:
    WINEPREFIX = os.getenv("WINEPREFIX")
else:
    WINEPREFIX = os.path.expanduser("~/.wine")
if not os.path.exists(WINEPREFIX):
    os.makedirs(WINEPREFIX)
    import init_wine
    init_wine.PREFIX    = PREFIX
    init_wine.WINE      = WINE
    init_wine.PLUGINDIR = PLUGINDIR
    init_wine.main()

print >> sys.stderr, "\033[4;32m%s\033[m" % " ".join(sys.argv[1:])

os.execv(WINE, sys.argv)
