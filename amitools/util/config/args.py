

class ValueArgParser(object):

    def __init__(self, grp_name, val_name):
        self.grp_name = grp_name
        self.val_name = val_name

    def parse(self, cfg_set, creator, logger, in_val):
        # ignore empty
        if in_val is None:
            return True
        return creator.parse_entry("args", cfg_set, logger,
                                   self.grp_name, self.val_name, in_val)


class DynValueArgParser(object):

    def __init__(self, grp_name, val_keys, val_sep, key_sep):
        self.grp_name = grp_name
        self.val_keys = val_keys
        self.val_sep = ',' if val_sep is None else val_sep
        self.key_sep = '=' if key_sep is None else key_sep

    def parse(self, cfg_set, creator, logger, in_val):
        if in_val is None:
            # ignore empty
            return True
        # in_val is a list
        for elem in in_val:
            ok = self._parse_pairs(cfg_set, creator, logger, elem,
                                   self.grp_name)
            if not ok:
                return False
        return True

    def _parse_pairs(self, cfg_set, creator, logger, in_val, grp_name):
        # first split line into key=value pairs
        pairs = in_val.split(self.val_sep)
        if len(pairs) == 0:
            logger.warning("args: empty option list: '%s'", in_val)
            return True
        # parse pairs
        for p in pairs:
            pos = p.find(self.key_sep)
            if pos == -1:
                logger.error("args: invalid key, value pair: '%s'", p)
                return False
            key = p[:pos]
            val = p[pos+1:]
            # check if key is valid
            ok = self._check_keys(key, self.val_keys)
            if not ok:
                logger.error("args: invalid key given: '%s'", key)
                return False
            # try to parse entry
            ok = creator.parse_entry("args", cfg_set, logger,
                                     grp_name, key, val)
            if not ok:
                return False
        return True

    def _check_keys(self, name, val_keys):
        # no check done
        if val_keys is None:
            return True
        # check keys
        for key in val_keys:
            if key.match_key(name):
                return True
        # no match
        return False


class DynGroupArgParser(DynValueArgParser):

    def __init__(self, grp_keys, val_keys, val_sep, key_sep, grp_sep):
        self.grp_keys = grp_keys
        self.val_keys = val_keys
        self.val_sep = ',' if val_sep is None else val_sep
        self.key_sep = '=' if key_sep is None else key_sep
        self.grp_sep = ':' if grp_sep is None else grp_sep

    def parse(self, cfg_set, creator, logger, in_val):
        # ignore empty in_val
        if in_val is None:
            return True
        # in_val is a list
        for elem in in_val:
            ok = self._parse_group(cfg_set, creator, logger, elem)
            if not ok:
                return False
        return True

    def _parse_group(self, cfg_set, creator, logger, in_val):
        # split group name from in_val
        pos = in_val.find(self.grp_sep)
        if pos == -1:
            logger.error("args: no group name given: '%s'", in_val)
            return False
        grp_name = in_val[:pos]
        rem_val = in_val[pos+1:]
        # check group name
        ok = self._check_keys(grp_name, self.grp_keys)
        if not ok:
            logger.error("args: invalid group name given: '%s'", grp_name)
            return False
        # parse key, values in this group
        return self._parse_pairs(cfg_set, creator, logger, rem_val,
                                 grp_name)


