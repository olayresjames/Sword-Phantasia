"""Generate Sword Phantasia environment art without external services.

The scenes intentionally use a limited pixel-art palette so they sit beside the
existing character and monster sprites.  Run this file whenever the assets need
to be regenerated; Pillow is only required for generation, not while playing.
"""

from pathlib import Path
import random

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "environments"
WIDTH, HEIGHT = 960, 360


PALETTES = {
    "frontier": ("#101a2b", "#243657", "#647899", "#1b2b35", "#314a46", "#88a36a"),
    "mosswood": ("#08151a", "#15322e", "#31594a", "#101f24", "#1c342d", "#477a4b"),
    "crypt": ("#0d0d17", "#25243a", "#4d4962", "#11131e", "#242738", "#67657a"),
    "throne": ("#100913", "#2b102b", "#61284b", "#110d1a", "#29152c", "#743247"),
}


def gradient(draw, top, bottom):
    def rgb(value):
        value = value.lstrip("#")
        return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))

    start, end = rgb(top), rgb(bottom)
    for y in range(HEIGHT):
        ratio = y / max(1, HEIGHT - 1)
        color = tuple(round(start[channel] * (1 - ratio) + end[channel] * ratio) for channel in range(3))
        draw.line((0, y, WIDTH, y), fill=color)


def stars(draw, rng, color, count=65):
    for _ in range(count):
        x, y = rng.randrange(WIDTH), rng.randrange(12, 190)
        size = 2 if rng.random() > .88 else 1
        draw.rectangle((x, y, x + size, y + size), fill=color)


def frontier(draw, rng, colors):
    _, _, mist, ground, ridge, light = colors
    draw.ellipse((685, 42, 795, 152), fill="#e8d99d")
    draw.ellipse((705, 53, 810, 155), fill=colors[0])
    draw.polygon([(0, 218), (120, 155), (210, 205), (350, 130), (470, 215), (610, 145), (760, 205), (865, 142), (960, 210), (960, 360), (0, 360)], fill="#1c293a")
    draw.polygon([(0, 250), (125, 220), (240, 250), (410, 203), (570, 250), (720, 216), (960, 246), (960, 360), (0, 360)], fill=ridge)
    draw.rectangle((0, 260, WIDTH, HEIGHT), fill=ground)
    draw.polygon([(390, 360), (460, 260), (505, 260), (602, 360)], fill="#57556a")
    draw.polygon([(427, 360), (471, 260), (490, 260), (550, 360)], fill="#827b74")
    draw.rectangle((735, 152, 750, 257), fill="#202534")
    draw.rectangle((704, 143, 780, 160), fill="#202534")
    draw.rectangle((716, 116, 768, 151), fill="#202534")
    draw.rectangle((724, 105, 734, 120), fill="#202534")
    draw.rectangle((752, 102, 762, 120), fill="#202534")
    for _ in range(130):
        x, y = rng.randrange(WIDTH), rng.randrange(260, HEIGHT)
        h = rng.randrange(3, 12)
        draw.line((x, y, x + rng.choice((-2, -1, 1, 2)), y - h), fill=rng.choice((light, "#647b58", "#405c4c")), width=1)
    stars(draw, rng, mist, 35)


