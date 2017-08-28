import logging
from amitools.util.log import *


def test_log_level_value():
    v = ConfigLogLevelValue()
    assert v.parse_value("off") == OFF
    assert v.parse_value("CRITICAL") == logging.CRITICAL
    assert v.parse_value("eRRoR") == logging.ERROR
    assert v.parse_value("warn") == logging.WARNING
    assert v.parse_value("warning") == logging.WARNING
    assert v.parse_value("INFO") == logging.INFO
    assert v.parse_value("debug") == logging.DEBUG


def test_log_level_group_ok():
    g = ConfigLogLevelGroup()
    s = ConfigSet()
    s.add_group("loglevel", g)
    d = {
        'loglevel': {
            'foo': 'off',
            'bar': 'info',
            'baz': 'error'
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
    assert cfg == {'loglevel': {'foo': OFF,
                                'bar': logging.INFO, 'baz': logging.ERROR}}


def test_log_level_group_error():
    g = ConfigLogLevelGroup()
    s = ConfigSet()
    s.add_group("loglevel", g)
    d = {
        'loglevel': {
            'foo': 'oFFO'
        }
    }
    dp = ConfigDictParser(d)
    c = ConfigCreator()
    pl = PreLogger()
    ok = dp.parse(s, c, pl)
    assert not ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 1
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()


def test_log_level_group_args():
    g = ConfigLogLevelGroup()
    s = ConfigSet()
    s.add_group("loglevel", g)
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    g.add_args(ap)
    # no arg
    args = a.parse_args([])
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {}
    # short arg
    args = a.parse_args("-l bla=info".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'loglevel': {'bla': logging.INFO}}
    # long arg
    args = a.parse_args("--log-levels bla=info".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'loglevel': {'bla': logging.INFO}}


def test_log_group_ok():
    g = ConfigLogGroup()
    s = ConfigSet()
    s.add_group("log", g)
    d = {
        'log': {
            'verbose': 2,
            'quiet': 3,
            'log_file': 'my.log',
            'default_level': 'info'
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
    assert cfg == {'log': {'verbose': 2,
                           'quiet': 3,
                           'log_file': 'my.log',
                           'default_level': logging.INFO}}


def test_log_group_error():
    g = ConfigLogGroup()
    s = ConfigSet()
    s.add_group("log", g)
    d = {
        'log': {
            'verbose': 'hi'
        }
    }
    dp = ConfigDictParser(d)
    c = ConfigCreator()
    pl = PreLogger()
    ok = dp.parse(s, c, pl)
    assert not ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 1
    assert pl.get_num_msgs(logging.CRITICAL) == 0


def test_log_group_args():
    g = ConfigLogGroup()
    s = ConfigSet()
    s.add_group("log", g)
    c = ConfigCreator()
    pl = PreLogger()
    a = argparse.ArgumentParser()
    ap = ConfigArgsParser(a)
    g.add_args(ap)
    # no arg
    args = a.parse_args([])
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'log': {'verbose': 0,
                           'quiet': 0}}
    # short arg
    args = a.parse_args("-v -q -L foo.log -D info".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'log': {'verbose': 1,
                           'quiet': 1,
                           'log_file': 'foo.log',
                           'default_level': logging.INFO}}
    # long arg
    args = a.parse_args(
        "--verbose --quiet --log-file foo.log --default-level info".split())
    ok = ap.parse(s, c, pl, args)
    assert ok
    assert pl.get_num_msgs(logging.WARNING) == 0
    assert pl.get_num_msgs(logging.ERROR) == 0
    assert pl.get_num_msgs(logging.CRITICAL) == 0
    cfg = c.get_cfg_set()
    assert cfg == {'log': {'verbose': 1,
                           'quiet': 1,
                           'log_file': 'foo.log',
                           'default_level': logging.INFO}}
