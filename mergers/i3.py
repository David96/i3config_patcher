from patternmerger import PatternMerger
from os import path
from xdg.BaseDirectory import xdg_config_home

class Merger(PatternMerger):
    def __init__(self):
        super().__init__({
                "root" :  ["^\s*font\s", "^\s*client\.\w+", "^\s*new_window\s",
                                    "^\s*new_float\s", "^\s*hide_edge_borders\s"],
                "bar":    ["^\s*strip_workspace_numbers\s",
                                    "^\s*font\s", "^\s*mode\s"],
                "colors": [".*"]})
        self.files = {"config": [ "~/.i3/config", path.join(xdg_config_home, "i3/config") ] }
