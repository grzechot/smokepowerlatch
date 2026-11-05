# Eksport STEP modulu 230 V (bryly B-rep) - ta sama geometria co modul_230V.scad (v4 261103).
# Zapisuje tez modul_230V.FCStd (bryly Korpus, Pokrywa, Stara_obudowa) do edycji w FreeCAD.
# Uruchomienie: "C:\Program Files\FreeCAD 1.0\bin\freecadcmd.exe" modul_230V_step.py
# Pliki STEP w ukladzie wspolrzednych starej obudowy (PowerSwitch-SSR-Mount.stl).
import os
import FreeCAD as App
import Part, Mesh, Draft
from FreeCAD import Vector as V

OUT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
OLD = "PowerSwitch-SSR-Mount.stl"  # third-party enclosure, NOT included - see README
FONT = "C:/Windows/Fonts/arialbd.ttf"

W, D, H, t = 40.0, 26.0, 140.8, 3.0
Yf = -4.0
POS = V(432.18, 320.15, 8.1)
OLD_OPEN_Y = 316.15
ins_d, ins_h = 4.0, 6.0
win = (20.0, 75.0, 97.0)
screws_old = [(13.85, 4.9), (13.85, H - t - 3.8)]
cable = (16.0, 24.0, 8.0)
podest = (15.0, 8.7)
shelf = (16.0, 97.0, 99.1)
rib = (19.0, 21.0, 16.0)
capT, cap_cl = 2.6, 0.2
slotsZ = [6.85, 46.35, 102.6, 132.55]
slot = (1.6, 5.0)
tab = (2.2, 1.2, 4.5)
lid_x, lid_z = 32.5, [51.4, 94.4]
boss_d, boss_y1 = 9.5, 16.0
tab_y0 = Yf + capT - tab[1]
slot_y0 = tab_y0 - (slot[0] - tab[1]) / 2

doc = App.newDocument("modul")

def box(x, y, z, dx, dy, dz): return Part.makeBox(dx, dy, dz, V(x, y, z))
def cyl(p, d, h, axis): return Part.makeCylinder(d / 2, h, p, axis)
def fuse(shapes):
    s = shapes[0]
    for o in shapes[1:]:
        s = s.fuse(o)
    return s

def poly_face(pts):
    return Part.Face(Part.makePolygon([V(x, y, 0) for x, y in pts] + [V(pts[0][0], pts[0][1], 0)]))

def warn_faces(s=24.0):
    tri = poly_face([(-s / 2, 0), (s / 2, 0), (0, s * 0.866)])
    ring = tri.cut(tri.makeOffset2D(-2.0, join=2))
    bolt = poly_face([(1.5, 9), (-2.5, 1), (0, 1), (-1.5, -4), (2.5, 3), (0, 3)])
    return [ring, moved(bolt, 0, s * 0.33)]

def moved(sh, dx, dy):                     # przesuniecie w geometrii (translate() zmienia tylko Placement,
    m = App.Matrix()                       # ktory mirror() potem gubi/dubluje)
    m.move(V(dx, dy, 0))
    return sh.transformGeometry(m)

def text_faces(txt, size, y):
    ss = Draft.make_shapestring(String=txt, FontFile=FONT, Size=size)
    doc.recompute()
    sh = ss.Shape.copy()
    bb = sh.BoundBox
    return [moved(sh, -(bb.XMin + bb.XMax) / 2, y)]

def label_faces():
    return warn_faces(), text_faces("UWAGA", 4.5, 0) + text_faces("230 V", 6.0, -8.4)

def engrave(faces2d, z0, y0, mirror, xc=W / 2):
    out = []
    for f in faces2d:
        g = f.copy()
        if mirror:
            g = g.mirror(V(0, 0, 0), V(1, 0, 0))
        sol = g.extrude(V(0, 0, 1))
        sol.rotate(V(0, 0, 0), V(1, 0, 0), 90)
        sol.translate(V(xc, y0, z0))
        out.append(sol)
    return out

