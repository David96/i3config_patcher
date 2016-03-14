import re

class Matcher:
    """
        Provides basic matching functionality tailored for i3 config files.
    """
    MATCH_VARIABLE = -1
    MATCH_NONE = 0
    MATCH_LINE = 1
    MATCH_BLOCK = 2

    match_level = 0
    matching_block = 0
    current_block = None

    def __init__(self, line_patterns, blocks):
        self.line_patterns = line_patterns
        self.blocks = blocks

    def matches(self, line):
        """
            Match a line to the provided line and block patterns.
            Assumes that it is called line by line to make block matching work.

            Args:
                the line you want to match

            Returns:
                (MATCH_VARIABLE, name) in case there's a variable defined in that line
                (MATCH_NONE, None) in case there's nothing matching the provided patterns and no variable defined
                (MATCH_LINE, pattern) in case the line matches pattern
                (MATCH_BLOCK, block) in case the line corresponds to block

        """
        matchObj = re.match("^\s*(\w+)\s*(\".*\")?\s*{", line)
        if matchObj:
            self.match_level += 1
            block = matchObj.group(1)
            if block in self.blocks:
                self.current_block = block
                self.matching_block = self.match_level
                return (self.MATCH_BLOCK, block)

        matchObj = re.match("\s*}\s*", line)
        if matchObj:
            self.match_level -= 1
            if self.matching_block == self.match_level + 1:
                self.matching_block = 0
                return (self.MATCH_BLOCK, self.current_block)

        if self.matching_block > 0 and self.matching_block <= self.match_level:
            return (self.MATCH_BLOCK, self.current_block)

        matchObj = re.match("^set\s+\$(\w+)\s+(.+)", line)
        if matchObj:
            return (self.MATCH_VARIABLE, matchObj.group(1))

        for pattern in self.line_patterns:
            matchObj = re.match(pattern, line)
            if matchObj:
                return (self.MATCH_LINE, pattern)
        return (self.MATCH_NONE, None)


