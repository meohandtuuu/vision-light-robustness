from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run optional Ultralytics inference using image-level annotations.")
    parser.add_argument("--model", required=True, help="Ultralytics-compatible model weights")
    parser.add_argument("--images", required=True, help="Directory containing annotated images")
    parser.add_argument("--annotations", required=True, help="CSV with image_id, condition, illuminance_lux, target_present")
    parser.add_argument("--target-class-ids", required=True, help="Comma-separated class IDs to count as the target")
    parser.add_argument("--confidence", type=float, default=0.25)
    parser.add_argument("--out", default="predictions.csv")
    args = parser.parse_args()
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit("Install Ultralytics first: pip install ultralytics") from exc
    if not 0 <= args.confidence <= 1:
        parser.error("--confidence must be between 0 and 1")
    try:
        target_ids = {int(item.strip()) for item in args.target_class_ids.split(",") if item.strip()}
        if not target_ids:
            raise ValueError
    except ValueError:
        parser.error("--target-class-ids must contain one or more integer IDs")

    image_dir = Path(args.images)
    with Path(args.annotations).open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"image_id", "condition", "illuminance_lux", "target_present"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            parser.error(f"annotation CSV missing columns: {', '.join(sorted(missing))}")
        annotations = list(reader)
    model = YOLO(args.model)
    output: list[dict[str, str | int | float]] = []
    for row in annotations:
        image_path = image_dir / row["image_id"]
        if not image_path.is_file():
            parser.error(f"image not found: {image_path}")
        result = model.predict(source=str(image_path), conf=args.confidence, verbose=False)[0]
        hits: list[float] = []
        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls.item())
                confidence = float(box.conf.item())
                if class_id in target_ids:
                    hits.append(confidence)
        output.append({
            "image_id": row["image_id"], "condition": row["condition"],
            "illuminance_lux": row["illuminance_lux"], "target_present": row["target_present"],
            "predicted_present": int(bool(hits)), "confidence": max(hits, default=0.0),
        })
    with Path(args.out).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["image_id", "condition", "illuminance_lux", "target_present", "predicted_present", "confidence"])
        writer.writeheader()
        writer.writerows(output)
    print(f"Wrote {len(output)} predictions to {Path(args.out).resolve()}")


if __name__ == "__main__":
    main()

