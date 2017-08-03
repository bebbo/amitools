from __future__ import print_function
from amitools.sysemu.memcfg import *


def test_amc_simple():
    mc = AmigaMemoryConfig()
    mc.add_ram('8M') # add 8 MiB
    print(mc.get_range_list())
