import re

MATCH_VARIABLE = -1
MATCH_NONE = 0
MATCH_LINE = 1
MATCH_OPEN = 2
MATCH_CLOSE = 3

class Matcher:
    """
        Provides basic matching functionality for simple config files.
    """

    def __init__(self, blocks, pattern_open,
                        pattern_close=None, nested_blocks=False):
        """
            :param blocks: the blocks to match, format:
                { "blockname" : ["patterns", "to", "match"], "anotherblock": [ ...] }

                The "root" block matches everything without a block.
            :param pattern_open: The pattern that opens a block, first match group
                is used as its name.
            :param pattern_close: The pattern that closes a block. Only necessary if
                nested_blocks==True
            :param nested_blocks: Whether nested blocks have to be supported.
                Requires pattern_close to be set.
        """

        if nested_blocks and not pattern_close:
            raise Exception("pattern_close must be defined when nested_blocks=True")

        self.pattern_open = pattern_open
        self.pattern_close = pattern_close
        self.nested_blocks = nested_blocks
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
            block = matchObj.group(1)
            if self.nested_blocks:
                self.match_level += 1
                self.matching_blocks.append(block)
            else:
                self.matching_blocks[0] = block
            return MatchObj(MATCH_OPEN, self.pattern_open, block, matchObj.groups())

        current_block = self.matching_blocks[self.match_level]
        if self.pattern_close:
            matchObj = re.match(self.pattern_close, line)
            if matchObj:
                if self.nested_blocks:
                    self.match_level -= 1
                    self.matching_blocks.pop()
                else:
                    self.matching_blocks[0] = "root"
                return MatchObj(MATCH_CLOSE, self.pattern_close,
                                        current_block, matchObj.groups())

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
