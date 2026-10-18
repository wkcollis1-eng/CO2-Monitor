# Third-Party Notices

This repository redistributes vendor and community files that are **not** covered
by the root [LICENSE](LICENSE). They are listed below with the terms that do
apply. Under CERN-OHL-S §1.7 and §3.3(d) these are *Available Components* and
remain licensed under their own terms.

Nothing here restricts **building the node**. The board in this repository is a
fit-check model of an existing carrier, and the files below are 3D visualisation
meshes, a reference breakout design and reference documents.

"Identical to upstream blob `xxxxxxxx`" means the file's git blob hash matches
that object in the named upstream repository, checked 2026-10-18. Where a file
could not be matched to a source, this says so.

---

## 3D models

### Adafruit SCD30 (PID 4867) mesh — MIT
- File: `hardware/3d/4867 Adafruit SCD30.step`
- Source: Adafruit Industries,
  [adafruit/Adafruit_CAD_Parts](https://github.com/adafruit/Adafruit_CAD_Parts),
  `4867 SCD-30 C02 Sensor/4867 Adafruit SCD30.step`. Identical to upstream blob
  `0ffdf9f8`
- Modifications: none
- License: MIT, as below. The notice has to travel with the file:

  ```
  MIT License

  Copyright (c) 2016 Adafruit Industries

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
  ```

### Seeed XIAO ESP32-C3 mesh
- File: `hardware/3d/seeed-studio-xiao-esp32-c3.step`
- Source: Seeed Studio, vendor-supplied CAD for the XIAO ESP32-C3. Byte-identical
  to the copy in
  [mmwave-presence-node](https://github.com/wkcollis1-eng/mmwave-presence-node)
- License: no explicit grant found in the file; redistributed as a
  manufacturer-supplied support file
- Modifications: none

### Hammond 1551V4 enclosure base and cover meshes
- Files: `hardware/CO2_Monitor/CO2_Monitor.3dshapes/Hammond_1551V4_Base.step` and
  `Hammond_1551V4_Cover.step`
- Source: Hammond Manufacturing's CAD model of the 1551V4BK enclosure
  (`1551V4BK.stp`, which is not included here)
- **Modified**: split on 2026-10-18 into separate base and cover bodies, so that
  each can hang on its own footprint. Both headers record the Open CASCADE STEP
  processor 8.0 as the writer
- License: no explicit grant found in the source file; redistributed as a
  manufacturer-supplied support file, modified as stated

### USB-C plug and cable mesh — **provenance not recovered**
- File: `hardware/3d/usb-c-type-c-male-connector-cable-1.snapshot.1/USB C Male connector cable.STEP`
- Source: by its snapshot directory name, the GrabCAD community library entry
  `usb-c-type-c-male-connector-cable-1`. The STEP header names SolidWorks 2019
  and is stamped `2025-04-26`, and its author and organisation fields are empty.
  The GrabCAD page refused automated access when this notice was written
  (HTTP 403, 2026-10-18), so **neither the author nor the licence could be
  confirmed**
- Modifications: none
- It is the plug shown in U1's USB-C socket in the 3D view, and in the two
  renders `hardware/CO2 Monitor_OPEN.png` and `CO2 Monitor_EXPLODED.png`.
  Nothing else uses it. If you need clean provenance, delete the directory and
  those two renders: the board, the firmware and every other file are
  unaffected, and the plug simply stops rendering.

## Board design files

### Adafruit SCD30 breakout PCB — **CC BY-SA 3.0**
- Files: `hardware/adafruit-scd30/Adafruit SCD30.brd` and `Adafruit SCD30.sch`
  (EAGLE)
- Source: Adafruit Industries,
  [adafruit/Adafruit-SCD-30-PCB](https://github.com/adafruit/Adafruit-SCD-30-PCB).
  Identical to upstream blobs `c3428bab` and `f0dffc69`
- Modifications: none
- License: Creative Commons Attribution-ShareAlike 3.0 Unported. Upstream's
  `README.md` and `license.txt` are carried beside the board files, unmodified
  (identical to upstream blobs `b0108dfd` and `1d1e1d6e`), because the licence
  section of that README requires it:

  > Adafruit invests time and resources providing this open source design, please
  > support Adafruit and open-source hardware by purchasing products from
  > [Adafruit](https://www.adafruit.com)!
  >
  > Designed by Limor Fried/Ladyada for Adafruit Industries.
  >
  > Creative Commons Attribution/Share-Alike, all text above must be included in
  > any redistribution.
  > See license.txt for additional details.

### Adafruit SCD30 fab print and schematic images
- Files: `hardware/adafruit-scd30/adafruit_products_SCD30_fab_print.png` and
  `adafruit_products_SCD30_sch.png`
- Source: by name, Adafruit Industries' images of the 4867's fabrication print
  and schematic. **Not matched to a source byte-for-byte**: neither is a blob in
  the PCB repository above
- Copyright Adafruit Industries
- Modifications: none

### Footprints and a schematic derived from vendor designs
These sit inside the CERN-OHL-S `hardware/` tree, but they are not wholly
original, so their sources are recorded here:

- `hardware/CO2_Monitor/CO2_Monitor.pretty/Adafruit_SCD30_Socketed.kicad_mod` was
  generated from the pad and outline geometry of `Adafruit SCD30.brd` above. To
  the extent that it is an adaptation of that CC BY-SA 3.0 work, it is also
  offered under CC BY-SA 3.0, with the Adafruit attribution above.
- `hardware/CO2_Monitor/CO2_Monitor.pretty/XIAO_ESP32C3_Socketed.kicad_mod` takes
  its body outline from the KiCad standard-library footprint
  `RF_Module:MCU_Seeed_ESP32C3`. The KiCad libraries are licensed under CC BY-SA
  4.0, with an exception that waives article 3 for designs that use them
  (https://www.kicad.org/libraries/license/). A footprint redistributed as part
  of a library is outside that exception, so to the extent this one adapts the
  KiCad footprint, it is also offered under CC BY-SA 4.0.
- `hardware/Seeed_XIAO_ESP32C3/` is a KiCad 10 redraw of Seeed Studio's XIAO
  ESP32C3 schematic (`docs/Seeeduino-XIAO-ESP32C3-SCH.pdf`), drawn so the module's
  nets could be checked against an independent transcription. **The circuit is
  Seeed Studio's design**, and the title block credits Seeed Studio. It is not
  claimed as original work.

## Documentation

All five PDFs in `docs/` are unmodified vendor documents, redistributed as the
primary references that the firmware comments and the README cite. Each remains
the copyright of its publisher.

| File | Publisher | Identity |
|---|---|---|
| `docs/1551V4BK.pdf` | Hammond Manufacturing | Drawing of the 1551V4BK enclosure |
| `docs/Seeeduino-XIAO-ESP32C3-SCH.pdf` | Seeed Studio | XIAO ESP32C3 schematic; EAGLE 9.6.2, created 2022-12-09 (PDF metadata) |
| `docs/Sensirion_CO2_Sensors_SCD30_Design-In_Guidelines_D1.pdf` | Sensirion AG | SCD30 design-in guidelines, D1; created 2019-02-25 (PDF metadata) |
| `docs/Sensirion_CO2_Sensors_SCD30_Interface_Description.pdf` | Sensirion AG | SCD30 interface description |
| `docs/adafruit-scd30.pdf` | Adafruit Industries | The "Adafruit SCD-30" learning guide, from learn.adafruit.com. The page numbers cited in `esphome/co2-node-common.yaml` refer to this PDF |

## Referenced but not redistributed

The board also uses 3D models from the KiCad standard libraries
(`${KICAD10_3DMODEL_DIR}`). Those files are **not** included here; they come from
your local KiCad installation. The board stores its footprints inline, so the
footprint-library nicknames it records (`UPS_Custom`, `Adafruit INA260`) are not
needed to open or render it.
