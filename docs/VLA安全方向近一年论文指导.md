# VLA 安全方向近一年论文指导

## 0. 文档目的

本文针对一个具体研究方向整理近期文献和实验路线：

> **预测性失败检测与安全恢复：VLA 能否在不可逆失败发生之前预测风险，并在不显著牺牲任务成功率的前提下选择安全恢复动作？**

检索范围为 2025-09-29 至 2026-09-29。文献按“问题已经被解决到什么程度、还剩什么空白、怎样形成可验证的研究问题”组织，而不是按模型发布时间罗列。

本文不是把所有 VLA 安全论文都收集起来，也不把“安全”当作单一指标。当前最需要区分的是：

- 任务是否完成；
- 执行过程是否违反安全约束；
- 模型能否提前发现自己将要失败；
- 发现风险后能否停止、回退、重新规划或恢复；
- 监测器是否因为误报造成过度保守。

## 1. 先给结论

对近一年文献的判断是：

1. **VLA 安全评测已经不是空白。** LIBERO-Plus、SafeVLA-Bench、VLA-Arena、ForesightSafety-VLA 等工作正在快速建立扰动、安全规则和多维指标。
2. **对抗攻击也已经较拥挤。** 视觉补丁、语言攻击、后门和模型无关攻击都已有近期代表性工作。
3. **一般性的 failure detection 已经出现。** Sentinel、SAFE、FLARE 等工作已经分别覆盖运行时监测、多任务失败检测和自主恢复。
4. **仍然相对空缺的是一个闭环问题：** 监测器根据当前观测、动作块和执行条件预测短时未来风险，触发具有安全代价约束的 fallback，并证明它在未见任务或真实机器人上确实减少不可恢复失败。

因此，研究重点不应是再做一个“安全评分器”，而应是：

> **风险预测的提前量、校准性、干预决策和恢复结果是否形成一个可验证的闭环。**

如果只在模拟器中离线判断“这个 episode 最后是否失败”，论文容易退化成已有 benchmark 的再标注。若能证明“提前停止/回退/重规划”改变了真实闭环结果，研究含金量会明显提高。

## 2. 近一年文献地图

### 2.1 运行时监测与失败检测

