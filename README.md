# Vision Light Robustness

[中文说明](README.zh-CN.md)

Measure where an object detector starts missing a target as image brightness changes.

This repository provides a small, reproducible evaluation pipeline. Its included CSV is **illustrative demo data**, not a benchmark result. Use your own labeled images and detector outputs before making performance claims.

## Quick start

```bash
python -m vision_stress_lab --input examples/demo_predictions.csv --out results
```

This writes a per-condition `summary.json` and a `recall.svg` plot. The evaluator uses Python's standard library. Each input row represents one image-level target-presence decision.

## Input format

Required columns: `image_id,condition,illuminance_lux,target_present,predicted_present,confidence`.

- `condition`: e.g. `normal`, `dim`, `bright`, or `glare`
- `illuminance_lux`: measured with a lux meter where possible; use `NA` when unavailable
- `target_present` and `predicted_present`: `0` or `1`
- `confidence`: maximum target-class confidence, or `0` when the target was not detected

## Workflow

1. Capture the same target under several lighting conditions and label whether it is present in each image.
2. Run the detector and export one row per image using the input schema.
3. Evaluate the predictions and keep the raw CSV beside the generated report.

For an optional Ultralytics YOLOv8/YOLO11 model, install `pip install -e ".[augment]" ultralytics` only if you need image tools, then use `scripts/run_yolo.py` to turn an annotation CSV and image folder into the prediction CSV. See `docs/yolo-workflow.md` for the annotation schema. A compatible model file and your own labeled images are required.

You can create a small **synthetic** brightness stress set from your labeled images with `scripts/generate_stress_set.py` (requires Pillow). Use it to debug the pipeline; label synthetic conditions honestly and confirm any finding under real lighting.

The metric is image-level recall for target presence, plus precision, false-positive rate, and mean confidence. It does not calculate bounding-box mAP. Use a separate detection benchmark if localization accuracy is the research question.

## Limits

Synthetic brightness edits can help debug a pipeline, but they do not replace real lighting tests. Lighting changes can interact with exposure, glare, motion blur, and camera settings. Record those conditions if they matter to your result.

Python 3.10 or later; no third-party packages required for evaluation.

## License

MIT. See `LICENSE`.

