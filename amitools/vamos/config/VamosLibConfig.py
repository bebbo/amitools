class VamosLibConfig:
    """A vamos library configuration object.
    """

    def __init__(self, name, mode='auto', version=0,
                 profile=False, expunge='last_close'):
        self.name = name
        self.mode = mode
        self.version = version
        self.profile = profile
        self.expunge = expunge
        # types of keys
        self._keys = {
            'mode': str,
            'version': int,
            'profile': bool,
            'expunge': str
        }

    def __repr__(self):
        return "VamosLibConfig({},mode={},version={},profile={},expunge={})" \
            .format(self.name, self.mode, self.version, self.profile,
                    self.expunge)

    def dump(self, logger):
        for key in sorted(self._keys):
            logger.debug("config: [%s]  %s = %s",
                         self.name, key, getattr(self, key))

    def parse_key_value(self, lib_name, kv_str, errors):
        """parse a key value string: k=v,k=v,..."""
        kvs = kv_str.split(',')
        if len(kvs) == 0:
            errors.append("%s: No key,value given in -o option: '%s'" %
                          (lib_name, kv_str))
        else:
            for kv in kvs:
                r = kv.split('=')
                if len(r) != 2:
                    errors.append("%s: Syntax error: '%s'" % (lib_name, kv))
                else:
                    k, v = r
                    self.set_value(lib_name, k, v, errors)

    def set_value(self, lib_name, k, v, errors):
        if k in self._keys:
            t = self._keys[k]
            try:
                rv = t(v)
                # validate value
                check_name = '_check_' + k
                if hasattr(self, check_name):
                    check_func = getattr(self, check_name)
                    if check_func(rv):
                        setattr(self, k, rv)
                    else:
                        errors.append("%s: invalid '%s' value: '%s'" %
                                      (lib_name, k, rv))
                # no validation available
                else:
                    setattr(self, k, rv)
            except ValueError:
                errors.append(
                    "%s: invalid '%s' value: '%s' for type %s" %
                    (lib_name, k, v, t))
        else:
            errors.append("%s: invalid key: '%s'" % (lib_name, k))

    def _check_mode(self, v):
        return v in ('auto', 'vamos', 'amiga', 'fake', 'off')

    def _check_version(self, v):
        return v >= 0

    def _check_expunge(self, v):
        return v in ('last_close', 'shutdown', 'no_mem')
