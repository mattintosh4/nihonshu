#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

PREFIX     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WINETRICKS = os.path.join(PREFIX, 'libexec', 'winetricks')

os.environ['PATH'] = os.path.join(PREFIX, 'bin') + ':' + os.getenv('PATH')

os.execv(WINETRICKS, sys.argv)