def mosswood(draw, rng, colors):
    _, _, mist, ground, ridge, light = colors
    draw.ellipse((425, 45, 545, 165), fill="#96bed0")
    stars(draw, rng, mist, 45)
    for x, width, height in ((20, 105, 305), (150, 70, 260), (760, 90, 290), (885, 105, 315)):
        draw.rectangle((x, HEIGHT - height, x + width, HEIGHT), fill="#091419")
        for branch_y in (100, 155, 210):
            direction = 1 if x < WIDTH / 2 else -1
            draw.polygon([(x + width // 2, branch_y), (x + width // 2 + direction * 155, branch_y - 55), (x + width // 2 + direction * 130, branch_y - 35), (x + width // 2, branch_y + 20)], fill="#091419")
    draw.polygon([(0, 250), (130, 220), (260, 252), (420, 205), (590, 250), (760, 212), (960, 245), (960, 360), (0, 360)], fill=ridge)
    draw.rectangle((0, 266, WIDTH, HEIGHT), fill=ground)
    draw.polygon([(392, 360), (452, 266), (502, 266), (575, 360)], fill="#263b35")
    for _ in range(75):
        x, y = rng.randrange(WIDTH), rng.randrange(245, HEIGHT)
        if rng.random() < .18:
            draw.rectangle((x, y - 4, x + 2, y), fill="#a8d5d2")
            draw.ellipse((x - 3, y - 8, x + 5, y - 4), fill="#64a9a0")
        else:
            draw.line((x, y, x, y - rng.randrange(3, 10)), fill=rng.choice((light, "#335b42", "#203f35")))


def crypt(draw, rng, colors):
    _, _, mist, ground, ridge, light = colors
    stars(draw, rng, mist, 24)
    draw.rectangle((0, 235, WIDTH, HEIGHT), fill=ground)
    for x in range(0, WIDTH, 120):
        draw.rectangle((x + 20, 105, x + 96, 275), fill="#151725")
        draw.ellipse((x + 20, 65, x + 96, 145), fill="#151725")
        draw.rectangle((x + 38, 125, x + 78, 275), fill="#080a11")
        draw.ellipse((x + 38, 92, x + 78, 160), fill="#080a11")
        draw.line((x + 18, 104, x + 98, 104), fill="#39394c", width=3)
    draw.polygon([(360, 360), (430, 238), (512, 238), (610, 360)], fill="#353646")
    for y in range(258, 360, 20):
        inset = (y - 258) // 2
        draw.line((420 - inset, y, 535 + inset, y), fill="#565568", width=2)
    for x in (280, 665):
        draw.rectangle((x, 170, x + 9, 278), fill="#5d493c")
        draw.polygon([(x - 8, 175), (x + 5, 145), (x + 17, 175)], fill="#95704b")
        draw.polygon([(x - 2, 168), (x + 5, 148), (x + 12, 168), (x + 5, 184)], fill="#9b68d1")
    for _ in range(55):
        x, y = rng.randrange(WIDTH), rng.randrange(245, HEIGHT)
        draw.rectangle((x, y, x + rng.randrange(2, 9), y + 2), fill=rng.choice((ridge, light, "#46475a")))


def throne(draw, rng, colors):
    _, _, mist, ground, ridge, light = colors
    stars(draw, rng, mist, 80)
    draw.ellipse((395, 45, 565, 215), outline="#9e3d74", width=5)
    draw.ellipse((420, 70, 540, 190), outline="#57214c", width=3)
    for x in (80, 230, 700, 850):
        draw.polygon([(x, 360), (x + 22, 92), (x + 58, 92), (x + 80, 360)], fill="#120d18")
        draw.polygon([(x + 8, 98), (x + 40, 42), (x + 72, 98)], fill="#251123")
    draw.polygon([(0, 270), (180, 235), (355, 272), (490, 220), (660, 270), (820, 230), (960, 265), (960, 360), (0, 360)], fill=ridge)
    draw.rectangle((0, 282, WIDTH, HEIGHT), fill=ground)
    draw.polygon([(345, 360), (425, 282), (535, 282), (625, 360)], fill="#31192d")
    for x in (145, 790):
        draw.polygon([(x, 280), (x + 18, 230), (x + 10, 195), (x + 30, 220), (x + 42, 182), (x + 50, 232), (x + 68, 280)], fill="#a43a4d")
        draw.polygon([(x + 20, 250), (x + 36, 205), (x + 50, 252), (x + 36, 270)], fill="#ff8b3e")
    for _ in range(45):
        x, y = rng.randrange(WIDTH), rng.randrange(245, HEIGHT)
        draw.line((x, y, x + rng.randrange(-9, 10), y - rng.randrange(4, 18)), fill=rng.choice((light, "#a44355", "#4c263e")))


SCENE_DRAWERS = {"frontier": frontier, "mosswood": mosswood, "crypt": crypt, "throne": throne}


def generate_title_scene():
    """Create a square key-art panel with room for the game title."""
    size = 600
    image = Image.new("RGB", (size, size), "#090d18")
    draw = ImageDraw.Draw(image)
    for y in range(size):
        ratio = y / (size - 1)
        start, end = (9, 13, 24), (42, 16, 43)
        color = tuple(round(start[i] * (1 - ratio) + end[i] * ratio) for i in range(3))
        draw.line((0, y, size, y), fill=color)
    rng = random.Random("sword-phantasia")
    for _ in range(95):
        x, y = rng.randrange(size), rng.randrange(20, 375)
        draw.rectangle((x, y, x + 1, y + 1), fill=rng.choice(("#485879", "#7b6792", "#9f6f8e")))
    draw.ellipse((388, 55, 520, 187), fill="#d8bd72")
    draw.ellipse((416, 42, 538, 180), fill="#0d1120")
    draw.polygon([(0, 410), (105, 315), (206, 390), (310, 275), (426, 386), (530, 300), (600, 360), (600, 600), (0, 600)], fill="#111729")
    draw.polygon([(0, 455), (145, 398), (255, 446), (405, 365), (600, 445), (600, 600), (0, 600)], fill="#17172a")
    draw.polygon([(245, 600), (292, 415), (333, 415), (392, 600)], fill="#38263b")
    draw.polygon([(284, 600), (305, 415), (322, 415), (351, 600)], fill="#6f4a52")
    # The distant primordial king forms a clear antagonist silhouette.
    draw.polygon([(285, 385), (263, 326), (225, 285), (260, 300), (285, 335)], fill="#171323")
    draw.polygon([(339, 385), (361, 326), (402, 283), (363, 301), (338, 335)], fill="#171323")
    draw.polygon([(285, 325), (295, 280), (313, 299), (332, 278), (341, 326)], fill="#171323")
    draw.ellipse((282, 305, 344, 373), fill="#171323")
    draw.rectangle((276, 355, 350, 432), fill="#171323")
    draw.rectangle((299, 327, 310, 334), fill="#ff6c45")
    draw.rectangle((319, 327, 330, 334), fill="#ff6c45")
    draw.ellipse((304, 375, 325, 397), fill="#c13e5c")
    draw.ellipse((310, 381, 319, 391), fill="#ffc55c")
    # Foreground blades hint at the three playable paths without crowding the logo.
    draw.polygon([(82, 600), (111, 452), (121, 450), (110, 600)], fill="#c7d1dc")
    draw.polygon([(102, 477), (128, 465), (130, 476), (106, 488)], fill="#8c5d48")
    draw.line((506, 600, 473, 455), fill="#bac7d1", width=8)
    draw.line((469, 455, 498, 442), fill="#6f4c3d", width=8)
    draw.arc((454, 430, 540, 590), 100, 260, fill="#9db9ca", width=7)
    image = image.resize((300, 300), Image.Resampling.NEAREST).resize((600, 600), Image.Resampling.NEAREST)
    image.save(OUT_DIR / "title.png", optimize=True)


def generate_scene(key):
    rng = random.Random(key)
    image = Image.new("RGB", (WIDTH, HEIGHT), PALETTES[key][0])
    draw = ImageDraw.Draw(image)
    gradient(draw, PALETTES[key][0], PALETTES[key][1])
    SCENE_DRAWERS[key](draw, rng, PALETTES[key])
    # Pixel-art color unification and a crisp 2x upscale.
    image = image.resize((WIDTH // 2, HEIGHT // 2), Image.Resampling.NEAREST)
    image = image.resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image.save(OUT_DIR / f"{key}.png", optimize=True)


if __name__ == "__main__":
    for scene_key in PALETTES:
        generate_scene(scene_key)
    generate_title_scene()
    print(f"Generated environment art in {OUT_DIR}")
