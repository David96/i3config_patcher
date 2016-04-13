import logging
from os import path
from xdg.BaseDirectory import xdg_config_home

from matcher import *
from merger import BaseMerger

class Merger(BaseMerger):
    """
        Provides merging functionality for two i3 config files.
        Merges only the style parts (identified by regex patterns) from the new file into the old one.
    """

    def merge(self, software, name, oldconfig, newconfig):
        logging.debug("Software: %s" % software)
        if software == "i3":
            patterns = {
                "root" :  ["^\s*font\s", "^\s*client\.\w+", "^\s*new_window\s",
                                    "^\s*new_float\s", "^\s*hide_edge_borders\s"],
                "bar":    ["^\s*strip_workspace_numbers\s",
                                    "^\s*font\s", "^\s*mode\s"],
                "colors": [".*"] }
        elif software == "i3status":
            patterns = {"general" :  ["^\s*colors\s", "^\s*color_\w+\s"]}

        return self.merge_config(patterns, oldconfig, newconfig)


    def get_supported_software(self):
        return {"i3":
            { "config": ["~/.i3/config", path.join(xdg_config_home, "i3/config")]},
                "i3status":
            { "config": [ "~/.i3status/config",
                            path.join(xdg_config_home, "i3status/config")]}}

    def merge_config(self, patterns, oldconfig, newconfig):
        """
            Merge the style of two i3 config files.
            Overrides oldconfig.

            :param name: name of the file in the theme
            :param oldconfig: Path to old config
            :param newconfig: Path to merge into old config
        """
        matcher = Matcher(patterns)

        (blocks, variables) = self.__parse_config(matcher, newconfig)
        return self.__merge_config(matcher, blocks, variables, oldconfig)

    def __get_used_variables(self, line, variables):
        """
            Returns variables used by a line.
            Sets "used" to "True" for each found variable!
        """
        variable_matches = {}
        for variable in variables:
            # There might be variables including other variables (like $light and $lighter, $dark and $darker etc.)
            # i3 allows usage of variables in strings like $varblabla so we look for multiple variable occurences
            # at the same position and if in doubt take the longer variable.
            # See https://github.com/David96/i3config_patcher/issues/6
            try:
                position = line.index("$%s" % variable)
                if position in variable_matches:
                    logging.debug("Found conflicting variable usage of %s with %s at %d in %s",
                            variable, variable_matches[position], position, line)
                    variable_matches[position] = variable \
                            if len(variable) > len(variable_matches[position]) else variable_matches[position]
                    logging.debug("Using %s", variable_matches[position])
                else:
                    variable_matches[position] = variable
            except ValueError:
                pass
        used_variables = set(variable_matches.values())
        for var in used_variables:
            variables[var].used = True
        return used_variables

    def __append_variables(self, config, variables, used_variables):
        config.extend([variables.pop(v).line if v in variables else "" for v in used_variables])

    def __append_pattern(self, config, variables, matches, pattern):
        self.__append_variables_for_pattern(config, variables, matches, pattern)
        self.__append_matches_for_pattern(config, matches, pattern)
        matches[pattern] = None

    def __append_variables_for_pattern(self, config, variables, matches, pattern):
        if matches[pattern] != None:
            for match in matches[pattern]:
                self.__append_variables(config, variables, match.used_variables)

    def __append_variables_for_block(self, config, variables, block):
        self.__append_variables(config, variables, block.used_variables)
        for b in block.blocks:
            self.__append_variables_for_block(config, variables, b)

    def __append_matches_for_pattern(self, config, matches, pattern):
        if matches[pattern] != None:
            config.extend([m.line for m in matches[pattern]])

    def __append_block(self, config, block, variables):
        for pattern in block.matches:
            self.__append_pattern(config, variables, block.matches, pattern)
        for b in block.blocks:
            block_config = []
            self.__append_block(block_config, b, variables)
            if len(block_config) > 0:
                config.append("%s {\n%s\n}\n" % (b.name, "".join(block_config)))

    def __parse_config(self, matcher, path):
        blocks = { "root": Block("root", None) }
        current_block = blocks["root"]
        variables = {}
        with open(path) as f:
            for line in f:
                matchobj = matcher.matches(line)
                if matchobj.match_type == MATCH_OPEN:
                    new_block = Block(matchobj.current_block, current_block)
                    blocks[matchobj.current_block] = new_block
                    current_block.blocks.add(new_block)
                    current_block = new_block
                elif matchobj.match_type == MATCH_CLOSE:
                    current_block = current_block.parent
                elif matchobj.match_type == MATCH_VARIABLE:
                    variables[matchobj.groups[0]] =  Variable(matchobj.groups[0], matchobj.groups[1], line)
                elif matchobj.match_type == MATCH_LINE:
                    used_variables = self.__get_used_variables(line, variables)
                    current_block.used_variables |= used_variables
                    match = Match(matchobj.pattern, line, used_variables)
                    if matchobj.pattern in current_block.matches:
                        current_block.matches[matchobj.pattern].append(match)
                    else:
                        current_block.matches[matchobj.pattern] = [ match ]

        return (blocks, variables)

    def __merge_config(self, matcher, blocks, variables, path):
        patched_config = []
        with open(path) as f:
            for i, line in enumerate(f):
                matchobj = matcher.matches(line)
                current_block = blocks[matchobj.current_block] if matchobj.current_block in blocks else None
                if current_block != None and matchobj.match_type == MATCH_OPEN:
                    self.__append_variables_for_block(patched_config, variables, current_block)
                elif current_block != None and matchobj.match_type == MATCH_VARIABLE and matchobj.groups[0] in variables:
                    new_var = variables[matchobj.groups[0]]
                    if new_var.used:
                        variables.pop(new_var.name)
                        # Only ask if they have different values
                        if new_var.value != matchobj.groups[1]:
                            override = input("override %s=%s with %s=%s? [y/n] " %
                                    (matchobj.groups[0], matchobj.groups[1], new_var.name, new_var.value))
                            if override.lower() == "y":
                                patched_config.append(new_var.line)
                                continue

                if current_block != None and matchobj.match_type == MATCH_CLOSE:
                    # Append all matches that we didn't have a counterpart for in the old config
                    self.__append_block(patched_config, current_block, variables)
                    blocks.pop(current_block.name)

                if current_block != None and matchobj.match_type == MATCH_LINE and matchobj.pattern in current_block.matches:
                    self.__append_pattern(patched_config, variables, current_block.matches, matchobj.pattern)
                else:
                    patched_config.append(line)

        # Append matches that we couldn't inline-replace
        self.__append_block(patched_config, blocks["root"], variables)

        return patched_config

""" Helper classes """

class Match:

    def __init__(self, pattern, line, used_variables):
        self.pattern = pattern
        self.line = line
        self.used_variables = used_variables

class Block:

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.matches = {}
        self.blocks = set()
        self.used_variables = set()

class Variable:
    def __init__(self, name, value, line):
        self.name = name
        self.value = value
        self.line = line
        self.used = False

