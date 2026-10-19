"""Generates the site icons in public/: a white serif "B" on the schutterij red.

Usage: python scripts/make_favicon.py [path-to-bold-serif.ttf]
(defaults to Georgia Bold on Windows; needs Pillow)
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOD = (163, 23, 28)  # --rood in src/styles/global.css
PUBLIC = Path(__file__).resolve().parents[1] / "public"
FONT = sys.argv[1] if len(sys.argv) > 1 else r"C:\Windows\Fonts\georgiab.ttf"


def icon(size: int, radius: float) -> Image.Image:
    scale = 4  # draw large, downsample for smooth edges
    s = size * scale
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, s - 1, s - 1), radius=int(s * radius), fill=ROOD)
    font = ImageFont.truetype(FONT, int(s * 0.78))
    l, t, r, b = d.textbbox((0, 0), "B", font=font)
    d.text(((s - (r - l)) / 2 - l, (s - (b - t)) / 2 - t), "B", font=font, fill="white")
    return im.resize((size, size), Image.LANCZOS)


def main():
    icon(48, 0.18).save(PUBLIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    icon(192, 0.18).save(PUBLIC / "icon-192.png", optimize=True)
    # iOS applies its own rounded mask, so the touch icon is a full square.
    icon(180, 0).convert("RGB").save(PUBLIC / "apple-touch-icon.png", optimize=True)


if __name__ == "__main__":
    main()
