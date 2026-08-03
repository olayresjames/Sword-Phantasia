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


if __name__ == "__main__":
    slime()
    goblin()
    skeleton()
    demon_king()
    print(f"Generated monster sprites in {OUT_DIR}")
