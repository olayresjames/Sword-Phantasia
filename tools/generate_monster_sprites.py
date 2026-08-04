"""Generate the battle monster sprites without external services."""

from pathlib import Path
from PIL import Image, ImageDraw


SIZE = 64
SCALE = 2
OUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "monster-sprites"
INK = "#17131f"


def canvas():
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def ellipse(draw, box, fill, width=2):
    draw.ellipse(box, fill=fill, outline=INK, width=width)


def polygon(draw, points, fill, width=2):
    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=INK, width=width, joint="curve")


def save(image, name):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image.resize((SIZE * SCALE, SIZE * SCALE), Image.Resampling.NEAREST).save(OUT_DIR / name)


def slime():
    image, draw = canvas()
    # Soft, translucent-looking body with a wide, friendly monster silhouette.
    polygon(draw, [(10, 49), (12, 37), (18, 25), (28, 18), (36, 18), (47, 27),
                   (53, 39), (54, 49), (49, 54), (16, 54)], "#289a98")
    draw.rectangle((14, 45, 51, 51), fill="#227b82")
    draw.line([(13, 49), (16, 54), (49, 54), (53, 49)], fill=INK, width=2)
    ellipse(draw, (20, 31, 27, 39), "#d8fbef", 1)
    ellipse(draw, (38, 31, 45, 39), "#d8fbef", 1)
    draw.rectangle((23, 34, 25, 38), fill="#173246")
    draw.rectangle((40, 34, 42, 38), fill="#173246")
    draw.line((28, 44, 32, 46, 37, 43), fill="#15384b", width=2)
    draw.rectangle((20, 24, 26, 27), fill="#54cbb9")
    draw.rectangle((16, 29, 20, 35), fill="#54cbb9")
    draw.rectangle((24, 21, 31, 23), fill="#8be4ce")
    draw.rectangle((46, 40, 50, 45), fill="#52c6b7")
    save(image, "slime.png")


def goblin():
    image, draw = canvas()
    # Oversized ears, crooked posture, scavenged armor, and a chipped dagger.
    polygon(draw, [(8, 23), (20, 25), (19, 36)], "#668e42")
    polygon(draw, [(56, 22), (44, 26), (45, 36)], "#668e42")
    ellipse(draw, (17, 17, 47, 43), "#759e48")
    polygon(draw, [(20, 20), (27, 12), (29, 20)], "#4e7339")
    polygon(draw, [(37, 19), (43, 12), (45, 23)], "#4e7339")
    draw.rectangle((22, 26, 28, 31), fill="#e1d56a")
    draw.rectangle((38, 26, 44, 31), fill="#e1d56a")
    draw.rectangle((25, 28, 28, 31), fill="#452332")
    draw.rectangle((38, 28, 41, 31), fill="#452332")
    polygon(draw, [(29, 30), (35, 27), (36, 35)], "#587b3b", 1)
    draw.line((26, 37, 32, 39, 40, 36), fill="#442635", width=2)
    draw.rectangle((29, 38, 32, 41), fill="#e7d9a7")
    draw.rectangle((36, 37, 39, 40), fill="#e7d9a7")
    polygon(draw, [(19, 41), (28, 37), (41, 39), (48, 53), (16, 53)], "#684334")
    draw.line((28, 40, 36, 52), fill="#ba873e", width=3)
    draw.rectangle((20, 52, 29, 57), fill="#49312d", outline=INK, width=2)
    draw.rectangle((39, 52, 49, 57), fill="#49312d", outline=INK, width=2)
    polygon(draw, [(47, 40), (55, 31), (58, 32), (52, 45)], "#a9b5b2", 1)
    draw.rectangle((47, 42, 55, 45), fill="#a76536", outline=INK, width=1)
    save(image, "goblin.png")


def skeleton():
    image, draw = canvas()
    # Ancient warrior with a cracked skull, violet burial cloth, and bone limbs.
    polygon(draw, [(18, 24), (13, 33), (17, 50), (25, 53), (29, 36)], "#4d365f")
    polygon(draw, [(46, 24), (52, 34), (48, 51), (39, 54), (35, 36)], "#4d365f")
    ellipse(draw, (20, 9, 45, 33), "#d7d0b6")
    draw.rectangle((22, 23, 43, 31), fill="#c3b99e")
    polygon(draw, [(22, 13), (26, 9), (29, 14), (34, 9), (43, 13), (45, 23),
                   (40, 31), (25, 30), (20, 22)], "#d7d0b6", 1)
    polygon(draw, [(24, 18), (30, 16), (30, 23), (25, 24)], "#2a2233", 1)
    polygon(draw, [(35, 16), (42, 18), (40, 24), (34, 23)], "#2a2233", 1)
    draw.rectangle((31, 23, 35, 27), fill="#2a2233")
    draw.line((28, 29, 31, 27, 34, 30, 37, 27, 40, 30), fill="#786f64", width=1)
    draw.line((35, 10, 33, 15, 37, 18, 34, 22), fill="#796f64", width=1)
    draw.rectangle((27, 32, 39, 49), fill="#bfb69e", outline=INK, width=2)
    for y in (36, 41, 46):
        draw.line((28, y, 38, y), fill="#7a7367", width=1)
    draw.line((24, 34, 18, 50), fill="#d7d0b6", width=4)
    draw.line((42, 34, 48, 49), fill="#d7d0b6", width=4)
    draw.line((30, 49, 25, 58), fill="#d7d0b6", width=4)
    draw.line((37, 49, 43, 58), fill="#d7d0b6", width=4)
    draw.line((21, 38, 49, 57), fill=INK, width=3)
    draw.line((22, 37, 50, 56), fill="#aab5bd", width=1)
    save(image, "skeleton.png")


