"""Generate the printer power-safety schematics, stage by stage (KiCad 10).

Usage:  python tools/gen_power.py            (from the repo root)
Writes kicad/safety.kicad_sym, kicad/steps/<code>_*.kicad_sch, kicad/printer_power_safety.kicad_sch (= A6)
and docs/steps.md + docs/bom.md. Rendering to PNG: tools/render.py. Stages and parts: tools/steps_text.py.

Layout follows the sketches (tools/sketches.py): mains 230 V at the bottom with straight L / N / PE rails, loads
added to the right in wiring order; PSUs, SSR and relay coils straddle the boundary; low voltage above, DC and
signal lines run vertically up to the Duet. The detector module sits high, a 3-wire bundle (5V / 0V / OK) runs
down and splits at PS2. Wire colours as bought: L brown, N blue, PE green-yellow, 0 V black, 5 V red, 12 V yellow,
24 V orange, signals purple.
"""
import os, uuid, copy
from sexp import parse, dump, find, uq
from steps_text import VARIANTS, PARTS, FEAT_CODE

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KLIB = "C:/Program Files/KiCad/10.0/share/kicad/symbols/"
PROJECT = "printer_power_safety"
DATE = "261105"
q = lambda s: '"%s"' % str(s).replace('"', '\\"')
U = lambda: q(uuid.uuid4())
RED, BLUE, GRAY = "200 0 0", "0 0 194", "95 94 90"
L, N, PE = "153 60 29", "55 138 221", "99 153 34"
V0, V5, V12, V24, SIG = "44 44 42", "226 75 74", "239 159 39", "216 90 48", "127 119 221"

# ---------------------------------------------------------------- project symbol library
F127 = '(effects (font (size 1.27 1.27)))'
def _pin(kind, x, y, ang, name, num, length=2.54):
    return '(pin %s line (at %s %s %d) (length %s) (name %s %s) (number %s %s))' % (kind, x, y, ang, length, q(name), F127, q(num), F127)

def _props(ref, val, desc, ry, vy):
    return ('(property "Reference" %s (at 0 %s 0) %s) (property "Value" %s (at 0 %s 0) %s)'
            ' (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))'
            ' (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))'
            ' (property "Description" %s (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))') % (q(ref), ry, F127, q(val), vy, F127, q(desc))

# Duet 2 WiFi: one block with the used terminals at the bottom; pin x = layout x - 165.1 (placed at 165.1, 38.1)
DUET_PINS = [("GND", 96.52), ("5V_EXT", 101.6), ("PS_ON", 180.34), ("HB", 185.42),
             ("VIN-", 193.04), ("VIN+", 198.12), ("BED-", 226.06), ("BED+", 231.14)]
DUET_AT = (165.1, 38.1)

