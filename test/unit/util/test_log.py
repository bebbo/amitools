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


def test_log_setup_minimal():
    # empty config set
    cfg_set = ConfigSet()
    c = ConfigMainParser(cfg_set, prog="bluna")
    l = LogSetup(c)
    # parse args
    ok = c.parse("".split())
    assert ok
    # default level
    assert l.get_default_level() == logging.WARNING
    # now get a logger and log
    ml = l.get_logger("my_log")
    ml.error("an error!")
    # make sure its the default level
    assert ml.getEffectiveLevel() == logging.WARNING


def test_log_setup_default_level_verbose():
    # empty config set
    cfg_set = ConfigSet()
    c = ConfigMainParser(cfg_set, prog="bluna")
    l = LogSetup(c, cfg_level=logging.DEBUG)
    # parse args: verbose
    ok = c.parse("-v".split())
    assert ok
    # default is shifted to info
    assert l.get_default_level() == logging.INFO
    # now get a logger and log
    ml = l.get_logger("my_log")
    # make sure its the default level
    assert ml.getEffectiveLevel() == logging.INFO
    l.shutdown()


def test_log_setup_default_level_verbose_max():
    # empty config set
    cfg_set = ConfigSet()
    c = ConfigMainParser(cfg_set, prog="bluna")
    l = LogSetup(c, cfg_level=logging.INFO)
    # parse args: verbose
    ok = c.parse("-vvvvv".split())
    assert ok
    # default is shifted to info
    assert l.get_default_level() == logging.DEBUG
    # now get a logger and log
    ml = l.get_logger("my_log")
    # make sure its the default level
    assert ml.getEffectiveLevel() == logging.DEBUG
    l.shutdown()


def test_log_setup_default_level_quiet():
    # empty config set
    cfg_set = ConfigSet()
    c = ConfigMainParser(cfg_set, prog="bluna")
    l = LogSetup(c, cfg_level=logging.DEBUG)
    # parse args: quiet
    ok = c.parse("-q".split())
    assert ok
    # default is shifted to error
    assert l.get_default_level() == logging.ERROR
    # now get a logger and log
    ml = l.get_logger("my_log")
    # make sure its the default level
    assert ml.getEffectiveLevel() == logging.ERROR



def test_log_setup_default_level_quiet_max():
    # empty config set
    cfg_set = ConfigSet()
    c = ConfigMainParser(cfg_set, prog="bluna")
    l = LogSetup(c, cfg_level=logging.DEBUG)
    # parse args: quiet
    ok = c.parse("-qqqqq".split())
    assert ok
    # default is shifted to error
    assert l.get_default_level() == OFF
    # now get a logger and log
    ml = l.get_logger("my_log")
    # make sure its the default level
    assert ml.getEffectiveLevel() == OFF

def test_log_setup_set_loglevel():
    # empty config set
    cfg_set = ConfigSet()
    c = ConfigMainParser(cfg_set)
    l = LogSetup(c, cfg_level=logging.DEBUG)
    # parse args
    ok = c.parse("-l foo=info".split())
    assert ok
    # default level
    assert l.get_default_level() == logging.WARNING
    # now get a logger
    ml = l.get_logger("foo")
    # make sure its the defined level
    assert ml.getEffectiveLevel() == logging.INFO
    # even derived channels should work
    ml2 = l.get_logger("foo.bar")
    assert ml2.getEffectiveLevel() == logging.INFO


def test_log_setup_module():
    # empty config set
    cfg_set = ConfigSet()
    c = ConfigMainParser(cfg_set, prog="bluna")
    init(c)
    # parse args
    ok = c.parse("".split())
    assert ok
    # default level
    assert get_default_level() == logging.WARNING
    # now get a logger and log
    ml = get_logger("my_log")
    ml.error("an error!")
    # make sure its the default level
    assert ml.getEffectiveLevel() == logging.WARNING
    shutdown()
