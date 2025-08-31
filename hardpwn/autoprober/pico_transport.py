"""
Host-side Pico transport. Expects the Pico to run the provided pico_main.py MicroPython firmware
which replies JSON-line or simple text lines for commands.
"""
import serial, time, json
from typing import List, Tuple, Optional

class PicoSerialTransport:
    def __init__(self, port, db=None, baud=115200, timeout=2.0):
        self.ser = serial.Serial(port, baud, timeout=timeout)
        # give Pico time to boot
        time.sleep(1.5)
        self.db = db

    def _send(self, line, timeout=2.0):
        self.ser.reset_input_buffer()
        self.ser.write((line.strip()+"\n").encode())
        t0=time.time()
        while time.time()-t0 < timeout:
            line = self.ser.readline().decode().strip()
            if not line:
                continue
            # try JSON
            try:
                return json.loads(line)
            except Exception:
                return {'_raw': line}
        return {}

    def list_pins(self):
        r = self._send("LIST_PINS", 0.5)
        return r.get('pins', list(range(2,28)))

    def capture_edges(self, pin:int, duration_ms:int=300):
        r = self._send(f"CAPTURE_EDGES {pin} {duration_ms}", duration_ms/1000.0 + 0.5)
        return r.get('edges', [])

    def uart_ports(self):
        r = self._send("UART_PORTS", 0.5)
        return r.get('ports', [])

    def uart_try(self, port, baud, timeout=0.5):
        r = self._send(f"UART_TRY {port} {baud} {int(timeout*1000)}", timeout+0.5)
        if isinstance(r, dict) and 'data' in r:
            d = r['data']
            if isinstance(d, str):
                return d.encode()
            return d
        return b''

    def i2c_scan(self, sda:int, scl:int, freq_hz:int=100000):
        r = self._send(f"I2C_SCAN {sda} {scl} {freq_hz}", 2.0)
        return r.get('addresses', [])

    def spi_xfer(self, sclk, mosi, miso, cs, data:bytes, freq_hz=1000000, mode=0):
        import binascii
        r = self._send(f"SPI_XFER {sclk} {mosi} {miso} {cs} {binascii.hexlify(data).decode()}", 2.0)
        if isinstance(r, dict) and 'resp' in r:
            return bytes.fromhex(r['resp'])
        return b''

    def jtag_try_idcode(self, pins:Tuple[int,int,int,int]):
        r = self._send(f"JTAG_IDCODE {pins[0]} {pins[1]} {pins[2]} {pins[3]}", 1.0)
        if isinstance(r, dict) and 'idcode' in r:
            try:
                return int(r['idcode'], 16)
            except Exception:
                return None
        return None

    def identify_chips(self):
        r = self._send("IDENTIFY_CHIPS", 1.0)
        return r.get('chips', [])
