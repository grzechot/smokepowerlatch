"""Stages A0..A6 for the KiCad schematics, docs/steps.md and docs/bom.md.

The full descriptions (why, limits, effectiveness) are in docs/stages.md; here only the schematic notes and the parts list.
Features: th, fuse, relay, standby, smoke, nano. Each stage builds on the previous one.
"""

VARIANTS = [
    dict(code="A0", slug="firestarter", title="Firestarter", feats=set(), stars=0,
         notes=["A0 Firestarter: C14 inlet, 1-pole switch SW1, Wago X1, PSU 24 V, SSR, bed heater, Duet. No protection.",
                "PE from the inlet to the PE stud (PS1 earth) and directly to the bed plate; the bed connector carries L and N only."]),
    dict(code="A1", slug="24_thermalcut", title="24+ThermalCut", feats={"th"}, stars=2,
         notes=["A1: TH1 thermal cutoff on the bed, in series with the heater (KSD301 NC 130 °C, 250 V / 10 A).",
                "Opens without Duet or SSR - covers a shorted SSR. Screw it to the bed plate with thermal paste."]),
    dict(code="A2", slug="24_thermalcut_fuse", title="24+ThermalCut+Fuse", feats={"th", "fuse"}, stars=2,
         notes=["A2: F1 slow-blow fuse in L, right after the inlet (C14 inlet module with fuse drawer).",
                "Size: (bed W + PSU W / 0.85) / 230 V x 1.25, e.g. 750 W + 350 W -> T6.3A."]),
    dict(code="A3", slug="24_relay", title="24+Relay", feats={"th", "fuse", "relay"}, stars=3,
         notes=["A3: K1 relay in N, 24 V coil switched low side by Duet PS_ON. START S1 (230 V!) in parallel with the K1 contact.",
                "Hold START until Duet runs M80; M81 (e.g. in heater-fault.g) switches everything off. Inlet and switch at the front only.",
                "CHECK: Duet 2 PS_ON pin type and current."]),
    dict(code="A4", slug="24-5", title="24/5", feats={"th", "fuse", "relay", "standby"}, stars=3,
         notes=["A4: PS2 5 V standby, fed before K1. Duet on 5V_EXT, K1 with a 5 V coil, PS_ON switches the coil low side.",
                "No 230 V START: only low voltage at the front. M80 = PS1 + SSR on, M81 = off, Duet stays on.",
                "CHECK: Duet 2 5V_EXT jumper; PS_ON must never see more than 5 V."]),
    dict(code="A5", slug="24-5_smoke", title="24/5+Smoke", feats={"th", "fuse", "relay", "standby", "smoke"}, stars=4,
         notes=["A5: detector module mounted high: U2 5->12 V, SD119 and K3 coil on 12 V; chain SD119 NC + K3 NO fed from 5 V.",
                "3-wire bundle 5V / 0V / OK to PS2; OK feeds the K1 coil. Smoke, loss of 12 V or any broken wire -> K1 off.",
                "OK carries 5 V, never 12 V. Monthly: press the detector TEST button - the printer must switch off."]),
    dict(code="A6", slug="24-5_smoke_nano", title="24/5+Smoke+Nano", feats={"th", "fuse", "relay", "standby", "smoke", "nano"}, stars=4,
         notes=["A6: Arduino Nano supervisor on 5 V standby drives Q1 on the low side of the K1 coil.",
                "GATE = PS_ON active AND heartbeat HB fresh (< 5 s); latched off after OK drops or HB stops.",
                "Duet daemon.g toggles HB. R2 keeps Q1 off when the Nano is not driving it; R7 pulls OK low when the chain is open."]),
]

# feat: which feature brings the part; unless: part removed when that feature is present
PARTS = [
    dict(ref="J1", part="IEC C14 inlet (A2+: module with fuse drawer)", feat="base", opinion="–"),
    dict(ref="SW1", part="1-pole rocker switch, near the inlet", feat="base", opinion="with a reversed Schuko plug it may break N only"),
    dict(ref="X1", part="Wago lever terminals L / N (PE bypasses X1)", feat="base", opinion="–"),
    dict(ref="PS1", part="PSU 24 V, class I (e.g. Mean Well LRS-350-24)", feat="base", opinion="–"),
    dict(ref="J4", part="PE stud on the case, at the PS1 earth terminal", feat="base", opinion="essential: insulation fault -> PE, not a live frame"),
    dict(ref="U1", part="SSR DC->AC 25 A, genuine, on heatsink", feat="base", opinion="switching element, not a protection; fails shorted"),
    dict(ref="J3", part="Bed connector L / N, flexible silicone cable", feat="base", opinion="–"),
    dict(ref="HT1", part="Bed heater 230 V", feat="base", opinion="–"),
    dict(ref="J7", part="PE wire to the bed plate", feat="base", opinion="–"),
    dict(ref="U3", part="Duet 2 WiFi", feat="base", opinion="–"),
    dict(ref="TH1", part="Thermal cutoff KSD301 NC 130 °C, 250 V/10 A, on the bed", feat="th", opinion="independent of SSR and firmware; bimetal resets when cool"),
    dict(ref="F1", part="Fuse T6.3A 5x20 (size to load)", feat="fuse", opinion="short circuit / overload only"),
    dict(ref="K1", part="Relay 16 A NO, 24 V coil (e.g. G2RL-1A-E 24V)", feat="relay", unless="standby", opinion="removes 230 V from PS1 and SSR"),
    dict(ref="S1", part="START push button 1 NO, 230 V / 10 A", feat="relay", unless="standby", opinion="230 V at the button: inlet at the front only"),
    dict(ref="K1", part="Relay 16 A NO, 5 V coil (e.g. G2RL-1A-E 5V)", feat="standby", opinion="removes 230 V from PS1 and SSR"),
    dict(ref="D1", part="Diode 1N4148, K1 coil flyback", feat="relay", opinion="–"),
    dict(ref="PS2", part="PSU 5 V standby, class II (e.g. Mean Well IRM-10-5)", feat="standby", opinion="keeps Duet, detector and Nano alive"),
    dict(ref="B1", part="Smoke detector SD119 (12 V, relay output set to NC)", feat="smoke", opinion="any-cause fire detection; fail-safe only with K3"),
    dict(ref="U2", part="Step-up MT3608 / XL6009 5 -> 12 V (IN- = OUT-)", feat="smoke", opinion="detector supply"),
    dict(ref="K3", part="Relay G5V-1 12 V coil, 1 A NO", feat="smoke", opinion="detector supply supervision"),
    dict(ref="D3", part="Diode 1N4148, K3 coil flyback", feat="smoke", opinion="–"),
    dict(ref="W1", part="3-wire sheathed cable 5V / 0V / OK to the module", feat="smoke", opinion="a 5V-OK short bypasses the detector: route away from edges"),
    dict(ref="A1", part="Arduino Nano v3 (supervisor firmware)", feat="nano", opinion="watchdog + latch + diagnostics"),
    dict(ref="Q1", part="MOSFET AO3400 (logic level)", feat="nano", opinion="K1 coil driver"),
    dict(ref="R1, R2", part="100 Ω gate resistor, 10 kΩ gate pull-down", feat="nano", opinion="Q1 off when undriven"),
    dict(ref="R7", part="10 kΩ pull-down on the OK input", feat="nano", opinion="–"),
    dict(ref="D4", part="Schottky 1N5819 into the Nano 5V pin (no back-feed from USB)", feat="nano", opinion="–"),
]

FEAT_CODE = {"base": "A0", "th": "A1", "fuse": "A2", "relay": "A3", "standby": "A4", "smoke": "A5", "nano": "A6"}
