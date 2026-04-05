from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "profile-banner-ocean.gif"
LINKEDIN_CHIP = ROOT / "assets" / "contact-linkedin.png"
EMAIL_CHIP = ROOT / "assets" / "contact-email.png"
GMAIL_ICON_SOURCE = ROOT / "assets" / "gmail-icon-source.png"

WIDTH = 1280
HEIGHT = 420
FRAMES = 24
FPS_MS = 90

TITLE = "Oi, eu sou o Lucas Gabriel"
SUBTITLE = "Aqui compartilho projetos, estudos e experimentos que estou construindo."

PANEL_BOX = (24, 24, WIDTH - 24, HEIGHT - 24)


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


TITLE_FONT = load_font(58, bold=True)
BODY_FONT = load_font(24, bold=False)
CHIP_FONT = load_font(19, bold=True)
ICON_FONT = load_font(18, bold=True)


def lerp_color(start: tuple[int, int, int], end: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(start[i] + (end[i] - start[i]) * t) for i in range(3))


def make_base_panel() -> Image.Image:
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))

    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((34, 30, WIDTH - 16, HEIGHT - 14), radius=42, fill=(0, 0, 0, 78))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    canvas = Image.alpha_composite(canvas, shadow)

    panel = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gradient = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient)
    top = (17, 68, 95)
    bottom = (8, 35, 54)
    left, upper, right, lower = PANEL_BOX
    inner_height = lower - upper

    for step in range(inner_height):
        mix = step / max(inner_height - 1, 1)
        row = lerp_color(top, bottom, mix)
        gradient_draw.rounded_rectangle(
            (left, upper + step, right, upper + step + 1),
            radius=44,
            fill=(*row, 255),
        )

    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(PANEL_BOX, radius=44, fill=255)
    panel = Image.composite(gradient, Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)), mask)
    return Image.alpha_composite(canvas, panel)


def draw_multiline_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    x: int,
    y: int,
    max_width: int,
    line_gap: int,
) -> int:
    words = text.split()
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        attempt = f"{current} {word}"
        if draw.textlength(attempt, font=font) <= max_width:
            current = attempt
        else:
            lines.append(current)
            current = word
    lines.append(current)

    for index, line in enumerate(lines):
        draw.text((x, y + index * line_gap), line, font=font, fill=fill)
    return y + len(lines) * line_gap


def draw_wave(draw: ImageDraw.ImageDraw, index: int) -> None:
    phase = (index / FRAMES) * math.tau
    offset_x = math.sin(phase) * 9
    offset_y = math.sin(phase * 0.65) * 2
    draw.ellipse(
        (-120 + offset_x, 350 + offset_y, WIDTH + 120 + offset_x, 406 + offset_y),
        fill=(92, 206, 232, 52),
    )


def build_frame(index: int) -> Image.Image:
    frame = make_base_panel()
    draw = ImageDraw.Draw(frame, "RGBA")

    draw.text((82, 138), TITLE, font=TITLE_FONT, fill=(248, 252, 255, 255))
    draw_multiline_text(
        draw,
        text=SUBTITLE,
        font=BODY_FONT,
        fill=(230, 245, 252, 228),
        x=82,
        y=220,
        max_width=640,
        line_gap=32,
    )

    draw_wave(draw, index)

    return frame.convert("P", palette=Image.Palette.ADAPTIVE)


def make_chip_base(width: int = 196, height: int = 58) -> Image.Image:
    chip = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    body_draw = ImageDraw.Draw(chip)
    body_draw.rounded_rectangle((1, 1, width - 2, height - 2), radius=20, fill=(9, 36, 54, 255), outline=(104, 196, 224, 88), width=1)
    return chip


def save_linkedin_chip() -> None:
    image = make_chip_base()
    draw = ImageDraw.Draw(image, "RGBA")

    tile_box = (14, 13, 44, 43)
    draw.rounded_rectangle(tile_box, radius=8, fill=(10, 102, 194, 255))
    draw.text((21, 18), "in", font=ICON_FONT, fill=(255, 255, 255, 255))
    draw.text((57, 17), "LinkedIn", font=CHIP_FONT, fill=(241, 250, 255, 248))

    LINKEDIN_CHIP.parent.mkdir(parents=True, exist_ok=True)
    image.save(LINKEDIN_CHIP)


def save_email_chip() -> None:
    image = make_chip_base()
    draw = ImageDraw.Draw(image, "RGBA")

    gmail_mark = Image.open(GMAIL_ICON_SOURCE).convert("RGBA")
    gmail_mark.thumbnail((28, 22), Image.Resampling.LANCZOS)
    mark_x = 14
    mark_y = 18
    image.alpha_composite(gmail_mark, (mark_x, mark_y))
    draw.text((50, 17), "Gmail", font=CHIP_FONT, fill=(241, 250, 255, 248))

    EMAIL_CHIP.parent.mkdir(parents=True, exist_ok=True)
    image.save(EMAIL_CHIP)


def main() -> None:
    frames = [build_frame(index) for index in range(FRAMES)]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=FPS_MS,
        loop=0,
        disposal=2,
        optimize=False,
        transparency=0,
    )
    save_linkedin_chip()
    save_email_chip()
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
