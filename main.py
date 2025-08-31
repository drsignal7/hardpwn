#!/usr/bin/env python3
"""
HardPWN orchestrator - CLI entrypoint.

Examples:
  # Probe using Raspberry Pi GPIO transports
  sudo python3 main.py probe --transport pi

  # Probe using Raspberry Pi Pico on /dev/ttyACM0 (Pico must run pico_main.py)
  python3 main.py probe --transport pico --port /dev/ttyACM0

  # Full run (probe -> recon -> flash -> glitch)
  sudo python3 main.py all --transport pi
"""
import argparse
import os
import sys
from hardpwn.utils.db import HardpwnDB

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["probe","recon","flash","glitch","all"], help="Action")
    p.add_argument("--transport", choices=["pi","pico"], required=True, help="Transport to use")
    p.add_argument("--port", help="Serial port for pico (e.g. /dev/ttyACM0)")
    return p.parse_args()

def choose_backends(transport, port, db):
    if transport == "pi":
        from hardpwn.autoprober.pigpio_transport import PiGpioTransport as APTrans
        from hardpwn.firmflasher.pigpio_transport import PiGpioFlasherTransport as FFTrans
        from hardpwn.glitchlab.pigpio_glitch_transport import PiGpioGlitchTransport as GTrans
        ap = APTrans(db)
        ff = FFTrans(db)
        gl = GTrans(db)
    else:
        if not port:
            raise SystemExit("Pico transport requires --port")
        from hardpwn.autoprober.pico_transport import PicoSerialTransport as APTrans
        from hardpwn.firmflasher.pico_transport import PicoFlasherTransport as FFTrans
        from hardpwn.glitchlab.pico_glitch_transport import PicoGlitchTransport as GTrans
        ap = APTrans(port, db)
        ff = FFTrans(port, db)
        gl = GTrans(port, db)
    return ap, ff, gl

def main():
    args = parse_args()
    os.makedirs("results", exist_ok=True)
    db = HardpwnDB("results/hardpwn.db")

    ap, ff, gl = choose_backends(args.transport, args.port, db)

    if args.action in ("probe", "all"):
        print("[*] Running probe...")
        report = ap.run_probe()
        print("[*] Probe finished.")
    if args.action in ("recon", "all"):
        print("[*] Running recon (chip identification)...")
        recon = ap.run_recon()
        print("[*] Recon finished:", recon)
    if args.action in ("flash", "all"):
        print("[*] Running firmware dump...")
        dumps = ff.run_dump()
        print("[*] Firmware dump finished:", dumps)
    if args.action in ("glitch", "all"):
        print("[*] Running glitch campaigns...")
        out = gl.run_campaigns()
        print("[*] Glitch campaigns finished:", out)

    print("[*] Exporting session JSON")
    out = db.export_json("results/session.json")
    print("[*] Session exported to", out)

if __name__ == "__main__":
    main()