def demon_king():
    image, draw = canvas()
    # Primordial void-fire and a huge silhouette make the boss visually dominant.
    for x, y, color in [(7, 17, "#7b2cc4"), (55, 18, "#b13a42"), (9, 40, "#3f46af"), (54, 42, "#7f275e")]:
        polygon(draw, [(x, y + 7), (x - 3, y + 2), (x, y - 5), (x + 2, y), (x + 5, y - 8),
                       (x + 6, y + 5)], color, 1)
    polygon(draw, [(26, 24), (15, 17), (4, 6), (9, 21), (20, 31)], "#33213e")
    polygon(draw, [(38, 24), (49, 16), (60, 5), (55, 22), (44, 32)], "#33213e")
    draw.line((7, 8, 22, 29), fill="#6f3c78", width=2)
    draw.line((58, 8, 42, 29), fill="#6f3c78", width=2)
    polygon(draw, [(25, 19), (18, 9), (14, 4), (16, 17), (22, 27)], "#60405e")
    polygon(draw, [(39, 19), (46, 9), (50, 4), (48, 18), (42, 27)], "#60405e")
    polygon(draw, [(23, 12), (27, 6), (32, 12), (37, 6), (42, 13), (39, 20), (25, 20)], "#9b693a", 1)
    ellipse(draw, (20, 15, 44, 38), "#35243f")
    polygon(draw, [(22, 19), (30, 16), (32, 20), (41, 17), (43, 28), (38, 36),
                   (27, 36), (20, 28)], "#442b4d", 1)
    polygon(draw, [(23, 23), (30, 21), (29, 27), (23, 27)], "#ff6b3d", 1)
    polygon(draw, [(35, 21), (42, 23), (41, 27), (35, 27)], "#ff6b3d", 1)
    draw.rectangle((25, 24, 29, 25), fill="#ffd36a")
    draw.rectangle((36, 24, 40, 25), fill="#ffd36a")
    polygon(draw, [(27, 32), (32, 29), (38, 32), (35, 38), (30, 38)], "#191522", 1)
    polygon(draw, [(17, 34), (25, 29), (32, 36), (40, 29), (49, 35), (45, 55),
                   (20, 55)], "#292037")
    polygon(draw, [(14, 34), (22, 29), (25, 40), (17, 43)], "#694054")
    polygon(draw, [(50, 34), (42, 29), (39, 40), (47, 43)], "#694054")
    draw.line((24, 38, 20, 54), fill="#a76a3e", width=3)
    draw.line((41, 38, 45, 54), fill="#a76a3e", width=3)
    ellipse(draw, (27, 37, 38, 49), "#c43b4d", 1)
    ellipse(draw, (30, 40, 35, 46), "#ffb13b", 1)
    draw.line((32, 37, 32, 49), fill="#ffe48b", width=1)
    polygon(draw, [(20, 52), (29, 51), (28, 60), (15, 60)], "#211a2c")
    polygon(draw, [(36, 51), (45, 52), (50, 60), (36, 60)], "#211a2c")
    draw.rectangle((15, 58, 29, 61), fill="#503142", outline=INK, width=1)
    draw.rectangle((36, 58, 51, 61), fill="#503142", outline=INK, width=1)
    draw.line((32, 12, 32, 57), fill="#9d5e8e", width=1)
    save(image, "demon-king-koji.png")


def tideheart_behemoth():
    image, draw = canvas()
    # A colossal royal slime with a luminous tidal core and broken crown.
    polygon(draw, [(5, 53), (8, 37), (16, 23), (27, 15), (39, 16), (51, 26),
                   (58, 42), (57, 54), (50, 59), (13, 59)], "#176f86")
    polygon(draw, [(10, 49), (14, 34), (25, 23), (39, 22), (51, 35), (54, 50)], "#269eaa", 1)
    draw.rectangle((11, 51, 54, 57), fill="#14566d")
    ellipse(draw, (20, 31, 28, 40), "#d9ffff", 1)
    ellipse(draw, (39, 31, 47, 40), "#d9ffff", 1)
    draw.rectangle((23, 34, 26, 39), fill="#14334c")
    draw.rectangle((41, 34, 44, 39), fill="#14334c")
    ellipse(draw, (27, 38, 41, 52), "#56297a", 2)
    ellipse(draw, (30, 41, 38, 49), "#b26cff", 1)
    draw.line((32, 42, 36, 48), fill="#f0dcff", width=2)
    polygon(draw, [(21, 20), (23, 9), (29, 16), (34, 6), (39, 16), (47, 10),
                   (45, 23)], "#d29b36")
    draw.rectangle((23, 19, 45, 23), fill="#9f6728", outline=INK, width=2)
    draw.rectangle((13, 31, 18, 38), fill="#66d4d1")
    draw.rectangle((48, 40, 54, 47), fill="#66d4d1")
    draw.line((23, 47, 28, 51, 33, 48), fill="#103d55", width=2)
    save(image, "tideheart-behemoth.png")


