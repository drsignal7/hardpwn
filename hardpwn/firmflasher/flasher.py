import os, datetime, traceback
from typing import List

class FirmFlasher:
    def __init__(self, transport, db=None, outdir='results/dumps'):
        """
        transport: an object implementing:
          - spi_read(addr,length) or spi_xfer(...)
          - i2c_read(sda,scl,addr,length) or i2c_read_page(...)
          - uart_boot_read(meta)
          - jtag_read_mem(addr,length)
        """
        self.t = transport
        self.db = db
        self.outdir = outdir
        os.makedirs(self.outdir, exist_ok=True)
        self.logs = []

    def _outpath(self, tag):
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(self.outdir, f"{tag}_{ts}.bin")

    def run_dump(self):
        dumps = []
        # Transport may provide a list of candidate interfaces to dump
        # We'll try SPI first, then I2C, UART, JTAG
        try:
            if hasattr(self.t, 'dump_spi'):
                p = self.t.dump_spi()
                if p:
                    dumps.append(p)
                    if self.db: self.db.log_dump(p)
        except Exception as e:
            self.logs.append(f"SPI dump failed: {e}")
        try:
            if hasattr(self.t, 'dump_i2c'):
                p = self.t.dump_i2c()
                if p:
                    dumps.append(p)
                    if self.db: self.db.log_dump(p)
        except Exception as e:
            self.logs.append(f"I2C dump failed: {e}")
        try:
            if hasattr(self.t, 'dump_uart'):
                p = self.t.dump_uart()
                if p:
                    dumps.append(p)
                    if self.db: self.db.log_dump(p)
        except Exception as e:
            self.logs.append(f"UART dump failed: {e}")
        try:
            if hasattr(self.t, 'dump_jtag'):
                p = self.t.dump_jtag()
                if p:
                    dumps.append(p)
                    if self.db: self.db.log_dump(p)
        except Exception as e:
            self.logs.append(f"JTAG dump failed: {e}")
        return dumps