SAFETY_LIB = '''(kicad_symbol_lib (version 20241209) (generator "gen_power")
 (symbol "RELAY_SPLIT" (pin_names (offset 0.254) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  %s
  (symbol "RELAY_SPLIT_1_1"
   (rectangle (start -2.54 -1.524) (end 2.54 1.524) (stroke (width 0.254) (type default)) (fill (type background)))
   %s %s)
  (symbol "RELAY_SPLIT_2_1"
   (polyline (pts (xy -2.54 0) (xy 2.286 1.778)) (stroke (width 0.254) (type default)) (fill (type none)))
   (polyline (pts (xy 2.54 0) (xy 2.54 0.762)) (stroke (width 0.254) (type default)) (fill (type none)))
   %s %s))
 (symbol "SMOKE_DET" (pin_names (offset 0.254) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  %s
  (symbol "SMOKE_DET_0_1"
   (rectangle (start -7.62 -3.81) (end 7.62 3.81) (stroke (width 0.254) (type default)) (fill (type background)))
   (polyline (pts (xy -7.62 0) (xy -2.54 0) (xy 3.302 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
   (polyline (pts (xy 2.54 -1.524) (xy 2.54 0) (xy 7.62 0)) (stroke (width 0.254) (type default)) (fill (type none)))
   (text "+12V" (at -5.08 2.794 0) (effects (font (size 0.889 0.889))))
   (text "0V" (at 5.08 2.794 0) (effects (font (size 0.889 0.889))))
   (text "C" (at -6.35 -1.27 0) (effects (font (size 0.889 0.889))))
   (text "NC" (at 5.715 -1.27 0) (effects (font (size 0.889 0.889)))))
  (symbol "SMOKE_DET_1_1" %s %s %s %s))
 (symbol "DCDC_STEPUP" (pin_names (offset 0.254)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  %s
  (symbol "DCDC_STEPUP_0_1"
   (rectangle (start -7.62 -5.08) (end 7.62 5.08) (stroke (width 0.254) (type default)) (fill (type background))))
  (symbol "DCDC_STEPUP_1_1" %s %s %s %s))
 (symbol "PLUG_2P" (pin_names (offset 0.254) (hide yes)) (pin_numbers (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  %s
  (symbol "PLUG_2P_0_1"
   (rectangle (start -2.54 1.778) (end 2.54 -11.938) (stroke (width 0.254) (type default)) (fill (type background)))
   (polyline (pts (xy -2.54 0) (xy 2.54 0)) (stroke (width 0.254) (type dash)) (fill (type none)))
   (polyline (pts (xy -2.54 -10.16) (xy 2.54 -10.16)) (stroke (width 0.254) (type dash)) (fill (type none))))
  (symbol "PLUG_2P_1_1" %s %s %s %s))
 (symbol "DUET2" (pin_names (offset 0.762)) (pin_numbers (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  %s
  (symbol "DUET2_0_1"
   (rectangle (start -76.2 10.16) (end 73.66 -10.16) (stroke (width 0.254) (type default)) (fill (type background)))
   (text "Duet 2 WiFi" (at 0 2.54 0) (effects (font (size 2.54 2.54) (bold yes)))))
  (symbol "DUET2_1_1" %s)))
''' % (
    _props("K", "RELAY_SPLIT", "Relay drawn as separate units: A = coil, B = NO contact", 3.81, -3.81),
    _pin("passive", -5.08, 0, 0, "A1", "A1"), _pin("passive", 5.08, 0, 180, "A2", "A2"),
    _pin("passive", -5.08, 0, 0, "13", "13"), _pin("passive", 5.08, 0, 180, "14", "14"),
    _props("B", "SMOKE_DET", "Smoke detector, 12 V, relay output C-NC (NC opens on alarm; NC is CLOSED when unpowered)", -6.35, -8.89),
    _pin("passive", -10.16, 0, 0, "C", "3"), _pin("passive", 10.16, 0, 180, "NC", "4"),
    _pin("power_in", -5.08, 6.35, 270, "+12V", "1"), _pin("power_in", 5.08, 6.35, 270, "0V", "2"),
    _props("U", "DCDC_STEPUP", "Non-isolated step-up module; IN- and OUT- are the same copper, connect both", 6.35, -6.35),
    _pin("passive", -10.16, 2.54, 0, "IN-", "2"), _pin("power_in", -10.16, -2.54, 0, "IN+", "1"),
    _pin("passive", 10.16, 2.54, 180, "OUT-", "4"), _pin("power_out", 10.16, -2.54, 180, "OUT+", "3"),
    _props("J", "PLUG_2P", "2-pole plug and socket, mated: 1-3 = L, 2-4 = N", 3.81, -14.605),
    _pin("passive", -5.08, 0, 0, "L", "1"), _pin("passive", -5.08, -10.16, 0, "N", "2"),
    _pin("passive", 5.08, 0, 180, "L", "3"), _pin("passive", 5.08, -10.16, 180, "N", "4"),
    _props("U", "DUET2", "Duet 2 WiFi, only the terminals used here", 12.7, -12.7),
    " ".join(_pin("passive", round(x - DUET_AT[0], 2), -12.7, 90, n, str(i + 1)) for i, (n, x) in enumerate(DUET_PINS)))

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
    px, py = {0: (px, py), 90: (-py, px), 180: (-px, -py), 270: (py, -px)}[rot]
    return (-px if mirror else px), -py          # KiCad rotates, then mirrors; screen y grows downwards

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
        if not power and nc:
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

    def wire(self, *pts, c=None):
        for a, b in zip(pts, pts[1:]):
            if a != b:
                self.wires.append((tuple(round(v, 2) for v in a), tuple(round(v, 2) for v in b), c))

    def rail(self, y, xs, gaps=(), c=None):
        """Horizontal rail through the sorted points xs; no wire inside the (xa, xb) gaps of series parts."""
        xs = sorted(set(round(v, 2) for v in xs))
        for a, b in zip(xs, xs[1:]):
            if not any(ga <= a and b <= gb for ga, gb in gaps):
                self.wire((a, y), (b, y), c=c)

    def vline(self, x, ys, c=None):
        """Vertical line through the points ys (split there, so taps and labels connect)."""
        ys = sorted(set(round(v, 2) for v in ys))
        for a, b in zip(ys, ys[1:]):
            self.wire((x, a), (x, b), c=c)

    def label(self, t, x, y, rot=0):
        self.items.append('(label %s (at %s %s %d) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid %s))' % (q(t), x, y, rot, U()))

    def text(self, t, x, y, size=1.27, bold=False, color=None):
        c = " (color %s 1)" % color if color else ""
        self.items.append('(text %s (exclude_from_sim no) (at %s %s 0) (effects (font (size %s %s)%s%s) (justify left bottom)) (uuid %s))' % (
            q(t), x, y, size, size, " (bold yes)" if bold else "", c, U()))

    def line(self, pts, color, width=0.15, closed=False):
        p = " ".join("(xy %s %s)" % xy for xy in pts + (pts[:1] if closed else []))
        self.items.append('(polyline (pts %s) (stroke (width %s) (type dash) (color %s 1)) (fill (type none)) (uuid %s))' % (p, width, color, U()))

    def box(self, x1, y1, x2, y2, color, width=0.3):
        self.line([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], color, width, True)

    def write(self, path, date, rev):
        from collections import Counter
        ends = Counter()
        for a, b, _ in self.wires:
            ends[a] += 1; ends[b] += 1
        pincount = Counter(self.pins)
        body = list(self.items)
        for a, b, c in self.wires:
            col = "(color %s 1)" % c if c else ""
            body.append('(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)%s) (uuid %s))' % (a[0], a[1], b[0], b[1], col, U()))
        for p in set(ends) | set(pincount):
            if ends[p] + pincount[p] >= 3 and ends[p] >= 2:
                body.append('(junction (at %s %s) (diameter 0) (color 0 0 0 0) (uuid %s))' % (p[0], p[1], U()))
        for p in set(self.nc_pins):
            if ends[p] == 0 and pincount[p] == 1:
                body.append('(no_connect (at %s %s) (uuid %s))' % (p[0], p[1], U()))
        hdr = '(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid %s) (paper "A3")\n' % q(self.root)
        hdr += '(title_block (title %s) (date %s) (rev %s) (company "Gregor"))\n' % (q(self.title), q(date), q(rev))
        libs = '(lib_symbols\n' + '\n'.join('\t' + dump(s, 1) for s in self.libs.values()) + ')\n'
        tail = '\n(sheet_instances (path "/" (page "1")))\n(embedded_fonts no))\n'
        open(path, "w", encoding="utf8").write(hdr + libs + "\n".join(body) + tail)

