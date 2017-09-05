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


def test_vamos_config_volume_group_args():
    # create config
    vg = VolumeConfigGroup()
    s = ConfigSet()
    s.add_named_group(vg)
    # setup parser
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    vg.add_args(ap)
    # parse arg list
    args = a.parse_args("-V bla=.,home=~".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    ref = {
        'volumes': {
            'bla': os.path.abspath('.'),
            'home': os.path.expanduser('~')
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
            'bar': 'b:+c:'
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


def test_vamos_config_assign_group_args():
    # create config
    ag = AssignConfigGroup()
    s = ConfigSet()
    s.add_named_group(ag)
    # setup parser
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    ag.add_args(ap)
    # parse arg list
    args = a.parse_args("-a bla=blub:+bluna:,foo=bar:".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    ref = {
        'assigns': {
            'bla': ['blub:', 'bluna:'],
            'foo': ['bar:']
        }
    }
    assert cfg == ref


def test_vamos_config_path_group():
    g = PathConfigGroup()
    s = ConfigSet()
    s.add_group("path", g)
    d = {
        'path': {
            'cmd_path': ['a:']
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
            'cmd_path': ['a:']
        }
    }
    assert cfg == ref


def test_vamos_config_path_group_args():
    # create config
    g = PathConfigGroup()
    s = ConfigSet()
    s.add_named_group(g)
    # setup parser
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    g.add_args(ap)
    # parse arg list
    args = a.parse_args("-p c:+sc:c".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    ref = {
        'paths': {
            'cmd_path': ['c:', 'sc:c'],
        }
    }
    assert cfg == ref
