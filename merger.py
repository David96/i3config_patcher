import os

class BaseMerger:
    """
        All mergers have to extend this class.

        Things to declare:
            self.files = { name : [path1, path2, ...], ... }: (declare in __init__)
                path1, path2, ...:  possible places where the supported software may store the specific config file.
                                    expanduser is called on them, so you can use paths like ~/.bla/blubb

                name: the name of the file in a theme.

                Example: self.files = {"config": [ "~/.i3/config"), path.join(xdg_config_home, "i3/config") ] }

            def merge(self, name, oldconfig, newconfig):
                When a theme is applied, this is called for each file we declared to support in self.files
                and that is included in the theme

                Params:
                    name: the name of the file to merge in the theme

                    oldconfig: the path to the original config

                    newconfig: the path to the config to merge

                returns:
                    a list containing the patched config line by line
    """

    def apply(self, orig_files, new_files):
        if not hasattr(self, "files"):
            raise AttributeError("%s.%s doesn't have a »files« Attribute - read the docs about how and why to add it." % \
                    (self.__module__, type(self).__name__))
        for name, theme_path in new_files.items():
            if name in self.files:
                for orig_path in self.files[name]:
                    if os.access(os.path.expanduser(orig_path), os.W_OK):
                        with open(os.path.expanduser(orig_path), "w") as f:
                            f.writelines(self.merge(name, orig_files[name], theme_path))
                        break

