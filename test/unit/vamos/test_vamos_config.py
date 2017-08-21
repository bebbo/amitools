import logging
import pytest

from amitools.vamos.config import *


def test_vamos_config_dosname_key():
    akey = AmigaDOSNameKey()
    assert akey.match_key("a_valid_NAME")
    assert not akey.match_key("invalid:")
    assert not akey.match_key("in/va/lid")


def test_vamos_config_dospath_val():
    dval = AmigaDOSAbsPathValue()
    assert dval.parse_value("ok:") == "ok:"
    assert dval.parse_value("ok:a") == "ok:a"
    assert dval.parse_value("ok:a/path") == "ok:a/path"
    assert dval.parse_value("ok:a/path/") == "ok:a/path/"
    with pytest.raises(ValueError):
        dval.parse_value("nok")
    with pytest.raises(ValueError):
        dval.parse_value("nok:/bla")


def test_vamos_config_volume_group():
    vg = VolumeConfigGroup()
    s = ConfigSet()
    s.add_group("volumes", vg)
    d = {
        'volumes': {
            'sys': '/',
            'home': '~',
            'cwd': '.'
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
    ref = {
        'volumes': {
            'sys': '/',
            'home': os.path.expanduser("~"),
            'cwd': os.path.abspath(".")
        }
    }
    assert cfg == ref


def test_vamos_config_assign_group():
    ag = AssignConfigGroup()
    s = ConfigSet()
    s.add_group("assigns", ag)
    d = {
        'assigns': {
            'bla': ['a:'],
            'foo': 'b:',
            'bar': 'b:,c:'
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
    ref = {
        'assigns': {
            'bla': ['a:'],
            'foo': ['b:'],
            'bar': ['b:', 'c:']
        }
    }
    assert cfg == ref


def test_vamos_config_path_group():
    ag = PathConfigGroup()
    s = ConfigSet()
    s.add_group("path", ag)
    d = {
        'path': {
            'path': ['a:']
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
    ref = {
        'path': {
            'path': ['a:']
        }
    }
    assert cfg == ref
