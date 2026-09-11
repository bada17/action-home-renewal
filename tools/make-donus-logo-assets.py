"""Create exact-size DONUS logo assets from the official transparent PNG."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def fit_on_transparent_canvas(
    source: Image.Image,
    size: tuple[int, int],
    margin: tuple[int, int],
) -> Image.Image:
    """Resize ``source`` proportionally and center it on a transparent canvas."""

    canvas_width, canvas_height = size
    margin_x, margin_y = margin
    max_width = canvas_width - margin_x * 2
    max_height = canvas_height - margin_y * 2

    scale = min(max_width / source.width, max_height / source.height)
    target_size = (
        max(1, round(source.width * scale)),
        max(1, round(source.height * scale)),
    )
    resized = source.resize(target_size, Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    position = (
        (canvas_width - resized.width) // 2,
        (canvas_height - resized.height) // 2,
    )
    canvas.alpha_composite(resized, position)
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    source = Image.open(args.source).convert("RGBA")
    logo_bbox = source.getbbox()
    if logo_bbox is None:
        raise ValueError("The source image has no visible pixels.")
    logo = source.crop(logo_bbox)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "donus-logo-pc-200x66.png": fit_on_transparent_canvas(
            logo, (200, 66), (2, 2)
        ),
        "donus-logo-mobile-300x120.png": fit_on_transparent_canvas(
            logo, (300, 120), (2, 2)
        ),
        "donus-favicon-16x16.png": fit_on_transparent_canvas(
            logo, (16, 16), (0, 0)
        ),
    }

    for filename, image in outputs.items():
        output_path = args.output_dir / filename
        image.save(output_path, format="PNG", optimize=True)
        print(f"{output_path}\t{image.width}x{image.height}\tRGBA")


if __name__ == "__main__":
    main()
