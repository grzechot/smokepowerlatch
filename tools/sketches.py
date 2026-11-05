"""Stage sketches as standalone SVG (docs/sketches/*.svg), readable on GitHub.

Usage:  python tools/sketches.py
Layout rules: mains 230 V at the bottom, L/N/PE rails left to right, low voltage above; straight lines,
signals and DC lines run vertically to Duet; wire colours as bought (L brown, N blue, PE green-yellow,
0 V black, 5 V red, 12 V yellow, 24 V orange, signals purple).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "sketches")

L, N, PE = "#993C1D", "#378ADD", "#639922"
V0, V5, V12, V24, SIG, MECH = "#2C2C2A", "#E24B4A", "#EF9F27", "#D85A30", "#7F77DD", "#5F5E5A"

STYLE = """<style>
text{font-family:Arial,Helvetica,sans-serif;fill:#2C2C2A}
.ts{font-size:12px}.th{font-size:14px;font-weight:bold}
.coral>rect{fill:#FAECE7;stroke:#993C1D}.coral>text{fill:#712B13}
.gray>rect{fill:#F1EFE8;stroke:#5F5E5A}.gray>text{fill:#444441}
.teal>rect{fill:#E1F5EE;stroke:#0F6E56}.teal>text{fill:#085041}
.purple>rect{fill:#EEEDFE;stroke:#534AB7}.purple>text{fill:#3C3489}
.pink>rect{fill:#FBEAF0;stroke:#993556}.pink>text{fill:#72243E}
.blue>rect{fill:#E6F1FB;stroke:#185FA5}.blue>text{fill:#0C447C}
.amber>rect{fill:#FAEEDA;stroke:#854F0B}.amber>text{fill:#633806}
.red>rect{fill:#FCEBEB;stroke:#A32D2D}.red>text{fill:#791F1F}
.green>rect{fill:#EAF3DE;stroke:#3B6D11}.green>text{fill:#27500A}
.haz{fill:#A32D2D;font-size:14px;font-weight:bold}
</style>"""


class Svg:
    def __init__(self, h, title):
        self.h, self.title, self.items = h, title, []

    def p(self, d, color, w=2, dash=None):
        da = ' stroke-dasharray="%s"' % dash if dash else ""
        self.items.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s"%s stroke-linejoin="round"/>' % (d, color, w, da))

    def dot(self, x, y, color, r=3):
        self.items.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (x, y, r, color))

    def ring(self, x, y, color):
        self.items.append('<circle cx="%s" cy="%s" r="6" fill="none" stroke="%s" stroke-width="1.5"/>' % (x, y, color))
        self.dot(x, y, color, 2.5)

    def t(self, x, y, s, cls="ts", anchor=None):
        a = ' text-anchor="%s"' % anchor if anchor else ""
        self.items.append('<text class="%s" x="%s" y="%s"%s>%s</text>' % (cls, x, y, a, s))

    def box(self, x, y, w, h, color, label, sub=None, big=True):
        cx = x + w / 2
        if sub:
            body = ('<text class="%s" x="%s" y="%s" text-anchor="middle" dominant-baseline="central">%s</text>'
                    '<text class="ts" x="%s" y="%s" text-anchor="middle" dominant-baseline="central">%s</text>') % (
                "th" if big else "ts", cx, y + h / 2 - 8, label, cx, y + h / 2 + 9, sub)
        else:
            body = '<text class="%s" x="%s" y="%s" text-anchor="middle" dominant-baseline="central">%s</text>' % (
                "th" if big else "ts", cx, y + h / 2, label)
        self.items.append('<g class="%s"><rect x="%s" y="%s" width="%s" height="%s" rx="4" stroke-width="0.6"/>%s</g>' % (
            color, x, y, w, h, body))

    def zone(self, x, y, w, h, color):
        self.items.append('<rect x="%s" y="%s" width="%s" height="%s" fill="none" stroke="%s" stroke-dasharray="6 4"/>' % (x, y, w, h, color))

    def frame(self, x, y, w, h):
        self.items.append('<rect x="%s" y="%s" width="%s" height="%s" fill="none" stroke="%s" stroke-width="0.6" stroke-dasharray="3 3"/>' % (x, y, w, h, MECH))

    def band(self, x, y, w, h):
        self.items.append('<rect x="%s" y="%s" width="%s" height="%s" rx="6" fill="#888780" opacity="0.18"/>' % (x, y, w, h))

    def write(self, name):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 %d" width="1020" height="%d" role="img">'
               '<title>%s</title>%s<rect width="680" height="%d" fill="#ffffff"/>\n%s\n</svg>\n') % (
            self.h, self.h * 1.5, self.title, STYLE, self.h, "\n".join(self.items))
        open(os.path.join(OUT, name + ".svg"), "w", encoding="utf8").write(svg)


# ---------------------------------------------------------------- shared pieces
def contact(s, x1, x2, y, color):
    """Horizontal NO contact between x1 and x2 (open blade)."""
    s.dot(x1, y, color, 2); s.dot(x2, y, color, 2)
    s.p("M%s %s L%s %s" % (x1, y, x2 - 2, y - 9), color, 2)


def heater(s, x, y1, y2):
    s.p("M%s %s V%s l5 2 l-10 3 l10 3 l-10 3 l10 3 l-10 3 l5 2 V%s" % (x, y1, y1 + 4, y2), L, 2)


def legend(s, y):
    s.t(40, y, "L brown, N blue, PE green-yellow &#183; 0 V black, 5 V red, 12 V yellow, 24 V orange, signals purple")


# ---------------------------------------------------------------- A0..A2 (one 24 V PSU)
def basic(code, name, th, fuse):
    s = Svg(380, "%s %s" % (code, name))
    s.zone(40, 40, 520, 180, N); s.zone(40, 230, 520, 110, V5)
    s.t(50, 60, "Low voltage 24 V"); s.t(85, 334, "Mains 230 V &#8211; hazardous", "haz"); s.t(6, 352, "Wall")
    s.box(595, 235, 75, 100, "amber", ""); s.t(632, 328, "Bed", "th", "middle")
    sw, x1 = (125, 170) if fuse else (100, 160)
    lr = "M75 260 H85 M115 260 H%d" % sw if fuse else "M75 260 H%d" % sw
    lr += " M%d 260 H%d M%d 260 H400 M470 260 H545" % (sw + 35 if fuse else 140, x1, x1 + 35)
    lr += " M575 260 H603 M643 260 H655" if th else " M575 260 H655"
    s.p(lr, L)
    if fuse:
        s.items.append('<rect x="85" y="254" width="30" height="12" rx="1" fill="none" stroke="%s" stroke-width="1.5"/>' % L)
        s.t(92, 246, "F1")
    s.p("M75 285 H%d M%d 285 H545 M575 285 H655" % (x1, x1 + 35), N)
    s.p("M75 310 H612", PE); s.dot(612, 310, PE)
    heater(s, 655, 260, 285); s.t(606, 301, "heater")
    s.p("M280 235 V260", L); s.p("M310 235 V285", N); s.p("M340 235 V310", PE)
    s.dot(280, 260, L); s.dot(310, 285, N); s.ring(340, 310, PE); s.t(352, 330, "PE stud")
    lx = x1 + 43
    s.t(lx, 255, "L"); s.t(lx, 280, "N"); s.t(lx, 305, "PE")
    s.p("M300 175 V115", V24); s.p("M310 175 V115", V0)
    s.p("M430 215 V115 M437 215 V115", SIG, 1)
    s.t(443, 150, "BED")
    s.box(25, 245, 50, 80, "coral", "C14")
    s.box(sw, 248, 35 if fuse else 40, 24, "coral", "SW1", big=False)
    s.box(x1, 245, 35, 52, "coral", "X1")
    s.box(250, 175, 120, 60, "gray", "PS1 24 V"); s.box(400, 215, 70, 60, "gray", "SSR")
    s.box(260, 60, 260, 55, "blue", "Duet 2 WiFi")
    s.box(545, 248, 30, 49, "coral", "")
    if th:
        s.box(603, 249, 40, 22, "red", "TH1", big=False)
    s.t(380, 365, "Bed connector: L, N only")
    return s


# ---------------------------------------------------------------- A3 24+Relay (230 V START near the front)
def relay230():
    s = Svg(400, "A3 24+Relay")
    s.zone(40, 40, 535, 180, N); s.zone(40, 230, 535, 130, V5)
    s.t(50, 60, "Low voltage 24 V"); s.t(85, 354, "Mains 230 V &#8211; hazardous", "haz"); s.t(6, 372, "Wall")
    s.box(605, 235, 67, 120, "amber", ""); s.t(638, 348, "Bed", "th", "middle")
    s.p("M75 260 H85 M115 260 H125 M160 260 H170 M205 260 H410 M480 260 H560 M590 260 H612 M646 260 H660", L)
    s.items.append('<rect x="85" y="254" width="30" height="12" rx="1" fill="none" stroke="%s" stroke-width="1.5"/>' % L)
    s.t(92, 246, "F1")
    s.p("M75 285 H170 M205 285 H228 M252 285 H560 M590 285 H660", N)
    contact(s, 228, 252, 285, N)
    s.p("M220 285 V305 H230 M250 305 H260 V285", N, 1.5)
    s.dot(220, 285, N); s.dot(260, 285, N); s.dot(230, 305, N, 2); s.dot(250, 305, N, 2)
    s.p("M228 299 H252 M240 299 V292 M235 292 H245", MECH, 1.5); s.t(266, 310, "S1 START")
    s.p("M240 240 V278", MECH, 1, "3 3")
    s.p("M75 330 H620", PE); s.dot(620, 330, PE)
    heater(s, 660, 260, 285); s.t(612, 316, "heater")
    s.p("M300 235 V260", L); s.p("M330 235 V285", N); s.p("M360 235 V330", PE)
    s.dot(300, 260, L); s.dot(330, 285, N); s.ring(360, 330, PE); s.t(372, 350, "PE stud")
    s.t(208, 255, "L"); s.t(208, 280, "N"); s.t(208, 325, "PE")
    s.p("M325 175 V115", V24); s.p("M335 175 V115", V0); s.p("M440 215 V115 M447 215 V115", SIG, 1)
    s.t(453, 150, "BED")
    s.p("M222 212 H202", V24, 1.5); s.t(198, 216, "+24V", anchor="end")
    s.p("M240 200 V186", SIG, 1); s.t(240, 181, "PS_ON", anchor="middle")
    s.p("M260 95 H242", SIG, 1); s.t(238, 99, "PS_ON", anchor="end")
    s.box(25, 245, 50, 80, "coral", "C14"); s.box(125, 248, 35, 24, "coral", "SW1", big=False)
    s.box(170, 245, 35, 52, "coral", "X1"); s.box(222, 200, 36, 40, "purple", "K1")
    s.box(270, 175, 120, 60, "gray", "PS1 24 V"); s.box(410, 215, 70, 60, "gray", "SSR")
    s.box(260, 60, 260, 55, "blue", "Duet 2 WiFi"); s.box(560, 248, 30, 49, "coral", "")
    s.box(612, 249, 34, 22, "red", "TH1", big=False)
    s.t(40, 392, "Hold S1 until Duet runs M80; M81 = everything off"); s.t(400, 392, "Bed connector: L, N only")
    return s


# ---------------------------------------------------------------- A4 24/5 (5 V standby)
def standby():
    s = Svg(380, "A4 24/5")
    s.zone(40, 40, 535, 180, N); s.zone(40, 230, 535, 110, V5)
    s.t(50, 60, "Low voltage 5 V / 24 V"); s.t(85, 334, "Mains 230 V &#8211; hazardous", "haz"); s.t(6, 352, "Wall")
    s.box(605, 235, 67, 100, "amber", ""); s.t(638, 328, "Bed", "th", "middle")
    s.p("M222 175 V125", V0, 3); s.p("M236 175 V125", V5, 3)
    s.p("M236 150 H340 V190", V5); s.dot(236, 150, V5, 3.5); s.t(250, 170, "5 V standby")
    s.p("M356 190 V125", SIG, 1)
    s.p("M410 175 V125", V0); s.p("M420 175 V125", V24)
    s.p("M505 215 V125 M512 215 V125", SIG, 1)
    s.p("M75 260 H85 M115 260 H125 M160 260 H170 M205 260 H490 M540 260 H560 M590 260 H612 M646 260 H660", L)
    s.items.append('<rect x="85" y="254" width="30" height="12" rx="1" fill="none" stroke="%s" stroke-width="1.5"/>' % L)
    s.t(92, 246, "F1")
    s.p("M75 285 H170 M205 285 H336 M360 285 H560 M590 285 H660", N); contact(s, 336, 360, 285, N)
    s.p("M348 240 V279", MECH, 1, "3 3")
    s.p("M75 310 H620", PE); s.dot(620, 310, PE)
    heater(s, 660, 260, 285); s.t(612, 301, "heater")
    s.p("M222 235 V260", L); s.p("M236 235 V285", N); s.dot(222, 260, L); s.dot(236, 285, N)
    s.p("M400 235 V260", L); s.p("M425 235 V285", N); s.p("M450 235 V310", PE)
    s.dot(400, 260, L); s.dot(425, 285, N); s.ring(450, 310, PE); s.t(462, 330, "PE stud")
    s.t(207, 255, "L"); s.t(207, 280, "N"); s.t(207, 305, "PE")
    s.box(25, 245, 50, 80, "coral", "C14"); s.box(125, 248, 35, 24, "coral", "SW1", big=False)
    s.box(170, 245, 35, 52, "coral", "X1"); s.box(212, 175, 34, 60, "teal", "PS2", "5 V", big=False)
    s.box(330, 190, 36, 50, "purple", "K1"); s.box(380, 175, 90, 60, "gray", "PS1 24 V")
    s.box(490, 215, 50, 60, "gray", "SSR")
    s.box(200, 70, 360, 55, "blue", "Duet 2 WiFi")
    for x, t in ((204, "GND"), (240, "5V_EXT"), (338, "PS_ON"), (390, "GND"), (424, "VIN"), (494, "BED")):
        s.t(x, 116, t)
    s.box(560, 248, 30, 49, "coral", ""); s.box(612, 249, 34, 22, "red", "TH1", big=False)
    s.t(40, 372, "M80: K1 on, PS1 + SSR live; M81: off, Duet stays on 5 V"); s.t(420, 372, "Bed connector: L, N only")
    return s


# ---------------------------------------------------------------- detector module (used in A5, A6)
def module_at(s):
    """Detector module x 250..400, y 58..196; bundle leaves at the bottom: 5 V x262, 0 V x272, OK x282."""
    s.frame(250, 62, 150, 134); s.t(292, 207, "module, high")
    s.p("M262 196 V70 H372 V112", V5, 1.5); s.p("M300 70 V74", V5, 1.5); s.dot(300, 70, V5, 2.5)
    s.p("M272 196 V100 H285 V90 M272 116 H285 M272 148 H290", V0, 1.5)
    s.dot(272, 116, V0, 2.5); s.dot(272, 148, V0, 2.5)
    s.p("M345 90 V148 M330 116 H345 M325 148 H345", V12, 1.5); s.dot(345, 116, V12, 2.5)
    s.dot(372, 112, V5, 2); s.dot(372, 136, V5, 2)
    s.p("M372 112 L379 137 M372 136 H380", V5, 1.5)
    s.p("M372 136 V146", V5, 1.5)
    s.dot(372, 146, V5, 2); s.dot(372, 170, V5, 2); s.p("M372 146 L380 168", V5, 1.5)
    s.p("M372 170 V182 H282 V196", V5, 1.5, "6 2")
    s.p("M330 126 H369 M325 158 H369", MECH, 1, "3 3")
    s.t(380, 128, "NC"); s.t(380, 162, "K3")
    s.box(280, 74, 70, 16, "teal", "U2 5&#8594;12 V", big=False)
    s.box(285, 108, 45, 26, "pink", "SD119", big=False)
    s.box(290, 140, 35, 22, "purple", "K3", big=False)


def smoke(code, name, nano):
    s = Svg(470, "%s %s" % (code, name))
    s.zone(40, 10, 535, 290, N); s.zone(40, 310, 535, 110, V5)
    s.t(50, 30, "Low voltage 5 / 12 / 24 V"); s.t(85, 414, "Mains 230 V &#8211; hazardous", "haz"); s.t(6, 432, "Wall")
    s.box(605, 315, 67, 100, "amber", ""); s.t(638, 408, "Bed", "th", "middle")
    module_at(s)
    s.band(256, 202, 32, 26); s.t(292, 222, "bundle")
    s.p("M222 255 V48", V0, 3); s.p("M236 255 V48", V5, 3)
    s.p("M262 196 V232 H236", V5); s.dot(236, 232, V5)
    s.p("M272 196 V262 H246", V0)
    s.p("M282 196 V275", V5, 2, "6 2")
    s.t(286, 252, "OK")
    if nano:
        s.p("M330 295 H340", V5, 1.5)
        s.box(340, 285, 22, 20, "gray", "Q1", big=False)
        s.p("M362 295 H372 V240 H456", V0, 1.5); s.dot(456, 240, V0)
        s.p("M351 285 V272", SIG, 1); s.t(351, 268, "GATE", anchor="middle")
        s.p("M282 258 H292", SIG, 1); s.dot(282, 258, SIG, 2)
        s.p("M410 48 V58 M432 48 V58", SIG, 1)
        s.t(410, 70, "HB", anchor="middle"); s.t(432, 82, "PS_ON", anchor="middle")
        s.box(50, 80, 100, 135, "green", "Nano", "supervisor")
        s.p("M150 205 H222", V0, 1.5); s.dot(222, 205, V0)
        for y, t in ((95, "+5V"), (115, "PS_ON"), (135, "HB"), (155, "OK"), (175, "GATE")):
            s.p("M150 %d H160" % y, SIG, 1); s.t(163, y + 4, t)
    else:
        s.p("M330 295 H410 V48", SIG, 1)
    s.p("M456 255 V48", V0); s.p("M466 255 V48", V24)
    s.p("M526 295 V48 M533 295 V48", SIG, 1)
    s.p("M75 340 H85 M115 340 H125 M160 340 H170 M205 340 H510 M548 340 H560 M590 340 H612 M646 340 H660", L)
    s.items.append('<rect x="85" y="334" width="30" height="12" rx="1" fill="none" stroke="%s" stroke-width="1.5"/>' % L)
    s.t(92, 326, "F1")
    s.p("M75 365 H170 M205 365 H291 M315 365 H560 M590 365 H660", N); contact(s, 291, 315, 365, N)
    s.p("M303 315 V359", MECH, 1, "3 3")
    s.p("M75 390 H620", PE); s.dot(620, 390, PE)
    heater(s, 660, 340, 365); s.t(612, 381, "heater")
    s.p("M222 315 V340", L); s.p("M236 315 V365", N); s.dot(222, 340, L); s.dot(236, 365, N)
    s.p("M445 315 V340", L); s.p("M462 315 V365", N); s.p("M480 315 V390", PE)
    s.dot(445, 340, L); s.dot(462, 365, N); s.ring(480, 390, PE); s.t(492, 410, "PE stud")
    s.t(207, 335, "L"); s.t(207, 360, "N"); s.t(207, 385, "PE")
    s.box(25, 325, 50, 80, "coral", "C14"); s.box(125, 328, 35, 24, "coral", "SW1", big=False)
    s.box(170, 325, 35, 52, "coral", "X1"); s.box(212, 255, 34, 60, "teal", "PS2", "5 V", big=False)
    s.box(276, 275, 54, 40, "purple", "K1"); s.box(430, 255, 65, 60, "gray", "PS1", "24 V")
    s.box(510, 295, 38, 60, "gray", "SSR", big=False)
    s.box(200, 14, 360, 34, "blue", ""); s.t(290, 30, "Duet 2 WiFi", "th")
    pins =[(204, "GND"), (240, "5V_EXT"), (436, "GND"), (470, "VIN"), (512, "BED")]
    if not nano:
        pins.append((376, "PS_ON"))
    for x, t in pins:
        s.t(x, 43, t)
    s.box(560, 328, 30, 49, "coral", ""); s.box(612, 329, 34, 22, "red", "TH1", big=False)
    s.t(40, 446, "Bundle to the detector: 5 V, 0 V, OK. OK = 5 V back only if the detector is powered and sees no smoke")
    legend(s, 462)
    return s


def module_detail():
    s = Svg(400, "Detector module")
    s.frame(140, 40, 360, 270); s.t(140, 32, "Detector module (high, ceiling)")
    s.p("M180 345 V60 H440 V150", V5); s.p("M260 60 V70", V5, 1.5); s.dot(260, 60, V5)
    s.p("M220 345 V110 H250 V95", V0); s.p("M220 155 H240 M220 215 H250", V0, 1.5)
    s.dot(220, 155, V0, 2.5); s.dot(220, 215, V0, 2.5)
    s.p("M330 95 V215 M310 155 H330 M300 215 H330", V12); s.dot(330, 155, V12, 2.5); s.t(336, 128, "+12 V")
    s.dot(440, 150, V5, 2.5); s.dot(440, 180, V5, 2.5); s.p("M440 150 L448 181 M440 180 H450", V5, 1.5)
    s.p("M440 180 V210", V5)
    s.dot(440, 210, V5, 2.5); s.dot(440, 240, V5, 2.5); s.p("M440 210 L450 238", V5, 1.5)
    s.p("M440 240 V280 H260 V345", V5, 1.5, "6 2")
    s.p("M310 168 H436 M300 228 H436", MECH, 1, "3 3")
    s.t(456, 169, "NC (SD119 relay)"); s.t(456, 229, "K3 NO"); s.t(350, 274, "OK")
    s.box(240, 70, 100, 25, "teal", "U2 5&#8594;12 V", big=False)
    s.box(240, 140, 70, 35, "pink", "SD119"); s.box(250, 200, 50, 35, "purple", "K3 12 V", big=False)
    s.band(170, 318, 100, 32)
    s.t(173, 370, "5 V"); s.t(212, 370, "0 V"); s.t(250, 370, "OK")
    s.t(285, 338, "3-wire bundle to PS2 / K1")
    s.t(40, 392, "12 V stays inside the module; the contacts are fed from 5 V, so OK never carries 12 V")
    return s


def main():
    os.makedirs(OUT, exist_ok=True)
    sheets = {
        "A0_firestarter": basic("A0", "Firestarter", False, False),
        "A1_24_thermalcut": basic("A1", "24+ThermalCut", True, False),
        "A2_24_thermalcut_fuse": basic("A2", "24+ThermalCut+Fuse", True, True),
        "A3_24_relay": relay230(),
        "A4_24-5": standby(),
        "A5_24-5_smoke": smoke("A5", "24/5+Smoke", False),
        "A6_24-5_smoke_nano": smoke("A6", "24/5+Smoke+Nano", True),
        "detector_module": module_detail(),
    }
    for name, s in sheets.items():
        s.write(name)
    print("PODSUMOWANIE: %d sketches in %s" % (len(sheets), OUT))


if __name__ == "__main__":
    main()
