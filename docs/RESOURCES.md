# 官方资料与必读索引

按模块使用，先完成必读指定章节，再决定是否选读。以下时间是阅读估计，与总课时有重叠，不逐项累加。核验说明区分页面/摘要、全文与运行；未做真实模型实验。

原始记录：[sources.json](sources.json)。来源核验日期：2026-10-11。

## M01 数学、Python与深度学习

[进入模块](modules/01-math-and-deep-learning.md)，按模块里的顺序与章节范围阅读。

| 编号 | 必读/选读 | 官方资料 | 约小时 | 为什么读 |
|---|---|---|---:|---|
| P-PYTHON | 选读 | [The Python Tutorial](https://docs.python.org/3/tutorial/) | 8 | 补函数、数据结构与文件处理 |
| P-D2L | 必读 | [动手学深度学习（中文）](https://zh.d2l.ai/) | 12 | 中文主教材的指定章节 |
| P-PYTORCH | 必读 | [PyTorch Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html) | 6 | 连接公式和训练代码 |
| P-MML | 选读 | [Mathematics for Machine Learning](https://mml-book.com/) | 8 | 按问题查漏，非整书前置 |
| P-OPT | 选读 | [CS231n Optimization](https://cs231n.github.io/optimization-1/) | 2 | 独立核查梯度 |

## M02 视觉表征与Transformer

[进入模块](modules/02-vision-and-transformers.md)，按模块里的顺序与章节范围阅读。

| 编号 | 必读/选读 | 官方资料 | 约小时 | 为什么读 |
|---|---|---|---:|---|
| P-D2L | 必读 | [动手学深度学习（中文）](https://zh.d2l.ai/) | 12 | 中文主教材的指定章节 |
| P-CS231N | 选读 | [Stanford CS231n 2025](https://cs231n.stanford.edu/2025/schedule.html) | 8 | 视觉表征查漏 |
| P-ATTN | 必读 | [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | 3 | 手算scaled dot-product attention |
| P-VIT | 必读 | [An Image is Worth 16x16 Words](https://arxiv.org/abs/2010.11929) | 2 | 图像token化的核心论文 |
| P-ROPE | 选读 | [RoFormer: Enhanced Transformer with Rotary Position Embedding](https://arxiv.org/abs/2104.09864) | 3 | 位置编码推导入口 |

## M03 机器人、控制、数据与仿真

[进入模块](modules/03-robotics-foundations.md)，按模块里的顺序与章节范围阅读。

| 编号 | 必读/选读 | 官方资料 | 约小时 | 为什么读 |
|---|---|---|---:|---|
| R-01 | 必读 | [Modern Robotics: Mechanics, Planning, and Control](https://hades.mech.northwestern.edu/index.php/Modern_Robotics) | 6 | 补齐机器人坐标、关节/任务空间、雅可比和反馈控制，使读者能检查模型动作接口。 |
| R-02 | 必读 | [Stanford CS234: Reinforcement Learning — Lecture Materials](https://web.stanford.edu/class/cs234/modules.html) | 2 | 用状态、动作、转移与奖励建立连续决策语言，并区分状态和传感器观测。 |
| R-03 | 必读 | [MuJoCo Documentation — Overview](https://mujoco.readthedocs.io/en/stable/overview.html) | 1 | 理解仿真的结构、动态状态、推进步骤与接触建模职责，避免把可视化当作完整评测。 |
| R-04 | 必读 | [LIBERO: Benchmarking Knowledge Transfer for Lifelong Robot Learning](https://github.com/Lifelong-Robot-Learning/LIBERO) | 3 | 把成功率主张落实到任务、初始状态、动作接口和具体评测协议。 |
| R-05 | 必读 | [Open X-Embodiment: Robotic Learning Datasets and RT-X Models](https://robotics-transformer-x.github.io/) | 0.5 | 学习跨本体数据的共享与动作语义对齐，区分统一格式和统一物理意义。 |
| R-06 | 必读 | [DROID: A Large-Scale In-the-Wild Robot Manipulation Dataset](https://droid-dataset.github.io/) | 0.5 | 理解示教 episode、本体观测、相机和场景划分，建立数据卡而非只记规模。 |

## M04 扩散与Flow Matching

[进入模块](modules/04-diffusion-and-flow.md)，按模块里的顺序与章节范围阅读。

| 编号 | 必读/选读 | 官方资料 | 约小时 | 为什么读 |
|---|---|---|---:|---|
| V-01 | 必读 | [Denoising Diffusion Probabilistic Models](https://hojonathanho.github.io/diffusion/) | 3 | 补足可lip Flow Matching 讲解之前的离散扩散与噪声回归基础。 |
| V-02 | 选读 | [Score-Based Generative Modeling through Stochastic Differential Equations](https://arxiv.org/abs/2011.13456v2) | 4 | 把离散扩散、score 估计、SDE/ODE 与求解器放回各自层级。 |
| V-03 | 必读 | [Flow Matching for Generative Modeling](https://arxiv.org/abs/2210.02747v2) | 4 | 为标准库一维高斯实验提供原始方法来源，避免把所有 FM 路径等同于直线或全局最优运输。 |
| V-04 | 必读 | [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752v2) | 2 | 区分生成表示、损失与骨干，建立视频 latent 压缩前置。 |
| V-05 | 必读 | [Scalable Diffusion Models with Transformers (DiT)](https://www.wpeebles.com/DiT) | 2 | 补足可lip AdaLN、位置编码专题与完整生成架构之间的关系。 |
| V-06 | 选读 | [Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598) | 2 | 建立视频条件采样和 guidance 消融的正确概念。 |

## M05 模仿学习与VLA

[进入模块](modules/05-imitation-and-vla.md)，按模块里的顺序与章节范围阅读。

| 编号 | 必读/选读 | 官方资料 | 约小时 | 为什么读 |
|---|---|---|---:|---|
| R-04 | 必读 | [LIBERO: Benchmarking Knowledge Transfer for Lifelong Robot Learning](https://github.com/Lifelong-Robot-Learning/LIBERO) | 3 | 把成功率主张落实到任务、初始状态、动作接口和具体评测协议。 |
| R-05 | 必读 | [Open X-Embodiment: Robotic Learning Datasets and RT-X Models](https://robotics-transformer-x.github.io/) | 0.5 | 学习跨本体数据的共享与动作语义对齐，区分统一格式和统一物理意义。 |
| R-06 | 必读 | [DROID: A Large-Scale In-the-Wild Robot Manipulation Dataset](https://droid-dataset.github.io/) | 0.5 | 理解示教 episode、本体观测、相机和场景划分，建立数据卡而非只记规模。 |
| R-07 | 必读 | [A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning (DAgger)](https://proceedings.mlr.press/v15/ross11a.html) | 2 | 解释 BC 的闭环分布偏移与互动收集的作用及专家查询前提。 |
| R-08 | 必读 | [Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ACT)](https://arxiv.org/html/2304.13705v1) | 3 | 从单步 BC 递进到动作序列，认识预测长度、执行长度和重叠集成。 |
| R-09 | 必读 | [Diffusion Policy: Visuomotor Policy Learning via Action Diffusion](https://arxiv.org/html/2303.04137v4) | 3 | 把扩散学习迁移到动作分布，同时区别生成能力和闭环数据偏移。 |
| R-10 | 必读 | [RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control](https://robotics-transformer2.github.io/) | 1.5 | 建立 VLA 的第一条动作表示路线：复用语言 token 输出接口。 |
| R-11 | 必读 | [OpenVLA: An Open-Source Vision-Language-Action Model](https://openvla.github.io/) | 1.5 | 理解开放 VLA 的视觉—语言—动作链路，并学习检查动作归一化与本体适配。 |
| R-12 | 必读 | [π0: A Vision-Language-Action Flow Model for General Robot Control](https://arxiv.org/html/2410.24164v1) | 3 | 连接 M04 的 Flow Matching 与连续动作输出，理解模型结构和训练数据配方各自的作用。 |
| R-13 | 选读 | [π0.5: a Vision-Language-Action Model with Open-World Generalization](https://arxiv.org/abs/2504.16054) | 3 | 完成基础对照后，研究怎样把语义任务、跨本体示教与低层动作结合，并审查未见环境协议。 |
| R-14 | 选读 | [Physical Intelligence openpi — Official Model and Training Code](https://github.com/Physical-Intelligence/openpi) | 3 | 从论文机制走向实现接口，核对配置、数据转换、归一化和评测版本。 |

## M06 latent世界模型与规划

[进入模块](modules/06-latent-world-models.md)，按模块里的顺序与章节范围阅读。

| 编号 | 必读/选读 | 官方资料 | 约小时 | 为什么读 |
|---|---|---|---:|---|
| W-01 | 必读 | [World Models](https://worldmodels.github.io/) | 2 | 用三个组件建立世界模型进入控制系统的第一张计算图。 |
| W-02 | 必读 | [Learning Latent Dynamics for Planning from Pixels (PlaNet)](https://danijar.com/project/planet/) | 3 | 学习 RSSM 的 prior/posterior、模型预测与动作搜索的关系。 |
| W-03 | 必读 | [Dream to Control: Learning Behaviors by Latent Imagination (Dreamer)](https://danijar.com/project/dreamer/) | 3 | 和 PlaNet 对照训练时想象、执行时规划两种模型用途。 |
| W-04 | 选读 | [Mastering Diverse Control Tasks through World Models (DreamerV3)](https://danijar.com/project/dreamerv3/) | 2.5 | 在已理解 actor/critic 后再理解世界模型训练稳定性。 |
| W-05 | 必读 | [Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture (I-JEPA)](https://arxiv.org/abs/2301.08243) | 2 | 建立 JEPA 表征预测目标，防止把静态表征模型误称通用机器人策略。 |
| W-06 | 必读 | [V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning](https://arxiv.org/abs/2506.09985) | 3 | 连接表征学习、动作条件预测和图像目标规划。 |

## M08 视频生成

[进入模块](modules/08-video-generation.md)，按模块里的顺序与章节范围阅读。

| 编号 | 必读/选读 | 官方资料 | 约小时 | 为什么读 |
|---|---|---|---:|---|
| P-ROPE | 选读 | [RoFormer: Enhanced Transformer with Rotary Position Embedding](https://arxiv.org/abs/2104.09864) | 3 | 位置编码推导入口 |
| V-04 | 必读 | [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752v2) | 2 | 区分生成表示、损失与骨干，建立视频 latent 压缩前置。 |
| V-05 | 必读 | [Scalable Diffusion Models with Transformers (DiT)](https://www.wpeebles.com/DiT) | 2 | 补足可lip AdaLN、位置编码专题与完整生成架构之间的关系。 |
| V-06 | 选读 | [Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598) | 2 | 建立视频条件采样和 guidance 消融的正确概念。 |
| V-07 | 必读 | [Video Diffusion Models](https://arxiv.org/abs/2204.03458v2) | 3 | 从图像生成过渡到时间结构和视频条件生成。 |
| V-08 | 必读 | [Stable Video Diffusion: Scaling Latent Video Diffusion Models to Large Datasets](https://arxiv.org/abs/2311.15127v1) | 3 | 补足只学网络结构时容易遗漏的训练阶段与数据质量。 |
| V-09 | 选读 | [Towards Accurate Generative Models of Video: A New Metric & Challenges (FVD)](https://arxiv.org/abs/1812.01717v2) | 3 | 训练分布评估与协议可比性意识，避免把视频距离当物理正确率。 |
| V-10 | 必读 | [VBench: Comprehensive Benchmark Suite for Video Generative Models](https://vchitect.github.io/VBench-project/) | 2 | 把视觉质量、跨帧一致性和条件符合度拆成可解释的评测规约。 |
| V-11 | 选读 | [Open-Sora official repository (hpcaitech)](https://github.com/hpcaitech/Open-Sora) | 6 | 任选一套现代公开工程追踪端到端数据流；运行前固定 commit 并重验硬件、许可与任务范围。 |
| V-12 | 选读 | [Wan2.1 official repository (Wan-Video)](https://github.com/Wan-Video/Wan2.1) | 6 | 任选一套现代工程研究条件控制与采样接口，区分发布权重与论文范围。 |

## M07 视频世界模型与WAM

[进入模块](modules/07-video-world-models-and-wam.md)，按模块里的顺序与章节范围阅读。

| 编号 | 必读/选读 | 官方资料 | 约小时 | 为什么读 |
|---|---|---|---:|---|
| W-06 | 必读 | [V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning](https://arxiv.org/abs/2506.09985) | 3 | 连接表征学习、动作条件预测和图像目标规划。 |
| W-07 | 必读 | [Learning Universal Policies via Text-Guided Video Generation (UniPi)](https://arxiv.org/abs/2302.00111) | 2.5 | 学习视频计划与动作解码两个模块的边界。 |
| W-08 | 必读 | [Genie: Generative Interactive Environments](https://arxiv.org/abs/2402.15391) | 2 | 讨论 latent action 可控性与真实机器人动作对齐的差距。 |
| W-09 | 选读 | [Genie 3 — official model overview and limitations](https://deepmind.google/models/genie/) | 0.5 | 练习把世界生成的演示范围与物理仿真、控制证据分开。 |
| W-10 | 必读 | [Cosmos-Predict2 — official models and action-conditioned sample](https://github.com/nvidia-cosmos/cosmos-predict2) | 1 | 区分动作作为条件的前向预测器与直接输出动作的策略。 |
| W-11 | 选读 | [Cosmos 3 — official unified model project](https://research.nvidia.com/labs/cosmos-lab/cosmos3/) | 0.5 | 观察多模态世界与动作接口的统一设计，同时练习审查公开能力边界。 |
| W-12 | 必读 | [Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning](https://arxiv.org/abs/2601.16163) | 2.5 | 理解视频模型怎样同时承担策略、前向模型和价值评估角色。 |
| W-13 | 必读 | [World Action Models are Zero-shot Policies (DreamZero)](https://arxiv.org/abs/2602.15922) | 2 | 从联合目标、闭环上下文和迁移协议理解 WAM，而非从名称判断。 |
| W-14 | 选读 | [Causal World Modeling for Robot Control (LingBot-VA)](https://arxiv.org/abs/2601.21998v1) | 2.5 | 研究因果时序、生成计算和实际动作执行怎样协调。 |

## M09 评测、复现与研究

[进入模块](modules/09-evaluation-and-research.md)，按模块里的顺序与章节范围阅读。

| 编号 | 必读/选读 | 官方资料 | 约小时 | 为什么读 |
|---|---|---|---:|---|
| P-RLEVAL | 必读 | [Deep Reinforcement Learning at the Edge of the Statistical Precipice](https://proceedings.neurips.cc/paper/2021/hash/f514cec81cb148559cf475e7426eed5e-Abstract.html) | 3 | 小样本评测与不确定性报告 |
| R-04 | 必读 | [LIBERO: Benchmarking Knowledge Transfer for Lifelong Robot Learning](https://github.com/Lifelong-Robot-Learning/LIBERO) | 3 | 把成功率主张落实到任务、初始状态、动作接口和具体评测协议。 |
| R-13 | 选读 | [π0.5: a Vision-Language-Action Model with Open-World Generalization](https://arxiv.org/abs/2504.16054) | 3 | 完成基础对照后，研究怎样把语义任务、跨本体示教与低层动作结合，并审查未见环境协议。 |
| R-14 | 选读 | [Physical Intelligence openpi — Official Model and Training Code](https://github.com/Physical-Intelligence/openpi) | 3 | 从论文机制走向实现接口，核对配置、数据转换、归一化和评测版本。 |
| V-09 | 选读 | [Towards Accurate Generative Models of Video: A New Metric & Challenges (FVD)](https://arxiv.org/abs/1812.01717v2) | 3 | 训练分布评估与协议可比性意识，避免把视频距离当物理正确率。 |
| V-10 | 必读 | [VBench: Comprehensive Benchmark Suite for Video Generative Models](https://vchitect.github.io/VBench-project/) | 2 | 把视觉质量、跨帧一致性和条件符合度拆成可解释的评测规约。 |

## 核验边界

| 编号 | 核验说明 |
|---|---|
| P-PYTHON | 官方教程说明面向已有一点编程基础的学习者。 |
| P-D2L | 目录核验包含线性代数、微积分、概率、自动微分与注意力。 |
| P-PYTORCH | 官方教程核验训练工作流与基础API。 |
| P-MML | 作者官网提供数学基础章节与公开PDF入口。 |
| P-OPT | 官方课程笔记核验finite differences和gradient descent。 |
| P-CS231N | 固定2025课程页，包含视觉基础和Transformer材料。 |
| P-ATTN | arXiv标题、作者与摘要主题核验。 |
| P-VIT | arXiv确认视觉Transformer与图像patch主题。 |
| P-ROPE | arXiv确认rotary position embedding。 |
| P-RLEVAL | NeurIPS正式论文页面核验题名和评测统计主题。 |
| R-01 | 核验作者所在 Northwestern 官方教材主页，含免费预印本入口、章目、练习与视频；本课程选读配置空间、刚体运动、运动学和控制章节。 |
| R-02 | 核验 Stanford 官方 2026 课程资料页，列出 Introduction、Tabular MDP planning、Policy evaluation 及推荐章节；单独打开 Lecture 2 PDF 未成功，因此仅将已读取的官方课程导航标为核验入口。 |
| R-03 | 核验官方文档 Introduction、MJCF、mj_step 及 mjModel/mjData 分离介绍；未安装、运行仿真或验证当地系统兼容性。stable 文档可能随版本更新。 |
| R-04 | 核验作者官方仓库 README 的套件说明、任务读取、固定初始状态、训练和独立评测入口；仅阅读代码说明，未下载数据或运行环境。 |
| R-05 | 核验作者项目页数据汇集、标准格式、RT-X 模型与七维动作说明；未逐一核验全部子数据集许可、规模版本或下载可用性。 |
| R-06 | 核验作者项目页数据字段示例、统一硬件平台、多场景采集介绍，以及后续相机标定/语言标注更新说明；未下载数据。 |
| R-07 | 核验 PMLR 2011 作者、会议元数据及摘要，并浏览同站原论文 Algorithm 3.1 的当前策略访问、专家标注和数据汇集过程；教学实验不宣称论文复现。 |
| R-08 | 核验 2023 原论文 v1 方法、leader/follower 动作约定、CVAE 训练与先验均值推理、同一时刻预测的时间集成及分块消融；未复现实验。 |
| R-09 | 核验作者项目页与原论文 v4 的 II-C 动作扩散、观测条件和 To/Tp/Ta 滚动执行，以及示教覆盖和推理开销局限；未复现实验。 |
| R-10 | 核验作者项目页 Approach Overview：动作文本 token、机器人与视觉语言共同训练、推理反 token 化进入闭环；未独立复验作者报告的性能。 |
| R-11 | 核验作者官方项目页原始 OpenVLA 的视觉编码器、投影器、语言主干、token 化动作和数据来源；正文仅讲原始机制，不混入后续 OFT 等版本，不下载权重。 |
| R-12 | 核验原论文 v1 的 III–V：VLM、动作专家、本体状态、Flow Matching 连续动作以及预训练/后训练的数据角色；未运行模型或复现实验。 |
| R-13 | 核验 arXiv 原论文入口、作者与摘要中的异构任务共同训练及新家庭实验主张；本课程只作为进阶选读，没有独立验证泛化结果。 |
| R-14 | 核验 Physical Intelligence 官方仓库 README 的模型类型、数据适配/训练入口、操作系统/GPU要求和 JAX/PyTorch 支持差异；main 会变化，实际实验须固定提交。未安装、下载权重或推理。 |
| V-01 | 已浏览作者项目页，核对作者、2020 年论文、训练与采样算法入口及加噪/去噪主题；未复现实验。 |
| V-02 | 已浏览 arXiv 论文记录与摘要，核对 2021-02-10 v2、反向 SDE、score、probability-flow ODE 及同边缘分布主题；未复现实验。 |
| V-03 | 已浏览 arXiv 记录及 v2 HTML，核对条件概率路径、向量场回归、训练无需模拟但采样使用 ODE 的范围；未复现原文 ImageNet 实验。 |
| V-04 | CVF 页面本次访问被 403 拒绝，改用作者 arXiv 论文记录核对 2022-04-13 v2、autoencoder latent 与 cross-attention 条件主题；未复现实验。 |
| V-05 | 已浏览作者项目页，核对 ICCV 2023、latent patch Transformer、AdaLN、模型/patch 缩放及论文代码入口；未复现作者 FID。 |
| V-06 | 已浏览 arXiv 作者与摘要，核对 2022 年论文将条件/无条件 score 组合及质量/多样性权衡；没有将引导分称为概率。 |
| V-07 | 已浏览 arXiv 记录与 v2 HTML，核对 2022-06-22 版本、图像/视频联合训练与条件时空延长主题；未复现实验。 |
| V-08 | 已浏览 arXiv v1 记录与 HTML，核对 2023-11-25 版本、数据整理、图像预训练/视频预训练/高质量微调；论文任务范围不等于每个发布 checkpoint 的任务范围。 |
| V-09 | 已浏览 arXiv 记录与摘要，核对 2019-03-27 v2 和 FVD 视频生成分布评价主题；本课程没有运行 FVD 或复现作者的人类研究。 |
| V-10 | 已浏览作者项目页，核对 16 维视频评测、代码与论文入口，并检查展示图归一化说明；不记录排行榜排名为课程验收。 |
| V-11 | 已浏览官方仓库 README，核对 configs、opensora、scripts、video autoencoder 与训练/推理文档入口，以及已公布版本；未下载权重、安装依赖或运行视频模型。它不等同于 OpenAI Sora。 |
| V-12 | 已浏览官方 README 的任务表、权重入口与推理参数，确认 T2V/I2V/首尾帧等任务使用不同配置或权重；未下载运行，也未启用提示扩写 API；不假设所有新型号均公开。 |
| W-01 | 作者交互式论文可访问；核验视觉压缩、时序模型、控制器与想象环境的主题和方法接口。 |
| W-02 | 作者项目页和 arXiv:1811.04551 可访问；主题为像素输入、确定性与随机潜在动态、多步 overshooting 及在线规划。 |
| W-03 | 作者项目页和 arXiv:1912.01603 可访问；核验 latent imagination、策略/价值训练以及解析梯度路线。 |
| W-04 | 作者项目页与 Nature 正式论文信息可访问；将归一化、平衡与变换用于稳定跨任务学习。课程未复现论文性能。 |
| W-05 | 作者论文 arXiv 页面和官方 facebookresearch/ijepa 说明可访问；从图像上下文预测目标块表征，非像素生成。静态图像模型不等同动作条件动态。 |
| W-06 | 论文摘要与 v1 HTML §§2–4、官方 vjepa2 仓库可访问；明确动作无关预训练、含状态信号的交互后训练、V-JEPA 2-AC 与 MPC 的区别。 |
| W-07 | 作者论文页面、NeurIPS 论文与 Google Research 官方说明可访问；文本条件视频计划由逆动力学转换为低层动作。 |
| W-08 | 论文及 Google DeepMind 官方 publication 页可访问；未标注真实动作的视频、时空 tokenizer、自回归动态与 latent action 接口主题一致。 |
| W-09 | DeepMind 官方现行模型页可访问，含交互能力与有限动作、多主体、地点准确性、持续时长限制；属会更新的官方说明，非独立复现。 |
| W-10 | 官方 GitHub README 可访问；Models 表区分 Text2Image、Video2World 和 Video+Action 动作条件样例，后者预测未来画面。未下载或运行模型。 |
| W-11 | NVIDIA 研究项目页可访问，列出 Unified MoT、autoregressive diffusion 及理解/生成/策略/前向与逆向动态接口。技术报告 PDF 的浏览工具打开失败，故以已核验官方页面为资料入口。 |
| W-12 | v1 HTML §§4.1–4.3 与限制可访问；核验 latent frame injection、动作/状态/价值联合训练、直接策略和 best-of-N 规划，以及成功示教分布之外的 rollout 数据需求。 |
| W-13 | 作者论文 v1 HTML 方法部分可访问；联合视频动作、动作块后真实观测更新和跨本体评测为论文定义的范围。课程未复现论文性能。 |
| W-14 | 作者论文 v1 HTML 可访问；核验交错视频动作、双流 MoT、闭环观测与异步执行。仅讨论此版本，不把后续 VA2 说明混入。 |
