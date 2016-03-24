from xdg.BaseDirectory import xdg_config_home, xdg_data_home
import shutil
import os
from config import Config
from merger import BaseMerger

THEME_PATH = os.path.join(xdg_data_home, "config_patcher")

class Theme:
    """
        The structure of a theme is very simple.
        The name of it is the name of its directory,
        which includes one directory for each software it supports
        containing the config files to use.

        Example structure::

            blue/
            --->i3/
            ------->config

        This would create a theme »blue« including a config file for i3
    """
    def __init__(self, name, files, mergers, themes):
        self.name = name
        self.files = files
        self.mergers = mergers
        self.themes = themes

    def apply(self):
        for name,files in self.files.items():
            if name in self.mergers:
                print("Merging %s for %s" % (name, files))
                self.mergers[name].apply(self.themes.original.files[name], files)
        Config().set("theme", self.name)

class Themes:
    """
        Functionality to load themes from XDG_DATA_HOME/config_patcher
        (usually ~/.local/share/config_patcher/)

        The first time it is run it backups all files that are supported
        by any merger into the "originals" theme.
        When a theme is applied, the style is applied to the originals.
        The actual config files are overwritten, so changes should be made
        inside the originals theme, reapplying the style afterwards.

        Resetting to them is possible by applying the originals theme.

        TODO: improve this backup system. It is bad.
    """

    def __init__(self):
        self.mergers = self.__load_mergers()
        if not os.path.exists(os.path.join(THEME_PATH, "originals")):
            self.backup_config()
        self.original = self.load_theme("originals")

    def load_theme(self, name):
        theme_dir = os.path.join(THEME_PATH, name)
        files = self.__load_files(theme_dir)
        if files:
            return Theme(name, files, self.mergers, self)
        return None

    def backup_config(self, software=None):
        if software:
            files = self.merger[software].files
            path = os.path.join(THEME_PATH, "originals", software)
            for name, files in files.items():
                for f in files:
                    if os.access(f, os.R_OK):
                        dirname = os.path.dirname(os.path.join(path, name))
                        if not os.path.exists(dirname):
                            os.makedirs(dirname)
                        shutil.copyfile(f, os.path.join(path, name))
        else:
            for m in self.merger:
                self.backup_config(m)

    def __load_files(self, directory):
        if os.path.isdir(directory):
            dirs = [ name for name in os.listdir(directory) \
                    if os.path.isdir(os.path.join(directory, name)) ]
            files = {}
            for d in dirs:
                files[d] = { name : os.path.join(directory, d, name) \
                        for name in os.listdir(os.path.join(directory, d)) \
                        if os.path.isfile(os.path.join(directory, d, name)) }
            return files
        return None

    def __load_mergers(self):
        mergers = {}
        for f in os.scandir(os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "mergers")):
            if f.is_file() and f.name.endswith(".py"):
                name = f.name[:-3]
                mod = __import__("mergers.%s" % name, fromlist=["Merger"])
                try:
                    m = getattr(mod, "Merger")
                    if issubclass(m, BaseMerger):
                        print("Found merger for %s" % name)
                        mergers[name] = m()
                except AttributeError:
                    print("Merger %s found but doesn't implement a Merger class inheriting from BaseMerger" % name)
        return mergers
