#!/usr/bin/env python3
"""Draw the front page for make.fun news-image-20261125.

Renders one 1024x1024 newspaper front page summing up the world's
news of Tuesday 25 November 2026 and writes it to entry.png next to
this file. Build-time tool only: the entry program (main.py) copies
the finished image to /output. Uses Pillow, which is available on the
build machine; the entry itself is a plain copy and needs stdlib only.

Every story below was checked against the day's wires (Reuters, AP,
UEFA, UN News, Kyiv Independent and others) during research on
26 November 2026. Press time: 04:00 UTC, 26 November 2026.
"""

import glob
import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
PAPER = (246, 241, 227)      # cream newspaper paper
INK = (26, 26, 26)
RED = (168, 30, 30)
GRAY = (110, 105, 92)
LIGHT = (232, 226, 210)

REGION_COLORS = {
    "EUROPE": (31, 78, 121),
    "MIDDLE EAST": (139, 26, 26),
    "AMERICAS": (46, 107, 52),
    "ASIA-PACIFIC": (181, 107, 0),
    "AFRICA": (107, 79, 161),
    "OCEANIA": (15, 122, 122),
    "WORLD": (85, 85, 85),
}

STATUS_COLORS = {
    "CONFIRMED": (30, 125, 50),
    "OFFICIAL": (21, 101, 192),
    "REPORTED": (239, 108, 0),
    "CLAIM": (198, 40, 40),
    "PENDING": (97, 97, 97),
    "ONGOING": (106, 27, 154),
}

# (region, field, status, source, headline, body, scene)
LEADS = [
    ("MIDDLE EAST", "war", "REPORTED", "Reuters",
     "Houthi drone hits Riyadh's tallest tower — 11 hurt",
     "A Houthi drone struck Riyadh's tallest tower for the second time "
     "in a week, wounding 11 people from four countries. The coalition "
     "hit Hodeidah port in reply.",
     "tower", "TOWER HIT TWICE", "11 HURT"),
    ("EUROPE", "war", "REPORTED", "Kyiv Independent",
     "Ukrainian drones set two Russian refineries ablaze",
     "Fires broke out at the Syzran and Kuibyshev refineries in Samara, "
     "800 km from the border, after overnight drone strikes. Moscow said "
     "it downed 305 drones.",
     "refinery", "TWO REFINERIES ABLAZE", "305 DRONES DOWNED"),
    ("AMERICAS", "tech", "CONFIRMED", "Reuters",
     "Huawei convicted in New York on 10 of 12 counts",
     "A federal jury found Huawei guilty of bank fraud, sanctions breaches "
     "and stealing US trade secrets. Cleared of racketeering; sentencing "
     "in 2027, appeal planned.",
     "court", "GUILTY ON 10 COUNTS", "10 OF 12"),
    ("ASIA-PACIFIC", "space", "OFFICIAL", "Reuters",
     "Shenzhou-24 carries first foreigner to Tiangong",
     "China launched Shenzhou-24 carrying Pakistani astronaut Muhammad "
     "Zeeshan Ali — the first foreigner aboard Tiangong. The crew will "
     "run science in orbit.",
     "rocket", "FIRST FOREIGNER ABOARD", "SHENZHOU-24"),
    ("OCEANIA", "diplomacy", "OFFICIAL", "wires",
     "Australia signs Solomons pact: AU$740m, no foreign base",
     "Australia and Solomon Islands signed a sweeping security treaty in "
     "Canberra. Honiara pledges no foreign base; Canberra gives AU$740m "
     "over 10 years.",
     "treaty", "NO FOREIGN BASE", "AU$740M"),
    ("MIDDLE EAST", "war", "CONFIRMED", "IDF + medics",
     "Gaza strike kills Hamas security chief and family",
     "An Israeli strike on a Beach camp flat killed Mohammed Abu al-Ouf, "
     "Hamas's security chief in northern Gaza, with his wife and two "
     "daughters.",
     "gaza", "CEASEFIRE FRAYING", "74,746 DEAD"),
]

