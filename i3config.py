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
                variable_matches = {}
                for variable in variables:
                    # There might be variables including other variables (like $light and $lighter, $dark and $darker etc.)
                    # i3 allows usage of variables in strings like $varblabla so we look for multiple variable occurences
                    # at the same position and if in doubt take the longer variable.
                    # See https://github.com/David96/i3config_patcher/issues/6
                    try:
                        position = line.index(variable)
                        if position in variable_matches:
                            print("Found conflicting variable usage of %s with %s at %d in %s" %
                                    (variable, variable_matches[position], position, pattern))
                            variable_matches[position] = variable \
                                    if len(variable) > len(variable_matches[position]) else variable_matches[position]
                            print("Using %s" % variable_matches[position])
                        else:
                            variable_matches[position] = variable
                    except ValueError:
                        pass
                for var in variable_matches.values():
                    if var not in used_variables:
                        used_variables[var] = pattern
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
