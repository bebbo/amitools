"""config key classes to match entries"""

import fnmatch
import re


class ConfigKeyBase(object):

    def __init__(self, case=False, group_by_name=None):
        self.case = case
        self.group_by_name = group_by_name

    def do_group_by_name(self):
        return self.group_by_name

    def _match_str(self, a, b):
        if self.case:
            return a == b
        else:
            return a.lower() == b.lower()


class ConfigKey(ConfigKeyBase):
    """a simple key matcher that exactly matches its name

    Args:
        key (str): key name
        case (bool, optional): compare name case (in)sensitive
    """

    def __init__(self, key, case=False, group_by_name=None):
        super(ConfigKey, self).__init__(case, group_by_name)
        self.key = key

    def get_key(self):
        return self.key

    def match_key(self, key):
        """pass a key an return true if match was found

        Args:
            key (str): key to match
        Returns:
            bool    True if match, False otherwise
        """
        return self._match_str(self.key, key)


class ConfigKeyList(ConfigKeyBase):
    """match against a list of keys

    Args:
        name (str): key name
        keys ([str]): list of keys to match
        case (bool): case sensitive match
    """

    def __init__(self, keys, case=False, group_by_name=False):
        super(ConfigKeyList, self).__init__(case, group_by_name)
        self.keys = keys

    def match_key(self, key):
        for k in self.keys:
            if self._match_str(k, key):
                return True
        return False


class ConfigKeyGlob(ConfigKeyBase):
    """match against a shell glob pattern

    Args:
        name (str): key name
        glob (str): string with glob pattern
        case (bool): case sensitive match
    """

    def __init__(self, glob, case=False, group_by_name=False):
        super(ConfigKeyGlob, self).__init__(case, group_by_name)
        if case:
            self.glob = glob
        else:
            self.glob = glob.lower()

    def match_key(self, key):
        if self.case:
            return fnmatch.fnmatchcase(key, self.glob)
        else:
            return fnmatch.fnmatchcase(key.lower(), self.glob)


class ConfigKeyRegEx(ConfigKeyBase):
    """match against a regular expression.

    Args:
        name(str): key name
        regex(str): regex to match
        case (bool): case sensitve match
    """

    def __init__(self, regex, case=False, group_by_name=False):
        super(ConfigKeyRegEx, self).__init__(case, group_by_name)
        self.regex = regex
        self.prog = re.compile(regex, 0 if case else re.IGNORECASE)

    def match_key(self, key):
        m = self.prog.match(key)
        if m is None:
            return False
        else:
            # full match?
            return m.end() == len(key)