def thornlord_grak():
    image, draw = canvas()
    # An elder goblin champion in living briar armor with a crescent cleaver.
    polygon(draw, [(13, 21), (4, 11), (18, 16), (21, 28)], "#446a32")
    polygon(draw, [(49, 21), (60, 10), (46, 16), (43, 29)], "#446a32")
    ellipse(draw, (16, 14, 48, 43), "#587f39")
    polygon(draw, [(18, 17), (22, 6), (27, 16), (32, 5), (38, 16), (45, 7),
                   (46, 23)], "#4f392d")
    draw.line((21, 14, 17, 5, 13, 2), fill="#87512d", width=3)
    draw.line((41, 14, 46, 5, 51, 2), fill="#87512d", width=3)
    polygon(draw, [(20, 25), (28, 21), (29, 29), (21, 30)], "#e6c34f", 1)
    polygon(draw, [(35, 21), (44, 25), (43, 30), (35, 29)], "#e6c34f", 1)
    draw.rectangle((25, 25, 28, 28), fill="#5b1f2d")
    draw.rectangle((36, 25, 39, 28), fill="#5b1f2d")
    draw.line((24, 36, 31, 39, 41, 34), fill="#331e27", width=2)
    draw.rectangle((27, 38, 31, 42), fill="#e6d8aa")
    draw.rectangle((36, 37, 40, 41), fill="#e6d8aa")
    polygon(draw, [(15, 40), (24, 34), (33, 39), (42, 34), (51, 42), (47, 59),
                   (17, 59)], "#405a2f")
    for x, y in ((18, 42), (25, 37), (43, 39), (49, 45), (22, 53)):
        polygon(draw, [(x, y), (x + 3, y - 5), (x + 5, y + 1)], "#7b9b3b", 1)
    draw.line((43, 42, 55, 55), fill="#75452c", width=4)
    polygon(draw, [(48, 35), (57, 27), (61, 29), (58, 42), (52, 48), (46, 45),
                   (52, 41)], "#b9c0b0", 1)
    draw.rectangle((19, 56, 30, 62), fill="#352823", outline=INK, width=2)
    draw.rectangle((39, 56, 50, 62), fill="#352823", outline=INK, width=2)
    save(image, "thornlord-grak.png")


def ashen_bonewyrm():
    image, draw = canvas()
    # A coiled skeletal wyrm crowned with crypt fire.
    for x, y in ((10, 14), (52, 12), (7, 43), (55, 45)):
        polygon(draw, [(x, y + 8), (x - 3, y + 2), (x, y - 5), (x + 4, y + 1),
                       (x + 6, y - 6), (x + 7, y + 7)], "#7246a8", 1)
    draw.arc((9, 27, 55, 62), 15, 315, fill=INK, width=10)
    draw.arc((9, 27, 55, 62), 15, 315, fill="#c9c0a6", width=6)
    for x, y in ((17, 50), (24, 56), (35, 56), (44, 49)):
        draw.line((x, y, x - 3, y + 6), fill="#827968", width=2)
    polygon(draw, [(19, 12), (25, 6), (38, 7), (47, 15), (44, 29), (35, 36),
                   (22, 31), (16, 23)], "#d8d0b6")
    polygon(draw, [(18, 15), (11, 9), (16, 22), (22, 26)], "#aaa18b")
    polygon(draw, [(44, 15), (52, 9), (47, 24), (42, 27)], "#aaa18b")
    polygon(draw, [(21, 17), (29, 14), (29, 22), (22, 23)], "#2d2435", 1)
    polygon(draw, [(34, 14), (42, 18), (40, 24), (33, 22)], "#2d2435", 1)
    draw.rectangle((24, 18, 28, 21), fill="#bd6cff")
    draw.rectangle((35, 18, 39, 21), fill="#bd6cff")
    polygon(draw, [(24, 28), (31, 25), (41, 28), (37, 36), (27, 34)], "#b8ae96", 1)
    draw.line((27, 30, 39, 30), fill="#5e5660", width=1)
    for x in (28, 32, 36):
        draw.line((x, 30, x + 1, 34), fill="#5e5660", width=1)
    polygon(draw, [(19, 11), (23, 1), (29, 9), (34, 0), (38, 10), (44, 3),
                   (45, 15)], "#574060", 1)
    save(image, "ashen-bonewyrm.png")


if __name__ == "__main__":
    slime()
    goblin()
    skeleton()
    demon_king()
    tideheart_behemoth()
    thornlord_grak()
    ashen_bonewyrm()
    print(f"Generated monster sprites in {OUT_DIR}")
