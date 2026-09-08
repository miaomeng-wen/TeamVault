---
title: "DeMamba: AI-Generated Video Detection on Million-Scale GenVideo Benchmark"
aliases:
  - DeMamba
  - GenVideo
  - Chen_2024_DeMamba
  - arXiv:2405.19707
tags:
  - dataset
  - benchmark
  - aigc-video
  - deepfake-detection
  - mamba
created: 2026-09-08
assignee: 文宇豪
reading_status: reading
screening_status: candidate
source_id: doi:10.1007/s11432-024-4894-0
source_type: article
doi: 10.1007/s11432-024-4894-0
source_url: https://doi.org/10.1007/s11432-024-4894-0
pdf_url:
authors: Chen; Hong; Huang; Xu; Gu; Li; Lan; Zhu; Zhang; Wang; Li
year: 2026
source: Science China Information Sciences，Vol. 69, Issue 6, Article 162103（预印本：arXiv:2405.19707）
theme: 02_数据集与基准
study_area: AI 生成视频检测（AI-Generated Video Detection / AIGC 视频伪造检测与取证）
data_source: GenVideo 数据集（训练集 2,294,594 片段，测试集 19,588 片段；涵盖主流扩散/自回归等 10+ 类生成模型与 Youku-mPLUG、Kinetics-400、MSR-VTT 真实视频）
methodology: 构建百万级 AIGC 视频检测基准 GenVideo 及两项评测协议（跨生成器泛化、质量退化分类）；提出基于 3D 连续扫描机制的状态空间模型即插即用插件 DeMamba（Detail Mamba）
core_variable: 自变量：生成器机制/架构（未见域）、视频压缩与常见扰动退化类型；因变量：分类准确率（ACC）、平均精度（AP）
key_finding: 传统人脸伪造与图像检测器难以应对通用 AIGC 视频的跨模型泛化与传播退化；DeMamba 插件通过捕捉局部时空不一致性，在 XCLIP 上取得 0.9710 AP（+12.02%），且推理延迟低、鲁棒性优秀
relevance: 提供目前首个百万级通用 AI 视频检测公开基准 GenVideo（脱离人脸 Deepfake 局限，覆盖全场景），并提出基于 Mamba 的时空细粒度取证插件，直接契合团队视频伪造检测与泛化评测课题
primary_chapter: 第 3 节（GenVideo 数据集构建与组织）、第 4 节（DeMamba 插件架构与连续扫描机制）
secondary_chapters: 第 5 节（跨生成器泛化与退化视频实验评估）
evidence_scope: 全文 11 页正文及附录（含代码开源地址与实验消融细节）
---

## 一句话结论

针对现有伪造视频检测多局限于人脸且缺乏大规模前沿生成视频基准的瓶颈，本文构建了首个百万级通用 AI 生成视频检测基准 **GenVideo**（涵盖 10+ 种主流生成器与超 230 万视频片段），并设计了基于状态空间模型的即插即用插件 **DeMamba**，通过 3D 连续扫描捕获细粒度时空不一致性，显著提升了在未见生成器与传播退化场景下的泛化性与鲁棒性。

## 核心发现

- **跨生成器泛化瓶颈显著**：纯图像检测模型由于无法利用时序一致性线索，在视频伪造检测上表现受限；传统视频检测模型则难以有效建模局部细微空间畸变，跨生成器（尤其是未见生成模型）的泛化能力下降剧烈。
- **数据规模对泛化性至关重要**：在 GenVideo 上的消融分析表明，生成器涵盖种类及单生成器训练样本规模与检测器跨域泛化性能呈强正相关，百万级多样化数据是避免检测器走捷径的关键。
- **DeMamba 插件性能与效率兼备**：将 DeMamba 作为即插即用模块接入 XCLIP（DeMamba-XCLIP-FT），在跨生成器任务上取得 0.9710 AP 与 0.9020 F1，较基础 XCLIP 提升 12.02% AP；且测试推理延迟增加极小，单卡 QPS 与原模型保持在同一数量级。
- **退化鲁棒性突出**：在 H.264 压缩、JPEG 压缩、高斯噪声、色彩变换等 8 种实际传播退化测试下，DeMamba 均表现出优于现有基线的抗干扰鲁棒性。

