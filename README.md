# Printer power safety

Mains (230 V) power and safety circuit for a 3D printer with a Duet 2 WiFi controller and a 230 V bed heater
switched by an SSR. The circuit is built up in eight steps. Each step adds one protection and explains why
it is needed and how good it is.

![final circuit](docs/img/step7.png)

| Step | Adds | Rating |
|---|---|---|
| 0 | baseline: inlet, 1-pole switch, PSU 24 V, SSR, bed heater, Duet | – |
| 1 | bed thermal cutoff TH1 (in series with the heater) | ★★★★☆ |
| 2 | mains fuse F1 | ★★★☆☆ |
| 3 | 2-pole main switch Q0 | ★★★☆☆ |
| 4 | mains relays K1/K2, fail-safe 5 V loop, STOP button, 5 V standby PSU | ★★★★☆ |
| 5 | Arduino Nano supervisor (heartbeat watchdog, loop diagnostics) | ★★★★☆ |
| 6 | smoke detector SD119 in the loop | ★★★☆☆ |
| 7 | detector supply supervision relay K3 (detector becomes fail-safe) | ★★★★★ |

- **Full description, hazards and BOM after every step:** [docs/steps.md](docs/steps.md)
- **Final BOM:** [docs/bom.md](docs/bom.md)

## Files

- `kicad/printer_power_safety.kicad_pro` – the final circuit (same as step 7). Open this in KiCad 10.
- `kicad/steps/stepN_*.kicad_pro` – every step as its own small project.
- `kicad/safety.kicad_sym` – project symbols: split relay (coil / contact units), smoke detector, step-up module.
- `tools/gen_power.py` – generates all schematics and the docs from `tools/steps_text.py`.
  `tools/render.py` runs ERC and exports the PNG previews (Windows: KiCad CLI + headless Edge + Pillow).

```
python tools/gen_power.py
python tools/render.py
```

The schematics are generated: edit the generator (or edit in KiCad and stop regenerating that file).

## Status

Design study – **not built, not tested on hardware**. ERC passes on every step (0 errors, 0 warnings).
Before building, check against the Duet 2 documentation:
- powering the Duet from 5 V standby through 5V_EXT (internal 5 V jumper);
- which pin provides PS_ON or a GPIO for `M80`/`M81 C"…"`, and its voltage.

Also check the SD119 relay behaviour (NC closed when unpowered, open when the head is removed) on the real detector.

**Mains voltage can kill.** The 230 V side must be built and checked by a qualified person.
