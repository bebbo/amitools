"""parse a given dictionary and convert it into a normalized cfg dict"""


class ConfigDictParser(object):

    def __init__(self, cfg_dict):
        self.cfg_dict = cfg_dict

    def parse(self, cfg_set, creator, logger, args=None):
        for group in self.cfg_dict:
            group_dict = self.cfg_dict[group]
            for val_name in group_dict:
                in_val = group_dict[val_name]
                ok = creator.parse_entry("dict", cfg_set, logger,
                                         group, val_name, in_val)
                if not ok:
                    return False
        return True
