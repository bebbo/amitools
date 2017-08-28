"""wrapper for Python's logging module to better support configuration"""

import logging
from .config import *

OFF = 100
level_map = {
    'off': OFF,
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'warn': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}
levels = (
    logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR,
    logging.CRITICAL, OFF
)


class ConfigLogLevelValue(ConfigEnumValue):
    """a log value to store logging levels"""

    def __init__(self):
        super(ConfigLogLevelValue, self).__init__(level_map)


class ConfigLogLevelGroup(ConfigGroup):
    """a group to store logger to level entries"""

    def __init__(self):
        super(ConfigLogLevelGroup, self).__init__()
        self.key = ConfigKeyRegEx("[A-Z_]+")
        self.val = ConfigLogLevelValue()
        self.add_key_value(self.key, self.val)

    def add_args(self, parser, grp_name='loglevel'):
        parser.add_dyn_value(grp_name, '-l', '--log-levels',
                             desc="set logging levels")


class ConfigLogGroup(ConfigGroup):
    """store logging configuration options"""

    def __init__(self):
        super(ConfigLogGroup, self).__init__()
        self.add_value("verbose", ConfigIntValue())
        self.add_value("quiet", ConfigIntValue())
        self.add_value("log_file", ConfigPathValue(expand=True))
        self.add_value("default_level", ConfigLogLevelValue())

    def add_args(self, parser, grp_name='log'):
        parser.add_counter_value(grp_name, 'verbose', '-v', '--verbose',
                                 desc="increase verbosity of logging output")
        parser.add_counter_value(grp_name, 'quiet', '-q', '--quiet',
                                 desc="increase quietness of logging output")
        parser.add_value(grp_name, 'log_file', '-L', '--log-file',
                         desc="set output log file")
        parser.add_value(grp_name, 'default_level', '-D', '--default-level',
                         desc="set default logging level")
