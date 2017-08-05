import pytest
from amitools.util.config import *


def test_config_bool():
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
    # store
    d = {}
    b.store(d, True)
    assert d['a_bool'] == True


def test_config_int():
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
    # store
    d = {}
    v.store(d, "10")
    assert d['a_int'] == 10


def test_config_int_range():
    v = ConfigIntValue("a_int", 0, int_range=(-10, 10))
    assert v.parse_value(-10) == -10
    assert v.parse_value(10) == 10
    with pytest.raises(ValueError):
        v.parse_value(-20)
    with pytest.raises(ValueError):
        v.parse_value(20)


def test_config_size():
    v = ConfigSizeValue("a_size", "2m")
    assert v.get_default() == 2 * 1024 * 1024
    assert v.parse_value("0x10ki") == 16 * 1024
    assert v.parse_value("$4g") == 4 * 1024 * 1024 * 1024
    # store
    d = {}
    v.store(d, 17)
    assert d['a_size'] == 17

def test_config_str():
    v = ConfigStringValue("a_string", "hugo")
    assert v.get_default() == "hugo"
    assert v.parse_value("hello") == "hello"
    with pytest.raises(ValueError):
        v.parse_value(True)
    with pytest.raises(ValueError):
        v.parse_value(12)
    with pytest.raises(ValueError):
        v.parse_value(None)
    # store
    d = {}
    v.store(d, "hoi")
    assert d['a_string'] == "hoi"

def test_config_str_none():
    v = ConfigStringValue("a_none", None, allow_none=True)
    assert v.get_default() is None
    assert v.parse_value(None) is None
    assert v.parse_value("hello") is "hello"
    # store
    d = {}
    v.store(d, None)
    assert d['a_none'] is None

def test_config_enum_list():
    v = ConfigEnumValue("a_enum", ("a", "b", "c"), "a")
    assert v.get_default() == "a"
    assert v.parse_value("b") == "b"
    with pytest.raises(ValueError):
        v.parse_value("d")
    with pytest.raises(ValueError):
        v.parse_value(12)

def test_config_enum_map():
    v = ConfigEnumValue("a_enum", {"a" : 0, "b" : 1, "c" : 2}, 0)
    assert v.get_default() == 0
    assert v.parse_value("b") == 1
    assert v.parse_value(2) == 2
    with pytest.raises(ValueError):
        v.parse_value("d")
    with pytest.raises(ValueError):
        v.parse_value(12)