# ---------------------------------------------------------------- the circuit, stage by stage
YL, YN, YPE = 215.9, 226.06, 238.76      # mains rails
YB = 195.58                              # mains / low-voltage boundary = centre line of PSUs and SSR
YC, YD, YT = 167.64, 162.56, 157.48      # K1 coil, its flyback diode, supply tap
YDU = 50.8                               # Duet terminal row
XO, X5, XK = 96.52, 101.6, 114.3         # PS2 0 V and +5 V lines, K1
XA1, XA2 = 109.22, 119.38                # K1 coil A1 / A2 = K1 contact 13 / 14
XPS, XHB = 180.34, 185.42                # Duet PS_ON, HB
X0P, X24 = 193.04, 198.12                # PS1 0 V and +24 V lines
B0, B5 = 104.14, 106.68                  # bundle: 0 V, 5 V (OK runs on XA1)

def build(v):
    S = Sheet("Printer power safety – %s %s" % (v["code"], v["title"]))
    has = lambda f: f in v["feats"]
    relay, standby, smoke, nano = has("relay"), has("standby"), has("smoke"), has("nano")

    # --- inlet J1; PE leaves at once and bypasses X1
    J1 = S.place("J1", "Connector", "IEC_60320_C14_Receptacle", "C14 inlet" + (" + fuse drawer" if has("fuse") else ""),
                 anchor=("1", (35.56, YL)), ref_at=(20.32, 208.28), val_at=(17.78, 233.68))
    S.wire(J1["3"], (38.1, J1["3"][1]), (38.1, YPE), c=PE)
    S.place("#FLG01", "power", "PWR_FLAG", "PWR_FLAG", at=(43.18, YL))
    S.place("#FLG02", "power", "PWR_FLAG", "PWR_FLAG", at=(43.18, YN), rot=180)
    lx, lg = [35.56, 43.18, 86.36, 91.44], []
    nx, ng = [35.56, 43.18, 86.36], []
    pex = [38.1, 86.36]

    # --- F1, SW1, Wago X1
    if has("fuse"):
        S.place("F1", "Device", "Fuse", "T6.3A", at=(50.8, YL), rot=90, ref_at=(49.53, 210.82), val_at=(47.0, 213.36))
        lx += [46.99, 54.61]; lg.append((46.99, 54.61))
    S.place("SW1", "Switch", "SW_SPST", "1-pole", at=(66.04, YL), ref_at=(63.5, 210.82), val_at=(62.23, 213.36))
    lx += [60.96, 71.12]; lg.append((60.96, 71.12))
    S.place("#FLG03", "power", "PWR_FLAG", "PWR_FLAG", at=(91.44, YL))
    S.box(76.2, YL - 3.81, 83.82, YN + 3.81, GRAY, 0.2); S.text("X1 Wago", 75.57, YL - 4.45, 1.0)
    for t, y in (("L", YL), ("N", YN), ("PE", YPE)):
        S.label(t, 86.36, y)

    # --- PS2 5 V standby, fed before K1
    if standby:
        PS2 = S.place("PS2", "Converter_ACDC", "IRM-10-5", "5 V standby", at=(99.06, YB), rot=90, mirror=True,
                      ref_at=(84.07, 193.04), val_at=(76.2, 199.39))
        assert PS2["2"][0] == X5 and PS2["1"][0] == XO and PS2["3"][0] == XO and PS2["4"][0] == X5
        S.wire(PS2["2"], (X5, YL), c=L); S.wire(PS2["1"], (XO, YN), c=N)
        lx.append(X5); nx.append(XO)

    # --- K1 relay in N: contact on the N rail, coil straight above it
    if relay:
        S.place("K1", "safety", "RELAY_SPLIT", "", at=(XK, YN), unit=2, ref_at=(112.4, 223.52), hide_val=True)
        nx += [XA1, XA2, 124.46]; ng.append((XA1, XA2))
        S.place("#FLG04", "power", "PWR_FLAG", "PWR_FLAG", at=(124.46, YN), rot=180)
        K1 = S.place("K1", "safety", "RELAY_SPLIT", "%s V coil, 16 A" % ("5" if standby else "24"), at=(XK, YC), unit=1,
                     ref_at=(99.0, 172.72), val_at=(88.0, 175.26))
        D1 = S.place("D1", "Device", "D", "1N4148", at=(XK, YD), ref_at=(112.4, 160.02), hide_val=True)
        S.wire(K1["A1"], (XA1, YD), D1["1"]); S.wire(D1["2"], (XA2, YD), K1["A2"])
        S.line([(XK, YC + 1.9), (XK, YN - 2.0)], GRAY)
        if not standby:                          # A3: START at 230 V across the K1 contact, coil from 24 V
            S.place("S1", "Switch", "SW_Push", "START (230 V)", at=(XK, YN + 6.35), ref_at=(122.0, 231.14), val_at=(122.0, 233.68))
            S.wire((XA1, YN), (XA1, YN + 6.35), c=N); S.wire((XA2, YN), (XA2, YN + 6.35), c=N)
            S.wire((XA1, YD), (XA1, YT), c=V24); S.label("24V", XA1, YT)
        if not nano:                             # coil low side switched by Duet PS_ON
            S.wire(K1["A2"], (XPS, YC), (XPS, YDU), c=SIG)

    # --- PS1 24 V, PE stud at its earth, SSR
    PS1 = S.place("PS1", "Converter_ACDC", "IRM-60-24", "PSU 24 V", at=(195.58, YB), rot=90, mirror=True,
                  ref_at=(203.2, 193.04), val_at=(203.2, 199.39))
    assert PS1["1"][0] == X24 and PS1["2"][0] == X0P and PS1["3"][0] == X24 and PS1["4"][0] == X0P
    S.wire(PS1["1"], (X24, YL), c=L); S.wire(PS1["2"], (X0P, YN), c=N)
    lx.append(X24); nx.append(X0P)
    S.vline(X24, [PS1["3"][1], YDU] + ([YT] if relay and not standby else []), c=V24)
    if relay and not standby:
        S.label("24V", X24, YT)
    S.vline(X0P, [PS1["4"][1], YDU] + ([63.5] if standby else []) + ([180.34] if nano else []), c=V0)
    S.place("J4", "Connector", "Screw_Terminal_01x01", "PE stud (PS1 earth)", anchor=("1", (203.2, YPE)), rot=270,
            ref_at=(206.0, 243.84), val_at=(206.0, 246.38))
    pex.append(203.2)
    SSR = S.place("U1", "Relay_SolidState", "S202S02", "SSR 25 A DC-AC", at=(228.6, YB), rot=270, ref_at=(234.95, 193.04), val_at=(234.95, 199.39))
    S.wire(SSR["2"], (SSR["2"][0], YL), c=L); S.wire(SSR["1"], (SSR["1"][0], YL), (248.92, YL), c=L)
    lx.append(SSR["2"][0])
    S.wire(SSR["4"], (SSR["4"][0], YDU), c=SIG); S.wire(SSR["3"], (SSR["3"][0], YDU), c=SIG)

    # --- bed: plug L / N, TH1 and heater on the bed, PE directly to the plate
    S.place("J3", "safety", "PLUG_2P", "Bed plug L / N", at=(254, YL), ref_at=(251.46, 211.84), val_at=(244.0, 233.68))
    nx.append(248.92)
    if has("th"):
        S.place("TH1", "Switch", "SW_SPST_Temperature_NC", "KSD301 130 °C", at=(271.78, YL - 2.54), ref_at=(268.0, 208.28), val_at=(265.0, 210.82))
        S.wire((259.08, YL), (266.7, YL), c=L); S.wire((276.86, YL), (287.02, YL), c=L)
    else:
        S.wire((259.08, YL), (287.02, YL), c=L)
    HT = S.place("HT1", "Device", "Heater", "Bed heater 230 V", at=(287.02, 220.98), ref_at=(290.83, 219.71), val_at=(279.4, 232.41))
    S.wire((287.02, YL), HT["1"], c=L); S.wire(HT["2"], (287.02, YN), (259.08, YN), c=N)
    S.place("J7", "Connector", "Screw_Terminal_01x01", "Bed plate PE", anchor=("1", (287.02, YPE)), ref_at=(290.0, 236.22), val_at=(290.0, 243.84))
    pex.append(287.02)
    S.box(262.89, 204.47, 302.26, 247.65, GRAY, 0.2); S.text("Bed", 264.16, 246.38, 1.5, True)

    S.rail(YL, lx, lg, L); S.rail(YN, nx, ng, N); S.rail(YPE, pex, (), PE)

    # --- Duet
    S.place("U3", "safety", "DUET2", "Duet 2 WiFi", at=DUET_AT, ref_at=(91.44, 26.67), hide_val=True)

    # --- 5 V standby lines from PS2 up to the Duet
    if standby:
        S.vline(XO, [PS2["3"][1], 63.5, YDU] + ([165.1] if smoke else []), c=V0)
        S.vline(X5, [PS2["4"][1], YDU] + ([170.18] if smoke else [YT]) + ([58.42] if nano else []), c=V5)
        S.label("0V", XO, 63.5); S.label("0V", X0P, 63.5)
        if not smoke:                            # A4: K1 coil fed straight from 5 V
            S.wire((X5, YT), (XA1, YT), (XA1, YD), c=V5)
        if nano:
            S.label("5V", X5, 58.42)

    if smoke:
        detector(S, nano)
    if nano:
        supervisor(S, K1)

    # --- zones, title, notes
    S.box(22.86, 20.32, 304.8, YB, BLUE); S.box(22.86, YB, 304.8, 251.46, RED)
    S.text("LOW VOLTAGE 5 / 12 / 24 V DC (SELV)" if standby else "LOW VOLTAGE 24 V DC (SELV)", 25.4, 25.4, 1.5, True, BLUE)
    S.text("MAINS 230 V AC – HAZARDOUS", 25.4, 250.19, 1.5, True, RED)
    S.text("Printer power safety – %s %s" % (v["code"], v["title"]), 22.86, 15.24, 2.5, True)
    y = 259.08
    for line in v["notes"]:
        S.text(line, 22.86, y); y += 3.81
    S.text("Wires: L brown, N blue, PE green-yellow, 0 V black, 5 V red, 12 V yellow, 24 V orange, signals purple."
           " Full description: docs/stages.md", 22.86, y)
    return S

