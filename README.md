# 🔧 Hardpwn — Unified Hardware Hacking Automation Framework

<p align="center">
  <img src="https://img.shields.io/badge/status-beta-orange?style=flat-square" />
  <img src="https://img.shields.io/badge/platform-Raspberry%20Pi%20%7C%20Pico-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" />
</p>

---

## 📌 Overview

**Hardpwn** is a modular framework for **hardware security research and analysis**.  
It automates tedious hardware reverse engineering tasks, enabling researchers to move faster from *recon* to *firmware extraction* to *fault injection testing*.

The toolkit unifies three major stages of hardware hacking into one workflow:

- **AutoProber** → Identifies active debug/communication interfaces (UART, SPI, I²C, JTAG).  
- **FirmFlasher** → Extracts firmware from chips via supported protocols.  
- **GlitchLab** → Automates glitching attempts for fault injection experiments.  

Hardpwn is designed to be **extensible**, hardware-agnostic (supports Raspberry Pi and Pico), and integrates results into a central database for easy visualization and analysis.

---

## ✨ Key Features

- 🔍 **Automated Interface Recon**  
  - Detects common hardware interfaces from pin probing.  
  - Logs pinout mappings for reuse.  

- 📦 **Firmware Dumping**  
  - SPI flash, UART bootloaders, and JTAG memory reads.  
  - Dumps stored in `results/firmware/`.  

- ⚡ **Glitching Engine**  
  - Runs clock/voltage glitch attempts with configurable parameters.  
  - Logs successes/failures for reproducibility.  

- 🗄️ **Central Database**  
  - SQLite (`results/hardpwn.db`) holds all session data.  
  - Easy to query, integrate into GUI dashboards, or export.  

- 🔌 **Multi-Hardware Support**  
  - Raspberry Pi (full GPIO access).  
  - Raspberry Pi Pico (via USB serial interface).  

---

## 📂 Project Structure

```
hardpwn/
├── autoprobe/        # AutoProber backend logic
│   └── autoprobe.py
├── firmflasher/      # Firmware dumping engine
│   └── firmflasher.py
├── glitchlab/        # GlitchLab fault injection
│   └── glitchlab.py
├── database/         # SQLite wrapper
│   └── db.py
├── results/          # Logs, dumps, and database storage
│   ├── firmware/
│   └── hardpwn.db
├── main.py           # CLI orchestrator
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
```

---

## ⚙️ Installation

### Requirements
- Python **3.9+**
- `pip install -r requirements.txt`
- Supported hardware: **Raspberry Pi (3B+/4B/5)** or **Raspberry Pi Pico**

### Dependencies
```text
pyserial
spidev
smbus2
```

---

## ▶️ Usage

Run the tool from the project root:

```bash
python3 main.py [command] [options]
```

### Commands

#### 🔎 Probe
```bash
python3 main.py probe --transport pi
python3 main.py probe --transport pico --port /dev/ttyACM0
```
Discovers active interfaces (UART/SPI/I²C/JTAG).  

#### 📦 Flash
```bash
python3 main.py flash --transport pi
python3 main.py flash --transport pico --port /dev/ttyACM0
```
Extracts firmware and saves under `results/firmware/`.  

#### ⚡ Glitch
```bash
python3 main.py glitch --transport pi
python3 main.py glitch --transport pico --port /dev/ttyACM0
```
Runs glitch experiments, logging all attempts in the DB.  

---

## 📊 Data Management

Hardpwn keeps all results in a **central SQLite database**:

- `interfaces` → discovered pin mappings  
- `firmware` → dumps and metadata  
- `glitch` → glitch attempt logs  

To inspect:
```bash
sqlite3 results/hardpwn.db
.tables
SELECT * FROM interfaces;
```

This makes it easy to integrate a future **GUI frontend** or export to JSON/CSV for reporting.

---

## 🛠️ Development Notes

- Designed with **pluggable architecture**: researchers can extend by adding new protocol drivers.  
- Backend works in **simulation mode** if no hardware is connected (for testing logic).  
- Hardware drivers are intentionally minimal — actual wiring and power management must be handled by the researcher.  

---

## 🚦 Roadmap

- [ ] Qt GUI frontend (visualize results & control operations).  
- [ ] Advanced glitch strategies (e.g., pattern-based or adaptive).  
- [ ] Integration with external tools (OpenOCD, ChipWhisperer, Ghidra).  
- [ ] Plugin system for community-contributed modules.  

---

## ⚠️ Disclaimer

This project is provided **for research and educational use only**.  
Do not use on hardware without **explicit authorization**.  
The authors take no responsibility for misuse.

---

## 👤 Credits

<<<<<<< HEAD
Developed with ❤️ by **Prady**  
=======
Developed with ❤️ by **[Your Name / Handle]**  
>>>>>>> 83f524fe7485dba4e4ebfd67c0fe1b83598b4d75
Inspired by years of community hardware research and automation needs.  

---

✨ *Hardpwn aims to make hardware hacking workflows cleaner, faster, and reproducible — while keeping the details flexible enough for researchers to adapt to their targets.*  
