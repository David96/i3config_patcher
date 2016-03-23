import os

class BaseMerger:
    """
        All mergers have to extend this class.

        Things to declare:
            .. function:: self.files = { name : [path1, path2, ...], ... }

                path1, path2, ...:  possible places where the supported software may store the specific config file.
                expanduser is called on them, so you can use paths like ~/.bla/blubb

                name: the name of the file in a theme.

                :example:

                .. code-block:: python

                    self.files = {"config": [ "~/.i3/config"),
                                    path.join(xdg_config_home, "i3/config") ] }

            .. function:: merge(self, name, oldconfig, newconfig)

                When a theme is applied, this is called for each file we declared to support in self.files
                and that is included in the theme

                :param name: the name of the file to merge in the theme
                :param oldconfig: the path to the original config
                :param newconfig: the path to the config to merge

                :returns: a list containing the patched config line by line

        See :class:`mergers.i3.Merger` for an example implementation.
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

