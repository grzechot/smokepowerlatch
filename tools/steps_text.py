"""Variant descriptions and parts list (single source for the schematic notes, docs/steps.md and docs/bom.md).

Hierarchy:
  A  core        – simplest hardware that protects against the worst faults (fire), A0 -> A4, each builds on the previous
  B  diagnostics – Nano supervisor, builds on A4
  C  service     – 2-pole main switch, builds on A4
  FULL           – A4 + B1 + C1
Features: th, fuse, relays, smoke, nano, q0.
"""

CORE = {"th", "fuse", "relays", "smoke"}

VARIANTS = [
    dict(code="A0", slug="baseline", title="baseline (no protection)", level="A", feats=set(), stars=0,
         rating="nothing limits a fault; the circuit only works when every part works.",
         notes=["A0 baseline: inlet, 1-pole switch, PSU 24 V, SSR, bed heater, Duet. PE to PSU case (FG) and bed.",
                "Duet switches the SSR from its BED output (BED+ = VIN, BED- low-side switched)."],
         why=["The simplest working circuit: C14 inlet, 1-pole switch, 24 V PSU, Duet, SSR and a 230 V bed heater.",
              "",
              "Hazards of this circuit:",
              "- **SSR fails shorted** (the most common SSR failure, frequent with counterfeit SSR-25DA): the bed heats at full power"
              " without end. Duet thermal-runaway detection can only switch the SSR input off – useless when the SSR is shorted.",
              "- **No fuse**: the house breaker (B16) protects the building wiring, not 0.5–0.75 mm² wires inside the printer.",
              "- **No way to cut power automatically** or by an emergency button; no fire detection.",
              "- **1-pole switch + reversible Schuko plug**: with the plug reversed the switch breaks N; PSU, SSR and heater stay live when OFF.",
              "- 230 V on a moving bed (cable flexing), SSR heating (≈1–1.5 W per amp, needs a heatsink), SSR off-state leakage"
              " (a few mA – the bed is live even when not heating, PE is essential)."]),
    dict(code="A1", slug="bed_thermal_cutoff", title="bed thermal cutoff", level="A", feats={"th"}, stars=4,
         rating="independent of firmware and SSR; protects only against bed overheating; a bimetal resets by itself.",
         notes=["A1: TH1 thermal cutoff on the bed, in series with the heater (KSD301 NC 130 °C, 250 V / 10 A).",
                "Opens without Duet or SSR – covers the shorted-SSR case. Mount on the bed with good thermal contact."],
         why=["**Why it is first:** a shorted SSR is the most likely way this printer starts a fire, and nothing in A0"
              " can stop it. A thermal cutoff fixed to the bed, in series with the heater, opens by physics – no firmware, no SSR."
              " One cheap part.",
              "",
              "- Cutoff temperature ≈ 15–20 °C above the highest bed set-point (110 °C for ABS → 130 °C).",
              "- Current rating above the heater current (750 W ≈ 3.3 A → 10 A part is fine).",
              "- **Bimetal (KSD301)** resets when cool: with a shorted SSR the bed oscillates around 130 °C instead of running away."
              " Survivable, but the fault is not latched. **One-shot thermal fuse** latches off (must be replaced)."]),
    dict(code="A2", slug="mains_fuse", title="mains fuse", level="A", feats={"th", "fuse"}, stars=3,
         rating="clears short circuits and overloads; does nothing against overheating at normal current (stuck SSR).",
         notes=["A2: F1 slow-blow fuse in L, right after the inlet (inlet module with fuse drawer).",
                "Size: (bed W + PSU W / 0.85) / 230 V x 1.25, e.g. 750 W + 350 W -> 5.3 A -> T6.3A."],
         why=["**Why it is necessary:** the building breaker is sized for the house wiring (16 A). A short inside the printer –"
              " a chafed heater cable, a failed PSU input – can burn thin internal wires before a B16 trips. A fuse sized to the"
              " printer load clears it quickly.",
              "",
              "- Slow-blow (T) because of PSU inrush current; fuse in L.",
              "- Practical part: C14 inlet module with fuse drawer – the same module often has a 2-pole switch (→ C1 at no extra cost).",
              "- It does **not** help with a stuck SSR: the heater current is normal, the fuse does not see a fault."]),
    dict(code="A3", slug="mains_relays_stop", title="mains relays K1/K2, STOP, START self-hold", level="A",
         feats={"th", "fuse", "relays"}, stars=4,
         rating="hard-wired emergency stop and cut of ALL 230 V loads, no automatic restart; automatic cut still depends on Duet firmware.",
         notes=["A3: K1 (L) and K2 (N) mains relays switch PSU 24 V and SSR. 5 V standby PSU PS2 is always on.",
                "Loop: +5V -> F2 -> STOP (NC) -> [START || K4 self-hold] -> coils K1, K2, K4 (+ flyback, lamp H1) -> Q1 -> GND.",
                "Any open = power off and stays off until START is pressed. Power on: Duet M80 (Q1 on), then press START.",
                "Duet runs on 5 V standby (5V_EXT) and drives Q1 via PS_ON (M80/M81 C\"pin\"); heater-fault.g calls M81.",
                "CHECK before wiring: Duet 2 5V_EXT jumper and PS_ON pin type/voltage (3.3 V -> logic-level MOSFET)."],
         why=["**Why it is necessary:** A1 and A2 cannot remove power when something goes wrong, and A4 (smoke) needs"
              " something to switch. Two 16 A relays in L and N take 230 V off the 24 V PSU and the SSR – this also kills a"
              " stuck SSR and a failing PSU.",
              "",
              "- **Fail-safe loop:** relays need current to stay on. A broken wire, a pressed STOP or a dead driver = power off.",
              "- **STOP** (mushroom, latching, NC) acts directly on the coils – no software in the path.",
              "- **START self-hold (K4):** a small relay in parallel with K1/K2 holds the loop through its own contact."
              " After any opening (STOP, smoke, wire, Duet) the printer stays off until someone presses START at the printer –"
              " no automatic restart when smoke clears or a loose contact closes again.",
              "- **Automatic cut:** Duet stays alive on the 5 V standby supply and switches Q1 (PS_ON). RRF calls"
              " `heater-fault.g` on thermal runaway – put `M81` there.",
              "- **Two 1-pole relays instead of one 2-pole:** 16 A per contact, and if one contact welds the other pole still opens.",
              "- **H1** shows the loop state; **F2** protects the 5 V loop wiring.",
              "- Limitation: if Duet hangs with PS_ON active, nothing cuts power automatically → B1."]),
    dict(code="A4", slug="smoke_detector", title="smoke detector SD119 + supply supervision K3", level="A", feats=set(CORE), stars=4,
         rating="fire from any cause cuts power without software; fail-safe on detector supply loss; late (smoke) detection.",
         notes=["A4: SD119 relay contact C-NC in the loop, powered 12 V from step-up U2 (5 V standby).",
                "K3 coil on the same 12 V, K3 NO contact in series with SD119: no 12 V -> K3 drops -> loop open.",
                "Smoke -> NC opens -> K1/K2 drop, START self-hold keeps them off after the smoke clears.",
                "Detector head removed from base -> C-NC open (relay in the head) -> loop open. Check this on your SD119.",
                "Monthly: press the detector TEST button - the printer must switch off."],
         why=["**Why it belongs to the core:** A1 watches only the bed. A fire can also start in the PSU, the wiring, the SSR,"
              " the hot end or the filament. A smoke detector reacts to all of them and its contact drops the relays directly.",
              "",
              "- 12 V from a small step-up (MT3608) on the 5 V standby rail – the detector works whenever the printer is plugged in.",
              "- **Why K3 comes with it, not later:** the detector's relay is energised only in alarm. Without supply (dead step-up,"
              " loose wire) its NC contact stays closed for ever – the loop looks fine and a fire would not cut the power."
              " K3 is held on by the same 12 V, so a missing supply opens the loop. A detector without K3 is not worth fitting.",
              "- K3: small 12 V signal relay (G5V-1, 1 A contact – the loop current is ≈ 0.25 A), D3 flyback diode.",
              "- Still not covered: a powered detector whose sensor is dead. Use the TEST button regularly.",
              "",
              "**Core complete after A4:** two independent hardware paths remove heater power (TH1 on the bed; K1/K2 via the loop),"
              " the loop is fail-safe (STOP, smoke, detector supply, broken wire), it does not restart by itself, and the 230 V"
              " side is fused. No software in the safety path except the automatic cut by Duet (PS_ON)."]),
    dict(code="B1", slug="supervisor", title="Nano supervisor (watchdog + diagnostics)", level="B", feats=CORE | {"nano"}, stars=4,
         rating="independent of Duet; catches a hung controller; tells why the loop opened; fails in the safe direction.",
         notes=["B1 (on A4): Arduino Nano drives Q1 only if PS_ON active AND heartbeat HB fresh (< 5 s).",
                "Duet daemon.g toggles HB (M42) every second. Nano dead or reset -> R2 pulls Q1 gate low -> relays off.",
                "Sense: STOP, SMOKE (after SD119), DET (after K3), LOOP (coils). 10k pull-downs; LOOP is pulled down by the coils.",
                "First open node from the left = cause: STOP pressed / smoke / detector unpowered / latched off (START)."],
         why=["**Why it is an extension, not core:** the core already cuts power in hardware for STOP, smoke and broken wires."
              " B1 adds two things: an independent watchdog for a hung Duet (in A3/A4 a frozen Duet with PS_ON active keeps"
              " the heaters powered) and diagnostics – which part opened the loop.",
              "",
              "Options considered:",
              "- **74HC123 retriggerable monostable** – no firmware, very robust, but no diagnostics. Good minimal watchdog.",
              "- **Arduino Nano (chosen)** – watchdog on HB + PS_ON, reads four loop nodes, can report to Duet,"
              " room for an independent bed thermistor. 5 V logic matches the loop.",
              "- **ESP32** – Wi-Fi alerts and logging, but 3.3 V, more complex, more ways to fail.",
              "- **Safety relay (e.g. Pilz PNOZ)** – certified, monitors contacts, but costly and oversized for a hobby printer.",
              "",
              "- Fail-safe: Q1 needs an active high gate from the Nano; R2 holds it low during reset or when the Nano is missing.",
              "- D4 stops the Nano's USB 5 V from feeding the standby rail.",
              "- Option (not drawn): second NTC on the bed read by the Nano → independent over-temperature cut-off."]),
    dict(code="C1", slug="two_pole_switch", title="2-pole main switch", level="C", feats=CORE | {"q0"}, stars=3,
         rating="service safety with a reversible plug; manual only, no fault protection.",
         notes=["C1 (on A4): Q0 2-pole main switch (L and N). A Schuko plug can be reversed – a 1-pole switch may break only N.",
                "Q0 also switches the 5 V standby PSU. Still unplug the printer before working inside."],
         why=["**Why it is an extension:** it protects the person servicing the printer, not against a fault while printing."
              " After A3 the relays already break L and N of the PSU and the SSR; what stays live behind a 1-pole switch with a"
              " reversed plug is the inlet wiring, F1 and the 5 V standby PSU.",
              "",
              "- A Schuko plug fits both ways. A 1-pole switch in the wire that happens to be N leaves everything at 230 V when 'off'.",
              "- 16 A rated rocker or the inlet module's built-in 2-pole switch (often in the same part as F1).",
              "- It is a manual isolator, not an automatic protection."]),
    dict(code="FULL", slug="full", title="full circuit (A4 + B1 + C1)", level="", feats=CORE | {"nano", "q0"}, stars=0,
         rating="core protections plus watchdog, diagnostics and 2-pole isolation.",
         notes=["Full circuit: core A4 + B1 Nano supervisor + C1 2-pole main switch.",
                "Before printing test every path: STOP, START self-hold, detector TEST button, pull 12 V, unplug HB, M81."],
         why=["All protections together. Remaining before building: verify the Duet 5V_EXT / PS_ON details, use a genuine SSR"
              " on a heatsink, a flexible strain-relieved bed cable, and test every path (STOP, START self-hold, TEST button,"
              " pull 12 V, unplug HB, M81) before printing."]),
]