# (region, field, status, source, headline, body)
BRIEFS = [
    ("EUROPE", "war", "REPORTED", "Reuters",
     "Kyiv says it hit Savasleyka air base, five planes damaged",
     "Three MiG-31 jets and two Su-34 bombers were knocked out, Kyiv says."),
    ("EUROPE", "energy", "REPORTED", "Hudson / ISW",
     "Russian strike halts a DTEK power plant",
     "A strike halted a thermal plant; power was hit in five regions."),
    ("EUROPE", "war", "REPORTED", "Kyiv Independent",
     "Zaporizhzhia block hit: 2 killed, 48 hurt",
     "A strike partly destroyed a five-storey block, killing two and injuring 48."),
    ("EUROPE", "war", "OFFICIAL", "Kyiv Independent",
     "Zelenskyy confirms strike on Russian ship",
     "Zelenskyy defended the right to hit the ship, despite allies' concerns."),
    ("EUROPE", "war", "REPORTED", "The Independent",
     "Norway and Ukraine expand anti-drone shield",
     "The two countries will widen cooperation on a new anti-drone system."),
    ("EUROPE", "sport", "CONFIRMED", "UEFA",
     "Liverpool and Barça win; PSG held, Bayern beaten",
     "Liverpool won 3–0 at Brugge, Barça 4–1 at Sabah; Roma held PSG 2–2, Lille beat Bayern 2–1."),
    ("MIDDLE EAST", "war", "CLAIM", "wires",
     "Iran claims mines set four tankers ablaze",
     "Tehran said mines hit four tankers in Hormuz; no maritime authority has confirmed it."),
    ("MIDDLE EAST", "energy", "CLAIM", "Reuters",
     "Houthis say they hit Saudi Arabia's biggest refinery",
     "The group said it hit the kingdom's largest refinery; Brent held at $94.81 a barrel."),
    ("MIDDLE EAST", "war", "REPORTED", "Reuters",
     "IS attack kills two Syrian security men",
     "An IS attack killed two security men and wounded five in Hasaka, state TV said."),
    ("MIDDLE EAST", "law", "OFFICIAL", "UN News",
     "UN rights chief warns of 'further atrocity crimes'",
     "Volker Türk cited killings despite the ceasefire and Gaza's shrinking area."),
    ("AMERICAS", "markets", "OFFICIAL", "Reuters",
     "US proposes tariffs on 14 trading partners",
     "Washington targets excess factory capacity; the highest rates hit China."),
    ("AMERICAS", "markets", "OFFICIAL", "Reuters",
     "US growth revised up to 4.3%; core prices 3.3%",
     "Q3 growth was revised sharply higher; the Fed's core inflation gauge stayed at 3.3%."),
    ("AMERICAS", "transport", "REPORTED", "wires",
     "Thanksgiving rush hit by O'Hare ground stops",
     "Flights halted twice in two days at Chicago O'Hare; an East Coast storm looms."),
    ("AMERICAS", "tech", "REPORTED", "Reuters",
     "AI sell-off: Nvidia falls, Anthropic slides",
     "Huang apologised as Nvidia fell 3.9%; Anthropic slid below its $83 IPO price."),
    ("AMERICAS", "tech", "REPORTED", "Reuters",
     "Microsoft declares 'Code Red' after outage",
     "Internal memos show an emergency declared after a historic outage rattled customers."),
    ("AMERICAS", "crime", "REPORTED", "wires",
     "Cartagena siege ends: 20 hostages freed",
     "Forces freed 20 hostages from a Cartagena supermarket a day after gunmen seized 30."),
    ("AMERICAS", "politics", "REPORTED", "wires",
     "Bolsonaro taken to ICU with bowel obstruction",
     "The ex-president was rushed to intensive care in Brasília with severe abdominal pain."),
    ("AMERICAS", "energy", "REPORTED", "wires",
     "Millions without power as Cuba blacks out again",
     "Fuel shortages and an ageing grid left millions of Cubans without electricity."),
    ("ASIA-PACIFIC", "markets", "REPORTED", "Reuters",
     "Asia shares bounce as Wall Street recovers",
     "Nikkei rose 1.6% and Seoul 1.9% as Wall Street fought back from deep lows."),
    ("ASIA-PACIFIC", "health", "REPORTED", "wires",
     "Landmine toll nears 7,000 in 2025, a five-year high",
     "Landmine casualties hit a five-year high, led by Myanmar and Syria, monitors report."),
    ("ASIA-PACIFIC", "politics", "REPORTED", "CNA",
     "Taiwan parties step up poll campaigning",
     "With three days to local elections, leaders criss-crossed the island in motorcades."),
    ("ASIA-PACIFIC", "sport", "REPORTED", "wires",
     "India chase first Test series win in NZ in 17 years",
     "India head into Friday's second Test eyeing a first series win in NZ in 17 years."),
    ("AFRICA", "war", "REPORTED", "rights groups",
     "RSF drones kill 19 in Sudan's Blue Nile capital",
     "Drone strikes on Damazin and Roseires killed 19 civilians, two rights groups said."),
    ("AFRICA", "health", "REPORTED", "UN News",
     "Ebola workers trapped as fighting rages in Ituri",
     "WHO staff took cover for over 24 hours in a hospital as heavy fighting closed in."),
    ("AFRICA", "war", "REPORTED", "wires",
     "Congo rebels pull back after clashes",
     "Lubanga's CRP halted its advance on Bunia and withdrew, citing Uganda-mediated talks."),
    ("AFRICA", "sport", "REPORTED", "wires",
     "Senegal get 2025 AFCON title back after CAS ruling",
     "The Court of Arbitration for Sport restored Senegal's 2025 Africa Cup of Nations title."),
    ("OCEANIA", "tech", "REPORTED", "wires",
     "Australia passes Digital Duty of Care",
     "Parliament passed a law forcing Big Tech to prevent harm, with fines up to 5%."),
    ("OCEANIA", "markets", "REPORTED", "wires",
     "Australia inflation jumps to 4.9%",
     "Prices rose faster than expected as a lightning bushfire hit Flinders Island."),
    ("OCEANIA", "energy", "REPORTED", "Beyond2C",
     "Green steel: Australia–China hydrogen pact",
     "Greensteel Australia and Envision will explore a 400 MW green hydrogen system."),
    ("WORLD", "climate", "REPORTED", "Reuters",
     "OPEC blames EU for COP31 collapse",
     "Haitham Al Ghais said oil producers should not be blamed for the talks' failure."),
    ("WORLD", "climate", "REPORTED", "Beyond2C",
     "Warming hits 1.46°C over past 12 months",
     "The 12-month average sits 0.04°C below the 1.5°C limit; 2025 stood at 1.41°C."),
    ("WORLD", "war", "OFFICIAL", "UN News",
     "UN aid chief: war blocks Yemen's food and medicine",
     "Tom Fletcher warned fighting is cutting Yemeni families off from the aid they need."),
    ("WORLD", "sport", "REPORTED", "Reuters",
     "Qatar Grand Prix goes ahead despite the war",
     "Doha's Formula One race runs this weekend despite the war on Qatar's doorstep."),
]

