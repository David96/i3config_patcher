from xdg.BaseDirectory import xdg_config_home, xdg_data_home
import shutil
import os
import logging

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
                logging.debug("Applying %s for %s", self.name, name)
                self.__get_merger_for_software(name).apply(name, self)
        Config().set("theme", self.name)

    def __get_merger_for_software(self, software):
        if software not in self.mergers:
            return None
        mergers = self.mergers[software]
        return max(mergers, key=lambda x:x.get_priority())

class Themes:
    """
        Functionality to load themes from XDG_DATA_HOME/config_patcher
        (usually ~/.local/share/config_patcher/)

        When patching a file, it is checked whether it already exists
        in the »originals« theme, if not, it is copied to
        THEME_DIR/originals/software/file.
        When a theme is applied, the style is applied to the originals.
        The actual config files are overwritten, so changes should be made
        inside the originals theme, reapplying the style afterwards.

        Resetting to them is possible by applying the originals theme.
    """

    def __init__(self):
        self.mergers = self.__load_mergers()
        os.makedirs(os.path.join(THEME_PATH, "originals"), exist_ok=True)
        self.original = self.load_theme("originals")

    def load_theme(self, name):
        theme_dir = os.path.join(THEME_PATH, name)
        if not os.path.isdir(theme_dir):
            return None
        files = self.__load_files(theme_dir)
        return Theme(name, files, self.mergers, self)

    def backup_if_necessary(self, software, name, filename):
        if Config().get("theme") == "originals" or \
                not software in self.original.files or \
                not name in self.original.files[software]:
            logging.debug("Backing up %s" % filename)
            files_dir = os.path.join(THEME_PATH, "originals", software)
            os.makedirs(files_dir, exist_ok=True)
            shutil.copyfile(filename, os.path.join(files_dir, name))
            self.original = self.load_theme("originals")

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
                        merger = m()
                        logging.debug("Found merger for %s", \
                                merger.get_supported_software().keys())
                        for software in merger.get_supported_software():
                            if software in mergers:
                                mergers[software].append(merger)
                            else:
                                mergers[software] = [ merger ]
                except AttributeError:
                    logging.warning("Merger %s found but doesn't implement a Merger class inheriting from BaseMerger", name)
        return mergers
