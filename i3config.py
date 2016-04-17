#!/bin/env python
import sys
import logging

from themes import Themes
from config import Config

import os

if __name__ == "__main__":
    c = Config()

    if len(sys.argv) != 2:
        print("Usage: %s theme-name", file=sys.stderr)
        print("The current theme is %s" % c.get("theme"), file=sys.stderr)
        sys.exit(-1)

    logging.basicConfig(format='[%(levelname)7s] %(filename)16s:%(lineno)3s: %(message)s', level=logging.DEBUG)

    themes = Themes()
    t = themes.load_theme(sys.argv[1])
    if t:
        t.apply()
    else:
        print("Theme %s doesn't exist!" % sys.argv[1], file=sys.stderr)
