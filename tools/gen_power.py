"""Generate the printer power-safety schematics, variant by variant (KiCad 10).

Usage:  python tools/gen_power.py            (from the repo root)
Writes kicad/safety.kicad_sym, kicad/steps/<code>_*.kicad_sch, kicad/printer_power_safety.kicad_sch (= FULL)
and docs/steps.md + docs/bom.md. Rendering to PNG: tools/render.py.
Variants and their hierarchy (A core, B diagnostics, C service): tools/steps_text.py.

Layout: ladder diagram. Mains harness = three horizontal rails (L, N, PE) at the top, loads tap down.
Low-voltage harness = +5V / GND rails at the bottom, the 5 V safety loop is one horizontal rung.
Signal lines (PS_ON, HB, SENSE_*) use net labels; power lines are drawn as wires.
"""
import os, uuid, copy
from sexp import parse, dump, find, uq
from steps_text import VARIANTS, PARTS, FEAT_CODE

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KLIB = "C:/Program Files/KiCad/10.0/share/kicad/symbols/"
PROJECT = "printer_power_safety"
q = lambda s: '"%s"' % str(s).replace('"', '\\"')
U = lambda: q(uuid.uuid4())
RED, BLUE = "200 0 0", "0 0 194"

# ---------------------------------------------------------------- project symbol library
SAFETY_LIB = '''(kicad_symbol_lib (version 20241209) (generator "gen_power")
 (symbol "RELAY_SPLIT" (pin_names (offset 0.254) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  (property "Reference" "K" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
  (property "Value" "RELAY_SPLIT" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (property "Description" "Relay drawn as separate units: A = coil, B = NO contact" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (symbol "RELAY_SPLIT_1_1"
   (rectangle (start -2.54 -1.524) (end 2.54 1.524) (stroke (width 0.254) (type default)) (fill (type background)))
   (pin passive line (at -5.08 0 0) (length 2.54) (name "A1" (effects (font (size 1.27 1.27)))) (number "A1" (effects (font (size 1.27 1.27)))))
   (pin passive line (at 5.08 0 180) (length 2.54) (name "A2" (effects (font (size 1.27 1.27)))) (number "A2" (effects (font (size 1.27 1.27))))))
  (symbol "RELAY_SPLIT_2_1"
   (polyline (pts (xy -2.54 0) (xy 2.286 1.778)) (stroke (width 0.254) (type default)) (fill (type none)))
   (polyline (pts (xy 2.54 0) (xy 2.54 0.762)) (stroke (width 0.254) (type default)) (fill (type none)))
   (pin passive line (at -5.08 0 0) (length 2.54) (name "13" (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27)))))
   (pin passive line (at 5.08 0 180) (length 2.54) (name "14" (effects (font (size 1.27 1.27)))) (number "14" (effects (font (size 1.27 1.27)))))))
 (symbol "SMOKE_DET" (pin_names (offset 0.254) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  (property "Reference" "B" (at 0 6.35 0) (effects (font (size 1.27 1.27))))
  (property "Value" "SMOKE_DET" (at 0 8.89 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (property "Description" "Smoke detector, 12 V, relay output C-NC (NC opens on alarm; NC is CLOSED when unpowered)" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (symbol "SMOKE_DET_0_1"
   (rectangle (start -7.62 -3.81) (end 7.62 3.81) (stroke (width 0.254) (type default)) (fill (type background)))
   (polyline (pts (xy -7.62 0) (xy -2.54 0) (xy 3.302 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
   (polyline (pts (xy 2.54 -1.524) (xy 2.54 0) (xy 7.62 0)) (stroke (width 0.254) (type default)) (fill (type none)))
   (text "+12V" (at -5.08 -2.794 0) (effects (font (size 0.889 0.889))))
   (text "0V" (at 5.08 -2.794 0) (effects (font (size 0.889 0.889))))
   (text "C" (at -6.35 1.27 0) (effects (font (size 0.889 0.889))))
   (text "NC" (at 5.715 1.27 0) (effects (font (size 0.889 0.889)))))
  (symbol "SMOKE_DET_1_1"
   (pin passive line (at -10.16 0 0) (length 2.54) (name "C" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
   (pin passive line (at 10.16 0 180) (length 2.54) (name "NC" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
   (pin power_in line (at -5.08 -6.35 90) (length 2.54) (name "+12V" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
   (pin power_in line (at 5.08 -6.35 90) (length 2.54) (name "0V" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))))
 (symbol "DCDC_STEPUP" (pin_names (offset 0.254)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  (property "Reference" "U" (at 0 6.35 0) (effects (font (size 1.27 1.27))))
  (property "Value" "DCDC_STEPUP" (at 0 -8.89 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (property "Description" "Non-isolated step-up module, common GND" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (symbol "DCDC_STEPUP_0_1"
   (rectangle (start -7.62 -5.08) (end 7.62 5.08) (stroke (width 0.254) (type default)) (fill (type background))))
  (symbol "DCDC_STEPUP_1_1"
   (pin power_in line (at -10.16 2.54 0) (length 2.54) (name "IN+" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
   (pin power_out line (at 10.16 2.54 180) (length 2.54) (name "OUT+" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
   (pin passive line (at 0 -7.62 90) (length 2.54) (name "GND" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))))
'''

