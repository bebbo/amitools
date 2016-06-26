from __future__ import print_function

import os
import struct


class Helper(object):
  def __init__(self, rom_data):
    self.data = rom_data
    self.size = len(rom_data)
    self.kib = self.size / 1024

  def is_kick_rom(self, verify=True):
    if not self.check_size():
      return False
    if not self.check_header():
      return False
    if not self.check_footer():
      return False
    if self.get_rom_size_field() != self.kib:
      return False
    if verify:
      return self.verify_check_sum()
    else:
      return True

  def check_header(self):
    # expect 0x1114 0x4ef9
    val = self._read_long(0)
    if self.kib == 512:
      return val == 0x11144ef9
    elif self.kib == 256:
      return val == 0x11114ef9
    else:
      return False

  def check_footer(self):
    # expect 0x0019 ... 0x001f
    off = self.size - 14
    num = 0x19
    for i in xrange(7):
      val = self._read_word(off)
      if val != num:
        return False
      val += 1
      off += 2
    return True

  def check_size(self):
    # expect 256k or 512k ROM
    if self.size % 1024 != 0:
      return False
    if self.kib not in (256, 512):
      return False
    return True

  def calc_check_sum(self, skip_off=None):
    """Check internal kickstart checksum and return True if is correct"""
    chk_sum = 0
    num_longs = self.size / 4
    off = 0
    max_u32 = 0xffffffff
    for i in xrange(num_longs):
      val = struct.unpack_from(">I", self.data, off)[0]
      if off != skip_off:
        chk_sum += val
      off += 4
      if chk_sum > max_u32:
        chk_sum = chk_sum & max_u32
        chk_sum += 1
    return max_u32 - chk_sum

  def verify_check_sum(self):
    chk_sum = self.calc_check_sum()
    return chk_sum == 0

  def read_check_sum(self):
    sum_off = self.size - 0x18
    return self._read_long(sum_off)

  def recalc_check_sum(self):
    sum_off = self.size - 0x18
    return self.calc_check_sum(sum_off)

  def write_check_sum(self):
    cs = self.recalc_check_sum()
    sum_off = self.size - 0x18
    self._write_long(sum_off, cs)

  def write_rom_size_field(self):
    off = self.size - 0x14
    self._write_long(off, self.size)

  def write_header(self, jump_addr):
    val = 0x11114ef9 if self.kib == 256 else 0x11144ef9
    self._write_long(0, val)
    self._write_long(4, jump_addr)

  def write_footer(self):
    off = self.size - 0x10
    num = 0x18
    for i in xrange(8):
      self._write_word(off, num)
      num += 1
      off += 2

  def get_boot_pc(self):
    """return PC for booting the ROM"""
    return self._read_long(4)

  def get_rom_ver_rev(self):
    """get (ver, rev) version info from ROM"""
    return struct.unpack_from(">HH", self.data, 12)

  def get_rom_size_field(self):
    """return size of ROM stored in ROM itself"""
    off = self.size - 0x14
    return self._read_long(off)

  def get_base_addr(self):
    return self.get_boot_pc() & ~0xffff

  def _read_long(self, off):
    return struct.unpack_from(">I", self.data, off)[0]

  def _write_long(self, off, val):
    return struct.pack_into(">I", self.data, off, val)

  def _read_word(self, off):
    return struct.unpack_from(">H", self.data, off)[0]

  def _write_word(self, off, val):
    return struct.pack_into(">H", self.data, off, val)


class Loader(object):
  """Load kick rom images in different formats"""
  @classmethod
  def load(cls, kick_file, rom_key_file=None):
    raw_img = None
    rom_key = None
    # read rom image
    with open(kick_file, "rb") as fh:
      raw_img = fh.read()
    # coded rom?
    need_key = False
    if raw_img[:11] == 'AMIROMTYPE1':
      rom_img = raw_img[11:]
      need_key = True
    else:
      rom_img = raw_img
    # decode rom
    if need_key:
      # read key file
      if rom_key_file is None:
        path = os.path.dirname(kick_file)
        rom_key_file = os.path.join(path, "rom.key")
      with open(rom_key_file, "rb") as fh:
        rom_key = fh.read()
      rom_img = cls._decode(rom_img, rom_key)
    return rom_img

  @classmethod
  def _decode(cls, img, rom_key):
    data = bytearray(img)
    n = len(rom_key)
    for i in xrange(len(data)):
      off = i % n
      data[i] = data[i] ^ ord(rom_key[off])
    return bytes(data)


# tiny test
if __name__ == '__main__':
  import sys
  args = sys.argv
  n = len(args)
  if n > 1:
    ks_file = args[1]
  else:
    ks_file = 'amiga-os-310-a500.rom'
  print(ks_file)
  ks = Loader.load(ks_file,'rom.key')
  kh = Helper(ks)
  print("is_kick_rom", kh.is_kick_rom())
  print("pc=%08x" % kh.get_boot_pc())
  print("ver,rev=", kh.get_rom_ver_rev())
  print("size %08x == %08x" % (kh.get_rom_size_field(), len(ks)))
  print("base %08x" % kh.get_base_addr())
  print("get chk_sum=%08x" % kh.read_check_sum())
  print("calc chk_sum=%08x" % kh.recalc_check_sum())
#  with open("out.rom", "wb") as fh:
#    fh.write(ks.get_data())

