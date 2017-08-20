import pytest
from amitools.util.config import *
from amitools.util.prelog import PreLogger
from io import StringIO
import logging
import argparse
import tempfile

# ----- values


def test_config_val_bool():
    b = ConfigBoolValue(False)
    assert b.get_default() == False
    assert b.parse_value(True) == True
    assert b.parse_value(False) == False
    assert b.parse_value('YES') == True
    assert b.parse_value('No') == False
    assert b.parse_value('on') == True
    assert b.parse_value('off') == False
    assert b.parse_value(u'off') == False
    with pytest.raises(ValueError):
        b.parse_value(1)
    with pytest.raises(ValueError):
        b.parse_value('hoi')
    with pytest.raises(ValueError):
        b.parse_value(None)


def test_config_val_int():
    v = ConfigIntValue(0)
    assert v.get_default() == 0
    assert v.parse_value("10") == 10
    assert v.parse_value(42) == 42
    assert v.parse_value("0x10") == 16
    assert v.parse_value("$20") == 32
    assert v.parse_value(u"10") == 10
    with pytest.raises(ValueError):
        v.parse_value(True)
    with pytest.raises(ValueError):
        v.parse_value('hoi')
    with pytest.raises(ValueError):
        v.parse_value(None)


def test_config_val_int_range():
    v = ConfigIntValue(0, int_range=(-10, 10))
    assert v.parse_value(-10) == -10
    assert v.parse_value(10) == 10
    with pytest.raises(ValueError):
        v.parse_value(-20)
    with pytest.raises(ValueError):
        v.parse_value(20)


def test_config_val_size():
    v = ConfigSizeValue("2m")
    assert v.get_default() == 2 * 1024 * 1024
    assert v.parse_value("0x10ki") == 16 * 1024
    assert v.parse_value("$4g") == 4 * 1024 * 1024 * 1024
    assert v.parse_value(u"0x10ki") == 16 * 1024


def test_config_val_str():
    v = ConfigStringValue("hugo")
    assert v.get_default() == "hugo"
    assert v.parse_value("hello") == "hello"
    assert v.parse_value(u"hello") == u"hello"
    with pytest.raises(ValueError):
        v.parse_value(True)
    with pytest.raises(ValueError):
        v.parse_value(12)
    with pytest.raises(ValueError):
        v.parse_value(None)


def test_config_val_str_none():
    v = ConfigStringValue(None, allow_none=True)
    assert v.get_default() is None
    assert v.parse_value(None) is None
    assert v.parse_value("hello") is "hello"


def test_config_val_enum_list():
    v = ConfigEnumValue(("a", "b", "c"), "a")
    assert v.get_default() == "a"
    assert v.parse_value("b") == "b"
    with pytest.raises(ValueError):
        v.parse_value("d")
    with pytest.raises(ValueError):
        v.parse_value(12)


def test_config_val_enum_map():
    v = ConfigEnumValue({"a": 0, "b": 1, "c": 2}, 0)
    assert v.get_default() == 0
    assert v.parse_value("b") == 1
    assert v.parse_value(2) == 2
    with pytest.raises(ValueError):
        v.parse_value("d")
    with pytest.raises(ValueError):
        v.parse_value(12)


def test_config_val_list():
    v = ConfigStringValue("")
    vl = ConfigValueList(v)
    assert vl.get_default() == []
    assert vl.parse_value(None) == []
    assert vl.parse_value([]) == []
    assert vl.parse_value(["a", "b"]) == ["a", "b"]
    assert vl.parse_value("a,b") == ["a", "b"]


def test_config_val_list_append():
    v = ConfigStringValue("")
    vl = ConfigValueList(v)
    assert vl.parse_value("+a,b") == ["a", "b"]
    assert vl.parse_value("+a,b", ["c"]) == ["c", "a", "b"]

# ----- keys


def test_config_key_name():
    k = ConfigKey("a")
    assert k.match_key("a")
    assert k.match_key("A")
    assert not k.match_key("b")


def test_config_key_name_case():
    k = ConfigKey("a", case=True)
    assert k.match_key("a")
    assert not k.match_key("A")
    assert not k.match_key("b")


def test_config_key_list():
    k = ConfigKeyList(["b", "c", "d"])
    assert k.match_key("b")
    assert k.match_key("C")
    assert not k.match_key("a")


def test_config_key_list_case():
    k = ConfigKeyList(["b", "c", "d"], case=True)
    assert k.match_key("b")
    assert not k.match_key("C")
    assert not k.match_key("a")


def test_config_key_glob():
    k = ConfigKeyGlob("*.lib")
    assert k.match_key("h.lib")
    assert k.match_key("B.lIb")
    assert not k.match_key("h.libi")


