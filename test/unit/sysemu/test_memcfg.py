from __future__ import print_function
import pytest

from amitools.sysemu.memcfg import *


def test_amc_ram_8m():
    mc = AmigaMemoryConfig()
    mc.add_ram('8M')  # add 8 MiB
    rl = mc.get_range_list()
    assert len(rl) == 1
    assert rl[0].num_pages == 128
    mc.check()


def test_amc_ram_64m():
    mc = AmigaMemoryConfig()
    mc.add_ram('64M')  # add 64 MiB
    rl = mc.get_range_list()
    assert len(rl) == 1
    assert rl[0].num_pages == 1024
    # more than 256 pages..
    with pytest.raises(ConfigError):
        mc.check()


def test_amc_ram_64m_cia_custom():
    mc = AmigaMemoryConfig()
    mc.add_cias()
    mc.add_custom_chips()
    mc.add_ram('64M')
    rl = mc.get_range_list()
    assert len(rl) == 5
    print(rl)
