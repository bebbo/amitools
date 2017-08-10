import pytest
from amitools.util.config import *

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


def test_config_val_str():
    v = ConfigStringValue("a_string", "hugo")
    assert v.get_default() == "hugo"
    assert v.parse_value("hello") == "hello"
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