TIMELINE = [
    ("02:46", "Gaza strike kills Hamas chief"),
    ("05:45", "One killed in Samara drone attack"),
    ("06:45", "Two Samara refineries hit"),
    ("10:27", "Gaza toll: 74,746 dead"),
    ("23:44", "Champions League night ends"),
]

NUMBERS = [
    "305 drones downed (Moscow)",
    "74,746 Gaza dead",
    "4.3% US Q3 growth",
    "$94.81 Brent",
    "1.46°C warming",
    "AU$740m Solomons aid",
]

DATE_CHECK_OUT = (
    "22 Nov COP31 ends, no pact | 22 Nov corvette Merkury sunk | "
    "23 Nov drone violates Polish airspace | 24 Nov Ukraine–Germany missile deal | "
    "24 Nov Real Madrid 5–1 PSV | 24 Nov Cartagena siege begins"
)

DATE_CHECK_NOT_YET = (
    "27 Nov — India v NZ 2nd Test | 28 Nov — Taiwan elections | "
    "30 Nov — Qatar GP | 2027 — Huawei sentencing; COP32 Ethiopia"
)

# (lon, lat) of the six lead stories, in lead order.
LEAD_PINS = [(46.7, 24.7), (50.2, 53.2), (-74.0, 40.7),
             (100.3, 40.9), (160.0, -9.6), (34.5, 31.5)]

CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-55, 60),
     (-80, 45), (-90, 30), (-97, 26), (-105, 20), (-86, 12), (-79, 9),
     (-92, 15), (-110, 23), (-125, 40), (-124, 48), (-150, 60)],
    [(-79, 9), (-60, 10), (-52, 5), (-35, -8), (-40, -20), (-48, -28),
     (-58, -35), (-70, -55), (-73, -40), (-70, -20), (-80, -5)],
    [(-10, 36), (-9, 43), (0, 50), (5, 58), (10, 62), (18, 70), (30, 71),
     (40, 68), (30, 60), (28, 55), (20, 45), (12, 44), (3, 43), (-2, 37)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -25), (28, -33), (20, -35),
     (12, -18), (9, 0), (-8, 5)],
    [(40, 68), (60, 70), (80, 73), (110, 76), (140, 72), (160, 66),
     (178, 65), (160, 60), (140, 50), (130, 42), (127, 35), (120, 25),
     (110, 20), (100, 10), (95, 15), (90, 22), (80, 15), (75, 8), (70, 20),
     (60, 25), (50, 28), (43, 12), (40, 30)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (135, -12), (130, -13), (122, -17)],
]


def find_font(names):
    for pat in ("/usr/share/fonts/**/*.ttf", "/usr/local/share/fonts/**/*.ttf"):
        for path in glob.glob(pat, recursive=True):
            base = os.path.basename(path)
            for name in names:
                if base.lower() == name.lower():
                    return path
    return None


def load_fonts():
    serif_b = find_font(["DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf"])
    serif = find_font(["DejaVuSerif.ttf", "LiberationSerif-Regular.ttf"])
    sans_b = find_font(["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"])
    sans = find_font(["DejaVuSans.ttf", "LiberationSans-Regular.ttf"])

    def f(path, size):
        if path:
            return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    return {
        "masthead": f(serif_b, 48),
        "date": f(serif_b, 17),
        "counts": f(sans_b, 12),
        "lead_head": f(serif_b, 15),
        "lead_body": f(sans, 11),
        "lead_meta": f(sans, 9),
        "banner": f(sans_b, 16),
        "callout": f(sans_b, 11),
        "badge": f(sans_b, 8),
        "section": f(sans_b, 12),
        "brief_head": f(sans_b, 11),
        "brief_body": f(sans, 9),
        "brief_src": f(sans, 8),
        "map_key": f(sans, 9),
        "strip": f(sans_b, 10),
        "strip_body": f(sans, 9),
        "footer": f(sans, 9),
        "footer_s": f(sans, 8),
        "footer_b": f(sans_b, 9),
    }


def wrap(draw, text, font, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def trunc(draw, text, font, width):
    if draw.textlength(text, font=font) <= width:
        return text
    while text and draw.textlength(text + "…", font=font) > width:
        text = text[:-1]
    return text + "…"


def pill(draw, x, y, text, font, fill, fg=(255, 255, 255)):
    w = int(draw.textlength(text, font=font)) + 10
    h = 13
    draw.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=fill)
    draw.text((x + 5, y + 2), text, font=font, fill=fg)
    return w


