class AmiPathError(Exception):

    def __init__(self, path, reason):
        self.path = path
        self.reason = reason

    def __str__(self):
        return "AmiPathError: %s: %s" % (self.path, self.reason)


class AmiPath(object):
    """holds a single Amiga path either in relative or absolute format.

    A path is considered 'absolute' if it starts with a volume: or
    assign: prefix.

    A relative path can only be resolved with the current directory stored
    in the associated path environment.

    A colon prefixed path is also considered relative, e.g. ':bla'.
    It is local to the prefix of the current directory.

    The empty string '' represents the current directory of the associated
    environment.

    In a 'volume path' all assigns are resolved and it
    always starts with a valid volume: prefix.

    Valid path syntax is:

    (prefix:)?(name)?(/name)+/?

    prefix: all but '/:', may be empty
    name: all but '/:', non-empty

    ':/', '//' is invalid
    """

    def __init__(self, pstr="", env=None, mgr=None):
        self.pstr = pstr
        self.env = env
        # set cache path manager (if any)
        if mgr is None:
            if env is not None:
                self.mgr = env.get_mgr()
            else:
                self.mgr = None
        else:
            self.mgr = mgr

    def __str__(self):
        return self.pstr

    def __repr__(self):
        return "AmiPath('{}',env={},mgr={})" \
            .format(self.pstr, self.env, self.mgr)

    def get_str(self):
        """get the path as a string"""
        return self.pstr

    def get_env(self):
        """return the associated path environemnt (if any)"""
        return self.env

    def get_mgr(self):
        """return the associated path manager (if any)"""
        return self.mgr

    def _ensure_mgr(self):
        if self.mgr is None:
            raise ValueError("path manager required!")
        return self.mgr

    def _ensure_env(self):
        if self.env is None:
            raise ValueError("path env required!")
        return self.env

    def is_local(self):
        """is it a local path?"""
        return self.pstr.find(':') <= 0

    def is_absolute(self):
        """is it an absolute path starting with a volume/assign prefix?"""
        return self.pstr.find(':') > 0

    def is_parent_local(self):
        """check if the path is relative to parent"""
        p = self.pstr
        return len(p) > 0 and p[0] == '/'

    def is_prefix_local(self):
        """check if the path is relative to the prefix"""
        p = self.pstr
        return len(p) > 0 and p[0] == ':'

    def is_name_only(self):
        """check if the relative path is a single name only"""
        p = self.pstr
        if len(p) == 0:
            return False
        ps = p.find('/')
        pc = p.find(':')
        return ps == -1 and pc == -1

    def ends_with_name(self):
        """make sure the path ends with a name

        A path ending with / or : is not valid.
        """
        p = self.pstr
        # empty is invalid
        if len(p) == 0:
            return False
        # last char must not be colon or slash
        lc = p[-1]
        if lc == '/' or lc == ':':
            return False
        return True

    def prefix(self):
        """if the path is absolute then a prefix string is returned.

        The prefix in a valid abs path is either an assign or volume name.

        A relative path has a None prefix.
        """
        pos = self.pstr.find(':')
        if pos <= 0:
            return None
        else:
            return self.pstr[:pos]

    def postfix(self, skip_leading=False):
        """the postfix string of the path.

        A relative path is returned as is.
        The postifx of an absolute path is starting with the colon ':'
        """
        p = self.pstr
        pos = p.find(':')
        # skip prefix
        if pos > 0:
            p = p[pos+1:]
        # strip trailing slash if any
        if len(p) > 1 and p[-1] == '/':
            p = p[:-1]
        # strip parent local
        if skip_leading and len(p) > 0 and p[0] in ('/', ':'):
            p = p[1:]
        return p

    @classmethod
    def build(cls, prefix=None, postfix="", env=None, mgr=None):
        """rebuild a path from prefix and postfix"""
        if prefix is None:
            pstr = postfix
        else:
            pstr = prefix + ":" + postfix
        return cls(pstr, env, mgr)

    def rebuild(self, prefix, postfix):
        return AmiPath.build(prefix, postfix, self.env, self.mgr)

    def __eq__(self, other):
        if not isinstance(other, AmiPath):
            return False
        return self.prefix() == other.prefix() and \
            self.postfix() == other.postfix()

    def __ne__(self, other):
        if not isinstance(other, AmiPath):
            return True
        return self.prefix() != other.prefix() or \
            self.postfix() != other.postfix()

    def is_valid(self):
        if not self.is_syntax_valid():
            return False
        if self.is_absolute():
            return self.is_prefix_valid()
        else:
            return True

    def is_syntax_valid(self):
        """check if a path has valid syntax.

        Returns True if all checks passed otherwise False
        """
        # valid cases
        s = self.pstr
        if s in (':', '', '/'):
            return True
        # invalid cases
        if s.find('//') != -1:
            return False
        # colon/slash check
        colon_pos = self.pstr.find(':')
        slash_pos = self.pstr.find('/')
        # a slash before the colon is not allowed
        if slash_pos > -1 and slash_pos < colon_pos:
            return False
        # slash follows colon
        if colon_pos > -1 and colon_pos + 1 == slash_pos:
            return False
        # is there a second colon?
        if colon_pos != -1:
            other_pos = self.pstr.find(':', colon_pos+1)
            if other_pos != -1:
                return False
        # all checks passed
        return True

    def is_prefix_valid(self):
        """check if prefix is either a volume or assign name"""
        p = self.prefix()
        if p is None:
            raise AmiPathError(self, "no prefix in path")
        mgr = self._ensure_mgr()
        return mgr.is_prefix_name(p)

    def is_volume_path(self):
        """check if the prefix is a valid volume name.

        A relative path always returns False
        """
        p = self.prefix()
        if p is None:
            raise AmiPathError(self, "no prefix in path")
        mgr = self._ensure_mgr()
        return mgr.is_volume_name(p)

    def is_assign_path(self):
        """check if the prefix is a valid assign name.

        A relative path always returns False
        """
        p = self.prefix()
        if p is None:
            raise AmiPathError(self, "no prefix in path")
        mgr = self._ensure_mgr()
        return mgr.is_assign_name(p)

    def is_multi_assign_path(self):
        """check if path resolves to multiple paths"""
        if self.is_local():
            raise AmiPathError(self, "no prefix in path")
        # check if global path prefix contains multi assigns
        p = self.prefix()
        mgr = self._ensure_mgr()
        res = mgr.contains_multi_assigns(p)
        if res is None:
            raise AmiPathError(self, "no assign in prefix")
        return res

    def parent(self):
        """return a new path with the last path component removed.

        Returns None if stripping is not possible.

        The path is not expanded (to a absolute or even volume path)!

        Example:
            bar -> ''
            foo/bar -> foo
            baz:foo/bar -> baz:foo
            baz:foo -> ''
            /bar -> /
            / -> None
            :foo -> foo
            foo: -> None
        """
        p = self.postfix()
        if p in ('/', ':'):
            return None
        last_pos = p.rfind('/')
        if last_pos == -1:
            col_pos = p.find(':')
            # special case: ":foo" -> ":"
            if col_pos == 0:
                postfix = ':'
            # "foo:"
            elif col_pos == len(p) - 1:
                return None
            else:
                postfix = ''
        elif last_pos == 0:
            postfix = '/'
        else:
            postfix = p[:last_pos]
        return self.rebuild(self.prefix(), postfix)

    def get_names(self, with_special_name=False):
        """return a list of strings with the names contained in postfix

        Note if skip_leading is False then a parent or prefix local path
        gets a special name prefixed: '/' or ':'
        """
        p = self.postfix(not with_special_name)
        n = len(p)
        if n == 0:
            return []
        # add leading char as a special name
        if n > 0 and p[0] in ('/', ':'):
            res = [p[0]]
            if n == 1:
                return res
            else:
                return res + p[1:].split('/')
        else:
            return p.split("/")

    def join(self, opath):
        """join this path with the given path.

        If expand is True then this path can be made absolute if necessary.

        Note:May return None if join is not possible.
        """
        # if other is absolute then replace my path
        if opath.is_absolute():
            return opath
        # other is parent relative?
        elif opath.is_parent_local():
            if self.is_parent_local():
                raise AmiPathError(
                    self, "can't join two parent relative paths")
            # try to strip last name of my path
            my = self.parent()
            if my is not None:
                prefix = self.prefix()
                my_post = my.postfix()
                if my_post == '':
                    postfix = opath.postfix(True)
                elif my_post == ':':
                    postfix = ':' + opath.postfix(True)
                else:
                    postfix = my_post + opath.postfix()
                return self.rebuild(prefix, postfix)
            else:
                raise AmiPathError(self, "can't join parent relative path")
        # other is prefix local: ':bla'
        elif opath.is_prefix_local():
            prefix = self.prefix()
            skip = False if prefix is None else True
            postfix = opath.postfix(skip)
            return self.rebuild(prefix, postfix)
        # other is local
        else:
            prefix = self.prefix()
            my_post = self.postfix()
            o_post = opath.postfix()
            if my_post == '':
                postfix = o_post
            elif my_post in ('/', ':'):
                postfix = my_post + o_post
            else:
                postfix = my_post + '/' + o_post
            return self.rebuild(prefix, postfix)

    def abspath(self):
        """return an absolute path

        If the path is already absolute then return self.
        Otherwise create a new AmiPath object with the absolute path
        by joining this path with the current directory of the path env.
        """
        # already absolute?
        if self.is_absolute():
            return self
        # get current directory and join cur dir with my path
        env = self._ensure_env()
        cur_dir = env.get_cur_dir()
        return cur_dir.join(self)

    def volpath(self):
        """return a volume path.

        If its not a multi path then return the one and only resolved
        volume path for this path.

        For a multi path a AmiPathError is raised!
        """
        if self.is_local():
            return self.abspath()
        elif self.is_volume_path():
            return self
        else:
            # assigns
            p = self.prefix()
            mgr = self._ensure_mgr()
            res = mgr.resolve_assign(p, True)
            if len(res) == 1:
                return AmiPath(res[0]).join(AmiPath(self.postfix()))
            else:
                raise AmiPathError(self, "volpath() encountered multi assign!")

    def volpaths(self):
        """return a list of volume paths for this path.

        If the path resolves to multiple paths then all resulting paths
        are generated by recursevily applying multi-assigns.
        """
        if self.is_local():
            return [self.abspath()]
        elif self.is_volume_path():
            return [self]
        else:
            # assigns
            p = self.prefix()
            mgr = self._ensure_mgr()
            vpaths = mgr.resolve_assign(p, True)
            return list(map(lambda x: AmiPath(x).join(AmiPath(self.postfix())),
                            vpaths))

    def map_assign(self, recursive=False):
        """if path is prefixed by an assign name then resolve the assign.

        always returns a list as the assign might be a multi assign.

        otherwise return the path unmodified.
        """
        if self.is_absolute() and self.is_assign_path():
            p = self.prefix()
            mgr = self._ensure_mgr()
            vpaths = mgr.resolve_assign(p, recursive=recursive)
            return list(map(lambda x: AmiPath(x).join(AmiPath(self.postfix())),
                            vpaths))
        else:
            return [self]

    def cmdpaths(self, with_cur_dir=True, make_volpaths=True):
        """return a list of command paths derived from this path.

        If the path contains a name only then a list containing the
        current cmd paths form the path env are returned. If
        with_cur_dir is enabled then the current dir is added as well.

        If this path is not a name only then it is converted to a
        volpath and returned in a single item list.

        Path that do not end with name raise an AmiPathError
        """
        if self.is_name_only():
            env = self._ensure_env()
            # get cmd paths
            cmd_paths = env.get_cmd_paths()
            if make_volpaths:
                res = []
                for cmd_path in cmd_paths:
                    res += cmd_path.volpaths()
            else:
                res = cmd_paths
            # join our name
            res = list(map(lambda x: x.join(self), res))
            # add current dir
            if with_cur_dir:
                cur_dir = env.get_cur_dir()
                res.append(cur_dir.join(self))
            return res
        elif self.ends_with_name():
            # use my path only
            if make_volpaths:
                return self.volpaths()
            else:
                return [self]
        else:
            raise AmiPathError(self, "can't derive cmdpaths")
