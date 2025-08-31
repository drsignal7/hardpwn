import traceback
from .types import ProbeReport, Finding
from .analysis import estimate_baud_from_edges, confidence_from_count

class AutoProber:
    def __init__(self, transport):
        """
        transport: object implementing methods:
          - list_pins()
          - capture_edges(pin, duration_ms)
          - uart_ports(), uart_try(port,baud)
          - i2c_scan(sda,scl)
          - spi_xfer(sclk,mosi,miso,cs,data)
          - jtag_try_idcode((tck,tms,tdi,tdo))
        """
        self.t = transport

    def run_probe(self, target_id="target"):
        report = ProbeReport(target_id=target_id)
        try:
            pins = self.t.list_pins()
            report.log(f"Scanning {len(pins)} pins")
        except Exception as e:
            report.log(f"Failed to list pins: {e}")
            pins = []

        # detect UART via host ports first
        try:
            ports = self.t.uart_ports()
            for p in ports:
                for baud in [115200, 57600, 38400, 19200, 9600]:
                    try:
                        d = self.t.uart_try(p, baud)
                        if d:
                            f = Finding(kind='uart', pins={'port':p}, confidence=0.95, meta={'baud':baud, 'sample': d.decode(errors='replace') if isinstance(d,bytes) else str(d)})
                            report.add_finding(f)
                            report.log(f"Detected UART at {p} @ {baud}")
                            raise StopIteration
                    except StopIteration:
                        break
                    except Exception:
                        continue
        except Exception:
            pass

        # detect UART on pins by edge capture (if supported)
        try:
            for pin in pins:
                try:
                    edges = self.t.capture_edges(pin, 300)
                    baud = estimate_baud_from_edges(edges)
                    if baud:
                        f = Finding(kind='uart', pins={'rx':pin}, confidence=0.7, meta={'baud':baud})
                        report.add_finding(f)
                        report.log(f"UART candidate on pin {pin} ~{baud}")
                        break
                except Exception:
                    continue
        except Exception:
            pass

        # I2C detection
        try:
            found=False
            for sda in pins:
                if found: break
                for scl in pins:
                    if sda == scl: continue
                    try:
                        addrs = self.t.i2c_scan(sda, scl)
                        if addrs:
                            conf = confidence_from_count(len(addrs))
                            f = Finding(kind='i2c', pins={'sda':sda,'scl':scl}, confidence=conf, meta={'addresses':[hex(a) for a in addrs]})
                            report.add_finding(f)
                            report.log(f"I2C found on sda={sda},scl={scl} -> {addrs}")
                            found=True
                            break
                    except Exception:
                        continue
        except Exception:
            pass

        # SPI detection (JEDEC)
        try:
            tried = 0
            spi_found=False
            for sclk in pins:
                if spi_found: break
                for mosi in pins:
                    if mosi==sclk: continue
                    for miso in pins:
                        if miso in (sclk,mosi): continue
                        for cs in pins:
                            if cs in (sclk,mosi,miso): continue
                            tried+=1
                            if tried>400: break
                            try:
                                resp = self.t.spi_xfer(sclk,mosi,miso,cs, bytes([0x9F,0,0,0]))
                                if resp and len(resp)>=4 and resp[1] not in (0x00,0xFF):
                                    f = Finding(kind='spi', pins={'sclk':sclk,'mosi':mosi,'miso':miso,'cs':cs}, confidence=0.9, meta={'jedec': resp[1:4].hex()})
                                    report.add_finding(f)
                                    report.log(f"SPI JEDEC {resp[1:4].hex()} at sclk={sclk} mosi={mosi} miso={miso} cs={cs}")
                                    spi_found=True
                                    break
                            except Exception:
                                continue
                        if spi_found: break
                    if spi_found: break
        except Exception:
            pass

        # JTAG detection
        try:
            tried=0
            jtag_found=False
            for tck in pins:
                if jtag_found: break
                for tms in pins:
                    if tms==tck: continue
                    for tdi in pins:
                        if tdi in (tck,tms): continue
                        for tdo in pins:
                            if tdo in (tck,tms,tdi): continue
                            tried+=1
                            if tried>800: break
                            try:
                                idc = self.t.jtag_try_idcode((tck,tms,tdi,tdo))
                                if idc:
                                    f = Finding(kind='jtag', pins={'tck':tck,'tms':tms,'tdi':tdi,'tdo':tdo}, confidence=0.85, meta={'idcode':hex(idc)})
                                    report.add_finding(f)
                                    report.log(f"JTAG IDCODE {hex(idc)} found at tck={tck}")
                                    jtag_found=True
                                    break
                            except Exception:
                                continue
                        if jtag_found: break
                    if jtag_found: break
        except Exception:
            pass

        # return and let caller log into DB
        return report

    def run_recon(self):
        """
        Helper to attempt chip identification using found SPI/I2C/JTAG hints.
        The transport can expose a helper. Return list of chip dicts.
        """
        try:
            chips = []
            if hasattr(self.t, 'identify_chips'):
                chips = self.t.identify_chips()
            return chips
        except Exception:
            return []