def detector(S, nano):
    """Detector module mounted high; 3-wire bundle 5V / 0V / OK down to PS2 and the K1 coil."""
    S.box(102.87, 58.42, 175.26, 121.92, GRAY, 0.2)
    S.text("Detector module (mounted high)", 114.3, 120.65, 1.27, True)
    # bundle: 0 V and 5 V split at PS2, OK goes straight down to the K1 coil
    S.wire((XO, 165.1), (B0, 165.1), (B0, 66.04), c=V0)
    S.wire((X5, 170.18), (B5, 170.18), c=V5); S.vline(B5, [170.18, 99.06, 71.12], c=V5)
    S.vline(XA1, [116.84, YD] + ([147.32] if nano else []), c=V5)
    S.line([(102.87, 125.73), (111.76, 125.73), (111.76, 154.94), (102.87, 154.94)], GRAY, 0.15, True)
    S.text("W1 bundle", 113.03, 133.35, 1.0); S.text("5V / 0V / OK", 113.03, 135.89, 1.0)
    # U2 5 -> 12 V; IN- and OUT- both connected
    U2 = S.place("U2", "safety", "DCDC_STEPUP", "MT3608 5->12 V", at=(121.92, 68.58), ref_at=(118.0, 62.23), val_at=(115.0, 77.47))
    S.wire((B0, 66.04), U2["2"], c=V0); S.wire((B5, 71.12), U2["1"], c=V5)
    S.wire(U2["4"], (170.18, 66.04), (170.18, 88.9), c=V0); S.rail(88.9, [147.32, 157.48, 162.56, 170.18], c=V0)
    S.wire(U2["3"], (137.16, 71.12), c=V12); S.vline(137.16, [71.12, 78.74, 92.71], c=V12)
    S.rail(78.74, [137.16, 157.48, 162.56], c=V12)
    S.text("12 V", 139.7, 77.47, 1.0); S.label("0V", 170.18, 88.9)
    # SD119 and the K3 coil in parallel across 12 V / 0 V
    SD = S.place("B1", "safety", "SMOKE_DET", "SD119 (NC)", at=(142.24, 99.06), ref_at=(139.0, 106.68), val_at=(136.0, 109.22))
    S.wire((147.32, 88.9), SD["2"], c=V0)
    S.place("K3", "safety", "RELAY_SPLIT", "12 V coil", at=(157.48, 83.82), rot=270, unit=1, ref_at=(150.5, 82.55), val_at=(141.0, 85.09))
    D3 = S.place("D3", "Device", "D", "1N4148", at=(162.56, 83.82), rot=270, ref_at=(164.0, 83.82), hide_val=True)
    S.wire((162.56, 78.74), D3["1"], c=V12); S.wire(D3["2"], (162.56, 88.9), c=V0)
    # chain from 5 V: SD119 C-NC, K3 NO -> OK
    S.wire((B5, 99.06), SD["3"], c=V5)
    S.place("K3", "safety", "RELAY_SPLIT", "", at=(157.48, 99.06), unit=2, ref_at=(155.0, 104.14), hide_val=True)
    S.line([(157.48, 90.3), (157.48, 97.5)], GRAY)
    S.wire((162.56, 99.06), (162.56, 116.84), (XA1, 116.84), c=V5)
    S.text("OK", 150.0, 115.57, 1.0)

