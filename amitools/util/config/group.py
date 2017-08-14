"""combine config keys and values to groups and groups to sets"""

from .key import ConfigKey


class ConfigGroup(object):
    """a config group combines a list of config entries.

    A config entry is specified by a key and value pair.
    By default the key is derived from the name of the value.
    """

    def __init__(self, name):
        self.name = name
        self.entries = []

    def get_name(self):
        return self.name

    def add_value(self, val):
        """add a value by its name as a key.
        """
        name = val.get_name()
        key = ConfigKey(name)
        self.add_key_value(key, val)

    def add_key_value(self, key, val):
        """add a config entry by giving its key and value.
        """
        self.entries.append((key, val))

    def match_key(self, name):
        """find a key and return the associated (key, value) tuple or None.
        """
        for e in self.entries:
            key = e[0]
            if key.match_key(name):
                return e
        return None


class ConfigSet(object):
    """a config set combines a list of groups.
    """

    def __init__(self):
        self.groups = []

    def add_group(self, grp):
        name = grp.get_name()
        key = ConfigKey(name)
        self.add_key_group(key, grp)

    def add_key_group(self, key, grp):
        self.groups.append((key, grp))

    def match_key(self, name):
        """find a key and return the associated (key, group) tuple or None.
        """
        for g in self.groups:
            key = g[0]
            if key.match_key(name):
                return g
        return None