_libs = {}
def lib_table(lib):
    if lib not in _libs:
        path = os.path.join(ROOT_DIR, "kicad", "safety.kicad_sym") if lib == "safety" else KLIB + lib + ".kicad_sym"
        _libs[lib] = {uq(s[1]): s for s in find(parse(open(path, encoding="utf8").read()), "symbol")}
    return _libs[lib]

def libsym(lib, name):
    syms = lib_table(lib)
    s = copy.deepcopy(syms[name])
    ext = find(s, "extends")
    if ext:                                      # flatten a derived symbol
        base = copy.deepcopy(syms[uq(ext[0][1])])
        bname = uq(base[1])
        s = [e for e in s if not (isinstance(e, list) and e[0] == "extends")]
        for e in base:
            if isinstance(e, list) and e[0] == "symbol":
                e[1] = q(uq(e[1]).replace(bname, name, 1)); s.append(e)
            elif isinstance(e, list) and e[0] in ("pin_names", "pin_numbers", "exclude_from_sim", "in_bom", "on_board") and not find(s, e[0]):
                s.insert(2, e)
    s[1] = q(lib + ":" + name)
    return s

def sym_pins(s, unit):
    out = {}
    for sub in find(s, "symbol"):
        u = int(uq(sub[1]).rsplit("_", 2)[-2])
        if u not in (0, unit):
            continue
        for p in find(sub, "pin"):
            a = find(p, "at")[0]
            out[uq(find(p, "number")[0][1])] = (float(a[1]), float(a[2]))
    return out

def xform(px, py, rot, mirror):
    if mirror:
        px = -px
    px, py = {0: (px, py), 90: (-py, px), 180: (-px, -py), 270: (py, -px)}[rot]
    return px, -py                               # screen y grows downwards

