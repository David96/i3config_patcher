#!/bin/env python
import sys

from matcher import Matcher

def mergeI3(oldconfig, newconfig):
    matcher = Matcher(["^font\s", "^client\.\w+", "^new_window\s", "^new_float\s", "^hide_edge_borders\s"], ["bar"])
    patched_config = []

    replacements = {}
    variables = {}
    with open(newconfig) as f:
        for line in f:
            match, pattern = matcher.matches(line)
            # store all variables and matches we find
            if match == Matcher.MATCH_VARIABLE:
                variables[pattern] = line
            if match > Matcher.MATCH_NONE:
                try:
                    replacements[pattern].append(line)
                except:
                    replacements[pattern] = [ line ]

    with open(oldconfig) as f:
        for i,line in enumerate(f):
            match, pattern = matcher.matches(line)
            # don't override existing variables, later the user should be asked here
            if match == Matcher.MATCH_VARIABLE and pattern in variables:
                print("%s already set, not overriding" % pattern)
                variables.pop(pattern)
            # Look for a replacement of the found match
            if match > Matcher.MATCH_NONE and pattern in replacements:
                replacement = replacements[pattern]
                if replacement != None:
                    # Look for actual usage of the variables extracted from the new config
                    # Append them right before the actual usage
                    # Might want to find a more pythonic way to do this
                    for line in replacement:
                        for name, var_line in variables.copy().items():
                            if "$%s" % name in line:
                                print("Found usage of %s after line %d" % (name, i))
                                patched_config.append(var_line)
                                variables.pop(name)
                    print("Replacing %s, line %d, with:\n%s" % (line.strip(), i, ''.join(replacement)))
                    patched_config.extend(replacement)
                    replacements[pattern] = None
            # If we don't have a match, just append the line of the old config to our combined one
            else:
                patched_config.append(line)

    # Add missing parts that we didn't find a place to inline-replace for at the end of the file
    for pattern, replacement in replacements.items():
        if replacement != None:
            patched_config.extend(replacement)

    # Write our new shiny config
    with open(oldconfig, 'w') as f:
        f.writelines(patched_config)

if len(sys.argv) != 3:
    print("Usage: %s <path/to/old/config> <path/to/new/config>")
    sys.exit(-1)
mergeI3(sys.argv[1], sys.argv[2])
