# 首版框架状态

远端独立 Conda 环境、官方 LIBERO 固定版本、适配层、重放快照、候选采样、门控分叉执行接口、结果结构、保守标签、轨迹分组、动作距离及 MLP 工厂已实现。

## 实测验收

{
  "smoke_passed": true,
  "determinism_passed": true,
  "collection_approved": false,
  "scientific_hypotheses_tested": false,
  "state_max": 0.0,
  "state_mse_max": 0.0,
  "rgb_max": 0.0,
  "success_agreement_min": 1.0,
  "repeat_checks": 20
}

100步随机动作冒烟：libero_goal/0，双相机128×128，7维动作；已保存20帧并人工检查示例。随机动作未完成任务，不能视为专家成功轨迹。

重放检查仅覆盖随机小动作；不是接触丰富专家状态的最终验收。collection_approved 始终为 false，尚未开始800分叉或模型训练。

## 环境限制

- NVIDIA CUDA设备可见，但 EGL 实测为 Mesa llvmpipe 软件渲染；系统缺少 NVIDIA EGL库/入口。
- 环境使用CPU版 PyTorch，仅供初态加载及轻量评分器；未修改全局CUDA或其他项目环境。
- GitHub远端直连可用，原有代理失效；本地推送使用本地代理。
- Hugging Face直连连接超时，演示数据下载路径尚待解决。

## 下一阶段

实现两个任务的专家演示导入与成功重放、接触状态快照验收、任务特定安全/进度提取器；其后完成约800个分叉、人工标签审计和三种子基线/评分器评估。详细模块边界见 docs/architecture.md。