# ---------------------------------------------------------------- schematic builder
class Sheet:
    def __init__(self, title):
        self.title, self.items, self.libs, self.root = title, [], {}, str(uuid.uuid4())
        self.wires, self.pins, self.nc_pins = [], [], []

    def place(self, ref, lib, name, value, at=None, anchor=None, rot=0, mirror=False, unit=1,
              ref_at=None, val_at=None, hide_ref=False, hide_val=False, nc=True):
        s = libsym(lib, name)
        self.libs[lib + ":" + name] = s
        rel = {n: xform(px, py, rot, mirror) for n, (px, py) in sym_pins(s, unit).items()}
        if anchor:                               # place so that pin anchor[0] lands on anchor[1]
            pn, (ax, ay) = anchor
            at = (ax - rel[pn][0], ay - rel[pn][1])
        x, y = round(at[0], 2), round(at[1], 2)
        pp = {n: (round(x + dx, 2), round(y + dy, 2)) for n, (dx, dy) in rel.items()}
        power = ref.startswith("#")
        self.pins += list(pp.values())
        if not power:
            if nc:
                self.nc_pins += list(pp.values())
        rx, ry = ref_at or (x, y - 6)
        vx, vy = val_at or (x, y + 6)
        F = '(effects (font (size 1.27 1.27))%s)'
        props = [("Reference", ref, rx, ry, power or hide_ref), ("Value", value, vx, vy, (power and name == "PWR_FLAG") or hide_val),
                 ("Footprint", "", x, y, True), ("Datasheet", "", x, y, True)]
        t = '(symbol (lib_id %s) (at %s %s %d)%s (unit %d) (exclude_from_sim no) (in_bom %s) (on_board %s) (dnp no) (uuid %s)\n' % (
            q(lib + ":" + name), x, y, rot, " (mirror y)" if mirror else "", unit, "no" if power else "yes", "no" if power else "yes", U())
        for k, v, px, py, h in props:
            t += '\t(property %s %s (at %s %s %d) %s)\n' % (q(k), q(v), px, py, rot if rot in (90, 270) else 0, F % (" (hide yes)" if h else ""))
        for n in pp:
            t += '\t(pin %s (uuid %s))\n' % (q(n), U())
        t += '\t(instances (project %s (path %s (reference %s) (unit %d)))))' % (q(PROJECT), q("/" + self.root), q(ref), unit)
        self.items.append(t)
        return pp

    def wire(self, *pts):
        for a, b in zip(pts, pts[1:]):
            if a != b:
                self.wires.append((tuple(map(lambda v: round(v, 2), a)), tuple(map(lambda v: round(v, 2), b))))

    def rail(self, y, xs, gaps=()):
        """Horizontal rail through the sorted points xs; no wire inside the (xa, xb) gaps of series parts."""
        xs = sorted(set(round(v, 2) for v in xs))
        for a, b in zip(xs, xs[1:]):
            if not any(ga <= a and b <= gb for ga, gb in gaps):
                self.wire((a, y), (b, y))

    def label(self, t, x, y, rot=0):
        just = "left bottom"
        self.items.append('(label %s (at %s %s %d) (effects (font (size 1.27 1.27)) (justify %s)) (uuid %s))' % (q(t), x, y, rot, just, U()))
        self.nc_pins.append(None)

    def text(self, t, x, y, size=1.27, bold=False, color=None):
        c = " (color %s 1)" % color if color else ""
        self.items.append('(text %s (exclude_from_sim no) (at %s %s 0) (effects (font (size %s %s)%s%s) (justify left bottom)) (uuid %s))' % (
            q(t), x, y, size, size, " (bold yes)" if bold else "", c, U()))

    def outline(self, pts, color):
        p = " ".join("(xy %s %s)" % xy for xy in pts + [pts[0]])
        self.items.append('(polyline (pts %s) (stroke (width 0.3) (type dash) (color %s 1)) (fill (type none)) (uuid %s))' % (p, color, U()))

    def write(self, path, date, rev):
        from collections import Counter
        ends = Counter()
        for a, b in self.wires:
            ends[a] += 1; ends[b] += 1
        pincount = Counter(self.pins)
        body = list(self.items)
        for a, b in self.wires:
            body.append('(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid %s))' % (a[0], a[1], b[0], b[1], U()))
        for p in set(ends) | set(pincount):
            if ends[p] + pincount[p] >= 3 and ends[p] >= 2:
                body.append('(junction (at %s %s) (diameter 0) (color 0 0 0 0) (uuid %s))' % (p[0], p[1], U()))
        for p in set(x for x in self.nc_pins if x):
            if ends[p] == 0 and pincount[p] == 1:
                body.append('(no_connect (at %s %s) (uuid %s))' % (p[0], p[1], U()))
        hdr = '(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid %s) (paper "A3")\n' % q(self.root)
        hdr += '(title_block (title %s) (date %s) (rev %s) (company "Gregor"))\n' % (q(self.title), q(date), q(rev))
        libs = '(lib_symbols\n' + '\n'.join('\t' + dump(s, 1) for s in self.libs.values()) + ')\n'
        tail = '\n(sheet_instances (path "/" (page "1")))\n(embedded_fonts no))\n'
        open(path, "w", encoding="utf8").write(hdr + libs + "\n".join(body) + tail)

# ---------------------------------------------------------------- the circuit, step by step
YL, YN, YPE = 50.8, 55.88, 60.96         # mains rails
Y5, YG = 203.2, 208.28                   # low-voltage rails
YR = 154.94                              # 5 V safety loop rung

