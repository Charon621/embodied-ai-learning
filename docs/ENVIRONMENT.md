# 环境与计算路线

本课程的入门实验只依赖Python标准库，不下载模型、数据，不调用API。推荐Python 3.11或3.12；发布时实际运行环境与结果见[验证报告](VALIDATION.md)。本地生成物写入 `outputs/`，该目录被Git忽略。

## 第一天：Windows Git Bash

先检查现有环境，已有工具就不重复安装：

```bash
python --version
git --version
cd /e/.hermes/AI学习/embodied-ai-learning
python labs/01_behavior_cloning.py --seed 7 --output-dir outputs/bc
python labs/02_flow_matching.py --seed 7 --output-dir outputs/flow
python labs/03_world_model_planning.py --seed 7 --output-dir outputs/world
python scripts/validate_repo.py
```

Linux/macOS读者在自己的工作目录执行相同Python命令，`cd` 路径自行替换。从GitHub获取时：

```bash
git clone https://github.com/Charon621/embodied-ai-learning.git
cd embodied-ai-learning
python scripts/validate_repo.py
```

若终端尚未在E盘，先 `cd /e/你选的目录` 再clone。不要把多GB模型下载到默认用户缓存后才迁移。

## 三条计算路线

| 路线 | 可完成的成果 | 增加实验前检查 |
|---|---|---|
| CPU | 全部主线阅读、手算、3个toy实验与受控报告 | Python与写入路径 |
| 消费级GPU | 小模型训练、官方例子的小规模评测或推理 | 对应官方版本的显存/驱动/分辨率/量化要求 |
| 研究资源 | 完整结果复现、跨场景消融、多种子评测 | 数据/权重许可、总预算、协议与停机条件 |

这里没有保证所有VLA或视频模型都能在一张消费级卡上运行。可先检查官方README的任务、checkpoint、精度和卸载配置，再估算显存与时间。CPU toy不被称为完整Dreamer/VLA/视频模型复现。

## 扩展PyTorch与仿真环境

需要M01/M02的框架练习时，先建立独立虚拟环境，再按[PyTorch官方安装选择器](https://docs.pytorch.org/get-started/locally/)选命令：

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
# Linux/macOS: source .venv/bin/activate
# 此时再执行官方选择器提供的安装命令
```

MuJoCo、LIBERO/openpi和视频生成工具分开用环境。先在本机核对Windows原生支持；上游仅验证Linux时，另用Linux机器/受支持环境做可选实验。本课程不会让初学者一开始混装所有工具链。

## E盘存储与恢复

可选下载时明确指定E盘工作目录与模型缓存路径；安装位置不等于缓存位置。HF等工具如需缓存，可在该实验终端设置 `HF_HOME=/e/AIModels/huggingface`，具体Windows工具接受的路径格式按其文档确认。原始数据、权重、日志、API密钥和个人进度不提交Git。

每个实验保留配置、输出和源码commit。失败后先保存错误摘要与最小复现；只删除你确认用途的生成目录，不运行广泛清理命令。外部下载与付费资源由学习者选用，本仓库验证不包含它们。