def supervisor(S, K1):
    """A6: Nano drives Q1 on the low side of the K1 coil; Duet PS_ON and HB go to the Nano."""
    Q1 = S.place("Q1", "Device", "Q_NMOS", "AO3400", anchor=("D", (127, YC)), mirror=True, ref_at=(131.0, 177.8), val_at=(131.0, 185.42))
    S.wire(K1["A2"], Q1["D"], c=SIG)
    R1 = S.place("R1", "Device", "R", "100", anchor=("1", Q1["G"]), rot=90, ref_at=(137.16, 170.18), hide_val=True)
    R2 = S.place("R2", "Device", "R", "10k", anchor=("1", R1["2"]), ref_at=(143.5, 177.8), val_at=(143.5, 180.0))
    S.wire(R1["2"], (147.32, R1["2"][1]), c=SIG); S.label("GATE", 147.32, R1["2"][1])
    S.wire(Q1["S"], (127, 180.34), R2["2"], (X0P, 180.34), c=V0)
    S.wire((XPS, YDU), (XPS, 60.96), c=SIG); S.label("PS_ON", XPS, 60.96)
    S.wire((XHB, YDU), (XHB, 55.88), c=SIG); S.label("HB", XHB, 55.88)
    S.label("OK", XA1, 147.32)
    A = S.place("A1", "MCU_Module", "Arduino_Nano_v3.x", "Nano supervisor", at=(60.96, 109.22), ref_at=(50.8, 81.28), val_at=(40.64, 78.74))
    for pin, name in (("5", "GATE"), ("6", "PS_ON"), ("7", "HB"), ("8", "OK")):
        y = A[pin][1]
        if name == "OK":
            S.wire(A[pin], (43.18, y), (35.56, y), c=SIG)
            R7 = S.place("R7", "Device", "R", "10k", anchor=("1", (43.18, y)), ref_at=(44.5, 111.76), val_at=(44.5, 114.3))
            S.wire(R7["2"], (43.18, 116.84), c=V0); S.label("0V", 43.18, 116.84)
        else:
            S.wire(A[pin], (35.56, y), c=SIG)
        S.label(name, 35.56, y)
    D4 = S.place("D4", "Device", "D", "1N5819", anchor=("1", A["27"]), rot=90, ref_at=(68.58, 76.2), val_at=(68.58, 78.74))
    S.wire(D4["2"], (D4["2"][0], 73.66), c=V5); S.label("5V", D4["2"][0], 73.66)
    S.wire(A["4"], (A["4"][0], 137.16), (A["29"][0], 137.16), A["29"], c=V0); S.label("0V", A["4"][0], 137.16)

