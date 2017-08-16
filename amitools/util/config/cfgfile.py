"""parse a config file with python's configparser"""

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