def build(v):
    S = Sheet("Printer power safety – %s: %s" % (v["code"], v["title"]))
    has = lambda f: f in v["feats"]

    # --- inlet J1 and its flags
    J1 = S.place("J1", "Connector", "IEC_60320_C14_Receptacle", "C14 inlet" + (" + fuse drawer" if has("fuse") else ""), at=(25.4, 63.5),
                 ref_at=(22.86, 53.34), val_at=(25.4, 73.66))
    S.wire(J1["1"], (36.83, J1["1"][1]), (36.83, YL))
    S.wire(J1["2"], (39.37, J1["2"][1]), (39.37, YN))
    S.wire(J1["3"], (41.91, J1["3"][1]), (41.91, YPE))
    S.place("#FLG01", "power", "PWR_FLAG", "PWR_FLAG", at=(44.45, YL))
    S.place("#FLG02", "power", "PWR_FLAG", "PWR_FLAG", at=(49.53, YN), rot=180)

    Lx, Nx, Lg, Ng = [36.83, 41.91, 44.45], [39.37, 41.91, 49.53], [], []
    S.label("L", 41.91, YL); S.label("N", 41.91, YN); S.label("PE", 46.99, YPE)

    # --- F1 mains fuse
    if has("fuse"):
        S.place("F1", "Device", "Fuse", "T6.3A", at=(50.8, YL), rot=90, ref_at=(50.8, 45.72), val_at=(50.8, 48.26))
        Lg.append((46.99, 54.61)); Lx += [46.99, 54.61]
    # --- switch: SW1 1-pole, Q0 2-pole (service extension C1)
    if has("q0"):
        S.place("Q0", "Switch", "SW_DPST", "2-pole 16 A", anchor=("3", (60.96, YL)), ref_at=(66.04, 45.72), val_at=(66.04, 48.26))
        Ng.append((60.96, 71.12)); Nx += [60.96, 71.12, 73.66, 81.28]
        S.place("#FLG04", "power", "PWR_FLAG", "PWR_FLAG", at=(81.28, YN), rot=180)
        S.label("N_SW", 73.66, YN)
    else:
        S.place("SW1", "Switch", "SW_SPST", "1-pole", at=(66.04, YL), ref_at=(66.04, 45.72), val_at=(66.04, 48.26))
    Lg.append((60.96, 71.12)); Lx += [60.96, 71.12, 73.66, 81.28]
    S.place("#FLG03", "power", "PWR_FLAG", "PWR_FLAG", at=(81.28, YL))
    S.label("L_SW", 73.66, YL)

    # --- K1 / K2 mains relays + 5 V standby PSU
    if has("relays"):
        PS2 = S.place("PS2", "Converter_ACDC", "IRM-10-5", "5 V standby, 2 A", at=(86.36, 86.36), rot=270,
                      ref_at=(71.12, 85.09), val_at=(71.12, 87.63))
        S.wire((PS2["2"][0], YL), PS2["2"]); S.wire((PS2["1"][0], YN), PS2["1"])     # IRM-10: 2 = AC/L, 1 = AC/N
        Lx.append(PS2["2"][0]); Nx.append(PS2["1"][0])
        S.place("K1", "safety", "RELAY_SPLIT", "G2RL-1A-E 5V 16A", at=(106.68, YL), unit=2, ref_at=(106.68, 48.26), hide_val=True)
        S.place("K2", "safety", "RELAY_SPLIT", "G2RL-1A-E 5V 16A", at=(106.68, YN), unit=2, ref_at=(106.68, 58.67), hide_val=True)
        Lg.append((101.6, 111.76)); Ng.append((101.6, 111.76))
        Lx += [101.6, 111.76, 119.38, 127]; Nx += [101.6, 111.76, 119.38, 129.54]
        S.place("#FLG05", "power", "PWR_FLAG", "PWR_FLAG", at=(127, YL))
        S.place("#FLG06", "power", "PWR_FLAG", "PWR_FLAG", at=(129.54, YN), rot=180)
        S.label("L_K", 119.38, YL); S.label("N_K", 119.38, YN)

    # --- PSU 24 V, its FG, Duet VIN
    PS1 = S.place("PS1", "Converter_ACDC", "IRM-60-24", "PSU 24 V", at=(152.4, 86.36), rot=270, ref_at=(137.16, 85.09), val_at=(137.16, 87.63))
    S.wire((PS1["1"][0], YL), PS1["1"]); S.wire((PS1["2"][0], YN), PS1["2"])
    Lx.append(PS1["1"][0]); Nx.append(PS1["2"][0])
    J4 = S.place("J4", "Connector", "Screw_Terminal_01x01", "PSU FG", anchor=("1", (162.56, 76.2)), rot=270, ref_at=(170.18, 80.01), val_at=(170.18, 82.55))
    S.wire((162.56, YPE), J4["1"])
    J2 = S.place("J2", "Connector_Generic", "Conn_01x02", "Duet VIN (1:+ 2:-)", anchor=("1", (PS1["3"][0], 101.6)), rot=270,
                 ref_at=(165.1, 105.41), val_at=(170.18, 107.95))
    S.wire(PS1["3"], J2["1"])
    S.wire(PS1["4"], (PS1["4"][0], 99.06), (J2["2"][0], 99.06), J2["2"])

    # --- SSR, bed thermal cutoff, bed heater
    xL = 210.82
    SSR = S.place("U1", "Relay_SolidState", "S202S02", "SSR 25 A DC-AC", at=(203.2, 86.36), ref_at=(199.39, 74.93), val_at=(199.39, 77.47))
    S.wire((xL, YL), SSR["1"])
    HT = S.place("J3", "Connector", "Screw_Terminal_01x03", "Bed heater 230 V", anchor=("3", (xL, 111.76)), rot=270,
                 ref_at=(226.06, 115.57), val_at=(226.06, 118.11))
    S.text("3: L  2: N  1: PE", 217.17, 123.19, 1.0)
    if has("th"):
        TH =S.place("TH1", "Switch", "SW_SPST_Temperature_NC", "KSD301 130°C", anchor=("2", (xL, 93.98)), rot=90,
                     ref_at=(226.06, 97.79), val_at=(226.06, 100.33))
        S.wire(SSR["2"], TH["2"]); S.wire(TH["1"], HT["3"])
    else:
        S.wire(SSR["2"], HT["3"])
    S.wire((HT["2"][0], YN), HT["2"]); S.wire((HT["1"][0], YPE), HT["1"])
    J5 = S.place("J5", "Connector_Generic", "Conn_01x02", "Duet BED (1:- 2:+)", anchor=("1", (190.5, 96.52)), rot=270,
                 ref_at=(180.34, 101.6), val_at=(176.53, 104.14))
    S.wire(SSR["4"], (190.5, SSR["4"][1]), J5["1"])
    S.wire(SSR["3"], (187.96, SSR["3"][1]), J5["2"])

    # --- mains rails
    S.rail(YL, Lx + [xL], Lg)
    S.rail(YN, Nx + [HT["2"][0]], Ng)
    S.rail(YPE, [41.91, 46.99, 162.56, HT["1"][0]])

    # --- outlines and headers
    S.outline([(27.94, 39.37), (236.22, 39.37), (236.22, 127), (203.2, 127), (203.2, 86.36), (27.94, 86.36)], RED)
    S.text("MAINS 230 V AC – HAZARDOUS", 30.48, 43.18, 1.5, True, RED)
    lv_bottom = 218.44 if has("relays") else 132.08
    xr = 330.2 if has("relays") else 304.8
    S.outline([(27.94, 86.36), (203.2, 86.36), (203.2, 127), (236.22, 127), (236.22, 86.36), (xr, 86.36), (xr, lv_bottom), (27.94, lv_bottom)], BLUE)
    S.text("LOW VOLTAGE 24 V / 5 V DC (SELV)", 30.48, 91.44, 1.5, True, BLUE)
    S.text("isolation barrier: PSU, SSR", 160.02, 90.17, 1.0)

    if has("relays"):
        lv(S, PS2, has)

    # --- title and notes
    S.text("Printer power safety – %s: %s" % (v["code"], v["title"]), 27.94, 30.48, 2.5, True)
    y = lv_bottom + 7.62
    for line in v["notes"]:
        S.text(line, 27.94, y); y += 3.81
    return S

