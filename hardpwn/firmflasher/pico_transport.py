"""
Host-side Pico flasher that instructs Pico firmware to read SPI/I2C/JTAG and return data.
The Pico microcontroller performs the low-level reads and streams data back; host writes binary file.
"""
import serial, time, json, binascii, os

class PicoFlasherTransport:
    def __init__(self, port, db=None, baud=115200, timeout=5.0):
        self.ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(1.0)
        self.db = db

    def _cmd(self, cmd, timeout=5.0):
        self.ser.reset_input_buffer()
        self.ser.write((cmd.strip()+"\n").encode())
        t0=time.time()
        out=b""
        # some commands may stream raw bytes rather than JSON; follow protocol:
        # Expect first line JSON with {'type':'ok','size':N} then read N bytes raw.
        line = self.ser.readline().decode().strip()
        if not line:
            return {}
        try:
            j = json.loads(line)
            return j
        except Exception:
            return {'_raw': line}

    def run_streamed_dump(self, cmd, outpath):
        # Instruct pico to start dump; Pico will first send JSON status {"size":N}
        self.ser.reset_input_buffer()
        self.ser.write((cmd.strip()+"\n").encode())
        header = self.ser.readline().decode().strip()
        try:
            meta = json.loads(header)
            size = int(meta.get('size',0))
        except Exception:
            return None
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        with open(outpath, "wb") as fh:
            remaining = size
            while remaining > 0:
                chunk = self.ser.read(min(4096, remaining))
                if not chunk:
                    break
                fh.write(chunk)
                remaining -= len(chunk)
        if self.db: self.db.log_dump(outpath)
        return outpath

    def dump_spi(self, outpath="results/dumps/pico_spi.bin"):
        return self.run_streamed_dump("SPI_DUMP", outpath)

    def dump_i2c(self, outpath="results/dumps/pico_i2c.bin"):
        return self.run_streamed_dump("I2C_DUMP", outpath)

    def dump_jtag(self, outpath="results/dumps/pico_jtag.bin"):
        return self.run_streamed_dump("JTAG_DUMP", outpath)
