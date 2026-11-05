// Modul 230 V (K1, K2, zasilacz 5 V) przykrecany do PowerSwitch-SSR-Mount, gora rowno.
// Uklad lokalny: X 0..W (X=0 sciana przy starej obudowie), Y Yf..D (Yf strona otwarta / pokrywa,
// Y=D sciana zewnetrzna z napisem), Z 0..H (dol..gora). Pozycja w ukladzie starej obudowy: POS.
// part = "body" | "cap" | "old" | "assembly" | "module" | "body_print" | "cap_print"
// v2 261103: H 140.8, przepust nizej o 30 i otwarty od pokrywy, wyciecie na kabel zamiast GX12.
// v4 261103 (wg obudowa1.stl Gregora): korpus 4 mm glebiej do przodu (Yf = -4, rowno ze stara obudowa),
// wnetrze: podest na dnie, polka i przegroda przekaznikow zamiast kieszeni; pokrywa plaska wpuszczona w korpus:
// 4 jezyki po lewej w szczelinach lewej scianki, 2 sruby M3 po prawej w tulejkach (tulejka = oparcie pokrywy).
part = "assembly";

$fn = 48;
W = 40; D = 26; H = 140.8; t = 3;
Yf = -4;                                   // przod korpusu
POS = [432.18, 320.15, 8.1];              // prawa sciana starej obudowy, gora rowno z z = 148.9
OLD = "PowerSwitch-SSR-Mount.stl";   // third-party enclosure, NOT included - see README
OLD_OPEN_Y = 316.15;                       // otwarta strona starej obudowy

ins_d = 4.0; ins_h = 6;                    // otwory na wtapiane tulejki M3
win = [20, 75, 97];                        // przepust w scianie X=0: otwarty od Yf do Y=win[0], Z od..do
screws_old = [[13.85, 4.9], [13.85, H - t - 3.8]];   // [Y, Z] srub M3 ze starej obudowy w tulejki
cable = [16, 24, 8];                       // wyciecie na kabel w dnie: X od..do, do Y

podest = [15, 8.7];                        // podest na dnie: od Y do tylu, do Z
shelf = [16, 97, 99.1];                    // polka pod przekaznikami: od Y, Z od..do
rib = [19, 21, 16];                        // przegroda K1 | K2: X od..do, od Y; od polki do gory

capT = 2.6;                                // pokrywa plaska: Y Yf..Yf+capT
cap_cl = 0.2;                              // luz pokrywy w ramce
slotsZ = [6.85, 46.35, 102.6, 132.55];     // srodki jezykow / szczelin w lewej sciance
slot = [1.6, 5];                           // szczelina: Y, Z (przelotowa w X)
tab = [2.2, 1.2, 4.5];                     // jezyk: wejscie w scianke, grubosc, wysokosc
lid_x = 32.5; lid_z = [51.4, 94.4];        // sruby pokrywy (tulejki przy prawej sciance)
boss_d = 9.5; boss_y1 = 16;

tab_y0 = Yf + capT - tab[1];               // jezyk rowno z tylna powierzchnia pokrywy
slot_y0 = tab_y0 - (slot[0] - tab[1]) / 2;

module tri2d(s) { polygon([[-s/2, 0], [s/2, 0], [0, s*0.866]]); }
module warn2d(s = 24) {
    difference() { tri2d(s); offset(delta = -2) tri2d(s); }
    translate([0, s*0.33]) polygon([[1.5, 9], [-2.5, 1], [0, 1], [-1.5, -4], [2.5, 3], [0, 3]]);
}
module warn_text2d(sz = 6) {
    text("UWAGA", size = sz*0.75, halign = "center", font = "Liberation Sans:style=Bold");
    translate([0, -sz*1.4]) text("230 V", size = sz, halign = "center", font = "Liberation Sans:style=Bold");
}

