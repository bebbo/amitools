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

    def set_entry(self, grp_name, name, val):
        grp = self._add_group(grp_name)
        grp[name] = val
