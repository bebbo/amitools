class ConfigCreator(object):

    def __init__(self):
        self.config = {}

    def get_cfg_set(self):
        return self.config

    def _add_group(self, name):
        if name in self.config:
            return self.config[name]
        else:
            grp = {}
            self.config[name] = grp
            return grp

    def _set_entry(self, grp_entry, grp_name, val_entry, val_name, val):
        # group by key?
        group_by_name = grp_entry.get_key().do_group_by_name()
        if group_by_name is not None:
            # add a top-level group with grp_key name
            top_grp = self._add_group(group_by_name)
            # add custom group
            if grp_name in top_grp:
                grp = top_grp[grp_name]
            else:
                grp = {}
                top_grp[grp_name] = grp
        else:
            grp = self._add_group(grp_name)
        grp[val_name] = val

    def parse_entry(self, cfg_file, cfg_set, logger,
                    grp_name, val_name, in_val):
        # find associated group
        grp_entry = cfg_set.match_key(grp_name)
        if grp_entry is None:
            # section not found!
            logger.warning("%s: invalid group '%s'",
                           cfg_file, grp_name)
        else:
            grp = grp_entry.get_value()
            # find associated option
            val_entry = grp.match_key(val_name)
            if val_entry is None:
                # option not found!
                logger.warning(
                    "%s: invalid value '%s.%s'",
                    cfg_file, grp_name, val_name)
            else:
                val = val_entry.get_value()
                # parse option value
                try:
                    out_val = val.parse_value(in_val)
                    # store in result
                    self._set_entry(grp_entry, grp_name,
                                    val_entry, val_name,
                                    out_val)
                except ValueError as e:
                    logger.error("%s: failed parsing '%s.%s': %s",
                                 cfg_file, grp_name, val_name, e)
                    return False
        return True
