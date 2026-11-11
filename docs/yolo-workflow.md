# Optional Ultralytics workflow

The core evaluator is dependency-free. To generate predictions from your own images, install Ultralytics separately and provide a compatible model file.

## Annotation CSV

Create `annotations.csv` with columns:

```csv
image_id,condition,illuminance_lux,target_present
desk-001.jpg,normal,520,1
desk-002.jpg,glare,2400,1
```

`target_present` records whether the target class is truly present in that image. Use one row for every image, including images without the target.

## Run inference

```bash
python scripts/run_yolo.py --model path/to/best.pt --images path/to/images --annotations annotations.csv --target-class-ids 0 --out predictions.csv
python -m vision_stress_lab --input predictions.csv --out results
```

The script records whether any selected target class was detected and its highest confidence. It does not calculate bounding-box localization quality. Keep the model name, model file hash, confidence threshold, image source, camera settings, lux measurement method, and labels with any report you publish.

## Evidence discipline

The bundled demo CSV is hand-authored solely to demonstrate the report format. It is not a model run. Do not cite it as detector performance.

