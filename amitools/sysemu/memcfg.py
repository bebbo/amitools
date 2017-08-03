from bare68k.memcfg import *
from bare68k.errors import *


class AmigaMemoryConfig(MemoryConfig):

    def __init__(self):
        MemoryConfig.__init__(self)
        self.kick_rom = None
        self.ext_rom = None
        self.ram_ranges = []

    def add_ram(self, size, units=1024):
        """give ram size in KiB or use size str or adjust units

           Note: add ram last to fill the sparse regions around special ranges
        """
        # ram always starts at 0
        res = self.add_ram_range_addr(0, size, units)
        self.ram_ranges += res
        return res

    def add_rom(self, addr, rom, mirror=True):
        """add a ROM to the memory layout"""
        self.kickrom = rom
        size = rom.get_size_kib()
        data = rom.get_data()
        if size == 256:
            res = self.add_rom_range_addr(addr, size, data)
            if mirror:
                self.add_mirror_range_addr(addr + 0x40000, 0x40000, addr)
        elif size == 512:
            res = self.add_rom_range_addr(addr, size, data)
        else:
            raise ConfigError("invalid ROM size: {}".format(size))

    def add_kick_rom(self, rom):
        """add a kickstart ROM @f80000"""
        return self.add_rom(0xf80000, rom)

    def add_ext_rom(self, rom):
        """add ext ROM at @e00000"""
        return self.add_rom(0xe00000, rom)

    def add_cias(self):
        """add CIA page @bfxxxx"""
        def cia_r(mode, addr):
            print("CIA read  @%08x" % addr)
            return 0
        def cia_w(mode, addr, val):
            print("CIA write @%08x = %02x" % (addr, val))
        return self.add_special_range(0xbf, 1, cia_r, cia_w)

    def add_custom_chips(self):
        """add custom chips range @dfxxxx"""
        def custom_r(mode, addr):
            print("CuC read  @%08x" % addr)
            return 0
        def custom_w(mode, addr, val):
            print("CuC write @%08x = %04x" % (addr, val))
        return self.add_special_range(0xdf, 1, custom_r, custom_w)

    def add_rtc(self):
        """add real time clock at @dcxxxx"""
        def rtc_r(mode, addr):
            print("rtc read  @%08x" % addr)
            return 0
        def rtc_w(mode, addr, val):
            print("rtc write @%08x = %04x" % (addr, val))
        return self.add_special_range(0xdc, 1, rtc_r, rtc_w)

    def add_ide(self):
        """add IDE controller at @daxxxx"""
        def ide_r(mode, addr):
            print("ide read  @%08x" % addr)
            return 0
        def ide_w(mode, addr, val):
            print("ide write @%08x = %04x" % (addr, val))
        return self.add_special_range(0xdc, 1, ide_r, ide_w)

    def add_reserved(self, flash_rom=True, autoconf=True, ranger=True):
        # empty flash rom
        if flash_rom:
            self.add_empty_range(0xf0, 8)
        # autoconf
        if autoconf:
            self.add_empty_range(0xe8, 1)
        # ranger mem
        if ranger:
            self.add_empty_range(0xc0, 16)
