"""define config types for paths, assigns and volumes"""

from amitools.util.config import *


class AmigaDOSNameKey(ConfigKeyRegEx):
    """a key that accepts valid AmigaDOS names"""

    def __init__(self):
        super(AmigaDOSNameKey, self).__init__("[^/:]+")


class AmigaDOSAbsPathValue(ConfigRegExValue):
    """an absolute Amiga path, may start with an assign name"""

    def __init__(self, is_abs=True):
        super(AmigaDOSAbsPathValue, self).__init__("[^/:]+:([^/].*)?")


class VolumeConfigGroup(ConfigGroup):
    """define volume names and assign existing directories"""

    def __init__(self):
        super(VolumeConfigGroup, self).__init__()
        key = AmigaDOSNameKey()
        val = ConfigPathValue(must_exist=True, is_dir=True,
                              make_abs=True, expand=True)
        self.add_key_value(key, val)


class AssignConfigGroup(ConfigGroup):
    """define assigns by setting a non-empty list of paths"""

    def __init__(self):
        super(AssignConfigGroup, self).__init__()
        key = AmigaDOSNameKey()
        val = AmigaDOSAbsPathValue()
        vlist = ConfigValueList(val, allow_empty=False)
        self.add_key_value(key, vlist)


class PathConfigGroup(ConfigGroup):
    """define the command search path for the shell"""

    def __init__(self):
        super(PathConfigGroup, self).__init__()
        val = AmigaDOSAbsPathValue()
        vlist = ConfigValueList(val, allow_empty=False)
        self.add_value("path", vlist)
