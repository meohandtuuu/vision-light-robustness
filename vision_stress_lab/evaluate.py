from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

REQUIRED = {"image_id", "condition", "illuminance_lux", "target_present", "predicted_present", "confidence"}


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    if not rows:
        raise ValueError("Input CSV has no prediction rows")
    for line, row in enumerate(rows, start=2):
        for key in ("target_present", "predicted_present"):
            if row[key].strip() not in {"0", "1"}:
                raise ValueError(f"Line {line}: {key} must be 0 or 1")
        confidence = float(row["confidence"])
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Line {line}: confidence must be between 0 and 1")
        row["confidence"] = str(confidence)
        row["condition"] = row["condition"].strip() or "unspecified"
    return rows


def evaluate_rows(rows: list[dict[str, str]]) -> dict[str, object]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["condition"]].append(row)
    conditions = [_metrics(name, group) for name, group in sorted(groups.items())]
    return {
        "evidence_type": "prediction_csv_evaluation",
        "task": "image_level_target_presence",
        "total_images": len(rows),
        "conditions": conditions,
        "metric_notes": {
            "recall": "true positives / target-present images; null when no target is present",
            "precision": "true positives / predicted-positive images; null when there are no positive predictions",
            "false_positive_rate": "false positives / target-absent images; null when no target-absent image exists",
            "confidence": "mean supplied confidence across all images, including zero for no detection if that is how the CSV was recorded",
        },
    }


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def _metrics(condition: str, rows: list[dict[str, str]]) -> dict[str, object]:
    tp = fp = fn = tn = targets = 0
    for row in rows:
        target, predicted = int(row["target_present"]), int(row["predicted_present"])
        targets += target
        if target and predicted:
            tp += 1
        elif not target and predicted:
            fp += 1
        elif target and not predicted:
            fn += 1
        else:
            tn += 1
    confidence = sum(float(row["confidence"]) for row in rows) / len(rows)
    return {
        "condition": condition,
        "images": len(rows),
        "target_images": targets,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "recall": _ratio(tp, tp + fn),
        "precision": _ratio(tp, tp + fp),
        "false_positive_rate": _ratio(fp, fp + tn),
        "mean_confidence": round(confidence, 6),
        "median_illuminance_lux": _median_lux(rows),
    }


def _median_lux(rows: list[dict[str, str]]) -> float | None:
    values = sorted(float(row["illuminance_lux"]) for row in rows if row["illuminance_lux"].strip().upper() not in {"", "NA", "N/A"})
    if not values:
        return None
    middle = len(values) // 2
    return values[middle] if len(values) % 2 else round((values[middle - 1] + values[middle]) / 2, 3)