# ---------------------------------------------------------------- docs
def in_variant(p, v):
    feats = v["feats"] | {"base"}
    return p["feat"] in feats and p.get("unless") not in feats

def bom_table(v):
    rows = ["| Ref | Part | Added | Note |", "|---|---|---|---|"]
    for p in PARTS:
        if in_variant(p, v):
            rows.append("| %s | %s | %s | %s |" % (p["ref"], p["part"], FEAT_CODE[p["feat"]], p["opinion"]))
    return "\n".join(rows)

def write_docs(files):
    md = ["# Printer power safety – KiCad schematics and BOM per stage", "",
          "What each stage adds, why, and how well it protects: [stages.md](stages.md). The schematics follow the stage"
          " sketches: mains at the bottom, low voltage above, wire colours as bought. Images: `docs/img/<code>.png`,"
          " KiCad: `kicad/steps/`.", ""]
    for v, fn in zip(VARIANTS, files):
        md += ["## %s – %s" % (v["code"], v["title"]), "", "![%s](img/%s.png)" % (v["code"], v["code"]), "",
               "KiCad: [`%s`](../kicad/steps/%s)" % (fn, fn), ""]
        md += ["- " + n for n in v["notes"]] + ["", "**BOM of %s**" % v["code"], "", bom_table(v), ""]
    open(os.path.join(ROOT_DIR, "docs", "steps.md"), "w", encoding="utf8").write("\n".join(md))
    a5 = next(v for v in VARIANTS if v["code"] == "A5")
    bom = ["# BOM", "", "## A5 24/5+Smoke (hardware protection complete)", "", bom_table(a5), "",
           "## A6 24/5+Smoke+Nano", "", bom_table(VARIANTS[-1]), ""]
    open(os.path.join(ROOT_DIR, "docs", "bom.md"), "w", encoding="utf8").write("\n".join(bom))

