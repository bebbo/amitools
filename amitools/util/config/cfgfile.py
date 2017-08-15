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

    def parse(self, cfg_set, creator, logger):
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

        # find associated group
        key_grp = cfg_set.match_key(sect)
        if key_grp is None:
            # section not found!
            logger.warning("%s: invalid section '%s'",
                           self.cfg_file, sect)
        else:
            grp = key_grp[1]
            # find associated option
            key_val = grp.match_key(opt)
            if key_val is None:
                # option not found!
                logger.warning(
                    "%s: invalid option '%s.%s'",
                    self.cfg_file, sect, opt)
            else:
                val = key_val[1]
                # parse option value
                try:
                    out_val = val.parse_value(in_val)
                    # store in result
                    creator.set_entry(sect, opt, out_val)
                except ValueError as e:
                    logger.error("%s: failed parsing '%s.%s': %s",
                                 self.cfg_file, sect, opt, e)
                    return False
        return True