module body() {
    difference() {
        union() {
            difference() {
                translate([0, Yf, 0]) cube([W, D - Yf, H]);
                translate([t, Yf - 1, t]) cube([W - 2*t, D - t - Yf + 1, H - 2*t]);
            }
            translate([t, podest[0], t - 0.5]) cube([W - 2*t, D - t - podest[0] + 0.5, podest[1] - t + 0.5]);
            translate([t - 0.5, shelf[0], shelf[1]]) cube([W - 2*t + 1, D - t - shelf[0] + 0.5, shelf[2] - shelf[1]]);
            translate([rib[0], rib[2], shelf[2] - 0.5]) cube([rib[1] - rib[0], D - t - rib[2] + 0.5, H - t - shelf[2] + 1]);
            for (p = screws_old) translate([0, p[0], p[1]]) rotate([0, 90, 0]) cylinder(d = 8, h = 8);
            for (z = lid_z) translate([lid_x, Yf + capT, z]) rotate([-90, 0, 0]) cylinder(d = boss_d, h = boss_y1 - Yf - capT);
        }
        for (p = screws_old) translate([-1, p[0], p[1]]) rotate([0, 90, 0]) cylinder(d = ins_d, h = ins_h + 1);
        for (z = lid_z) translate([lid_x, Yf + capT - 1, z]) rotate([-90, 0, 0]) cylinder(d = ins_d, h = 11);
        for (z = slotsZ) translate([-1, slot_y0, z - slot[1]/2]) cube([t + 1, slot[0], slot[1]]);
        translate([-1, Yf - 1, win[1]]) cube([t + 2, win[0] - Yf + 1, win[2] - win[1]]);
        cw = cable[1] - cable[0];
        translate([cable[0], Yf - 1, -1]) cube([cw, cable[2] - cw/2 - Yf + 1, t + 2]);
        translate([(cable[0] + cable[1])/2, cable[2] - cw/2, -1]) cylinder(d = cw, h = t + 2);
        translate([W/2, D + 0.4, 96]) rotate([90, 0, 0]) linear_extrude(1) mirror([1, 0, 0]) warn2d();
        translate([W/2, D + 0.4, 82]) rotate([90, 0, 0]) linear_extrude(1) mirror([1, 0, 0]) warn_text2d();
    }
}

module cap() {                             // plaska pokrywa wpuszczona w przod korpusu
    difference() {
        union() {
            translate([t + cap_cl, Yf, t + cap_cl]) cube([W - 2*t - 2*cap_cl, capT, H - 2*t - 2*cap_cl]);
            for (z = slotsZ) translate([t - tab[0], tab_y0, z - tab[2]/2]) cube([tab[0] + cap_cl + 0.5, tab[1], tab[2]]);
        }
        for (z = lid_z) translate([lid_x, Yf - 1, z]) rotate([-90, 0, 0]) cylinder(d = 3.4, h = capT + 2);
        translate([17, Yf + 0.6, 74]) rotate([90, 0, 0]) linear_extrude(1) warn2d();
        translate([17, Yf + 0.6, 60]) rotate([90, 0, 0]) linear_extrude(1) warn_text2d();
    }
}

module old_modified() {                    // przepust (otwarty od strony otwartej) i 2 otwory w prawej scianie
    difference() {
        import(OLD);
        translate([POS[0] - 6, OLD_OPEN_Y - 1, POS[2] + win[1]]) cube([7, POS[1] + win[0] - OLD_OPEN_Y + 1, win[2] - win[1]]);
        for (p = screws_old) translate([POS[0] - 6, POS[1] + p[0], POS[2] + p[1]]) rotate([0, 90, 0]) cylinder(d = 3.4, h = 7);
    }
}

if (part == "body") translate(POS) body();
if (part == "cap") translate(POS) cap();
if (part == "old") old_modified();
if (part == "body_print") translate([0, 0, D]) rotate([-90, 0, 0]) body();
if (part == "cap_print") translate([0, 0, Yf + capT]) rotate([-90, 0, 0]) cap();
if (part == "assembly") {
    color("silver") old_modified();
    color("SteelBlue") translate(POS) body();
    color("Orange", 0.6) translate(POS) cap();
}
if (part == "module") {                    // body + cap only, without the third-party enclosure
    color("SteelBlue") body();
    color("Orange", 0.6) cap();
}
