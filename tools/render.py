"""ERC + PNG preview of every variant (Windows: KiCad 10 CLI + headless Edge + Pillow).

Usage:  python tools/render.py
"""
import glob, os, re, subprocess, tempfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def render(sch, png, tmp):
    subprocess.run([CLI, "sch", "export", "svg", "-o", tmp, "--exclude-drawing-sheet", sch], check=True, capture_output=True)
    svg = os.path.join(tmp, os.path.splitext(os.path.basename(sch))[0] + ".svg")
    html = os.path.join(tmp, "view.html")
    open(html, "w").write('<html><body style="margin:0;background:#fff"><img src="file:///%s" style="width:3000px"></body></html>' % svg.replace("\\", "/"))
    shot = os.path.join(tmp, "shot.png")
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--screenshot=" + shot, "--window-size=3000,2130", "file:///" + html.replace("\\", "/")],
                   capture_output=True)
    im = Image.open(shot)
    bb = Image.eval(im.convert("L"), lambda v: 255 - v if v < 240 else 0).getbbox()
    im.crop((max(bb[0] - 20, 0), max(bb[1] - 20, 0), bb[2] + 20, bb[3] + 20)).save(png)

def erc(sch, tmp):
    rpt = os.path.join(tmp, "erc.rpt")
    subprocess.run([CLI, "sch", "erc", "-o", rpt, sch], capture_output=True)
    txt = open(rpt, encoding="utf8").read()
    m = re.search(r"ERC messages: (\d+)\s+Errors (\d+)\s+Warnings (\d+)", txt)
    issues = re.findall(r"^\[(\w+)\]: (.*)$", txt, re.M)
    return m.groups() if m else ("?", "?", "?"), issues

def main():
    with tempfile.TemporaryDirectory() as tmp:
        for sch in sorted(glob.glob(os.path.join(ROOT, "kicad", "steps", "*.kicad_sch"))):
            n = os.path.basename(sch).split("_")[0]
            (tot, err, warn), issues = erc(sch, tmp)
            render(sch, os.path.join(ROOT, "docs", "img", "%s.png" % n), tmp)
            print("%-4s  ERC errors %s warnings %s  %s" % (n, err, warn, sorted(set(i[0] for i in issues))))
    print("PODSUMOWANIE: PNG in docs/img")

if __name__ == "__main__":
    main()