def lv(S, PS2, has):
    """5 V standby harness, safety loop with START self-hold, smoke detector, supervisor."""
    gp, vp = PS2["3"], PS2["4"]                  # IRM-10-5: 3 = -Vo, 4 = +Vo
    if gp[0] > vp[0]:
        gp, vp = vp, gp
    S.wire(vp, (vp[0], Y5)); S.wire(gp, (gp[0], YG))
    x5, xg = [vp[0], 93.98, 99.06], [gp[0], 86.36]
    S.place("#PWR01", "power", "+5V", "+5V", at=(93.98, Y5), val_at=(93.98, 199.39))
    S.place("#PWR02", "power", "GND", "GND", at=(86.36, YG), val_at=(86.36, 213.36))
    nano = has("nano")

    # rung: +5V -> F2 -> STOP -> [SD119 -> K3] -> [START || K4] -> coils -> Q1 -> GND
    S.wire((99.06, Y5), (99.06, YR))
    rx, gaps = [99.06, 102.87, 110.49, 116.84, 127], [(102.87, 110.49), (116.84, 127)]
    S.place("F2", "Device", "Fuse", "0.5A", at=(106.68, YR), rot=90, ref_at=(106.68, 148.59), val_at=(106.68, 151.13))
    S.place("S1", "Switch", "SW_Push_Open", "STOP (NC)", at=(121.92, YR), ref_at=(121.92, 146.05), val_at=(121.92, 148.59))
    if nano:
        S.label("SENSE_STOP", 130.81, YR, 90); rx.append(130.81)
    if has("smoke"):
        SD = S.place("B1", "safety", "SMOKE_DET", "SD119", at=(144.78, YR), ref_at=(144.78, 146.05), val_at=(144.78, 148.59))
        rx += [134.62, 154.94]; gaps.append((134.62, 154.94))
        p12, p0 = SD["1"], SD["2"]
        DC = S.place("U2", "safety", "DCDC_STEPUP", "MT3608 5->12 V", anchor=("3", (129.54, 177.8)), ref_at=(119.38, 170.18), val_at=(119.38, 172.72))
        S.wire(p12, (p12[0], 167.64), (p12[0], 172.72), (p12[0], 177.8), DC["3"])
        S.wire(p0, (p0[0], 167.64), (p0[0], 172.72), (p0[0], YG)); xg.append(p0[0])
        S.wire(DC["1"], (DC["1"][0], Y5)); x5.append(DC["1"][0])
        S.wire(DC["2"], (DC["2"][0], YG)); xg.append(DC["2"][0])
        S.text("12 V", 131.45, 176.53, 1.0)
        S.place("K3", "safety", "RELAY_SPLIT", "G5V-1 12V", at=(167.64, YR), unit=2, ref_at=(167.64, 151.13), hide_val=True)
        S.place("K3", "safety", "RELAY_SPLIT", "G5V-1 12V", anchor=("A1", (p12[0], 167.64)), unit=1, ref_at=(133.35, 166.37), val_at=(129.54, 168.91))
        D3 = S.place("D3", "Device", "D", "1N4148", at=(144.78, 172.72), ref_at=(144.78, 175.26), hide_val=True)
        S.wire((p12[0], 172.72), D3["1"]); S.wire(D3["2"], (p0[0], 172.72))
        rx += [162.56, 172.72]; gaps.append((162.56, 172.72))
        if nano:
            S.label("SENSE_SMOKE", 158.75, YR, 90); rx.append(158.75)
            S.label("SENSE_DET", 175.26, YR, 90); rx.append(175.26)

    # START self-hold: S2 (NO) in parallel with the K4 contact, K4 coil in parallel with K1/K2
    S.place("S2", "Switch", "SW_Push", "START (NO)", at=(182.88, YR), ref_at=(182.88, 146.05), val_at=(182.88, 148.59))
    S.place("K4", "safety", "RELAY_SPLIT", "G5V-1 5V", at=(182.88, 162.56), unit=2, ref_at=(182.88, 166.37), hide_val=True)
    S.wire((177.8, YR), (177.8, 162.56)); S.wire((187.96, YR), (187.96, 162.56))
    rx += [177.8, 187.96]; gaps.append((177.8, 187.96))
    if nano:
        S.label("SENSE_LOOP", 191.77, YR, 90); rx.append(191.77)

    # relay coils (one flyback diode set serves all parallel coils), lamp, low-side MOSFET
    branches = [("K1", 195.58), ("D1", 200.66), ("K2", 210.82), ("D2", 215.9), ("K4", 226.06), ("R4", 236.22)]
    yc = 170.18
    for ref, x in branches:
        if ref.startswith("K"):
            val = "G5V-1 5V" if ref == "K4" else "G2RL-1A-E 5V 16A"
            p = S.place(ref, "safety", "RELAY_SPLIT", val, anchor=("A1", (x, 157.48)), rot=270, unit=1,
                        ref_at=(x, 173.99), hide_val=True)
            S.wire((x, YR), p["A1"]); S.wire(p["A2"], (x, yc))
        elif ref.startswith("D"):
            p = S.place(ref, "Device", "D", "1N4148", anchor=("1", (x, 158.75)), rot=270, ref_at=(x, 173.99), hide_val=True)
            S.wire((x, YR), p["1"]); S.wire(p["2"], (x, yc))
        else:
            r = S.place("R4", "Device", "R", "330", anchor=("1", (x, YR)), ref_at=(x + 2.54, 158.75), hide_val=True)
            h = S.place("H1", "Device", "LED", "LED", anchor=("2", r["2"]), rot=90, ref_at=(x, 173.99), hide_val=True)
            S.wire(h["1"], (x, yc))
    rx += [x for _, x in branches]
    S.rail(YR, rx, gaps)
    xq = 243.84
    Q1 = S.place("Q1", "Device", "Q_NMOS", "AO3400", anchor=("D", (xq, yc)), mirror=True, ref_at=(255.27, 165.1), val_at=(255.27, 167.64))
    S.rail(yc, [x for _, x in branches] + [xq])
    S.wire(Q1["S"], (Q1["S"][0], YG)); xg.append(Q1["S"][0])
    R1 = S.place("R1", "Device", "R", "100", anchor=("1", Q1["G"]), rot=90, ref_at=(255.27, 179.07), hide_val=True)
    R2 = S.place("R2", "Device", "R", "10k", anchor=("1", (264.16, 175.26)), ref_at=(261.62, 180.34), hide_val=True)
    S.wire(R1["2"], (264.16, 175.26)); S.wire(R2["2"], (264.16, YG)); xg.append(264.16)
    S.wire((264.16, 175.26), (264.16, 170.18), (269.24, 170.18))

    # Duet expansion header: PS_ON, HB, 5V_EXT, GND
    J6 = S.place("J6", "Connector_Generic", "Conn_01x04", "Duet exp.", anchor=("1", (317.5, 187.96)),
                 ref_at=(320.04, 182.88), val_at=(320.04, 185.42))
    for t, n in (("PS_ON", "1"), ("HB", "2"), ("5V_EXT", "3"), ("GND", "4")):
        S.text(t, 323.85, J6[n][1] + 0.5, 1.0)
    S.wire(J6["1"], (309.88, J6["1"][1])); S.label("PS_ON", 309.88, J6["1"][1])
    if nano:
        S.wire(J6["2"], (309.88, J6["2"][1])); S.label("HB", 309.88, J6["2"][1])
    S.wire(J6["3"], (312.42, J6["3"][1]), (312.42, Y5)); x5.append(312.42)
    S.wire(J6["4"], (314.96, J6["4"][1]), (314.96, YG)); xg.append(314.96)

    if nano:
        A = S.place("A1", "MCU_Module", "Arduino_Nano_v3.x", "Arduino Nano (supervisor)", at=(281.94, 162.56),
                    ref_at=(269.24, 132.08), val_at=(269.24, 134.62))
        D4 = S.place("D4", "Device", "D", "1N5819", anchor=("1", A["27"]), rot=90, ref_at=(292.1, 133.35), val_at=(295.91, 135.89))
        S.place("#PWR03", "power", "+5V", "+5V", at=D4["2"], val_at=(D4["2"][0], 125.73))
        for g in ("4", "29"):
            S.wire(A[g], (A[g][0], YG)); xg.append(A[g][0])
        S.wire(A["19"], (299.72, A["19"][1])); S.label("PS_ON", 299.72, A["19"][1])
        S.wire(A["20"], (299.72, A["20"][1])); S.label("HB", 299.72, A["20"][1])
        sense = [("21", "SENSE_STOP", "R5"), ("23", "SENSE_SMOKE", "R6"), ("25", "SENSE_DET", "R7"), ("26", "SENSE_LOOP", None)]
        for pin, name, rref in sense:
            y = A[pin][1]
            if rref:                             # node floats when the part before it opens -> pull-down
                S.wire(A[pin], (297.18, y), (314.96, y)); S.label(name, 297.18, y)
                r = S.place(rref, "Device", "R", "10k", anchor=("1", (314.96, y)), rot=90, ref_at=(318.77, y - 1.27), hide_val=True)
                S.place("#PWR1" + rref[1], "power", "GND", "GND", at=(325.12, y), rot=90, hide_val=True)
                S.wire(r["2"], (325.12, y))
            else:                                # coil node: pulled down by the relay coils
                S.wire(A[pin], (297.18, y)); S.label(name, 297.18, y)
    else:
        S.label("PS_ON", 269.24, 170.18)

    S.rail(Y5, x5); S.rail(YG, xg)
    S.text("+5V standby", 30.48, Y5 + 0.5, 1.0); S.text("GND", 30.48, YG + 0.5, 1.0)
    S.text("5 V safety loop: all series parts closed + START pressed once = K1/K2 on, K4 holds", 99.06, 137.16, 1.0)

