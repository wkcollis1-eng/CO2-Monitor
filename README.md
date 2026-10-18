<div align="center">

# CO2 Monitor

**NDIR CO2 Sensing for Two Rooms, Built to Fail Visibly**

[![Hardware: CERN-OHL-S v2](https://img.shields.io/badge/Hardware-CERN--OHL--S%20v2-orange.svg)](LICENSE-HARDWARE)
[![Code: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE-CODE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/Docs-CC%20BY%204.0-lightgrey.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Draft%20firmware%2C%20not%20deployed-yellow.svg)](#status)
[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-EA4AAA.svg?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/wkcollis1-eng)

</div>

Two CO2 nodes, one in a bedroom and one in a family room. Each pairs an **Adafruit
SCD30** (PID 4867, a Sensirion NDIR sensor) with a **Seeed XIAO ESP32-C3** on a
small carrier board, inside a **Hammond 1551V4** enclosure. They run **ESPHome**
and report to **Home Assistant**.

All behaviour lives in one file, [`esphome/co2-node-common.yaml`](esphome/co2-node-common.yaml).
Each node file holds nothing but its name and its own API key.

---

## The problem this is built for

> It is 03:00 in a closed bedroom. The SCD30's cable worked loose an hour ago.
> Nobody is awake to notice, and nobody is coming to fix it tonight.

A CO2 sensor that has stopped answering is dangerous in one specific way: Home
Assistant keeps showing the last good number, and a flat, healthy-looking reading
is exactly what a dead sensor looks like. The acceptance test is **what the node
reports at that moment**, not whether it is online. The firmware is built around
three such moments, named in the header of the common file:

1. **Every boot.** ESPHome 2026.9.1 turns the SCD30's automatic self-calibration
   (ASC) **on** by default and writes that setting to the sensor at every boot
   [S: ESPHome 2026.9.1 source, `scd30/sensor.py:65`, `scd30/scd30.cpp:91`]. ASC
   assumes the sensor regularly sees fresh outdoor air. A closed room in a house
   with no HRV or ERV never does, so ASC would walk the baseline upward where
   nobody would see it. It is turned off explicitly.
2. **Power-up.** The SCD30's first reading after power-up is 0 ppm
   [S: `docs/adafruit-scd30.pdf` p10, p16], and ESPHome passes it through. A
   filter drops it. 0 ppm is not a possible indoor value, so dropping every 0
   costs nothing.
3. **The sensor stops answering.** After 240 s with no reading, the CO2 entity
   goes **unknown** and **CO2 Sensor Fault** turns on. After 900 s the node
   reboots to re-run the sensor setup, **at most three times in a row**. The
   counter survives the reboot, so a dead cable cannot turn into a reboot loop that
   hides it. After the third reboot the node stays up and keeps reporting the fault.

## Status

| | |
|---|---|
| Firmware | **Rev 1.0-draft**, 2026-10-18 |
| Compile | Both nodes compiled on **ESPHome 2026.9.1** with 0 compiler warnings and 0 errors [M: build logs, 2026-10-18; config_hash `0xa7e479a5` bedroom, `0xc9ec59d4` family room]. ESPHome's own advisory that an OTA password costs about 3.5 KB of flash prints for both, and is accepted |
| Watchdog | Host-simulated: the clean config passes all 35 checks, and each of the 5 injected faults is caught [M: `harness/faults.py`, 2026-10-18]. See [The watchdog harness](#the-watchdog-harness) for what that does and does not prove |
| Deployment | **Not deployed.** The firmware is not yet in the Home Assistant config |
| Hardware | **No new PCB.** The carrier is an existing ESP32-C3 sensor-node board. The KiCad file here is that board, unchanged, with the SCD30 and the enclosure placed on it for a 3D fit check |

## Repository layout

```
esphome/    Node firmware: co2-node-common.yaml plus one thin file per node
harness/    Host-side simulation of the watchdog lambdas, and its fault injector
hardware/   KiCad 10 board (fit-check model) and footprint library
  3d/                 Vendor 3D models: SCD30, XIAO ESP32-C3, USB-C plug
  adafruit-scd30/     Adafruit's EAGLE files for the SCD30 breakout, with their licence
  Seeed_XIAO_ESP32C3/ KiCad redraw of the XIAO's schematic, for net checking
docs/       Vendor primary sources: Hammond drawing, Sensirion and Adafruit
            SCD30 documents, Seeed XIAO schematic
```

## Hardware

| | |
|---|---|
| Carrier | 23.0 × 38.0 mm, 2-layer, 1.6 mm [M: the board file] |
| MCU | Seeed XIAO ESP32-C3 |
| Sensor | Adafruit SCD30 breakout (PID 4867), I2C address `0x61`. The only device on the bus |
| I2C | SDA GPIO6 (D4), SCL GPIO7 (D5), **50 kHz** [S: `docs/adafruit-scd30.pdf` p15-16] |
| Status LED | GPIO20 (D7). Kept dark: the box is opaque |
| Enclosure | Hammond 1551V4, 80 × 80 × 20.3 mm ABS [S: `docs/1551V4BK.pdf`] |

### PH1: sensor header

The SCD30 is cabled from its STEMMA QT socket to PH1, a 1x04 right-angle header.
No header is soldered to the SCD30.

| PH1 pad | Signal | QT wire |
|---|---|---|
| 1 | GND | black |
| 2 | +3V3 | red |
| 3 | SDA | blue |
| 4 | SCL | yellow |

> **Pad 2 is the square pad, not pad 1.** Count from the square pad and you will
> put 3V3 on the wrong wire. Place each wire by colour.

**Feed the breakout from 3V3, never 5 V.** The breakout's 10K SDA and SCL
pull-ups go to VIN [S: `hardware/adafruit-scd30/Adafruit SCD30.brd` netlist], so
VIN sets the high level that the XIAO's 3.3 V pins see on the bus.

### Fit in the enclosure

The 1551V4 is 15.30 mm deep inside, floor to cover [S: Hammond drawing, Section
A-A]. Both boards sit on standoffs on the enclosure floor, not on its bosses.
Figures marked [D] are arithmetic on dimensions measured from the vendor STEP
models:

- **The SCD30 is the tight part.** On 6 mm standoffs it clears the cover by
  0.735 mm nominal [D]. The sensor's height tolerance is ±0.70 mm [S: Sensirion
  SCD30 datasheet, Table 6], and the cover's moulded lettering stands 0.20 mm
  [M: cover STEP], so the worst case is a clash under the lettering. On 5 mm
  standoffs the worst case is 1.035 mm to the cover, or 0.835 mm under the
  lettering [D: 1.035 − 0.20]. The SCD30's standoff height is the open fit
  question.
- **The carrier** on 6 mm standoffs: a XIAO soldered in on pin headers leaves
  0.95 mm [D]. A socketed XIAO does not fit. The mounting screw under the
  XIAO has to go in before the XIAO does.
- The floor has a 1.0 mm recess at its centre, ±7.53 mm [M: base STEP]. Keep
  standoffs off it.

## Firmware

[`esphome/co2-node-common.yaml`](esphome/co2-node-common.yaml) holds all the
behaviour. [`bedroom-co2-node.yaml`](esphome/bedroom-co2-node.yaml) and
[`family-room-co2-node.yaml`](esphome/family-room-co2-node.yaml) hold only
`substitutions`, their own API encryption key, and the `packages:` include. Both
nodes therefore run the same behaviour from one copy, and a fix made once
reaches both.

### Entities

| Entity | Kind | Notes |
|---|---|---|
| CO2 | sensor, ppm | Every 60 s. **Unknown** when the sensor has been silent for 240 s |
| CO2 Sensor Fault | binary_sensor, problem | On from 240 s of silence until the next good reading |
| CO2 Stale Reboots | sensor, diagnostic | Recovery reboots in a row, 0 to 3. Cleared by a good reading |
| Node Status, WiFi Signal, Uptime, Free Heap, Loop Time | diagnostics | |
| Node ESPHome Version, Reset Reason | diagnostics | |
| Node Restart | button | |

**There is no SCD30 temperature or humidity entity, on purpose.** The SCD30 heats
itself, which skews both readings, and the rooms already have their own T/RH
sensors.

### Settings that matter

| Setting | Value | Why |
|---|---|---|
| `automatic_self_calibration` | `false` | Moment 1 above |
| `filters: filter_out` | `0.0` | Moment 2 above |
| `altitude_compensation` | `157m` | House elevation about 515 ft [D: 515 × 0.3048 = 156.97 m] |
| `update_interval` | `60s` | The watchdog's 240 s and 900 s are counted in these 60 s reads |
| `min_version` | `2026.9.1` | The only version it has been compiled on. Raise it only after a recompile |

### Calibration: outdoors, by hand

With ASC off, **forced recalibration (FRC) is the only calibration path.**
Sensirion's ±50 ppm lifetime drift figure holds only with ASC or FRC in use
[S: Sensirion SCD30 datasheet v1.0-D1, Table 1, p2; not in this repository].
The node exposes an API
action, `forced_recalibration(reference_ppm)`:

1. Take the node outdoors, or to an open window in steady air.
2. Leave it powered and reading there for several minutes.
3. Call the action with the outdoor reference, about 420 ppm [I: the global
   background; a local outdoor reading falsifies it, and wins].

The node refuses a reference outside 400 to 2000 ppm and logs the refusal.
**Never call it from an automation.** A reference given indoors bakes the
room's excess CO2 into every later reading.

### The watchdog

A 30 s interval measures the age of the last good reading. It uses unsigned
arithmetic, so it survives the 49-day `millis()` wrap.

| Age of last reading | Action |
|---|---|
| 240 s | CO2 goes unknown, CO2 Sensor Fault turns on, a warning is logged |
| 900 s | Recovery reboot, if fewer than 3 in a row so far. The count is stored in flash, so it survives the reboot |
| after the 3rd reboot | No more reboots. The node stays online, reporting the fault |

A recovery boot starts with the fault still on, so Home Assistant never sees a
"healthy" gap between reboots. The first good reading clears the fault and the
count. Why 240 s: four missed 60 s reads always raise the fault, and three can,
if a 30 s tick lands just before the fourth read is due. After boot, the dropped 0 ppm reading comes
at about 60 s and the first real one at about 120 s, which leaves about 120 s of
margin [I: falsified if a boot with a working sensor logs "no SCD30 reading"].

### Building

1. Copy the three files in `esphome/` into your ESPHome config directory.
2. Provide a `secrets.yaml` with these keys: `wifi_ssid`, `wifi_password`,
   `ap_password`, `ota_password`, `api_key_bedroom_co2_node`,
   `api_key_family_room_co2_node`.
3. Compile with ESPHome 2026.9.1 or later. Do the first flash over USB, then
   use OTA. Logging runs over the C3's native USB Serial/JTAG, which frees GPIO20
   for the LED.

Neither node file sets `wifi: use_address` yet. Add your DHCP reservation there
if your ESPHome host cannot resolve `.local` names.

## The watchdog harness

`harness/` runs the watchdog's real lambdas on a PC, against simulated time.

- [`gen.py`](harness/gen.py) extracts the `on_boot`, `on_value` and `interval`
  lambdas **verbatim** from `co2-node-common.yaml`, and wraps them in
  [`sim.cpp.in`](harness/sim.cpp.in). The lambda text is never retyped, so the
  test runs exactly what the firmware runs.
- `sim.cpp.in` stubs `millis()` (including the 32-bit wrap), the restored
  globals, `App.safe_reboot()` and the entities. It runs eight scenarios: healthy;
  a late first read at about 306 s; a sensor that dies and never returns; one
  that dies and returns at 50 min; a 100 s glitch; a 600 s glitch that recovers;
  healthy across the `millis()` wrap; and dead from power-up.
- [`faults.py`](harness/faults.py) proves the test can fail. It runs the clean
  config, which must PASS, then five single-span faults, each of which must FAIL:
  the NaN guard removed, the reboot cap raised to 4, the stale threshold cut to
  24 s, wrap-unsafe age arithmetic, and a recovery boot that clears the fault.

```
pip install ziglang pyyaml
python harness/faults.py esphome/co2-node-common.yaml harness/work
```

The last line should read `FAULTS: PASS (0 of 6 directions wrong)`. Last run on
Python 3.14.3, ziglang 0.16.0 and PyYAML 6.0.3 [M, 2026-10-18].

**What the harness does not prove:** anything about the SCD30 driver, the I2C
bus, or ESPHome's own flash storage. It shows that the lambdas, given the stubbed
behaviour, do what this README says. The stub for `safe_reboot()` persisting the
reboot count was taken from ESPHome 2026.9.1's shutdown order, where the globals
store themselves before the preferences flush. A different ESPHome version needs
that re-read.

## Working on the board

Open `hardware/CO2 Monitor.kicad_pro` in **KiCad 10**. The in-repo 3D models
resolve through `${KIPRJMOD}`, so a fresh clone renders the assembly without any
path fixing.

**This is a fit-check model, not a board to fabricate.** Its tracks, vias,
outline, and footprint placement and pads are identical to the carrier board's
own file [M: 69 tracks and vias, 8 outline items and 10 footprints compared,
2026-10-18]. The Hammond base and cover models hang on the SCD30 footprint.

Know these before you file a bug against it:

1. **The design rules belong to another board.** `CO2 Monitor.kicad_pro`
   carries a minimum clearance of 0.2032 mm and a copper-to-edge clearance of
   0.025 mm, inherited from an unrelated cap-touch board. The carrier's own
   rules are not in this repository. Set the rules yourself before any revision.
2. **`kicad-cli pcb drc` reports 16 to 18 findings, and the count varies from
   run to run on an unchanged file** [M: 6 runs, 2026-10-18]:

   | n | severity | rule | cause |
   |---|---|---|---|
   | 7 to 9 | error | `clearance` | 0.2000 mm SCL/SDA gaps against the inherited 0.2032 mm minimum. KiCad reports a different selection of track pairs on each run, always among the same 11 tracks |
   | 4 | warning | `lib_footprint_mismatch` | C1, LED, PH1, R1 differ from their library versions |
   | 4 | warning | `silk_edge_clearance` | cosmetic |
   | 1 | warning | `lib_footprint_issues` | U1: library `UPS_Custom` is not in this project's library table |

   Compare DRC results by the objects they name, not by the count.
3. **7 model references do not resolve:** 5 hidden ones, and 2 visible
   duplicates of the XIAO that point at files not in this repository. The XIAO
   renders from `3d/`, once.
4. **The footprint library's own 3D paths are broken.** The `.kicad_mod` files in
   `CO2_Monitor/CO2_Monitor.pretty/` point at paths that do not exist relative to
   this project. The board stores its footprints inline, and those copies are the
   ones that render, so this matters only if you re-place a footprint from the
   library. The library is also not registered in a `fp-lib-table`.

## Third-party assets

Full detail, including the terms for each file, is in
**[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)**. These files are *not*
covered by this repository's own licences.

| Asset | Origin | Terms |
|---|---|---|
| `hardware/3d/4867 Adafruit SCD30.step` | Adafruit, `Adafruit_CAD_Parts` | MIT |
| `hardware/adafruit-scd30/` | Adafruit, `Adafruit-SCD-30-PCB` | CC BY-SA 3.0 |
| `hardware/3d/seeed-studio-xiao-esp32-c3.step` | Seeed Studio | vendor file |
| `hardware/CO2_Monitor/CO2_Monitor.3dshapes/` | Hammond, split into base and cover | vendor file, modified |
| `hardware/3d/usb-c-…snapshot.1/` | GrabCAD community model | **author and licence not recovered**; delete it if that matters to you |
| `docs/*.pdf` | Hammond, Seeed, Sensirion, Adafruit | publisher's copyright |

## Credentials

Every credential resolves through ESPHome `!secret`. No `secrets.yaml` is
committed, and the repository's `.gitignore` excludes one. Each commit is
scanned by gitleaks at commit time, and the full history was scanned before
publication, with this repository's own rules. Those rules extend the defaults
to catch inline Wi-Fi and OTA credentials.

---

## License

Three licences, because this repository holds three different kinds of work:

| Content | Paths | Licence |
|---|---|---|
| Hardware design | `hardware/` | [CERN-OHL-S v2](LICENSE-HARDWARE) |
| Code | `esphome/`, `harness/` | [MIT](LICENSE-CODE) |
| Documentation | this README | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

See **[LICENSE](LICENSE)** for the full breakdown and attribution examples, and
**[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)** for the vendor files that
none of the above covers.

```
Copyright (C) 2026 William K. Collis

This source describes Open Hardware and is licensed under the CERN-OHL-S v2.

You may redistribute and modify this source and make products using it under
the terms of the CERN-OHL-S v2 (https://ohwr.org/cern_ohl_s_v2.txt).

This source is distributed WITHOUT ANY EXPRESS OR IMPLIED WARRANTY, INCLUDING
OF MERCHANTABILITY, SATISFACTORY QUALITY AND FITNESS FOR A PARTICULAR PURPOSE.
Please see the CERN-OHL-S v2 for applicable conditions.

Source location: https://github.com/wkcollis1-eng/CO2-Monitor
```

---

## 💝 Support This Project

[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-%E2%9D%A4-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/wkcollis1-eng)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-ffdd00?logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/wkcollis)

If the watchdog design or its harness saved you time on your own sensor node,
sponsorship funds continued instrumentation, hardware and documentation.
