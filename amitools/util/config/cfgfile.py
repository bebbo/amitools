"""parse a config file with python's configparser"""

import os
try:
    # Py2.7
    import ConfigParser as configparser
except ImportError:
    import configparser


class ConfigFileParser(object):

    def __init__(self, cfg_file, fobj=None):
        self.cfg_file = cfg_file
        self.fobj = fobj
        self.legacy_opt = {}

    def add_legacy_option(self, old_sect, old_opt, new_sect, new_opt):
        """add a legacy mapping.

        Perform mapped lookup for given old option to new option and issue
        a legacy warning.
        """
        self.legacy_opt[(old_sect, old_opt)] = (new_sect, new_opt)

    def parse(self, cfg_set, creator, logger, args=None):
        cfg = configparser.ConfigParser()
        cfg.optionxform = str  # do not case convert

        # read config
        try:
            if self.fobj is not None:
                cfg.readfp(self.fobj, self.cfg_file)
            else:
                with open(self.cfg_file) as fh:
                    cfg.readfp(fh, self.cfg_file)
            logger.info("%s: config read", self.cfg_file)
        except configparser.Error as e:
            logger.error("%s: failed parsing: %s", self.cfg_file, e)
            return False

        # run through sections
        for sect in cfg.sections():
            for opt in cfg.options(sect):
                in_val = cfg.get(sect, opt)
                if not self._parse_sect_opt(cfg_set, creator, logger,
                                            sect, opt, in_val):
                    return False
        return True

    def _parse_sect_opt(self, cfg_set, creator, logger, sect, opt, in_val):
        # is it a legacy mapping?
        old_so = (sect, opt)
        if old_so in self.legacy_opt:
            sect, opt = self.legacy_opt[old_so]
            logger.warning("%s: legacy option '%s.%s' used."
                           " please use '%s.%s' now!",
                           self.cfg_file, old_so[0], old_so[1], sect, opt)

        return creator.parse_entry(self.cfg_file, cfg_set, logger,
                                   sect, opt, in_val)


class ConfigFileManager(object):
    """The ConfigFileManager handles a set of config files.

    You can define both global config files and a local files to be read in
    order.

    Additionally, you can add argparse switches to disable reading the global
    config files first and also specify an alternate config file.
    """

    def __init__(self, app_name, add_default_global=True):
        self.app_name = app_name
        self.global_files = []
        # set default names
        self.def_cfg_name = ".{}rc".format(self.app_name)
        self.def_global_cfg = "~/{}".format(self.def_cfg_name)
        self.def_local_cfg = self.def_cfg_name
        # add a default global file
        if add_default_global:
            self.global_files.append((self.def_global_cfg, None))
        # set the local file
        self.local_file = (self.def_local_cfg, None)

    def get_default_config_name(self):
        return self.def_cfg_name

    def get_default_global_config_file(self):
        return self.def_global_cfg

    def get_default_local_config_file(self):
        return self.def_local_cfg

    def set_global_config_file(self, path, fobj=None):
        self.global_files = [(path, fobj)]

    def add_global_config_file(self, path, fobj=None):
        """add a custom global config file"""
        self.global_files.append((path, fobj))

    def set_local_config_file(self, path, fobj=None):
        self.local_file = (path, fobj)

    def add_args(self, argparser, agroup=None):
        if agroup is None:
            agroup = argparser.add_argument_group("config file")
        self.add_skip_global_config_arg(argparser, agroup=agroup)
        self.add_select_local_config_arg(argparser, agroup=agroup)

    def add_skip_global_config_arg(self, argparser,
                                   name=None, long_name=None, agroup=None):
        """add a switch to the argparser to disable the global config file

        By default the switch ``-S`` and long name ``--skip-global-config``
        is used.
        """
        if name is None:
            name = '-S'
            if long_name is None:
                long_name = '--skip-global-config'
        args = [name]
        if long_name is not None:
            args.append(long_name)
        # options
        gf_txt = ",".join(map(lambda x: x[0], self.global_files))
        help_txt = 'do not read the global config files ({})'.format(gf_txt)
        kwargs = {
            'default': False,
            'action': 'store_true',
            'help': help_txt,
            'dest': 'skip_global_config'
        }
        if agroup is None:
            argparser.add_argument(*args, **kwargs)
        else:
            agroup.add_argument(*args, **kwargs)

    def add_select_local_config_arg(self, argparser,
                                    name=None, long_name=None, agroup=None):
        """add an argument to argparser that allows to pick the local config.

        By default the switch ``-c`` and ``--config-file`` is used.
        """
        if name is None:
            name = '-c'
            if long_name is None:
                long_name = '--config-file'
        args = [name]
        if long_name is not None:
            args.append(long_name)
        # options
        lf = self.local_file[0]
        help_txt = 'read the local config from given file (default: {})' \
            .format(lf)
        kwargs = {
            'help': help_txt,
            'default': None,
            'dest': 'config_file'
        }
        if agroup is None:
            argparser.add_argument(*args, **kwargs)
        else:
            agroup.add_argument(*args, **kwargs)

    def parse(self, cfg_set, creator, logger, args=None):
        # check args
        skip_global = False
        lf, lfobj = self.local_file
        if args is not None:
            skip_global = getattr(args, 'skip_global_config', skip_global)
            nlf = getattr(args, 'config_file', None)
            if nlf is not None:
                lf, lfobj = nlf, None
        else:
            nlf = None
        # first read global configs
        if not skip_global:
            for gfp in self.global_files:
                gf, gfobj = gfp
                gf = os.path.expanduser(gf)
                if gfobj is not None or os.path.isfile(gf):
                    logger.info("%s: reading global config", gf)
                    p = ConfigFileParser(*gfp)
                    ok = p.parse(cfg_set, creator, logger, args)
                    if not ok:
                        return False
                else:
                    logger.info("%s: skipping global config", gf)
        # finally, read local config
        lf = os.path.expanduser(lf)
        if lfobj is not None or os.path.isfile(lf):
            logger.info("%s: reading local config", lf)
            p = ConfigFileParser(lf, lfobj)
            ok = p.parse(cfg_set, creator, logger, args)
            if not ok:
                return False
        else:
            # if local file is not default then warn
            if nlf is not None:
                logger.warning("%s: can't find local config!", lf)
            else:
                logger.info("%s: skipping local config", lf)
        return True
