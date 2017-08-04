import ConfigParser
import os
import os.path

from VamosLibConfig import VamosLibConfig


class VamosConfig(ConfigParser.SafeConfigParser):
    """The global vamos configuration object"""

    default_lib = '*.library'

    def __init__(self, extra_file=None, skip_defaults=False,
                 args=None, def_data_dir=None):
        ConfigParser.SafeConfigParser.__init__(self)
        self.def_data_dir = def_data_dir
        self.files = []
        self.args = args

        # keep errors until logging is available
        self.errors = []

        # prepend extra file
        if extra_file != None:
            self.files.append(extra_file)
        # read default config files (if they exist)
        if not skip_defaults:
            # add config in current working dir
            self.files.append(os.path.join(os.getcwd(), ".vamosrc"))
            # add config in home directory
            self.files.append(os.path.expanduser("~/.vamosrc"))

        # read configs
        self.found_files = self.read(self.files)

        # setup config
        self._reset()
        self._parse_config()
        self._parse_lib_config()
        self._parse_args(args)
        self._parse_lib_args(args)
        self._set_defaults()

    def validate(self, logger):
        """validate config values and return True for valid config.

        If something is not valid then traces are emitted accordingly.
        The method expects tracing to be setup correctly before.

        Args:
          logger  output config infos

        Returns:
          bool    True if config is valid otherwise false
        """
        if len(self.found_files) == 0:
            logger.warn("no config file found: %s" % ",".join(self.files))
        else:
            logger.info("read config file: %s" % ",".join(self.found_files))
        # dump config
        self._dump(logger)
        # print recorded errors
        ok = True
        if len(self.errors) > 0:
            ok = False
            for e in self.errors:
                log_main.error("config error: " + e)
        # check some values
        if ok:
            ok = self._normalize_values()
        return ok

    def _normalize_values(self):
        ok = True
        # normalize CPU value
        if self.cpu in ('68000', '000', '00'):
            self.cpu = '68000'
        elif self.cpu in ('68020', '020', '20'):
            self.cpu = '68020'
        elif self.cpu in ('68030', '030', '30'):
            # fake 030 CPU only to set AttnFlags accordingly
            self.cpu = '68030'
            log_main.info("fake 68030 CPU selected")
        else:
            log_main.error("Invalid CPU type: %s" % cfg.cpu)
            ok = False
        return ok

    def get_lib_config(self, lib_name, sane_name=None, use_default=True):
        """get a configuration object for the given lib"""
        # specific lib in config?
        if lib_name in self.libs:
            return self.libs[lib_name]
        # search addtional sane_name?
        if sane_name is not None:
            if sane_name in self.libs:
                return self.libs[sane_name]
        # default config
        if self.default_lib in self.libs and use_default:
            return self.libs[self.default_lib]
        # none found
        return None

    def get_args(self):
        """return the command line arguments"""
        return self.args

    def _dump(self, logger):
        # main config
        for key in sorted(self._keys):
            logger.debug("config: [vamos]  %s = %s", key, getattr(self, key))
        # lib configs
        for lib in sorted(self.libs):
            lib_cfg = self.libs[lib]
            lib_cfg.dump(logger)

    def _reset(self):
        # default library config
        # make sure exec and dos is taken from vamos
        self.libs = {
            '*.library': VamosLibConfig('*.library', 'auto', 40, False),
            'exec.library': VamosLibConfig('exec.library', 'vamos', 40, False),
            'dos.library': VamosLibConfig('dos.library', 'vamos', 40, False),
        }
        # define keys that can be set
        self._keys = {
            # logging
            'logging': (str, None),
            'verbose': (int, 0),
            'quiet': (bool, False),
            'benchmark': (bool, False),
            'log_file': (str, None),
            # low-level tracing
            'instr_trace': (bool, False),
            'memory_trace': (bool, False),
            'internal_memory_trace': (bool, False),
            'reg_dump': (bool, False),
            # cpu emu
            'cpu': (str, "68000"),
            'max_cycles': (int, 0),
            'cycles_per_block': (int, 1000),
            # system
            'ram_size': (int, 1024),
            'stack_size': (int, 4),
            'hw_access': (str, "cias+custom"),
            'shell': (bool, False),
            # dirs
            'data_dir': (str, self.def_data_dir),
            # paths
            'cwd': (str, None),
            'pure_ami_paths': (bool, False)
        }
        # prefill keys with None
        for key in self._keys:
            setattr(self, key, None)

    def _set_defaults(self):
        for key in self._keys:
            val = getattr(self, key)
            if val is None:
                def_val = self._keys[key][1]
                setattr(self, key, def_val)

    def _check_cpu(self, val):
        return val in ('68000', '68020', '68030',
                       '000', '020', '030',
                       '00', '20', '30')

    def _set_value(self, key, value):
        if key in self._keys:
            val_type = self._keys[key][0]
            try:
                rv = val_type(value)
                # check value
                check_name = '_check_' + key
                if hasattr(self, check_name):
                    check_func = getattr(self, check_name)
                    if(check_func(rv)):
                        setattr(self, key, rv)
                    else:
                        self.errors.append(
                            "Invalid '%s' value: '%s'" % (key, rv))
                else:
                    setattr(self, key, rv)
            except ValueError:
                self.errors.append(
                    "Invalid '%s' type: '%s' must be %s" %
                    (key, value, val_type))
        else:
            self.errors.append("Invalid key: '%s'" % key)

    def _parse_config(self):
        # parse [vamos] section
        sect = 'vamos'
        for key in self._keys:
            if self.has_option(sect, key) and getattr(self, key) is None:
                value = self.get(sect, key)
                self._set_value(key, value)

    def _parse_args(self, args):
        # get paramters from args (allow to overwrite existing settings)
        for key in self._keys:
            if hasattr(args, key):
                arg_value = getattr(args, key)
                if arg_value is not None:
                    self._set_value(key, arg_value)

    def _parse_lib_config(self):
        # run through all sections matching [<bla.library>]:
        for lib_name in self.sections():
            if lib_name.endswith('.library') or lib_name.endswith('.device'):
                # check for lib
                if lib_name in self.libs:
                    lib = self.libs[lib_name]
                else:
                    lib = VamosLibConfig(lib_name)
                    self.libs[lib_name] = lib
                # walk through options
                for key in self.options(lib_name):
                    if key in lib._keys:
                        v = self.get(lib_name, key)
                        # set value
                        lib.set_value(lib_name, key, v, self.errors)
                    else:
                        self.errors.append(
                            "%s: Invalid option: '%s'" % (lib_name, key))

    def _parse_lib_args(self, args):
        # parse lib options
        if hasattr(args, 'lib_options') and args.lib_options != None:
            for e in args.lib_options:
                # lib+key=value,key=value
                r = e.split('+')
                if len(r) != 2:
                    self.errors.append("Syntax error: '%s'" % e)
                else:
                    lib, kv = r
                    # generate lib name
                    if lib.endswith('.library') or lib.endswith('.device'):
                        lib_name = lib
                    else:
                        lib_name = lib + '.library'
                    # find or create config
                    if lib_name in self.libs:
                        # use already defined lib
                        lib_cfg = self.libs[lib_name]
                    else:
                        # create new lib
                        lib_cfg = VamosLibConfig(lib_name)
                        self.libs[lib_name] = lib_cfg
                    # parse key value
                    lib_cfg.parse_key_value(lib_name, kv, self.errors)
