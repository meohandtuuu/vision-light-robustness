from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .evaluate import evaluate_rows, load_rows
from .plot import write_recall_svg


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate detector predictions by lighting condition.")
    parser.add_argument("--input", required=True, help="Prediction CSV")
    parser.add_argument("--out", default="results", help="Output directory")
    args = parser.parse_args()
    rows = load_rows(Path(args.input))
    report = evaluate_rows(rows)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    with (out_dir / "condition_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        columns = ["condition", "images", "target_images", "true_positives", "false_positives", "false_negatives", "true_negatives", "recall", "precision", "false_positive_rate", "mean_confidence", "median_illuminance_lux"]
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(report["conditions"])
    write_recall_svg(report["conditions"], out_dir / "recall.svg")
    print(f"Evaluated {report['total_images']} images across {len(report['conditions'])} conditions.")
    for item in report["conditions"]:
        print(f"{item['condition']:<16} n={item['images']:>4} recall={item['recall']} precision={item['precision']} FPR={item['false_positive_rate']}")
    print("Reminder: results only describe the input CSV. Check its evidence source before publishing claims.")


if __name__ == "__main__":
    main()