def draw_scene(draw, scene, x, y, w, h):
    """A distinct little scene per lead illustration."""
    if scene == "tower":
        draw.rectangle([x, y, x + w, y + h], fill=(38, 52, 86))
        draw.rectangle([x, y + h - 26, x + w, y + h], fill=(24, 32, 54))
        for bx, bh in ((0, 26), (52, 40), (96, 30), (150, 46), (210, 34), (262, 28)):
            draw.rectangle([x + bx, y + h - 26 - bh, x + bx + 34, y + h - 26],
                           fill=(16, 22, 40))
        draw.rectangle([x + 138, y + 8, x + 158, y + h - 26], fill=(200, 170, 90))
        draw.polygon([(x + 138, y + 8), (x + 158, y + 8), (x + 148, y - 2)],
                     fill=(200, 170, 90))
        for wy in range(y + 16, y + h - 30, 9):
            draw.rectangle([x + 143, wy, x + 153, wy + 4], fill=(255, 230, 140))
        for i, (cx, cy, r) in enumerate(((176, 26, 9), (188, 18, 12), (202, 26, 8))):
            draw.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                         fill=(200, 200, 200))
        draw.ellipse([x + 236, y + 12, x + 242, y + 18], fill=(20, 20, 20))
        draw.line([x + 232, y + 15, x + 246, y + 15], fill=(20, 20, 20), width=2)
    elif scene == "refinery":
        draw.rectangle([x, y, x + w, y + h], fill=(74, 44, 30))
        draw.rectangle([x, y + h - 22, x + w, y + h], fill=(40, 26, 18))
        for bx, bw in ((10, 26), (60, 20), (120, 30), (200, 24), (260, 28)):
            draw.rectangle([x + bx, y + h - 22 - 34, x + bx + bw, y + h - 22],
                           fill=(28, 18, 12))
        draw.rectangle([x + 150, y + 6, x + 158, y + h - 22], fill=(28, 18, 12))
        draw.rectangle([x + 230, y + 12, x + 238, y + h - 22], fill=(28, 18, 12))
        for fx, fy, s in ((60, 34, 16), (120, 30, 20), (205, 36, 14), (262, 32, 17)):
            draw.polygon([(x + fx - s, y + fy + 10), (x + fx, y + fy - 14),
                          (x + fx + s, y + fy + 10)], fill=(255, 120, 20))
            draw.polygon([(x + fx - s // 2, y + fy + 10), (x + fx, y + fy - 4),
                          (x + fx + s // 2, y + fy + 10)], fill=(255, 210, 60))
        for cx, cy, r in ((180, 18, 10), (196, 12, 12), (212, 20, 8)):
            draw.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                         fill=(120, 120, 120))
    elif scene == "court":
        draw.rectangle([x, y, x + w, y + h], fill=(58, 84, 110))
        draw.polygon([(x + 60, y + 8), (x + w - 60, y + 8), (x + w // 2, y + 30)],
                     fill=(230, 226, 210))
        for cx in (86, 130, 174, 218, 262):
            draw.rectangle([x + cx - 7, y + 30, x + cx + 7, y + h - 16],
                           fill=(240, 238, 228))
        draw.rectangle([x + 40, y + h - 16, x + w - 40, y + h - 8],
                       fill=(230, 226, 210))
        draw.rectangle([x + 20, y + h - 8, x + w - 20, y + h], fill=(210, 204, 186))
        draw.line([x + w // 2, y + 34, x + w // 2, y + 44], fill=(255, 215, 90),
                  width=3)
        draw.line([x + w // 2 - 16, y + 36, x + w // 2 + 16, y + 36],
                  fill=(255, 215, 90), width=3)
        for sx in (w // 2 - 16, w // 2 + 16):
            draw.polygon([(x + sx - 8, y + 36), (x + sx + 8, y + 36),
                          (x + sx, y + 48)], fill=(255, 215, 90))
    elif scene == "rocket":
        draw.rectangle([x, y, x + w, y + h], fill=(8, 10, 26))
        import random
        rnd = random.Random(42)
        for _ in range(26):
            sx = x + rnd.randint(4, w - 4)
            sy = y + rnd.randint(3, h - 14)
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        draw.ellipse([x - 60, y + h - 14, x + w + 60, y + h + 60], fill=(40, 90, 160))
        draw.ellipse([x - 40, y + h - 6, x + w + 40, y + h + 40], fill=(90, 140, 200))
        rx, ry = x + 60, y + 12
        draw.rectangle([rx, ry, rx + 16, ry + 30], fill=(240, 240, 240))
        draw.polygon([(rx, ry), (rx + 16, ry), (rx + 8, ry - 10)], fill=(200, 40, 40))
        draw.polygon([(rx, ry + 30), (rx + 16, ry + 30), (rx + 8, ry + 44)],
                     fill=(255, 140, 30))
        draw.polygon([(rx, ry + 30), (rx + 16, ry + 30), (rx + 8, ry + 38)],
                     fill=(255, 220, 80))
        draw.rectangle([x + 190, y + 18, x + 236, y + 26], fill=(180, 180, 180))
        draw.rectangle([x + 236, y + 12, x + 252, y + 32], fill=(150, 150, 150))
        draw.rectangle([x + 190, y + 10, x + 200, y + 34], fill=(40, 90, 180))
        draw.rectangle([x + 252, y + 10, x + 262, y + 34], fill=(40, 90, 180))
    elif scene == "treaty":
        draw.rectangle([x, y, x + w, y + h], fill=(140, 190, 220))
        draw.rectangle([x, y + h - 18, x + w, y + h], fill=(30, 100, 160))
        for wy in (h - 14, h - 8):
            for sx in range(0, w, 26):
                draw.arc([x + sx, y + wy - 5, x + sx + 26, y + wy + 7],
                         start=180, end=360, fill=(255, 255, 255), width=2)
        draw.rectangle([x + 18, y + 6, x + 24, y + h - 18], fill=(120, 90, 40))
        draw.rectangle([x + w - 24, y + 6, x + w - 18, y + h - 18],
                       fill=(120, 90, 40))
        draw.polygon([(x + 24, y + 8), (x + 62, y + 8), (x + 62, y + 26),
                      (x + 24, y + 26)], fill=(20, 60, 140))
        for sx, sy in ((30, 14), (44, 12), (52, 20), (36, 22)):
            draw.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2],
                         fill=(255, 255, 255))
        draw.polygon([(x + w - 62, y + 8), (x + w - 24, y + 8), (x + w - 24, y + 26),
                      (x + w - 62, y + 26)], fill=(20, 120, 60))
        draw.ellipse([x + w - 52, y + 14, x + w - 34, y + 20], fill=(255, 215, 0))
        draw.rectangle([x + w // 2 - 46, y + 18, x + w // 2 + 46, y + h - 6],
                       fill=(250, 248, 240), outline=(150, 140, 120))
        for ly in range(y + 24, y + h - 12, 6):
            draw.line([x + w // 2 - 38, ly, x + w // 2 + 38, ly],
                      fill=(170, 165, 150), width=1)
        draw.ellipse([x + w // 2 + 24, y + h - 20, x + w // 2 + 40, y + h - 8],
                     fill=(168, 30, 30))
    elif scene == "gaza":
        draw.rectangle([x, y, x + w, y + h], fill=(120, 118, 112))
        draw.rectangle([x, y + h - 20, x + w, y + h], fill=(70, 68, 64))
        draw.rectangle([x + 16, y + 18, x + 76, y + h - 20], fill=(52, 52, 50))
        draw.polygon([(x + 76, y + 18), (x + 110, y + 30), (x + 110, y + h - 20),
                      (x + 76, y + h - 20)], fill=(44, 44, 42))
        draw.rectangle([x + 130, y + 28, x + 190, y + h - 20], fill=(60, 60, 58))
        draw.rectangle([x + 210, y + 12, x + 280, y + h - 20], fill=(48, 48, 46))
        for wx in (28, 48):
            for wy in (30, 46):
                draw.rectangle([x + wx, y + wy, x + wx + 10, y + wy + 8],
                               fill=(220, 200, 120))
        for cx, cy, r in ((150, 16, 11), (168, 10, 13), (186, 18, 9), (240, 14, 10)):
            draw.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                         fill=(90, 88, 84))
        draw.rectangle([x + 250, y + 34, x + 268, y + 52], fill=(255, 255, 255))
        draw.rectangle([x + 256, y + 38, x + 262, y + 48], fill=(200, 30, 30))
        draw.rectangle([x + 252, y + 42, x + 266, y + 44], fill=(200, 30, 30))


def build_page():
    fonts = load_fonts()
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # outer frame
    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=2)
    d.rectangle([10, 10, W - 11, H - 11], outline=INK, width=1)

    # ---- masthead ----
    title = "THE DAILY GLOBE"
    d.text((W // 2, 6), title, font=fonts["masthead"], fill=INK, anchor="mt")
    d.text((W // 2, 58), "TUESDAY 25 NOVEMBER 2026",
           font=fonts["date"], fill=RED, anchor="mt")
    d.line([16, 78, W - 16, 78], fill=INK, width=2)
    d.line([16, 81, W - 16, 81], fill=RED, width=1)

    regions = sorted({s[0] for s in LEADS} | {s[0] for s in BRIEFS})
    fields = sorted({s[1] for s in LEADS} | {s[1] for s in BRIEFS})
    n_stories = len(LEADS) + len(BRIEFS)
    counts = "%d STORIES · %d REGIONS · %d FIELDS · PRESS TIME 04:00 UTC" % (
        n_stories, len(regions), len(fields))
    d.text((W // 2, 85), counts, font=fonts["counts"], fill=INK, anchor="mt")
    d.line([16, 98, W - 16, 98], fill=INK, width=1)

    # ---- lead cards: 3 columns x 2 rows ----
    cw = 325
    ch = 140
    x0, y0 = 14, 104
    gap = 6
    for i, lead in enumerate(LEADS):
        region, field, status, source, head, body, scene, banner, callout = lead
        cx = x0 + (i % 3) * (cw + gap)
        cy = y0 + (i // 3) * (ch + gap)
        d.rectangle([cx, cy, cx + cw, cy + ch], outline=INK, width=1,
                    fill=(255, 255, 255))
        # illustration (drawn on a layer so no scene can paint outside it)
        layer = Image.new("RGB", (cw - 2, 50), PAPER)
        ld = ImageDraw.Draw(layer)
        draw_scene(ld, scene, 0, 0, cw - 2, 50)
        img.paste(layer, (cx + 1, cy + 1))
        d.text((cx + 10, cy + 6), banner, font=fonts["banner"], fill=(255, 255, 255),
               stroke_width=2, stroke_fill=(0, 0, 0))
        pill(d, cx + cw - 8 - (len(status) * 6 + 12), cy + 6, status,
             fonts["badge"], STATUS_COLORS[status])
        cw2 = int(d.textlength(callout, font=fonts["callout"])) + 12
        d.rounded_rectangle([cx + 8, cy + 34, cx + 8 + cw2, cy + 48], radius=6,
                            fill=(0, 0, 0))
        d.text((cx + 14, cy + 37), callout, font=fonts["callout"],
               fill=(255, 215, 90))
        # headline + body + meta
        ty = cy + 56
        for line in wrap(d, head, fonts["lead_head"], cw - 14)[:2]:
            d.text((cx + 7, ty), line, font=fonts["lead_head"], fill=INK)
            ty += 17
        for line in wrap(d, body, fonts["lead_body"], cw - 14)[:3]:
            d.text((cx + 7, ty), line, font=fonts["lead_body"], fill=(40, 40, 40))
            ty += 13
        d.text((cx + 7, cy + ch - 13), "%s · %s" % (source, region),
               font=fonts["lead_meta"], fill=GRAY)

    # ---- ALSO ON briefs: 2 columns ----
    by = y0 + 2 * ch + gap + 6
    d.text((14, by), "ALSO ON — %d MORE STORIES" % len(BRIEFS),
           font=fonts["section"], fill=RED)
    d.line([14, by + 16, W - 14, by + 16], fill=INK, width=1)
    brief_top = by + 22
    col_w = (W - 28 - 10) // 2
    rows = (len(BRIEFS) + 1) // 2
    row_h = 21
    for i, b in enumerate(BRIEFS):
        region, field, status, source, head, body = b
        col = i % 2
        row = i // 2
        bx = 14 + col * (col_w + 10)
        byy = brief_top + row * row_h
        d.rectangle([bx, byy + 2, bx + 4, byy + row_h - 3],
                    fill=REGION_COLORS[region])
        head_w = col_w - 14 - (len(status) * 6 + 14)
        d.text((bx + 9, byy), trunc(d, head, fonts["brief_head"], head_w),
               font=fonts["brief_head"], fill=INK)
        pill(d, bx + col_w - (len(status) * 6 + 12), byy + 1, status,
             fonts["badge"], STATUS_COLORS[status])
        body_txt = trunc(d, body + "  (%s)" % source, fonts["brief_body"],
                         col_w - 14)
        d.text((bx + 9, byy + 11), body_txt, font=fonts["brief_body"],
               fill=(60, 60, 60))

    # ---- map ----
    my = brief_top + rows * row_h + 8
    d.text((14, my), "THE DAY, MAPPED — LEAD STORIES 1–6",
           font=fonts["section"], fill=INK)
    map_x, map_y, map_w, map_h = 14, my + 14, 620, 89
    d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], outline=INK,
                width=1, fill=(235, 232, 220))

    def proj(lon, lat):
        return (map_x + (lon + 180) / 360.0 * map_w,
                map_y + (90 - lat) / 180.0 * map_h)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(196, 190, 172), outline=(120, 115, 100))
    for i, (lon, lat) in enumerate(LEAD_PINS):
        px, py = proj(lon, lat)
        col = REGION_COLORS[LEADS[i][0]]
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=col, outline=(255, 255, 255),
                  width=2)
        d.text((px, py), str(i + 1), font=fonts["badge"], fill=(255, 255, 255),
               anchor="mm")
    # colour key
    kx = map_x + map_w + 12
    d.text((kx, map_y + 2), "KEY — STORIES BY REGION", font=fonts["map_key"],
           fill=INK)
    counts_by_region = {}
    for s in LEADS + BRIEFS:
        counts_by_region[s[0]] = counts_by_region.get(s[0], 0) + 1
    key_regions = ["EUROPE", "MIDDLE EAST", "AMERICAS", "ASIA-PACIFIC",
                   "AFRICA", "OCEANIA", "WORLD"]
    for j, region in enumerate(key_regions):
        kx2 = kx + (j // 4) * 180
        ky = map_y + 18 + (j % 4) * 13
        d.rectangle([kx2, ky, kx2 + 10, ky + 10], fill=REGION_COLORS[region])
        d.text((kx2 + 14, ky), "%s %d" % (region, counts_by_region.get(region, 0)),
               font=fonts["map_key"], fill=INK)

    # ---- timeline strip ----
    ty = map_y + map_h + 6
    d.rectangle([14, ty, W - 14, ty + 18], fill=(26, 26, 26))
    d.text((20, ty + 4), "TIMELINE (UTC)", font=fonts["strip"], fill=(255, 215, 90))
    tx = 130
    for t, what in TIMELINE:
        seg = "%s  %s" % (t, what)
        d.text((tx, ty + 4), seg, font=fonts["strip_body"], fill=(255, 255, 255))
        tx += int(d.textlength(seg, font=fonts["strip_body"])) + 14

    # ---- numbers strip (one line) ----
    ny = ty + 20
    d.text((14, ny), "THE DAY IN NUMBERS —", font=fonts["section"], fill=RED)
    nx = 14 + int(d.textlength("THE DAY IN NUMBERS —  ", font=fonts["section"]))
    for num in NUMBERS:
        d.text((nx, ny + 1), "· " + num, font=fonts["strip_body"], fill=INK)
        nx += int(d.textlength("· " + num, font=fonts["strip_body"])) + 12

    # ---- date check ----
    dy = ny + 18
    d.rectangle([14, dy, W - 14, dy + 38], outline=INK, width=1,
                fill=(255, 255, 255))
    d.text((20, dy + 3), "DATE CHECK", font=fonts["section"], fill=RED)
    d.text((20, dy + 16), "Discarded (other days): " + DATE_CHECK_OUT,
           font=fonts["footer_s"], fill=INK)
    d.text((20, dy + 28), "Not yet: " + DATE_CHECK_NOT_YET,
           font=fonts["footer_s"], fill=INK)

    # ---- footer: legend + press time ----
    fy = dy + 44
    d.text((14, fy),
           "HOW TO READ THE TAGS:  CONFIRMED = 2+ outlets or official source  ·  "
           "OFFICIAL = on the record  ·  REPORTED = one outlet  ·  "
           "CLAIM = one side's account, unconfirmed  ·  PENDING = not settled yet",
           font=fonts["footer"], fill=INK)
    d.text((14, fy + 12),
           "Every story on this page happened, or was first reported, on "
           "Tuesday 25 November 2026. Wires read to 04:00 UTC, 26 Nov 2026. "
           "Sources named beside each story.",
           font=fonts["footer"], fill=GRAY)
    return img


def main():
    img = build_page()
    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (out, size, sha))
    if size > 1048576:
        print("WARNING: over the 1 MiB gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
