import pytest
from amitools.util.config import *
from amitools.util.prelog import PreLogger
from io import StringIO
import logging

# ----- values


def test_config_val_bool():
    b = ConfigBoolValue("a_bool", False)
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
    v = ConfigIntValue("a_int", 0)
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
    v = ConfigIntValue("a_int", 0, int_range=(-10, 10))
    assert v.parse_value(-10) == -10
    assert v.parse_value(10) == 10
    with pytest.raises(ValueError):
        v.parse_value(-20)
    with pytest.raises(ValueError):
        v.parse_value(20)


def test_config_val_size():
    v = ConfigSizeValue("a_size", "2m")
    assert v.get_default() == 2 * 1024 * 1024
    assert v.parse_value("0x10ki") == 16 * 1024
    assert v.parse_value("$4g") == 4 * 1024 * 1024 * 1024
    assert v.parse_value(u"0x10ki") == 16 * 1024


def test_config_val_str():
    v = ConfigStringValue("a_string", "hugo")
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
    v = ConfigStringValue("a_none", None, allow_none=True)
    assert v.get_default() is None
    assert v.parse_value(None) is None
    assert v.parse_value("hello") is "hello"


def test_config_val_enum_list():
    v = ConfigEnumValue("a_enum", ("a", "b", "c"), "a")
    assert v.get_default() == "a"
    assert v.parse_value("b") == "b"
    with pytest.raises(ValueError):
        v.parse_value("d")
    with pytest.raises(ValueError):
        v.parse_value(12)


def test_config_val_enum_map():
    v = ConfigEnumValue("a_enum", {"a": 0, "b": 1, "c": 2}, 0)
    assert v.get_default() == 0
    assert v.parse_value("b") == 1
    assert v.parse_value(2) == 2
    with pytest.raises(ValueError):
        v.parse_value("d")
    with pytest.raises(ValueError):
        v.parse_value(12)


def test_config_val_list():
    v = ConfigStringValue("a_val", "")
    vl = ConfigValueList("a_list", v)
    assert vl.get_default() == []
    assert vl.parse_value(None) == []
    assert vl.parse_value([]) == []
    assert vl.parse_value(["a", "b"]) == ["a", "b"]
    assert vl.parse_value("a,b") == ["a", "b"]

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
    k = ConfigKeyList("a", ["b", "c", "d"])
    assert k.match_key("b")
    assert k.match_key("C")
    assert not k.match_key("a")


def test_config_key_list_case():
    k = ConfigKeyList("a", ["b", "c", "d"], case=True)
    assert k.match_key("b")
    assert not k.match_key("C")
    assert not k.match_key("a")


def test_config_key_glob():
    k = ConfigKeyGlob("a", "*.lib")
    assert k.match_key("h.lib")
    assert k.match_key("B.lIb")
    assert not k.match_key("h.libi")


def test_config_key_glob_case():
    k = ConfigKeyGlob("a", "*.lib", case=True)
    assert k.match_key("h.lib")
    assert not k.match_key("B.lIb")
    assert not k.match_key("h.libi")


def test_config_key_regex():
    k = ConfigKeyRegEx("a", "a.*z")
    assert k.match_key("abz")
    assert k.match_key("AbZ")
    assert not k.match_key("abzl")
    assert not k.match_key("bz")


def test_config_key_regex_case():
    k = ConfigKeyRegEx("a", "a.*z", case=True)
    assert k.match_key("abz")
    assert not k.match_key("AbZ")
    assert not k.match_key("abzl")
    assert not k.match_key("bz")

# ----- group and set


def test_config_group():
    g = ConfigGroup("grp")
    v = ConfigIntValue("a_int", 0)
    g.add_value(v)
    assert g.match_key("a_int") == (ConfigKey("a_int"), v)


def test_config_group_key():
    g = ConfigGroup("grp")
    v = ConfigIntValue("a_int", 0)
    k = ConfigKeyList("a", ["b", "c", "d"], case=True)
    g.add_key_value(k, v)
    assert g.match_key("b") == (k, v)


def test_config_set():
    s = ConfigSet()
    g = ConfigGroup("grp")
    s.add_group(g)
    assert s.match_key("grp") == (ConfigKey("grp"), g)


def test_config_set_key():
    s = ConfigSet()
    g = ConfigGroup("grp")
    k = ConfigKeyList("a", ["b", "c", "d"], case=True)
    s.add_key_group(k, g)
    assert s.match_key("b") == (k, g)

# ----- creator


def test_creator():
    c = ConfigCreator()
    c.set_entry("grp", "key", 42)
    assert c.get_cfg_set() == {"grp": {"key": 42}}


# ----- config file

def create_config_set():
    s = ConfigSet()
    g = ConfigGroup("grp")
    s.add_group(g)
    v = ConfigIntValue("bla", 0)
    g.add_value(v)
    return s


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