# ---------------------------------------------------------------- docs
def stars(n):
    return "★" * n + "☆" * (5 - n) if n else "–"

def in_variant(p, v):
    feats = v["feats"] | {"base"}
    return p["feat"] in feats and p.get("unless") not in feats

def bom_table(v):
    rows = ["| Ref | Part | Added | Protection | Opinion |", "|---|---|---|---|---|"]
    for p in PARTS:
        if in_variant(p, v):
            rows.append("| %s | %s | %s | %s | %s |" % (p["ref"], p["part"], FEAT_CODE[p["feat"]], stars(p["stars"]), p["opinion"]))
    return "\n".join(rows)

HIERARCHY = """```
A0 baseline ── A1 TH1 ── A2 F1 ── A3 K1/K2 + STOP + START ── A4 smoke + K3   CORE: against the worst
                                                               │
                                                               ├── B1 Nano supervisor      diagnostics
                                                               ├── C1 2-pole switch Q0     service
                                                               └── FULL = A4 + B1 + C1
```

| Fault (worst first) | Consequence | Covered by |
|---|---|---|
| SSR fails shorted | bed heats without end → fire | A1 TH1 (hardware), A3 K1/K2 (via Duet), B1 (hung Duet) |
| Fire from any other cause (PSU, wiring, hot end) | fire spreads | A4 smoke detector + K3 |
| Short circuit inside the printer | thin wires burn | A2 F1 |
| Emergency / operator sees a problem | – | A3 STOP |
| Power returns by itself after a fault (smoke clears, loose contact) | heaters restart unattended | A3 START self-hold |
| Detector unpowered | detector silently useless | A4 K3 |
| Duet hangs with heaters on | runaway not cut automatically | B1 watchdog |
| Why did it switch off? | guessing | B1 sense lines |
| Reversed Schuko plug + 1-pole switch | live parts when 'off' (service) | C1 Q0 |
"""

