"""
Raspberry Pi transport for AutoProber (uses spidev, smbus2, pyserial, openocd).
This file attempts to use standard Pi APIs. Run on Raspbian with SPI/I2C enabled.
"""
import os
import subprocess
import time
from typing import List, Tuple, Optional

try:
    import spidev
except Exception:
    spidev = None

try:
    import smbus2
except Exception:
    smbus2 = None

def _exists_dev(path):
    return os.path.exists(path)

class PiGpioTransport:
    def __init__(self, db=None):
        self.db = db

    def list_pins(self) -> List[int]:
        # common BCM header pins 2..27
        return list(range(2, 28))

    def capture_edges(self, pin:int, duration_ms:int=300):
        # Not implemented here: for accurate capture use pigpio
        return []

    def uart_ports(self) -> List[str]:
        candidates = ['/dev/serial0','/dev/ttyAMA0','/dev/ttyS0','/dev/ttyUSB0','/dev/ttyACM0']
        return [p for p in candidates if _exists_dev(p)]

    def uart_try(self, port:str, baud:int, timeout:float=0.5):
        try:
            import serial
            s = serial.Serial(port, baud, timeout=timeout)
            data = s.read(512)
            s.close()
            return data
        except Exception:
            return b''

    def i2c_scan(self, sda:int, scl:int, freq_hz:int=100000) -> List[int]:
        # scan I2C buses 0 and 1, best-effort
        addrs = []
        if smbus2 is None:
            return addrs
        for busnum in (0,1):
            try:
                bus = smbus2.SMBus(busnum)
                for addr in range(0x03, 0x78):
                    try:
                        bus.read_byte(addr)
                        addrs.append(addr)
                    except Exception:
                        pass
                bus.close()
            except Exception:
                pass
        return sorted(set(addrs))

    def spi_xfer(self, sclk, mosi, miso, cs, data:bytes, freq_hz:int=1000000, mode:int=0) -> bytes:
        if spidev is None:
            raise RuntimeError("spidev not available")
        spi = spidev.SpiDev()
        spi.open(0, 0)
        spi.max_speed_hz = freq_hz
        spi.mode = mode
        resp = bytes(spi.xfer2(list(data)))
        spi.close()
        return resp

    def jtag_try_idcode(self, pins:Tuple[int,int,int,int]) -> Optional[int]:
        # Best-effort: try openocd scan_chain and parse any idcode hex occurrences.
        try:
            cmd = "openocd -c 'adapter_khz 1000' -c 'init' -c 'scan_chain' -c 'exit'"
            proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=8, text=True)
            out = proc.stdout
            for line in out.splitlines():
                if 'idcode' in line.lower() or 'idcode' in line:
                    import re
                    m = re.search(r'0x[0-9a-fA-F]+', line)
                    if m:
                        return int(m.group(0), 16)
        except Exception:
            pass
        return None

    def identify_chips(self):
        """
        Try to identify an SPI flash by issuing JEDEC 0x9F on /dev/spidev0.0.
        """
        chips = []
        try:
            jedec = self.spi_xfer(None,None,None,None, bytes([0x9F,0,0,0]))
            if jedec and len(jedec) >= 4:
                chips.append({'type':'spi_flash', 'jedec': jedec[1:4].hex()})
        except Exception:
            pass
        return chips