class ConfigArgsParser(object):
    """bind a config set to a number of command line arguments.

    Pass in an ``argparse`` parser instance and define the options
    you like to add. Then parse the all arguments and submit the
    resulting args to this parser. It will then create and fill
    the resulting config set.
    """

    def __init__(self, aparser):
        self.aparser = aparser
        self.entries = {}
        self.arg_groups = {}

    def _add_arg(self, arg_name, long_arg_name, desc, arg_group=None,
                 **kwargs):
        # build args
        args = [arg_name]
        if long_arg_name is not None:
            args.append(long_arg_name)
        # build kwargs
        arg_var, need_dest = self._get_arg_var(arg_name, long_arg_name)
        kwargs['help'] = desc
        if need_dest:
            kwargs['dest'] = arg_var
        # add argparse argument
        if arg_group is None:
            self.aparser.add_argument(*args, **kwargs)
        else:
            # does arg_group exist?
            if arg_group in self.arg_groups:
                ag = self.arg_groups[arg_group]
            else:
                ag = self.aparser.add_argument_group(arg_group)
                self.arg_groups[arg_group] = ag
            ag.add_argument(*args, **kwargs)
        return arg_var

    def _get_arg_var(self, arg_name, long_arg_name):
        # re-build arg_var derivation of argparse
        if arg_name[0] != '-':
            return arg_name, False
        elif long_arg_name is not None:
            if long_arg_name.startswith('--'):
                return long_arg_name[2:].replace('-', '_'), True
            else:
                raise ValueError("invalid long_arg_name: " + long_arg_name)
        else:
            if len(arg_name) == 2:
                return arg_name[1], True
            else:
                raise ValueError("invalid arg_name: " + arg_name)

    def add_bool_value(self, grp_name, val_name, arg_name,
                       long_arg_name=None, desc=None, default=False,
                       const=None, arg_group=None):
        """create an option argument that maps to a bool value.

        By default the value is set to ``False`` if arg is missing or set to
        ``True``if arg was found. Adjust ``default``value to change this
        behaviour.

        Args:
            grp_name (str): group name of value
            val_name (str): name of value in group
            arg_name (str): argument name for argparse, e.g. ``-a``
            long_arg_name (str, optional): long argument name, e.g. ``--foo``
            desc (str): argument description
            default (bool): value if arg is not set
            const (any): store this value if argument is set
            arg_group (argparse.Group, optional): add argument to group
        """
        # store action?
        if const is None:
            action = 'store_true' if not default else 'store_false'
            arg_var = self._add_arg(arg_name, long_arg_name, desc,
                                    default=default, action=action,
                                    arg_group=arg_group)
        else:
            action = 'store_const'
            arg_var = self._add_arg(arg_name, long_arg_name, desc,
                                    default=default, action=action,
                                    const=const, arg_group=arg_group)
        # create argument
        # add parser
        p = ValueArgParser(grp_name, val_name)
        self.entries[arg_var] = p

    def add_counter_value(self, grp_name, val_name, arg_name,
                          long_arg_name=None, desc=None, default=0,
                          arg_group=None):
        """create an option argument that maps to an integer counter.

        By default the value is set to ``default`` if arg is missing.
        Every time you mention the argument the counter is incremented by one.

        Args:
            grp_name (str): group name of value
            val_name (str): name of value in group
            arg_name (str): argument name for argparse, e.g. ``-a``
            long_arg_name (str, optional): long argument name, e.g. ``--foo``
            desc (str): argument description
            default (int): start value of counter
            arg_group (argparse.Group, optional): add argument to group
        """
        arg_var = self._add_arg(arg_name, long_arg_name, desc,
                                default=default, action='count',
                                arg_group=arg_group)
        p = ValueArgParser(grp_name, val_name)
        self.entries[arg_var] = p

    def add_value(self, grp_name, val_name, arg_name, long_arg_name=None,
                  desc=None, arg_group=None):
        """create an option argument that directly maps to value

        Args:
            grp_name (str): group name of value
            val_name (str): name of value in group
            arg_name (str): argument name for argparse, e.g. ``-a``
            long_arg_name (str, optional): long argument name, e.g. ``--foo``
            desc (str): argument description
            arg_group (argparse.Group, optional): add argument to group
        """
        # create argument
        arg_var = self._add_arg(arg_name, long_arg_name, desc,
                                arg_group=arg_group)
        # add parser
        p = ValueArgParser(grp_name, val_name)
        self.entries[arg_var] = p

    def add_dyn_value(self, grp_name, arg_name, long_arg_name=None,
                      val_keys=None, desc=None, val_sep=None, key_sep=None,
                      arg_group=None):
        """allows you to specify one or multiple values in a group.

        The added arg allows to set multiple values of a group by specifying
        a list of key and value pairs.

        By default the list looks like: ``key=value,key2=value2``.
        The ``val_sep`` is comma and the ``key_sep``is the equal sign.

        Args:
            grp_name (str): group name to assign values
            arg_name (str): argument name for argparse
            long_arg_name (str, optional): long argument name, e.g. ``--foo``
            val_keys ([ConfigKey], optional): list of keys to allow
            desc (str): argument description
            val_sep (str, optional): char to separate values, default: ``,``
            key_sep (str, optional): char to separate key and value, ``=``
            arg_group (argparse.Group, optional): add argument to group
        """
        arg_var = self._add_arg(arg_name, long_arg_name, desc,
                                action='append', arg_group=arg_group)
        # add parser
        p = DynValueArgParser(grp_name, val_keys, val_sep, key_sep)
        self.entries[arg_var] = p

    def add_dyn_group(self, grp_keys, arg_name, long_arg_name=None,
                      val_keys=None, desc=None, val_sep=None, key_sep=None,
                      grp_sep=None, arg_group=None):
        """allows you to specify one or multiple values in a set of groups.

        You specify an argument with a group name prefix first and then a
        list of key value pairs in this group. E.g. ``group:key=value``.

        Args:
            grp_keys ([ConfigKey]): allowed groups to be set
            arg_name (str): argument name for argparse
            long_arg_name (str, optional): long argument name, e.g. ``--foo``
            val_keys ([ConfigKey], optional): list of keys to allow
            desc (str): argument description
            val_sep (str, optional): char to separate values, default: ``,``
            key_sep (str, optional): char to separate key and value, ``=``
            grp_sep (str, optional): char to postfix group, ``:``
        """
        arg_var = self._add_arg(arg_name, long_arg_name, desc,
                                action='append', arg_group=None)
        # add parser
        p = DynGroupArgParser(grp_keys, val_keys, val_sep, key_sep, grp_sep)
        self.entries[arg_var] = p

    def parse(self, cfg_set, creator, logger, args):
        """perform the parse and config set generation.

        Submit the ``args`` created by the ``argparse`` to derive the
        config set
        """
        # run through the registered entries
        arg_dict = vars(args)
        for e in self.entries:
            # read args value
            in_val = arg_dict[e]
            parser = self.entries[e]
            # parse value
            if not parser.parse(cfg_set, creator, logger, in_val):
                return False
        return True
