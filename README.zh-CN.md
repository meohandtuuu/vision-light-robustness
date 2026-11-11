# 视觉光照鲁棒性

测量目标检测器在亮度变化时从什么时候开始漏检。

仓库提供一个可复现的评估流程。附带的 CSV 是**演示数据**，不是模型测试结果。请用自己的标注图像和检测输出再得出性能结论。

## 快速运行

```bash
python -m vision_stress_lab --input examples/demo_predictions.csv --out results
```

程序会生成按光照条件汇总的 `summary.json`、`condition_metrics.csv` 和 `recall.svg`。核心评估器只用 Python 标准库，每行代表一张图像中是否存在目标。

输入 CSV 列为：`image_id,condition,illuminance_lux,target_present,predicted_present,confidence`。指标包括图像级召回率、精确率、误报率和平均置信度；不计算边界框 mAP。

可选的 YOLO 推理与数据增强流程见 [`docs/yolo-workflow.md`](docs/yolo-workflow.md)。合成亮度图像只能用于调试，不能替代真实光照测试。Python 3.10 或更高版本；基础评估无第三方依赖。

## License

MIT，见 `LICENSE`。

