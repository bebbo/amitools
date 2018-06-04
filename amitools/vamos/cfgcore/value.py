
def parse_scalar(val_type, val, allow_none=False):
  if type(val) is val_type:
    return val
  # none handling
  if val is None:
    if allow_none:
      return None
    else:
      raise ValueError("None not allowed for type: %s" % val_type)
  # bool special strings
  if val_type is bool:
    if type(val) is str:
      lv = val.lower()
      if lv in ("on", "true"):
        return True
      elif lv in ("off", "false"):
        return False
  return val_type(val)


def split_nest(in_str, sep=',', nest_pair='()', keep_nest=False):
  """split a string by sep, but don't touch seps in nested pairs"""
  res = []
  cur = []
  nesting = 0
  if nest_pair is None:
    nest_begin = None
    nest_end = None
  else:
    nest_begin = nest_pair[0]
    nest_end = nest_pair[1]
  # split string loop
  for c in in_str:
    if c == nest_end:
      nesting -= 1
    if nesting == 0:
      if c in sep:
        if len(cur) > 0:
          res.append("".join(cur))
          cur = []
      elif c not in (nest_begin, nest_end) or keep_nest:
        cur.append(c)
    else:
      cur.append(c)
    # adjust nesting
    if c == nest_begin:
      nesting += 1
  # final element
  if len(cur) > 0:
    res.append("".join(cur))
  return res


class Value(object):
  def __init__(self, item_type, default=None, allow_none=None):
    self.item_type = item_type
    self.nest_pair = None
    if allow_none is None:
      self.allow_none = item_type is str
    else:
      self.allow_none = allow_none
    if default:
      self.default = self.parse(default)
    else:
      self.default = None

  def parse(self, val):
    return parse_scalar(self.item_type, val, self.allow_none)

  def __eq__(self, other):
    return self.item_type == other.item_type and \
        self.default == other.default

  def __repr__(self):
    return "Value(%s, default=%s)" % (self.item_type, self.default)


class ValueList(object):
  def __init__(self, item_type, default=None, allow_none=None,
               sep=',', nest_pair='()'):
    self.item_type = item_type
    self.sep = sep
    self.nest_pair = nest_pair
    self.is_sub_value = type(item_type) in (Value, ValueList, ValueDict)
    if self.is_sub_value:
      self.sub_nest_pair = item_type.nest_pair
    else:
      self.sub_nest_pair = None
    if allow_none is None:
      self.allow_none = item_type is str
    else:
      self.allow_none = allow_none
    if default:
      self.default = self.parse(default)
    else:
      self.default = None

  def parse(self, val):
    if val is None:
      return []
    elif type(val) is str:
      # split string by sep
      val = split_nest(val, self.sep, self.sub_nest_pair)
    elif type(val) not in (list, tuple):
      raise ValueError("expected list or tuple: %s" % val)
    # rebuild list
    res = []
    for v in val:
      if self.is_sub_value:
        r = self.item_type.parse(v)
      else:
        r = parse_scalar(self.item_type, v, self.allow_none)
      res.append(r)
    return res

  def __eq__(self, other):
    return self.item_type == other.item_type and \
        self.default == other.default and \
        self.sep == other.sep

  def __repr__(self):
    return "ValueList(%s, default=%s, sep=%s)" % \
        (self.item_type, self.default, self.sep)


class ValueDict(object):
  def __init__(self, item_type, default=None, allow_none=None,
               sep=',', kv_sep=':', nest_pair='{}'):
    self.item_type = item_type
    self.sep = sep
    self.kv_sep = kv_sep
    self.nest_pair = nest_pair
    self.is_sub_value = type(item_type) in (Value, ValueList, ValueDict)
    if self.is_sub_value:
      self.sub_nest_pair = item_type.nest_pair
    else:
      self.sub_nest_pair = None
    if allow_none is None:
      self.allow_none = item_type is str
    else:
      self.allow_none = allow_none
    if default:
      self.default = self.parse(default)
    else:
      self.default = None

  def parse(self, val):
    if val is None:
      return {}
    elif type(val) is str:
      # convert str to dict
      d = {}
      kvs = split_nest(val, self.sep, self.sub_nest_pair, True)
      for kv in kvs:
        key, val = split_nest(kv, self.kv_sep, self.sub_nest_pair)
        d[key] = val
      val = d
    elif type(val) in (list, tuple):
      # allow list of entries and merge them
      res = {}
      for elem in val:
        d = self.parse(elem)
        res.update(d)
      return res
    elif type(val) is not dict:
      raise ValueError("expected dict: %s" % val)
    # rebuild dict
    res = {}
    for key in val:
      v = val[key]
      if self.is_sub_value:
        r = self.item_type.parse(v)
      else:
        r = parse_scalar(self.item_type, v, self.allow_none)
      res[key] = r
    return res

  def __eq__(self, other):
    return self.item_type == other.item_type and \
        self.default == other.default and \
        self.sep == other.sep and \
        self.kv_sep == other.kv_sep

  def __repr__(self):
    return "ValueDict(%s, default=%s, sep=%s, kv_sep=%s)" % \
        (self.item_type, self.default, self.sep, self.kv_sep)
