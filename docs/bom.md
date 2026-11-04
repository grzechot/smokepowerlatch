# BOM

## Core (A4)

| Ref | Part | Added | Protection | Opinion |
|---|---|---|---|---|
| J1 | IEC C14 inlet (with fuse: module with fuse drawer) | A0 | – | – |
| SW1 | 1-pole rocker switch | A0 | ★☆☆☆☆ | breaks only one wire; with a reversed plug that can be N |
| PS1 | PSU 24 V, class I with FG (e.g. Mean Well LRS-350-24) | A0 | – | – |
| J4 | PE to PSU case (FG) | A0 | ★★★☆☆ | essential: insulation fault -> PE instead of live frame |
| U1 | SSR DC->AC 25 A, genuine, on heatsink | A0 | – | switching element, not a protection; fails shorted |
| J3 | Bed heater 230 V, 3-wire (L, N, PE), flexible cable | A0 | – | – |
| J2, J5 | Duet 2 WiFi VIN and BED terminals | A0 | – | – |
| TH1 | Thermal cutoff KSD301 NC 130 °C, 250 V/10 A, on the bed | A1 | ★★★★☆ | independent of SSR and firmware; auto-reset (thermal fuse = latching) |
| F1 | Fuse T6.3A 5x20 (size to load) | A2 | ★★★☆☆ | short circuit / overload only |
| K1, K2 | Relay Omron G2RL-1A-E 5 V coil, 16 A NO | A3 | ★★★★☆ | removes 230 V from PSU and SSR; fail-safe (needs coil current) |
| PS2 | PSU 5 V 2 A standby, class II (Mean Well IRM-10-5) | A3 | – | keeps Duet, loop and supervisor alive |
| S1 | Emergency STOP mushroom, latching, 1 NC | A3 | ★★★★☆ | hard-wired, no software in the path |
| S2, K4 | START push button 1 NO + relay G5V-1 5 V (self-hold) | A3 | ★★★★☆ | no automatic restart after any loop opening |
| F2 | Fuse 0.5 A (5 V loop) | A3 | ★★☆☆☆ | protects loop wiring |
| Q1 | MOSFET AO3400 (logic-level) + R1 100 Ω, R2 10 kΩ pull-down | A3 | ★★★☆☆ | loop driver; pull-down = off when undriven |
| D1, D2 | Diode 1N4148 (coil flyback, shared by K1/K2/K4) | A3 | – | – |
| H1, R4 | LED + 330 Ω (loop closed) | A3 | ★☆☆☆☆ | indication only |
| J6 | Duet 5V_EXT / GND / PS_ON / HB (expansion header) | A3 | – | – |
| B1 | Smoke detector SD119 (12 V, relay C-NC) | A4 | ★★★★☆ | any-cause fire detection; fail-safe only together with K3 |
| U2 | Step-up MT3608 5 -> 12 V | A4 | – | detector supply |
| K3 | Relay G5V-1 12 V coil, 1 A NO + D3 1N4148 | A4 | ★★★★★ | detector supply supervision; makes B1 fail-safe |

## Full circuit (A4 + B1 + C1)

| Ref | Part | Added | Protection | Opinion |
|---|---|---|---|---|
| J1 | IEC C14 inlet (with fuse: module with fuse drawer) | A0 | – | – |
| PS1 | PSU 24 V, class I with FG (e.g. Mean Well LRS-350-24) | A0 | – | – |
| J4 | PE to PSU case (FG) | A0 | ★★★☆☆ | essential: insulation fault -> PE instead of live frame |
| U1 | SSR DC->AC 25 A, genuine, on heatsink | A0 | – | switching element, not a protection; fails shorted |
| J3 | Bed heater 230 V, 3-wire (L, N, PE), flexible cable | A0 | – | – |
| J2, J5 | Duet 2 WiFi VIN and BED terminals | A0 | – | – |
| TH1 | Thermal cutoff KSD301 NC 130 °C, 250 V/10 A, on the bed | A1 | ★★★★☆ | independent of SSR and firmware; auto-reset (thermal fuse = latching) |
| F1 | Fuse T6.3A 5x20 (size to load) | A2 | ★★★☆☆ | short circuit / overload only |
| K1, K2 | Relay Omron G2RL-1A-E 5 V coil, 16 A NO | A3 | ★★★★☆ | removes 230 V from PSU and SSR; fail-safe (needs coil current) |
| PS2 | PSU 5 V 2 A standby, class II (Mean Well IRM-10-5) | A3 | – | keeps Duet, loop and supervisor alive |
| S1 | Emergency STOP mushroom, latching, 1 NC | A3 | ★★★★☆ | hard-wired, no software in the path |
| S2, K4 | START push button 1 NO + relay G5V-1 5 V (self-hold) | A3 | ★★★★☆ | no automatic restart after any loop opening |
| F2 | Fuse 0.5 A (5 V loop) | A3 | ★★☆☆☆ | protects loop wiring |
| Q1 | MOSFET AO3400 (logic-level) + R1 100 Ω, R2 10 kΩ pull-down | A3 | ★★★☆☆ | loop driver; pull-down = off when undriven |
| D1, D2 | Diode 1N4148 (coil flyback, shared by K1/K2/K4) | A3 | – | – |
| H1, R4 | LED + 330 Ω (loop closed) | A3 | ★☆☆☆☆ | indication only |
| J6 | Duet 5V_EXT / GND / PS_ON / HB (expansion header) | A3 | – | – |
| B1 | Smoke detector SD119 (12 V, relay C-NC) | A4 | ★★★★☆ | any-cause fire detection; fail-safe only together with K3 |
| U2 | Step-up MT3608 5 -> 12 V | A4 | – | detector supply |
| K3 | Relay G5V-1 12 V coil, 1 A NO + D3 1N4148 | A4 | ★★★★★ | detector supply supervision; makes B1 fail-safe |
| A1 | Arduino Nano v3 (supervisor firmware) | B1 | ★★★★☆ | independent watchdog + diagnostics; dies safe |
| R5..R7 | 10 kΩ pull-downs on sense inputs STOP, SMOKE, DET | B1 | – | – |
| D4 | Schottky 1N5819 into Nano 5V pin (no back-feed from USB) | B1 | – | – |
| Q0 | Main switch 2-pole 16 A (replaces SW1) | C1 | ★★★☆☆ | manual isolation of L and N |
