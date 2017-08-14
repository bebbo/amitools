from amitools.util.prelog import PreLogger
import logging


def test_prelog_get_msgs():
    pl = PreLogger()
    pl.debug("a static message")
    pl.debug("with arg %d", 42)
    pl.debug("kwarg", exc_info=False)
    msgs = pl.get_log_msgs()
    assert len(msgs) == 3
    assert msgs[0] == (logging.DEBUG, "a static message", (), {})
    assert msgs[1] == (logging.DEBUG, "with arg %d", (42,), {})
    assert msgs[2] == (logging.DEBUG, "kwarg", (), {"exc_info": False})


def test_prelog_levels():
    pl = PreLogger()
    pl.debug("debug")
    pl.info("info")
    pl.warning("warning")
    pl.error("error")
    pl.critical("critical")
    msgs = pl.get_log_msgs()
    assert len(msgs) == 5
    assert msgs[0] == (logging.DEBUG, "debug", (), {})
    assert msgs[1] == (logging.INFO, "info", (), {})
    assert msgs[2] == (logging.WARNING, "warning", (), {})
    assert msgs[3] == (logging.ERROR, "error", (), {})
    assert msgs[4] == (logging.CRITICAL, "critical", (), {})


def test_prelog_to_logger():
    pl = PreLogger()
    class Test(object):

        def log(self, lvl, msg, *args, **kwargs):
            assert lvl == logging.DEBUG
            assert msg == "with arg %d"
            assert args == (42,)
            assert kwargs == {"exc_info": False}
    pl.debug("with arg %d", 42, exc_info=False)
    pl.to_logger(Test())
