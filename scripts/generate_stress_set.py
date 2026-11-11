from __future__ import annotations

import argparse
import csv
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create labeled synthetic brightness variants from an image folder.")
    parser.add_argument("--images", required=True, help="Source image folder")
    parser.add_argument("--annotations", required=True, help="CSV with image_id,target_present")
    parser.add_argument("--out", default="stress_images")
    args = parser.parse_args()
    try:
        from PIL import Image, ImageDraw, ImageEnhance
    except ImportError as exc:
        raise SystemExit("Install Pillow first: pip install '.[augment]'") from exc

    source_dir, out_dir = Path(args.images), Path(args.out)
    with Path(args.annotations).open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not {"image_id", "target_present"}.issubset(reader.fieldnames or []):
            parser.error("annotation CSV must contain image_id,target_present columns")
        labels = {row["image_id"]: row["target_present"] for row in reader}
    conditions = [("dim_30", 0.3), ("dim_60", 0.6), ("normal", 1.0), ("bright_160", 1.6)]
    output_rows: list[dict[str, str]] = []
    for image_id, target_present in sorted(labels.items()):
        path = source_dir / image_id
        if path.suffix.lower() not in IMAGE_SUFFIXES or not path.is_file():
            parser.error(f"supported image not found: {path}")
        with Image.open(path) as original:
            original = original.convert("RGB")
            for condition, factor in conditions:
                variant = ImageEnhance.Brightness(original).enhance(factor)
                relative = Path(condition) / path.name
                target = out_dir / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                variant.save(target)
                output_rows.append({"image_id": str(relative), "condition": condition, "illuminance_lux": "NA", "target_present": target_present})
            glare = ImageEnhance.Brightness(original).enhance(1.15)
            overlay = Image.new("RGBA", glare.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            width, height = glare.size
            draw.ellipse((width * 0.48, -height * 0.15, width * 1.15, height * 0.52), fill=(255, 255, 255, 155))
            glare = Image.alpha_composite(glare.convert("RGBA"), overlay).convert("RGB")
            relative = Path("synthetic_glare") / path.name
            target = out_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            glare.save(target)
            output_rows.append({"image_id": str(relative), "condition": "synthetic_glare", "illuminance_lux": "NA", "target_present": target_present})
    with (out_dir / "annotations.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["image_id", "condition", "illuminance_lux", "target_present"])
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Created {len(output_rows)} synthetic images and {out_dir / 'annotations.csv'}")


if __name__ == "__main__":
    main()

