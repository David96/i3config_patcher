import os
import logging

class BaseMerger:
    """
        All mergers have to extend this class.

        Must declare:
            :func:`get_supported_software`

            :func:`merge`

        Can declare:
            :func:`get_priority`

        See :class:`mergers.patternmerger.Merger` for an example implementation.
    """

    def merge(self, software, name, oldconfig, newconfig):
        """
            When a theme is applied, this is called for each file we declared to support in self.files
            and that is included in the theme

            :param name: the name of the file to merge in the theme
            :param oldconfig: the path to the original config
            :param newconfig: the path to the config to merge

            :returns: a list containing the patched config line by line
        """
        raise NotImplementedError

    def get_supported_software(self):
        """
            Tells us which software is supported by this merger.
            Must be overridden by inheriting classes.
            Example: :func:`mergers.patternmerger.Merger.get_supported_software`

            :returns: dict - { "software": {"theme-filename" : ["real", "filenames"]} }
        """
        raise NotImplementedError

    def get_priority(self):
        """
            Priority of the merger. If multiple mergers claim support for a software,
            the one with the highest priority is used.

            :default: 0
        """
        return 0

    def apply(self, software, theme):
        new_files = theme.files[software]
        files = self.get_supported_software()[software]
        logging.debug("Applying %s for %s" % (files, software))
        for name, theme_path in new_files.items():
            if name in files:
                for orig_path in files[name]:
                    filename = os.path.expanduser(orig_path)
                    if os.access(filename, os.W_OK):
                        theme.themes.backup_if_necessary(software, name, filename)
                        # reload orig files because the original theme might have
                        # changed (in case a backup was necessary)
                        orig_files = theme.themes.original.files[software]
                        with open(filename, "w") as f:
                            f.writelines(self.merge(software, name,
                                        orig_files[name], theme_path))
                        break

