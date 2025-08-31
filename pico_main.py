# pico_main.py - MicroPython firmware for Raspberry Pi Pico
# Implements a simple line protocol. Responds JSON on a single line for structured commands,
# and for large dumps sends a JSON header with {"size":N} then streams N raw bytes.

import sys, ujson, utime
from machine import Pin, SPI, I2C, UART

uart = UART(0, 115200)
# Adjust pins below if you wire differently
SPI_SCK = 18
SPI_MOSI = 19
SPI_MISO = 16
SPI_CS = 17

def reply(obj):
    try:
        uart.write(ujson.dumps(obj) + "\\n")
    except Exception as e:
        uart.write(ujson.dumps({"error":str(e)}) + "\\n")

def handle_list_pins():
    # Pico GPIOs 0..26 are common; return a simple list
    reply({"pins": list(range(0,27))})

def handle_check_uart():
    reply({"ok": True})

def handle_check_spi():
    # quick test: init SPI bus (may conflict with hardware wiring)
    try:
        spi = SPI(0, sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
        spi.deinit()
        reply({"ok": True})
    except Exception as e:
        reply({"ok": False, "error": str(e)})

def handle_i2c_scan(sda, scl, freq):
    try:
        i2c = I2C(1, sda=Pin(sda), scl=Pin(scl), freq=freq)
        addrs = i2c.scan()
        reply({"addresses": addrs})
    except Exception as e:
        reply({"addresses": [], "error": str(e)})

def hexlify(b):
    return ubinascii.hexlify(b).decode() if b else ""

def handle_spi_xfer(sclk, mosi, miso, cs, hexd):
    import ubinascii
    data = ubinascii.unhexlify(hexd)
    try:
        spi = SPI(0, sck=Pin(sclk), mosi=Pin(mosi), miso=Pin(miso))
        cs_pin = Pin(cs, Pin.OUT)
        cs_pin.value(0)
        resp = bytearray(len(data))
        spi.write_readinto(data, resp)
        cs_pin.value(1)
        reply({"resp": ubinascii.hexlify(resp).decode()})
    except Exception as e:
        reply({"resp":"", "error": str(e)})

def handle_spi_dump():
    # This is a high-level example for demo. Real SPI dump needs chip-specific commands and speed.
    import ubinascii
    spi = SPI(0, sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
    size = 64*1024  # change per need and wiring
    uart.write(ujson.dumps({"size": size}) + "\\n")
    # naive read: issue 0x03 reads (not universally correct)
    for addr in range(0, size, 256):
        cmd = bytes([0x03, (addr>>16)&0xFF, (addr>>8)&0xFF, addr&0xFF]) + bytes([0]*256)
        resp = bytearray(len(cmd))
        spi.write_readinto(cmd, resp)
        # last 256 bytes are data
        uart.write(resp[-256:])

def handle_glitch_v(pw_ns, delay_ns):
    # placeholder: implement MOSFET/power switching using a dedicated pin
    reply({"result":"NOT_IMPLEMENTED"})

# simple command dispatcher
def dispatch(line):
    parts = line.strip().split()
    if not parts:
        return
    cmd = parts[0].upper()
    try:
        if cmd == "LIST_PINS":
            handle_list_pins()
        elif cmd == "CHECK_UART":
            handle_check_uart()
        elif cmd == "CHECK_SPI":
            handle_check_spi()
        elif cmd == "I2C_SCAN" and len(parts) >= 3:
            handle_i2c_scan(int(parts[1]), int(parts[2]), int(parts[3]) if len(parts)>3 else 100000)
        elif cmd == "SPI_XFER" and len(parts) >= 6:
            handle_spi_xfer(int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]), parts[5])
        elif cmd == "SPI_DUMP":
            handle_spi_dump()
        elif cmd == "GLITCH_V" and len(parts) >= 3:
            handle_glitch_v(int(parts[1]), int(parts[2]))
        else:
            reply({"error":"unknown_cmd","raw":line})
    except Exception as e:
        reply({"error": str(e)})

# main loop reads from UART
def main_loop():
    buf = b""
    while True:
        if uart.any():
            ch = uart.read(1)
            if not ch:
                continue
            if ch in (b"\\n", b"\\r"):
                try:
                    line = buf.decode().strip()
                except Exception:
                    line = ""
                buf = b""
                if line:
                    dispatch(line)
            else:
                buf += ch
        else:
            utime.sleep_ms(10)

if __name__ == "__main__":
    main_loop()
