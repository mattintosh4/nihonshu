#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nihonshu - Custom Wine Binary for OS X (Ja)
#
# Copyright (C) 2013 mattintosh4, https://github.com/mattintosh4/nihonshu

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