def test_config_key_glob_case():
    k = ConfigKeyGlob("*.lib", case=True)
    assert k.match_key("h.lib")
    assert not k.match_key("B.lIb")
    assert not k.match_key("h.libi")


def test_config_key_regex():
    k = ConfigKeyRegEx("a.*z")
    assert k.match_key("abz")
    assert k.match_key("AbZ")
    assert not k.match_key("abzl")
    assert not k.match_key("bz")


def test_config_key_regex_case():
    k = ConfigKeyRegEx("a.*z", case=True)
    assert k.match_key("abz")
    assert not k.match_key("AbZ")
    assert not k.match_key("abzl")
    assert not k.match_key("bz")

# ----- group and set


def test_config_group():
    g = ConfigGroup()
    v = ConfigIntValue(0)
    g.add_value("a_int", v)
    e = g.match_key("a_int")
    assert e.get_key().get_key() == "a_int"
    assert e.get_value() == v


def test_config_group_key():
    g = ConfigGroup()
    v = ConfigIntValue(0)
    k = ConfigKeyList(["b", "c", "d"], case=True)
    g.add_key_value(k, v)
    e = g.match_key("b")
    assert e.get_key() == k
    assert e.get_value() == v


def test_config_set():
    s = ConfigSet()
    g = ConfigGroup()
    s.add_group("grp", g)
    e = s.match_key("grp")
    assert e.get_key().get_key() == "grp"
    assert e.get_value() == g


def test_config_set_key():
    s = ConfigSet()
    g = ConfigGroup()
    k = ConfigKeyList(["b", "c", "d"], case=True)
    s.add_key_group(k, g)
    e = s.match_key("b")
    assert e.get_key() == k
    assert e.get_value() == g

# ----- creator


def create_config_set(group_by_name=None):
    s = ConfigSet()
    # fix group
    g = ConfigGroup()
    s.add_group("grp", g)
    v = ConfigIntValue(0)
    g.add_value("bla", v)
    v2 = ConfigEnumValue(("a", "b", "c"), "a")
    g.add_value("foo", v2)
    v3 = ConfigBoolValue(False)
    g.add_value("b1", v3)
    v4 = ConfigBoolValue(True)
    g.add_value("b2", v4)
    # dyn group
    g2 = ConfigGroup()
    g2k = ConfigKeyGlob("*.lib")
    s.add_key_group(g2k, g2, group_by_name)
    v5 = ConfigIntValue(21)
    g2.add_value("baz", v5)
    return s


def test_creator():
    s = create_config_set()
    c = ConfigCreator()
    pl = PreLogger()
    ok = c.parse_entry("bla", s, pl, "grp", "bla", 12)
    assert ok
    assert c.get_cfg_set() == {"grp": {"bla": 12}}

# ----- config dict


def test_config_dict_ok():
    s = create_config_set()
    d = {
        'grp': {
            'foo': 'b',
            'bla': 12
        }
    }
    dp = ConfigDictParser(d)
    c = ConfigCreator()
    pl = PreLogger()
    ok = dp.parse(s, c, pl)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'bla': 12, 'foo': 'b'}}


def test_config_dict_error():
    s = create_config_set()
    d = {
        'grp': {
            'foo': 'b',
            'bla': 12
        }
    }
    dp = ConfigDictParser(d)
    c = ConfigCreator()
    pl = PreLogger()
    ok = dp.parse(s, c, pl)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'bla': 12, 'foo': 'b'}}


def test_config_dict_multi():
    s = create_config_set()
    d = {
        'a.lib': {
            'baz': 7
        },
        'bla.lib': {
            'baz': 13
        }
    }
    dp = ConfigDictParser(d)
    c = ConfigCreator()
    pl = PreLogger()
    ok = dp.parse(s, c, pl)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'a.lib': {'baz': 7}, 'bla.lib': {'baz': 13}}


def test_config_dict_multi_group():
    s = create_config_set(group_by_name="lib")
    d = {
        'a.lib': {
            'baz': 7
        },
        'bla.lib': {
            'baz': 13
        }
    }
    dp = ConfigDictParser(d)
    c = ConfigCreator()
    pl = PreLogger()
    ok = dp.parse(s, c, pl)
    print(pl.get_log_msgs())
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'lib': {'a.lib': {'baz': 7}, 'bla.lib': {'baz': 13}}}


# ----- config file


def test_config_file_parser():
    c = ConfigCreator()
    s = create_config_set()
    test = u"""
[grp]
bla=12
"""
    io = StringIO(test)
    cf = ConfigFileParser("test", io)
    pl = PreLogger()
    ok = cf.parse(s, c, pl)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'bla': 12}}


def test_config_file_parser_cfg_error():
    c = ConfigCreator()
    s = create_config_set()
    test = u"""
[grp]
bla;12
"""
    io = StringIO(test)
    cf = ConfigFileParser("test", io)
    pl = PreLogger()
    ok = cf.parse(s, c, pl)
    assert not ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 1
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {}


