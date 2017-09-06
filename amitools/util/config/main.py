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
        def_cfg (dict, optional): default config values stored in a dict
        cfg_name (str, optional): allows you to overwrite config file name
        **kwargs: extra args for argparse.ArgumentParser
    """

    def __init__(self, cfg_set, def_cfg=None, cfg_name=None, **kwargs):
        if def_cfg is None:
            def_cfg = {}
        self.cfg_set = cfg_set
        self.def_cfg = def_cfg
        self.argument_parser = argparse.ArgumentParser(**kwargs)
        self.logger = PreLogger()
        # config file name: derive from prog name
        if cfg_name is None:
            cfg_name = self.argument_parser.prog
        # parsers
        self.def_parser = ConfigDictParser(def_cfg)
        self.file_parser = ConfigFileManager(cfg_name)
        self.arg_parser = ConfigArgsParser(self.argument_parser)
        self.parsers = [self.def_parser, self.file_parser, self.arg_parser]
        # results
        self.args = None
        self.cfg_dict = None
        # for derived classes
        self._setup_arg_parser(self.arg_parser)
        self._setup_file_parser(self.file_parser)
        # post parse callbacks
        self.post_callbacks = []

    def _setup_arg_parser(self, arg_parser):
        grp_dict = {}
        for grp_entry in self.cfg_set.get_groups():
            grp = grp_entry.get_value()
            grp.add_args(arg_parser, )

    def _setup_file_parser(self, file_parser):
        # add switches to argument parser
        file_parser.add_args(self.argument_parser)

    def add_post_parse_callback(self, cb):
        self.post_callbacks.append(cb)

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

    def get_cfg_default_dict(self):
        """return the default dictionary"""
        return self.def_cfg

    def set_logger(self, logger):
        """replace the pre-logger once logging is fully setup"""
        self.logger = logger

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
        # post callbacks
        for cb in self.post_callbacks:
            res = cb()
            if res is not None and res is not True:
                return res
        return True
