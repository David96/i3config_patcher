from patternmerger import PatternMerger
from os import path
from xdg.BaseDirectory import xdg_config_home

class Merger(PatternMerger):
    def __init__(self):
        super().__init__({
                "general" :  ["^\s*colors\s", "^\s*color_\w+\s"]})
        self.files = {"config": [ path.join(xdg_config_home, "i3status/config") ] }
