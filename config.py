from xdg.BaseDirectory import xdg_config_home
import os
from configparser import ConfigParser

CONFIG_PATH = os.path.join(xdg_config_home, "config_patcher")
CONFIG_FILE = os.path.join(CONFIG_PATH, "config")

class Config:
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    def __init__(self):
        try:
            self.config
        except:
            if not os.path.exists(CONFIG_PATH):
                os.makedirs(CONFIG_PATH)

            self.config = ConfigParser()
            self.config.read(CONFIG_FILE)

    def set(self, name, value, section="default"):
        try:
            self.config[section][name] = value
        except:
            self.config[section] = {name: value}
        self.write()

    def get(self, name, section="default"):
        try:
            return self.config[section][name]
        except KeyError:
            return None

    def get_all(self, section="default"):
        try:
            return self.config._sections[section]
        except KeyError:
            return None

    def write(self):
        with open(CONFIG_FILE, "w") as f:
            self.config.write(f)
