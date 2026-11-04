# BOM – final circuit (step 7)

| Ref | Part | Added | Protection | Opinion |
|---|---|---|---|---|
| J1 | IEC C14 inlet (from step 2: module with fuse drawer) | 0 | – | – |
| PS1 | PSU 24 V, class I with FG (e.g. Mean Well LRS-350-24) | 0 | – | – |
| J4 | PE to PSU case (FG) | 0 | ★★★☆☆ | essential: insulation fault -> PE instead of live frame |
| U1 | SSR DC->AC 25 A, genuine, on heatsink | 0 | – | switching element, not a protection; fails shorted |
| J3 | Bed heater 230 V, 3-wire (L, N, PE), flexible cable | 0 | – | – |
| J2, J5 | Duet 2 WiFi VIN and BED terminals | 0 | – | – |
| TH1 | Thermal cutoff KSD301 NC 130 °C, 250 V/10 A, on the bed | 1 | ★★★★☆ | independent of SSR and firmware; auto-reset (thermal fuse = latching) |
| F1 | Fuse T6.3A 5x20 (size to load) | 2 | ★★★☆☆ | short circuit / overload only |
| Q0 | Main switch 2-pole 16 A | 3 | ★★★☆☆ | manual isolation of L and N |
| K1, K2 | Relay Omron G2RL-1A-E 5 V coil, 16 A NO | 4 | ★★★★☆ | removes 230 V from PSU and SSR; fail-safe (needs coil current) |
| PS2 | PSU 5 V 2 A standby, class II (Mean Well IRM-10-5) | 4 | – | keeps Duet, loop and supervisor alive |
| S1 | Emergency STOP mushroom, latching, 1 NC | 4 | ★★★★☆ | hard-wired, no software in the path |
| F2 | Fuse 0.5 A (5 V loop) | 4 | ★★☆☆☆ | protects loop wiring |
| Q1 | MOSFET AO3400 (logic-level) + R1 100 Ω, R2 10 kΩ pull-down | 4 | ★★★☆☆ | loop driver; pull-down = off when undriven |
| D1, D2 | Diode 1N4148 (coil flyback) | 4 | – | – |
| H1, R4 | LED + 330 Ω (loop closed) | 4 | ★☆☆☆☆ | indication only |
| J6 | Duet 5V_EXT / GND / PS_ON / HB (expansion header) | 4 | – | – |
| A1 | Arduino Nano v3 (supervisor firmware) | 5 | ★★★★☆ | independent watchdog; dies safe |
| R5..R7 | 10 kΩ pull-downs on sense inputs (added with each sense line) | 5 | – | – |
| D4 | Schottky 1N5819 into Nano 5V pin (no back-feed from USB) | 5 | – | – |
| B1 | Smoke detector SD119 (12 V, relay C-NC) | 6 | ★★★☆☆ | any-cause fire detection; fail-unsafe alone |
| U2 | Step-up MT3608 5 -> 12 V | 6 | – | detector supply |
| K3 | Relay G5V-1 12 V coil, 1 A NO + D3 1N4148 | 7 | ★★★★★ | detector supply supervision; makes B1 fail-safe |