def main():
    kdir = os.path.join(ROOT_DIR, "kicad")
    open(os.path.join(kdir, "safety.kicad_sym"), "w", encoding="utf8").write(SAFETY_LIB)
    _libs.pop("safety", None)
    open(os.path.join(kdir, "sym-lib-table"), "w", encoding="utf8").write(
        '(sym_lib_table (version 7)\n  (lib (name "safety") (type "KiCad") (uri "${KIPRJMOD}/safety.kicad_sym") (options "") (descr "Printer power safety symbols")))\n')
    files = []
    for v in VARIANTS:
        fn = "%s_%s.kicad_sch" % (v["code"], v["slug"])
        build(v).write(os.path.join(kdir, "steps", fn), DATE, v["code"])
        files.append(fn)
    build(VARIANTS[-1]).write(os.path.join(kdir, PROJECT + ".kicad_sch"), DATE, VARIANTS[-1]["code"])
    pro = '{"meta": {"filename": "%s.kicad_pro", "version": 3}}\n'
    open(os.path.join(kdir, PROJECT + ".kicad_pro"), "w").write(pro % PROJECT)
    for fn in files:                             # each stage opens as its own small project
        open(os.path.join(kdir, "steps", fn.replace(".kicad_sch", ".kicad_pro")), "w").write(pro % fn[:-10])
    open(os.path.join(kdir, "steps", "sym-lib-table"), "w", encoding="utf8").write(
        '(sym_lib_table (version 7)\n  (lib (name "safety") (type "KiCad") (uri "${KIPRJMOD}/../safety.kicad_sym") (options "") (descr "Printer power safety symbols")))\n')
    write_docs(files)
    print("PODSUMOWANIE: %d stages written to %s" % (len(VARIANTS), kdir))

if __name__ == "__main__":
    main()