# feat: which feature brings the part; unless: part removed when that feature is present
PARTS = [
    dict(ref="J1", part="IEC C14 inlet (with fuse: module with fuse drawer)", feat="base", stars=0, opinion="–"),
    dict(ref="SW1", part="1-pole rocker switch", feat="base", unless="q0", stars=1, opinion="breaks only one wire; with a reversed plug that can be N"),
    dict(ref="PS1", part="PSU 24 V, class I with FG (e.g. Mean Well LRS-350-24)", feat="base", stars=0, opinion="–"),
    dict(ref="J4", part="PE to PSU case (FG)", feat="base", stars=3, opinion="essential: insulation fault -> PE instead of live frame"),
    dict(ref="U1", part="SSR DC->AC 25 A, genuine, on heatsink", feat="base", stars=0, opinion="switching element, not a protection; fails shorted"),
    dict(ref="J3", part="Bed heater 230 V, 3-wire (L, N, PE), flexible cable", feat="base", stars=0, opinion="–"),
    dict(ref="J2, J5", part="Duet 2 WiFi VIN and BED terminals", feat="base", stars=0, opinion="–"),
    dict(ref="TH1", part="Thermal cutoff KSD301 NC 130 °C, 250 V/10 A, on the bed", feat="th", stars=4, opinion="independent of SSR and firmware; auto-reset (thermal fuse = latching)"),
    dict(ref="F1", part="Fuse T6.3A 5x20 (size to load)", feat="fuse", stars=3, opinion="short circuit / overload only"),
    dict(ref="K1, K2", part="Relay Omron G2RL-1A-E 5 V coil, 16 A NO", feat="relays", stars=4, opinion="removes 230 V from PSU and SSR; fail-safe (needs coil current)"),
    dict(ref="PS2", part="PSU 5 V 2 A standby, class II (Mean Well IRM-10-5)", feat="relays", stars=0, opinion="keeps Duet, loop and supervisor alive"),
    dict(ref="S1", part="Emergency STOP mushroom, latching, 1 NC", feat="relays", stars=4, opinion="hard-wired, no software in the path"),
    dict(ref="S2, K4", part="START push button 1 NO + relay G5V-1 5 V (self-hold)", feat="relays", stars=4, opinion="no automatic restart after any loop opening"),
    dict(ref="F2", part="Fuse 0.5 A (5 V loop)", feat="relays", stars=2, opinion="protects loop wiring"),
    dict(ref="Q1", part="MOSFET AO3400 (logic-level) + R1 100 Ω, R2 10 kΩ pull-down", feat="relays", stars=3, opinion="loop driver; pull-down = off when undriven"),
    dict(ref="D1, D2", part="Diode 1N4148 (coil flyback, shared by K1/K2/K4)", feat="relays", stars=0, opinion="–"),
    dict(ref="H1, R4", part="LED + 330 Ω (loop closed)", feat="relays", stars=1, opinion="indication only"),
    dict(ref="J6", part="Duet 5V_EXT / GND / PS_ON / HB (expansion header)", feat="relays", stars=0, opinion="–"),
    dict(ref="B1", part="Smoke detector SD119 (12 V, relay C-NC)", feat="smoke", stars=4, opinion="any-cause fire detection; fail-safe only together with K3"),
    dict(ref="U2", part="Step-up MT3608 5 -> 12 V", feat="smoke", stars=0, opinion="detector supply"),
    dict(ref="K3", part="Relay G5V-1 12 V coil, 1 A NO + D3 1N4148", feat="smoke", stars=5, opinion="detector supply supervision; makes B1 fail-safe"),
    dict(ref="A1", part="Arduino Nano v3 (supervisor firmware)", feat="nano", stars=4, opinion="independent watchdog + diagnostics; dies safe"),
    dict(ref="R5..R7", part="10 kΩ pull-downs on sense inputs STOP, SMOKE, DET", feat="nano", stars=0, opinion="–"),
    dict(ref="D4", part="Schottky 1N5819 into Nano 5V pin (no back-feed from USB)", feat="nano", stars=0, opinion="–"),
    dict(ref="Q0", part="Main switch 2-pole 16 A (replaces SW1)", feat="q0", stars=3, opinion="manual isolation of L and N"),
]

FEAT_CODE = {"base": "A0", "th": "A1", "fuse": "A2", "relays": "A3", "smoke": "A4", "nano": "B1", "q0": "C1"}