| 论文 | 时间/出处 | 解决的问题 | 主要启示 | 尚未解决的问题 |
|---|---|---|---|---|
| [Sentinel: Unpacking Failure Modes of Generative Policies](https://proceedings.mlr.press/v270/agia25a) | CoRL 2025 | 用动作时序一致性检测 erratic failure，用 VLM 检测任务进展失败 | 失败不能只用最终 success 表示，动作异常和任务停滞需要不同监测器 | 监测器主要是检测，闭环恢复和安全代价仍不完整 |
| [SAFE: Multitask Failure Detection for VLA Models](https://vla-safe.github.io/) | 2026 | 面向通用 VLA 的多任务失败检测，并强调未见任务零样本检测 | “跨任务失败检测”比单任务分类更值得研究 | 失败检测与动作干预之间的闭环关系仍需严格验证 |
| [FLARE: Failure-Aware Framework for Autonomous Correction and Recovery](https://openaccess.thecvf.com/content/CVPR2026/papers/Zhao_FLARE_A_Failure-Aware_Framework_for_Autonomous_Correction_and_Recovery_in_CVPR2026_paper.pdf) | CVPR 2026 | 失败感知、自主纠错与恢复 | 恢复已经成为公开研究问题，不能把“首次研究恢复”作为创新表述 | 需要在未见任务、长时任务和物理安全约束下验证恢复策略 |
| [Predictive vision-language monitoring for proactive safety](https://doi.org/10.3389/frobt.2026.1870024) | 2026 | 根据视觉、当前动作和执行条件预测短时未来风险，触发 fallback 和重规划 | “预测未来风险而不是事后报警”是当前更有潜力的切口 | VLM 延迟、提示敏感性、模拟器外泛化和恢复代价仍是问题 |
| [SO-101 Failure and Recovery Analysis](https://arxiv.org/abs/2606.08881) | 2026 | 在低成本真实机器人上进行失败分类和 recovery-aware evaluation | 真实部署中执行不稳定可能是主要失败来源，二元成功率不够 | 任务规模、跨平台泛化和自动恢复算法仍需扩大 |

### 2.2 安全约束和成功—安全差距

| 论文/基准 | 时间/出处 | 解决的问题 | 对本方向的意义 |
|---|---|---|---|
| [SafeVLA](https://safevla.github.io/) | NeurIPS 2025 Spotlight | CMDP、Safety-CHORES、Safe RL 和压力测试 | 物理安全对齐已有较完整框架，不能只提出“加入安全损失” |
| [SafeVLA-Bench](https://safevla.org/) | 2026-09 | 同时报告 Success、Safety、Success-But-Unsafe、Violation Severity | 必须把“成功”和“安全完成”拆开；安全成本不应由最终成功率替代 |
| [ForesightSafety-VLA](https://arxiv.org/abs/2606.27079) | 2026 | 13 类安全问题，覆盖物理、指令和视觉风险，并报告风险暴露时间 | 安全研究需要过程级风险指标和分层诊断，而不只是 episode 终点标签 |
| [VLA-Arena](https://vla-arena.github.io/) | ICML 2026 | 170 个任务，覆盖安全、干扰、外推和长时任务 | 只在两个 LIBERO 任务上做强结论会显得过窄 |

### 2.3 鲁棒性和对抗攻击

| 论文/基准 | 时间/出处 | 研究对象 | 对本方向的警告 |
|---|---|---|---|
| [LIBERO-Plus](https://openaccess.thecvf.com/content/CVPR2026/html/Fei_LIBERO-Plus_A_Progressive_Robustness_Benchmark_for_Visual-Language-Action_Models_CVPR2026_paper.html) | CVPR 2026 | 7 个扰动维度、分级鲁棒性分析 | “标准 benchmark 成功率高”已经被证明不等于鲁棒 |
| [AttackVLA](https://arxiv.org/abs/2511.12149) | 2025-11 | 统一攻击和后门评测，包含目标长时动作后门 | 对抗攻击赛道已有标准化趋势，简单新攻击容易同质化 |
| [Adversarial Attacks on Robotic VLA](https://arxiv.org/abs/2506.03350) | 2025 | 文本攻击和对 VLA 动作控制权的诱导 | 语言攻击已被单独研究，不能把 prompt 攻击当成空白 |

## 3. 读论文的正确方法

不要只记录“模型结构”和“成功率”。每篇论文至少填写以下信息：

```markdown
# Paper

## Safety object
保护的是人、机器人、物体、任务、语言指令还是模型完整性？

## Threat model
攻击者或环境能改变图像、语言、动作、训练数据、初始状态中的哪一项？

## Time horizon
安全判断发生在单步、动作块、短时窗口还是完整 episode？

## Label source
标签来自模拟器状态、规则、人工视频、最终成功率还是真实机器人？

## Intervention
检测到风险后，系统是否停止、降速、回退、重新观察、澄清或重规划？

## Metrics
是否报告提前量、误报、漏报、风险校准、恢复成功率和安全代价？

## Generalization
是否跨任务、跨机器人、跨初始状态、跨扰动和跨模型？

## Weakness
最容易被审稿人质疑的地方是什么？

## Relation to our work
是重复、互补，还是仅仅换了名称？
```

建议建立 `papers.csv`，字段至少包括：

```text
paper,year,venue,model,task_suite,embodiment,threat_model,
failure_type,label_source,closed_loop,intervention,
lead_time,recovery_metric,safety_metric,real_robot,code,main_limit
```

## 4. 目前最值得研究的核心问题

推荐的主问题是：

> 给定当前观测、语言指令、机器人状态和即将执行的动作块，VLA 能否预测未来短时窗口内的失败或安全违规，并选择一个经过验证的恢复动作？

可以形式化为：

\[
P(\text{failure within }H\text{ steps}\mid o_t, l, a_{t:t+K})
\]

\[
P(\text{safety violation within }H\text{ steps}\mid o_t, l, a_{t:t+K})
\]

\[
P(\text{recoverable}\mid o_t,l,a_{t:t+K},r)
\]

其中：

- `o_t` 是当前观测和机器人状态；
- `l` 是语言指令；
- `a_{t:t+K}` 是即将执行的动作块；
- `H` 是预测窗口；
- `r` 是候选恢复动作或恢复策略。

研究贡献不应只是提高一个 detector 的 AUROC，而应验证以下闭环命题：

\[
\text{预测风险}
\rightarrow
\text{提前干预}
\rightarrow
\text{降低不可恢复失败和安全代价}
\]

## 5. 推荐实验设计

### 5.1 最小可行版本

第一阶段不要训练新 VLA。先选一个可复现的开放模型和一个低成本环境，建立失败轨迹数据。

建议记录：

- RGB 和腕部相机观测；
- 语言指令；
- 机器人本体状态；
- 当前动作和动作块；
- 物体位姿和接触状态；
- 任务进展；
- 碰撞、越界和危险接触；
- 是否成功；
- 是否可恢复；
- 从风险出现到最终失败的时间。

失败类型至少包括：

1. 目标定位错误；
2. 抓取失败；
3. 物体滑落；
4. 动作震荡或停滞；
5. 任务进展错误；
6. 语言—执行错位；
7. 碰撞或安全违规；
8. 超时；
9. 可恢复失败；
10. 不可恢复失败。

### 5.2 监测器比较

至少比较四种监测器：

1. 动作时序一致性监测；
2. 视觉任务进展监测；
3. 视觉、动作和机器人状态融合模型；
4. action-conditioned future outcome model。

不要只报告分类 AUROC。必须报告：

- `time-to-detection`：失败前多少步发现风险；
- `false intervention rate`：本来会成功却被错误打断的比例；
- `missed failure rate`：未检测到的失败比例；
- `calibration error`：风险概率是否可信；
- `risk-coverage curve`：系统在不同拒绝率下的安全表现；
- `latency`：监测器是否来得及用于实时控制。

### 5.3 恢复动作比较

检测风险后至少比较：

- 继续原动作；
- 立即停止；
- 降速执行；
- 回退到最近安全状态；
- 重新观察后重规划；
- 使用预定义恢复动作；
- 使用学习到的恢复策略。

恢复结果应该区分：

```text
safe_success
unsafe_success
safe_recovery_then_success
safe_recovery_then_failure
unsafe_failure
unrecoverable_failure
false_stop
```

## 6. 最关键的评价指标

### 6.1 风险预测

- AUROC、AUPRC；
- Brier score；
- Expected Calibration Error；
- 预测提前量；
- 事件级召回率，而不是逐帧准确率。

### 6.2 安全与任务

- Task Success Rate；
- Safety Satisfaction Rate；
- Success-But-Unsafe；
- Failure-But-Recoverable；
- 违规严重程度；
- 累积安全成本；
- 风险暴露时间。

### 6.3 恢复能力

- 恢复成功率；
- 平均恢复步数；
- 恢复后任务完成率；
- 恢复动作造成的新违规率；
- 误触发停止率；
- 每次恢复的额外延迟和动作代价。

## 7. 研究中必须避免的陷阱

### 7.1 不要把最终成功率当作完整安全标签

成功但碰撞、成功但物体不稳定、成功但扰动旁边物体，都必须单独记录。SafeVLA-Bench 已经明确展示了 success 和 safety 之间的差距。[SafeVLA-Bench](https://safevla.org/)

### 7.2 不要把事后检测包装成预测性安全

如果系统只有在失败发生后才报警，它是 failure recognition，不是 proactive safety。必须报告失败发生前的预测提前量。

### 7.3 不要只做一个模型、一个任务、一个环境

failure detector 很容易记住任务视觉模板。至少要按轨迹、任务、初始状态和物体配置拆分，验证未见任务或未见初态。

### 7.4 不要把 VLM 的文字判断当成物理真值

VLM 可以解释“看起来可能失败”，但安全标签仍需要模拟器状态、碰撞信号、任务进展规则或人工核验。语言解释不能替代物理事件。

### 7.5 不要只优化 detector 的分数

如果 detector AUROC 提升，但触发干预后任务成功率下降、安全代价不变，那么它没有形成有效的安全系统。

### 7.6 不要过早训练一个新 VLA

先证明失败预测和恢复问题真实存在，再决定是否需要训练模型。否则很容易把数据、评测和训练问题混在一起。

## 8. 对当前 FERA-VLA 项目的建议

当前仓库中的 LIBERO 适配、状态重放、候选动作、公共后缀和分叉执行模块可以保留，但需要改变它们的研究用途：

- `snapshot.py`：用于构造“同一状态下不同动作后果”的失败预测数据；
- `candidate_sampler.py`：用于生成正常、近失败和明显失败动作块；
- `branches.py`：用于记录动作块、公共后缀和恢复结果；
- `outcome_extractor.py`：扩展为失败类型、安全事件、可恢复性和风险暴露时间；
- `labeler.py`：不再把主要目标写成模糊的 functional equivalence，而是明确区分 safe、unsafe、recoverable、irrecoverable；
- `scorers.py`：从等价动作 MLP 改为 action-conditioned risk/recovery predictor。

现有项目的下一步不应是继续扩大“功能等价动作”采集，而应先做一个小型诊断：

1. 选择一个可复现 VLA 和两个任务；
2. 收集正常、失败和可恢复失败轨迹；
3. 比较动作一致性、视觉进展和状态条件模型的提前预警能力；
4. 加入停止、回退和重新规划三种干预；
5. 检查干预是否降低不可恢复失败，而不是只提高 detector 指标。

只有当这五步显示出稳定的闭环收益，才值得继续做新的模型或训练损失。

## 9. 推荐阅读顺序

### 第一组：理解失败监测

1. [Sentinel](https://proceedings.mlr.press/v270/agia25a)
2. [SAFE](https://vla-safe.github.io/)
3. [SO-101 Failure and Recovery Analysis](https://arxiv.org/abs/2606.08881)

### 第二组：理解安全评价

4. [SafeVLA-Bench](https://safevla.org/)
5. [ForesightSafety-VLA](https://arxiv.org/abs/2606.27079)
6. [VLA-Arena](https://vla-arena.github.io/)

### 第三组：理解安全对齐

7. [SafeVLA](https://safevla.github.io/)
8. [FLARE](https://openaccess.thecvf.com/content/CVPR2026/papers/Zhao_FLARE_A_Failure-Aware_Framework_for_Autonomous_Correction_and_Recovery_in_CVPR2026_paper.pdf)
9. [Predictive vision-language monitoring](https://doi.org/10.3389/frobt.2026.1870024)

### 第四组：理解鲁棒性和攻击边界

10. [LIBERO-Plus](https://openaccess.thecvf.com/content/CVPR2026/html/Fei_LIBERO-Plus_A_Progressive_Robustness_Benchmark_for_Visual-Language-Action_Models_CVPR2026_paper.html)
11. [AttackVLA](https://arxiv.org/abs/2511.12149)
12. [Adversarial Attacks on Robotic VLA](https://arxiv.org/abs/2506.03350)

阅读顺序应从“失败是什么”开始，再读“如何评价安全”，然后读“如何训练和恢复”，最后读攻击与鲁棒性。否则很容易把一种攻击方法误认为完整安全研究。

## 10. 选题判断标准

一个值得继续的题目至少应满足以下四项中的三项：

- 能在失败真正发生之前提供有用的风险预测；
- 干预后显著降低不可恢复失败或安全成本；
- 在未见任务、未见初态或不同模型上仍有效；
- 不依赖单一 VLA、单一 benchmark 或人工挑选的阈值。

如果一个想法只满足“在一个模拟器上让 success rate 提升”，它更像工程优化；如果它能解释为什么 VLA 会失败、何时应当停止、怎样恢复，以及这种机制能否跨任务泛化，才更接近安全方向的研究贡献。

## 11. 暂定论文主线

可以先用下面的工作标题，不要过早把方法命名成完整框架：

> **Predictive Failure Monitoring and Safe Recovery for Vision-Language-Action Policies**

中文：

> **面向视觉—语言—动作策略的预测性失败监测与安全恢复**

对应的中心假设是：

> VLA 的许多危险失败在最终任务失败之前已经表现为可检测的进展停滞、动作异常、接触风险或未来状态偏离；利用这些信号进行提前干预，可以在保持任务成功率的同时减少不可恢复失败。

这个假设比“动作距离不等于功能差异”更接近 VLA 安全的实际需求，也更容易连接现有的运行时监测、世界模型、安全约束和恢复策略工作。
