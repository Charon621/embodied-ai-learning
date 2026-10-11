# 发布时的实测摘要

[baseline-metrics.json](baseline-metrics.json) 保存 Windows/Python 3.12.10 上的三组种子实测、来源/课程结构检查和源码摘要。原始 CSV/SVG 在运行命令后生成，未将大批临时产物提交。

```bash
python scripts/validate_repo.py --run-labs --seeds 7,19,42 --report outputs/validation/report.json
```

每个 seed 都从头运行三个脚本，结果写入 `outputs/validation/seed-<seed>/`。JSON 中的 script SHA-256 对应实测时脚本的原始文件字节；换行转换或修改代码会改变摘要。新的报告有新的时间，不能拿时间字段要求整份报告逐字节相同。单个实验的固定 seed 产物可单独比较。

这些数值是教学 toy 的证据，没有完整神经模型、GPU或机器人实验。指标解释、预算限制与未验证内容见[验证报告](../学习指南/验证记录.md)。