def test_config_file_parser_val_error():
    c = ConfigCreator()
    s = create_config_set()
    test = u"""
[grp]
bla=12+3
"""
    io = StringIO(test)
    cf = ConfigFileParser("test", io)
    pl = PreLogger()
    ok = cf.parse(s, c, pl)
    assert not ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 1
    assert pl.get_num_msgs(logging.CRITICAL) == 0


def test_config_file_parser_invalid_sect_opt():
    c = ConfigCreator()
    s = create_config_set()
    test = u"""
[grp2]
bla=12

[grp]
blub=12
"""
    io = StringIO(test)
    cf = ConfigFileParser("test", io)
    pl = PreLogger()
    ok = cf.parse(s, c, pl)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 2
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0


def test_config_file_parser_legacy_map():
    c = ConfigCreator()
    s = create_config_set()
    test = u"""
[grp_old]
blob=12
"""
    io = StringIO(test)
    cf = ConfigFileParser("test", io)
    cf.add_legacy_option("grp_old", "blob", "grp", "bla")
    pl = PreLogger()
    ok = cf.parse(s, c, pl)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 1
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'bla': 12}}


def test_config_file_mgr_check_def():
    cfm = ConfigFileManager("baz")
    assert cfm.get_default_config_name() == ".bazrc"
    assert cfm.get_default_global_config_file() == "~/.bazrc"
    assert cfm.get_default_local_config_file() == ".bazrc"


def test_config_file_mgr_default():
    c = ConfigCreator()
    s = create_config_set()
    # g_cfg
    g_cfg = u"""
[grp]
bla=12
foo=c
"""
    g_cfg_fobj = StringIO(g_cfg)
    # l_cfg
    l_cfg = u"""
[grp]
foo=b
"""
    l_cfg_fobj = StringIO(l_cfg)
    # setup manager
    cfm = ConfigFileManager("baz")
    cfm.set_global_config_file("g", g_cfg_fobj)
    cfm.set_local_config_file("l", l_cfg_fobj)
    pl = PreLogger()
    ok = cfm.parse(s, c, pl)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'bla': 12, 'foo': 'b'}}


def test_config_file_mgr_skip_global():
    c = ConfigCreator()
    s = create_config_set()
    # g_cfg
    g_cfg = u"""
[grp]
bla=12
"""
    g_cfg_fobj = StringIO(g_cfg)
    # l_cfg
    l_cfg = u"""
[grp]
foo=b
"""
    l_cfg_fobj = StringIO(l_cfg)
    # setup manager
    cfm = ConfigFileManager("baz")
    cfm.set_global_config_file("g", g_cfg_fobj)
    cfm.set_local_config_file("l", l_cfg_fobj)
    # arg parse setup
    a = argparse.ArgumentParser()
    cfm.add_skip_global_config_arg(a)
    # parse args: skip global
    args = a.parse_args("-S".split())
    pl = PreLogger()
    ok = cfm.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    # check that no globals are read
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'foo': 'b'}}


def test_config_file_mgr_set_config_file():
    c = ConfigCreator()
    s = create_config_set()
    # g_cfg
    g_cfg = u"""
[grp]
bla=12
"""
    g_cfg_fobj = StringIO(g_cfg)
    # l_cfg
    l_cfg = u"""
[grp]
foo=b
"""
    l_cfg_fobj = StringIO(l_cfg)
    # my local config file
    myf = tempfile.NamedTemporaryFile(mode='w', delete=False)
    myname = myf.name
    myf.write(u"""
[grp]
foo=c
""")
    myf.close()
    # setup manager
    cfm = ConfigFileManager("baz")
    cfm.set_global_config_file("g", g_cfg_fobj)
    cfm.set_local_config_file("l", l_cfg_fobj)
    # arg parse setup
    a = argparse.ArgumentParser()
    cfm.add_select_local_config_arg(a)
    # parse args: set config file
    args = a.parse_args("-c {}".format(myname).split())
    pl = PreLogger()
    ok = cfm.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    # check that no globals are read
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'bla': 12, 'foo': 'c'}}
    # cleanup temp file
    os.remove(myname)

# ----- config args


def test_config_args_value_switch():
    s = create_config_set()
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    ap.add_value('grp', 'bla', '-b', '--bla', desc="set the bla")
    # shot arg
    args = a.parse_args("-b 12".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'bla': 12}}
    # long arg
    args = a.parse_args("--bla 21".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'bla': 21}}


def test_config_args_value_fixed():
    s = create_config_set()
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    ap.add_value('grp', 'bla', 'foo', desc="set the foo")
    # shot arg
    args = a.parse_args("12".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'bla': 12}}


