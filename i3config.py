#!/bin/env python
import sys

from matcher import Matcher

def add_variables_for_pattern(config, variables, used_variables, pattern):
    # Find all variables used in pattern
    var = [variable for variable,var_pattern in used_variables.items() if var_pattern == pattern]
    # Add them to our config
    config.extend([variables[variable] for variable in var])

def mergeI3(oldconfig, newconfig):
    matcher = Matcher(["^font\s", "^client\.\w+", "^new_window\s", "^new_float\s", "^hide_edge_borders\s"], ["bar"])
    patched_config = []

    replacements = {}
    variables = {}
    used_variables = {}
    with open(newconfig) as f:
        for line in f:
            match, pattern = matcher.matches(line)
            # store all variables and matches we find
            if match == Matcher.MATCH_VARIABLE:
                variables[pattern] = line
            if match > Matcher.MATCH_NONE:
                for variable in variables:
                    if "$%s" % variable in line and variable not in used_variables:
                        print("Added variable %s for pattern %s" % (variable, pattern))
                        used_variables[variable] =  pattern
                try:
                    replacements[pattern].append(line)
                except:
                    replacements[pattern] = [ line ]

    with open(oldconfig) as f:
        for i,line in enumerate(f):
            match, pattern = matcher.matches(line)
            # don't override existing variables, later the user should be asked here
            if match == Matcher.MATCH_VARIABLE and pattern in used_variables:
                override = input("%s already set, override? [y/n] " % pattern)
                if override.lower() == "y":
                    continue
                else:
                    used_variables.pop(pattern)
            # Look for a replacement of the found match
            if match > Matcher.MATCH_NONE and pattern in replacements:
                replacement = replacements[pattern]
                if replacement != None:
                    add_variables_for_pattern(patched_config, variables, used_variables, pattern)
                    print("Replacing %s, line %d, with:\n%s" % (line.strip(), i, ''.join(replacement)))
                    patched_config.extend(replacement)
                    replacements[pattern] = None
            # If we don't have a match, just append the line of the old config to our combined one
            else:
                patched_config.append(line)

    # Add missing parts that we didn't find a place to inline-replace for at the end of the file
    for pattern, replacement in replacements.items():
        if replacement != None:
            add_variables_for_pattern(patched_config, variables, used_variables, pattern)
            patched_config.extend(replacement)

    # Write our new shiny config
    with open(oldconfig, 'w') as f:
        f.writelines(patched_config)

if len(sys.argv) != 3:
    print("Usage: %s <path/to/old/config> <path/to/new/config>")
    sys.exit(-1)
mergeI3(sys.argv[1], sys.argv[2])
