#!/bin/env python
import sys

from i3merger import I3Merger

if len(sys.argv) != 3:
    print("Usage: %s <path/to/old/config> <path/to/new/config>")
    sys.exit(-1)
merger = I3Merger()
merger.merge(sys.argv[1], sys.argv[2])