def write_docs(files):
    md = ["# Printer power safety – variants", "",
          "**A – core:** the simplest hardware that protects against the worst faults; A0 → A4, each builds on the previous one."
          " **B – diagnostics** and **C – service** are independent extensions of A4. Images: `docs/img/<code>.png`, KiCad: `kicad/steps/`.",
          "", HIERARCHY,
          "Ratings (★ out of 5) say how well a part protects against the fault it is meant for – not how well the whole printer is protected.", ""]
    for v, fn in zip(VARIANTS, files):
        base = {"B": " (extension of A4)", "C": " (extension of A4)"}.get(v["level"], "")
        md += ["## %s – %s%s" % (v["code"], v["title"], base), "", "![%s](img/%s.png)" % (v["code"], v["code"]), "",
               "KiCad: [`%s`](../kicad/steps/%s)" % (fn, fn), ""]
        md += v["why"] + [""]
        md += ["**Rating:** %s – %s" % (stars(v["stars"]), v["rating"]), "", "**BOM of %s**" % v["code"], "", bom_table(v), ""]
    open(os.path.join(ROOT_DIR, "docs", "steps.md"), "w", encoding="utf8").write("\n".join(md))
    core = next(v for v in VARIANTS if v["code"] == "A4")
    bom = ["# BOM", "", "## Core (A4)", "", bom_table(core), "", "## Full circuit (A4 + B1 + C1)", "", bom_table(VARIANTS[-1]), ""]
    open(os.path.join(ROOT_DIR, "docs", "bom.md"), "w", encoding="utf8").write("\n".join(bom))

