# amipath
# a tool to work with amiga paths

import sys
from amitools.util.config import *
from amitools.path.config import *
import amitools.util.log as log


def create_config_def():
    s = ConfigSet()
    add_path_config_groups(s)
    return s


def main(args=None):
    s = create_config_def()
    c = ConfigMainParser(s, cfg_name="vamos")
    log.init(c)
    ok = c.parse(args)
    if not ok:
        return 1
    cfg = c.get_cfg_dict()
    print(cfg)
    return 0

if __name__ == '__main__':
    sys.exit(main())
