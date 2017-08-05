import logging
from amitools.vamos.config import VamosConfig, VamosLibConfig


def test_config_default():
    vc = VamosConfig()
    log = logging.getLogger("test")
    assert vc.validate(log) == True
