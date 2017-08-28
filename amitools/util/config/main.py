import argparse
from amitools.util.prelog import PreLogger
from .args import ConfigArgsParser
from .cfgfile import ConfigFileManager
from .cfgdict import ConfigDictParser
from .create import ConfigCreator


class ConfigMainParser(object):
    """the main config parser class

    The main parser combines a default config set stored in a dict
    with an argument parser and a

    Args:
        cfg_set (ConfigSet): configuration definition
        def_cfg (dict): default config values stored in a dict
        **kwargs: extra args for argparse.ArgumentParser
    """

    def __init__(self, cfg_set, def_cfg, **kwargs):
        self.cfg_set = cfg_set
        self.def_cfg = def_cfg
        self.argument_parser = argparse.ArgumentParser(**kwargs)
        self.logger = PreLogger()
        # parsers
        self.def_parser = ConfigDictParser(def_cfg)
        self.file_parser = ConfigFileManager(self.argument_parser.prog)
        self.arg_parser = ConfigArgsParser(self.argument_parser)
        self.parsers = [self.def_parser, self.file_parser, self.arg_parser]
        # results
        self.args = None
        self.cfg_dict = None
        # for derived classes
        self._setup_arg_parser(self.arg_parser)
        self._setup_file_parser(self.file_parser)

    def _setup_arg_parser(self, arg_parser):
        pass

    def _setup_file_parser(self, file_parser):
        # add switches to argument parser
        file_parser.add_select_local_config_arg(self.argument_parser)
        file_parser.add_skip_global_config_arg(self.argument_parser)

    def get_arg_parser(self):
        """return the argparse.ArgumentParser for additional setup"""
        return self.argument_parser

    def get_cfg_arg_parser(self):
        """return the arg parser to configure options"""
        return self.arg_parser

    def get_cfg_file_parser(self):
        """return the file parser to configure options"""
        return self.file_parser

    def get_pre_logger(self):
        """access the pre logger that records all parse messages"""
        return self.logger

    def get_args(self):
        """get argparse args"""
        return self.args

    def get_cfg_dict(self):
        """return the final config dict"""
        return self.cfg_dict

    def get_cfg_def(self):
        """return the config definition"""
        return self.cfg_set

    def parse(self, args=None, namespace=None):
        """main parse call. pass command args and get final config

        Returns:
            True if parsing was ok, otherwise False
        """
        # first call argparse
        self.args = self.argument_parser.parse_args(args, namespace)
        # now our parsers
        creator = ConfigCreator()
        for p in self.parsers:
            ok = p.parse(self.cfg_set, creator, self.logger, self.args)
            if not ok:
                return False
        self.cfg_dict = creator.get_cfg_set()
        return True