def test_config_args_bool_value_switch():
    s = create_config_set()
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    ap.add_bool_value('grp', 'b1', '-f', '--foo', desc="set b1 to True")
    # no arg
    args = a.parse_args([])
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'b1': False}}
    # shot arg
    args = a.parse_args("-f".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'b1': True}}
    # long arg
    args = a.parse_args("--foo".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'b1': True}}


def test_config_args_bool_value_default():
    s = create_config_set()
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    ap.add_bool_value('grp', 'b1', '-f', '--foo',
                      desc="set b1 to True", default=True)
    # no arg
    args = a.parse_args([])
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'b1': True}}
    # shot arg
    args = a.parse_args("-f".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'b1': False}}
    # long arg
    args = a.parse_args("--foo".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'b1': False}}


def test_config_args_bool_value_const():
    s = create_config_set()
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    ap.add_bool_value('grp', 'foo', '-f', '--foo',
                      desc="set foo to 'c'", default='b', const='c')
    # no arg
    args = a.parse_args([])
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'foo': 'b'}}
    # shot arg
    args = a.parse_args("-f".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'foo': 'c'}}
    # long arg
    args = a.parse_args("--foo".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'foo': 'c'}}


def test_config_args_dyn_value_ok():
    s = create_config_set()
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    ap.add_dyn_value('grp', '-g', desc="set grp values")
    # parse arg list
    args = a.parse_args("-g bla=12,foo=b".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'bla': 12, 'foo': 'b'}}


def test_config_args_dyn_value_error():
    s = create_config_set()
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    ap.add_dyn_value('grp', '-g', desc="set grp values")
    # syntax error in arg list
    args = a.parse_args("-g b".split())
    ok = ap.parse(s, c, pl, args)
    assert not ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 1
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    # syntax error in arg list
    args = a.parse_args("-g bla=12,foo=b,".split())
    ok = ap.parse(s, c, pl, args)
    assert not ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 2
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    # syntax error in arg list
    args = a.parse_args("-g bla=12=3,foo=b,".split())
    ok = ap.parse(s, c, pl, args)
    assert not ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 3
    assert pl.get_num_msgs(logging.CRITICAL) == 0


def test_config_args_dyn_value_val_key():
    s = create_config_set()
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    ap.add_dyn_value('grp', '-g', desc="set grp values",
                     val_keys=[ConfigKey("bla")])
    # valid key
    args = a.parse_args("-g bla=12".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'bla': 12}}
    # invalid key
    args = a.parse_args("-g foo=b".split())
    ok = ap.parse(s, c, pl, args)
    assert not ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 1
    assert pl.get_num_msgs(logging.CRITICAL) == 0


def test_config_args_dyn_group_ok():
    s = create_config_set()
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    gk = ConfigKey('grp')
    ap.add_dyn_group([gk], '-g', desc="set grp values")
    # parse arg list
    args = a.parse_args("-g grp:bla=12,foo=b".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'grp': {'bla': 12, 'foo': 'b'}}


def test_config_args_dyn_group_error():
    s = create_config_set()
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    gk = ConfigKey('grp')
    ap.add_dyn_group([gk], '-g', desc="set grp values")
    # syntax error: no group name
    args = a.parse_args("-g grp;bla=12,foo=b".split())
    ok = ap.parse(s, c, pl, args)
    assert not ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 1
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    # invalid group
    args = a.parse_args("-g foo:bla=12,foo=b".split())
    ok = ap.parse(s, c, pl, args)
    assert not ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 2
    assert pl.get_num_msgs(logging.CRITICAL) == 0


# ----- MainParser

def test_config_main_parser_ok():
    s = create_config_set()
    d = {
        'grp': {
            'bla': 10
        }
    }
    c = ConfigMainParser(s, d, prog="bluna")
    # pimp file cfg
    # g_cfg
    g_cfg = u"""
[grp]
foo=a
"""
    g_cfg_fobj = StringIO(g_cfg)
    # l_cfg
    l_cfg = u"""
[grp]
foo=b
"""
    l_cfg_fobj = StringIO(l_cfg)
    # setup manager
    cfm = c.get_cfg_file_parser()
    assert cfm.get_default_config_name() == ".blunarc"
    cfm.set_global_config_file("g", g_cfg_fobj)
    cfm.set_local_config_file("l", l_cfg_fobj)
    # setup args
    ap = c.get_cfg_arg_parser()
    gk = ConfigKey('grp')
    ap.add_dyn_group([gk], '-g', desc="set grp values")
    # parse args
    ok = c.parse("-g grp:bla=12".split())
    assert ok
    pl = c.get_pre_logger()
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    assert c.get_cfg_dict() == {'grp': {'bla': 12, 'foo': 'b'}}
