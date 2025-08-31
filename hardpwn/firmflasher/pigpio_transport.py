"""
Pi-based flasher implementing common flash access methods using spidev and smbus2.
WARNING: Generic read uses 0x03 (legacy) command. For many chips you will need 0x0B/fast-read
with dummy cycles. For robust extraction use flashrom when possible.
"""
import os
try:
    import spidev
except Exception:
    spidev = None

try:
    import smbus2
except Exception:
    smbus2 = None

class PiGpioFlasherTransport:
    def __init__(self, db=None):
        self.db = db
        if spidev:
            self.spi = spidev.SpiDev()
            try:
                self.spi.open(0,0)
                self.spi.max_speed_hz = 2000000
            except Exception:
                self.spi = None
        else:
            self.spi = None

    def dump_spi(self, outpath=None, size=1024*1024, chunk=4096):
        outpath = outpath or "results/dumps/spi_flash.bin"
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        if not self.spi:
            raise RuntimeError("spidev not available")
        with open(outpath, "wb") as fh:
            for addr in range(0, size, chunk):
                # send 0x03 + 3-byte addr then read chunk
                cmd = [0x03, (addr>>16)&0xFF, (addr>>8)&0xFF, addr&0xFF] + [0]*min(chunk, size-addr)
                resp = bytes(self.spi.xfer2(cmd))
                fh.write(resp[-min(chunk,size-addr):])
        if self.db: self.db.log_dump(outpath)
        return outpath

    def dump_i2c(self, outpath=None, addr=0x50, size=8192, page=32):
        outpath = outpath or "results/dumps/i2c_eeprom.bin"
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        if smbus2 is None:
            raise RuntimeError("smbus2 not available")
        bus = smbus2.SMBus(1)
        data = bytearray()
        for off in range(0, size, page):
            for i in range(page):
                try:
                    b = bus.read_byte(addr + ((off + i) & 0xFF))
                    data.append(b)
                except Exception:
                    data.append(0)
        bus.close()
        with open(outpath, "wb") as fh:
            fh.write(data[:size])
        if self.db: self.db.log_dump(outpath)
        return outpath

    def dump_uart(self, outpath=None):
        # Bootloader specific implementations needed for real devices (STM32/stlink, esp)
        # This placeholder returns no data
        return None

    def dump_jtag(self, outpath=None, size=64*1024, chunk=256):
        # JTAG memory reading is adapter-specific (openocd). Implement as needed.
        return None
