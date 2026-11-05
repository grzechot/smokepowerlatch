# BOM

## A5 24/5+Smoke (hardware protection complete)

| Ref | Part | Added | Note |
|---|---|---|---|
| J1 | IEC C14 inlet (A2+: module with fuse drawer) | A0 | – |
| SW1 | 1-pole rocker switch, near the inlet | A0 | with a reversed Schuko plug it may break N only |
| X1 | Wago lever terminals L / N (PE bypasses X1) | A0 | – |
| PS1 | PSU 24 V, class I (e.g. Mean Well LRS-350-24) | A0 | – |
| J4 | PE stud on the case, at the PS1 earth terminal | A0 | essential: insulation fault -> PE, not a live frame |
| U1 | SSR DC->AC 25 A, genuine, on heatsink | A0 | switching element, not a protection; fails shorted |
| J3 | Bed connector L / N, flexible silicone cable | A0 | – |
| HT1 | Bed heater 230 V | A0 | – |
| J7 | PE wire to the bed plate | A0 | – |
| U3 | Duet 2 WiFi | A0 | – |
| TH1 | Thermal cutoff KSD301 NC 130 °C, 250 V/10 A, on the bed | A1 | independent of SSR and firmware; bimetal resets when cool |
| F1 | Fuse T6.3A 5x20 (size to load) | A2 | short circuit / overload only |
| K1 | Relay 16 A NO, 5 V coil (e.g. G2RL-1A-E 5V) | A4 | removes 230 V from PS1 and SSR |
| D1 | Diode 1N4148, K1 coil flyback | A3 | – |
| PS2 | PSU 5 V standby, class II (e.g. Mean Well IRM-10-5) | A4 | keeps Duet, detector and Nano alive |
| B1 | Smoke detector SD119 (12 V, relay output set to NC) | A5 | any-cause fire detection; fail-safe only with K3 |
| U2 | Step-up MT3608 / XL6009 5 -> 12 V (IN- = OUT-) | A5 | detector supply |
| K3 | Relay G5V-1 12 V coil, 1 A NO | A5 | detector supply supervision |
| D3 | Diode 1N4148, K3 coil flyback | A5 | – |
| W1 | 3-wire sheathed cable 5V / 0V / OK to the module | A5 | a 5V-OK short bypasses the detector: route away from edges |

## A6 24/5+Smoke+Nano

| Ref | Part | Added | Note |
|---|---|---|---|
| J1 | IEC C14 inlet (A2+: module with fuse drawer) | A0 | – |
| SW1 | 1-pole rocker switch, near the inlet | A0 | with a reversed Schuko plug it may break N only |
| X1 | Wago lever terminals L / N (PE bypasses X1) | A0 | – |
| PS1 | PSU 24 V, class I (e.g. Mean Well LRS-350-24) | A0 | – |
| J4 | PE stud on the case, at the PS1 earth terminal | A0 | essential: insulation fault -> PE, not a live frame |
| U1 | SSR DC->AC 25 A, genuine, on heatsink | A0 | switching element, not a protection; fails shorted |
| J3 | Bed connector L / N, flexible silicone cable | A0 | – |
| HT1 | Bed heater 230 V | A0 | – |
| J7 | PE wire to the bed plate | A0 | – |
| U3 | Duet 2 WiFi | A0 | – |
| TH1 | Thermal cutoff KSD301 NC 130 °C, 250 V/10 A, on the bed | A1 | independent of SSR and firmware; bimetal resets when cool |
| F1 | Fuse T6.3A 5x20 (size to load) | A2 | short circuit / overload only |
| K1 | Relay 16 A NO, 5 V coil (e.g. G2RL-1A-E 5V) | A4 | removes 230 V from PS1 and SSR |
| D1 | Diode 1N4148, K1 coil flyback | A3 | – |
| PS2 | PSU 5 V standby, class II (e.g. Mean Well IRM-10-5) | A4 | keeps Duet, detector and Nano alive |
| B1 | Smoke detector SD119 (12 V, relay output set to NC) | A5 | any-cause fire detection; fail-safe only with K3 |
| U2 | Step-up MT3608 / XL6009 5 -> 12 V (IN- = OUT-) | A5 | detector supply |
| K3 | Relay G5V-1 12 V coil, 1 A NO | A5 | detector supply supervision |
| D3 | Diode 1N4148, K3 coil flyback | A5 | – |
| W1 | 3-wire sheathed cable 5V / 0V / OK to the module | A5 | a 5V-OK short bypasses the detector: route away from edges |
| A1 | Arduino Nano v3 (supervisor firmware) | A6 | watchdog + latch + diagnostics |
| Q1 | MOSFET AO3400 (logic level) | A6 | K1 coil driver |
| R1, R2 | 100 Ω gate resistor, 10 kΩ gate pull-down | A6 | Q1 off when undriven |
| R7 | 10 kΩ pull-down on the OK input | A6 | – |
| D4 | Schottky 1N5819 into the Nano 5V pin (no back-feed from USB) | A6 | – |