def main():
    kdir = os.path.join(ROOT_DIR, "kicad")
    open(os.path.join(kdir, "safety.kicad_sym"), "w", encoding="utf8").write(SAFETY_LIB)
    open(os.path.join(kdir, "sym-lib-table"), "w", encoding="utf8").write(
        '(sym_lib_table (version 7)\n  (lib (name "safety") (type "KiCad") (uri "${KIPRJMOD}/safety.kicad_sym") (options "") (descr "Printer power safety symbols")))\n')
    files = []
    for v in VARIANTS:
        fn = "%s_%s.kicad_sch" % (v["code"], v["slug"])
        build(v).write(os.path.join(kdir, "steps", fn), "261104", v["code"])
        files.append(fn)
    build(VARIANTS[-1]).write(os.path.join(kdir, PROJECT + ".kicad_sch"), "261104", "FULL")
    pro = '{"meta": {"filename": "%s.kicad_pro", "version": 3}}\n'
    open(os.path.join(kdir, PROJECT + ".kicad_pro"), "w").write(pro % PROJECT)
    for fn in files:                             # each variant opens as its own small project
        open(os.path.join(kdir, "steps", fn.replace(".kicad_sch", ".kicad_pro")), "w").write(pro % fn[:-10])
    open(os.path.join(kdir, "steps", "sym-lib-table"), "w", encoding="utf8").write(
        '(sym_lib_table (version 7)\n  (lib (name "safety") (type "KiCad") (uri "${KIPRJMOD}/../safety.kicad_sym") (options "") (descr "Printer power safety symbols")))\n')
    write_docs(files)
    print("PODSUMOWANIE: %d variants written to %s" % (len(VARIANTS), kdir))

if __name__ == "__main__":
    main()
