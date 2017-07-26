from bare68k.memcfg import *

class AmigaMemoryConfig(MemoryConfig):
  def __init__(self):
    MemoryConfig.__init__(self)
    self.kickrom = None

  def add_kick_rom(self, kickrom):
    """add a kickstart or extended ROM to the memory layout"""
    self.kickrom = kickrom
    base_addr = kickstart.get_base_addr()
    size = kickstart.get_size_kib()
    return self.add_rom_range_addr(base_addr, size, kickstart.get_rom_data())

  def dummy(self):
    # empty flash rom
    self.add_empty_range(0xf0,8)
    # add ram
    self.add_ram_range_addr(0, ram_size)
    # empty IDE
    self.add_empty_range(0xda,1)
    # ?
    self.add_empty_range(0xa0,1)
    # autoconf
    self.add_empty_range(0xe8,1)
    # ranger mem
    self.add_empty_range(0xc0,16)
    # clocl
    self.add_empty_range(0xdc,1)
    # cia
    def cia_r(mode, addr):
      print("CIA read  @%08x" % addr)
      return (21, None)
    def cia_w(mode, addr, val):
      print("CIA write @%08x = %02x" % (addr, val))
    self.add_special_range(0xbf, 1, cia_r, cia_w)
    def custom_r(mode, addr):
      print("Cus read  @%08x" % addr)
      return (21, None)
    def custom_w(mode, addr, val):
      print("Cus write @%08x = %04x" % (addr, val))
    self.add_special_range(0xdf, 1, custom_r, custom_w)
