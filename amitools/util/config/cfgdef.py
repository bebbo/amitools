"""combine config keys and values to groups and groups to sets"""

from .key import ConfigKey


class ConfigEntry(object):
    """a config entry combines a key with a value"""

    def __init__(self, key, val, group_by_name=None):
        self.key = key
        self.val = val
        self.group_by_name = group_by_name

    def get_key(self):
        return self.key

    def get_value(self):
        return self.val

    def get_group_by_name(self):
        return self.group_by_name


class ConfigGroup(object):
    """a config group combines a list of config entries.

    A config entry is specified by a key and value pair.
    By default the key is derived from the name of the value.
    """

    def __init__(self, name=None):
        self.entries = []
        self.name = name

    def get_name(self):
        return self.name

    def add_entry(self, e):
        """add a value by its name as a key.
        """
        self.entries.append(e)

    def add_value(self, name, val):
        key = ConfigKey(name)
        return self.add_key_value(key, val)

    def add_key_value(self, key, val):
        entry = ConfigEntry(key, val)
        self.entries.append(entry)
        return entry

    def match_key(self, name):
        """find a key and return the associated entry or None.
        """
        for e in self.entries:
            key = e.get_key()
            if key.match_key(name):
                return e
        return None

    def add_args(self, aparser, agroup=None):
        """automatically add arguments to a config args parser"""
        pass


class ConfigSet(object):
    """a config set combines a list of groups.
    """

    def __init__(self):
        self.groups = []

    def get_groups(self):
        return self.groups

    def add_entry(self, entry):
        if not isinstance(entry.get_value(), ConfigGroup):
            raise ValueError("entry must be a ConfigGroup")
        self.groups.append(entry)

    def add_group(self, name, grp, group_by_name=None):
        key = ConfigKey(name)
        return self.add_key_group(key, grp, group_by_name)

    def add_key_group(self, key, grp, group_by_name=None):
        entry = ConfigEntry(key, grp, group_by_name)
        self.groups.append(entry)
        return entry

    def add_named_group(self, grp, group_by_name=None):
        name = grp.get_name()
        return self.add_group(name, grp, group_by_name)

    def match_key(self, name):
        """find a key and return the associated entry or None.
        """
        for entry in self.groups:
            key = entry.get_key()
            if key.match_key(name):
                return entry
        return None
