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

LOG_FORMAT = '%(asctime)-15s  %(levelname)-10s  %(name)-10s  %(message)s'


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
        self.add_value("log_file", ConfigPathValue(
            expand=True, allow_none=True))
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


class LogSetup(object):
    """setup logging in a ConfigMainParser"""

    def __init__(self, main_cfg, def_level=logging.WARNING,
                 cfg_logger="config", cfg_level=logging.WARNING):
        self.main_cfg = main_cfg
        self.cfg_logger = cfg_logger
        # configs will be set after parsing
        self.log_cfg = None
        self.log_level_cfg = None
        # manage our loggers
        self.loggers = {}
        # get the cfg def and add sections for log and loglevel
        cfg_def = main_cfg.get_cfg_def()
        llg = ConfigLogLevelGroup()
        cfg_def.add_group("loglevel", llg)
        lg = ConfigLogGroup()
        cfg_def.add_group("log", lg)
        # add to arg parser
        ap = main_cfg.get_cfg_arg_parser()
        llg.add_args(ap)
        lg.add_args(ap)
        # setup defaults
        def_cfg = main_cfg.get_cfg_default_dict()
        def_cfg['log'] = {
            'log_file': None,
            'default_level': def_level
        }
        def_cfg['loglevel'] = {}
        # set config logger default level
        if self.cfg_logger is not None:
            def_cfg['loglevel'][self.cfg_logger] = cfg_level
        # setup post parse call
        main_cfg.add_post_parse_callback(self._setup)

    def _setup(self):
        """after config parsing is done we setup logging"""
        cfg_dict = self.main_cfg.get_cfg_dict()
        self.log_cfg = cfg_dict['log']
        self.log_level_cfg = cfg_dict['loglevel']
        # setup logging
        log_file = self.log_cfg['log_file']
        self.default_level = self._get_default_level()
        pl = self.main_cfg.get_pre_logger()
        pl.debug("logging basicConfig: filename=%s, level=%d",
                 log_file,
                 self.default_level)
        logging.basicConfig(format=LOG_FORMAT,
                            filename=log_file,
                            level=self.default_level)
        # finally log pre log entries
        cfg_logger = self.cfg_logger
        if cfg_logger is not None:
            logger = self.get_logger(cfg_logger)
            pre_logger = self.main_cfg.get_pre_logger()
            pre_logger.to_logger(logger)
            # replace pre_logger with real one
            self.main_cfg.set_logger(logger)

    def get_default_level(self):
        """return effective default level"""
        return self.default_level

    def shutdown(self):
        """flush logging resources"""
        logging.shutdown()

    def get_logger(self, name):
        # already created?
        if name in self.loggers:
            return self.loggers[name]
        # create new
        logger = logging.getLogger(name)
        self.loggers[name] = logger
        # check if it has a special level
        level = self._get_logger_level(name)
        if level is not None:
            logger.setLevel(level)
        return logger

    def _get_logger_level(self, name):
        pl = self.main_cfg.get_pre_logger()
        levels = self.log_level_cfg
        if name in levels:
            lvl = levels[name]
            pl.debug("logger level '%s' from config: %d", name, lvl)
            return lvl
        else:
            # if its not a sub logger
            pos = name.find('.')
            if pos == -1:
                lvl = self.default_level
                pl.debug("logger level '%s' from default: %d", name, lvl)
                return lvl
            else:
                pl.debug("logger level '%s' not set", name)

    def _get_default_level(self):
        lvl = self.log_cfg['default_level']
        verbose = self.log_cfg['verbose']
        quiet = self.log_cfg['quiet']
        delta = quiet - verbose
        if delta != 0:
            pl = self.main_cfg.get_pre_logger()
            new_lvl = self._adjust_level(lvl, delta)
            pl.debug("adjust default level: lvl=%d delta=%d -> lvl=%d",
                     lvl, delta, new_lvl)
            return new_lvl
        else:
            return lvl

    def _adjust_level(self, lvl, delta):
        # find level index
        try:
            pos = levels.index(lvl)
            if pos == -1:
                return lvl
            # adjust index
            pos += delta
            # out of range: clamp
            n = len(levels)
            if pos < 0:
                pos = 0
            elif pos >= n:
                pos = n-1
            # return level value
            return levels[pos]
        except:
            return lvl


# module log setup instance
_log_setup = None


def init(main_cfg, **kwargs):
    """module level init of logging.

    Note: call after creating MainConfig and before parsing config values.
    """
    global _log_setup
    if _log_setup is not None:
        raise RuntimeError("log: already initialized!")
    _log_setup = LogSetup(main_cfg, **kwargs)


def shutdown():
    """module level shutdown of logging"""
    global _log_setup
    if _log_setup is None:
        raise RuntimeError("log: not initialized!")
    _log_setup.shutdown()
    _log_setup = None


def get_logger(name):
    """module level logger access"""
    global _log_setup
    if _log_setup is None:
        raise RuntimeError("log: not initialized!")
    return _log_setup.get_logger(name)


def get_default_level():
    """module level logger access"""
    global _log_setup
    if _log_setup is None:
        raise RuntimeError("log: not initialized!")
    return _log_setup.get_default_level()
