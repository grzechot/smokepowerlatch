# Printer power safety

Mains (230 V) power and safety circuit for a 3D printer with a Duet 2 WiFi controller and a 230 V bed heater
switched by an SSR. Protections are added one at a time: first a **core** of simple hardware against the worst
faults, then independent **extensions** for diagnostics and service. Each variant explains why the protection is
needed and how good it is.

![core circuit](docs/img/A4.png)

```
A0 baseline ── A1 TH1 ── A2 F1 ── A3 K1/K2 + STOP + START ── A4 smoke + K3   CORE: against the worst
                                                               │
                                                               ├── B1 Nano supervisor      diagnostics
                                                               ├── C1 2-pole switch Q0     service
                                                               └── FULL = A4 + B1 + C1
```

| Variant | Adds | Rating |
|---|---|---|
| A0 | baseline: inlet, 1-pole switch, PSU 24 V, SSR, bed heater, Duet | – |
| A1 | bed thermal cutoff TH1 (in series with the heater) – shorted SSR | ★★★★☆ |
| A2 | mains fuse F1 – short circuit | ★★★☆☆ |
| A3 | mains relays K1/K2, fail-safe 5 V loop, STOP, START self-hold (K4), 5 V standby PSU | ★★★★☆ |
| A4 | smoke detector SD119 + supply supervision relay K3 – fire from any cause | ★★★★☆ |
| B1 | Arduino Nano supervisor: heartbeat watchdog, which part opened the loop | ★★★★☆ |
| C1 | 2-pole main switch Q0 – service with a reversible plug | ★★★☆☆ |
| FULL | A4 + B1 + C1 | |

- **Hazard table, full description and BOM of every variant:** [docs/steps.md](docs/steps.md)
- **BOM (core and full):** [docs/bom.md](docs/bom.md)

## Files

- `kicad/printer_power_safety.kicad_pro` – the full circuit (same as FULL). Open this in KiCad 10.
- `kicad/steps/<code>_*.kicad_pro` – every variant as its own small project.
- `kicad/safety.kicad_sym` – project symbols: split relay (coil / contact units), smoke detector, step-up module.
- `tools/gen_power.py` – generates all schematics and the docs from `tools/steps_text.py`.
  `tools/render.py` runs ERC and exports the PNG previews (Windows: KiCad CLI + headless Edge + Pillow).

```
python tools/gen_power.py
python tools/render.py
```

The schematics are generated: edit the generator (or edit in KiCad and stop regenerating that file).

## Status

Design study – **not built, not tested on hardware**. ERC passes on every variant (0 errors, 0 warnings).
Before building, check against the Duet 2 documentation:
- powering the Duet from 5 V standby through 5V_EXT (internal 5 V jumper);
- which pin provides PS_ON or a GPIO for `M80`/`M81 C"…"`, and its voltage.

Also check the SD119 relay behaviour (NC closed when unpowered, open when the head is removed) on the real detector.

**Mains voltage can kill.** The 230 V side must be built and checked by a qualified person.