def body():
    s = box(0, Yf, 0, W, D - Yf, H).cut(box(t, Yf - 1, t, W - 2 * t, D - t - Yf + 1, H - 2 * t))
    adds = [box(t, podest[0], t - 0.5, W - 2 * t, D - t - podest[0] + 0.5, podest[1] - t + 0.5),
            box(t - 0.5, shelf[0], shelf[1], W - 2 * t + 1, D - t - shelf[0] + 0.5, shelf[2] - shelf[1]),
            box(rib[0], rib[2], shelf[2] - 0.5, rib[1] - rib[0], D - t - rib[2] + 0.5, H - t - shelf[2] + 1)]
    adds += [cyl(V(0, y, z), 8, 8, V(1, 0, 0)) for y, z in screws_old]
    adds += [cyl(V(lid_x, Yf + capT, z), boss_d, boss_y1 - Yf - capT, V(0, 1, 0)) for z in lid_z]
    s = fuse([s] + adds)
    cuts = [cyl(V(-1, y, z), ins_d, ins_h + 1, V(1, 0, 0)) for y, z in screws_old]
    cuts += [cyl(V(lid_x, Yf + capT - 1, z), ins_d, 11, V(0, 1, 0)) for z in lid_z]
    cuts += [box(-1, slot_y0, z - slot[1] / 2, t + 1, slot[0], slot[1]) for z in slotsZ]
    cuts.append(box(-1, Yf - 1, win[1], t + 2, win[0] - Yf + 1, win[2] - win[1]))
    cw = cable[1] - cable[0]
    cuts.append(box(cable[0], Yf - 1, -1, cw, cable[2] - cw / 2 - Yf + 1, t + 2))
    cuts.append(cyl(V((cable[0] + cable[1]) / 2, cable[2] - cw / 2, -1), cw, t + 2, V(0, 0, 1)))
    tri, txt = label_faces()
    cuts += engrave(tri, 96, D + 0.4, True) + engrave(txt, 82, D + 0.4, True)
    for c in cuts:
        s = s.cut(c)
    return s.removeSplitter()

def cap():
    adds = [box(t + cap_cl, Yf, t + cap_cl, W - 2 * t - 2 * cap_cl, capT, H - 2 * t - 2 * cap_cl)]
    adds += [box(t - tab[0], tab_y0, z - tab[2] / 2, tab[0] + cap_cl + 0.5, tab[1], tab[2]) for z in slotsZ]
    s = fuse(adds)
    cuts = [cyl(V(lid_x, Yf - 1, z), 3.4, capT + 2, V(0, 1, 0)) for z in lid_z]
    tri, txt = label_faces()
    cuts += engrave(tri, 74, Yf + 0.6, False, 17) + engrave(txt, 60, Yf + 0.6, False, 17)
    for c in cuts:
        s = s.cut(c)
    return s.removeSplitter()

def old_modified():
    m = Mesh.Mesh(OLD)
    sh = Part.Shape()
    sh.makeShapeFromMesh(m.Topology, 0.05)
    s = Part.makeSolid(sh).removeSplitter()
    cuts = [box(POS.x - 6, OLD_OPEN_Y - 1, POS.z + win[1], 7, POS.y + win[0] - OLD_OPEN_Y + 1, win[2] - win[1])]
    cuts += [cyl(V(POS.x - 6, POS.y + y, POS.z + z), 3.4, 7, V(1, 0, 0)) for y, z in screws_old]
    for c in cuts:
        s = s.cut(c)
    return s.removeSplitter()

b = body(); b.translate(POS)
c = cap(); c.translate(POS)
o = old_modified()
for name, shp in (("modul_korpus", b), ("modul_pokrywa", c), ("stara_obudowa_z_oknem", o)):
    print(name, "valid", shp.isValid(), "solids", len(shp.Solids), "volume", round(shp.Volume, 1))
    shp.exportStep(os.path.join(OUT, name + ".step"))
Part.makeCompound([o, b, c]).exportStep(os.path.join(OUT, "zlozenie.step"))
for obj in list(doc.Objects):
    doc.removeObject(obj.Name)
for name, shp in (("Stara_obudowa", o), ("Korpus", b), ("Pokrywa", c)):
    doc.addObject("Part::Feature", name).Shape = shp
doc.recompute()
doc.saveAs(os.path.join(OUT, "modul_230V.FCStd"))
print("PODSUMOWANIE: STEP zapisane w", OUT)
