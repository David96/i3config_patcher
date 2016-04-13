#!/bin/env python
import sys
import logging

from themes import Themes
from config import Config

import os

if __name__ == "__main__":
    c = Config()

    if len(sys.argv) != 2:
        print("Usage: %s theme-name")
        print("The current theme is %s" % c.get("theme"))
        sys.exit(-1)

    logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)

    themes = Themes()
    t = themes.load_theme(sys.argv[1])
    t.apply()
