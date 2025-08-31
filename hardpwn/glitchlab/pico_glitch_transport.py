"""
Host-side Pico glitch transport: instructs Pico firmware to toggle pins for glitching.
The Pico firmware must implement GLITCH_V, GLITCH_C, GLITCH_R commands.
"""
import serial, time, json

class PicoGlitchTransport:
    def __init__(self, port, db=None, baud=115200, timeout=2.0):
        self.ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(1.0)
        self.db = db

    def _cmd(self, line, timeout=2.0):
        self.ser.reset_input_buffer()
        self.ser.write((line.strip()+"\n").encode())
        t0 = time.time()
        while time.time()-t0 < timeout:
            l = self.ser.readline().decode().strip()
            if not l:
                continue
            try:
                return json.loads(l)
            except Exception:
                return {'_raw':l}
        return {}

    def glitch_voltage(self, pulse_ns, delay_ns):
        r = self._cmd(f"GLITCH_V {pulse_ns} {delay_ns}", timeout=2.0)
        return r

    def glitch_clock(self, pulse_ns, delay_ns):
        r = self._cmd(f"GLITCH_C {pulse_ns} {delay_ns}", timeout=2.0)
        return r

    def glitch_reset(self, pulse_ns, delay_ns):
        r = self._cmd(f"GLITCH_R {pulse_ns} {delay_ns}", timeout=2.0)
        return r
