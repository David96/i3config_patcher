#!/bin/env python
import sys

from themes import Themes
from config import Config

import os

c = Config()

if len(sys.argv) != 2:
    print("Usage: %s theme-name")
    print("The current theme is %s" % c.get("theme"))
    sys.exit(-1)

themes = Themes()
t = themes.load_theme(sys.argv[1])
t.apply()
