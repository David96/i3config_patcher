import re

MATCH_VARIABLE = -1
MATCH_NONE = 0
MATCH_LINE = 1
MATCH_OPEN = 2
MATCH_CLOSE = 3

class Matcher:
    """
        Provides basic matching functionality tailored to i3 config files.
    """
    pattern_open = "^\s*(\w+)\s*(\"?.*\"?)?\s*{"
    pattern_close = "\s*}\s*"

    def __init__(self, blocks):
        self.match_level = 0
        self.matching_blocks = [ "root" ]
        self.blocks = blocks

    def matches(self, line):
        """
            Match a line to the provided line and block patterns.
            Assumes that it is called line by line to make block matching work.

            :param line: the line you want to match

            :returns: :class:`.MatchObj`

        """
        matchObj = re.match(self.pattern_open, line)
        if matchObj:
            self.match_level += 1
            block = matchObj.group(1)
            self.matching_blocks.append(block)
            return MatchObj(MATCH_OPEN, self.pattern_open, block, matchObj.groups())

        current_block = self.matching_blocks[self.match_level]
        matchObj = re.match(self.pattern_close, line)
        if matchObj:
            self.match_level -= 1
            self.matching_blocks.pop()
            return MatchObj(MATCH_CLOSE, self.pattern_close, current_block, matchObj.groups())

        matchObj = re.match("^set\s+\$(\w+)\s+(.+)", line)
        if matchObj:
            return MatchObj(MATCH_VARIABLE, None, current_block, matchObj.groups())

        if current_block in self.blocks:
            for pattern in self.blocks[current_block]:
                matchObj = re.match(pattern, line)
                if matchObj:
                    return MatchObj(MATCH_LINE, pattern, current_block, matchObj.groups())
        return MatchObj(MATCH_NONE, None, current_block, None)

class MatchObj:
    def __init__(self, match_type, pattern, current_block, groups):
        self.match_type = match_type
        self.pattern = pattern
        self.current_block = current_block
        self.groups = groups
