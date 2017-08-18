"""config key classes to match entries"""

import fnmatch
import re


class ConfigKey(object):
    """a simple key matcher that exactly matches its name

    Args:
        name (str): key name
        case (bool, optional): compare name case (in)sensitive
    """

    def __init__(self, name, case=False, group_by_key=False):
        self.name = name
        self.case = case
        self.group_by_key = group_by_key

    def __eq__(self, other):
        """compare a key by its name only."""
        return self.name == other.name

    def do_group_by_key(self):
        return self.group_by_key

    def get_name(self):
        return self.name

    def match_key(self, key):
        """pass a key an return true if match was found

        Args:
            key (str): key to match
        Returns:
            bool    True if match, False otherwise
        """
        return self._match_str(self.name, key)

    def _match_str(self, a, b):
        if self.case:
            return a == b
        else:
            return a.lower() == b.lower()


class ConfigKeyList(ConfigKey):
    """match against a list of keys

    Args:
        name (str): key name
        keys ([str]): list of keys to match
        case (bool): case sensitive match
    """

    def __init__(self, name, keys, case=False, group_by_key=False):
        super(ConfigKeyList, self).__init__(name, case, group_by_key)
        self.keys = keys

    def match_key(self, key):
        for k in self.keys:
            if self._match_str(k, key):
                return True
        return False


class ConfigKeyGlob(ConfigKey):
    """match against a shell glob pattern

    Args:
        name (str): key name
        glob (str): string with glob pattern
        case (bool): case sensitive match
    """

    def __init__(self, name, glob, case=False, group_by_key=False):
        super(ConfigKeyGlob, self).__init__(name, case, group_by_key)
        if case:
            self.glob = glob
        else:
            self.glob = glob.lower()

    def match_key(self, key):
        if self.case:
            return fnmatch.fnmatchcase(key, self.glob)
        else:
            return fnmatch.fnmatchcase(key.lower(), self.glob)


class ConfigKeyRegEx(ConfigKey):
    """match against a regular expression.

    Args:
        name(str): key name
        regex(str): regex to match
        case (bool): case sensitve match
    """

    def __init__(self, name, regex, case=False, group_by_key=False):
        super(ConfigKeyRegEx, self).__init__(name, case, group_by_key)
        self.regex = regex
        self.prog = re.compile(regex, 0 if case else re.IGNORECASE)

    def match_key(self, key):
        m = self.prog.match(key)
        if m is None:
            return False
        else:
            # full match?
            return m.end() == len(key)