## 方法与数据

- **数据集构成（GenVideo）**：
  - **规模**：训练集包含 1,213,511 条真实视频与 1,081,083 条生成视频；测试集包含 10,000 条真实视频与 8,588 条生成视频。
  - **真实视频来源**：Youku-mPLUG、Kinetics-400、MSR-VTT。
  - **伪造视频来源**：涵盖扩散模型（SVD、I2VGen-XL、VideoCrafter、Animatediff、LaVie、ModelScopeT2V、DynamiCrafter、SEINE 等）、自回归/DiT 类（Latte、Sora、VideoPoet、Magvit 等）及商业服务（Pika）等，覆盖 T2V 与 I2V 全场景内容。
- **评测任务设计**：
  - **Task 1: 跨生成器泛化（Cross-Generator Generalization）**：分为多对多（Many-to-Many，10 类基线生成器训练后在未见生成器测试集评估）与一对多（One-to-Many）。
  - **Task 2: 退化视频分类（Degraded Video Classification）**：评估视频在 H.264 压缩、JPEG、裁剪、翻转、文字水印、图片水印、高斯噪声与颜色变换下的检测鲁棒性。
- **DeMamba 检测模型**：
  - **结构**：特征编码器（CLIP / XCLIP）+ 局部区域划分（Spatial Consolidation）+ DeMamba Block + 全局/局部特征聚合分类头。
  - **3D 连续扫描（Continuous Scan）**：改进传统 Mamba 的 sweep-scan 方式，采用空间相邻连续扫描顺序（如 `(1,1) -> (1,2) -> (2,2) -> (2,1)`），确保空间与时序 token 上下文关系的连贯整合。
  - **开源资源**：代码与数据集公开于 [GitHub: chenhaoxing/DeMamba](https://github.com/chenhaoxing/DeMamba)。

## 与本课题的关系

- **基准支撑**：本团队在开展通用 AIGC 视频伪造检测研究时，GenVideo 可作为评测模型泛化性与鲁棒性的核心训练与评测基准之一。
- **方法借鉴**：DeMamba 将 State Space Model（Mamba）引入取证任务并采用 3D 连续扫描的思想，对团队探索长序列视频取证与低开销时空不一致性建模具有重要参考价值。

## 证据与页码索引

| 证据 | 位置 | 跳转 |
| --- | --- | --- |
| GenVideo 训练集/测试集数据划分与生成器类别清单 | 第 3 页 Table 1 | [打开来源](https://doi.org/10.1007/s11432-024-4894-0) |
| DeMamba 整体架构与 3D 连续扫描时序展开图 | 第 4 页 Figure 2 | [打开来源](https://doi.org/10.1007/s11432-024-4894-0) |
| 跨生成器多对多与一对多实验对比结果（ACC / AP / Recall / F1） | 第 5 页 Table 3, Table 4 | [打开来源](https://doi.org/10.1007/s11432-024-4894-0) |
| 8 种传播退化条件下的鲁棒性评测结果 | 第 6 页 Table 5 | [打开来源](https://doi.org/10.1007/s11432-024-4894-0) |
| 分区大小（Zone size）与扫描顺序的消融实验 | 第 6 页 Table 7, Table 8 | [打开来源](https://doi.org/10.1007/s11432-024-4894-0) |

> [!note] 写作规则
> - 状态只改本页 frontmatter，进度由 [[../../04_Tables/团队任务看板|团队任务看板]] 自动汇总，不要手工登记到任何清单。
> - 文件命名必须是 `作者_年份_短标题.md`，存放在 `theme` 对应的唯一主题子目录。
> - 写入前按 `source_id` 全库查重；PDF、数据集等大文件放团队文件库，不提交进 Git。
> - 改完状态即可提交，无需通知任何人更新看板。

---

建档说明：本笔记由智能体协助建档（2026-09-08）。来源经核验：论文于 2024 年以预印本发布于 arXiv (2405.19707)，随后正式刊载于《Science China Information Sciences》2026 年第 69 卷第 6 期（Article 162103），DOI 为 `10.1007/s11432-024-4894-0`。建档状态为 `unread` / `candidate`（待认领），认领人认领后请将 PDF 上传至团队文件库并回填 `pdf_url`。
